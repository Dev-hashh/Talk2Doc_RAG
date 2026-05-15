"""
Central configuration loaded from environment variables / .env file.
All tuneable values live here so routers and services never hard-code anything.
"""

# env_path = BASE_DIR / ".env"


from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # goes to talk2doc/

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///talk2doc.db"
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Groq
    USE_GROQ: bool = False
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
        

    # ── Ollama ────────────────────────────────────────────────────────────────
    ollama_url: str = "http://localhost:11434/api/generate"
    model_name: str = "deepseek-v3.1:671b-cloud"

    # ── Embeddings ────────────────────────────────────────────────────────────
    embedding_model: str = "hashing"   # use BAAI/bge-small-en on hosts with enough RAM

    # ── Chunking defaults ─────────────────────────────────────────────────────
    default_chunk_size: int = 500
    default_overlap: int = 50

    # ── Retrieval ─────────────────────────────────────────────────────────────
    default_top_k: int = 5

    # ── Storage ───────────────────────────────────────────────────────────────
    #Supabase Storage
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    
    # Directory where .index and .pkl files are stored.
    # Resolved relative to the project root (two levels above this file).
    index_dir: str = "indexes"
    database_path: str = "talk2doc.db"
    auth_secret: str = ""
    auth_token_minutes: int = 60 * 24 * 7
    
    

    @property
    def index_path(self) -> Path:
        p = Path(self.index_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def configured_index_path(self) -> Path:
        return Path(self.index_dir)

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
    #cors_origins: list[str] = ["*"]
    cors_origins: list[str] = ["https://talk2doc.onrender.com"]


settings = Settings()
