# Background
A minimal ml system that lets you ask questions against your own notes, documents, or articles and nothing else.

## personal-knowledge-Index
1. You provide documents
2. They are chunked
3. Chunks are embedded
4. A question retrieves the most relevant chunks
5. The model answers using only those chunks

## Out of Scope (Explicit Non-Goals)
Not a chatbot
Not connected to the internet
Not trained on external data
Not a productivity app
   
## Why this exists
* * fill in here with case studies * *

 Documents (.md)
      ↓
Chunker
      ↓
Embeddings
      ↓
Vector Store
      ↓
Query
      ↓
Top-K chunks
      ↓
LLM answer (constrained)


personal-knowledge-index/
├── README.md
├── docs/
│   └── sample.md
├── ingest.py
├── ask.py
├── requirements.txt
└── notes.md   # your own dev notes
