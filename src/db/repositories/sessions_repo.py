from src.db.connection import get_conn
from src.utils.logger import get_logger

logger = get_logger(__name__)


def insert(session_id: str, title: str, created_at: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO sessions (session_id, title, created_at) VALUES (?, ?, ?)",
            (session_id, title, created_at),
        )
    logger.info(f"Session row inserted: {session_id}")


def update_title(session_id: str, title: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE sessions SET title = ? WHERE session_id = ?",
            (title, session_id),
        )
    logger.info(f"Session title row updated: {session_id}")


def list_all() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT session_id, title, created_at FROM sessions ORDER BY created_at DESC"
        ).fetchall()
    return [{"session_id": r[0], "title": r[1], "created_at": r[2]} for r in rows]


def delete(session_id: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    logger.info(f"Session row deleted: {session_id}")


def delete_checkpoints(session_id: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM checkpoints WHERE thread_id = ?", (session_id,))
        conn.execute("DELETE FROM writes WHERE thread_id = ?", (session_id,))
    logger.info(f"Checkpoint/write rows cleared for: {session_id}")
