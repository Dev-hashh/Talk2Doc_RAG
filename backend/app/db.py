from __future__ import annotations

from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, Text, DateTime, func, Index
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from app.config import settings
#from backend.app.config import settings


# 🔗 Use DATABASE_URL (Postgres or SQLite fallback)
DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing!")

# 🧠 Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},
)


# 🧱 Session
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# 🧬 Base model
Base = declarative_base()


# 👤 User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


# Optional explicit index (already covered by index=True)
Index("idx_users_email", User.email)


class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    index_name = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(
        String,
        ForeignKey("chat_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String, nullable=False)
    author = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


Index("idx_chat_conversations_user_updated", ChatConversation.user_id, ChatConversation.updated_at)
Index("idx_chat_messages_conversation_created", ChatMessage.conversation_id, ChatMessage.created_at)


# 🔌 Dependency (FastAPI)
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🚀 Init DB (create tables)
def init_db():
    
    Base.metadata.create_all(bind=engine)
    print("[DB] Initialized database and created tables.")
    print(f"[DB] Using database: {DATABASE_URL}")
