from sentence_transformers import CrossEncoder
from functools import lru_cache


@lru_cache(maxsize=None)
def get_reranker(model_name):
    return CrossEncoder(model_name)

def rerank(question, results, top_n=3,
           model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):

    # 1. Load the cross-encoder model
    model = get_reranker(model_name)

    # 2. Make a pair [question, chunk text] for every chunk
    pairs = [[question, result["text"]] for result in results]

    # 3. Score every pair (higher score = better answer)
    scores = model.predict(pairs)

    # 4. Put each score inside its result dict
    for result, score in zip(results, scores):
        result["rerank_score"] = float(score)

    # 5. Sort from highest score to lowest
    results = sorted(results, key=lambda r: r["rerank_score"], reverse=True)

    # 6. Keep only the best top_n
    return results[:top_n]


if __name__ == "__main__":
    # Change this import line to match where your retrieval.py lives
    from src.retrieval.retrieval import retrieve

    question = "What are the types of an operating system"

    # Get 10 chunks first, not just 3
    results = retrieve(question, top_k=10)

    print("BEFORE re-ranking (top 3):")
    for r in results[:3]:
        print("Page:", r["page"], "| Distance:", round(r["distance"], 4))

    best = rerank(question, results, top_n=3)

    print("\nAFTER re-ranking (top 3):")
    for r in best:
        print("Page:", r["page"], "| Score:", round(r["rerank_score"], 2))