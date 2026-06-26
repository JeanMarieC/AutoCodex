"""LLM client factory — the single seam between the app and the model provider.

Provider is chosen by `LLM_PROVIDER`:
  • "ollama"  — local, free, unlimited (default). Needs the Ollama app running.
  • "gemini"  — Google Gemini cloud (needs GOOGLE_API_KEY).

`structured_model()` returns a model bound to a Pydantic schema using the method
that works for the active provider, so callers don't branch on provider.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

from app.config import get_settings


def _provider() -> str:
    return get_settings().llm_provider.lower()


def llm_available() -> bool:
    if _provider() == "ollama":
        return True  # assume the local server is up; calls fall back if not
    return bool(get_settings().google_api_key)


@lru_cache
def get_chat_model() -> BaseChatModel:
    """A configured chat model for the active provider. Cached per process."""
    s = get_settings()
    if _provider() == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(model=s.ollama_chat_model, base_url=s.ollama_base_url, temperature=0.2)

    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=s.gemini_model, google_api_key=s.google_api_key, temperature=0.2
    )


def structured_model(schema: type[BaseModel]) -> Any:
    """Bind a Pydantic schema for structured output, per-provider method."""
    model = get_chat_model()
    if _provider() == "ollama":
        # Ollama's native JSON-schema structured output works across local models.
        return model.with_structured_output(schema, method="json_schema")
    return model.with_structured_output(schema)
