from typing import Dict, List, Optional
from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import SlideGeneratorInput, SlideGeneratorOutput
from app.agents.template_decider import CarouselFormat
from app.services.ai.gemini_service import GeminiServiceError
from app.services.template_service import template_service


FORMAT_SLIDE_GUIDES: Dict[str, str] = {
    CarouselFormat.LISTICLE_TIPS: """
    Purpose: To create slides with clean visuals, and helpful standalone tips, one per slide.
    Listicle tips follow a numbered format, one per slide. Each tip should be a standalone tip, unrelated to other tips or external context that wouldn't be available to the target audience.
    Slide Visual Guidelines:
        1. The styles should match across all slides.
        2. The visuals should not be distracting to the text.
        3. Negative space should be used to create a clean and professional look.
        4. The visuals should be consistent, for example: if TIP # is used on the first slide, it should be used on the second slide, and so on.
    """,
}


class SlideGenerator(BaseAgent[SlideGeneratorInput, SlideGeneratorOutput]):
    _instance: Optional['SlideGenerator'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        super().__init__()
    
    async def _validate_input(self, input_data: SlideGeneratorInput) -> None:
        if not input_data.format_type or not input_data.format_type.strip():
            raise ValidationError("format_type is required")
        
        if input_data.num_slides < 3 or input_data.num_slides > 10:
            raise ValidationError(
                f"num_slides must be between 3 and 10, got {input_data.num_slides}"
            )
        
        if not input_data.brand_kit:
            raise ValidationError("brand_kit is required")
        
        required_fields = {
            "brand_name": input_data.brand_kit.brand_name,
            "brand_niche": input_data.brand_kit.brand_niche,
            "brand_style": input_data.brand_kit.brand_style,
            "product_service_desc": input_data.brand_kit.product_service_desc,
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value or not str(field_value).strip():
                raise ValidationError(f"brand_kit.{field_name} is required")
        
        if not input_data.user_prompt or not input_data.user_prompt.strip():
            raise ValidationError("user_prompt cannot be empty")
        
        if len(input_data.user_prompt.strip()) < 10:
            raise ValidationError("user_prompt must be at least 10 characters")
        
        if not input_data.slides_text:
            raise ValidationError("slides_text cannot be empty")
        
        if not isinstance(input_data.slides_text, list):
            raise ValidationError("slides_text must be a list")
        
        if len(input_data.slides_text) != input_data.num_slides:
            raise ValidationError(
                f"slides_text length ({len(input_data.slides_text)}) must match "
                f"num_slides ({input_data.num_slides})"
            )
        
        for i, text in enumerate(input_data.slides_text):
            if text is None:
                raise ValidationError(f"slides_text[{i}] cannot be None")
            if not isinstance(text, str):
                raise ValidationError(f"slides_text[{i}] must be a string")
        
        if not input_data.template_id or not input_data.template_id.strip():
            raise ValidationError("template_id is required")
        
        template = template_service.get_template(input_data.template_id)
        if not template:
            raise ValidationError(f"Template '{input_data.template_id}' not found")
    
    async def _execute(self, input_data: SlideGeneratorInput) -> SlideGeneratorOutput:
        try:
            template_base64 = self._load_template_image(input_data.template_id)
            
            slides_images: List[str] = []
            images_rationale: List[str] = []
            
            first_image, first_rationale = await self._generate_slide_image(
                input_data=input_data,
                slide_index=0,
                slide_text=input_data.slides_text[0],
                reference_image_base64=template_base64,
                is_first_slide=True,
            )
            slides_images.append(first_image)
            images_rationale.append(first_rationale)
            
            for i in range(1, input_data.num_slides):
                slide_image, slide_rationale = await self._generate_slide_image(
                    input_data=input_data,
                    slide_index=i,
                    slide_text=input_data.slides_text[i],
                    reference_image_base64=first_image,
                    is_first_slide=False,
                )
                slides_images.append(slide_image)
                images_rationale.append(slide_rationale)
            
            return SlideGeneratorOutput(
                step_name="slide_generator",
                success=True,
                slides_images=slides_images,
                images_rationale=images_rationale,
            )
            
        except GeminiServiceError as e:
            raise ExecutionError(f"Slide generation service error: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error during slide generation: {str(e)}")
    
    def _load_template_image(self, template_id: str) -> str:
        try:
            image_base64 = template_service.get_template_image_base64(template_id, slide_number=1)
            return image_base64
            
        except Exception as e:
            raise ExecutionError(f"Template loading failed: {str(e)}")
    
    async def _generate_slide_image(
        self,
        input_data: SlideGeneratorInput,
        slide_index: int,
        slide_text: str,
        reference_image_base64: str,
        is_first_slide: bool,
    ) -> tuple[str, str]:
        try:
            prompt = self._build_slide_prompt(
                input_data=input_data,
                slide_index=slide_index,
                slide_text=slide_text,
                is_first_slide=is_first_slide,
            )
            
            image_base64 = await self.gemini.generate_image_with_reference(
                prompt=prompt,
                images_base64=[reference_image_base64],
                image_size="1K",
            )
            
            slide_type = "hook" if is_first_slide else "body"
            rationale = f"Slide {slide_index+1} ({slide_type}) generated with text: '{slide_text[:50]}...'"
            
            return image_base64, rationale
            
        except GeminiServiceError as e:
            raise ExecutionError(f"Slide {slide_index+1} generation failed: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected slide {slide_index+1} generation error: {str(e)}")
    
    def _build_slide_prompt(
        self,
        input_data: SlideGeneratorInput,
        slide_index: int,
        slide_text: str,
        is_first_slide: bool,
    ) -> str:
        slide_guide = FORMAT_SLIDE_GUIDES.get(input_data.format_type, "")
        brand_kit = input_data.brand_kit
        slide_type = "hook slide (first slide)" if is_first_slide else f"slide {slide_index + 1}"
        
        return f"""Create a {slide_type} for a carousel post by combining three elements:

1. REFERENCE IMAGE (Primary Source):
   - Extract and replicate: layout structure, color palette, typography style, spacing, visual elements
   - Maintain exact positioning of text areas and graphic elements
   - Preserve the overall aesthetic and design language

2. FORMAT GUIDE (Design Principles):
{slide_guide}
   - Use these principles to ensure the slide fits the carousel's purpose
   - Apply these guidelines when adapting the reference style

3. CAPTION TEXT (Content):
{slide_text}
   - Replace the reference image's text with this caption
   - Maintain readability and visual hierarchy from the reference
   - Ensure text doesn't exceed available space or disrupt layout

BRAND CONTEXT: {brand_kit.brand_name} | Style: {brand_kit.brand_style}

EXECUTION:
- Start with the reference image's exact visual style as your foundation
- Apply the format guide's principles to maintain carousel consistency
- Integrate the new caption text while preserving all visual styling
- Ensure this slide visually matches other slides in the series"""


slide_generator = SlideGenerator()
