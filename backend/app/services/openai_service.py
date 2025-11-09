import logging
from typing import Optional

from openai import AsyncOpenAI

from ..core.config import settings


# Overview:
# - Purpose: Provide a minimal async wrapper around OpenAI chat completions.
# Key Components:
# - OpenAIService: exposes generate_text for downstream agents with shared configuration.


logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = settings.openai_model

    async def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as error:
            logger.error(f"OpenAI generate_text failed: {error}")
            raise

