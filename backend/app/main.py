
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.routers import auth, chat, index, ingest


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ Ensure index storage exists
    try:
        settings.index_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"[Talk2Doc] Index directory unavailable: {exc}")

    # ✅ Initialize DB (creates tables in Supabase/Postgres)
    init_db()

    print(f"[Talk2Doc] Index directory : {settings.configured_index_path}")

    # 🔥 Updated logging
    if settings.DATABASE_URL.startswith("postgres"):
        print(f"[Talk2Doc] Database (Postgres) : connected")
    else:
        print(f"[Talk2Doc] Database (SQLite)  : {settings.db_path.resolve()}")

    print(f"[Talk2Doc] Ollama URL      : {settings.ollama_url}")
    print(f"[Talk2Doc] Default model   : {settings.model_name}")

    yield
    # Shutdown: nothing needed


# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Talk2Doc RAG API",
    description=(
        "FastAPI backend for the Talk2Doc RAG system.\n\n"
        "**Workflow**\n"
        "1. `POST /ingest` — upload a PDF to build a FAISS vector index.\n"
        "2. `POST /chat`   — ask questions; get answers grounded in the PDF.\n"
        "3. `GET /indexes` — inspect or delete existing indexes.\n"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(ingest.router)
app.include_router(chat.router)
app.include_router(index.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Service health check")
async def health():
    index_path = settings.configured_index_path
    return {
        "status": "ok",
        "database": "postgres" if settings.DATABASE_URL.startswith("postgres") else "sqlite",
        "ollama_url": settings.ollama_url,
        "model": settings.model_name,
        "embedding_model": settings.embedding_model,
        "index_dir": str(index_path),
        "index_dir_available": os.access(index_path, os.W_OK),
    }


@app.head("/health", tags=["Health"], include_in_schema=False)
async def health_head():
    return {}


@app.get("/", tags=["Health"], include_in_schema=False)
async def root():
    return {
        "message": "Talk2Doc RAG API is running. Visit /docs for the API reference."
    }
