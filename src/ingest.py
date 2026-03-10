import os
import json
import faiss
from PyPDF2 import PdfReader

from .logging_config import setup_logger
from .config import DOCS_DIR, ARTIFACTS_DIR, INDEX_PATH, META_PATH
from .chunking import chunk_text
from .embeddings import Embedder

logger = setup_logger("ingest")


def read_pdf_text(path: str) -> str:
    try:
        reader = PdfReader(path)
        pages = []
        for p in reader.pages:
            pages.append(p.extract_text() or "")
        return "\n".join(pages)
    except Exception:
        logger.exception(f"Failed to read PDF: {path}")
        raise


def build_index():
    try:
        os.makedirs(ARTIFACTS_DIR, exist_ok=True)
        os.makedirs(DOCS_DIR, exist_ok=True)

        pdfs = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith(".pdf")]
        if not pdfs:
            raise RuntimeError(f"No PDFs found in {DOCS_DIR}")

        logger.info(f"Found {len(pdfs)} PDFs in {DOCS_DIR}")

        embedder = Embedder()
        all_chunks = []
        meta = []

        for fn in pdfs:
            full_path = os.path.join(DOCS_DIR, fn)
            logger.info(f"Reading document: {fn}")
            raw_text = read_pdf_text(full_path)

            chunks = chunk_text(raw_text)
            logger.info(f"Chunked {fn} into {len(chunks)} chunks")

            for i, ch in enumerate(chunks):
                ch_clean = ch.strip()
                if not ch_clean:
                    continue
                all_chunks.append(ch_clean)
                meta.append({"source": fn, "chunk_id": f"{fn}_{i}", "text": ch_clean})

        if not all_chunks:
            raise RuntimeError("No usable text extracted from PDFs")

        logger.info(f"Generating embeddings for {len(all_chunks)} chunks")
        vectors = embedder.encode_texts(all_chunks)
        dim = vectors.shape[1]

        logger.info(f"Building FAISS IndexFlatIP with dim={dim}")
        faiss.normalize_L2(vectors)
        index = faiss.IndexFlatIP(dim)
        index.add(vectors)

        faiss.write_index(index, INDEX_PATH)
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        logger.info(f" FAISS index saved: {INDEX_PATH}")
        logger.info(f" Metadata saved: {META_PATH}")
        return True

    except Exception:
        logger.exception(" Ingestion failed")
        raise


if __name__ == "__main__":
    build_index()