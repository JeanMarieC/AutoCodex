"""Vector store — ChromaDB with one collection per car.

Embeddings are Google Gemini's free `text-embedding-004` (same key as the LLM).
Per-car collections keep retrieval naturally scoped to the selected vehicle and
make re-ingestion a clean wipe-and-replace.

`index_chunks` is shared by the ingest node and (next) the manual-upload
endpoint; `retrieve` is what closes the RAG loop in chat.
"""

from __future__ import annotations

from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from app.agent.state import Car
from app.config import get_settings
from app.llm.rag import ContextChunk
from app.rag.models import Chunk


def embeddings_available() -> bool:
    if get_settings().llm_provider.lower() == "ollama":
        return True  # local; calls fall back gracefully if Ollama isn't running
    return bool(get_settings().google_api_key)


@lru_cache
def _embeddings() -> Embeddings:
    s = get_settings()
    if s.llm_provider.lower() == "ollama":
        from langchain_ollama import OllamaEmbeddings

        return OllamaEmbeddings(model=s.ollama_embed_model, base_url=s.ollama_base_url)

    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    return GoogleGenerativeAIEmbeddings(model=s.embedding_model, google_api_key=s.google_api_key)


@lru_cache
def _client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(
        path=get_settings().chroma_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def _collection_name(car: Car) -> str:
    return f"car-{car.id}"


def get_vectorstore(car: Car) -> Chroma:
    return Chroma(
        client=_client(),
        collection_name=_collection_name(car),
        embedding_function=_embeddings(),
    )


def reset_car(car: Car) -> None:
    """Drop a car's collection so re-ingestion doesn't duplicate chunks."""
    try:
        _client().delete_collection(_collection_name(car))
    except Exception:
        pass  # collection may not exist yet


def index_chunks(car: Car, chunks: list[Chunk]) -> int:
    """Embed and store a car's chunks (replacing any prior index). Returns count."""
    if not chunks:
        return 0
    reset_car(car)
    return add_to_index(car, chunks)


def add_to_index(car: Car, chunks: list[Chunk]) -> int:
    """Add chunks to a car's collection without wiping it (used by upload)."""
    if not chunks:
        return 0
    vs = get_vectorstore(car)
    vs.add_texts(
        texts=[c.text for c in chunks],
        metadatas=[c.metadata() for c in chunks],
    )
    return len(chunks)


def retrieve(car: Car, query: str, k: int | None = None) -> list[ContextChunk]:
    """Top-k manual excerpts for a question, scoped to the car's collection."""
    k = k or get_settings().retrieval_k
    vs = get_vectorstore(car)
    docs = vs.similarity_search(query, k=k)
    out: list[ContextChunk] = []
    for d in docs:
        md = d.metadata
        ref = md.get("section") or f"p.{md.get('page', '?')}"
        out.append(
            ContextChunk(
                manual=str(md.get("manual_name", "Manual")),
                ref=str(ref),
                text=d.page_content,
            )
        )
    return out
