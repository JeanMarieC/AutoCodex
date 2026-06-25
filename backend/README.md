# Backend — Car Manual RAG Assistant

FastAPI service hosting the LangGraph agent pipeline and RAG chat API.

## Stack

- Python 3.11+, FastAPI, Pydantic, Uvicorn
- Managed with [`uv`](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`)

## Develop

```bash
cd backend
uv sync                 # create the venv and install deps from the lockfile
uv run uvicorn app.main:app --reload   # http://localhost:8000
```

- API root: `GET /api`
- Health: `GET /api/health`
- Interactive docs: `http://localhost:8000/docs`

## Test & lint

```bash
uv run pytest
uv run ruff check .
uv run mypy app
```

## Layout

```
app/
  main.py        FastAPI app + router mounting
  config.py      pydantic-settings
  api/           routes/ + schemas/  (REST + SSE endpoints)
  agent/         LangGraph state graph, nodes, events   (Phase 2.1)
  tools/         search / fetch / pdf tools             (Phase 2.3–2.4)
  rag/           chunking, embeddings, vector store     (Phase 2.4–2.5)
  db/            SQLAlchemy models + session            (Phase 2.6)
  services/      glue between API and agent
  core/          logging, exceptions
tests/           pytest suite
eval/            evaluation harness + labeled Q&A set   (Phase 2.7)
```
