def chunk_pages(pages, chunk_size=700, overlap=100):
    chunks = []
    step = chunk_size - overlap
    chunk_id = 0

    if step <= 0:
        raise ValueError("chunk_size must be greater than overlap.")

    for page in pages:
        text = page["text"]

        for i in range(0, len(text), step):
            chunk_text = text[i : i + chunk_size]

            if not chunk_text.strip():
                continue

            chunks.append(
                {
                    "text": chunk_text,
                    "source": page["source"],
                    "page": page["page"],
                    "chunk_id": chunk_id,
                }
            )
            chunk_id += 1

    return chunks

