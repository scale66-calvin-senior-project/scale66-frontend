"""
Anthropic Service - Anthropic API integration.

Provides:
- Text generation using Claude models
- Vision analysis using Claude Vision
- Structured outputs with Pydantic model validation

Used by agents for LLM calls and text generation.
"""

import logging
import base64
import httpx
from typing import Optional, List, TypeVar, Type
from pydantic import BaseModel
from anthropic import Anthropic, AsyncAnthropic
from app.core.config import settings

# Type variable for Pydantic models
T = TypeVar('T', bound=BaseModel)


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
    
    async def generate_structured_output(
        self,
        prompt: str,
        output_model: Type[T],
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> T:
        """
        Generate structured output using Claude with Pydantic model validation.
        
        Uses Anthropic's structured outputs feature to guarantee schema-compliant
        responses without manual JSON parsing or validation.
        
        Args:
            prompt: The prompt to send to the LLM
            output_model: Pydantic model class defining the expected output structure
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Validated instance of the output_model
            
        Raises:
            AnthropicServiceError: If generation fails or response is invalid
        
        Example:
            response = await service.generate_structured_output(
                prompt="Extract info from: John (john@example.com)",
                output_model=ContactInfo
            )
            # response is a validated ContactInfo instance
            print(response.name, response.email)
        """
        try:
            logger.debug(
                f"Generating structured output with model: {settings.anthropic_model}, "
                f"output schema: {output_model.__name__}"
            )
            
            # Use beta.messages.parse() for automatic Pydantic handling
            response = await self._client.beta.messages.parse(
                model=settings.anthropic_model,
                max_tokens=max_tokens,
                temperature=temperature,
                betas=["structured-outputs-2025-11-13"],
                messages=[{"role": "user", "content": prompt}],
                output_format=output_model,
            )
            
            # Check for refusals or max_tokens reached
            if response.stop_reason == "refusal":
                logger.warning("Claude refused the request for safety reasons")
                raise AnthropicServiceError(
                    "Claude refused the request. The output may not match the schema."
                )
            
            if response.stop_reason == "max_tokens":
                logger.warning(
                    "Response was cut off due to max_tokens limit. "
                    "Output may be incomplete."
                )
                raise AnthropicServiceError(
                    "Response exceeded max_tokens limit. Increase max_tokens and retry."
                )
            
            # Parse and validate the output
            parsed_output = response.parsed_output
            
            logger.debug(
                f"Successfully generated and validated structured output: "
                f"{output_model.__name__}"
            )
            
            return parsed_output
        
        except AnthropicServiceError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            logger.error(f"Failed to generate structured output: {e}")
            raise AnthropicServiceError(f"Failed to generate structured output: {e}")

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
