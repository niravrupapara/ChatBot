import logging
import os
import sys
from datetime import datetime

from src.utils.config_loader import load_config

config = load_config()

LOG_LEVEL = config.get("logging", {}).get("level", "INFO")
LOG_FORMAT = config.get("logging", {}).get("format", "%(asctime)s | %(levelname)s | %(name)s | %(message)s")

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)


def _get_next_log_filepath() -> str:
    """
    Generates a log filepath with an auto-incrementing serial number and timestamp:
    e.g. logs/app_001_2026-08-04_21-19-10.log
    """
    existing_files = [f for f in os.listdir(LOGS_DIR) if f.startswith("app_") and f.endswith(".log")]
    next_sr_no = len(existing_files) + 1
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"app_{next_sr_no:03d}_{timestamp}.log"
    return os.path.join(LOGS_DIR, filename)


# Single log file created per application process run
_CURRENT_LOG_FILE = _get_next_log_filepath()


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured Logger instance with dual handlers:
    1. Console Handler (sys.stdout)
    2. File Handler (logs/app_001_YYYY-MM-DD_HH-MM-SS.log)
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    if not logger.handlers:
        # 1. Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(console_handler)

        # 2. Serial Number + Timestamp File Handler
        file_handler = logging.FileHandler(_CURRENT_LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger
