from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from src.logging_config import setup_logger
from src.rag import RAG

logger = setup_logger("api")

app = FastAPI(title="Local Enterprise RAG Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local demo
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAG()


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(req: AskRequest):
    try:
        q = (req.question or "").strip()
        if not q:
            return {"error": "question is required"}
        logger.info(f"request_received question_len={len(q)}")
        return rag.answer(q)
    except Exception as e:
        logger.exception("Request failed")
        return {"error": str(e)}