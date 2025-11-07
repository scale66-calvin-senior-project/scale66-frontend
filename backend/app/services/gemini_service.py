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
        """Generate an image with Gemini using the official image API."""
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
            
