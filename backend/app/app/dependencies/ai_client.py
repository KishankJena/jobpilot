"""FastAPI dependency for injecting an AI client instance."""
from functools import lru_cache

from app.services.ai.base import AIClient
from app.services.ai.openai_client import OpenAICompatibleClient


@lru_cache
def _ai_client() -> AIClient:
    """
    Lazily construct the default AI client.

    In production you can replace this with a provider-specific factory
    (Azure, Vertex, local model, etc.) while keeping the same interface.
    """
    return OpenAICompatibleClient()


async def get_ai_client() -> AIClient:
    """
    Async-compatible dependency wrapper returning the shared AI client.

    The client itself is safe to reuse due to httpx's internal connection
    pooling; we do not create a new HTTP client per request.
    """
    return _ai_client()

