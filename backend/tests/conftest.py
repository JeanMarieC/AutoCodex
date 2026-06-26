"""Test-session setup.

Neutralizes API keys BEFORE the app imports/reads settings, so tests run fully
offline (stub search, no LLM) regardless of what's in the developer's .env.
Tests that exercise the keyed paths monkeypatch availability explicitly.
"""

import os
import tempfile
from pathlib import Path

# Must happen at import time, before app.config.get_settings() is first called.
# Pin gemini + empty key so llm/embeddings report unavailable → tests run fully
# offline (no Ollama/Gemini calls) unless a test explicitly monkeypatches.
os.environ["LLM_PROVIDER"] = "gemini"
os.environ["GOOGLE_API_KEY"] = ""
os.environ["TAVILY_API_KEY"] = ""
os.environ["ARCHIVE_SEARCH_ENABLED"] = "false"  # no network during tests
# Keep generated sample PDFs out of the project tree.
os.environ["MANUALS_DIR"] = tempfile.mkdtemp(prefix="carassistant-test-manuals-")
# Isolated throwaway SQLite database for the test session.
_db = Path(tempfile.mkdtemp(prefix="carassistant-test-db-")) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_db.as_posix()}"

import pytest  # noqa: E402

from app.agent import pacing  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _init_database():
    from app.db.session import init_db

    init_db()


@pytest.fixture(autouse=True)
def _no_delay(monkeypatch):
    monkeypatch.setattr(pacing, "DELAY", 0)
