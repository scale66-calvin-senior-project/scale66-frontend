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
        brand_kit = input_data.brand_kit
        
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
   - If the previous slide used certain highlighted areas, maintain that pattern"""
        else:
            reference_explanation = """
REFERENCE IMAGE PROVIDED:
You have been provided with ONE reference image:

1. TEMPLATE IMAGE:
   - Shows the visual style, layout structure, and design elements to replicate
   - Contains YELLOW HIGHLIGHTED areas showing modifiable zones
   - Use this for: design style, layout, color scheme, typography, spacing"""
        
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
