# NVIDIA AI Integration Guide for DocuMind

**Author:** `s.u.n.d.a.y`

This guide explains how to configure DocuMind to use the **NVIDIA AI API Catalog** for Embeddings, Reranking, and LLM Generation.

---

## 1. Quick Setup: Get an NVIDIA API Key

1. Go to [build.nvidia.com](https://build.nvidia.com/).
2. Create a free account or sign in.
3. Browse any model and click **"Get API Key"**.
4. NVIDIA grants **1,000 free API credits** on registration (no credit card required).

---

## 2. Where to Put Your Model Names

All model names in DocuMind are **customizable by you**. You can select any model available on `build.nvidia.com` and define it in your `.env` file without modifying any Python code.

Open (or create) your `.env` file in the root directory:

```bash
# 1. Paste your NVIDIA API Key:
NVIDIA_API_KEY=nvapi-your_key_here

# 2. Enter your chosen NVIDIA embedding model:
NVIDIA_EMBED_MODEL=

# 3. Enter your chosen NVIDIA reranking model:
NVIDIA_RERANK_MODEL=

# 4. Enter your chosen NVIDIA LLM / chat model:
NVIDIA_LLM_MODEL=
```

---

## 3. Recommended NVIDIA Models to Choose From

You can choose any models from [build.nvidia.com](https://build.nvidia.com/). Here are the top tested options:

### A. Embedding Models (`NVIDIA_EMBED_MODEL`)
Put one of these in `NVIDIA_EMBED_MODEL=`:
* `nvidia/llama-3.2-nv-embedqa-1b-v2` *(Recommended — High precision, fast)*
* `nvidia/nv-embedqa-e5-v5`

### B. Reranking Models (`NVIDIA_RERANK_MODEL`)
Put one of these in `NVIDIA_RERANK_MODEL=`:
* `nvidia/llama-3.2-nv-rerankqa-1b-v2` *(Recommended — Supports 4,000+ token context)*
* `nvidia/reranking-mistral-nemotron-4b`

### C. Chat / Generation Models (`NVIDIA_LLM_MODEL`)
Put one of these in `NVIDIA_LLM_MODEL=`:
* `nvidia/llama-3.1-nemotron-70b-instruct` *(Recommended — Exceptional instruction following & RAG context discipline)*
* `meta/llama-3.3-70b-instruct`
* `mistralai/mixtral-8x7b-instruct-v0.1`

---

## 4. Important: Reset ChromaDB Vector Store on First Run

Because the previous embedding model (`all-MiniLM-L6-v2`) used **384-dimensional** vectors and NVIDIA embedding models use **2,048-dimensional** vectors, ChromaDB must be cleared once so it can initialize with the new dimensions:

```bash
# Delete existing local vectorstore before running:
rm -rf Data/vectorstore
```

When you start the app and upload a document, ChromaDB will automatically recreate the database with the new NVIDIA vector dimensions.

---

## 5. Running the App

```bash
streamlit run frontend/streamlit_app.py
```
