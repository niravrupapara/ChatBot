from dotenv import load_dotenv
from src.graph.builder import build_graph
from src.session.manager import generate_session_id
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

graph = build_graph()
session_id = generate_session_id()
thread_config = {"configurable": {"thread_id": session_id}}


def chat(user_input: str) -> str:
    result = graph.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=thread_config
    )
    return result["messages"][-1].content


if __name__ == "__main__":
    print(f"Session ID: {session_id}")
    print("Chatbot ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = chat(user_input)
        print(f"Bot: {response}\n")
