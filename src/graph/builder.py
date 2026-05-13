import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from src.graph.state import ChatState
from src.graph.nodes.chat import chat_node
from src.utils.config_loader import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()


def build_graph():
    builder = StateGraph(ChatState)

    builder.add_node("chat", chat_node)
    builder.add_edge(START, "chat")
    builder.add_edge("chat", END)

    db_path = config["session"]["db_path"]
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    logger.info(f"Graph built with SQLite checkpointer at: {db_path}")

    return builder.compile(checkpointer=checkpointer)
