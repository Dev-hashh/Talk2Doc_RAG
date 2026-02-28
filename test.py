from email.mime import text
import sys
sys.stdout.reconfigure(encoding='utf-8')
import document_loader
import chunker

import os
print("Current working directory:", os.getcwd())
print("Files here:", os.listdir())

# Load documents
documents = document_loader.load_pdf("DBMS .pdf")
# print(f"Extracted text length: {len(documents)} characters")
# print(documents[:500])  # Print the first 500 characters of the extracted text
# print(documents)    

# Chunk documents
chunks = chunker.chunk_text(documents, chunk_size=1000, overlap=200)
print("Total length:", len(documents))
print("Number of chunks:", len(chunks))
print("Sample chunk:\n", chunks[0][:500])  # Print the first 500 characters of the first chunk

for i, c in enumerate(chunks):
    print(f"Chunk {i}: length={len(c)}, overlap={200 if i > 0 else 0}")
    



