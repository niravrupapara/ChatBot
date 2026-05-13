from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from src.utils.logger import get_logger

logger = get_logger(__name__)

_search = DuckDuckGoSearchRun()


@tool
def web_search(query: str) -> str:
    """Search the web for current information using DuckDuckGo."""
    logger.info(f"Web search: {query}")
    result = _search.run(query)
    logger.info("Web search completed")
    return result
