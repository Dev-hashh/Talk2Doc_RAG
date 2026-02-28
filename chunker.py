def chunk_pages(pages, chunk_size=700, overlap=100):
    chunks = []
    step = chunk_size - overlap
    chunk_id = 0

    for page in pages:
        text = page["text"]

        for i in range(0, len(text), step):
            chunk_text = text[i:i+chunk_size]

            if not chunk_text.strip():
                continue

            chunks.append({
                "text": chunk_text,
                "source": page["source"],
                "page": page["page"],
                "chunk_id": chunk_id
            })

            chunk_id += 1

        if i + chunk_size >= len(text):
            break

    return chunks



# text = "abcdefghijklmnopqrstuvwxyz" * 50  # 1300 chars
# chunks = chunk_text(text, chunk_size=700, overlap=100)

# print("Total length:", len(text))
# print("Number of chunks:", len(chunks))

# for i, c in enumerate(chunks):
#     print(f"Chunk {i}: length={len(c)}")