from langchain_core.tools import tool
from src.rag.retriever import retrieve
from src.utils.logger import get_logger

logger = get_logger(__name__)

_session_id: str = ""


def set_session_id(session_id: str):
    global _session_id
    _session_id = session_id
    logger.info(f"RAG tool session set: {session_id}")


def get_session_id() -> str:
    return _session_id


@tool
def rag_search(query: str) -> str:
    """Search the uploaded documents for information relevant to the query."""
    if not _session_id:
        return "No session active. Cannot search documents."

    logger.info(f"RAG search: {query}")
    context = retrieve(query, _session_id)

    if not context:
        return "No relevant information found in uploaded documents."

    return f"Relevant context from uploaded documents:\n\n{context}"
