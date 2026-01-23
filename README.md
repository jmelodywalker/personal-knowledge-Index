# Background
A minimal RAG tool that lets you define your own corpus (notes, documents, or articles), ask questions about your corpus, and get answers **only when the information exists in your corpus**.

## personal-knowledge-Index
1. You provide documents
2. They are chunked
3. Chunks are embedded
4. A question retrieves the most relevant chunks
5. The model answers using only those chunks

## Out of Scope (Explicit Non-Goals)
* Not a chatbot
* Not connected to the internet
* Not trained on external data
* Not a productivity app

## In Scope (Why This Exists)
The repo is intentionally small.

this exists to demonstrate:
	•	real API usage
	•	real retrieval
	•	real failure modes
	•	real cost surfaces
	•	and a clean mental model for RAG systems

#RAG #Retrieval-Augmented Generation #llm-demo
   
---

## What This Is

`personal-knowledge-index` is a local, minimal RAG system that is a corpus-bound / question-answering tool.  
It lets you query your own documents and get answers **only when the information exists in your corpus**.

If the answer is not present, the system returns: "Not found in corpus."

## The Problem It Solves

Most “RAG demos” still hallucinate when retrieval is weak.

This project demonstrates:
- strict containment
- deterministic retrieval
- explicit refusal to answer outside the corpus

The goal is **correctness over coverage**.

---

## How it Works (System Pipeline)

```text
Documents (.md) -> Chunker -> Embeddings -> Vector Store -> Query -> Top-K chunks -> LLM answer (constrained)

Repo Layout:
personal-knowledge-index/
├── README.md
├── docs/
│   └── sample.md
├── ingest.py
├── ask.py
├── requirements.txt
└── notes.md   # your own dev notes

personal-knowledge-index/
├── README.md
├── docs/
│   └── sample.md        # example corpus
├── index/               # persisted embeddings + FAISS index
│   └── .gitkeep
├── ingest.py            # chunk + embed + index documents
├── ask.py               # query + retrieve + answer
├── requirements.txt


Documents (.md)
↓
Deterministic chunking
↓
Embeddings (persisted locally)
↓
FAISS vector index
↓
Query embedding
↓
Top-K chunk retrieval
↓
LLM answers using only retrieved chunks

If retrieval cannot support an answer, the system exits early.

---

## Proof of Correctness (The Contract)

This system enforces a hard contract:

> If the answer is not explicitly present in the corpus, the model must not answer.

Example output: 
Answer (corpus-only): Not found in corpus.

This is enforced by:
- retrieval thresholds
- prompt constraints
- post-generation guards

fallback knowledge = No, guessing = No


## How to Run (3 Commands)

```bash
pip install -r requirements.txt
python ingest.py
python ask.py "Where is the index stored?"

Expected answer (from the sample corpus): ./index/

⸻

Extensions (Intentionally Deferred)

Possible future enhancements (not implemented here):
	•	citations per answer
	•	model switching via environment variables
	•	incremental re-ingestion
	•	token usage logging

These are omitted to preserve clarity and correctness.

⸻

License

MIT
