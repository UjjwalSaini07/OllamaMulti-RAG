import logging
import chromadb
from functools import lru_cache
from typing import Optional
from utils import load_config
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

config = load_config()

def get_ollama_embeddings() -> OllamaEmbeddings:
    try:
        model = config["ollama"]["embedding_model"]
        base_url = config["ollama"].get("base_url", "http://localhost:11434")
        logger.info("Loading Ollama embeddings (model=%s, base_url=%s)", model, base_url)
        return OllamaEmbeddings(model=model, base_url=base_url)
    except Exception as e:
        logger.error("Failed to initialize Ollama embeddings: %s", e)
        raise

#  Author: UjjwalS (https://www.ujjwalsaini.dev)
@lru_cache(maxsize=1)
def load_vectordb(embeddings: Optional[OllamaEmbeddings] = None) -> Chroma:
    try:
        embeddings = embeddings or get_ollama_embeddings()

        db_path = config["chromadb"].get("chromadb_path", "./chroma_db")
        collection_name = config["chromadb"].get("collection_name", "default")

        logger.info("Connecting to ChromaDB at %s (collection=%s)", db_path, collection_name)

        persistent_client = chromadb.PersistentClient(path=db_path)

        langchain_chroma = Chroma(
            client=persistent_client,
            collection_name=collection_name,
            embedding_function=embeddings,
        )

        logger.info("VectorDB loaded successfully.")
        return langchain_chroma

    except Exception as e:
        logger.error("Failed to load vector DB: %s", e)
        raise

