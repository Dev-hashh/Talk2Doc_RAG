from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name="BAAI/bge-small-en"):
        print("Loading embedding model...")
        self.model = SentenceTransformer(model_name)
        print("Embedding model loaded.")

    def embed_documents(self, documents):
        formatted_docs = ["passage: " + doc["text"] for doc in documents]
        return self.model.encode(formatted_docs, normalize_embeddings=True)

    def embed_query(self, query):
        return self.model.encode("query: " + query, normalize_embeddings=True)

