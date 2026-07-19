import os
import sqlite3

from src.utils.config_loader import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()

DB_PATH = config["session"]["db_path"]

def ensure_db_dir() -> None:
    """Make sure the parent folder for the SQLite DB exists."""
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)

def get_conn() -> sqlite3.Connection:
    """Return a fresh SQLite connection (safe for Streamlit's threading)."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

ensure_db_dir()
logger.info(f"SQLite DB ready at: {DB_PATH}")
