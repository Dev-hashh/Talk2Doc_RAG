"""
main.py
FastAPI application entry point.
  - Registers all routers
  - Configures CORS
  - Adds a health-check endpoint
  - Ensures the index storage directory exists on startup
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.routers import auth, chat, index, ingest


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: make sure index directory exists
    settings.index_path.mkdir(parents=True, exist_ok=True)
    init_db()
    print(f"[Talk2Doc] Index directory: {settings.index_path.resolve()}")
    print(f"[Talk2Doc] SQLite DB       : {settings.db_path.resolve()}")
    print(f"[Talk2Doc] Ollama URL     : {settings.ollama_url}")
    print(f"[Talk2Doc] Default model  : {settings.model_name}")
    yield
    # Shutdown: nothing to clean up


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
    return {
        "status": "ok",
        "ollama_url": settings.ollama_url,
        "model": settings.model_name,
        "index_dir": str(settings.index_path.resolve()),
    }


@app.get("/", tags=["Health"], include_in_schema=False)
async def root():
    return {"message": "Talk2Doc RAG API is running. Visit /docs for the API reference."}
