# Sample Corpus: Personal Knowledge Index

## Project definition
This tool answers questions using ONLY the documents in the /docs folder.
It does not browse the web.
If the answer is not in the provided documents, it must say: "Not found in corpus."

## Non-goals
- Not a chatbot
- Not a notes app
- Not internet-connected

## Chunking rules (v1)
- Target chunk size: 800 characters
- Chunk overlap: 120 characters
- Split preference:
  1) headings
  2) paragraphs
  3) sentences
  4) hard character cut as last resort

## Terms
- Corpus: the set of files in /docs
- Chunk: a slice of text that is embedded
- Top-K: the number of chunks retrieved for a question

## Facts for retrieval testing
- The repo name is: personal-knowledge-index
- The CLI command will be: python ask.py "..."
- The system uses a local vector index (FAISS)
- The index file will be stored in: ./index/

## Mini FAQ
Q: What happens if the answer is missing?
A: The system must not guess. It must say it is not found in corpus.

Q: What is the intended input format?
A: Markdown files (.md) placed in /docs
