from src.utils.config_loader import load_config
from src.utils.llm_client import get_mistral_client
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()
client = get_mistral_client()

RECENT_WINDOW = 4


def should_summarize(
    message_count: int,
    threshold: int = 10,
    existing_summary: str = "",
    last_summarized_count: int = 0,
) -> bool:
    """
    Checks if conversation summarization should trigger based on message_count (an integer).

    - First summary: Triggers when message_count >= threshold (e.g. 10 messages).
    - Subsequent summaries: Triggers when new unsummarized messages outside recent window >= threshold (e.g. 10 messages).
    """
    # First-time summarization trigger
    if not existing_summary:
        if message_count >= threshold:
            logger.info(f"📊 First-time summary triggered: {message_count} messages reached threshold ({threshold})")
            return True
        return False

    # Subsequent incremental batch trigger
    unsummarized_count = (message_count - RECENT_WINDOW) - last_summarized_count
    if unsummarized_count >= threshold:
        logger.info(
            f"📊 Subsequent summary triggered: {unsummarized_count} new unsummarized messages accumulated "
            f"(threshold: {threshold}, last summarized count: {last_summarized_count})"
        )
        return True
    return False


def summarize_messages(new_unsummarized_messages: list, existing_summary: str = "") -> str:
    """
    Combines existing summary with ONLY newly accumulated unsummarized messages.
    """
    text = "\n".join(
        f"{m.type.upper()}: {m.content}"
        for m in new_unsummarized_messages
        if hasattr(m, "content") and m.content
    )

    prior_context = f"Previous summary:\n{existing_summary}\n\n" if existing_summary else ""

    prompt = (
        f"{prior_context}"
        f"Incorporate the following new conversation messages into a concise updated summary. "
        f"Preserve key facts, user preferences, and context:\n\n{text}"
    )

    logger.info(f"💬 Generating LLM summary for {len(new_unsummarized_messages)} new messages...")

    response = client.chat.complete(
        model=config['model']['name'],
        messages=[{"role": "user", "content": prompt}],
    )

    summary = response.choices[0].message.content.strip()
    logger.info(f"✅ Summary generated successfully ({len(summary)} chars)")
    return summary
