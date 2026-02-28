import pickle
import numpy as np

from embedder import Embedder
from vector_store import VectorStore
from retriever import Retriever
from generator import Generator


INDEX_PATH = "faiss.index"
METADATA_PATH = "metadata.pkl"


print("Loading index...")
vector_store = VectorStore()
vector_store.load(INDEX_PATH)

print("Loading metadata...")
with open(METADATA_PATH, "rb") as f:
    chunks = pickle.load(f)

vector_store.documents = chunks

embedder = Embedder()
retriever = Retriever(embedder, vector_store)
generator = Generator()


while True:
    query = input("\nAsk a question (or type 'exit'): ")

    if query.lower() == "exit":
        break

    retrieved_chunks = retriever.retrieve(query, k=3)

    context = "\n".join([chunk["text"] for chunk in retrieved_chunks])

    print("\nSources:")
    for chunk in retrieved_chunks:
        print(f"- {chunk['source']} | page {chunk['page']} | chunk {chunk['chunk_id']}")

    answer = generator.generate(context, query)

    print("\nAnswer:\n", answer)