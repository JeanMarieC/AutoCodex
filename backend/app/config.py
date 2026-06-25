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
    # Phase 2.2 — LLM
    anthropic_api_key: str | None = None
    # Phase 2.3 — search
    tavily_api_key: str | None = None
    # Phase 2.5 — embeddings / vector store
    openai_api_key: str | None = None
    chroma_dir: str = "./.chroma"
    # Phase 2.6 — persistence (SQLite locally, Postgres in Docker)
    database_url: str = "sqlite:///./carassistant.db"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
