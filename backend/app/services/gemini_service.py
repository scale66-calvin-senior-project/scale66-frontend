import google.generativeai as genai
import aiofiles
import os
from typing import Optional
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("Gemini API key not provided")
        
        genai.configure(api_key=self.api_key)
        self.model_name = settings.gemini_model
        
    async def generate_image(self, prompt: str, output_path: str) -> str:
        """Generate image using Gemini nanobanana"""
        try:
            # Note: This is a placeholder implementation
            # Replace with actual Gemini nanobanana API calls when available
            logger.info(f"Generating image with prompt: {prompt[:50]}...")
            
            # For now, create a text file with the prompt as placeholder
            # In real implementation, this would call Gemini's image generation API
            async with aiofiles.open(output_path, 'w') as f:
                await f.write(f"Generated image for prompt: {prompt}")
            
            logger.info(f"Image saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Gemini image generation error: {str(e)}")
            raise
            
    async def enhance_image_prompt(self, basic_prompt: str) -> str:
        """Use Gemini to enhance image prompts"""
        try:
            model = genai.GenerativeModel(self.model_name)
            
            enhance_prompt = f"""
            Enhance this image generation prompt to be more detailed and visually specific:
            
            {basic_prompt}
            
            Add details about:
            - Specific visual elements and composition
            - Lighting and atmosphere
            - Art style and quality descriptors
            - Camera angle and perspective
            
            Return only the enhanced prompt, nothing else:
            """
            
            response = await model.generate_content_async(enhance_prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini prompt enhancement error: {str(e)}")
            # Return original prompt if enhancement fails
            return basic_prompt