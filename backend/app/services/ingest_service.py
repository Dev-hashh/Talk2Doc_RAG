from __future__ import annotations

import os
import pickle
import tempfile
from pathlib import Path
from typing import Tuple

import faiss
import numpy as np

from app.config import settings
from docchat.document_loader import load_pdf
from docchat.chunker import chunk_pages
from docchat.embedder import Embedder
from docchat.storage import upload_index


_embedder: Embedder | None = None


def _get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder(model_name=settings.embedding_model)
    return _embedder


# 🔐 NEW
def _user_index_path(user_id: str) -> Path:
    path = settings.index_path / str(user_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load_pages_from_upload(pdf_bytes: bytes, pdf_filename: str) -> list[dict]:
    suffix = Path(pdf_filename).suffix or ".pdf"

    with tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=suffix,
        delete=False,
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


def ingest_pdf(
    pdf_bytes: bytes,
    pdf_filename: str,
    index_name: str | None = None,
    chunk_size: int | None = None,
    overlap: int | None = None,
    user_id: str | None = None,   # ✅ NEW
) -> Tuple[str, int]:

    chunk_size = chunk_size or settings.default_chunk_size
    overlap = overlap or settings.default_overlap

    stem = index_name or Path(pdf_filename).stem.replace(" ", "_").lower()

    pages = _load_pages_from_upload(pdf_bytes, pdf_filename)

    chunks: list[dict] = chunk_pages(pages, chunk_size=chunk_size, overlap=overlap)
    if not chunks:
        raise ValueError("No text could be extracted from the PDF.")

    embedder = _get_embedder()
    vectors: np.ndarray = embedder.embed_documents(chunks)

    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors.astype(np.float32))

    # 🔐 SAVE PER USER
    # base_path = _user_index_path(user_id)
    # index_path = base_path / f"{stem}.index"
    # metadata_path = base_path / f"{stem}.pkl"
    
    #Upload to Supabase Storage
    upload_index(user_id=str(user_id), stem=stem, index=index, chunks=chunks)

    faiss.write_index(index, str(index_path))

    with open(metadata_path, "wb") as f:
        pickle.dump(chunks, f)

    return stem, len(chunks)