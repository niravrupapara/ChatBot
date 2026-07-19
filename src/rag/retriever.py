from src.rag.ingestion import ingest_file
from src.rag.embeddings import add_chunks, query_chunks, has_documents, delete_session_index
from src.utils.logger import get_logger

logger = get_logger(__name__)


def index_document(file_path: str, session_id: str):
    logger.info(f"Indexing document: {file_path} for session: {session_id}")
    chunks = ingest_file(file_path)
    add_chunks(chunks, session_id)
    logger.info("Document indexed successfully")


def retrieve(query: str, session_id: str) -> str:
    chunks = query_chunks(query, session_id)
    if not chunks:
        return ""
    return "\n\n---\n\n".join(chunks)


def session_has_documents(session_id: str) -> bool:
    return has_documents(session_id)


def delete_session_documents(session_id: str) -> None:
    delete_session_index(session_id)
