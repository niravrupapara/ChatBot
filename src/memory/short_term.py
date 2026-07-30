from src.utils.config_loader import load_config

from src.utils.llm_client import get_mistral_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

config = load_config()


client = get_mistral_client()


def should_summarize(
    messages: list,
    threshold: int = 20,
    existing_summary: str = "",
    window: int = 6
) -> bool:
    if not existing_summary:
        return len(messages) > threshold
    # If summary already exists, only re-summarize when a full new batch accumulates
    unsummarized = len(messages) - window
    return unsummarized >= threshold * 2


def summarize_messages(old_messages: list, existing_summary: str = "") -> str:
    text = "\n".join(
        f"{m.type.upper()}: {m.content}"
        for m in old_messages
        if hasattr(m, "content") and m.content
    )

    prior = f"Previous summary:\n{existing_summary}\n\n" if existing_summary else ""

    prompt = f"{prior}Summarize this conversation concisely, preserving key facts, user preferences, and context:\n\n{text}"

    response = client.chat.complete(
        model=config['model']['name'],
        messages=[{"role": "user", "content": prompt}],
    )

    summary = response.choices[0].message.content
    logger.info(f"💬Summary generated: {len(summary)} chars")
    return summary
