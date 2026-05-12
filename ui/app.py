import streamlit as st
from dotenv import load_dotenv
from src.graph.builder import build_graph
from src.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

st.set_page_config(page_title="Chatbot", page_icon="🤖")
st.title("Chatbot")

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()
    logger.info("Graph initialized")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.spinner("Thinking..."):
        result = st.session_state.graph.invoke(
            {"messages": [{"role": "user", "content": prompt}]}
        )
        response = result["messages"][-1].content

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
