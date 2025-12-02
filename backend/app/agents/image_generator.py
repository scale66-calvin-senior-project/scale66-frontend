"""
Image Generator Agent - Step 5 of AI Pipeline

Input: ImageGeneratorInput (hook_slide_strategy, body_slides_strategy, hook_slide_text, body_slides_text)
Output: ImageGeneratorOutput (hook_slide_image, body_slides_images with text rendered)
"""

import base64
from pathlib import Path
from typing import Dict, List, Optional

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import ImageGeneratorInput, ImageGeneratorOutput
from app.agents.carousel_format_decider import CarouselFormat
from app.services.ai.gemini_service import GeminiServiceError


# Format-specific visual design guides - defines HOW slides LOOK, not content
FORMAT_SLIDE_GUIDES: Dict[str, str] = {
    CarouselFormat.LISTICLE_TIPS: """Visual design framework for numbered tips/insights carousel slides.

DESIGN PHILOSOPHY:
The imagery serves as a beautiful canvas for the tips being delivered. The visual design should enhance readability and create scroll-stopping appeal without competing with the text content.

HOOK SLIDE VISUAL DESIGN:
Layout: Clean, centered composition with generous whitespace
Canvas: Decorated background with subtle patterns, gradients, or textures that add visual interest without distraction
Text Zone: Large, prominent central area for hook text
Typography Style: Bold, high-contrast headline font - easily readable at small mobile sizes
Visual Accent: Minimal decorative elements (geometric shapes, subtle icons, or brand touches) that frame but don't overwhelm
Color Approach: Strong contrast between background and text - either dark text on light canvas or light text on dark canvas

BODY SLIDE VISUAL DESIGN:
Layout: Consistent with hook - maintains visual continuity across carousel
Canvas: Same decorated background style as hook - cohesive carousel feel
Text Zone: Prominent central area - the tip IS the visual
Typography Style: Clear, readable font - slightly smaller than hook but still mobile-optimized
Numbering: If tip numbers are shown, integrate them subtly into design (not just plain "1.", "2.")
Visual Elements: Minimal - decorative accents should complement, not compete with tip text

CRITICAL VISUAL RULES:
1. TEXT IS THE HERO: The tip text should be the visual focal point - all design serves readability
2. CLEAN CANVAS: Background decoration should be elegant and non-distracting
3. MOBILE-FIRST: All text must be readable on small screens - test at thumbnail size
4. VISUAL CONTINUITY: All slides should feel like they belong to the same carousel
5. NO IMAGERY CLUTTER: Avoid photos, complex illustrations, or busy graphics that compete with text
6. PROFESSIONAL FINISH: Polished, refined design that builds credibility

WHAT TO AVOID:
- Stock photo backgrounds that distract from text
- Busy patterns that reduce text readability
- Multiple competing visual elements
- Inconsistent styling between slides
- Text placed over high-contrast image areas
- Decorative elements that feel generic or clip-art-like

REFERENCE IMAGE USAGE:
The reference image represents a successful example of this format type. Analyze its:
- Color palette and contrast approach
- Typography treatment and text placement
- Background decoration style
- Overall composition and balance
- Whitespace usage and breathing room
Adapt these visual principles to the current carousel's content and brand.""",
}


class ImageGenerator(BaseAgent[ImageGeneratorInput, ImageGeneratorOutput]):
    """
    Generates AI images with text overlays baked in for carousel slides.
    """
    
    _instance: Optional['ImageGenerator'] = None
    
    def __new__(cls):
        """Singleton instance creation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize image generator agent."""
        super().__init__()
    
    async def _validate_input(self, input_data: ImageGeneratorInput) -> None:
        """
        Validate input data before execution.
        
        Args:
            input_data: Image generator input schema
            
        Raises:
            ValidationError: If input is invalid
        """
        # Validate brand_kit
        if not input_data.brand_kit:
            raise ValidationError("brand_kit is required")
        
        # Check required brand kit fields
        required_fields = {
            "brand_name": input_data.brand_kit.brand_name,
            "brand_niche": input_data.brand_kit.brand_niche,
            "brand_style": input_data.brand_kit.brand_style,
            "product_service_desc": input_data.brand_kit.product_service_desc,
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value or not str(field_value).strip():
                raise ValidationError(f"brand_kit.{field_name} is required")
        
        # Validate format_type
        if not input_data.format_type or not input_data.format_type.strip():
            raise ValidationError("format_type is required")
        
        # Validate complete_strategy
        if not input_data.complete_strategy or not input_data.complete_strategy.strip():
            raise ValidationError("complete_strategy cannot be empty")
        
        if len(input_data.complete_strategy.strip()) < 10:
            raise ValidationError("complete_strategy must be at least 10 characters")
        
        # Validate hook_slide_strategy
        if not input_data.hook_slide_strategy or not input_data.hook_slide_strategy.strip():
            raise ValidationError("hook_slide_strategy cannot be empty")
        
        if len(input_data.hook_slide_strategy.strip()) < 10:
            raise ValidationError("hook_slide_strategy must be at least 10 characters")
        
        if not isinstance(input_data.hook_slide_text, str):
            raise ValidationError("hook_slide_text must be a string")
        
        # Validate body_slides_strategy
        if not input_data.body_slides_strategy:
            raise ValidationError("body_slides_strategy cannot be empty")
        
        if not isinstance(input_data.body_slides_strategy, list):
            raise ValidationError("body_slides_strategy must be a list")
        
        if len(input_data.body_slides_strategy) < 2:
            raise ValidationError("body_slides_strategy must contain at least 2 slides")
        
        if len(input_data.body_slides_strategy) > 9:
            raise ValidationError("body_slides_strategy cannot contain more than 9 slides")
        
        # Validate body_slides_text
        if not input_data.body_slides_text:
            raise ValidationError("body_slides_text cannot be empty")
        
        if not isinstance(input_data.body_slides_text, list):
            raise ValidationError("body_slides_text must be a list")
        
        # Check array length match
        if len(input_data.body_slides_strategy) != len(input_data.body_slides_text):
            raise ValidationError(
                f"body_slides_strategy ({len(input_data.body_slides_strategy)}) and "
                f"body_slides_text ({len(input_data.body_slides_text)}) must have the same length"
            )
        
        # Validate each body slide strategy
        for i, slide in enumerate(input_data.body_slides_strategy):
            if not slide or not isinstance(slide, str) or not slide.strip():
                raise ValidationError(f"body_slides_strategy[{i}] is empty or invalid")
            
            if len(slide.strip()) < 5:
                raise ValidationError(
                    f"body_slides_strategy[{i}] must be at least 5 characters"
                )
        
        # Validate each body slide text (can be minimal or empty for some formats)
        for i, text in enumerate(input_data.body_slides_text):
            if text is None:
                raise ValidationError(f"body_slides_text[{i}] cannot be None")
            
            if not isinstance(text, str):
                raise ValidationError(f"body_slides_text[{i}] must be a string")
        
        self.logger.debug("Input validation passed")
    
    async def _execute(self, input_data: ImageGeneratorInput) -> ImageGeneratorOutput:
        """
        Execute image generation logic using configured Gemini model.
        
        Generates images with text overlays baked in.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Generated images with text rendered (base64 encoded strings)
            
        Raises:
            ExecutionError: If image generation fails
        """
        try:
            total_slides = 1 + len(input_data.body_slides_strategy)
            self.logger.debug(f"Generating {total_slides} images with text overlays for carousel")
            
            # Generate hook slide image from text only (no reference)
            self.logger.debug("Generating hook slide image from text")
            hook_image, hook_rationale = await self._generate_hook_image(
                input_data=input_data
            )
            
            # Generate body slide images using hook image as reference
            body_images: List[str] = []
            body_rationales: List[str] = []
            for i, (strategy, text) in enumerate(zip(
                input_data.body_slides_strategy,
                input_data.body_slides_text
            )):
                self.logger.debug(f"Generating body slide {i+1}/{len(input_data.body_slides_strategy)} with hook reference")
                body_image, body_rationale = await self._generate_body_image(
                    input_data=input_data,
                    hook_image_base64=hook_image,
                    slide_strategy=strategy,
                    slide_text=text,
                    slide_index=i
                )
                body_images.append(body_image)
                body_rationales.append(body_rationale)
            
            # Combine all rationales for logging
            all_rationales = [hook_rationale] + body_rationales
            
            self.logger.info(
                f"Image generation completed: "
                f"1 hook (template-based) + {len(body_images)} body images (with hook reference)"
            )
            
            return ImageGeneratorOutput(
                step_name="image_generator",
                success=True,
                hook_slide_image=hook_image,
                body_slides_images=body_images,
                images_rationale=all_rationales,
            )
            
        except GeminiServiceError as e:
            raise ExecutionError(f"Image generation service error: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error during image generation: {str(e)}")
    
    def _build_hook_prompt(self, input_data: ImageGeneratorInput) -> str:
        """
        Build prompt for hook image generation.
        
        Args:
            input_data: Full input data with all context
            
        Returns:
            Prompt string for hook image generation
        """
        system_prompt = self._build_system_prompt(input_data.format_type)
        user_prompt = self._build_hook_user_prompt(input_data)
        
        return f"{system_prompt}\n\n{user_prompt}"
    
    def _build_system_prompt(self, format_type: str) -> str:
        """
        Build system prompt for image generation with format-specific visual guide.
        
        Args:
            format_type: The carousel format type
            
        Returns:
            System prompt string
        """
        slide_guide = FORMAT_SLIDE_GUIDES.get(format_type)
        
        return f"""You are an expert carousel visual designer who creates FINAL SLIDE IMAGES for social media carousels.

YOUR ROLE:
- Create polished, ready-to-post slide images with text rendered on the canvas
- Use the STRATEGY to understand WHAT to communicate and WHY
- Use the FORMAT SLIDE GUIDE to know HOW to design the visual
- Use the REFERENCE IMAGE as a visual template for this format type

CRITICAL RULES:

1. OUTPUT IS FINAL. Your image is the actual carousel slide. Professional, polished, ready-to-post.

2. FORMAT SLIDE GUIDE IS YOUR PRIMARY VISUAL REFERENCE. It defines design philosophy, layout, typography treatment, color approach, and visual rules for this specific format. Follow it closely.

3. STRATEGY PROVIDES INTENT. The complete strategy and slide strategy tell you the purpose and message. The FORMAT SLIDE GUIDE tells you how to visualize it.

4. TEXT IS PRE-WRITTEN. Display ONLY the exact text provided. Do not add, modify, or paraphrase any text. The text generator has already crafted the perfect copy.

5. REFERENCE IMAGE IS YOUR TEMPLATE. It was retrieved as the closest visual example for this carousel format and user request. Analyze its design language (colors, typography, composition, decoration) and adapt it to the current content.

---

FORMAT: {format_type}

FORMAT SLIDE GUIDE:
{slide_guide}

---

VISUAL OUTPUT REQUIREMENTS:
- 4:5 vertical aspect ratio (optimized for mobile feeds)
- Text must be readable at thumbnail size
- High contrast between text and background
- Professional, polished finish
- Cohesive design that feels intentional"""
    
    def _build_hook_user_prompt(self, input_data: ImageGeneratorInput) -> str:
        """
        Build user prompt for hook slide image generation.
        
        Args:
            input_data: Full input data with all context
            
        Returns:
            User prompt string for hook slide
        """
        return f"""REFERENCE IMAGE:
The attached reference image is a successful example of a {input_data.format_type} hook slide. This was retrieved as the closest visual template for this format type. Analyze and adapt its design language.

COMPLETE CAROUSEL STRATEGY:
"{input_data.complete_strategy}"

THIS SLIDE'S STRATEGY:
"{input_data.hook_slide_strategy}"

EXACT TEXT TO RENDER:
"{input_data.hook_slide_text}"

Based on the reference image's visual style, this slide's strategy, and the FORMAT SLIDE GUIDE, create the hook slide image with the text rendered exactly as provided."""
    
    def _build_body_prompt(
        self,
        input_data: ImageGeneratorInput,
        slide_strategy: str,
        slide_text: str,
        slide_index: int
    ) -> str:
        """
        Build prompt for body image generation with hook reference.
        
        Args:
            input_data: Full input data with all context
            slide_strategy: Strategy for this specific body slide
            slide_text: Caption for this specific body slide
            slide_index: Index of this body slide (0-based)
            
        Returns:
            Prompt string for body image generation
        """
        system_prompt = self._build_body_system_prompt(input_data.format_type, slide_index)
        user_prompt = self._build_body_user_prompt(
            input_data=input_data,
            slide_strategy=slide_strategy,
            slide_text=slide_text,
            slide_index=slide_index,
        )
        
        return f"{system_prompt}\n\n{user_prompt}"
    
    def _build_body_system_prompt(self, format_type: str, slide_index: int) -> str:
        """
        Build system prompt for body slide image generation.
        
        Args:
            format_type: The carousel format type
            slide_index: Index of this body slide (0-based)
            
        Returns:
            System prompt string
        """
        slide_guide = FORMAT_SLIDE_GUIDES.get(format_type)
        slide_number = slide_index + 2  # +1 for 1-based, +1 for hook being slide 1
        
        return f"""You are an expert carousel visual designer creating BODY SLIDE {slide_number} of a carousel.

YOUR ROLE:
- Create a body slide that maintains PERFECT VISUAL CONTINUITY with the hook slide
- Use the HOOK IMAGE as your PRIMARY VISUAL REFERENCE - it establishes the design language
- Use the STRATEGY to understand this slide's purpose and message
- Use the FORMAT SLIDE GUIDE for body slide design principles

CRITICAL RULES:

1. HOOK IMAGE IS YOUR STYLE GUIDE. The attached hook image defines:
   - Color palette and contrast
   - Typography style and text treatment
   - Background decoration approach
   - Overall composition and layout
   - Whitespace and breathing room
   Match these elements precisely.

2. VISUAL CONTINUITY IS PARAMOUNT. A viewer should immediately recognize this as part of the same carousel. Do not deviate from the established aesthetic.

3. TEXT IS PRE-WRITTEN. Display ONLY the exact text provided. Do not add, modify, or paraphrase any text.

4. SLIDE POSITION MATTERS. This is body slide {slide_number - 1} - maintain the visual rhythm and pacing established by the carousel.

---

FORMAT: {format_type}

FORMAT SLIDE GUIDE (Body Slide Principles):
{slide_guide}

---

DESIGN APPROACH:
1. MATCH the hook's visual style exactly
2. ADAPT only the content (text, any slide-specific details)
3. MAINTAIN composition structure, color palette, typography
4. CREATE cohesion - this slide should feel like it "belongs" """
    
    def _build_body_user_prompt(
        self,
        input_data: ImageGeneratorInput,
        slide_strategy: str,
        slide_text: str,
        slide_index: int,
    ) -> str:
        """
        Build user prompt for body slide image generation.
        
        Args:
            input_data: Full input data with all context
            slide_strategy: Strategy for this specific body slide
            slide_text: Text for this specific body slide
            slide_index: Index of this body slide (0-based)
            
        Returns:
            User prompt string for body slide
        """
        total_body_slides = len(input_data.body_slides_strategy)
        slide_number = slide_index + 2
        
        return f"""REFERENCE IMAGE (HOOK SLIDE):
The attached image is the hook slide you created for this carousel. This establishes the PRIMARY visual style. Match it precisely.

SLIDE POSITION:
Body Slide {slide_index + 1} of {total_body_slides} (Slide {slide_number} of {total_body_slides + 1} total)

COMPLETE CAROUSEL STRATEGY:
"{input_data.complete_strategy}"

THIS SLIDE'S STRATEGY:
"{slide_strategy}"

EXACT TEXT TO RENDER:
"{slide_text}"

Based on the hook slide's visual style, this slide's strategy, and the FORMAT SLIDE GUIDE, create this body slide with the text rendered exactly as provided. Maintain perfect visual continuity with the hook."""
    
    def _load_template_image(self) -> str:
        """
        Load carousel template image from local storage.
        
        Returns:
            Base64 encoded template image
            
        Raises:
            ExecutionError: If template cannot be loaded
        """
        try:
            # Path to carousel-4 template
            template_path = Path(__file__).parent.parent.parent / "templates" / "carousel-4" / "1.png"
            
            if not template_path.exists():
                raise ExecutionError(f"Template not found: {template_path}")
            
            # Read and encode image
            with open(template_path, 'rb') as f:
                image_bytes = f.read()
            
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            self.logger.debug(f"Loaded template from: {template_path}")
            
            return image_base64
            
        except Exception as e:
            self.logger.error(f"Failed to load template: {e}")
            raise ExecutionError(f"Template loading failed: {str(e)}")
    
    async def _generate_hook_image(
        self,
        input_data: ImageGeneratorInput
    ) -> tuple[str, str]:
        """
        Generate hook slide image using template reference.
        
        Args:
            input_data: Full input data with all context
            
        Returns:
            Tuple of (base64 encoded image string, rationale)
            
        Raises:
            ExecutionError: If image generation fails
        """
        try:
            # Load template reference
            template_base64 = self._load_template_image()
            
            prompt = self._build_hook_prompt(input_data)
            
            image_base64 = await self.gemini.generate_image_with_reference(
                prompt=prompt,
                images_base64=[template_base64],
                image_size="1K",
            )
            
            rationale = f"Hook image generated with template reference and caption: '{input_data.hook_slide_text}'"
            
            return image_base64, rationale
            
        except GeminiServiceError as e:
            self.logger.error(f"Failed to generate hook image: {e}")
            raise ExecutionError(f"Hook image generation failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error generating hook image: {e}")
            raise ExecutionError(f"Unexpected hook image generation error: {str(e)}")
    
    async def _generate_body_image(
        self,
        input_data: ImageGeneratorInput,
        hook_image_base64: str,
        slide_strategy: str,
        slide_text: str,
        slide_index: int
    ) -> tuple[str, str]:
        """
        Generate body slide image using hook image as reference.
        
        Args:
            input_data: Full input data with all context
            hook_image_base64: Base64 encoded hook image to use as reference
            slide_strategy: Strategy for this specific body slide
            slide_text: Caption for this specific body slide
            slide_index: Index of this body slide (0-based)
            
        Returns:
            Tuple of (base64 encoded image string, rationale)
            
        Raises:
            ExecutionError: If image generation fails
        """
        try:
            prompt = self._build_body_prompt(input_data, slide_strategy, slide_text, slide_index)
            
            image_base64 = await self.gemini.generate_image_with_reference(
                prompt=prompt,
                images_base64=[hook_image_base64],
                image_size="1K",
            )
            
            rationale = f"Body image {slide_index+1} generated with hook reference and caption: '{slide_text}'"
            
            return image_base64, rationale
            
        except GeminiServiceError as e:
            self.logger.error(f"Failed to generate body image {slide_index+1}: {e}")
            raise ExecutionError(f"Body image {slide_index+1} generation failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error generating body image {slide_index+1}: {e}")
            raise ExecutionError(f"Unexpected body image {slide_index+1} generation error: {str(e)}")



image_generator = ImageGenerator()