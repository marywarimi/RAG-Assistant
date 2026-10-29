# src/generation/generation.py

import os
from dotenv import load_dotenv
from google import genai
from src.retrieval.retrieval import retrieve   # fix this line using the rule above

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


def build_prompt(question, chunks):
    context = "\n\n".join(
        f"[Source: {chunk['source']}, Page: {chunk['page']}]\n{chunk['text']}"
        for chunk in chunks
    )

    prompt = f"""
You are a helpful student learning assistant.
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
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=build_prompt(question, chunks)
    )

    return response.text


if __name__ == "__main__":
    question = input("Ask a question about your documents: ")

    chunks = retrieve(question)

    answer = generate_answer(question, chunks)

    print("\nAnswer:")
    print(answer)