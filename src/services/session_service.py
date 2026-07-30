import uuid
from datetime import datetime

from src.db.models import Session
from src.db.repositories import sessions_repo
from src.rag.retriever import delete_session_documents
from src.utils.llm_client import get_mistral_client
from src.utils.config_loader import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()

_mistral = get_mistral_client()


def generate_session_id(title: str = "New Chat") -> str:
    session_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat(timespec="seconds")
    sessions_repo.insert(session_id, title, created_at)
    logger.info(f"New session created: {session_id}")
    return session_id


def update_session_title(session_id: str, title: str) -> None:
    # Called after first user message to set a meaningful title
    short_title = title[:40] + "..." if len(title) > 40 else title
    sessions_repo.update_title(session_id, short_title)
    logger.info(f"Session title updated: {session_id} → '{short_title}'")


def generate_title(user_message: str) -> str:
    logger.info("Generating session title via LLM")
    prompt = (
        f"""
You are a chat title generator.

Generate a concise and descriptive title for the conversation.

Rules:
- Maximum 4 words
- No quotes
- No punctuation
- No emojis
- Do not respond like an assistant
- Avoid generic titles like "Hello", "Hi there", "Chat"
- Focus on the user's intent/topic

Examples:
hello -> Friendly Chat
hey bro -> Casual Conversation
how to learn python -> Learning Python
build rag chatbot -> RAG Chatbot
fix streamlit rerun issue -> Streamlit Rerun Fix

User message:
{user_message}

Title:
"""
    )
    try:
        response = _mistral.chat.complete(
            model=config["model"]["name"],
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=30,
        )
        title = response.choices[0].message.content.strip()
        logger.info(f"LLM title generated: '{title}'")
        return title
    except Exception as e:
        logger.warning(f"Title generation failed, using fallback: {e}")
        return user_message[:30] + "..." if len(user_message) > 30 else user_message


def list_sessions() -> list[Session]:
    sessions = sessions_repo.list_all()
    logger.info(f"Listed {len(sessions)} sessions")
    return sessions


def delete_session(session_id: str) -> None:
    sessions_repo.delete(session_id)
    sessions_repo.delete_checkpoints(session_id)
    delete_session_documents(session_id)
    logger.info(f"Session deleted: {session_id}")
