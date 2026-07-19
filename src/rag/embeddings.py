import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from src.utils.config_loader import load_config
from src.utils.runtime_config import get_override
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()

_model = None
_index_cache: dict = {}  # session_id -> (faiss_index, chunks_list)


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        model_name = config["rag"]["embedding_model"]
        logger.info(f"Loading embedding model: {model_name}")
        _model = SentenceTransformer(model_name)
    return _model


def _get_paths(session_id: str) -> tuple[str, str]:
    base = config["rag"]["vector_store_path"]
    os.makedirs(base, exist_ok=True)
    return (
        os.path.join(base, f"{session_id}.index"),
        os.path.join(base, f"{session_id}.pkl"),
    )


def add_chunks(chunks: list[str], session_id: str):
    model = _get_model()
    index_file, chunks_file = _get_paths(session_id)

    embeddings = model.encode(chunks).astype("float32")

    if os.path.exists(index_file):
        index = faiss.read_index(index_file)
        with open(chunks_file, "rb") as f:
            stored_chunks = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(embeddings.shape[1])
        stored_chunks = []

    index.add(embeddings)
    stored_chunks.extend(chunks)

    faiss.write_index(index, index_file)
    with open(chunks_file, "wb") as f:
        pickle.dump(stored_chunks, f)

    # Invalidate cache — next query will reload with the new chunks
    if session_id in _index_cache:
        _index_cache.pop(session_id)
        logger.info(f"Cache invalidated for session: {session_id}")

    logger.info(f"Stored {len(chunks)} chunks for session: {session_id}")


def query_chunks(query: str, session_id: str) -> list[str]:
    index_file, chunks_file = _get_paths(session_id)

    if not os.path.exists(index_file):
        logger.info("No index found for session")
        return []

    model = _get_model()
    top_k = get_override("top_k", config["rag"]["top_k"])
    logger.info(f"RAG query | top_k={top_k}")

    query_embedding = model.encode([query]).astype("float32")

    if session_id in _index_cache:
        index, stored_chunks = _index_cache[session_id]
        logger.info(f"RAG cache hit | session={session_id}")
    else:
        index = faiss.read_index(index_file)
        with open(chunks_file, "rb") as f:
            stored_chunks = pickle.load(f)
        _index_cache[session_id] = (index, stored_chunks)
        logger.info(f"RAG cache miss — loaded from disk | session={session_id}")

    _, indices = index.search(query_embedding, top_k)
    results = [stored_chunks[i] for i in indices[0] if i < len(stored_chunks)]

    logger.info(f"Retrieved {len(results)} chunks for session: {session_id}")
    return results


def has_documents(session_id: str) -> bool:
    index_file, _ = _get_paths(session_id)
    return os.path.exists(index_file)


def delete_session_index(session_id: str) -> None:
    index_file, chunks_file = _get_paths(session_id)
    removed = False
    for path in (index_file, chunks_file):
        if os.path.exists(path):
            os.remove(path)
            removed = True
    _index_cache.pop(session_id, None)
    if removed:
        logger.info(f"Deleted FAISS index for session: {session_id}")
    else:
        logger.info(f"No FAISS index found for session: {session_id}")
