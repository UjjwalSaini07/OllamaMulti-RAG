"""
PDF Ingestion Pipeline — production‑ready

Adds:
- Structured logging (JSON‑friendly) and timing
- Redis caching for PDF text + chunking (idempotent via SHA‑256)
- Concurrency for multi‑PDF extraction
- Robust config handling with sensible defaults
- Deterministic document IDs + metadata
- Batch adds to the vector DB with basic retry/backoff
- CLI entry point for local use

Assumptions:
- `vectordb_handler.load_vectordb()` returns a client with `.add_documents(list[Document])`
- `utils.load_config()` provides a dict, optional keys shown below
- `utils.timeit` exists; we also add our own `@log_timed` to instrument internals

Optional config keys (examples):
{
  "pdf_text_splitter": {
    "chunk_size": 1000,
    "overlap": 100,
    "separators": ["\n\n", "\n", " ", ""]
  },
  "redis": {
    "enabled": true,
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password": null,
    "ttl_seconds": 604800
  },
  "ingestion": {
    "max_workers": 4,
    "batch_size": 512,
    "max_retries": 3,
    "backoff_seconds": 1.0
  }
}
"""
from __future__ import annotations
import hashlib
import io
import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, BinaryIO, Dict, Iterable, List, Optional, Sequence, Tuple

import pypdfium2
from langchain.schema.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None

from vectordb_handler import load_vectordb
from utils import load_config, timeit  # noqa: F401  (kept for backward compat)

# -------------------------
# Logging setup
# -------------------------
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format=(
        "{\"ts\":\"%(asctime)s\",\"level\":\"%(levelname)s\","
        "\"msg\":\"%(message)s\",\"module\":\"%(module)s\",\"func\":\"%(funcName)s\"}"
    ),
)
logger = logging.getLogger(__name__)

# ==================================================================
#  Project   : Neura-Nix - Multimodal AI Assistant {Ollama MultiRag}
#  Author    : UjjwalS (https://www.ujjwalsaini.dev)
#  License   : Apache-2.0
#  Copyright : © 2025 UjjwalS. All rights reserved.
# ==================================================================
def log_timed(fn):
    """Simple timing decorator that logs duration in milliseconds."""

    def _wrap(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            dt_ms = (time.perf_counter() - t0) * 1000.0
            logger.info("timing", extra={"fn": fn.__name__, "duration_ms": round(dt_ms, 2)})

    return _wrap


# -------------------------
# Config models
# -------------------------
@dataclass
class SplitterCfg:
    chunk_size: int = 1000
    overlap: int = 100
    separators: Optional[List[str]] = None


@dataclass
class RedisCfg:
    enabled: bool = False
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ttl_seconds: int = 7 * 24 * 3600


@dataclass
class IngestionCfg:
    max_workers: int = max(2, os.cpu_count() or 2)
    batch_size: int = 512
    max_retries: int = 3
    backoff_seconds: float = 1.0


@dataclass
class AppCfg:
    splitter: SplitterCfg
    redis: RedisCfg
    ingestion: IngestionCfg

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AppCfg":
        ps = d.get("pdf_text_splitter", {}) or {}
        rc = d.get("redis", {}) or {}
        ic = d.get("ingestion", {}) or {}
        return AppCfg(
            splitter=SplitterCfg(
                chunk_size=int(ps.get("chunk_size", 1000)),
                overlap=int(ps.get("overlap", 100)),
                separators=ps.get("separators"),
            ),
            redis=RedisCfg(
                enabled=bool(rc.get("enabled", False)),
                host=str(rc.get("host", "localhost")),
                port=int(rc.get("port", 6379)),
                db=int(rc.get("db", 0)),
                password=rc.get("password"),
                ttl_seconds=int(rc.get("ttl_seconds", 7 * 24 * 3600)),
            ),
            ingestion=IngestionCfg(
                max_workers=int(ic.get("max_workers", max(2, os.cpu_count() or 2))),
                batch_size=int(ic.get("batch_size", 512)),
                max_retries=int(ic.get("max_retries", 3)),
                backoff_seconds=float(ic.get("backoff_seconds", 1.0)),
            ),
        )

# ==================================================================
#  Project   : Neura-Nix - Multimodal AI Assistant {Ollama MultiRag}
#  Author    : UjjwalS (https://www.ujjwalsaini.dev)
#  License   : Apache-2.0
#  Copyright : © 2025 UjjwalS. All rights reserved.
# ==================================================================
# -------------------------
# Redis helper
# -------------------------
class RedisCache:
    def __init__(self, cfg: RedisCfg):
        self.cfg = cfg
        self.client = None
        if cfg.enabled:
            if redis is None:
                logger.warning("Redis not installed, disabling caching.")
            else:
                try:
                    self.client = redis.Redis(
                        host=cfg.host, port=cfg.port, db=cfg.db, password=cfg.password, socket_timeout=5
                    )
                    # quick ping to confirm
                    self.client.ping()
                    logger.info("Redis cache enabled.")
                except Exception as e:  # pragma: no cover
                    logger.warning("Redis unavailable, caching disabled: %s", repr(e))
                    self.client = None

    def get(self, key: str) -> Optional[bytes]:
        if not self.client:
            return None
        try:
            return self.client.get(key)
        except Exception as e:  # pragma: no cover
            logger.warning("Redis GET failed: %s", repr(e))
            return None

    def set(self, key: str, value: bytes, ttl: Optional[int] = None) -> None:
        if not self.client:
            return
        try:
            self.client.set(key, value, ex=ttl or self.cfg.ttl_seconds)
        except Exception as e:  # pragma: no cover
            logger.warning("Redis SET failed: %s", repr(e))


# -------------------------
# Core utilities
# -------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@log_timed
def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract UTF‑8 text from a PDF byte string using pypdfium2."""
    # pypdfium2 accepts various inputs, including file paths and binary buffers
    with pypdfium2.PdfDocument(pdf_bytes) as pdf:
        out: List[str] = []
        for page_number in range(len(pdf)):
            page = pdf.get_page(page_number)
            textpage = page.get_textpage()
            out.append(textpage.get_text_range())
        return "\n".join(out)


def ensure_bytes(handle: BinaryIO | bytes | bytearray | io.BytesIO) -> bytes:
    if isinstance(handle, (bytes, bytearray)):
        return bytes(handle)
    if isinstance(handle, io.BytesIO):
        return handle.getvalue()
    # Try common file-like patterns
    if hasattr(handle, "getbuffer"):
        return bytes(handle.getbuffer())
    if hasattr(handle, "read"):
        pos = None
        try:
            pos = handle.tell()
        except Exception:
            pos = None
        data = handle.read()
        # attempt to reset cursor
        try:
            if pos is not None:
                handle.seek(pos)
        except Exception:
            pass
        return data
    raise TypeError("Unsupported input type for PDF bytes")


class TextChunker:
    def __init__(self, cfg: SplitterCfg):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=cfg.chunk_size, chunk_overlap=cfg.overlap, separators=cfg.separators
        )

    @log_timed
    def split(self, text: str) -> List[str]:
        return self.splitter.split_text(text)


# -------------------------
# Ingestion pipeline
# -------------------------
class PDFIngestor:
    def __init__(self, cfg: AppCfg):
        self.cfg = cfg
        self.cache = RedisCache(cfg.redis)
        self.chunker = TextChunker(cfg.splitter)
        self.vdb = load_vectordb()

    # Cache keys
    @staticmethod
    def _text_key(doc_hash: str) -> str:
        return f"pdf:text:{doc_hash}"

    @staticmethod
    def _chunks_key(doc_hash: str) -> str:
        return f"pdf:chunks:{doc_hash}"

    def _load_text_cached(self, doc_hash: str) -> Optional[str]:
        raw = self.cache.get(self._text_key(doc_hash))
        if raw is None:
            return None
        try:
            return raw.decode("utf-8")
        except Exception:
            return None

    def _store_text_cached(self, doc_hash: str, text: str) -> None:
        self.cache.set(self._text_key(doc_hash), text.encode("utf-8"))

    def _load_chunks_cached(self, doc_hash: str) -> Optional[List[str]]:
        raw = self.cache.get(self._chunks_key(doc_hash))
        if raw is None:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return None

    def _store_chunks_cached(self, doc_hash: str, chunks: List[str]) -> None:
        try:
            payload = json.dumps(chunks).encode("utf-8")
        except Exception:
            # Fallback: join with unit‑separator if JSON fails (very unlikely)
            payload = "\u001f".join(chunks).encode("utf-8")
        self.cache.set(self._chunks_key(doc_hash), payload)

    @log_timed
    def extract_text(self, item: BinaryIO | bytes | bytearray | io.BytesIO) -> Tuple[str, str]:
        """Return (doc_hash, text). Uses cache when enabled."""
        b = ensure_bytes(item)
        doc_hash = sha256_bytes(b)
        cached = self._load_text_cached(doc_hash)
        if cached is not None:
            logger.info("cache_hit", extra={"stage": "text", "doc_hash": doc_hash})
            return doc_hash, cached
        text = extract_text_from_pdf_bytes(b)
        self._store_text_cached(doc_hash, text)
        logger.info("cache_store", extra={"stage": "text", "doc_hash": doc_hash, "bytes": len(b)})
        return doc_hash, text

    @log_timed
    def chunk_text(self, doc_hash: str, text: str) -> List[str]:
        cached = self._load_chunks_cached(doc_hash)
        if cached is not None:
            logger.info("cache_hit", extra={"stage": "chunks", "doc_hash": doc_hash, "count": len(cached)})
            return cached
        chunks = self.chunker.split(text)
        self._store_chunks_cached(doc_hash, chunks)
        logger.info("cache_store", extra={"stage": "chunks", "doc_hash": doc_hash, "count": len(chunks)})
        return chunks

    def _make_documents(self, doc_hash: str, chunks: Sequence[str]) -> List[Document]:
        # Deterministic document IDs: doc_hash + chunk index
        docs: List[Document] = []
        for i, chunk in enumerate(chunks):
            docs.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "doc_id": f"{doc_hash}:{i}",
                        "source_hash": doc_hash,
                        "chunk_index": i,
                        "num_chunks": len(chunks),
                    },
                )
            )
        return docs

    def _backoff_sleep(self, attempt: int) -> None:
        base = self.cfg.ingestion.backoff_seconds
        time.sleep(base * (2 ** (attempt - 1)))

    @log_timed
    def add_documents(self, documents: List[Document]) -> None:
        if not documents:
            return
        batch_size = max(1, self.cfg.ingestion.batch_size)
        max_retries = max(0, self.cfg.ingestion.max_retries)
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            attempt = 0
            while True:
                attempt += 1
                try:
                    self.vdb.add_documents(batch)
                    logger.info("vdb_add_ok", extra={"batch": len(batch), "offset": i})
                    break
                except Exception as e:
                    logger.warning(
                        "vdb_add_fail", extra={"error": repr(e), "attempt": attempt, "batch": len(batch)}
                    )
                    if attempt > max_retries:
                        raise
                    self._backoff_sleep(attempt)

    @log_timed
    def ingest_many(self, pdf_items: Sequence[BinaryIO | bytes | bytearray | io.BytesIO]) -> int:
        """High‑level API: extract + chunk + add to vector DB. Returns document count."""
        if not pdf_items:
            logger.info("no_input")
            return 0

        max_workers = max(1, self.cfg.ingestion.max_workers)
        results: List[Tuple[str, str]] = []

        # 1) Extract text concurrently per PDF
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {ex.submit(self.extract_text, item): item for item in pdf_items}
            for fut in as_completed(futures):
                doc_hash, text = fut.result()
                results.append((doc_hash, text))

        # 2) Chunk + build docs (sequential; usually fast vs extraction)
        all_docs: List[Document] = []
        for doc_hash, text in results:
            chunks = self.chunk_text(doc_hash, text)
            all_docs.extend(self._make_documents(doc_hash, chunks))

        # 3) Add to vector DB in batches with retry
        self.add_documents(all_docs)
        logger.info("ingestion_done", extra={"docs": len(all_docs), "pdfs": len(results)})
        return len(all_docs)

# ==================================================================
#  Project   : Neura-Nix - Multimodal AI Assistant {Ollama MultiRag}
#  Author    : UjjwalS (https://www.ujjwalsaini.dev)
#  License   : Apache-2.0
#  Copyright : © 2025 UjjwalS. All rights reserved.
# ==================================================================
# -------------------------
# Public functional API — backwards compatible names
# -------------------------
_cfg = AppCfg.from_dict(load_config())
_ingestor = PDFIngestor(_cfg)


def get_pdf_texts(pdfs_bytes_list: Sequence[BinaryIO | bytes | bytearray | io.BytesIO]) -> List[str]:
    """Backwards‑compatible wrapper: returns a list of extracted texts."""
    out: List[str] = []
    for item in pdfs_bytes_list:
        _, text = _ingestor.extract_text(item)
        out.append(text)
    return out


def get_text_chunks(text: str) -> List[str]:
    """Backwards‑compatible wrapper: chunk a single text string using configured splitter."""
    # Use a per‑text pseudo hash to allow chunk caching even when called directly
    doc_hash = sha256_bytes(text.encode("utf-8"))
    return _ingestor.chunk_text(doc_hash, text)


def get_document_chunks(text_list: Sequence[str]) -> List[Document]:
    """Backwards‑compatible wrapper: convert texts to Document chunks with metadata."""
    docs: List[Document] = []
    for text in text_list:
        h = sha256_bytes(text.encode("utf-8"))
        chunks = _ingestor.chunk_text(h, text)
        docs.extend(_ingestor._make_documents(h, chunks))
    return docs


@log_timed
def add_documents_to_db(pdfs_bytes: Sequence[BinaryIO | bytes | bytearray | io.BytesIO]) -> int:
    """Backwards‑compatible wrapper: ingest and push to DB. Returns number of Document chunks added."""
    return _ingestor.ingest_many(pdfs_bytes)


# -------------------------
# CLI entry point
# -------------------------
CLI_HELP = """
Usage:
  python pdf_ingestion_plus.py file1.pdf [file2.pdf ...]

Environment:
  LOG_LEVEL=INFO|DEBUG|WARNING|ERROR (default INFO)

Notes:
  - Loads application config via utils.load_config(). See module docstring for keys.
  - Requires Redis running if caching is enabled in config.
"""


def _cli(argv: Sequence[str]) -> int:
    if len(argv) <= 1:
        print(CLI_HELP)
        return 0
    filepaths = argv[1:]
    pdf_items: List[bytes] = []
    for fp in filepaths:
        with open(fp, "rb") as f:
            pdf_items.append(f.read())
    count = add_documents_to_db(pdf_items)
    print(f"✅ Added {count} document chunks to the vector DB from {len(filepaths)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv))
