import io
import tempfile
import pickle
from pathlib import Path
import faiss
import numpy as np
from supabase import create_client

from app.config import settings

BUCKET = "Indexes"

def _client():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


def _index_key(user_id: str, stem: str) -> str:
    return f"{user_id}/{stem}.index"

def _meta_key(user_id: str, stem: str) -> str:
    return f"{user_id}/{stem}.pkl"


def upload_index(user_id: str, stem: str, index: faiss.Index, chunks: list[dict]):
    client = _client()

    # Serialize FAISS index to bytes
    with tempfile.NamedTemporaryFile(suffix=".index", delete=False) as tmp:
        faiss.write_index(index, tmp.name)
        tmp_path = Path(tmp.name)
    
    index_bytes = tmp_path.read_bytes()
    tmp_path.unlink()

    # Serialize chunks
    meta_bytes = pickle.dumps(chunks)

    client.storage.from_(BUCKET).upload(
        path=_index_key(user_id, stem),
        file=index_bytes,
        file_options={"upsert": "true"},
    )
    client.storage.from_(BUCKET).upload(
        path=_meta_key(user_id, stem),
        file=meta_bytes,
        file_options={"upsert": "true"},
    )


def download_index(user_id: str, stem: str) -> tuple[faiss.Index, list[dict]]:
    client = _client()

    try:
        index_bytes = client.storage.from_(BUCKET).download(_index_key(user_id, stem))
        meta_bytes  = client.storage.from_(BUCKET).download(_meta_key(user_id, stem))
    except Exception:
        raise FileNotFoundError(f"Index '{stem}' not found for user '{user_id}'.")

    # Write index bytes to temp file (FAISS needs a file path)
    with tempfile.NamedTemporaryFile(suffix=".index", delete=False) as tmp:
        tmp.write(index_bytes)
        tmp_path = Path(tmp.name)

    index = faiss.read_index(str(tmp_path))
    tmp_path.unlink()

    chunks: list[dict] = pickle.loads(meta_bytes)
    return index, chunks