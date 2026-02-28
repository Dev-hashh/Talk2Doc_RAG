import document_loader
import chunker

from embedder import Embedder
from vector_store import VectorStore
from retriever import Retriever
from generator import Generator


# 1. Load document
print("Loading document...")
pages = document_loader.load_pdf("DBMS .pdf")

# 2. Chunk
print("Chunking document...")
chunks = chunker.chunk_pages(pages)
print("Total chunks:", len(chunks))
# print("Total vectors in index:", vector_store.index.ntotal)

# 3. Embed
embedder = Embedder()
doc_embeddings = embedder.embed_documents(chunks)

# 4. Create vector store
vector_store = VectorStore()
vector_store.add(doc_embeddings, chunks)
print("Total vectors in index:", vector_store.index.ntotal)

# 5. Create retriever
retriever = Retriever(embedder, vector_store)

# 6. Create generator
generator = Generator()

# 7. Query loop
while True:
    query = input("\nAsk a question (or type 'exit'): ")

    if query.lower() == "exit":
        break


    
    retrieved_chunks = retriever.retrieve(query, k=3)

    context = "\n".join([chunk["text"] for chunk in retrieved_chunks])

    print("\nSources:")
    for chunk in retrieved_chunks:
        print(f"- {chunk['source']} | page {chunk['page']} | chunk {chunk['chunk_id']}")
        # print("Distances:", D)
        # print("Indices:", I)

    answer = generator.generate(context, query)

    print("\nAnswer:\n", answer)