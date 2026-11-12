# src/generation/generation.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")


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


def generate_answer(question, chunks, model_name=None):
    if not api_key:
        raise ValueError("NVIDIA_API_KEY was not found. Please set it in your .env file.")

    model = model_name or os.getenv("NVIDIA_LLM_MODEL")
    if not model or not model.strip():
        raise ValueError(
            "NVIDIA_LLM_MODEL is not configured. "
            "Please set your chosen chat model in .env (e.g. nvidia/llama-3.1-nemotron-70b-instruct)."
        )

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key,
    )

    prompt = build_prompt(question, chunks)

    response = client.chat.completions.create(
        model=model.strip(),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content
    if not answer:
        return "I could not write an answer this time. Please try asking again."
    return answer


if __name__ == "__main__":
    from src.retrieval.retrieval import retrieve
    from src.reranking.reranking import rerank

    question = input("Ask a question about your documents: ")

    chunks = retrieve(question, top_k=10)
    best_chunks = rerank(question, chunks, top_n=3)
    answer = generate_answer(question, best_chunks)

    print("\nAnswer:")
    print(answer)
