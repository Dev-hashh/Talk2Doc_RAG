"""
chat_service.py
Orchestrates the RAG query pipeline:
    question → embed → FAISS retrieval → context assembly → Ollama → answer
Wraps the docchat package that lives at the project root.
"""
from __future__ import annotations

import pickle
from typing import Tuple

import faiss
import numpy as np

from app.config import settings
from app.services.index_service import index_exists

# ── docchat package imports ───────────────────────────────────────────────────
from docchat.embedder import Embedder
from docchat.generator import Generator             #generate_answer to Generator

# Module-level singleton — avoids reloading the model on every request
_embedder: Embedder | None = None

def _get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder(model_name=settings.embedding_model)
    return _embedder


# ─────────────────────────────────────────────────────────────────────────────

def _load_index(stem: str) -> Tuple[faiss.Index, list[dict]]:
    """Load a FAISS index and its chunk metadata from disk."""
    index = faiss.read_index(str(settings.index_file(stem)))
    with open(settings.metadata_file(stem), "rb") as f:
        chunks: list[dict] = pickle.load(f)
    return index, chunks


def answer_question(
    question: str,
    index_name: str | None = None,
    top_k: int | None = None,
    model: str | None = None,
) -> Tuple[str, str, list[dict]]:
    """
    Full RAG query pipeline.

    Parameters
    ----------
    question   : the user's natural-language question
    index_name : which FAISS index to query (defaults to settings.default_index_stem)
    top_k      : number of chunks to retrieve
    model      : Ollama model override

    Returns
    -------
    (answer_text, index_stem_used, retrieved_chunks)
    """
    stem = index_name or settings.default_index_stem
    top_k = top_k or settings.default_top_k
    model = model or settings.model_name

    if not index_exists(stem):
        raise FileNotFoundError(
            f"Index '{stem}' not found. "
            "Please ingest a PDF first via POST /ingest."
        )

    # 1. Load index + metadata
    index, chunks = _load_index(stem)

    # 2. Embed the question using embed_query (applies "query: " prefix + normalisation)
    embedder = _get_embedder()
    q_vector: np.ndarray = embedder.embed_query(question)          # shape (dim,)
    q_vector = q_vector.reshape(1, -1).astype(np.float32)          # → (1, dim) for FAISS

    # 3. Retrieve top-k nearest chunks
    distances, indices = index.search(q_vector, top_k)
    retrieved: list[dict] = [
        chunks[i] for i in indices[0] if 0 <= i < len(chunks)
    ]

    # 4. Assemble context and call Ollama
    context = "\n\n---\n\n".join(chunk["text"] for chunk in retrieved)
    generator = Generator(model_name=model, url=settings.ollama_url)
    answer: str = generator.generate_answer(context=context, question=question)

    return answer, stem, retrieved

