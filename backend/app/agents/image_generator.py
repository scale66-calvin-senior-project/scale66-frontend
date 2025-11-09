"""
ImageGeneratorAgent - Carousel slide image rendering agent.
Generates visual assets for carousel slides using Gemini's image generation API,
managing output directories and saving images to disk with proper naming conventions.

Main Functions:
    1. process() - Generates images for all prompts in batch
    2. generate_single_image() - Renders a single slide image from prompt

Connections:
    - Inherits from: BaseAgent
    - Uses services: GeminiService for image generation
    - Uses config: settings.output_dir, settings.gemini_api_key
    - Called by: CarouselPipeline._process_pipeline()
    - Saves to: output/{pipeline_id}/carousel_slide_{n}.png
"""

import os
from typing import Dict, Any, List

from .base_agent import BaseAgent
from ..services.gemini_service import GeminiService
from ..core.config import settings


class ImageGeneratorAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ImageGenerator", config)
        self.output_dir = (config or {}).get("output_dir", settings.output_dir)
        self.gemini_service = None
        if settings.gemini_api_key:
            try:
                self.gemini_service = GeminiService()
            except Exception as error:
                self.log_error(f"Gemini init failed: {error}")
        else:
            self.log_error("Gemini API key not configured; image generation disabled")

    async def process(self, input_data: Dict[str, Any]) -> List[str]:
        prompts: List[str] = input_data.get("prompts", [])
        pipeline_id = input_data.get("pipeline_id", "default")
        generated_paths: List[str] = []
        for index, prompt in enumerate(prompts, start=1):
            generated_paths.append(
                await self.generate_single_image(
                    {
                        "prompt": prompt,
                        "pipeline_id": pipeline_id,
                        "slide_number": index,
                    }
                )
            )
        return generated_paths

    async def generate_single_image(self, input_data: Dict[str, Any]) -> str:
        prompt = input_data.get("prompt", "")
        pipeline_id = input_data.get("pipeline_id", "default")
        slide_number = input_data.get("slide_number", 1)
        if not self.gemini_service:
            raise RuntimeError("Gemini service is unavailable")
        pipeline_output_dir = os.path.join(self.output_dir, pipeline_id)
        os.makedirs(pipeline_output_dir, exist_ok=True)
        image_filename = f"carousel_slide_{slide_number}.png"
        image_path = os.path.join(pipeline_output_dir, image_filename)
        return await self.gemini_service.generate_image(prompt, image_path)

