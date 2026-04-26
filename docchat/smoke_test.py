import pickle, numpy as np
from unittest.mock import patch, MagicMock
from chunker import chunk_pages
from embedder import Embedder
from vector_store import VectorStore
from retriever import Retriever
import generator

# Build a fake "document"
pages = [{"text": "The Eiffel Tower is located in Paris, France. " * 20, "source": "fake.pdf", "page": 1}]
chunks = chunk_pages(pages)
print(f"Chunks created: {len(chunks)}")

embedder = Embedder()
embeddings = embedder.embed_documents(chunks)

vs = VectorStore()
vs.add(embeddings, chunks)

retriever = Retriever(embedder, vs)
results = retriever.retrieve("Where is the Eiffel Tower?", k=2)
print(f"Retrieved {len(results)} chunks")
assert len(results) > 0
assert "Paris" in results[0]["text"]

# Mock LLM call
mock_resp = MagicMock()
mock_resp.json.return_value = {"response": "Paris, France"}
mock_resp.raise_for_status = MagicMock()

with patch("generator.requests.post", return_value=mock_resp):
    g = generator.Generator()
    answer = g.generate(results[0]["text"], "Where is the Eiffel Tower?")
    print(f"Answer: {answer}")
    assert answer == "Paris, France"

print("All smoke tests passed.")