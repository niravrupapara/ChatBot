import sqlite3

from src.db.connection import get_conn
from src.utils.logger import get_logger

logger = get_logger(__name__)

_initialized = False


def init_schema(conn: sqlite3.Connection | None = None) -> None:
    """Create all application tables. Runs once per process — safe to call freely.

    LangGraph's SqliteSaver auto-creates its own `checkpoints` / `writes` tables,
    so we don't manage those here.
    """
    global _initialized
    if _initialized:
        return

    own_conn = conn is None
    if own_conn:
        conn = get_conn()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id  TEXT PRIMARY KEY,
                title       TEXT,
                created_at  TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memory (
                namespace  TEXT,
                key        TEXT,
                value      TEXT,
                updated_at TEXT,
                PRIMARY KEY (namespace, key)
            )
        """)
        conn.commit()
        _initialized = True
        logger.info("Schema initialized")
    finally:
        if own_conn:
            conn.close()
