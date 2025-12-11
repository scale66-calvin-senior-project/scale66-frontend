import asyncio
from typing import Optional, List

from app.agents.base_agent import BaseAgent
from app.models.pipeline import CaptionGeneratorInput, CaptionGeneratorOutput
from app.models.structured import ClaudeSlidesTextOutput
from app.constants import FORMAT_TEXT_GUIDES
from app.services.template_service import template_service


class CaptionGenerator(BaseAgent[CaptionGeneratorInput, CaptionGeneratorOutput]):
    _instance: Optional['CaptionGenerator'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        super().__init__()
    
    async def _validate_input(self, input_data: CaptionGeneratorInput) -> None:
        pass
    
    async def _execute(self, input_data: CaptionGeneratorInput) -> CaptionGeneratorOutput:
        # Generate hook slide caption
        hook_prompt = self._build_hook_prompt(input_data)
        hook_image = self._load_hook_template_image(input_data)
        
        hook_output = await asyncio.to_thread(
            self.gemini.generate_text_with_image_analysis,
            prompt=hook_prompt,
            images_base64=[hook_image],
            output_model=ClaudeSlidesTextOutput,
        )
        
        # Generate body slide captions
        body_prompt = self._build_body_prompt(input_data)
        body_image = self._load_body_template_image(input_data)
        
        body_output = await asyncio.to_thread(
            self.gemini.generate_text_with_image_analysis,
            prompt=body_prompt,
            images_base64=[body_image],
            output_model=ClaudeSlidesTextOutput,
        )
        
        expected_body_count = input_data.num_body_slides
        body_texts = body_output.body_texts
        if len(body_texts) != expected_body_count:
            if len(body_texts) < expected_body_count:
                while len(body_texts) < expected_body_count:
                    body_texts.append("[Content continues...]")
            else:
                body_texts = body_texts[:expected_body_count]
        
        return CaptionGeneratorOutput(
            step_name="caption_generator",
            success=True,
            hook_text=hook_output.hook_text,
            body_texts=body_texts,
        )
    
    def _load_hook_template_image(self, input_data: CaptionGeneratorInput) -> str:
        """Load hook template image as base64 encoded string for Gemini analysis."""
        return template_service.get_template_image_base64(
            input_data.template_id,
            input_data.hook_slide
        )
    
    def _load_body_template_image(self, input_data: CaptionGeneratorInput) -> str:
        """Load body template image as base64 encoded string for Gemini analysis."""
        return template_service.get_template_image_base64(
            input_data.template_id,
            input_data.body_slide
        )
    
    def _build_hook_prompt(self, input_data: CaptionGeneratorInput) -> str:
        """Build prompt for hook slide generation."""
        format_text_guide = FORMAT_TEXT_GUIDES.get(input_data.format_type, "")
        
        return f"""You are an expert text overlay writer for social media carousel slides.

Format Type: {input_data.format_type}

Analyze the provided hook slide template image to understand the styling and formatting requirements for the caption text. Use the image layout, typography, and design elements as your primary reference for how the caption should be structured and styled.

For understanding the content and tone of the caption, refer to the format style guide below:
{format_text_guide}

USER REQUEST: {input_data.user_prompt}

Generate a hook slide caption text that fits both the visual style of the template image and the content requirements of the format type.
"""
    
    def _build_body_prompt(self, input_data: CaptionGeneratorInput) -> str:
        """Build prompt for body slide generation."""
        format_text_guide = FORMAT_TEXT_GUIDES.get(input_data.format_type, "")
        
        return f"""You are an expert text overlay writer for social media carousel slides.

Format Type: {input_data.format_type}

Analyze the provided body slide template image to understand the styling and formatting requirements for the caption text. Use the image layout, typography, and design elements as your primary reference for how the caption should be structured and styled.

For understanding the content and tone of the captions, refer to the format style guide below:
{format_text_guide}

USER REQUEST: {input_data.user_prompt}

Generate {input_data.num_body_slides} body slide caption texts that fit both the visual style of the template image and the content requirements of the format type.
"""


caption_generator = CaptionGenerator()
