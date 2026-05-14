import os
import tempfile
import streamlit as st
from src.rag.retriever import index_document
from src.agents.tools.rag_search import set_session_id
from src.utils.logger import get_logger

logger = get_logger(__name__)


def render_file_upload(session_id: str):
    set_session_id(session_id)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Documents**")

    uploaded_file = st.sidebar.file_uploader(
        "Upload a file",
        type=["pdf", "txt"],
        key=f"upload_{session_id}",
    )

    if uploaded_file:
        doc_name = uploaded_file.name
        already_uploaded = doc_name in st.session_state.get("uploaded_docs", [])

        if not already_uploaded:
            with st.sidebar.status(f"Indexing {doc_name}..."):
                suffix = os.path.splitext(doc_name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                index_document(tmp_path, session_id)
                os.unlink(tmp_path)

                if "uploaded_docs" not in st.session_state:
                    st.session_state.uploaded_docs = []
                st.session_state.uploaded_docs.append(doc_name)

            logger.info(f"Document indexed: {doc_name} for session: {session_id}")

    if st.session_state.get("uploaded_docs"):
        for doc in st.session_state.uploaded_docs:
            st.sidebar.caption(f"📄 {doc}")
