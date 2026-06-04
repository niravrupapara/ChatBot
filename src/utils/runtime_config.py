from src.utils.logger import get_logger

logger = get_logger(__name__)

_overrides: dict = {}


def set_override(key: str, value) -> None:
    _overrides[key] = value
    logger.info(f"Runtime override set: {key} = {value}")


def get_override(key: str, default=None):
    return _overrides.get(key, default)


def get_all() -> dict:
    return dict(_overrides)
