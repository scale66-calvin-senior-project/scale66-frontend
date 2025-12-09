from typing import List, Optional, Literal
from app.agents.base_agent import BaseAgent
from app.models.pipeline import SlideGeneratorInput, SlideGeneratorOutput
from app.services.template_service import template_service


class SlideGenerator(BaseAgent[SlideGeneratorInput, SlideGeneratorOutput]):
    _instance: Optional['SlideGenerator'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        super().__init__()
    
    async def _validate_input(self, input_data: SlideGeneratorInput) -> None:
        pass
    
    async def _execute(self, input_data: SlideGeneratorInput) -> SlideGeneratorOutput:
        hook_template_base64 = self._load_template_image(
            input_data.template_id, 
            input_data.hook_slide
        )
        hook_image = await self._generate_slide_image(
            input_data=input_data,
            slide_index=0,
            slide_text=input_data.hook_text,
            template_image_base64=hook_template_base64,
            previous_slide_base64=None,
            slide_type="hook",
        )
        
        body_template_base64 = self._load_template_image(
            input_data.template_id, 
            input_data.body_slide
        )
        
        body_images: List[str] = []
        previous_body_slide = None
        
        for i, body_text in enumerate(input_data.body_texts):
            body_image = await self._generate_slide_image(
                input_data=input_data,
                slide_index=i + 1,
                slide_text=body_text,
                template_image_base64=body_template_base64,
                previous_slide_base64=previous_body_slide,
                slide_type="body",
            )
            body_images.append(body_image)
            previous_body_slide = body_image
        
        cta_image = None
        if input_data.cta_slide and input_data.cta_text:
            cta_template_base64 = self._load_template_image(
                input_data.template_id, 
                input_data.cta_slide
            )
            cta_image = await self._generate_slide_image(
                input_data=input_data,
                slide_index=input_data.num_slides - 1,
                slide_text=input_data.cta_text,
                template_image_base64=cta_template_base64,
                previous_slide_base64=None,
                slide_type="cta",
            )
        
        return SlideGeneratorOutput(
            step_name="slide_generator",
            success=True,
            hook_image=hook_image,
            body_images=body_images,
            cta_image=cta_image,
        )
    
    def _load_template_image(self, template_id: str, slide_filename: str) -> str:
        return template_service.get_template_image_base64(template_id, slide_filename)
    
    async def _generate_slide_image(
        self,
        input_data: SlideGeneratorInput,
        slide_index: int,
        slide_text: str,
        template_image_base64: str,
        previous_slide_base64: Optional[str],
        slide_type: Literal["hook", "body", "cta"],
    ) -> str:
        has_previous_slide = previous_slide_base64 is not None
        is_body_slide = slide_type == "body"
        
        prompt = self._build_slide_prompt(
            input_data=input_data,
            slide_index=slide_index,
            slide_text=slide_text,
            has_previous_slide=has_previous_slide,
            slide_type=slide_type,
        )
        
        if has_previous_slide:
            images_to_reference = [previous_slide_base64]
        else:
            images_to_reference = [template_image_base64]
        
        return await self.gemini.generate_image_with_reference(
            prompt=prompt,
            images_base64=images_to_reference,
            image_size="1K",
        )
    
    def _build_slide_prompt(
        self,
        input_data: SlideGeneratorInput,
        slide_index: int,
        slide_text: str,
        has_previous_slide: bool = False,
        slide_type: Literal["hook", "body", "cta"] = "body",
    ) -> str:
        if has_previous_slide:
            return f"""Create a carousel slide by EXACTLY replicating the previous slide's visual style.

RULES FOR USING THE PREVIOUS SLIDE:
1. PRESERVE EXACTLY the same visual style and formatting from the previous slide.
2. ONLY Change the content of the slide to match the new content.

CONTENT RULES:
Use PRIMARILY this text: {slide_text}{f"""

NUMBERING RULES:
- Continue the numbering sequence from previous slide (IF PRESENT)
- Use number (IF NEEDED): {slide_index}
- Match exact numbering style and placement""" if slide_type == "body" else ""}"""
        else:
            return f"""Create a carousel slide using the template as style reference.

RULES FOR USING THE TEMPLATE:
1. PRESERVE the template's exact visual style and formatting while removing any branding.
2. REMOVE ALL branding such as logos, social handles, website URLs, names, dates, etc.

CONTENT RULES:
Use PRIMARILY this text: {slide_text}{f"""

NUMBERING RULES:
- ONLY add numbering if template shows clear numbering format
- If present, use number: {slide_index}
- Match template's numbering style exactly""" if slide_type == "body" else ""}"""


slide_generator = SlideGenerator()
