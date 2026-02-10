"""
AI service abstraction for JobPath.

This package defines a provider-agnostic interface for AI capabilities
used across the platform (resume analysis, JD matching, interview prep,
rejection insights, and wellbeing coaching).

The concrete provider implementation (e.g. OpenAI-compatible, Azure,
local LLM) is selected via configuration and plugged into services via
dependency injection.
"""

