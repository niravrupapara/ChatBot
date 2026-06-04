import streamlit as st
from src.utils.runtime_config import set_override, get_override
from src.utils.config_loader import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
st.title("Settings")
st.caption("Changes apply immediately — reset on app restart.")

# --- Model Settings ---
st.subheader("Model")

model = st.selectbox(
    "Model",
    options=["mistral-small-latest", "mistral-medium-latest", "mistral-large-latest"],
    index=["mistral-small-latest", "mistral-medium-latest", "mistral-large-latest"].index(
        get_override("model_name", config["model"]["name"])
    ),
)
set_override("model_name", model)

temperature = st.slider(
    "Temperature",
    min_value=0.0, max_value=1.0,
    value=get_override("temperature", config["model"]["temperature"]),
    step=0.05,
    help="Higher = more creative, Lower = more focused",
)
set_override("temperature", temperature)

max_tokens = st.slider(
    "Max Tokens",
    min_value=256, max_value=4096,
    value=get_override("max_tokens", config["model"]["max_tokens"]),
    step=128,
    help="Maximum length of each response",
)
set_override("max_tokens", max_tokens)

st.divider()

# --- Memory Settings ---
st.subheader("Memory")

window_size = st.slider(
    "Window Size",
    min_value=4, max_value=20,
    value=get_override("window_size", config["memory"]["window_size"]),
    step=1,
    help="Number of recent messages sent to the LLM",
)
set_override("window_size", window_size)

summary_threshold = st.slider(
    "Summary Threshold",
    min_value=10, max_value=50,
    value=get_override("summary_threshold", config["memory"]["summary_threshold"]),
    step=2,
    help="How many messages before old ones get summarized",
)
set_override("summary_threshold", summary_threshold)

st.divider()

# --- RAG Settings ---
st.subheader("RAG")

top_k = st.slider(
    "Top K",
    min_value=1, max_value=10,
    value=get_override("top_k", config["rag"]["top_k"]),
    step=1,
    help="Number of document chunks retrieved for each query",
)
set_override("top_k", top_k)

logger.info(f"Settings page rendered | model={model} temp={temperature} tokens={max_tokens} window={window_size} threshold={summary_threshold} top_k={top_k}")
