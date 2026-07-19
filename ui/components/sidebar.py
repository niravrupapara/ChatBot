import streamlit as st
from src.services.session_service import (
    generate_session_id,
    list_sessions,
    delete_session,
)
from ui.components.file_upload import render_file_upload
from src.utils.logger import get_logger

logger = get_logger(__name__)


def render_sidebar() -> None:
    with st.sidebar:
        st.title("Chats")

        # New chat button
        if st.button("+ New Chat", use_container_width=True):
            st.session_state.session_id = generate_session_id()
            logger.info("New chat started from sidebar")
            st.rerun()

        st.divider()

        # List past sessions
        sessions = list_sessions()

        if not sessions:
            st.caption("No previous chats.")
            return

        for session in sessions:
            col1, col2 = st.columns([5, 1])

            with col1:
                is_active = session["session_id"] == st.session_state.get("session_id")
                label = f"**{session['title']}**" if is_active else session["title"]
                if st.button(label, key=f"load_{session['session_id']}", use_container_width=True):
                    st.session_state.session_id = session["session_id"]
                    logger.info(f"Session loaded: {session['session_id']}")
                    st.rerun()

            with col2:
                if st.button("🗑", key=f"del_{session['session_id']}"):
                    delete_session(session["session_id"])
                    logger.info(f"Session deleted from sidebar: {session['session_id']}")
                    # If deleted session was active, start a new one
                    if is_active:
                        st.session_state.session_id = generate_session_id()
                    st.rerun()

    render_file_upload(st.session_state.session_id)
