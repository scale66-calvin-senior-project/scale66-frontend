"""
Gemini Service - Google Gemini API integration for image generation.

Supports multiple Gemini image generation models:
- gemini-3-pro-image-preview (latest, highest quality)
- gemini-2.5-flash-image (faster, cost-effective)
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
    Google Gemini service for AI image generation.
    
    Uses generate_content API with IMAGE response modality.
    Supports gemini-3-pro-image-preview and gemini-2.5-flash-image.
    
    Default Model: Configured via settings.gemini_image_model
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
        Initialize Gemini service with configurable image model.
        """
        if self._client is None:
            try:
                self._client = genai.Client(api_key=settings.gemini_api_key)
                logger.debug(
                    f"Initialized Gemini client with model: {settings.gemini_image_model}"
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                raise GeminiServiceError(f"Failed to initialize Gemini client: {e}")
    
    async def generate_image(
        self, 
        prompt: str,
        aspect_ratio: str = "9:16",
        image_size: str = "1K",
    ) -> str:
        """
        Generate image using configured Gemini model.
        
        Uses generate_content API with IMAGE response modality.
        
        Args:
            prompt: Image generation prompt
            aspect_ratio: Image aspect ratio - "1:1", "3:4", "4:3", "9:16", "16:9" (default: 9:16)
            image_size: Image size - "1K", "2K", or "4K" (default: 1K)
                Note: 4K only supported on gemini-3-pro-image-preview
        
        Returns:
            Base64 encoded image string
            
        Raises:
            GeminiServiceError: If image generation fails
        """
        model_name = settings.gemini_image_model
        
        try:
            logger.debug(
                f"Generating image with {model_name} "
                f"(aspect_ratio={aspect_ratio}, size={image_size}): {prompt[:100]}..."
            )
            
            config = types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                ),
            )
            
            response = self._client.models.generate_content(
                model=settings.gemini_image_model,
                contents=prompt,
                config=config
            )
            
            # Extract image from response
            image_part = None
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_part = part
                    break
            
            if not image_part:
                logger.error("No image found in Gemini response")
                raise GeminiServiceError("No image found in Gemini response")
            
            # Get image bytes and encode to base64
            image_bytes = image_part.inline_data.data
            
            logger.debug("Image generated successfully")
            return base64.b64encode(image_bytes).decode("utf-8")
                
        except GeminiServiceError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate image with {model_name}: {e}")
            raise GeminiServiceError(f"Failed to generate image: {e}")

# Create singleton instance
gemini_service = GeminiService()
