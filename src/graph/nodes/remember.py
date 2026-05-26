from langgraph.store.base import BaseStore
from src.memory.long_term import extract_facts, format_memories, NAMESPACE, KEY
from src.graph.state import ChatState
from src.utils.logger import get_logger

logger = get_logger(__name__)


def remember_node(state: ChatState, store: BaseStore) -> dict:
    logger.info("Remember node activated")

    # Load existing memory profile
    existing_items = store.search(NAMESPACE)
    existing = existing_items[0].value if existing_items else {}

    # Extract new facts from recent messages
    new_facts = extract_facts(state["messages"], existing)

    # Save only if new facts found
    if new_facts:
        merged = {**existing, **new_facts}
        store.put(NAMESPACE, KEY, merged)
        logger.info(f"Memory updated with {len(new_facts)} new facts")

    return {}
