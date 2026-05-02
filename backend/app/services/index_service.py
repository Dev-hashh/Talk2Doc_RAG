from __future__ import annotations

from pathlib import Path

from app.schemas.models import DocumentInfo, IndexInfo
from docchat.storage import (
    download_index,
    delete_index_files,
    list_index_stems,
    index_exists_in_supabase,
)


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
    return index_exists_in_supabase(user_id, stem)


def list_indexes(user_id: str) -> list[IndexInfo]:
    stems = list_index_stems(user_id)
    indexes: list[IndexInfo] = []

    for stem in stems:
        try:
            _, chunks = download_index(user_id, stem)
        except Exception:
            chunks = []

        documents = _document_infos(chunks)

        indexes.append(
            IndexInfo(
                name=stem,
                index_file=f"{user_id}/{stem}.index",
                metadata_file=f"{user_id}/{stem}.pkl",
                size_bytes=0,
                chunk_count=len(chunks),
                document_count=len(documents),
                documents=documents,
            )
        )

    return indexes


def delete_index(stem: str, user_id: str) -> None:
    delete_index_files(user_id, stem)