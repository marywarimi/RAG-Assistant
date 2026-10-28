import streamlit as st

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from src.ingestion.pdf_reader import load_pdf

MAX_FILE_MB = 20

# Project root = two folders up from this file (frontend/streamlit_app.py)
RAW_DIR = Path(__file__).parent.parent / "Data" / "papers" / "raw"

# Insert code here: st.set_page_config with a page_title and a page_icon (an emoji)
st.set_page_config(
    page_title="Academic Research Paper Assistant"
    )

# ---------- Sidebar: help for the student ----------
# Insert code here: with st.sidebar: add a header "How it works"
# Insert code here: write 3 short steps (1. Upload  2. Ask  3. Read the answer)
# Insert code here: show the limits: PDF only, max 20 MB (use MAX_FILE_MB)
with st.sidebar:
    st.header("How it works")

    st.write("1. Upload your research paper.")
    st.write("2. Ask a question about the paper.")
    st.write("3. Read the answer.")

    st.info(f"Limits: PDF only, max {MAX_FILE_MB} MB")
# ---------- Main page ----------
# Insert code here: st.title with the app name
# Insert code here: st.write a friendly one-line welcome
st.title("Academic Research Paper Assistant")

st.write("Upload a research paper and ask questions to understand it better.")
# ---------- Upload area ----------
# Insert code here: st.subheader("1. Upload your paper")
# Insert code here: uploaded_file = st.file_uploader(... type=["pdf"] ...)
# Insert code here: st.caption showing "PDF only, up to 20 MB"
# Insert code here: if uploaded_file is not None, show a success message with its name

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
        

# ---------- Question area ----------
# Insert code here: st.subheader("2. Ask a question")
# Insert code here: question = st.text_input(... placeholder="e.g. What method did the authors use?")
# Insert code here: ask_clicked = st.button("Ask")

st.subheader("2. Ask a question")

question = st.text_input(
    "What would you like to know?",
    placeholder="e.g. What method did the authors use?"
)

ask_clicked = st.button("Ask")

# ---------- Answer area ----------
# Insert code here: st.subheader("3. Answer")
# Insert code here: if ask_clicked:
#     - if no file, show st.warning("Please upload a paper first")
#     - elif no question, show st.warning("Please type a question")
#     - else: use st.spinner and show a fake answer with st.info
#     - then st.expander("Sources") with a fake source line

st.subheader("3. Answer")

if ask_clicked:
    if uploaded_file is None:
        st.warning("Please upload a paper first.")

    elif not question.strip():
        st.warning("Please type a question.")

    else:
        with st.spinner("Finding an answer..."):
            st.info(
                "This is a placeholder answer. "
                "The RAG backend will generate a real answer here."
            )

        with st.expander("Sources"):
            st.write("Placeholder source: Page 1 of your research paper.")
