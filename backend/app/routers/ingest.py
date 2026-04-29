"""
routers/ingest.py
POST /ingest  — upload a PDF, run the ingest pipeline, save a FAISS index.
"""
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi import Depends
from sqlite3 import Row
from typing import Optional

from app.deps import get_current_user
from app.schemas.models import IngestResponse
from app.services.ingest_service import ingest_pdf

router = APIRouter(prefix="/ingest", tags=["Ingest"])

ALLOWED_CONTENT_TYPES = {"application/pdf", "application/octet-stream"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post(
    "",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and index a PDF",
    description=(
        "Accepts a PDF file via multipart form upload. "
        "Extracts text, chunks it, embeds the chunks, and stores the "
        "resulting FAISS index on disk under `indexes/<index_name>.index`."
    ),
)
async def ingest_document(
    file: UploadFile = File(..., description="PDF file to ingest"),
    index_name: Optional[str] = Form(
        default=None,
        description="Optional custom name for the index (no extension). "
                    "Defaults to the PDF filename stem.",
    ),
    chunk_size: int = Form(default=500, ge=100, le=2000),
    overlap: int = Form(default=50, ge=0, le=500),
    user: Row = Depends(get_current_user),
) -> IngestResponse:
    # ── Validate file type ────────────────────────────────────────────────────
    if file.content_type not in ALLOWED_CONTENT_TYPES and not (
        file.filename or ""
    ).lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are supported.",
        )

    # ── Read bytes ────────────────────────────────────────────────────────────
    pdf_bytes = await file.read()
    if len(pdf_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    if len(pdf_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE // (1024*1024)} MB.",
        )

    # ── Run ingest pipeline ───────────────────────────────────────────────────
    try:
        stem, num_chunks = ingest_pdf(
            pdf_bytes=pdf_bytes,
            pdf_filename=file.filename or "document.pdf",
            index_name=index_name,
            chunk_size=chunk_size,
            overlap=overlap,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingest failed: {exc}",
        )

    return IngestResponse(
        message="PDF ingested and indexed successfully.",
        index_name=stem,
        chunks_indexed=num_chunks,
        pdf_filename=file.filename or "document.pdf",
    )
