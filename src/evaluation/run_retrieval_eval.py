import json
from pathlib import Path

from src.retrieval.retrieval import retrieve
from src.reranking.reranking import rerank

# Project root = three folders up from this file
ROOT = Path(__file__).parent.parent.parent
QUESTIONS_FILE = ROOT / "test" / "eval_questions.json"
RESULTS_FILE = ROOT / "test" / "eval_results.json"


def is_match(chunk, item):
    # A chunk is correct if it comes from the right file AND the right page
    return chunk["source"] == item["source"] and chunk["page"] in item["expected_pages"]


def first_hit_position(chunks, item):
    # Go through the chunks in order and return the place (1, 2, 3...)
    # of the first correct one. Return None if there is no correct chunk.
    for position, chunk in enumerate(chunks, start=1):
        if is_match(chunk, item):
            return position
    return None


def run_evaluation():
    # Read all the questions from your JSON file
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    results = []

    for number, item in enumerate(questions, start=1):
        print(f"[{number}/{len(questions)}] {item['id']}: {item['question'][:60]}")

        # Same two steps as your app: retrieve 10, then rerank down to 3
        candidates = retrieve(item["question"], top_k=10)

        # Check the 10 BEFORE reranking, in case rerank changes the list order
        retrieve_position = first_hit_position(candidates, item)

        best_chunks = rerank(item["question"], candidates, top_n=3)
        rerank_position = first_hit_position(best_chunks, item)

        results.append({
            "id": item["id"],
            "question": item["question"],
            "source": item["source"],
            "expected_pages": item["expected_pages"],
            "retrieve_position": retrieve_position,
            "rerank_position": rerank_position,
            "final_chunks": [
                {"source": c["source"], "page": c["page"]} for c in best_chunks
            ],
        })

    return results


def show_scores(results):
    total = len(results)

    # How many times the right page was 1st, in the top 3, or in the top 10 (before rerank)
    hit1 = sum(1 for r in results if r["retrieve_position"] == 1)
    hit3 = sum(1 for r in results if r["retrieve_position"] is not None and r["retrieve_position"] <= 3)
    hit10 = sum(1 for r in results if r["retrieve_position"] is not None)

    # How many times the right page is in the final 3 (after rerank)
    final3 = sum(1 for r in results if r["rerank_position"] is not None)

    print("\n===== SCORES =====")
    print(f"Questions tested: {total}")
    print(f"Before rerank - right page 1st:        {hit1}/{total}")
    print(f"Before rerank - right page in top 3:   {hit3}/{total}")
    print(f"Before rerank - right page in top 10:  {hit10}/{total}")
    print(f"After rerank  - right page in final 3: {final3}/{total}  <-- what Gemini sees")

    # Score for each file separately
    print("\n===== SCORE PER FILE (after rerank) =====")
    per_file = {}
    for r in results:
        per_file.setdefault(r["source"], [0, 0])
        per_file[r["source"]][1] += 1
        if r["rerank_position"] is not None:
            per_file[r["source"]][0] += 1
    for source, (hits, count) in per_file.items():
        print(f"{source}: {hits}/{count}")


def show_failures(results):
    print("\n===== FAILURES (right page NOT in the final 3) =====")
    failed = [r for r in results if r["rerank_position"] is None]

    if not failed:
        print("None. Every question found its page.")
        return

    for r in failed:
        print(f"\n{r['id']}: {r['question']}")
        print(f"  Expected: {r['source']} page {r['expected_pages']}")
        if r["retrieve_position"] is not None:
            print(f"  Retrieve found it at place {r['retrieve_position']}, but rerank dropped it")
        else:
            print("  Retrieve did not find it in the top 10")
        print("  Gemini would have seen:")
        for c in r["final_chunks"]:
            print(f"    - {c['source']} page {c['page']}")


if __name__ == "__main__":
    results = run_evaluation()
    show_scores(results)
    show_failures(results)

    # Save everything so we can compare later, after changes
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_FILE}")