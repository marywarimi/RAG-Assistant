import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_nvidia_client():
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY was not found. Please set it in your .env file.")
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key,
    )


def retrieve(question, top_k=3, db_path="Data/vectorstore",
             collection_name="lessons", model_name=None):

    model = model_name or os.getenv("NVIDIA_EMBED_MODEL")
    if not model or not model.strip():
        raise ValueError(
            "NVIDIA_EMBED_MODEL is not configured. "
            "Please set your chosen embedding model in .env (e.g. nvidia/llama-3.2-nv-embedqa-1b-v2)."
        )

    # 1. Convert the question into numbers using NVIDIA query embedding
    client = get_nvidia_client()
    response = client.embeddings.create(
        input=[question],
        model=model.strip(),
        extra_body={"input_type": "query", "truncate": "END"},
    )
    question_embedding = response.data[0].embedding

    # 2. Open the saved database and get the collection
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_collection(name=collection_name)

    count = collection.count()
    if count == 0:
        return []

    # 3. Ask ChromaDB for the closest chunks
    search_results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(top_k, count),
    )

    # 4. Build a clean list of results
    results = []
    documents = search_results["documents"][0]
    metadatas = search_results["metadatas"][0]
    distances = search_results["distances"][0]

    for text, metadata, distance in zip(documents, metadatas, distances):
        results.append({
            "text": text,
            "page": metadata.get("page", 0),
            "source": metadata.get("source", "Unknown"),
            "distance": distance,
        })

    return results


if __name__ == "__main__":
    question = "What is a file system?"
    results = retrieve(question)

    for result in results:
        print("\nPage:", result["page"])
        print("Source:", result["source"])
        print("Distance:", round(result["distance"], 4))
        print("Text:", result["text"][:150])
