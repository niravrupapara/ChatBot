import os
from dotenv import load_dotenv
from src.graph.builder import build_graph

load_dotenv()
print("API KEY loaded:", os.getenv("MISTRAL_API_KEY"))

graph = build_graph()


def chat(user_input: str) -> str:
    result = graph.invoke({"messages": [{"role": "user", "content": user_input}]})
    return result["messages"][-1].content


if __name__ == "__main__":
    print("Chatbot ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = chat(user_input)
        print(f"Bot: {response}\n")
