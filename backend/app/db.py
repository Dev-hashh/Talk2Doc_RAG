from __future__ import annotations

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func, Index
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