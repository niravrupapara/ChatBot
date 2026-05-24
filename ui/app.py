import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
from src.graph.builder import build_graph
from src.session.manager import generate_session_id, update_session_title
from src.utils.logger import get_logger
from ui.components.sidebar import render_sidebar

load_dotenv()
logger = get_logger(__name__)

st.set_page_config(page_title="Chatbot", page_icon="🤖", layout="wide")

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()

render_sidebar()

st.title("Chatbot")

graph = st.session_state.graph
thread_config = {"configurable": {"thread_id": st.session_state.session_id}}

# Load and display all messages from persisted graph state
state = graph.get_state(thread_config)
messages = state.values.get("messages", []) if state.values else []

for i, msg in enumerate(messages):
    is_user = msg.type == "human"
    message(msg.content, is_user=is_user, key=f"msg_{i}" )

user_input = st.chat_input("Type your message...")
if user_input:
    # Update session title from first user message
    if len(messages) == 0:
        update_session_title(st.session_state.session_id, user_input)

    message(user_input, is_user=True, key="user_input_current")

    with st.spinner("Thinking..."):
        graph.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=thread_config
        )
    st.rerun()
