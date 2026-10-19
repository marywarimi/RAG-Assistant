
import chromadb
import chromadb


def store_chunks(chunks, db_path="Data/vectorstore", collection_name="lessons"):
    # 1. Create a client that saves the database to disk
    client = chromadb.PersistentClient(path=db_path)

    # 2. Get or create a collection
    collection = client.get_or_create_collection(name=collection_name)

    # 3. Create lists for IDs, documents, embeddings, and metadata
    ids = [
        f'{chunk["source"]}_p{chunk.get("page_number", chunk.get("page", 0))}_c{i}'
        for i, chunk in enumerate(chunks)
    ]

    documents = [chunk["text"] for chunk in chunks]

    embeddings = [chunk["embedding"] for chunk in chunks]

    metadatas = [
        {
            "page": chunk.get("page_number", chunk.get("page", 0)),
            "source": chunk["source"]
        }
        for chunk in chunks
    ]

    # 4. Store everything in the collection
    if chunks:
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    return collection


if __name__ == "__main__":
    from src.ingestion.pdf_reader import load_pdf
    from src.chunking.chunker import chunk_pages
    from src.embeddings.embedder import embed_chunks

    # 5. Load, chunk, embed, then store
    pages = load_pdf("Data/papers/raw/Lesson01-Introduction.pdf")
    chunks = chunk_pages(pages)
    embedded_chunks = embed_chunks(chunks)

    collection = store_chunks(embedded_chunks)

    # 6. Print the number of stored items
    print("Items stored in collection:", collection.count())





