# src/generation/generation.py
 
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors          # lets us catch Gemini's error messages
from src.retrieval.retrieval import retrieve
from src.reranking.reranking import rerank
 
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
 
# ---------- Settings you can change in one place ----------
 
# Models to try, in order. If the first is busy, we move to the next one.
MODELS = [
    "gemini-2.5-flash",        # main model
    "gemini-2.5-flash-lite",   # backup 1 (lighter, often less busy)
    "gemini-3.1-flash-lite",   # backup 2
]
 
RETRIES_PER_MODEL = 3          # how many times to try each model
WAIT_SECONDS = 2               # waiting time between tries (grows each time)
 
# Error codes that mean "busy or temporary problem, try again"
BUSY_CODES = {429, 500, 502, 503, 504}
 
 
def build_prompt(question, chunks):
    # Join the best chunks into one block of text, each with its source and page
    context = "\n\n".join(
        f"[Source: {chunk['source']}, Page: {chunk['page']}]\n{chunk['text']}"
        for chunk in chunks
    )
 
    prompt = f"""
You are a helpful document assistant.
Answer the question using the provided context.
 
Rules:
- Use the context to answer the question.
- If the answer is not in the context, say you could not find it in the provided documents.
- Do not invent facts.
- Give a clear, understandable answer.
- Do not write a Source or Page line. The app shows the sources separately.
 
Context:
{context}
 
Question:
{question}
 
Answer:
"""
    return prompt
 
 
def generate_answer(question, chunks):
    # Stop early with a clear message if the key is missing
    if not api_key:
        raise ValueError("GEMINI_API_KEY was not found. Check your .env file.")
 
    client = genai.Client(api_key=api_key)
    prompt = build_prompt(question, chunks)
 
    last_error = None
 
    # Go through the models one by one
    for model in MODELS:
 
        # Try the same model a few times before giving up on it
        for attempt in range(1, RETRIES_PER_MODEL + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
 
                # Sometimes Gemini returns no text, so we handle that too
                if not response.text:
                    return "I could not write an answer this time. Please try asking again."
 
                return response.text
 
            except errors.APIError as e:
                last_error = e
                code = getattr(e, "code", None)
 
                # 404 = this model name does not exist, so skip to the next model
                if code == 404:
                    print(f"[generation] {model} was not found. Trying the next model.")
                    break
 
                # Busy or temporary problem: wait a little, then try again
                if code in BUSY_CODES:
                    print(f"[generation] {model} is busy (error {code}), attempt {attempt} of {RETRIES_PER_MODEL}.")
                    if attempt < RETRIES_PER_MODEL:
                        time.sleep(WAIT_SECONDS * attempt)
                    continue
 
                # Any other error is a real problem, so show it
                raise
 
    # If we reach this line, every model failed
    raise RuntimeError(f"All Gemini models are busy or unavailable right now. Last error: {last_error}")
 
 
if __name__ == "__main__":
    question = input("Ask a question about your documents: ")
 
    # 1. Get 10 chunks that look close to the question
    chunks = retrieve(question, top_k=10)
 
    # 2. Let the re-ranker pick the best 3 of those 10
    best_chunks = rerank(question, chunks, top_n=3)
 
    # 3. Send only the best 3 to Gemini
    answer = generate_answer(question, best_chunks)
 
    print("\nAnswer:")
    print(answer)
 
