# Manual.ai — Agentic Car-Manual RAG Assistant

Add a car to your garage and an autonomous agent finds, fetches and indexes its
official manuals (owner's + workshop), then becomes a RAG chatbot that answers
maintenance and repair questions for that exact vehicle — with citations back to
the source pages.

## Architecture

```
┌──────────────┐     REST + SSE      ┌─────────────────────────────────────┐
│  frontend    │ ──────────────────▶ │  backend (FastAPI)                  │
│  React + TS  │ ◀────────────────── │                                     │
│  Tailwind    │   live agent steps  │  LangGraph agent pipeline:          │
└──────────────┘                     │   Parse → Search → Validate →       │
                                     │   Fetch → Ingest → Chat             │
                                     │                                     │
                                     │  Claude (reasoning + RAG answers)   │
                                     │  Chroma (vectors)  Postgres (state) │
                                     └─────────────────────────────────────┘
```

The 5 agent steps stream to the UI over SSE and render as a live progress
pipeline. The UI was built from a Claude Design handoff and lives in `frontend/`.

## Repo layout

```
.
├── frontend/             Vite + React + TS + Tailwind v4
├── backend/              Python 3.11 + FastAPI (managed by uv)
├── docker-compose.yml    api + web + Postgres + Chroma (Phase 3)
├── .env.example          root env (docker-compose)
└── .gitignore
```

## Tech stack

| Layer        | Choice                                                    |
| ------------ | --------------------------------------------------------- |
| Frontend     | React 19, TypeScript, Vite, Tailwind v4                   |
| Backend      | FastAPI, Pydantic, Uvicorn (Python 3.11+, `uv`)           |
| Agent        | LangGraph state graph with retry / graceful-failure paths |
| LLM          | Anthropic Claude (reasoning + RAG answers, tool calling)  |
| Search/fetch | Tavily scoped to manualslib.com / archive.org             |
| Docs         | PyMuPDF / pdfplumber + LangChain chunking                 |
| Vectors      | ChromaDB (per-car collections)                            |
| Persistence  | PostgreSQL + SQLAlchemy (SQLite for local dev)            |
| Streaming    | SSE for live agent progress                               |

## Getting started

Prerequisites: Node 20+, Python 3.11+, [`uv`](https://docs.astral.sh/uv/),
Docker (optional, for Phase 3).

### Backend

```bash
cd backend
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload      # http://localhost:8000  (docs: /docs)
```

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev                                # http://localhost:5173
```

The Vite dev server proxies `/api` to the backend on port 8000.

## Build phases

- **Phase 0 — Scaffolding** ✅ monorepo, frontend + backend skeletons, env, compose
- **Phase 1 — Frontend** recreate the design, API client layer, mocked endpoints
- **Phase 2 — Backend** agent graph → LLM → search/fetch → docs → vectors → DB → eval
- **Phase 3 — DevOps** Dockerfiles, full compose, GitHub Actions CI
