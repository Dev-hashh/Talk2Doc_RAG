"""
Index metadata helpers.

The ingest and chat services own the heavy RAG work. This module only inspects
the saved FAISS index and pickle metadata files so the API can show what is
available to the frontend.
"""
from __future__ import annotations

import pickle
from pathlib import Path

from app.config import settings
from app.schemas.models import DocumentInfo, IndexInfo


def _load_chunks(stem: str) -> list[dict]:
    with open(settings.metadata_file(stem), "rb") as f:
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


def index_exists(stem: str) -> bool:
    """Return true when both the FAISS index and metadata files exist."""
    return settings.index_file(stem).exists() and settings.metadata_file(stem).exists()


def list_indexes() -> list[IndexInfo]:
    """Return every complete (*.index + *.pkl) pair in the index directory."""
    indexes: list[IndexInfo] = []

    for idx_file in sorted(settings.index_path.glob("*.index")):
        stem = idx_file.stem
        metadata_file = settings.metadata_file(stem)

        if not metadata_file.exists():
            continue

        try:
            chunks = _load_chunks(stem)
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


def delete_index(stem: str) -> None:
    """Delete the index and metadata files for a saved index stem."""
    settings.index_file(stem).unlink(missing_ok=True)
    settings.metadata_file(stem).unlink(missing_ok=True)
