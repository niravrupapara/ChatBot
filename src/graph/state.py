from typing import Annotated
from langgraph.graph.message import add_messages
from typing import TypedDict


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
