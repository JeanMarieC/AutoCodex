"""Application settings, loaded from environment / .env via pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Car Manual RAG Assistant"
    environment: str = "development"
    debug: bool = True

    # Comma-separated list of origins allowed by CORS (the Vite dev server).
    cors_origins: str = "http://localhost:5173"

    # --- Wired in later phases (kept here so .env has a single home) ---
    # Phase 2.2 — LLM. Provider-swappable: "ollama" (local, free) or "gemini".
    llm_provider: str = "ollama"
    # Gemini (cloud)
    google_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    # Ollama (local) — chat + embeddings, no quota
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "mistral"
    ollama_embed_model: str = "nomic-embed-text"
    # Phase 2.3 — search & fetch
    tavily_api_key: str | None = None
    archive_search_enabled: bool = True   # Archive.org search API (free, no key)
    manuals_dir: str = "./.data/manuals"  # where fetched PDFs are saved
    fetch_timeout_seconds: float = 45.0
    max_manuals: int = 6                  # how many relevant manuals to fetch/index

    # Phase 2.4 — document processing
    chunk_size: int = 1000
    chunk_overlap: int = 150
    # Phase 2.5 — embeddings / vector store (Gemini embeddings, free, same key)
    chroma_dir: str = "./.chroma"
    embedding_model: str = "models/gemini-embedding-001"
    retrieval_k: int = 6  # chunks retrieved per question (across all indexed manuals)
    # Phase 2.6 — persistence (SQLite locally, Postgres in Docker)
    database_url: str = "sqlite:///./carassistant.db"

    # Auth (JWT). Override JWT_SECRET in production.
    jwt_secret: str = "dev-secret-change-me-in-production-please-0123456789"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
