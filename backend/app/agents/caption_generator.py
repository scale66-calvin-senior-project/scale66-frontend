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
        prompt = self._build_prompt(input_data)
        
        images_base64 = self._load_template_images(input_data)
        
        text_output = await asyncio.to_thread(
            self.gemini.generate_text_with_image_analysis,
            prompt=prompt,
            images_base64=images_base64,
            output_model=ClaudeSlidesTextOutput,
        )
        
        expected_body_count = input_data.num_body_slides
        if len(text_output.body_texts) != expected_body_count:
            if len(text_output.body_texts) < expected_body_count:
                while len(text_output.body_texts) < expected_body_count:
                    text_output.body_texts.append("[Content continues...]")
            else:
                text_output.body_texts = text_output.body_texts[:expected_body_count]
        
        return CaptionGeneratorOutput(
            step_name="caption_generator",
            success=True,
            hook_text=text_output.hook_text,
            body_texts=text_output.body_texts,
        )
    
    def _load_template_images(self, input_data: CaptionGeneratorInput) -> List[str]:
        """Load template images as base64 encoded strings for Gemini analysis."""
        images = []
        
        hook_image = template_service.get_template_image_base64(
            input_data.template_id,
            input_data.hook_slide
        )
        images.append(hook_image)
        
        body_image = template_service.get_template_image_base64(
            input_data.template_id,
            input_data.body_slide
        )
        images.append(body_image)
        
        return images
    
    def _build_prompt(self, input_data: CaptionGeneratorInput) -> str:
        format_text_guide = FORMAT_TEXT_GUIDES.get(input_data.format_type, "")
        
        return f"""You are an expert text overlay writer for social media carousel slides. Analyze the provided template images and generate appropriate caption text based on the user request.

USER REQUEST: {input_data.user_prompt}
{format_text_guide}

The images provided show:
1. Hook slide template (first image)
2. Body slide template (second image)

Generate caption text that fits the style and layout of these template images. Create {input_data.num_body_slides} body slide texts.

"""


caption_generator = CaptionGenerator()
