from typing import List, Optional
from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import SlideGeneratorInput, SlideGeneratorOutput
from app.services.template_service import template_service


class SlideGenerator(BaseAgent[SlideGeneratorInput, SlideGeneratorOutput]):
    """
    Slide Generator Agent - Generates carousel slide images using AI.
    
    Input:
        format_type: str
        num_body_slides: int
        brand_kit: BrandKit
        user_prompt: str
        hook_text: str
        body_texts: List[str]
        cta_text: Optional[str]
        template_id: str
        hook_slide: str
        body_slide: str
        cta_slide: Optional[str]
    
    Output:
        hook_image: str
        body_images: List[str]
        cta_image: Optional[str]
    """
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
    ) -> str:
        has_previous_slide = previous_slide_base64 is not None
        
        prompt = self._build_slide_prompt(
            input_data=input_data,
            slide_index=slide_index,
            slide_text=slide_text,
            has_previous_slide=has_previous_slide,
        )
        
        images_to_reference = [template_image_base64]
        if has_previous_slide:
            images_to_reference.append(previous_slide_base64)
        
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
    ) -> str:
        if has_previous_slide:
            reference_explanation = """REFERENCE IMAGES:
1. Template (First): Style reference showing aesthetic, layout, typography, colors, spacing
2. Previous Slide (Second): Formatting pattern for series continuity

IGNORE all text/content in both images - extract ONLY visual style and format patterns."""
        else:
            reference_explanation = """REFERENCE IMAGE:
Template: Style reference showing aesthetic, layout, typography, colors, spacing. While none of the content should be copied or reffered to, as much of the visual style should be preserved as possible.

IGNORE all text/content - extract ONLY visual style."""
        
        return f"""Create a carousel slide using the template as a style reference.

{reference_explanation}

CRITICAL: IGNORE TEMPLATE CONTENT
- DO NOT copy any words, text, labels, or information from the template
- Template content is placeholder material - completely irrelevant
- Use template ONLY for visual style

HIERARCHY OF REFERENCES:
1. PRIMARY REFERENCE: Previous Slide. The styling and the format of the previous slide should be STRICTLY preserved in the new slide. 
2. SECONDARY REFERENCE: Template. The template should be used to augment the previous slides formatting pattern and provide a more complete visual style. If no previous slide is provided, then the template should be used as the primary reference.

EXTRACT FROM TEMPLATE:
- Typography: fonts, weights, sizing, spacing, hierarchy
- Layout: positioning, structure, margins, padding
- Colors: backgrounds, text, accents, gradients
- Design: borders, shapes, textures, effects
- Spacing: white space, density, flow

CONTENT SOURCE:
Use ONLY this caption text for primary content areas:
{slide_text}

CONTENT PLACEMENT:
- Primary area: Fill with caption text above.{f'''
- When using template as primary reference: Follow the template's existing content structure and style in the main area. You may form additional words or labels beyond the caption if needed to match the template's format and improve visual coherence.''' if not has_previous_slide else ''}

REMOVE IRRELEVANT CONTENT:
- IMPORTANT: Remove all branding information and logos from the template. If this step is not followed, the slide will not be accepted.
- Remove ALL text, labels, and words from the template that don't relate to the caption or this carousel
- Remove ALL images, logos, icons, or graphics that aren't relevant to the current content
- Remove social handles, email addresses, website URLs, dates, or any specific information from the template
- If an element doesn't support or relate to the caption above, it should be removed entirely
- Blend removed areas seamlessly into the background to maintain clean design
- When in doubt, remove the content.

PRESERVE TEMPLATE STYLE:
- Match typography, layout, colors, spacing exactly
- Only adapt if caption length requires it. Use your formating expertise to make the slide look more coherent and visually appealing.
- Maintain visual hierarchy and readability

{f'''SERIES CONTINUITY:
- Match formatting pattern from previous slide.
- Keep numbering/structure consistent
- Ignore previous slide's words - extract format only''' if has_previous_slide else ''}

OUTPUT:
- Professional slide matching template aesthetic
- ALL content from caption only
- NO template text/labels copied
- Clean design with precise style preservation"""


slide_generator = SlideGenerator()
