import os
import json
import time
import faiss
import requests

from .logging_config import setup_logger
from .config import INDEX_PATH, META_PATH, OLLAMA_URL, OLLAMA_MODEL, TOP_K, MAX_CONTEXT_CHARS
from .embeddings import Embedder
from .prompts import build_prompt

logger = setup_logger("rag")


class RAG:
    def __init__(self):
        try:
            if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
                raise RuntimeError("Artifacts missing. Run ingestion first (python -m src.ingest).")

            logger.info("Loading FAISS index + metadata")
            self.index = faiss.read_index(INDEX_PATH)
            with open(META_PATH, "r", encoding="utf-8") as f:
                self.meta = json.load(f)

            self.embedder = Embedder()
            logger.info("RAG initialized successfully")
        except Exception:
            logger.exception("Failed to initialize RAG")
            raise

    def retrieve(self, question: str):
        try:
            t0 = time.time()
            qv = self.embedder.encode_query(question)
            qv = qv.reshape(1, -1)
            faiss.normalize_L2(qv)
            scores, ids = self.index.search(qv, TOP_K)

            hits = []
            for idx in ids[0]:
                if idx == -1:
                    continue
                hits.append(self.meta[idx])

            logger.info(f"retrieve_done top_k={TOP_K} hits={len(hits)} ms={int((time.time()-t0)*1000)}")
            return hits
        except Exception:
            logger.exception("Retrieval failed")
            raise

    def _call_ollama(self, prompt: str) -> str:
        try:
            t0 = time.time()
            payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
            r = requests.post(OLLAMA_URL, json=payload, timeout=180)
            r.raise_for_status()
            out = r.json().get("response", "").strip()
            logger.info(f"ollama_done model={OLLAMA_MODEL} ms={int((time.time()-t0)*1000)}")
            return out
        except Exception:
            logger.exception("Ollama call failed (is Ollama running? model pulled?)")
            raise

    def answer(self, question: str):
        try:
            t0 = time.time()
            hits = self.retrieve(question)
            sources = sorted(set(h["source"] for h in hits))

            context_parts = [f"Source: {h['source']}\n{h['text']}" for h in hits]
            context = "\n\n".join(context_parts)[:MAX_CONTEXT_CHARS]

            prompt = build_prompt(context, question)
            answer = self._call_ollama(prompt)

            logger.info(f"answer_done sources={len(sources)} total_ms={int((time.time()-t0)*1000)}")
            return {"question": question, "answer": answer, "sources": sources}

        except Exception:
            logger.exception("Answer generation failed")
            raise