"""
Gemini Service - Google Gemini API integration.
"""

import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiServiceError(Exception):
    """Base exception for Gemini service errors."""
    pass

class GeminiService:
    """
    Google Gemini service for text and image generation.
    Default Model: gemini-2.5-flash-image (configured in settings)
    """

    _instance: Optional['GeminiService'] = None
    _client: None

    def __new__(cls):
        """Singleton instance creation."""
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self): 
        """
        Initialize Gemini service.
        """
        if self._client is None:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self._client = genai.GenerativeModel(settings.gemini_model)
                logger.info(f"Initialized Gemini client with model: {settings.gemini_model}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                raise GeminiServiceError(f"Failed to initialize Gemini client: {e}")

    async def generate_image(
        self, 
        prompt: str,
        aspect_ratio: str = "16:9",
        image_size: str = "4K",
    ) -> str:
        """
        Generate image using Gemini image model.
        
        Args:
            prompt: Image generation prompt
            num_images: Number of images to generate
        
        Returns:
            Image URL
        """
        try:
            logger.info(f"Generating image with prompt: {prompt}")
            response = self._client.models.generate_content(
                contents=[prompt], 
                model=settings.gemini_model,
                config=types.GenerateContentConfig(
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=image_size,
                    )
                )
            )

            logger.info(f"Generated image with prompt: {prompt}")

            image_parts = image_parts[0].as_image()

            if not image_parts:
                logger.error("No image parts found in response")
                raise GeminiServiceError("No image parts found in response")

            image = image_parts[0].as_image()
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            logger.info(f"Converted image to base64: {img_base64}")

            return img_base64

        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            raise GeminiServiceError(f"Failed to generate image: {e}")

# Create singleton instance
gemini_service = GeminiService()