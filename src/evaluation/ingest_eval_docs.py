from pathlib import Path

import chromadb

from src.ingestion.pdf_reader import load_pdf
from src.ingestion.pptx_reader import load_pptx
from src.chunking.chunker import chunk_pages
from src.embeddings.embedder import embed_chunks
from src.vectorstore.store import store_chunks

# Project root = three folders up from this file (src/evaluation/ingest_eval_docs.py)
EVAL_DIR = Path(__file__).parent.parent.parent / "Data" / "eval_docs"

# Same database path and collection name that store_chunks uses
DB_PATH = "Data/vectorstore"
COLLECTION_NAME = "lessons"


def clear_store():
    # Open the same database on disk that store_chunks writes to
    client = chromadb.PersistentClient(path=DB_PATH)

    # Delete the old collection. If it does not exist yet, Chroma gives an error,
    # so try/except lets us carry on quietly in that case
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print("Old collection cleared.")
    except Exception:
        print("No old collection found, starting fresh.")


def ingest_all():
    # Start from an empty store so old uploads do not mix into the test
    clear_store()

    # Find all PDFs and PowerPoints in the eval_docs folder
    files = sorted(list(EVAL_DIR.glob("*.pdf")) + list(EVAL_DIR.glob("*.pptx")))

    print(f"Found {len(files)} files in {EVAL_DIR}")

    for number, file_path in enumerate(files, start=1):
        print(f"[{number}/{len(files)}] Ingesting {file_path.name} ...")

        # Step 1: read the file, same as your app does
        if file_path.suffix.lower() == ".pptx":
            pages = load_pptx(file_path)
        else:
            pages = load_pdf(file_path)

        # Steps 2, 3, 4: chunk, embed, store, same order as your app
        chunks = chunk_pages(pages)
        chunks = embed_chunks(chunks)
        collection = store_chunks(chunks)

        print(f"    done: {len(pages)} pages/slides, {len(chunks)} chunks")

    print(f"All files ingested. Total chunks in store: {collection.count()}")


if __name__ == "__main__":
    ingest_all()