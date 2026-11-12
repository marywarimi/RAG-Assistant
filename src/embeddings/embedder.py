import os
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


def embed_chunks(chunks, model_name=None):
    # Use model name from argument or .env; raise clear error if not specified
    model = model_name or os.getenv("NVIDIA_EMBED_MODEL")
    if not model or not model.strip():
        raise ValueError(
            "NVIDIA_EMBED_MODEL is not configured. "
            "Please set your chosen embedding model in .env (e.g. nvidia/llama-3.2-nv-embedqa-1b-v2)."
        )

    client = get_nvidia_client()
    texts = [chunk["text"] for chunk in chunks]

    # Batch calls to avoid exceeding payload limits
    batch_size = 32
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            input=batch,
            model=model.strip(),
            extra_body={"input_type": "passage", "truncate": "END"},
        )
        all_embeddings.extend([item.embedding for item in response.data])

    for chunk, embedding in zip(chunks, all_embeddings):
        chunk["embedding"] = embedding

    return chunks


if __name__ == "__main__":
    from src.ingestion.pdf_reader import load_pdf
    from src.chunking.chunker import chunk_pages

    pages = load_pdf("Data/papers/raw/Lesson01-Introduction.pdf")
    chunks = chunk_pages(pages)
    embedded_chunks = embed_chunks(chunks)

    print("Number of chunks:", len(embedded_chunks))
    print("Numbers in first embedding:", len(embedded_chunks[0]["embedding"]))
