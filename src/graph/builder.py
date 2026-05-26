import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from src.graph.state import ChatState
from src.graph.nodes.agent import agent_node
from src.graph.nodes.remember import remember_node
from src.memory.long_term import SqliteStore
from src.utils.config_loader import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()


def build_graph():
    builder = StateGraph(ChatState)

    # remember and agent run in parallel — no latency added
    builder.add_node("remember", remember_node)
    builder.add_node("agent", agent_node)

    builder.add_edge(START, "remember")
    builder.add_edge(START, "agent")
    builder.add_edge("remember", END)
    builder.add_edge("agent", END)

    db_path = config["session"]["db_path"]
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    store = SqliteStore(db_path)

    logger.info(f"Graph built: remember → agent | SQLite: {db_path}")

    return builder.compile(checkpointer=checkpointer, store=store)
