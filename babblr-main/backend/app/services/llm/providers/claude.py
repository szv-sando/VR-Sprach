"""
LOCAL OLLAMA PROVIDER (Replaces Anthropic Claude LLM provider)

This provider connects to a local Ollama instance (Llama 3) and supports
both synchronous and streaming responses.
"""

import logging
from typing import AsyncIterator

import ollama  # SUBSTITUÍDO: Importamos o motor local no lugar da API online

from app.services.llm.base import LLMResponse, StreamChunk
from app.services.llm.exceptions import (
    LLMAuthenticationError,
    LLMError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class ClaudeProvider:
    """Local Ollama provider masquerading as Claude.
    Connects to local Llama 3 for high-quality language model inference without internet.
    """

    def __init__(
        self,
        api_key: str = "",
        model: str = "llama3",  # Model changed to local Llama 3
    ):
        """Initialize the local provider."""
        # Não precisamos checar a API key porque o Ollama roda na própria máquina
        self._model = model

    @property
    def name(self) -> str:
        """Provider identifier."""
        return "ollama-local"

    @property
    def model(self) -> str:
        """Current model name."""
        return self._model

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a complete response using local Ollama."""
        try:
            # Inject system prompt at the beginning of the messages list
            formatted_messages = [{"role": "system", "content": system_prompt}]
            
            # The original structure might be missing types, so we handle standard dicts
            for msg in messages:
                formatted_messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

            response = ollama.chat(
                model=self._model,
                messages=formatted_messages
            )

            content = response['message']['content']

            return LLMResponse(
                content=content,
                model=self._model,
                tokens_used=100,  # Mock value as local Ollama doesn't track tokens by default
                finish_reason="stop",
            )

        except Exception as e:
            logger.error(f"Unexpected local Ollama error: {e}")
            raise LLMError(f"Local LLM error: {e}")

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[StreamChunk]:
        """Generate a streaming response using local Ollama."""
        try:
            formatted_messages = [{"role": "system", "content": system_prompt}]
            for msg in messages:
                formatted_messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

            stream = ollama.chat(
                model=self._model,
                messages=formatted_messages,
                stream=True  # Enables word-by-word streaming
            )

            for chunk in stream:
                if chunk['message']['content']:
                    yield StreamChunk(content=chunk['message']['content'], done=False)

            yield StreamChunk(content="", done=True, tokens_used=100)

        except Exception as e:
            logger.error(f"Unexpected streaming local error: {e}")
            raise LLMError(f"Unexpected error: {e}")

    async def health_check(self) -> bool:
        """Check if local Ollama service is running.
        Makes a minimal API call to verify connectivity.
        """
        try:
            # Simple check to see if the engine is awake
            ollama.chat(
                model=self._model,
                messages=[{"role": "user", "content": "hi"}]
            )
            return True
        except Exception as e:
            logger.warning(f"Local Ollama health check failed: {e}")
            return False