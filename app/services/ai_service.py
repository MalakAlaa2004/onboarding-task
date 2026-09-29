from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class OllamaCloudClient:
    """Production-ready asynchronous client for Ollama Cloud / OpenAI-compatible LLM endpoints.

    No simulations or mock strings: executes real network requests to the configured endpoint.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        default_model: str | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.OLLAMA_API_BASE).rstrip("/")
        self.api_key = api_key or settings.OLLAMA_API_KEY
        self.default_model = default_model or settings.OLLAMA_MODEL

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> dict[str, Any]:
        """Performs a real chat completion HTTP request to Ollama Cloud /v1/chat/completions."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        logger.info(
            "Dispatching LLM chat completion to %s (model: %s)", url, payload["model"]
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                logger.error(
                    "LLM Provider HTTP Error (%s): %s",
                    e.response.status_code,
                    e.response.text,
                )
                raise ExternalServiceError(
                    "OllamaCloud",
                    f"LLM API returned status {e.response.status_code}: {e.response.text[:200]}",
                ) from e
            except Exception as e:
                logger.error("LLM Provider network failure: %s", e)
                raise ExternalServiceError("OllamaCloud", str(e)) from e

        return data

    async def generate_portfolio_bio(
        self, skills: list[str], projects: list[str]
    ) -> str:
        """Generates a tailored developer profile pitch using real LLM inferences."""
        skills_csv = ", ".join(skills)
        projects_csv = ", ".join(projects)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an executive technical recruiter and career coach at NovaGates. "
                    "Write a punchy, senior-caliber 3-paragraph developer summary highlighting practical impact."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Candidate Core Skills: {skills_csv}\n"
                    f"Featured Projects: {projects_csv}\n"
                    "Generate a concise, professional summary highlighting backend and AI capabilities."
                ),
            },
        ]

        result = await self.chat_completion(messages=messages, temperature=0.5)
        choices = result.get("choices", [])
        if not choices:
            raise ExternalServiceError(
                "OllamaCloud", "Received empty completion choices from provider."
            )

        return choices[0]["message"]["content"]
