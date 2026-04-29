"""
ingest_service.py
Orchestrates the full ingest pipeline:
    PDF bytes → text extraction → chunking → embedding → FAISS index → disk
Wraps the docchat package that lives at the project root.
"""
from __future__ import annotations

import pickle
import tempfile
from pathlib import Path
from typing import Tuple

import faiss
import numpy as np

from app.config import settings

# ── docchat package imports ───────────────────────────────────────────────────
# The docchat package is located at the project root (a sibling of backend/).
# When the server is launched from the project root these imports resolve fine.
from docchat.document_loader import load_pdf
from docchat.chunker import chunk_pages
from docchat.embedder import Embedder


_embedder: Embedder | None = None


def _get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder(model_name=settings.embedding_model)
    return _embedder


def _load_pages_from_upload(pdf_bytes: bytes, pdf_filename: str) -> list[dict]:
    suffix = Path(pdf_filename).suffix or ".pdf"
    with tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=suffix,
        delete=False,
        dir=settings.index_path,
    ) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = Path(tmp.name)

    try:
        pages = load_pdf(str(tmp_path))
        for page in pages:
            page["source"] = pdf_filename
        return pages
    finally:
        tmp_path.unlink(missing_ok=True)


# ─────────────────────────────────────────────────────────────────────────────

def ingest_pdf(
    pdf_bytes: bytes,
    pdf_filename: str,
    index_name: str | None = None,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> Tuple[str, int]:
    """
    Full ingest pipeline.

    Parameters
    ----------
    pdf_bytes    : raw bytes of the uploaded PDF
    pdf_filename : original filename (used to derive a default index name)
    index_name   : explicit index stem to save as (optional)
    chunk_size   : characters per chunk (falls back to config default)
    overlap      : overlap between chunks (falls back to config default)

    Returns
    -------
    (index_stem, num_chunks)
    """
    chunk_size = chunk_size or settings.default_chunk_size
    overlap = overlap or settings.default_overlap

    # 1. Derive index stem
    stem = index_name or Path(pdf_filename).stem.replace(" ", "_").lower()

    # 2. Extract page records from the uploaded PDF
    pages = _load_pages_from_upload(pdf_bytes, pdf_filename)

    # 3. Chunk pages into metadata-rich chunk dicts
    chunks: list[dict] = chunk_pages(pages, chunk_size=chunk_size, overlap=overlap)
    if not chunks:
        raise ValueError("No text could be extracted from the PDF.")

    # 4. Embed
    embedder = _get_embedder()
    vectors: np.ndarray = embedder.embed_documents(chunks)   # shape (n, dim)

    # 5. Build FAISS index
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors.astype(np.float32))

    # 6. Persist
    faiss.write_index(index, str(settings.index_file(stem)))
    with open(settings.metadata_file(stem), "wb") as f:
        pickle.dump(chunks, f)

    return stem, len(chunks)
