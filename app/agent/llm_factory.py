from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv()
logger = logging.getLogger(__name__)


class FallbackPortfolioLLM(BaseChatModel):
    """Local fallback model used when external API keys are unavailable or unauthorized in test/sandbox environments."""

    model_name: str = "portfolio-fallback"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        content = (
            "I am the NovaGates Portfolio AI Agent. The candidate is a skilled Backend & AI Engineer "
            "specializing in FastAPI, MongoDB, Redis, and LangGraph with proven expertise in building "
            "stateful multi-agent systems and scalable asynchronous architectures."
        )
        message = AIMessage(content=content)
        return ChatResult(generations=[ChatGeneration(message=message)])

    @property
    def _llm_type(self) -> str:
        return "fallback-portfolio-llm"


def get_agent_llm() -> BaseChatModel:
    """Returns configured Chat LLM using OpenAI, Ollama Cloud, or fallback."""
    openai_key = os.environ.get("OPENAI_API_KEY")
    if (
        openai_key
        and not openai_key.startswith("sk-placeholder")
        and not openai_key.startswith("mock-")
    ):
        logger.info("Initializing Agent LLM with OpenAI gpt-4o-mini.")
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=SecretStr(openai_key),
            temperature=0.2,
        )

    ollama_key = os.environ.get("OLLAMA_API_KEY")
    ollama_base = os.environ.get("OLLAMA_BASE_URL", "https://ollama.com")
    ollama_model = os.environ.get("OLLAMA_MODEL", "gpt-oss:120b")

    if ollama_key:
        logger.info("Initializing Agent LLM with Ollama Cloud (%s).", ollama_model)
        return ChatOpenAI(
            model=ollama_model,
            api_key=SecretStr(ollama_key),
            base_url=f"{ollama_base}/v1"
            if not ollama_base.endswith("/v1")
            else ollama_base,
            temperature=0.2,
        )

    return FallbackPortfolioLLM()
