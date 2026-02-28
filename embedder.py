from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name="BAAI/bge-small-en"):
        print("Loading embedding model...")
        self.model = SentenceTransformer(model_name)
        print("Embedding model loaded.")

    def embed_documents(self, documents):
        """
        documents: list[str]
        returns: numpy array
        """
        formatted_docs = ["passage: " + doc["text"] for doc in documents]
        embeddings = self.model.encode(
            formatted_docs,
            normalize_embeddings=True
        )
        return embeddings

    def embed_query(self, query):
        """
        query: str
        returns: numpy array
        """
        embedding = self.model.encode(
            "query: " + query,
            normalize_embeddings=True
        )
        return embedding