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

##Unit tests for VectorStore
if __name__ == "__main__":
    import numpy as np
    from vector_store import VectorStore

    vs = VectorStore(dimension=4)
    embeddings = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], dtype="float32")
    docs = [{"text": "doc1"}, {"text": "doc2"}]
    vs.add(embeddings, docs)

    # Search returns correct doc
    results = vs.search(np.array([1, 0, 0, 0], dtype="float32"), k=1)
    assert results[0]["text"] == "doc1"

    # Save and reload
    import tempfile, os
    test_index_path = os.path.join(tempfile.gettempdir(), "test.index")
    vs.save(test_index_path)
    vs2 = VectorStore(dimension=4)
    vs2.load(test_index_path)

    vs2.documents = docs
    results2 = vs2.search(np.array([0, 1, 0, 0], dtype="float32"), k=1)
    assert results2[0]["text"] == "doc2"

    # k > ntotal should not crash (the -1 sentinel fix)
    results3 = vs.search(np.array([1, 0, 0, 0], dtype="float32"), k=99)
    assert len(results3) == 2  # Only 2 docs exist, no -1 bleed-through