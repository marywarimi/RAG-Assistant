import streamlit as st

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from src.ingestion.pdf_reader import load_pdf
from src.chunking.chunker import chunk_pages              # NEW (fixed)
from src.embeddings.embedder import embed_chunks          # NEW (fixed)
from src.vectorstore.store import store_chunks   
from src.retrieval.retrieval import retrieve
from src.generation.generation import generate_answer         # NEW (fixed)

MAX_FILE_MB = 20

# Project root = two folders up from this file (frontend/streamlit_app.py)
RAW_DIR = Path(__file__).parent.parent / "Data" / "papers" / "raw"

st.set_page_config(
    page_title="Academic Research Paper Assistant",
    page_icon="📄"                                        # NEW
)

# ---------- Sidebar ----------
with st.sidebar:
    st.header("How it works")

    st.write("1. Upload your research paper.")
    st.write("2. Ask a question about the paper.")
    st.write("3. Read the answer.")

    st.info(f"Limits: PDF only, max {MAX_FILE_MB} MB")

# ---------- Main page ----------
st.title("Academic Research Paper Assistant")

st.write("Upload a research paper and ask questions to understand it better.")

# ---------- Upload area ----------
st.subheader("1. Upload your paper")

uploaded_file = st.file_uploader(
    "Choose a research paper",
    type=["pdf"],
    help=f"Upload a PDF file up to {MAX_FILE_MB} MB.",
    max_upload_size=MAX_FILE_MB
)

st.caption(f"PDF only, up to {MAX_FILE_MB} MB")

if uploaded_file is not None:
    file_size_mb = uploaded_file.size / (1024 * 1024)

    if file_size_mb > MAX_FILE_MB:
        st.error(f"Your file exceeds the {MAX_FILE_MB} MB limit.")
    else:
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        save_path = RAW_DIR / uploaded_file.name
        save_path.write_bytes(uploaded_file.getbuffer())

        st.success(f"Uploaded successfully: {uploaded_file.name}")

        # NEW: prepare the paper only ONE time per file
        if st.session_state.get("prepared_file") != uploaded_file.name:
            with st.spinner("Reading your paper..."):
                pages = load_pdf(save_path)
                chunks = chunk_pages(pages)
                chunks = embed_chunks(chunks)
                store_chunks(chunks)
            st.session_state["prepared_file"] = uploaded_file.name

        st.success("Your paper is ready for questions!")

# ---------- Question area ----------
st.subheader("2. Ask a question")

question = st.text_input(
    "What would you like to know?",
    placeholder="e.g. What method did the authors use?"
)

ask_clicked = st.button("Ask")

# ---------- Answer area ----------
st.subheader("3. Answer")

if ask_clicked:
    if uploaded_file is None:
        st.warning("Please upload a paper first.")

    else:
        with st.spinner("Finding an answer..."):
            chunks = retrieve(question)
            answer = generate_answer(question, chunks)

        st.info(answer)

        with st.expander("Sources"):
            for chunk in chunks:
                st.write(f"{chunk['source']} - page {chunk['page']}")