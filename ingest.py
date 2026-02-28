
import os
import pickle

import document_loader
import chunker

from embedder import Embedder
from vector_store import VectorStore


INDEX_PATH = "faiss.index"
METADATA_PATH = "metadata.pkl"
PDF_PATH = "DBMS .pdf"


print("Loading document...")
pages = document_loader.load_pdf(PDF_PATH)

print("Chunking document...")
chunks = chunker.chunk_pages(pages)
print("Total chunks:", len(chunks))

if len(chunks) == 0:
    raise ValueError("No chunks created. Check PDF extraction.")

# Embed
embedder = Embedder()
doc_embeddings = embedder.embed_documents(chunks)

# Create vector store
vector_store = VectorStore()
vector_store.add(doc_embeddings, chunks)

print("Saving FAISS index...")
vector_store.save(INDEX_PATH)

print("Saving metadata...")
with open(METADATA_PATH, "wb") as f:
    pickle.dump(chunks, f)

print("Ingestion complete.")