from __future__ import annotations

import hashlib
import re

import numpy as np


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")
HASHING_MODELS = {"hashing", "hash", "local-hashing"}


class Embedder:
    def __init__(self, model_name="BAAI/bge-small-en"):
        self.model_name = model_name
        self.model = None
        self.dim = 384

        if model_name.lower() in HASHING_MODELS:
            print("Using low-memory hashing embeddings.")
            return

        print("Loading embedding model...")
        try:
            from sentence_transformers import SentenceTransformer
        except ModuleNotFoundError:
            print(
                "sentence-transformers is not installed; "
                "falling back to low-memory hashing embeddings."
            )
            return

        self.model = SentenceTransformer(model_name)
        print("Embedding model loaded.")

    def _hashing_encode(self, texts: list[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dim), dtype=np.float32)

        for row, text in enumerate(texts):
            for token in TOKEN_RE.findall(text.lower()):
                digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
                bucket = int.from_bytes(digest[:4], "little") % self.dim
                sign = 1.0 if digest[4] & 1 else -1.0
                vectors[row, bucket] += sign

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        np.divide(vectors, norms, out=vectors, where=norms != 0)
        return vectors

    def _encode(self, texts: list[str] | str) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]

        if self.model is None:
            vectors = self._hashing_encode(texts)
        else:
            vectors = self.model.encode(texts, normalize_embeddings=True)

        return np.asarray(vectors, dtype=np.float32)

    def embed_documents(self, documents):
        formatted_docs = ["passage: " + doc["text"] for doc in documents]
        return self._encode(formatted_docs)

    def embed_query(self, query):
        return self._encode("query: " + query)[0]
