"""
Central configuration loaded from environment variables / .env file.
All tuneable values live here so routers and services never hard-code anything.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Ollama ────────────────────────────────────────────────────────────────
    ollama_url: str = "http://localhost:11434/api/generate"
    model_name: str = "deepseek-v3.1:671b-cloud"

    # ── Embeddings ────────────────────────────────────────────────────────────
    embedding_model: str = "BAAI/bge-small-en"   # matches docchat Embedder default

    # ── Chunking defaults ─────────────────────────────────────────────────────
    default_chunk_size: int = 500
    default_overlap: int = 50

    # ── Retrieval ─────────────────────────────────────────────────────────────
    default_top_k: int = 5

    # ── Storage ───────────────────────────────────────────────────────────────
    # Directory where .index and .pkl files are stored.
    # Resolved relative to the project root (two levels above this file).
    index_dir: str = "indexes"
    database_path: str = "talk2doc.db"
    auth_secret: str = "change-me-in-production"
    auth_token_minutes: int = 60 * 24 * 7

    @property
    def index_path(self) -> Path:
        p = Path(self.index_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def db_path(self) -> Path:
        return Path(self.database_path)

    # ── Default index names ───────────────────────────────────────────────────
    default_index_stem: str = "faiss"   # → faiss.index / faiss.pkl

    def index_file(self, stem: str) -> Path:
        return self.index_path / f"{stem}.index"

    def metadata_file(self, stem: str) -> Path:
        return self.index_path / f"{stem}.pkl"

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: list[str] = ["*"]


settings = Settings()
