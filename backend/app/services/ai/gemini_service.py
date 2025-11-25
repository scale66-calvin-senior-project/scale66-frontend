"""
Gemini Service - Google Imagen 4 API integration for image generation.
"""

import logging
import base64
from typing import Optional
from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiServiceError(Exception):
    """Base exception for Gemini service errors."""
    pass

class GeminiService:
    """
    Google Imagen 4 service for image generation.
    Default Model: imagen-4.0-generate-001 (configured in settings)
    """

    _instance: Optional['GeminiService'] = None
    _client: Optional[genai.Client] = None

    def __new__(cls):
        """Singleton instance creation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self): 
        """
        Initialize Gemini service with Imagen 4.
        """
        if self._client is None:
            try:
                self._client = genai.Client(api_key=settings.gemini_api_key)
                logger.info(f"Initialized Gemini client with Imagen 4")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                raise GeminiServiceError(f"Failed to initialize Gemini client: {e}")

    async def generate_image(
        self, 
        prompt: str,
        aspect_ratio: str = "1:1",
        image_size: str = "1K",
    ) -> str:
        """
        Generate image using Imagen 4 model.
        
        Args:
            prompt: Image generation prompt (max 480 tokens)
            aspect_ratio: Image aspect ratio - "1:1", "3:4", "4:3", "9:16", "16:9" (default: 1:1)
            image_size: Image size - "1K" or "2K" (default: 1K)
        
        Returns:
            Base64 encoded image string
        """
        try:
            logger.info(f"Generating image with Imagen 4: {prompt[:100]}...")
            
            response = self._client.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                )
            )

            if not response.generated_images:
                logger.error("No images generated in response")
                raise GeminiServiceError("No images generated in response")

            image_bytes = response.generated_images[0].image.image_bytes
            
            logger.info(f"Image generated successfully")

            return base64.b64encode(image_bytes).decode("utf-8")

        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            raise GeminiServiceError(f"Failed to generate image: {e}")

# Create singleton instance
gemini_service = GeminiService()
