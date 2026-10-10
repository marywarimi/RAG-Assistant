# Academic Research Assistant (RAG Assistant)

A Retrieval-Augmented Generation (RAG) assistant that helps students find answers inside their own research papers. A student uploads a PDF (or another supported file), asks a question, and gets an answer that is based only on that document, with the source pages shown.

> **Project status:** work in progress. The folder structure and the first notebooks are in place. Ingestion, embeddings, retrieval, generation and the Streamlit app are being built step by step (see the [Roadmap](#roadmap)).

---

## Table of Contents

1. [What This Project Does](#what-this-project-does)
2. [How It Works](#how-it-works)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [What Each Part Does](#what-each-part-does)
6. [Getting Started (Windows)](#getting-started-windows)
7. [Roadmap](#roadmap)
8. [Testing](#testing)
9. [Key Terms](#key-terms)
10. [Author](#author)

---

## What This Project Does

Reading long research papers takes time. This assistant lets a student:

- Upload a document (PDF or similar, with a file size limit).
- Ask questions in plain language.
- Get an answer grounded in the uploaded document, not made up.
- See which parts of the document the answer came from.

---

## How It Works

The document goes through these stages:

| Stage | What happens | Simple picture |
|---|---|---|
| **Front end** | The student uploads a file and asks a question (built with Streamlit). | The table where you drop your notes |
| **Ingestion** | The document is brought into the system and its text is read, with page numbers kept. | Opening the paper and reading it |
| **Chunking** | The text is cut into small pieces. | Cutting a long paper into index cards |
| **Embeddings** | Each chunk is turned into a list of numbers that captures its meaning. | Giving each card a "meaning code" |
| **Vector store** | The embeddings and chunks are saved so they can be searched. | The shelf that holds all the cards |
| **Retrieval** | The question is turned into numbers too, and the closest chunks are found. | Picking the cards that match the question |
| **Generation** | A language model writes an answer using only the retrieved chunks. | Writing the answer from the chosen cards |
| **Pipeline** | Retrieval and generation are joined into one flow. | One button that does both steps |

```text
Upload -> Ingestion -> Chunking -> Embeddings -> Vector store
                                                     |
Question -> Retrieval <------------------------------+
               |
           Generation -> Answer + sources
```

The front end and the back end talk to each other through function calls first. An API layer may be added later.

---

## Tech Stack

- **Language:** Python
- **Front end:** Streamlit
- **Notebooks:** Jupyter (in VS Code)
- **Testing:** pytest
- **Version control:** Git and GitHub
- **Config:** environment variables in a `.env` file (never committed)

---

## Project Structure

```text
RAG-Assistant/
|-- .env.example          # Template for secret keys (no real keys here)
|-- .gitignore            # Files Git should ignore (.venv, .env, __pycache__)
|-- main.py               # Entry point of the project
|-- README.md             # This file
|-- requirements.txt      # Python packages to install
|
|-- Data/
|   `-- papers/
|       |-- raw/          # Original uploaded papers (not committed)
|       `-- processed/    # Cleaned text extracted from papers
|
|-- Notebooks/
|   |-- 01_document_processing.ipynb
|   |-- 02_embeddings.ipynb
|   `-- 03_retrieval.ipynb
|
|-- src/
|   |-- ingestion/        # Load documents and read their text
|   |-- embeddings/       # Turn chunks into vectors
|   |-- retrieval/        # Find the most relevant chunks
|   |-- generation/       # Write answers from the retrieved chunks
|   `-- evaluation/       # Measure answer and retrieval quality
|
`-- test/                 # Tests for the code in src/
```

---

## What Each Part Does

**Notebooks** are where I explore and test each idea first, one stage at a time. Once an idea works, the code moves into `src/`.

**`src/`** holds the real, reusable code. Each folder is one stage of the pipeline.

**`Data/`** holds the papers. Raw files stay local. Processed text is what the later stages use.

**`test/`** holds pytest tests that check each stage works.

**`.env.example`** shows which keys the project needs (for example an LLM API key). Copy it to `.env` and add your own key. Never upload your real `.env`.

**`main.py`** is where the project is started from.

---

## Getting Started (Windows)

**1. Clone the repository**

```bash
git clone https://github.com/<your-username>/RAG-Assistant.git
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

Copy `.env.example` to `.env`, then add your own API key inside `.env`.

**6. Open the notebooks**

Open the `Notebooks/` folder in VS Code and pick the `.venv` kernel before running any cell.

---

## Roadmap

- [x] Create the GitHub repository and clone it
- [x] Set up the folder structure
- [ ] Ingestion: read PDFs and keep page numbers
- [ ] Chunking: split text into small pieces
- [ ] Embeddings: turn chunks into vectors
- [ ] Vector store: save and search the vectors
- [ ] Retrieval: find the best chunks for a question
- [ ] Generation: write source-based answers
- [ ] Pipeline: connect retrieval and generation
- [ ] Streamlit front end: upload box, question box, answer and sources
- [ ] Tests with pytest
- [ ] Evaluation metrics
- [ ] CI/CD with GitHub Actions

---

## Testing

Once tests are added, run them from the project folder:

```bash
pytest
```

---

## Key Terms

- **RAG:** Retrieval-Augmented Generation. Find the right text first, then let the AI answer using that text.
- **Chunk:** A small piece of a document.
- **Embedding:** A list of numbers that represents the meaning of a chunk.
- **Vector store:** A place that stores embeddings so they can be searched by meaning.
- **Retrieval:** Finding the chunks closest to a question.
- **Generation:** The language model writing the final answer.
- **Pipeline:** Several steps joined so they run one after another.

---

## Author

**Mary**

