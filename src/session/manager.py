import uuid
import sqlite3
from datetime import datetime
from src.utils.config_loader import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()
DB_PATH = config["session"]["db_path"]


def _get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def setup_sessions_table() -> None:
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id  TEXT PRIMARY KEY,
                title       TEXT,
                created_at  TEXT
            )
        """)
    logger.info("Sessions table ready")


def generate_session_id(title: str = "New Chat") -> str:
    session_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO sessions (session_id, title, created_at) VALUES (?, ?, ?)",
            (session_id, title, created_at),
        )
    logger.info(f"New session created: {session_id}")
    return session_id


def update_session_title(session_id: str, title: str) -> None:
    # Called after first user message to set a meaningful title
    short_title = title[:40] + "..." if len(title) > 40 else title
    with _get_conn() as conn:
        conn.execute(
            "UPDATE sessions SET title = ? WHERE session_id = ?",
            (short_title, session_id),
        )
    logger.info(f"Session title updated: {session_id} → '{short_title}'")


def list_sessions() -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT session_id, title, created_at FROM sessions ORDER BY created_at DESC"
        ).fetchall()
    sessions = [{"session_id": r[0], "title": r[1], "created_at": r[2]} for r in rows]
    logger.info(f"Listed {len(sessions)} sessions")
    return sessions


def delete_session(session_id: str) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    logger.info(f"Session deleted: {session_id}")
