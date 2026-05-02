import os
import tempfile
import pickle
from pathlib import Path
import faiss
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

    with tempfile.NamedTemporaryFile(suffix=".index", delete=False) as tmp:
        faiss.write_index(index, tmp.name)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        index_bytes = f.read()
    os.remove(tmp_path)

    meta_bytes = pickle.dumps(chunks)

    print("Uploading index...")

    try:
        client.storage.from_(BUCKET).upload(
            path=_index_key(user_id, stem),
            file=index_bytes,
            file_options={
                "content-type": "application/octet-stream",
                "upsert": "true",
            },
        )
    except Exception as exc:
        print(f"Error uploading index: {exc}")
        raise

    try:
        client.storage.from_(BUCKET).upload(
            path=_meta_key(user_id, stem),
            file=meta_bytes,
            file_options={
                "content-type": "application/octet-stream",
                "upsert": "true",
            },
        )
    except Exception as exc:
        print(f"Error uploading metadata: {exc}")
        raise

    print("Upload successful.")


def download_index(user_id: str, stem: str) -> tuple[faiss.Index, list[dict]]:
    client = _client()

    try:
        index_bytes = client.storage.from_(BUCKET).download(_index_key(user_id, stem))
        meta_bytes = client.storage.from_(BUCKET).download(_meta_key(user_id, stem))
    except Exception:
        raise FileNotFoundError(f"Index '{stem}' not found for user '{user_id}'.")

    with tempfile.NamedTemporaryFile(suffix=".index", delete=False) as tmp:
        tmp.write(index_bytes)
        tmp_path = Path(tmp.name)

    index = faiss.read_index(str(tmp_path))
    tmp_path.unlink()

    chunks: list[dict] = pickle.loads(meta_bytes)
    return index, chunks


def list_index_stems(user_id: str) -> list[str]:
    client = _client()
    try:
        files = client.storage.from_(BUCKET).list(user_id)
        stems = set()
        for f in files:
            name = f.get("name", "")
            if name.endswith(".index"):
                stems.add(name[:-6])
        return sorted(stems)
    except Exception:
        return []


def index_exists_in_supabase(user_id: str, stem: str) -> bool:
    return stem in list_index_stems(user_id)


def delete_index_files(user_id: str, stem: str) -> None:
    client = _client()
    client.storage.from_(BUCKET).remove([
        _index_key(user_id, stem),
        _meta_key(user_id, stem),
    ])