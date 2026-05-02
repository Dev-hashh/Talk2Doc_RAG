from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np

from app.config import settings
from docchat.embedder import Embedder
from docchat.generator import Generator
from docchat.storage import download_index  # ✅ replaces _load_index


_embedder: Embedder | None = None


def _get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder(model_name=settings.embedding_model)
    return _embedder


def answer_question(
    question: str,
    index_name: str | None = None,
    top_k: int | None = None,
    model: str | None = None,
    user_id: str | None = None,
) -> Tuple[str, str, list[dict]]:

    print(f"DEBUG user_id={user_id!r}, type={type(user_id)}")

    stem = index_name or settings.default_index_stem
    top_k = top_k or settings.default_top_k
    model = model or settings.model_name

    # ✅ Load from Supabase instead of local disk
    index, chunks = download_index(str(user_id), stem)

    embedder = _get_embedder()
    q_vector: np.ndarray = embedder.embed_query(question)
    q_vector = q_vector.reshape(1, -1).astype(np.float32)

    distances, indices = index.search(q_vector, top_k)

    retrieved: list[dict] = [
        chunks[i] for i in indices[0] if 0 <= i < len(chunks)
    ]

    context = "\n\n---\n\n".join(chunk["text"] for chunk in retrieved)

    if settings.USE_GROQ:
        from docchat.groq_generator import GroqGenerator
        generator = GroqGenerator(api_key=settings.GROQ_API_KEY)
    else:
        generator = Generator(model_name=model, url=settings.ollama_url)

    answer: str = generator.generate_answer(context=context, question=question)

    return answer, stem, retrieved