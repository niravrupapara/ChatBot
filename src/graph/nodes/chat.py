from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from src.graph.state import ChatState
from src.utils.config_loader import load_config

config = load_config()

llm = ChatGoogleGenerativeAI(
    model=config["model"]["name"],
    temperature=config["model"]["temperature"],
    max_output_tokens=config["model"]["max_tokens"],
)


def chat_node(state: ChatState) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}
