import streamlit as st
import time
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

# ---------- Your backend (unchanged) ----------
from src.ingestion.pdf_reader import load_pdf
from src.chunking.chunker import chunk_pages
from src.embeddings.embedder import embed_chunks
from src.vectorstore.store import store_chunks
from src.retrieval.retrieval import retrieve
from src.reranking.reranking import rerank
from src.generation.generation import generate_answer
from src.ingestion.pptx_reader import load_pptx

MAX_FILE_MB = 20

# Project root = two folders up from this file (frontend/streamlit_app.py)
RAW_DIR = Path(__file__).parent.parent / "Data" / "papers" / "raw"

# Example questions shown as buttons (they fill the question box when clicked)
EXAMPLE_QUESTIONS = [
    "Summarize the key points.",
    "What are the main topics covered?",
    "Explain the most important concept.",
    "What are the key findings?",
]

# ---------- Page settings ----------
st.set_page_config(
    page_title="DocuMind",
    page_icon="🧠",
    layout="wide",          # use the full width of the screen
)

# ---------- Custom look (CSS) ----------
st.markdown(
    """
    <style>
    /* Dark navy sidebar with white text */
    [data-testid="stSidebar"] { background: #0F1F4B; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #FFFFFF !important; }

    /* Big headline on the home page */
    .hero-title { font-size: 3rem; font-weight: 800; line-height: 1.1; color: #0F1F4B; margin-bottom: 0.4rem; }
    .hero-accent { color: #2563EB; }
    .hero-sub { font-size: 1.15rem; color: #3B4A6B; margin-bottom: 1.2rem; }

    /* Small rounded tags for sources */
    .pill { display: inline-block; background: #E8EEFF; color: #1D4ED8; padding: 4px 12px;
            border-radius: 999px; font-size: 0.85rem; margin: 2px 6px 2px 0; }

    /* System info box in the sidebar */
    .sys-box { background: rgba(255,255,255,0.10); border-radius: 12px; padding: 12px 14px;
               font-size: 0.85rem; color: #FFFFFF; line-height: 1.6; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Memory for this browser tab ----------
if "history" not in st.session_state:
    st.session_state["history"] = []        # list of past questions and answers
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None  # the newest answer


# ---------- Small helper functions ----------
def set_question(text):
    """Put an example question into the question box."""
    st.session_state["question_input"] = text


def clear_history():
    """Remove all past questions and the current answer from the screen."""
    st.session_state["history"] = []
    st.session_state["last_result"] = None


def source_pills(sources):
    """Turn a list of sources into small rounded tags (HTML)."""
    tags = "".join(
        f'<span class="pill">{s["source"]} &bull; Page {s["page"]}</span>' for s in sources
    )
    return tags


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🧠 DocuMind")
    st.caption("Your knowledge. Within reach.")

    page = st.radio(
        "Menu",
        ["🏠 Home", "❓ How It Works", "ℹ️ About DocuMind"],
        label_visibility="collapsed",
    )

    st.markdown(
        f"""
        <div class="sys-box">
        <b>System Info</b><br>
        Supported: PDF, PPTX<br>
        Max file size: {MAX_FILE_MB} MB<br>
        Model: Gemini 2.5-Flash-lite
        </div>
        """,
        unsafe_allow_html=True,
    )


# =====================================================
# PAGE 1: HOME
# =====================================================
def show_home():
    # ----- Headline -----
    st.markdown(
        """
        <div class="hero-title">Your documents<br>have <span class="hero-accent">answers.</span></div>
        <div class="hero-sub">Upload your documents, ask a question in plain language,
        and get an answer with the exact source.</div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    # ----- Left side: upload -----
    with left:
        st.subheader("1. Upload your document")

        uploaded_file = st.file_uploader(
            "Choose a document",
            type=["pdf", "pptx"],
            help=f"Upload a PDF or PowerPoint file up to {MAX_FILE_MB} MB.",
            max_upload_size=MAX_FILE_MB,
            label_visibility="collapsed",
        )
        st.caption(f"PDF or PowerPoint (.pptx), up to {MAX_FILE_MB} MB")

        if uploaded_file is not None:
            file_size_mb = uploaded_file.size / (1024 * 1024)

            if file_size_mb > MAX_FILE_MB:
                st.error(f"Your file exceeds the {MAX_FILE_MB} MB limit.")

            # Prepare the document only ONE time per file
            elif st.session_state.get("prepared_file") != uploaded_file.name:
                RAW_DIR.mkdir(parents=True, exist_ok=True)
                save_path = RAW_DIR / uploaded_file.name
                save_path.write_bytes(uploaded_file.getbuffer())

                try:
                    with st.status("Preparing your document...", expanded=True) as status:
                        st.write("Reading the file...")
                        if save_path.suffix.lower() == ".pptx":
                            pages = load_pptx(save_path)
                        else:
                            pages = load_pdf(save_path)

                        st.write("Cutting the text into small pieces...")
                        chunks = chunk_pages(pages)

                        st.write("Turning the pieces into meaning codes...")
                        chunks = embed_chunks(chunks)

                        st.write("Saving them so they can be searched...")
                        store_chunks(chunks)

                        status.update(label="Your document is ready!", state="complete", expanded=False)

                    st.session_state["prepared_file"] = uploaded_file.name

                except Exception as e:
                    st.error("Something went wrong while reading this document. Please try again.")
                    with st.expander("Technical details"):
                        st.code(str(e))

        # Show which document is ready (stays visible even after visiting other pages)
        prepared = st.session_state.get("prepared_file")
        if prepared:
            st.success(f"Ready for questions: {prepared}")

    # ----- Right side: question -----
    with right:
        st.subheader("2. Ask your question")

        st.write("Try an example:")
        example_cols = st.columns(2)
        for i, example in enumerate(EXAMPLE_QUESTIONS):
            example_cols[i % 2].button(
                example,
                key=f"example_{i}",
                on_click=set_question,
                args=(example,),
            )

        question = st.text_area(
            "Your question",
            key="question_input",
            placeholder="Type your question here...",
            label_visibility="collapsed",
            height=100,
        )

        ask_clicked = st.button("Ask DocuMind", type="primary")

    # ----- Run the question through your backend -----
    if ask_clicked:
        if st.session_state.get("prepared_file") is None:
            st.warning("Please upload a document first.")

        elif not question.strip():
            st.warning("Please type a question first.")

        else:
            try:
                start = time.time()

                with st.status("Finding your answer...", expanded=True) as status:
                    st.write("Finding the closest pages...")
                    t0 = time.time()
                    candidates = retrieve(question, top_k=10)
                    t_retrieve = time.time() - t0

                    st.write("Choosing the best pages...")
                    t0 = time.time()
                    best_chunks = rerank(question, candidates, top_n=3)
                    t_rerank = time.time() - t0

                    st.write("Writing the answer...")
                    t0 = time.time()
                    answer = generate_answer(question, best_chunks)
                    t_generate = time.time() - t0

                    status.update(label="Answer ready!", state="complete", expanded=False)

                elapsed = time.time() - start

                # Collect the sources (remove repeats, keep the order)
                sources = []
                for chunk in best_chunks:
                    item = {"source": Path(str(chunk["source"])).name, "page": chunk["page"]}
                    if item not in sources:
                        sources.append(item)

                result = {
                    "question": question,
                    "answer": answer,
                    "sources": sources,
                    "timing": (
                        f"Answered in {elapsed:.1f}s "
                        f"(retrieve {t_retrieve:.1f}s, rerank {t_rerank:.1f}s, Gemini {t_generate:.1f}s)"
                    ),
                }

                st.session_state["last_result"] = result
                st.session_state["history"].append(result)

            except Exception as e:
                st.error(
                    "Something went wrong while getting the answer. "
                    "This can happen when the AI service is busy. Please try again in a moment."
                )
                with st.expander("Technical details"):
                    st.code(str(e))

    # ----- Answer area -----
    st.subheader("3. Your answer")

    result = st.session_state["last_result"]

    if result is None:
        st.info("Your answer will appear here, along with its sources.")
    else:
        with st.container(border=True):
            st.caption(f"Question: {result['question']}")
            st.markdown(result["answer"])

        with st.expander("📋 Copy answer"):
            st.code(result["answer"], language=None, wrap_lines=True)
            st.caption("Click the copy icon in the top right corner of the box.")

        st.markdown("**Sources**")
        st.markdown(source_pills(result["sources"]), unsafe_allow_html=True)
        st.caption(result["timing"])

    # ----- History area -----
    history = st.session_state["history"]

    if len(history) > 1:
        st.subheader("Earlier questions")
        for item in reversed(history[:-1]):
            with st.expander(item["question"]):
                st.markdown(item["answer"])
                st.caption(
                    "Sources: "
                    + ", ".join(f"{s['source']} (page {s['page']})" for s in item["sources"])
                )

    if history:
        st.button("Clear history", on_click=clear_history)


# =====================================================
# PAGE 2: HOW IT WORKS
# =====================================================
def show_how_it_works():
    st.title("How DocuMind works")
    st.write("DocuMind finds the right pages in your document first, then writes an answer from those pages only.")

    st.markdown("### 1. You upload a document")
    st.write("DocuMind reads your PDF or PowerPoint and remembers which page or slide each piece of text came from.")

    st.markdown("### 2. It prepares the document")
    st.write(
        "The text is cut into small pieces. Each piece is turned into a list of numbers "
        "that captures its meaning, and the pieces are saved so they can be searched."
    )

    st.markdown("### 3. You ask a question")
    st.write("DocuMind finds the pieces closest to your question, then checks them again to pick the best pages.")

    st.markdown("### 4. You get an answer with sources")
    st.write("An AI model (Google Gemini) writes the answer using only those pages. You can see which file and page it came from.")

    st.info("Because answers come from your own documents, you can always check them against the real page.")


# =====================================================
# PAGE 3: ABOUT
# =====================================================
def show_about():
    st.title("About DocuMind")
    st.write(
        "DocuMind is an AI-powered document intelligence application. It lets organizations "
        "ask questions about their own documents and get answers they can verify."
    )

    st.markdown("### Built with")
    st.write("Python, Streamlit, pypdf, python-pptx, and Google Gemini (gemini-2.5-flash).")

    st.markdown("### Built by")
    st.write("Mary Warimi")

    st.markdown("### Source code")
    st.write("[github.com/marywarimi](https://github.com/marywarimi)")


# ---------- Show the page chosen in the sidebar ----------
if page == "🏠 Home":
    show_home()
elif page == "❓ How It Works":
    show_how_it_works()
else:
    show_about()
