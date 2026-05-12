from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from src.graph.state import ChatState
from src.utils.config_loader import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()

llm = ChatGoogleGenerativeAI(
    model=config["model"]["name"],
    temperature=config["model"]["temperature"],
    max_output_tokens=config["model"]["max_tokens"],
)


def chat_node(state: ChatState) -> dict:
    user_msg = state["messages"][-1].content
    logger.info(f"User: {user_msg}")

    response = llm.invoke(state["messages"])

    logger.info("response received")
    return {"messages": [response]}
