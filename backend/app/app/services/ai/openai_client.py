"""
OpenAI-compatible AI client implementation.

This client is intentionally lightweight and focuses on the contract.
You can plug in any provider that supports the OpenAI-compatible
chat completions API surface (including self-hosted models).

Networking and provider-specific error handling are kept minimal here
so that this module can be adapted to your deployment environment.
"""
from __future__ import annotations

import os
import uuid
from typing import Sequence, Mapping, Any

import httpx

from app.services.ai.base import (
    AIClient,
    ChatMessage,
    ChatCompletionChoice,
    ChatCompletionResult,
)


class OpenAICompatibleClient(AIClient):
    """
    Simple OpenAI-compatible client using httpx.

    Environment variables:
    - AI_API_BASE: Base URL for the API (e.g. https://api.openai.com/v1)
    - AI_API_KEY: API key or Bearer token
    - AI_MODEL_DEFAULT: Default model name to use when none is provided
    """

    def __init__(
        self,
        *,
        api_base: str | None = None,
        api_key: str | None = None,
        default_model: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.api_base = api_base or os.getenv("AI_API_BASE", "https://api.openai.com/v1")
        self.api_key = api_key or os.getenv("AI_API_KEY", "")
        self.default_model = default_model or os.getenv("AI_MODEL_DEFAULT", "gpt-4.1-mini")
        self._client = httpx.AsyncClient(timeout=timeout_seconds)

    async def chat_completion(
        self,
        *,
        model: str | None = None,
        messages: Sequence[ChatMessage],
        temperature: float | None = 0.3,
        max_tokens: int | None = 800,
        metadata: Mapping[str, Any] | None = None,
    ) -> ChatCompletionResult:
        if not self.api_key:
            raise RuntimeError("AI_API_KEY is not configured")

        payload: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": [m.__dict__ for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if metadata:
            payload["metadata"] = dict(metadata)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.api_base.rstrip('/')}/chat/completions"

        # NOTE: In production you should add robust error handling,
        # retries, logging, and provider-specific safeguards here.
        response = await self._client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        choices: list[ChatCompletionChoice] = []
        for idx, choice in enumerate(data.get("choices", [])):
            message = choice.get("message", {})
            choices.append(
                ChatCompletionChoice(
                    index=choice.get("index", idx),
                    message=ChatMessage(
                        role=message.get("role", "assistant"),
                        content=message.get("content", ""),
                    ),
                    finish_reason=choice.get("finish_reason"),
                )
            )

        return ChatCompletionResult(
            id=str(data.get("id") or uuid.uuid4()),
            model=data.get("model", model or self.default_model),
            choices=choices,
            usage=data.get("usage"),
        )

