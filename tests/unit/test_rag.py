import os
import shutil
from src.rag.embeddings import add_chunks, query_chunks, delete_session_index

def test_query_chunks_bounds():
    session_id = "test_session_bounds"
    delete_session_index(session_id)
    try:
        # Add only 1 chunk to the index
        add_chunks(["Single test chunk content"], session_id)

        # Query with top_k > available chunks (default top_k is 3)
        results = query_chunks("test query", session_id)

        # Must return exactly 1 chunk, NOT 3 (which would happen if -1 index returned stored_chunks[-1])
        assert len(results) == 1
        assert results[0] == "Single test chunk content"
        print("All RAG bounds tests passed successfully!")
    finally:
        delete_session_index(session_id)

if __name__ == "__main__":
    test_query_chunks_bounds()

