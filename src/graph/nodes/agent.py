import json


from langchain_core.messages import AIMessage
from langgraph.store.base import BaseStore
from src.graph.state import ChatState
from src.agents.tools import ALL_TOOLS
from src.agents.tools.rag_search import get_session_id
from src.rag.retriever import session_has_documents
from src.memory.short_term import should_summarize, summarize_messages
from src.memory.long_term import format_memories, NAMESPACE

from src.utils.llm_client import get_mistral_client
from src.utils.config_loader import load_config
from src.utils.runtime_config import get_override, add_tool_call
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()


client = get_mistral_client()

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


MISTRAL_TOOLS = _get_mistral_tools()

MAX_TOOL_ITERATIONS = 10


def _build_system_message() -> dict | None:
    session_id = get_session_id()
    if session_id and session_has_documents(session_id):
        return {"role": "system", "content": "The user has uploaded documents. When answering questions about their content, always use the rag_search tool to find relevant information before responding."}
    return None


def agent_node(state: ChatState, store: BaseStore) -> dict:
    logger.info("Agent node activated")
    all_messages = state["messages"]
    existing_summary = state.get("summary", "")
    window = get_override("window_size", config.get("memory", {}).get("window_size", 10))
    threshold = get_override("summary_threshold", config.get("memory", {}).get("summary_threshold", 20))
    new_summary = existing_summary

    # Summarize old messages if threshold exceeded
    if should_summarize(all_messages, threshold):
        old_messages = all_messages[:-window]
        new_summary = summarize_messages(old_messages, existing_summary)
        logger.info("Conversation summarized")

    # Build LLM context: summary (if any) + recent messages only
    recent = _to_mistral_format(all_messages[-window:])
    if new_summary:
        messages = [{"role": "system", "content": f"Summary of earlier conversation:\n{new_summary}"}] + recent
    else:
        messages = recent

    # Build system messages: long-term memory + RAG
    system_messages = []

    memory_items = store.search(NAMESPACE)
    memory_text = format_memories(memory_items)
    if memory_text:
        system_messages.append({"role": "system", "content": memory_text})
        logger.info("Long-term memory injected")

    rag_msg = _build_system_message()
    if rag_msg:
        system_messages.append(rag_msg)
        logger.info("RAG system prompt injected")

    if system_messages:
        messages = system_messages + messages

    model_name = get_override("model_name", config["model"]["name"])
    temperature = get_override("temperature", config["model"]["temperature"])
    max_tokens = get_override("max_tokens", config["model"]["max_tokens"])
    logger.info(f"LLM call | model={model_name} temp={temperature} max_tokens={max_tokens}")

    for iteration in range(MAX_TOOL_ITERATIONS):
        response = client.chat.complete(
            model=model_name,
            messages=messages,
            tools=MISTRAL_TOOLS,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        msg = response.choices[0].message

        # No tool call — final answer
        if not msg.tool_calls:
            logger.info("Agent final response ready")
            return {"messages": [AIMessage(content=msg.content)], "summary": new_summary}

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
            logger.info(f"Calling tool: {tool_name} | args: {tool_args} | iter: {iteration + 1}")

            tool_fn = TOOL_MAP.get(tool_name)
            tool_result = tool_fn.invoke(tool_args) if tool_fn else f"Tool '{tool_name}' not found."
            add_tool_call(tool_name)
            logger.info(f"Tool result received: {tool_name}")

            messages.append({
                "role": "tool",
                "content": str(tool_result),
                "tool_call_id": tc.id,
            })

    logger.warning(f"Tool loop hit max iterations ({MAX_TOOL_ITERATIONS}) without final answer")
    fallback = (
        f"I wasn't able to complete this request after {MAX_TOOL_ITERATIONS} tool calls. "
        "Could you rephrase or simplify the question?"
    )
    return {"messages": [AIMessage(content=fallback)], "summary": new_summary}
