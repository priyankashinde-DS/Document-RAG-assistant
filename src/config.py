import os

DOCS_DIR = os.getenv("DOCS_DIR", "data/docs")
ARTIFACTS_DIR = os.getenv("ARTIFACTS_DIR", "artifacts")

INDEX_PATH = os.path.join(ARTIFACTS_DIR, "faiss.index")
META_PATH = os.path.join(ARTIFACTS_DIR, "meta.json")

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)

# Ollama service inside docker-compose
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")

TOP_K = int(os.getenv("TOP_K", "3"))
MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "4500"))

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))