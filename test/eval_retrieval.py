import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
import os

from src.retrieval.retrieval import retrieve

# 1. Find the questions file (it sits next to this script)
folder = os.path.dirname(__file__)
questions_path = os.path.join(folder, "eval_questions.json")

with open(questions_path, "r", encoding="utf-8") as f:
    questions = json.load(f)

hits = 0

# 2. Go through each question
for item in questions:
    question = item["question"]
    expected_page = item["expected_page"]

    results = retrieve(question, top_k=3)
    found_pages = [r["page"] for r in results]

    if expected_page in found_pages:
        hits += 1
        status = "HIT "
    else:
        status = "MISS"

    print(status, "|", question)
    print("      expected page:", expected_page, "| found pages:", found_pages)

# 3. Print the score
print("\nScore:", hits, "out of", len(questions))