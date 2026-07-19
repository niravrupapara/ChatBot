from src.db.connection import get_conn
from src.utils.logger import get_logger

logger = get_logger(__name__)


def upsert(namespace: str, key: str, value_json: str, updated_at: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO long_term_memory VALUES (?, ?, ?, ?)",
            (namespace, key, value_json, updated_at),
        )
    logger.info(f"Memory row upserted: {namespace}/{key}")


def search_by_prefix(namespace_prefix: str) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT key, value, updated_at FROM long_term_memory WHERE namespace LIKE ?",
            (namespace_prefix + "%",),
        ).fetchall()
    return [{"key": r[0], "value": r[1], "updated_at": r[2]} for r in rows]
