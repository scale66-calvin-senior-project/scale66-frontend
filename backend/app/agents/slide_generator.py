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
   - A STYLE REFERENCE ONLY - shows the aesthetic, layout, and design to replicate
   - IGNORE all text, words, and semantic content in this image
   - Extract ONLY: visual style, layout structure, color palette, typography style, spacing patterns, design elements
   - The actual content/meaning in this template is IRRELEVANT and must be replaced

2. PREVIOUS SLIDE (Second Image):
   - The immediately preceding slide in this carousel series
   - Shows the formatting and content structure pattern established for this series
   - IGNORE the specific words/content shown - extract ONLY the format pattern
   - Use this to maintain visual continuity and structural consistency across slides"""
        else:
            reference_explanation = """
REFERENCE IMAGE PROVIDED:
You have been provided with ONE reference image:

1. TEMPLATE IMAGE:
   - A STYLE REFERENCE ONLY - shows the aesthetic, layout, and design to replicate
   - IGNORE all text, words, and semantic content in this image
   - Extract ONLY: visual style, layout structure, color palette, typography style, spacing patterns, design elements
   - The actual content/meaning in this template is IRRELEVANT and must be replaced"""
        
        return f"""You are a professional carousel slide designer. Your task is to create a carousel slide for a social media carousel post using a style-reference approach.

{reference_explanation}

CRITICAL INSTRUCTION - IGNORE REFERENCE IMAGE CONTENT:
The reference image(s) provided contain existing text, labels, and visual content. You MUST:
- COMPLETELY IGNORE the semantic meaning, words, and content shown in the reference images
- DO NOT copy, replicate, or be influenced by any text, labels, or information displayed
- The reference content is placeholder/example material and has NO relevance to this carousel
- Treat the reference as a "visual mockup" showing ONLY style, not content

WHAT TO EXTRACT FROM REFERENCE IMAGES:
Extract and replicate ONLY these aesthetic and structural elements:
1. TYPOGRAPHY STYLE: Font family, font weight, text sizing hierarchy, letter spacing, line height
2. LAYOUT STRUCTURE: Positioning of content blocks, spatial relationships, margins, padding
3. COLOR PALETTE: Background colors, text colors, accent colors, gradients, overlays
4. DESIGN ELEMENTS: Borders, shapes, decorative elements, background textures, visual effects
5. VISUAL HIERARCHY: Size relationships, emphasis patterns, visual flow, readability structure
6. SPACING PATTERNS: White space distribution, content density, breathing room between elements

WHAT TO COMPLETELY IGNORE IN REFERENCE IMAGES:
DO NOT use or be influenced by:
- Any words, text, or labels shown in the reference
- The specific content or messaging displayed
- Placeholder information or example data
- The semantic meaning or context of reference content
- Email addresses, social handles, dates, or any specific information shown

CONTENT SOURCES (ONLY Use These):
All semantic content MUST come exclusively from these sources:

1. CAPTION TEXT (Primary Content):
{slide_text}

2. BRAND KIT INFORMATION (Contextual Use Only):
   - Brand Name: {brand_kit.brand_name}
   - Brand Style: {brand_kit.brand_style}
   - Niche: {brand_kit.brand_niche}
   - Product/Service: {brand_kit.product_service_desc}
   
   CRITICAL: This is the COMPLETE Brand Kit. If information is not listed above, it does NOT exist.
   Do NOT create or infer any additional brand information (emails, websites, social handles, etc.)

CONTENT PLACEMENT STRATEGY:
1. Primary content areas: Use the CAPTION TEXT provided above
2. Secondary/contextual areas: Use Brand Kit information ONLY if contextually appropriate
3. Slide numbering: Use the actual slide number ({slide_index})
4. Empty spaces: Leave clean/empty rather than adding irrelevant content
5. ABSOLUTE RULE - NO FABRICATION: Do NOT invent ANY information not explicitly provided
   - Do NOT create contact information, social handles, emails, phone numbers, websites
   - Do NOT add generic filler like "carousel post", "social media", dates, or placeholder text
   - Do NOT copy content from the reference images
   - Empty/minimal design is PREFERRED over fabricated or irrelevant information

STYLE PRESERVATION RULES:
These elements from the reference MUST be preserved:
- Exact typography style (font characteristics, sizing hierarchy)
- Precise layout structure and positioning patterns
- Complete color palette and visual scheme
- Spacing, padding, and margin patterns
- Design elements, borders, textures, decorative features
- Visual hierarchy and readability approach

STYLE MODIFICATION EXCEPTIONS:
Only deviate from the reference style in these cases:
1. DIRECT CONTRADICTION: When reference style completely contradicts the new content requirements
   - Example: Reference has room for 3 bullet points, but caption requires 5 points
   - Action: Adapt spacing/sizing to accommodate while preserving overall aesthetic
2. CONTENT INCOMPATIBILITY: When reference layout cannot physically accommodate the new content
   - Example: Reference designed for short text, but caption is lengthy
   - Action: Adjust layout minimally to fit content while maintaining style consistency
3. BRAND ALIGNMENT: When reference aesthetic contradicts brand kit specifications
   - Example: Reference is playful, but brand style is "professional, corporate"
   - Action: Adapt design to align with brand while preserving layout structure

In ALL other cases, preserve the reference aesthetic exactly.

FORMAT CONSISTENCY (When Previous Slide Provided):
When a previous slide is provided:
- MATCH the content structure and formatting pattern established
- If previous slide numbered items (e.g., "1. Point"), maintain that numbering system
- If previous slide positioned brand name in top-right, maintain that placement
- Ensure visual and structural continuity across the carousel series
- The previous slide establishes the EXACT format pattern to follow
- REMEMBER: Ignore the specific words in previous slide, extract only the format pattern

EXECUTION CHECKLIST:
1. (If provided) Examine previous slide to extract the format pattern being used
2. Analyze reference image to extract ONLY aesthetic style (ignore all text/content)
3. Identify layout structure, typography style, color palette, spacing patterns
4. Replace ALL content areas with new content from Caption and Brand Kit
5. Preserve the aesthetic style precisely (fonts, colors, spacing, layout)
6. Ensure NO content from reference images appears in the output
7. Verify NO fabricated information has been added
8. Match format consistency with previous slide (if provided)
9. Maintain visual continuity for carousel series

OUTPUT REQUIREMENTS:
- Professional carousel slide with reference aesthetic style
- ALL content derived exclusively from Caption and Brand Kit
- ZERO content copied or influenced by reference image text/labels
- Precise preservation of typography, layout, colors, and spacing from reference
- Format consistency with previous slides in series
- NO fabricated information - empty spaces preferred over irrelevant content
- Clean, cohesive design that matches the reference style but contains entirely new content"""


slide_generator = SlideGenerator()
