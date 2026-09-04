# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# backend/app/config.py -> backend/app -> backend -> repo root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://paper_trail:paper_trail@localhost:5443/paper_trail",
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "RS256")
JWT_PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY")
JWT_PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
JSON_LOGS = os.getenv("JSON_LOGS", "false").lower() == "true"

# Ollama runs on the host, not in podman-compose
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "qwen3-embedding:4b")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "2560"))
CHAT_MODEL = os.getenv("CHAT_MODEL", "mistral-nemo:12b")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# Default points at the repo-root documents/ dir for local dev. In the combined
# Docker image this is overridden (e.g. STORAGE_ROOT=/data/documents) and bind-mounted
# via `doit.sh docker-run` so uploads survive container restarts.
STORAGE_ROOT = Path(os.getenv("STORAGE_ROOT", str(BASE_DIR / "documents")))
RAW_PDF_DIR = STORAGE_ROOT / "raw" / "pdf"
MARKDOWN_DIR = STORAGE_ROOT / "processed" / "md"
RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)
MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
CHAT_TOP_K = int(os.getenv("CHAT_TOP_K", "5"))
