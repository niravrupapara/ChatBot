import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
load_dotenv()


from src.db.schema import init_schema
from src.graph.builder import build_graph
from src.session.manager import generate_session_id, update_session_title, generate_title
from src.utils.logger import get_logger
from src.utils.runtime_config import reset_tool_calls, get_tool_calls
from ui.components.sidebar import render_sidebar

logger = get_logger(__name__)

init_schema()

st.set_page_config(page_title="Chatbot", page_icon="🤖", layout="wide")

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()

render_sidebar()

# Deferred title generation — runs after first response is shown
if st.session_state.get("needs_title"):
    session_id = st.session_state.session_id
    first_msg = st.session_state.pop("first_message", "")
    logger.info(f"Generating title for session: {session_id}")
    title = generate_title(first_msg)
    update_session_title(session_id, title)
    st.session_state.needs_title = False
    st.rerun()

st.title("Chatbot")

graph = st.session_state.graph
thread_config = {"configurable": {"thread_id": st.session_state.session_id}}

# Load and display all messages from persisted graph state
state = graph.get_state(thread_config)
messages = state.values.get("messages", []) if state.values else []

for i, msg in enumerate(messages):
    is_user = msg.type == "human"
    message(msg.content, is_user=is_user, key=f"msg_{i}")

if st.session_state.get("last_tools_used"):
    st.caption(f"🔧 Tools used: {', '.join(st.session_state['last_tools_used'])}")

user_input = st.chat_input("Type your message...")
if user_input:
    # Flag title generation for after first response is shown
    if len(messages) == 0:
        st.session_state.needs_title = True
        st.session_state.first_message = user_input
        logger.info("First message detected — title generation deferred")

    message(user_input, is_user=True, key="user_input_current")

    with st.spinner("Thinking..."):
        reset_tool_calls()
        graph.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=thread_config
        )
        tools_used = get_tool_calls()

    if tools_used:
        st.session_state["last_tools_used"] = tools_used
        logger.info(f"Tools used this turn: {tools_used}")
    else:
        st.session_state.pop("last_tools_used", None)

    st.rerun()
