from __future__ import annotations

import pickle
from pathlib import Path
from typing import Tuple

import faiss
import numpy as np

from app.config import settings
from docchat.embedder import Embedder
from docchat.generator import Generator


_embedder: Embedder | None = None


def _get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder(model_name=settings.embedding_model)
    return _embedder


# 🔐 NEW
def _user_index_path(user_id: str) -> Path:
    return settings.index_path / str(user_id)


def _index_file(user_id: str, stem: str) -> Path:
    return _user_index_path(user_id) / f"{stem}.index"


def _metadata_file(user_id: str, stem: str) -> Path:
    return _user_index_path(user_id) / f"{stem}.pkl"


def _load_index(user_id: str, stem: str) -> Tuple[faiss.Index, list[dict]]:
    index_path = _index_file(user_id, stem)
    metadata_path = _metadata_file(user_id, stem)

    if not index_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(f"Index '{stem}' not found for this user.")

    index = faiss.read_index(str(index_path))

    with open(metadata_path, "rb") as f:
        chunks: list[dict] = pickle.load(f)

    return index, chunks


def answer_question(
    question: str,
    index_name: str | None = None,
    top_k: int | None = None,
    model: str | None = None,
    user_id: str | None = None,   # ✅ NEW
) -> Tuple[str, str, list[dict]]:

    print(f"DEBUG user_id={user_id!r}, type={type(user_id)}") 
    stem = index_name or settings.default_index_stem
    top_k = top_k or settings.default_top_k
    model = model or settings.model_name

    # 🔐 LOAD ONLY USER INDEX
    index, chunks = _load_index(user_id, stem)

    embedder = _get_embedder()
    q_vector: np.ndarray = embedder.embed_query(question)
    q_vector = q_vector.reshape(1, -1).astype(np.float32)

    distances, indices = index.search(q_vector, top_k)

    retrieved: list[dict] = [
        chunks[i] for i in indices[0] if 0 <= i < len(chunks)
    ]

    context = "\n\n---\n\n".join(chunk["text"] for chunk in retrieved)

    generator = Generator(model_name=model, url=settings.ollama_url)
    answer: str = generator.generate_answer(context=context, question=question)

    return answer, stem, retrieved