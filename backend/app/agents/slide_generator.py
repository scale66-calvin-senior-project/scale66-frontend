from typing import Dict, List, Optional
from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import SlideGeneratorInput, SlideGeneratorOutput
from app.agents.template_decider import CarouselFormat
from app.services.ai.gemini_service import GeminiServiceError
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
                template_image_base64=template_base64,
                previous_slide_base64=None,
            )
            slides_images.append(first_image)
            images_rationale.append(first_rationale)
            
            for i in range(1, input_data.num_slides):
                slide_image, slide_rationale = await self._generate_slide_image(
                    input_data=input_data,
                    slide_index=i,
                    slide_text=input_data.slides_text[i],
                    template_image_base64=template_base64,
                    previous_slide_base64=slides_images[i - 1],
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
        template_image_base64: str,
        previous_slide_base64: Optional[str],
    ) -> tuple[str, str]:
        try:
            prompt = self._build_slide_prompt(
                input_data=input_data,
                slide_index=slide_index,
                slide_text=slide_text,
                has_previous_slide=previous_slide_base64 is not None,
            )
            
            # For first slide, only use template. For subsequent slides, use both template and previous slide
            images_to_reference = [template_image_base64]
            if previous_slide_base64 is not None:
                images_to_reference.append(previous_slide_base64)
            
            image_base64 = await self.gemini.generate_image_with_reference(
                prompt=prompt,
                images_base64=images_to_reference,
                image_size="1K",
            )
            
            rationale = f"Slide {slide_index+1} generated with text: '{slide_text[:50]}...'"
            
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
        has_previous_slide: bool = False,
    ) -> str:
        brand_kit = input_data.brand_kit
        
        # Build reference images explanation
        reference_explanation = ""
        if has_previous_slide:
            reference_explanation = """
REFERENCE IMAGES PROVIDED:
You have been provided with TWO reference images:

1. TEMPLATE IMAGE (First Image):
   - Shows the visual style, layout structure, and design elements to replicate
   - Contains YELLOW HIGHLIGHTED areas showing modifiable zones
   - Use this for: design style, layout, color scheme, typography, spacing

2. PREVIOUS SLIDE (Second Image):
   - The immediately preceding slide in this carousel series
   - Shows the actual formatting and content structure used
   - Use this for: format consistency, content structure patterns, visual continuity
   - CRITICAL: Match the formatting approach used in the previous slide
   - If the previous slide used certain highlighted areas, maintain that pattern
"""
        else:
            reference_explanation = """
REFERENCE IMAGE PROVIDED:
You have been provided with ONE reference image:

1. TEMPLATE IMAGE:
   - Shows the visual style, layout structure, and design elements to replicate
   - Contains YELLOW HIGHLIGHTED areas showing modifiable zones
   - Use this for: design style, layout, color scheme, typography, spacing
"""
        
        return f"""You are a professional carousel slide designer. Your task is to create a carousel slide for a social media carousel post using a template-based approach.
{reference_explanation}
TEMPLATE IMAGE INTERPRETATION:
The template image contains YELLOW HIGHLIGHTED areas and NON-HIGHLIGHTED areas.

YELLOW HIGHLIGHTED AREAS (Modifiable Zones):
- These areas are marked in bright yellow shading showing template placeholder content
- The yellow shading is SEMI-TRANSPARENT, allowing you to see the background texture beneath
- Your task: REPLACE the content in these areas with new content from the Brand Kit or Caption
- CRITICAL: The yellow highlighting itself must be COMPLETELY REMOVED from the final output
- Background texture visible under yellow areas should be PRESERVED (the texture is part of the design)
- Original template text/details visible under yellow shading must be IGNORED and REPLACED

NON-HIGHLIGHTED AREAS (Preserve Exactly):
- All areas WITHOUT yellow highlighting must remain COMPLETELY UNCHANGED (see EXCEPTION CASES below)
- Preserve: background texture, layout structure, spacing, borders, decorative elements, color scheme
- Do not modify positioning, sizing, or styling of non-highlighted elements

EXCEPTION CASES - When Non-Highlighted Areas CAN Be Modified:
Only modify non-highlighted areas in these specific scenarios:
1. TEXT OVERFLOW: If caption content cannot fit within highlighted boundaries while maintaining readability, you may extend text into adjacent non-highlighted areas
   - Only overflow when absolutely necessary for legibility
   - Maintain the template's typography style when extending
   - Ensure overflow text respects the overall layout and doesn't disrupt other elements
2. VISUAL CONSISTENCY: If maintaining carousel series consistency requires matching elements established in previous slides
   - Example: If slide 1 established a visual element for brand consistency, subsequent slides may replicate it
   

CONTENT SOURCES (Priority Order):
1. CAPTION TEXT (Primary content for main highlighted areas):
{slide_text}

2. BRAND KIT INFORMATION (For contextual highlighted areas ONLY):
   - Brand Name: {brand_kit.brand_name}
   - Brand Style: {brand_kit.brand_style}
   - Niche: {brand_kit.brand_niche}
   - Product/Service: {brand_kit.product_service_desc}
   
   CRITICAL: This is the COMPLETE Brand Kit. If information is not listed above, it does NOT exist.
   Do NOT create or infer any additional brand information (emails, websites, social handles, etc.)

CONTENT PLACEMENT RULES:
1. Main highlighted content areas: Use ONLY the CAPTION TEXT provided above
2. Smaller highlighted areas (dates, labels, handles): Use Brand Kit information ONLY if contextually appropriate
3. If no relevant Brand Kit information exists for a highlighted area: LEAVE IT MATCHING THE BACKGROUND (empty/clean)
4. Slide number areas: Use the actual slide number ({slide_index + 1})
5. CRITICAL - NO FABRICATION: Do NOT invent, create, or add ANY information not explicitly provided in Caption or Brand Kit
   - Do NOT create email addresses, phone numbers, websites, or contact information
   - Do NOT add generic labels like "carousel post", "social media", dates, or placeholder text
   - Do NOT fill highlighted areas just because they exist - empty/clean areas are PREFERRED over irrelevant content
6. IMPORTANT: Err on the side of minimalism - leave highlighted areas empty rather than adding irrelevant information

DESIGN CONSTRAINTS:
- Maintain exact typography style (font family, weight, sizing hierarchy) from the reference
- Preserve precise positioning and spacing of all content areas
- Keep the same color palette (background, text colors, accent colors)
- Maintain visual hierarchy and readability from the template design
- All highlighted areas must have yellow shading removed in final output

FORMAT CONSISTENCY (When Previous Slide Provided):
If a previous slide is provided as reference:
- MATCH the content structure and formatting approach used in the previous slide
- If previous slide numbered the caption (e.g., "1. Point"), use the same numbering format
- If previous slide used certain highlighted areas (top corners, bottom areas), maintain that pattern
- Ensure visual and structural continuity across the carousel series
- The previous slide shows you the EXACT format to follow for this series

EXECUTION STEPS:
1. (If provided) Examine the previous slide to understand the format and structure being used
2. Identify all yellow highlighted areas in the template image
3. Preserve the background texture visible under the yellow shading
4. Remove all yellow highlighting from those areas
5. Replace placeholder content with appropriate content from Caption or Brand Kit ONLY
6. Leave highlighted areas empty if no relevant content is available (DO NOT FABRICATE)
7. Keep all non-highlighted areas exactly as shown in the template
8. Match the format consistency established by the previous slide (if provided)
9. Ensure visual consistency with the carousel series

OUTPUT REQUIREMENTS:
- Generate a clean, professional carousel slide
- NO yellow highlighting visible in the final image
- Cohesive visual style matching the template
- Format consistency matching the previous slide (if provided)
- Content contains ONLY information from Caption or Brand Kit - NO fabricated information
- Empty highlighted areas are acceptable and preferred over irrelevant content
- Professional typography and spacing maintained throughout"""


slide_generator = SlideGenerator()
