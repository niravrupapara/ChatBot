import uuid
from datetime import datetime

from src.utils.db import get_conn
from src.utils.llm_client import get_mistral_client
from src.utils.config_loader import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()




_mistral = get_mistral_client()



def _init_db() -> None:
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id  TEXT PRIMARY KEY,
                title       TEXT,
                created_at  TEXT
            )
        """)
    logger.info("Sessions table ready")


_init_db()


def setup_sessions_table() -> None:
    _init_db()


def generate_session_id(title: str = "New Chat") -> str:
    session_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO sessions (session_id, title, created_at) VALUES (?, ?, ?)",
            (session_id, title, created_at),
        )
    logger.info(f"New session created: {session_id}")
    return session_id


def update_session_title(session_id: str, title: str) -> None:
    # Called after first user message to set a meaningful title
    short_title = title[:40] + "..." if len(title) > 40 else title
    with get_conn() as conn:
        conn.execute(
            "UPDATE sessions SET title = ? WHERE session_id = ?",
            (short_title, session_id),
        )
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
            temperature=0.3,
        )
        title = response.choices[0].message.content.strip()
        logger.info(f"LLM title generated: '{title}'")
        return title
    except Exception as e:
        logger.warning(f"Title generation failed, using fallback: {e}")
        return user_message[:40] + "..." if len(user_message) > 40 else user_message


def list_sessions() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT session_id, title, created_at FROM sessions ORDER BY created_at DESC"
        ).fetchall()
    sessions = [{"session_id": r[0], "title": r[1], "created_at": r[2]} for r in rows]
    logger.info(f"Listed {len(sessions)} sessions")
    return sessions


def delete_session(session_id: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    logger.info(f"Session deleted: {session_id}")
