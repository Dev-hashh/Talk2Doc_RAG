
import pickle
import tempfile
from pathlib import Path

import faiss
import numpy as np

from docchat.storage import upload_index, download_index


class VectorStore:
    def __init__(self, dimension=384):
        print("Initializing FAISS index...")
        self.index = faiss.IndexFlatIP(dimension)
        self.documents = []
        print("FAISS index ready.")

    def add(self, embeddings, documents):
        self.index.add(np.array(embeddings))
        self.documents.extend(documents)

    def search(self, query_embedding, k=3):
        k = min(k, self.index.ntotal)
        if k == 0:
            return []

        _, indices = self.index.search(np.array([query_embedding]), k)

        unique_indices = []
        for idx in indices[0]:
            if idx not in unique_indices:
                unique_indices.append(idx)

        return [self.documents[i] for i in unique_indices]

    def save(self, user_id: str, stem: str = "faiss"):
        """Upload index + documents to Supabase Storage."""
        upload_index(user_id, stem, self.index, self.documents)
        print(f"Index saved to Supabase: {user_id}/{stem}")

    def load(self, user_id: str, stem: str = "faiss"):
        """Download index + documents from Supabase Storage."""
        self.index, self.documents = download_index(user_id, stem)
        print(f"Index loaded from Supabase: {user_id}/{stem}")