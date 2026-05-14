from pydantic import BaseModel, Field
from typing import Optional, List


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class UserPublic(BaseModel):
    id: int
    name: str
    email: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


# ── Ingest ──────────────────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    """Optional overrides sent as form/query params alongside the PDF file."""
    index_name: Optional[str] = Field(
        default=None,
        description="Custom name for the FAISS index (without extension). "
                    "Defaults to the PDF file stem.",
    )
    chunk_size: int = Field(default=500, ge=100, le=2000)
    overlap: int = Field(default=50, ge=0, le=500)


class IngestResponse(BaseModel):
    message: str
    index_name: str
    chunks_indexed: int
    pdf_filename: str


# ── Chat ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")
    index_name: Optional[str] = Field(
        default=None,
        description="Which FAISS index to query. Omit to use the default index.",
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing saved conversation to append to. Omit to create one.",
    )
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    model: Optional[str] = Field(
        default=None,
        description="Override the default Ollama model for this request.",
    )


class SourceInfo(BaseModel):
    filename: str
    page: Optional[int] = None
    chunk_id: Optional[int] = None
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    index_name: str
    question: str
    conversation_id: str
    sources: List[SourceInfo] = Field(
        default_factory=list,
        description="Retrieved chunks used to form the answer.",
    )


class SavedChatMessage(BaseModel):
    id: str
    role: str
    author: str
    time: str
    text: str
    citations: List[str] = Field(default_factory=list)


class SavedChatConversation(BaseModel):
    id: str
    index_id: str
    index_name: str
    title: str
    created_at: str
    updated_at: str
    messages: List[SavedChatMessage] = Field(default_factory=list)


class ChatHistoryResponse(BaseModel):
    conversations: List[SavedChatConversation] = Field(default_factory=list)


# ── Indexes ──────────────────────────────────────────────────────────────────

class DocumentInfo(BaseModel):
    id: str
    name: str
    chunks: int
    status: str = "indexed"


class IndexInfo(BaseModel):
    name: str
    index_file: str
    metadata_file: str
    size_bytes: int
    chunk_count: int = 0
    document_count: int = 0
    documents: List[DocumentInfo] = Field(default_factory=list)


class IndexListResponse(BaseModel):
    indexes: List[IndexInfo]
    total: int
