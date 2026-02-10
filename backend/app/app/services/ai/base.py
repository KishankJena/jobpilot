"""
Provider-agnostic AI client abstraction.

Key design goals:
- Single, well-documented interface used by domain services.
- OpenAI-compatible request/response shapes where practical.
- Easy to swap providers (OpenAI, Azure, local) without touching
  business logic.
- No deceptive behavior: AI suggestions must be explainable,
  reversible, and never fabricate skills or experience.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Literal, Sequence, Mapping, Any


Role = Literal["system", "user", "assistant"]


@dataclass
class ChatMessage:
    """Simple chat message used across providers."""

    role: Role
    content: str


@dataclass
class ChatCompletionChoice:
    """Single choice from a chat completion call."""

    index: int
    message: ChatMessage
    finish_reason: str | None = None


@dataclass
class ChatCompletionResult:
    """Normalized result shape loosely based on OpenAI's API."""

    id: str
    model: str
    choices: list[ChatCompletionChoice]
    usage: Mapping[str, Any] | None = None


class AIClient(Protocol):
    """
    Abstract AI client interface.

    Implementations may wrap HTTP APIs (e.g. OpenAI-compatible endpoints)
    or in-process models. All domain services should depend on this
    protocol rather than a concrete provider.
    """

    async def chat_completion(
        self,
        *,
        model: str,
        messages: Sequence[ChatMessage],
        temperature: float | None = 0.3,
        max_tokens: int | None = 800,
        metadata: Mapping[str, Any] | None = None,
    ) -> ChatCompletionResult:
        """
        Execute a chat completion request.

        Implementations MUST:
        - Avoid fabricating skills, dates, or employers.
        - Prefer constructive, empathetic tone for user-facing guidance.
        - Return content that is explainable and reversible by the user.
        """

