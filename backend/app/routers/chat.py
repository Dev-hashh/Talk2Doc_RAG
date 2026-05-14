"""
routers/chat.py
POST /chat - ask a question against an ingested FAISS index.
GET /chat/conversations - list saved conversations for the current user.
"""
import json
from datetime import datetime
from pathlib import Path
from sqlite3 import Row
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import ChatConversation, ChatMessage, get_db
from app.deps import get_current_user
from app.schemas.models import (
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    SavedChatConversation,
    SavedChatMessage,
    SourceInfo,
)
from app.services.chat_service import answer_question

router = APIRouter(prefix="/chat", tags=["Chat"])


def _title_from_question(question: str) -> str:
    compact = " ".join(question.split())
    return f"{compact[:51]}..." if len(compact) > 54 else compact


def _format_time(value: datetime | None) -> str:
    return value.isoformat() if value else ""


def _format_sources(sources: list[dict]) -> list[str]:
    citations: list[str] = []

    for source in sources:
        filename = Path(str(source.get("source", "document.pdf"))).name
        page = f" p.{source.get('page')}" if source.get("page") else ""
        chunk = f" #{source.get('chunk_id')}" if source.get("chunk_id") is not None else ""
        citations.append(f"{filename}{page}{chunk}")

    return citations


def _message_to_schema(message: ChatMessage) -> SavedChatMessage:
    try:
        citations = json.loads(message.citations_json or "[]")
    except json.JSONDecodeError:
        citations = []

    return SavedChatMessage(
        id=message.id,
        role=message.role,
        author=message.author,
        time="Saved",
        text=message.text,
        citations=citations if isinstance(citations, list) else [],
    )


def _conversation_to_schema(
    conversation: ChatConversation,
    messages: list[ChatMessage],
) -> SavedChatConversation:
    return SavedChatConversation(
        id=conversation.id,
        index_id=conversation.index_name,
        index_name=conversation.index_name,
        title=conversation.title,
        created_at=_format_time(conversation.created_at),
        updated_at=_format_time(conversation.updated_at),
        messages=[_message_to_schema(message) for message in messages],
    )


@router.get("/conversations", response_model=ChatHistoryResponse)
def list_conversations(
    user: Row = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatHistoryResponse:
    conversations = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user.id)
        .order_by(ChatConversation.updated_at.desc())
        .all()
    )
    conversation_ids = [conversation.id for conversation in conversations]
    messages: list[ChatMessage] = []

    if conversation_ids:
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.conversation_id.in_(conversation_ids))
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    messages_by_conversation: dict[str, list[ChatMessage]] = {}
    for message in messages:
        messages_by_conversation.setdefault(message.conversation_id, []).append(message)

    return ChatHistoryResponse(
        conversations=[
            _conversation_to_schema(
                conversation,
                messages_by_conversation.get(conversation.id, []),
            )
            for conversation in conversations
        ],
    )


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
    db: Session = Depends(get_db),
) -> ChatResponse:
    try:
        answer, stem, sources = answer_question(
            question=body.question,
            index_name=body.index_name,
            top_k=body.top_k,
            model=body.model,
            user_id=user.id,
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

    conversation = None
    if body.conversation_id:
        conversation = (
            db.query(ChatConversation)
            .filter(
                ChatConversation.id == body.conversation_id,
                ChatConversation.user_id == user.id,
            )
            .first()
        )

    if conversation is None:
        conversation = ChatConversation(
            id=f"chat-{uuid4().hex}",
            user_id=user.id,
            index_name=stem,
            title=_title_from_question(body.question),
        )
        db.add(conversation)

    citations = _format_sources(sources)
    now = datetime.utcnow()
    conversation.index_name = stem
    conversation.updated_at = now

    db.add_all([
        ChatMessage(
            id=f"msg-{uuid4().hex}",
            conversation_id=conversation.id,
            role="user",
            author="You",
            text=body.question,
            citations_json="[]",
            created_at=now,
        ),
        ChatMessage(
            id=f"msg-{uuid4().hex}",
            conversation_id=conversation.id,
            role="assistant",
            author="Assistant",
            text=answer,
            citations_json=json.dumps(citations),
            created_at=now,
        ),
    ])
    db.commit()

    return ChatResponse(
        answer=answer,
        index_name=stem,
        question=body.question,
        conversation_id=conversation.id,
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
