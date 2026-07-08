import os
from mistralai import Mistral
from src.utils.logger import get_logger

logger = get_logger(__name__)

_client : Mistral | None = None

def get_mistral_client() -> Mistral:
    """Singleton Mistral client - one instance shared across the app."""
    global _client
    if _client is None:
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise RuntimeError("MISTRAL_API_KEY not set in environment")
        _client = Mistral(api_key=api_key)
        logger.info("Mistral client initialized")
    return _client



