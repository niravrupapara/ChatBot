from src.memory.short_term import should_summarize

def test_should_summarize_initial():
    # 20 messages, threshold 20 -> False
    messages = ["msg"] * 20
    assert not should_summarize(messages, threshold=20, existing_summary="", window=6)

    # 21 messages, threshold 20 -> True
    messages_21 = ["msg"] * 21
    assert should_summarize(messages_21, threshold=20, existing_summary="", window=6)

def test_should_summarize_with_existing_summary():
    # Summary exists. Message count 22 (unsummarized = 22 - 6 = 16 < 40) -> False (no redundant call!)
    messages_22 = ["msg"] * 22
    summary = "Existing conversation summary"
    assert not should_summarize(messages_22, threshold=20, existing_summary=summary, window=6)

    # Message count 25 -> False
    messages_25 = ["msg"] * 25
    assert not should_summarize(messages_25, threshold=20, existing_summary=summary, window=6)

if __name__ == "__main__":
    test_should_summarize_initial()
    test_should_summarize_with_existing_summary()
    print("All memory unit tests passed successfully!")
