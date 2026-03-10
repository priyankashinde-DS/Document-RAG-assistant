import requests
import streamlit as st

from src.logging_config import setup_logger

logger = setup_logger("streamlit")

API_URL = "http://api:8000/ask"  # docker-compose service name
HEALTH_URL = "http://api:8000/health"

st.set_page_config(page_title=" Enterprise RAG", layout="centered")

st.title("Enterprise Knowledge Assistant (Local RAG)")
st.caption("FAISS + SentenceTransformers + Ollama (phi3:mini) + FastAPI + Streamlit")

# Health check
try:
    h = requests.get(HEALTH_URL, timeout=5)
    if h.status_code == 200:
        st.success("API is running ")
    else:
        st.warning("API health check failed (non-200).")
except Exception:
    st.warning("API not reachable yet. Wait a few seconds and refresh.")

q = st.text_area("Ask a question", placeholder="e.g., What is the refund policy?", height=100)

if st.button("Ask"):
    if not q.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving context and generating answer..."):
            try:
                logger.info(f"ui_ask question_len={len(q.strip())}")
                r = requests.post(API_URL, json={"question": q.strip()}, timeout=240)
                data = r.json()

                if "error" in data:
                    st.error(data["error"])
                    logger.error(f"ui_error {data['error']}")
                else:
                    st.subheader("Answer")
                    st.write(data.get("answer", ""))

                    st.subheader("Sources")
                    for s in data.get("sources", []):
                        st.write(f"- {s}")
            except Exception as e:
                st.error(str(e))
                logger.exception("UI request failed")