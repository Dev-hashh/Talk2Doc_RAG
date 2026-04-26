def chunk_pages(pages, chunk_size=700, overlap=100, min_chunk_length=20):
    chunks = []
    step = chunk_size - overlap
    chunk_id = 0

    if step <= 0:
        raise ValueError("chunk_size must be greater than overlap.")
    
    for page in pages:
        text = page["text"]

        for i in range(0, len(text), step):
            chunk_text = text[i : i + chunk_size]

            if len(chunk_text.strip()) < min_chunk_length:
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



if __name__ == "__main__":
    from chunker import chunk_pages  # ← also fix: should just use the local function

    pages = [{"text": "A" * 1000, "source": "test.pdf", "page": 1}]
    chunks = chunk_pages(pages, chunk_size=700, overlap=100)
    assert len(chunks) > 0
    assert all(len(c["text"]) <= 700 for c in chunks)
    assert chunks[0]["text"][600:] == chunks[1]["text"][:100]

    pages = [{"text": "Hi", "source": "test.pdf", "page": 1}]
    chunks = chunk_pages(pages, chunk_size=700, overlap=100)
    assert chunks == []

    try:
        chunk_pages(pages, chunk_size=100, overlap=100)
        assert False, "Should have raised"
    except ValueError:
        pass

    print("All chunker tests passed.")
