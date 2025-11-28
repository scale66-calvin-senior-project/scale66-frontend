"""
Anthropic Service - Anthropic API integration.

Provides:
- Text generation using Claude models
- Vision analysis using Claude Vision

Used by agents for LLM calls and text generation.
"""

import logging
import base64
import httpx
from typing import Optional, List
from anthropic import Anthropic, AsyncAnthropic
from app.core.config import settings


logger = logging.getLogger(__name__)


class AnthropicServiceError(Exception):
    """Base exception for Anthropic service errors."""
    pass


class AnthropicService:
    """
    Anthropic service for text generation and vision analysis.
    Default Model: claude-sonnet-4-5 (configured in settings)
    """

    _instance: Optional['AnthropicService'] = None
    _client: Optional[AsyncAnthropic] = None

    def __new__(cls):
        """Singleton instance creation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialization of the Anthropic service."""
        if self._client is None:
            try:
                self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                raise AnthropicServiceError(f"Failed to initialize Anthropic client: {e}")

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate text using Anthropic's Claude Sonnet 4.5 model.

        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text as a string
        """
        try:
            logger.debug(f"Generating text with model: {settings.anthropic_model}")

            response = await self._client.messages.create(
                model=settings.anthropic_model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()
            logger.debug(f"Generated text: {response_text[:200]}...")

            return response_text

        except Exception as e:
            logger.error(f"Failed to generate text: {e}")
            raise AnthropicServiceError(f"Failed to generate text: {e}")

    async def analyze_image(
        self,
        image_url: str,
        prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        """
        Analyze image using Anthropic's Claude Vision model.

        Args:
            image_url: The URL of the image (HTTP URL, data URL, or file path)
            prompt: The prompt to send to the LLM
            max_tokens: The maximum number of tokens to generate

        Returns:
            Analysis result as a string
        """
        try:
            logger.debug(f"Analyzing image (truncated): {image_url[:100]}...")
            
            # Handle different image URL formats
            if image_url.startswith("data:image/"):
                # Data URL format: data:image/png;base64,iVBORw0KG...
                parts = image_url.split(",", 1)
                if len(parts) == 2:
                    image_data = parts[1]  # Already base64
                    # Detect actual media type from base64 data magic bytes
                    # JPEG starts with /9j/, PNG starts with iVBORw0KG
                    if image_data.startswith("/9j/"):
                        media_type = "image/jpeg"
                    elif image_data.startswith("iVBORw0KG"):
                        media_type = "image/png"
                    else:
                        # Default to JPEG as that's what Gemini produces
                        media_type = "image/jpeg"
                else:
                    raise AnthropicServiceError("Invalid data URL format")
            elif image_url.startswith(("http://", "https://")):
                # HTTP/HTTPS URL - fetch the image
                response = httpx.get(image_url)
                image_data = base64.standard_b64encode(response.content).decode("utf-8")
                media_type = "image/jpeg"
            else:
                # Assume local file path
                with open(image_url, "rb") as f:
                    image_data = base64.standard_b64encode(f.read()).decode("utf-8")
                media_type = "image/png" if image_url.endswith(".png") else "image/jpeg"

            response = await self._client.messages.create(
                model=settings.anthropic_model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            response_text = response.content[0].text.strip()
            logger.debug(f"Analyzed image successfully")
            return response_text

        except Exception as e:
            logger.error(f"Failed to analyze image: {e}")
            raise AnthropicServiceError(f"Failed to analyze image: {e}")


anthropic_service = AnthropicService()
