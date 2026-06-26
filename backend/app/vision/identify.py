"""Dashboard warning-light identification via a local Ollama vision model.

Turns a photo of an instrument cluster into a short text description of the
illuminated warning light(s). That description then becomes a question to the
RAG layer, which answers from the car's manual — i.e. multimodal RAG.
"""

from __future__ import annotations

from ollama import AsyncClient

from app.config import get_settings

_PROMPT = (
    "This is a photo of a car's dashboard / instrument cluster. Identify the "
    "warning or indicator light(s) that are ON. For each, give its common name, "
    "colour, and the symbol it shows (e.g. 'red coolant-temperature light — "
    "thermometer in liquid'). If no warning light is clearly illuminated, say "
    "'No warning light is clearly visible.' Be concise — one or two sentences, "
    "no preamble."
)


async def identify_dashboard(image: bytes) -> str:
    """Return a short description of the dashboard warning light(s) in the image."""
    settings = get_settings()
    client = AsyncClient(host=settings.ollama_base_url)
    resp = await client.chat(
        model=settings.vision_model,
        messages=[{"role": "user", "content": _PROMPT, "images": [image]}],
        options={"temperature": 0.1},
    )
    return (resp.message.content or "").strip()
