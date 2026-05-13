import numexpr
from langchain_core.tools import tool
from src.utils.logger import get_logger

logger = get_logger(__name__)


@tool
def calculator(expression: str) -> str:
    """Safely evaluate a math expression. Example: '2 + 2', 'sqrt(16)', '3 * (4 + 5)'"""
    logger.info(f"Calculator expression: {expression}")
    try:
        result = numexpr.evaluate(expression).item()
        logger.info(f"Calculator result: {result}")
        return str(result)
    except Exception as e:
        logger.warning(f"Calculator error: {e}")
        return f"Could not evaluate expression: {e}"
