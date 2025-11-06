from typing import Dict, Any, List
import os
import asyncio
from .base_agent import BaseAgent
from ..models.pipeline import SlideContent
from ..services.gemini_service import GeminiService
from ..core.config import settings


class ImageGeneratorAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ImageGenerator", config)
        self.output_dir = config.get("output_dir", "./output") if config else "./output"
        self.gemini_service = None
        if settings.gemini_api_key:
            try:
                self.gemini_service = GeminiService()
            except ValueError as e:
                self.log_error(f"Failed to initialize Gemini service: {e}")
        
    async def process(self, input_data: Dict[str, Any]) -> List[SlideContent]:
        slide_contents = input_data.get("slide_contents", [])
        pipeline_id = input_data.get("pipeline_id", "default")
        
        self.log_info(f"Generating images for {len(slide_contents)} slides")
        
        # Create output directory for this pipeline
        pipeline_output_dir = os.path.join(self.output_dir, pipeline_id)
        os.makedirs(pipeline_output_dir, exist_ok=True)
        
        # Generate images for each slide
        updated_contents = []
        for slide_content in slide_contents:
            updated_content = await self._generate_image(slide_content, pipeline_output_dir)
            updated_contents.append(updated_content)
            
        return updated_contents
        
    async def _generate_image(self, slide_content: SlideContent, output_dir: str) -> SlideContent:
        self.log_info(f"Generating image for scene {slide_content.scene_number}")
        
        image_filename = f"scene_{slide_content.scene_number}.png"
        image_path = os.path.join(output_dir, image_filename)
        
        if self.gemini_service:
            # Generate image using Gemini (prompt already enhanced by OpenAI)
            generated_path = await self.gemini_service.generate_image(slide_content.image_prompt, image_path)
            slide_content.image_path = generated_path
        else:
            self.log_info("Using placeholder image generation (no Gemini API key)")
            # Create placeholder file
            await self._create_placeholder_image(image_path, slide_content.image_prompt)
            slide_content.image_path = image_path
        
        return slide_content
        
    async def generate_single_image(self, input_data: Dict[str, Any]) -> str:
        """Generate a single image for carousel slides"""
        prompt = input_data.get("prompt", "")
        pipeline_id = input_data.get("pipeline_id", "default")
        slide_number = input_data.get("slide_number", 1)
        
        self.log_info(f"Generating single image for slide {slide_number}")
        
        # Create output directory for this pipeline
        pipeline_output_dir = os.path.join(self.output_dir, pipeline_id)
        os.makedirs(pipeline_output_dir, exist_ok=True)
        
        image_filename = f"carousel_slide_{slide_number}.png"
        image_path = os.path.join(pipeline_output_dir, image_filename)
        
        if self.gemini_service:
            # Generate image using Gemini (prompt already enhanced by OpenAI)
            generated_path = await self.gemini_service.generate_image(prompt, image_path)
            return generated_path
        else:
            self.log_info("Using placeholder image generation (no Gemini API key)")
            # Create placeholder file
            await self._create_placeholder_image(image_path, prompt)
            return image_path

    async def _create_placeholder_image(self, image_path: str, prompt: str):
        # Placeholder implementation for when Gemini API is not available
        with open(image_path, 'w') as f:
            f.write(f"Placeholder image for prompt: {prompt}\n\nTo use Gemini image generation, add your Gemini API key to the .env file.")
            
    def _validate_image_prompt(self, prompt: str) -> bool:
        return len(prompt.strip()) > 0