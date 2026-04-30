from __future__ import annotations

import pickle
from pathlib import Path

from app.config import settings
from app.schemas.models import DocumentInfo, IndexInfo


# 🔐 NEW: per-user directory
def _user_index_path(user_id: str) -> Path:
    return settings.index_path / str(user_id)


def _index_file(user_id: str, stem: str) -> Path:
    return _user_index_path(user_id) / f"{stem}.index"


def _metadata_file(user_id: str, stem: str) -> Path:
    return _user_index_path(user_id) / f"{stem}.pkl"


def _load_chunks(user_id: str, stem: str) -> list[dict]:
    with open(_metadata_file(user_id, stem), "rb") as f:
        return pickle.load(f)


def _document_infos(chunks: list[dict]) -> list[DocumentInfo]:
    grouped: dict[str, int] = {}

    for chunk in chunks:
        source = Path(str(chunk.get("source") or "document.pdf")).name
        grouped[source] = grouped.get(source, 0) + 1

    return [
        DocumentInfo(
            id=f"{name}-{count}",
            name=name,
            chunks=count,
            status="indexed",
        )
        for name, count in sorted(grouped.items())
    ]


def index_exists(stem: str, user_id: str) -> bool:
    return _index_file(user_id, stem).exists() and _metadata_file(user_id, stem).exists()


def list_indexes(user_id: str) -> list[IndexInfo]:
    indexes: list[IndexInfo] = []

    user_path = _user_index_path(user_id)
    if not user_path.exists():
        return []

    for idx_file in sorted(user_path.glob("*.index")):
        stem = idx_file.stem
        metadata_file = _metadata_file(user_id, stem)

        if not metadata_file.exists():
            continue

        try:
            chunks = _load_chunks(user_id, stem)
        except Exception:
            chunks = []

        documents = _document_infos(chunks)

        indexes.append(
            IndexInfo(
                name=stem,
                index_file=str(idx_file),
                metadata_file=str(metadata_file),
                size_bytes=idx_file.stat().st_size + metadata_file.stat().st_size,
                chunk_count=len(chunks),
                document_count=len(documents),
                documents=documents,
            )
        )

    return indexes


def delete_index(stem: str, user_id: str) -> None:
    _index_file(user_id, stem).unlink(missing_ok=True)
    _metadata_file(user_id, stem).unlink(missing_ok=True)