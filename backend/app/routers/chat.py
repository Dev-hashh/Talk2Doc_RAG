"""
routers/chat.py
POST /chat  — ask a question against an ingested FAISS index.
"""
from fastapi import APIRouter, HTTPException, status

from pathlib import Path
from sqlite3 import Row

from fastapi import Depends

from app.deps import get_current_user
from app.schemas.models import ChatRequest, ChatResponse, SourceInfo
from app.services.chat_service import answer_question

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Ask a question about an ingested PDF",
    description=(
        "Embeds the question, retrieves the top-k relevant chunks from the "
        "specified FAISS index, and streams them to Ollama for answer generation."
    ),
)
async def chat(
    body: ChatRequest,
    user: Row = Depends(get_current_user),
) -> ChatResponse:
    try:
        answer, stem, sources = answer_question(
            question=body.question,
            index_name=body.index_name,
            top_k=body.top_k,
            model=body.model,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {exc}",
        )

    return ChatResponse(
        answer=answer,
        index_name=stem,
        question=body.question,
        sources=[
            SourceInfo(
                filename=Path(str(source.get("source", "document.pdf"))).name,
                page=source.get("page"),
                chunk_id=source.get("chunk_id"),
                snippet=str(source.get("text", ""))[:500],
            )
            for source in sources
        ],
    )
