from langgraph.graph import StateGraph, START, END
from src.graph.state import ChatState
from src.graph.nodes.chat import chat_node


def build_graph():
    builder = StateGraph(ChatState)

    builder.add_node("chat", chat_node)

    builder.add_edge(START, "chat")
    builder.add_edge("chat", END)

    return builder.compile()
