"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agent, chat, health
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers. More mounted per Phase 2 sub-phase: cars, persistence.
app.include_router(health.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/api")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "ok"}
