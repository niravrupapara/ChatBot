import uuid
from src.utils.logger import get_logger

logger = get_logger(__name__)


def generate_session_id() -> str:
    session_id = str(uuid.uuid4())
    logger.info(f"New session started: {session_id}")
    return session_id
