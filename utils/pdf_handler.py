import logging
import pypdfium2
from typing import List, BinaryIO
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from vectordb_handler import load_vectordb
from utils import load_config, timeit

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

config = load_config()
splitter_cfg = config.get("pdf_text_splitter", {})


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from a single PDF file.
    """
    with pypdfium2.PdfDocument(pdf_bytes) as pdf_file:
        return "\n".join(
            pdf_file.get_page(page_number).get_textpage().get_text_range()
            for page_number in range(len(pdf_file))
        )


def get_pdf_texts(pdfs_bytes_list: List[BinaryIO]) -> List[str]:
    """
    Extract texts from a list of PDF byte streams.
    """
    return [extract_text_from_pdf(pdf_bytes.getvalue()) for pdf_bytes in pdfs_bytes_list]


def get_text_chunks(text: str) -> List[str]:
    """
    Split text into overlapping chunks for vector storage.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=splitter_cfg.get("chunk_size", 1000),
        chunk_overlap=splitter_cfg.get("overlap", 100),
        separators=splitter_cfg.get("separators"),
    )
    return splitter.split_text(text)


def get_document_chunks(text_list: List[str]) -> List[Document]:
    """
    Convert list of raw texts into a list of Document chunks.
    """
    return [
        Document(page_content=chunk)
        for text in text_list
        for chunk in get_text_chunks(text)
    ]


@timeit
def add_documents_to_db(pdfs_bytes: List[BinaryIO]) -> None:
    """
    Extracts text from PDFs, chunks it, and stores it in the vector DB.
    """
    texts = get_pdf_texts(pdfs_bytes)
    documents = get_document_chunks(texts)

    vector_db = load_vectordb()
    vector_db.add_documents(documents)

    logging.info("✅ %d documents added to the vector database.", len(documents))
