import streamlit as st
from dotenv import load_dotenv
from src.graph.builder import build_graph
from src.session.manager import generate_session_id
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

st.set_page_config(page_title="Chatbot", page_icon="🤖")
st.title("Chatbot")

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()

graph = st.session_state.graph
thread_config = {"configurable": {"thread_id": st.session_state.session_id}}

# Load and display all messages from persisted graph state
state = graph.get_state(thread_config)
messages = state.values.get("messages", []) if state.values else []

for msg in messages:
    role = "user" if msg.type == "human" else "assistant"
    with st.chat_message(role):
        st.write(msg.content)

input = st.chat_input("Type your message...")
if input:
    with st.spinner("Thinking..."):
        graph.invoke(
            {"messages": [{"role": "user", "content": input}]},
            config=thread_config
        )
    st.rerun()
