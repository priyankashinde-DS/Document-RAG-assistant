def chunk_text(text: str, chunk_size: int = 700, overlap: int = 120):
    text = (text or "").strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks