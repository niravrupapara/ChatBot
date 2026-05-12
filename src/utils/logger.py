
import logging
from src.utils.config_loader import load_config


config = load_config()

LOG_LEVEL = config["logging"]["level"]
LOG_FORMAT = config["logging"]["format"]


logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)