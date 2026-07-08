import json
import sqlite3
from datetime import datetime
from typing import Iterable


from langgraph.store.base import (
    BaseStore, PutOp, SearchOp,
    SearchItem, Op, Result,
)

from src.utils.llm_client import get_mistral_client
from src.utils.config_loader import load_config
from src.utils.logger import get_logger



logger = get_logger(__name__)
config = load_config()
_mistral = get_mistral_client()


# --- SQLite-backed LangGraph Store ---

class SqliteStore(BaseStore):
    """Persistent store — saves memories to SQLite, survives app restarts."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._setup()
        logger.info("SqliteStore ready")

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _setup(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    namespace  TEXT,
                    key        TEXT,
                    value      TEXT,
                    updated_at TEXT,
                    PRIMARY KEY (namespace, key)
                )
            """)

    async def abatch(self, ops: Iterable[Op]) -> list[Result]:
        return self.batch(ops)

    def batch(self, ops: Iterable[Op]) -> list[Result]:
        results = []
        for op in ops:
            if isinstance(op, PutOp):
                self._put(op.namespace, op.key, op.value)
                results.append(None)
            elif isinstance(op, SearchOp):
                results.append(self._search(op.namespace_prefix))
            else:
                results.append(None)
        return results

    def _put(self, namespace: tuple, key: str, value: dict):
        ns = ".".join(namespace)
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO long_term_memory VALUES (?, ?, ?, ?)",
                (ns, key, json.dumps(value), datetime.now().isoformat()),
            )
        logger.info(f"Memory saved → {ns}/{key}")

    def _search(self, namespace_prefix: tuple) -> list[SearchItem]:
        ns = ".".join(namespace_prefix)
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT key, value, updated_at FROM long_term_memory WHERE namespace LIKE ?",
                (ns + "%",),
            ).fetchall()
        logger.info(f"Memory search → {ns} | found {len(rows)}")
        return [
            SearchItem(
                value=json.loads(r[1]),
                key=r[0],
                namespace=namespace_prefix,
                created_at=datetime.fromisoformat(r[2]),
                updated_at=datetime.fromisoformat(r[2]),
                score=None,
            )
            for r in rows
        ]


# --- Helper Functions ---

NAMESPACE = ("memories", "user")
KEY = "profile"


def extract_facts(messages: list, existing: dict) -> dict:
    """Extract new user facts from recent messages using Mistral."""
    text = "\n".join(
        f"{m.type.upper()}: {m.content}"
        for m in messages[-6:]
        if hasattr(m, "content") and m.content
    )
    existing_str = json.dumps(existing) if existing else "{}"
    prompt = f"""Extract new facts about the user from this conversation.
Return only facts NOT already in the existing profile.
Return a flat JSON object. Return {{}} if nothing new found.

Existing: {existing_str}
Conversation:
{text}

JSON only:"""

    try:
        response = _mistral.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip().strip("```json").strip("```").strip()
        facts = json.loads(raw)
        logger.info(f"Facts extracted: {list(facts.keys())}")
        return facts
    except Exception as e:
        logger.warning(f"Fact extraction failed: {e}")
        return {}


def format_memories(items: list) -> str:
    """Format stored memories as system prompt string."""
    if not items:
        return ""
    profile = items[0].value if items else {}
    if not profile:
        return ""
    facts = "\n".join(f"- {k}: {v}" for k, v in profile.items())
    logger.info(f"Memories loaded: {len(profile)} facts")
    return f"Known facts about the user:\n{facts}"
