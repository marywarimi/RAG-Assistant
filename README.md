# DocuMind: AI Document Intelligence Assistant

> Ask your documents anything. Get answers with the exact source.

DocuMind is an AI-powered document intelligence application that lets organizations interact with their internal knowledge base. Users upload documents (PDF and PowerPoint), ask questions in plain language, and receive context-aware answers generated with Retrieval-Augmented Generation (RAG). Every answer shows the document and page it came from, so it can be checked.

**Live demo:** [Open Documind](https://documind-mary.streamlit.app/)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Who Can Use It](#who-can-use-it)
4. [Why RAG and Not Just a Chat Assistant](#why-RAG-and-Not-Just-a-Chat-Assistant)
5. [Key Features](#key-features)
6. [System Architecture](#system-architecture)
7. [Tech Stack](#tech-stack)
8. [How the RAG Pipeline Works](#how-the-rag-pipeline-works)
9. [Technical Design Decisions](#technical-design-decisions)
10. [Evaluation and Testing](#evaluation-and-testing)
11. [Installation and Setup](#installation-and-setup)
12. [Project Structure](#project-structure)
13. [What Each Part Does](#what-each-part-does)
14. [Limitations](#limitations)
15. [Future Improvements](#future-improvements)
16. [Key Terms](#key-terms)
17. [Author](#author)

---

## Project Overview

Organizations keep important knowledge inside policies, reports, manuals and slide decks. DocuMind turns those files into something you can talk to.

You upload a document, type a question, and the system:

1. Finds the pages that are most related to your question.
2. Gives those pages to a language model (Google Gemini).
3. Shows you an answer written only from those pages, with the source and page number.

It was built and tested on lecture notes (PDF and PowerPoint), and the same design works for any organization's documents.

---

## Problem Statement

Organizations store critical knowledge across many files. Finding one answer usually means opening several documents and reading page by page, which wastes time and leads to mistakes.

General AI chatbots have never seen a company's private documents, so they can guess or invent answers.

DocuMind solves both problems. It searches the organization's own documents first, then answers only from what it found, so every answer can be traced back to a real page.

---

## Who Can Use It

| Team | How they would use it |
|---|---|
| Human Resources | Ask about leave policy, onboarding and staff handbooks |
| Finance | Query financial reports and budgets |
| Customer Support | Look up product documentation quickly |
| Operations | Retrieve standard operating procedures (SOPs) |
| Management | Search organization reports and meeting decks |
| Students | Ask questions about lecture notes and research papers |

---


   ## Why RAG and Not Just a Chat Assistant?

   For one or two files, a chat assistant like Claude, ChatGPT or Gemini works well. RAG is built for what a chat window cannot do:

   - **Scale:** organizations have thousands of documents, too many to paste into a chat. RAG searches them all and sends only the best pages to the AI.
   - **Control:** the organization chooses which documents go in, who can use the system, and which AI model sits behind it.
   - **Checkable answers:** every answer shows its file and page, and the system says so when the answer is not in the documents.
   - **Built into their own tools:** it can live inside a website, an HR portal or a support system.
   - **Cost and speed:** sending three pages to the AI is much cheaper than sending a whole library.
   - **Fresh knowledge:** when a document changes, you update the document store. Nothing needs retraining.

   I built DocuMind to understand this pipeline end to end, from reading files to deploying a live app.

## Key Features

- Upload PDF and PowerPoint (.pptx) files, with a 20 MB size limit.
- Ask questions in plain language.
- Answers are grounded in the uploaded documents, not made up.
- Sources are shown: the file name and page (or slide) number.
- Re-ranking step to push the best pages to the top of the results.
- A built-in evaluation that measures how often the system finds the right page.
- Secret keys are kept in a `.env` file and never uploaded to GitHub.

---

## System Architecture

```text
Upload -> Ingestion -> Chunking -> Embeddings -> Vector store
                                                     |
Question -> Retrieval <------------------------------+
               |
           Re-ranking
               |
           Generation -> Answer + sources
```

The Streamlit front end talks to the back end (the code in `src/`) through function calls. An API layer can be added later.

---

## Tech Stack

| Part | Tool |
|---|---|
| Language | Python |
| Front end | Streamlit |
| PDF reading | pypdf |
| PowerPoint reading | python-pptx |
| Embeddings | [model_name="all-MiniLM-L6-v2"] |
| Vector store | [chromadb] |
| Language model | Google Gemini (gemini-2.5-flash) |
| Testing | pytest |
| Version control | Git and GitHub |
| Config | Environment variables in a `.env` file |

---

## How the RAG Pipeline Works

| Stage | What happens | Simple picture |
|---|---|---|
| **Front end** | The user uploads a file and asks a question (built with Streamlit). | The table where you drop your files |
| **Ingestion** | The document is read and its text is pulled out, with page numbers kept. | Opening the file and reading it |
| **Chunking** | The text is cut into small pieces. | Cutting a long document into index cards |
| **Embeddings** | Each chunk is turned into a list of numbers that captures its meaning. | Giving each card a "meaning code" |
| **Vector store** | The embeddings and chunks are saved so they can be searched. | The shelf that holds all the cards |
| **Retrieval** | The question is turned into numbers too, and the closest chunks are found. | Picking the cards that match the question |
| **Re-ranking** | The found chunks are checked again and put in a better order. | A second look to pick the best cards |
| **Generation** | Gemini writes an answer using only the retrieved chunks. | Writing the answer from the chosen cards |
| **Pipeline** | Retrieval, re-ranking and generation are joined into one flow. | One button that does all the steps |

---

## Technical Design Decisions

- **Page numbers are kept from the start.** Ingestion saves the page (or slide) with every piece of text, so each answer can point to its source.
- **Answers come only from retrieved chunks.** The prompt tells the model to use the retrieved text, which reduces made-up answers.
- **Plain Python files instead of notebooks.** Notebooks were used at the start to explore ideas. The final project uses `.py` files because they are easier to test, reuse and run from the app.
- **One folder per pipeline stage in `src/`.** Each stage can be changed or tested on its own.
- **Evaluation files stay out of GitHub.** The documents used for testing are listed in `.gitignore`. Only the questions are committed.
- **Secrets stay out of the code.** The Gemini API key is read from `.env`, and `.env` is in `.gitignore`.

---

## Evaluation and Testing

The goal of the evaluation is to check how accurately the system finds the right page for a question.

**How it works**

1. Four documents (three PDFs and one PowerPoint) are ingested into one collection.
2. `test/eval_questions.json` holds questions, each with the page where the answer really is (`expected_page`).
3. `run_retrieval_evals.py` runs every question through retrieval and checks whether the expected page was found.
4. Failed questions are reviewed to see what to improve.

**Result:** [19 out of 20 found correct page and answer]

**Run the evaluation**

```bash
python src/evaluation/ingest_evals_docs.py
python src/evaluation/run_retrieval_evals.py
```

**Run the tests**

```bash
pytest
```

---

## Installation and Setup

These steps are for Windows.

**1. Clone the repository**

```bash
git clone https://github.com/marywarimi/RAG-Assistant.git
cd RAG-Assistant
```

**2. Create a virtual environment**

```bash
python -m venv .venv
```

**3. Activate it**

```bash
.venv\Scripts\activate
```

(On Mac or Linux the command is `source .venv/bin/activate`.)

**4. Install the packages**

```bash
pip install -r requirements.txt
```

**5. Set up your keys**

Copy `.env.example` to `.env`, then add your own Google Gemini API key inside `.env`. Use the variable name shown in `.env.example`. Never upload your real `.env`.

**6. Run the app**

```bash
streamlit run frontend/streamlit_app.py
```

---

## Project Structure

```text
RAG-Assistant/
|-- .streamlit/
|   `-- config.toml            # Streamlit settings
|-- .env.example               # Template for secret keys (no real keys here)
|-- .gitignore                 # Files Git should ignore (.venv, .env, __pycache__)
|-- main.py                    # Entry point of the project
|-- README.md                  # This file
|-- requirements.txt           # Python packages to install
|
|-- Data/
|   `-- papers/
|       |-- raw/               # Original uploaded files (not committed)
|       `-- processed/         # Cleaned text extracted from files
|
|-- vector_store/              # Saved embeddings (created when you ingest files)
|
|-- frontend/
|   `-- streamlit_app.py       # The web app: upload box, question box, answer
|
|-- src/
|   |-- ingestion/
|   |   |-- pdf_reader.py      # Reads text and page numbers from PDFs
|   |   `-- pptx_reader.py     # Reads text and slide numbers from PowerPoints
|   |-- chunking/
|   |   `-- chunker.py         # Cuts text into small pieces
|   |-- embeddings/
|   |   `-- embedder.py        # Turns chunks into vectors
|   |-- vector_store/
|   |   `-- store.py           # Saves and searches the vectors
|   |-- retrieve/
|   |   `-- retrieve.py        # Finds the closest chunks to a question
|   |-- reranking/
|   |   `-- reranking.py       # Re-orders the retrieved chunks
|   |-- generation/
|   |   `-- generation.py      # Builds the prompt and asks Gemini for the answer
|   `-- evaluation/
|       |-- check_resources.py       # Checks the evaluation files are ready
|       |-- ingest_evals_docs.py     # Loads the evaluation documents
|       `-- run_retrieval_evals.py   # Scores retrieval accuracy
|
`-- test/
    `-- eval_questions.json    # Questions and expected pages for evaluation
```

---

## What Each Part Does

**`frontend/`** is what the user sees: the upload box, the question box and the answer with its sources.

**`src/`** holds the real, reusable code. Each folder is one stage of the pipeline, in this order: ingestion, chunking, embeddings, vector store, retrieval, re-ranking, generation.

**`src/evaluation/`** holds the scripts that measure how well retrieval works.

**`Data/`** holds the documents. Raw files stay on your computer and are not uploaded to GitHub.

**`vector_store/`** is where the saved embeddings live after you ingest a file.

**`test/`** holds the evaluation questions and the pytest tests.

**`.streamlit/config.toml`** holds the app's look and settings.

**`.env.example`** shows which keys the project needs. Copy it to `.env` and add your own key.

**`main.py`** is where the project is started from.

---

## Limitations

- Only PDF and PowerPoint (.pptx) files are supported. Older .ppt files and Word documents are not supported yet.
- Uploads are limited to 20 MB.
- The first question on a new file can take several minutes, because the file must be read and embedded first. Later questions are faster.
- The answer step depends on the Gemini service, which can sometimes be busy and return a temporary "unavailable" error. Try again after a moment.
- Retrieval can still pick the wrong page sometimes. Re-ranking helps but does not remove this completely.


---

## Future Improvements

- **Word (.docx) support**, since many organizations keep their documents in Word.
- **Faster ingestion**, so the first question does not take minutes.
- **HyDE** (Hypothetical Document Embeddings) to improve how questions are matched to chunks.
- **LangChain**, to simplify and standardize the pipeline.
- **Vectorless RAG**, an approach that finds answers without a vector store, to compare against this design.
- **An API layer** between the front end and the back end.
- **CI/CD** with GitHub Actions to run the tests on every push.

---

## Key Terms

- **RAG:** Retrieval-Augmented Generation. Find the right text first, then let the AI answer using that text.
- **Chunk:** A small piece of a document.
- **Embedding:** A list of numbers that represents the meaning of a chunk.
- **Vector store:** A place that stores embeddings so they can be searched by meaning.
- **Retrieval:** Finding the chunks closest to a question.
- **Re-ranking:** Checking the found chunks again and putting the best ones first.
- **Generation:** The language model writing the final answer.
- **Pipeline:** Several steps joined so they run one after another.

---

## Author

**MARY WARIMI**

[LinkedIn](https://www.linkedin.com/in/mary-warimi-0476603a1) | [GitHub](https://github.com/marywarimi)
