"""
Gemini Service - Google Gemini API integration for image generation.

Supports multiple Gemini image generation models:
- gemini-3-pro-image-preview (latest, highest quality)
- gemini-2.5-flash-image (faster, cost-effective)
"""

import logging
import base64
from typing import Optional, List, Dict, Any
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
        aspect_ratio: str = "4:5",
        image_size: str = "1K",
    ) -> str:
        """
        Generate image from text prompt.
        
        Uses generate_content API with IMAGE response modality.
        
        Args:
            prompt: Image generation prompt
            aspect_ratio: Image aspect ratio - "1:1", "3:4", "4:3", "4:5", "9:16", "16:9" (default: 4:5)
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
    
    async def generate_image_with_reference(
        self,
        prompt: str,
        images_base64: List[str],
        aspect_ratio: str = "4:5",
        image_size: str = "1K",
    ) -> str:
        """
        Generate image from text prompt with reference image(s).
        
        Use cases:
        - Generate image based on template/reference image
        - Add text overlays to existing images
        - Multi-turn generation with visual context
        
        Args:
            prompt: Text instruction for image generation/editing
            images_base64: List of base64 encoded input images (required)
            aspect_ratio: Output image aspect ratio - "1:1", "3:4", "4:3", "4:5", "9:16", "16:9" (default: 4:5)
            image_size: Output image size - "1K", "2K", or "4K" (default: 1K)
        
        Returns:
            Base64 encoded generated image string
        
        Raises:
            GeminiServiceError: If generation fails
        """
        model_name = settings.gemini_image_model
        
        try:
            logger.debug(
                f"Generating image with {model_name} from {len(images_base64)} input image(s) + text"
            )
            
            # Build parts list: input images + text prompt
            parts = []
            
            # Add input images first
            for img_b64 in images_base64:
                # Decode base64 to bytes for inline_data
                img_bytes = base64.b64decode(img_b64)
                parts.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type="image/png",
                            data=img_bytes
                        )
                    )
                )
            
            # Add text prompt
            parts.append(types.Part(text=prompt))
            
            # Build config for IMAGE output
            config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                )
            )
            
            # Generate image
            response = self._client.models.generate_content(
                model=model_name,
                contents=types.Content(
                    role="user",
                    parts=parts
                ),
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
            
            logger.debug("Image generated successfully from input image + text")
            return base64.b64encode(image_bytes).decode("utf-8")
                
        except GeminiServiceError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate image with {model_name}: {e}")
            raise GeminiServiceError(f"Failed to generate image from input: {e}")

# Create singleton instance
gemini_service = GeminiService()
