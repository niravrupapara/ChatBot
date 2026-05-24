import os
from mistralai import Mistral
from src.utils.logger import get_logger

logger = get_logger(__name__)
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))


def should_summarize(messages: list, threshold: int = 20) -> bool:
    return len(messages) > threshold


def summarize_messages(old_messages: list, existing_summary: str = "") -> str:
    text = "\n".join(
        f"{m.type.upper()}: {m.content}"
        for m in old_messages
        if hasattr(m, "content") and m.content
    )

    prior = f"Previous summary:\n{existing_summary}\n\n" if existing_summary else ""

    prompt = f"{prior}Summarize this conversation concisely, preserving key facts, user preferences, and context:\n\n{text}"

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}],
    )

    summary = response.choices[0].message.content
    logger.info(f"💬Summary generated: {len(summary)} chars")
    return summary
