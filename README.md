# Background
A minimal RAG tool that answers questions only from your own notes, documents, or articles.

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
