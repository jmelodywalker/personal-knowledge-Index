import os
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np
import faiss
from openai import OpenAI


DOCS_DIR = Path("docs")
INDEX_DIR = Path("index")

# v1 defaults (tune later)
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
CHUNK_TARGET_CHARS = int(os.getenv("CHUNK_TARGET_CHARS", "800"))
CHUNK_OVERLAP_CHARS = int(os.getenv("CHUNK_OVERLAP_CHARS", "120"))


def read_markdown_files(docs_dir: Path) -> List[Tuple[str, str]]:
    """
    Returns list of (source_path, text).
    """
    if not docs_dir.exists():
        raise FileNotFoundError(f"Missing folder: {docs_dir.resolve()}")

    files = sorted([p for p in docs_dir.rglob("*.md") if p.is_file()])
    if not files:
        raise FileNotFoundError(f"No .md files found under: {docs_dir.resolve()}")

    out = []
    for p in files:
        text = p.read_text(encoding="utf-8", errors="ignore")
        out.append((str(p), text))
    return out


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def split_by_headings(text: str) -> List[str]:
    """
    Roughly split on markdown headings.
    Keeps heading lines with the section.
    """
    lines = text.split("\n")
    sections = []
    buf = []

    def flush():
        nonlocal buf
        if buf:
            sections.append("\n".join(buf).strip())
            buf = []

    for line in lines:
        if line.lstrip().startswith("#"):
            flush()
        buf.append(line)

    flush()
    # Remove empties
    return [s for s in sections if s.strip()]


def chunk_text(text: str, target_chars: int, overlap_chars: int) -> List[str]:
    """
    Chunk strategy:
      1) split by headings
      2) within each section, prefer paragraph splits
      3) if still too big, hard cut with overlap
    """
    text = normalize_newlines(text).strip()
    if not text:
        return []

    sections = split_by_headings(text)
    chunks: List[str] = []

    for sec in sections:
        # paragraph split (blank line)
        paras = [p.strip() for p in sec.split("\n\n") if p.strip()]
        current = ""

        def emit_current():
            nonlocal current
            if current.strip():
                chunks.append(current.strip())
            current = ""

        for p in paras:
            # if adding this paragraph stays under target, append
            candidate = (current + "\n\n" + p).strip() if current else p
            if len(candidate) <= target_chars:
                current = candidate
                continue

            # if current has content, emit it first
            if current:
                emit_current()

            # if paragraph itself is too big, hard cut it
            if len(p) > target_chars:
                start = 0
                while start < len(p):
                    end = min(start + target_chars, len(p))
                    chunk = p[start:end].strip()
                    if chunk:
                        chunks.append(chunk)
                    if end >= len(p):
                        break
                    start = max(0, end - overlap_chars)
                continue

            # else paragraph fits alone
            current = p

        emit_current()

    # optional overlap pass across chunk boundaries (lightweight)
    if overlap_chars > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = overlapped[-1]
            take = prev[-overlap_chars:] if len(prev) > overlap_chars else prev
            overlapped.append((take + "\n" + chunks[i]).strip())
        chunks = overlapped

    return [c for c in chunks if c.strip()]


def embed_texts(client: OpenAI, texts: List[str], model: str) -> np.ndarray:
    """
    Returns embeddings as float32 numpy array of shape (n, dim).
    """
    # OpenAI embeddings API supports batching via input=list
    resp = client.embeddings.create(model=model, input=texts)
    vectors = [d.embedding for d in resp.data]
    arr = np.array(vectors, dtype=np.float32)
    return arr


def build_faiss_index(vectors: np.ndarray) -> faiss.IndexFlatL2:
    if vectors.ndim != 2:
        raise ValueError("vectors must be 2D [n, dim]")
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    return index


def main() -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    files = read_markdown_files(DOCS_DIR)

    records: List[Dict[str, Any]] = []
    all_chunks: List[str] = []

    for path, text in files:
        chunks = chunk_text(text, CHUNK_TARGET_CHARS, CHUNK_OVERLAP_CHARS)
        for j, chunk in enumerate(chunks):
            rec = {
                "id": len(records),
                "source": path,
                "chunk_index": j,
                "text": chunk,
                "chars": len(chunk),
            }
            records.append(rec)
            all_chunks.append(chunk)

    if not all_chunks:
        raise RuntimeError("No chunks produced. Check docs content.")

    client = OpenAI()

    vectors = embed_texts(client, all_chunks, EMBED_MODEL)
    index = build_faiss_index(vectors)

    # Save index + metadata
    faiss_path = INDEX_DIR / "faiss.index"
    meta_path = INDEX_DIR / "chunks.json"

    faiss.write_index(index, str(faiss_path))
    meta_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    print("Ingest complete.")
    print(f"Docs files: {len(files)}")
    print(f"Chunks:     {len(records)}")
    print(f"Embed dim:  {vectors.shape[1]}")
    print(f"Saved:      {faiss_path} and {meta_path}")


if __name__ == "__main__":
    main()
