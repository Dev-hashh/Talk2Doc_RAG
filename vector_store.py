from importlib.resources import path

import faiss
import numpy as np
print("FAISS version:", faiss.__version__)
class VectorStore:
    def __init__(self, dimension=384):
        print("Initializing FAISS index...")
        self.index = faiss.IndexFlatIP(dimension)  # cosine similarity
        self.documents = []
        print("FAISS index ready.")

    def add(self, embeddings, documents):
        """
        embeddings: numpy array
        documents: list[str]
        """
        self.index.add(np.array(embeddings))
        self.documents.extend(documents)

    def search(self, query_embedding, k=3):
        k = min(k, self.index.ntotal)

        D, I = self.index.search(
            np.array([query_embedding]),
            k
        )
        print("Distances:", D)
        print("Indices:", I)

        # Remove duplicate indices
        unique_indices = []
        for idx in I[0]:
            if idx not in unique_indices:
                unique_indices.append(idx)

        results = [self.documents[i] for i in unique_indices]
        return results
    
    def save(self, path="faiss.index"):
        faiss.write_index(self.index, path)

    def load(self, path="faiss.index"):
        self.index = faiss.read_index(path)
        
        