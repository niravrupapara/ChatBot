import os
import json
from dotenv import load_dotenv
load_dotenv()

from mistralai import Mistral
from langchain_core.messages import AIMessage
from src.graph.state import ChatState
from src.agents.tools import ALL_TOOLS
from src.agents.tools.rag_search import get_session_id
from src.rag.retriever import session_has_documents
from src.utils.config_loader import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

TOOL_MAP = {t.name: t for t in ALL_TOOLS}


def _to_mistral_format(messages: list) -> list:
    role_map = {"human": "user", "ai": "assistant", "system": "system"}
    return [{"role": role_map.get(msg.type, "user"), "content": msg.content} for msg in messages]


def _get_mistral_tools() -> list:
    tools = []
    for t in ALL_TOOLS:
        schema = t.args_schema.schema() if t.args_schema else {"type": "object", "properties": {}}
        schema.pop("title", None)
        tools.append({
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": schema,
            }
        })
    return tools


def _build_system_message() -> dict | None:
    session_id = get_session_id()
    if session_id and session_has_documents(session_id):
        return {"role": "system", "content": "The user has uploaded documents. When answering questions about their content, always use the rag_search tool to find relevant information before responding."}
    return None


def agent_node(state: ChatState) -> dict:
    logger.info("Agent node activated")
    messages = _to_mistral_format(state["messages"])
    mistral_tools = _get_mistral_tools()

    system_msg = _build_system_message()
    if system_msg:
        messages = [system_msg] + messages
        logger.info("RAG system prompt injected")

    while True:
        response = client.chat.complete(
            model=config["model"]["name"],
            messages=messages,
            tools=mistral_tools,
            temperature=config["model"]["temperature"],
        )

        msg = response.choices[0].message

        # No tool call — final answer
        if not msg.tool_calls:
            logger.info("Agent final response ready")
            return {"messages": [AIMessage(content=msg.content)]}

        # Add assistant message with tool calls to history
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                }
                for tc in msg.tool_calls
            ]
        })

        # Execute each tool and add result to history
        for tc in msg.tool_calls:
            tool_name = tc.function.name
            tool_args = json.loads(tc.function.arguments)
            logger.info(f"Calling tool: {tool_name} | args: {tool_args}")

            tool_fn = TOOL_MAP.get(tool_name)
            tool_result = tool_fn.invoke(tool_args) if tool_fn else f"Tool '{tool_name}' not found."
            logger.info(f"Tool result received: {tool_name}")

            messages.append({
                "role": "tool",
                "content": str(tool_result),
                "tool_call_id": tc.id,
            })
