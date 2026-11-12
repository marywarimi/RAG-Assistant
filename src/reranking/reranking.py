import os
import requests
from dotenv import load_dotenv

load_dotenv()


def rerank(question, results, top_n=3, model_name=None):
    if not results:
        return []

    model = model_name or os.getenv("NVIDIA_RERANK_MODEL")
    if not model or not model.strip():
        raise ValueError(
            "NVIDIA_RERANK_MODEL is not configured. "
            "Please set your chosen reranking model in .env (e.g. nvidia/llama-3.2-nv-rerankqa-1b-v2)."
        )

    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY was not found. Please set it in your .env file.")

    url = "https://ai.api.nvidia.com/v1/retrieval/nvidia/reranking"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    payload = {
        "model": model.strip(),
        "query": {"text": question},
        "passages": [{"text": r["text"]} for r in results],
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        # Graceful fallback: return top_n un-reranked if API unavailable or rate-limited
        return results[:top_n]

    ranking_data = response.json().get("rankings", [])

    for item in ranking_data:
        idx = item["index"]
        results[idx]["rerank_score"] = float(item.get("logit", 0.0))

    results = sorted(results, key=lambda r: r.get("rerank_score", 0.0), reverse=True)
    return results[:top_n]


if __name__ == "__main__":
    from src.retrieval.retrieval import retrieve

    question = "What are the types of an operating system"
    results = retrieve(question, top_k=10)

    print("BEFORE re-ranking (top 3):")
    for r in results[:3]:
        print("Page:", r["page"], "| Distance:", round(r["distance"], 4))

    best = rerank(question, results, top_n=3)

    print("\nAFTER re-ranking (top 3):")
    for r in best:
        print("Page:", r["page"], "| Score:", round(r.get("rerank_score", 0.0), 2))