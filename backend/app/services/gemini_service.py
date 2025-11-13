"""
GeminiService - Wrapper for Google Gemini image generation API.
Provides async image generation capabilities using Gemini's official SDK,
handling binary response extraction and file I/O operations.

Main Functions:
    1. generate_image() - Generates and saves image from text prompt
    2. _extract_image_bytes() - Extracts binary image data from API response
    3. _write_bytes() - Saves binary data to file system

Connections:
    - Uses: Google genai client for image generation API
    - Configuration: Loads API key and model from settings
    - Used by: ImageGeneratorAgent for all visual asset generation
    - Saves to: Pipeline-specific output directories
"""

import asyncio
import os
from typing import Optional
import logging

from google import genai

from ..core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("Gemini API key not provided")

        self.model_name = settings.gemini_model
        self.client = genai.Client(api_key=self.api_key)

    async def generate_image(self, prompt: str, output_path: str) -> str:
        try:
            logger.info("Generating image with Gemini model '%s'", self.model_name)

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=[prompt],
            )

            image_bytes = self._extract_image_bytes(response)
            if not image_bytes:
                raise RuntimeError("Gemini response did not include image data")

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            await asyncio.to_thread(self._write_bytes, output_path, image_bytes)

            logger.info("Image saved to: %s", output_path)
            return output_path

        except Exception as e:
            logger.error("Gemini image generation error: %s", e)
            raise

    def _extract_image_bytes(self, response) -> bytes:
        candidates = getattr(response, "candidates", []) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            if not content:
                continue
            for part in getattr(content, "parts", []) or []:
                inline_data = getattr(part, "inline_data", None)
                if inline_data and getattr(inline_data, "data", None):
                    data = inline_data.data
                    if isinstance(data, bytes):
                        return data
                    return bytes(data)
        return b""

    @staticmethod
    def _write_bytes(path: str, data: bytes) -> None:
        with open(path, "wb") as f:
            f.write(data)
            
