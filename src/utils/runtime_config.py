from src.utils.logger import get_logger

logger = get_logger(__name__)

_overrides: dict = {}
_tool_calls: list = []


def set_override(key: str, value) -> None:
    _overrides[key] = value
    logger.info(f"Runtime override set: {key} = {value}")


def get_override(key: str, default=None):
    return _overrides.get(key, default)


def get_all() -> dict:
    return dict(_overrides)


def add_tool_call(tool_name: str) -> None:
    _tool_calls.append(tool_name)
    logger.info(f"Tool call recorded: {tool_name}")


def get_tool_calls() -> list:
    return list(_tool_calls)


def reset_tool_calls() -> None:
    _tool_calls.clear()
    logger.info("Tool call history reset")
