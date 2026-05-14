from pathlib import Path
from pypdf import PdfReader
from src.utils.config_loader import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = load_config()


def load_file(file_path: str) -> str:
    path = Path(file_path)
    logger.info(f"Loading file: {path.name}")

    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif path.suffix.lower() == ".txt":
        text = path.read_text(encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    logger.info(f"Loaded {len(text)} characters from {path.name}")
    return text


def chunk_text(text: str) -> list[str]:
    chunk_size = config["rag"]["chunk_size"]
    overlap = config["rag"]["chunk_overlap"]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    logger.info(f"Created {len(chunks)} chunks (size={chunk_size}, overlap={overlap})")
    return chunks


def ingest_file(file_path: str) -> list[str]:
    text = load_file(file_path)
    return chunk_text(text)
