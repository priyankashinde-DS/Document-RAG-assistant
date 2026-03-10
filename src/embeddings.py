import numpy as np
from sentence_transformers import SentenceTransformer

from src.logging_config import setup_logger
from src.config import EMBEDDING_MODEL_NAME

logger = setup_logger("embeddings")


class Embedder:
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.exception("Failed to load embedding model")
            raise

    def encode_texts(self, texts):
        try:
            vecs = self.model.encode(texts, show_progress_bar=False)
            return np.asarray(vecs, dtype="float32")
        except Exception:
            logger.exception("Failed to encode texts")
            raise

    def encode_query(self, q: str):
        try:
            vec = self.model.encode([q], show_progress_bar=False)[0]
            return np.asarray(vec, dtype="float32")
        except Exception:
            logger.exception("Failed to encode query")
            raise