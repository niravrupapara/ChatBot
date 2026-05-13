import os
from dotenv import load_dotenv
load_dotenv()

from mistralai import Mistral
from langchain_core.messages import AIMessage
from src.graph.state import ChatState
from src.utils.config_loader import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))


def _to_mistral_format(messages: list) -> list:
    role_map = {"human": "user", "ai": "assistant", "system": "system"}
    return [{"role": role_map.get(msg.type, "user"), "content": msg.content} for msg in messages]


def chat_node(state: ChatState) -> dict:
    user_msg = state["messages"][-1].content
    logger.info(f"User: {user_msg}")

    response = client.chat.complete(
        model=config["model"]["name"],
        messages=_to_mistral_format(state["messages"]),
        temperature=config["model"]["temperature"],
        max_tokens=config["model"]["max_tokens"],
    )

    reply = response.choices[0].message.content
    logger.info("Response received")

    return {"messages": [AIMessage(content=reply)]}
