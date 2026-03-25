import faiss
import numpy as np


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

    def save(self, path="faiss.index"):
        faiss.write_index(self.index, path)

    def load(self, path="faiss.index"):
        self.index = faiss.read_index(path)

