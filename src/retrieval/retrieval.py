
import chromadb
from sentence_transformers import SentenceTransformer
from functools import lru_cache


@lru_cache(maxsize=None)
def get_embedding_model(model_name):
    return SentenceTransformer(model_name)


def retrieve(question, top_k=3, db_path="Data/vectorstore",
             collection_name="lessons", model_name="all-MiniLM-L6-v2"):

    # 1. Load the same embedding model used before
    model = get_embedding_model(model_name)

    # 2. Convert the question into numbers
    question_embedding = model.encode(question).tolist()

    # 3. Open the saved database and get the collection
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(name=collection_name)

    # 4. Ask ChromaDB for the closest chunks
    search_results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(top_k, collection.count())
    )

    # 5. Build a clean list of results
    results = []

    documents = search_results["documents"][0]
    metadatas = search_results["metadatas"][0]
    distances = search_results["distances"][0]

    for text, metadata, distance in zip(documents, metadatas, distances):
        results.append({
            "text": text,
            "page": metadata.get("page", 0),
            "source": metadata.get("source", "Unknown"),
            "distance": distance
        })

    return results


if __name__ == "__main__":
    # 6. Ask a question and print the retrieved chunks
    question = "What is a file system?"

    results = retrieve(question)

    for result in results:
        print("\nPage:", result["page"])
        print("Source:", result["source"])
        print("Distance:", round(result["distance"], 4))
        print("Text:", result["text"][:150])
