"""
Image Generator Agent - Step 5 of AI Pipeline

Input: ImageGeneratorInput (hook_slide_story, body_slides_story, hook_slide_text, body_slides_text)
Output: ImageGeneratorOutput (hook_slide_image, body_slides_images with text rendered)
"""

import base64
from pathlib import Path
from typing import List, Optional

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import ImageGeneratorInput, ImageGeneratorOutput
from app.services.ai.gemini_service import GeminiServiceError


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
        
        Checks:
        - Brand kit is complete with required fields
        - Format type is valid
        - Complete story is not empty
        - Hook slide story and text are not empty
        - Body slides story and text arrays match in length and within limits
        - All story and text strings are valid
        
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
        
        # Validate complete_story
        if not input_data.complete_story or not input_data.complete_story.strip():
            raise ValidationError("complete_story cannot be empty")
        
        if len(input_data.complete_story.strip()) < 10:
            raise ValidationError("complete_story must be at least 10 characters")
        
        # Validate hook_slide_story
        if not input_data.hook_slide_story or not input_data.hook_slide_story.strip():
            raise ValidationError("hook_slide_story cannot be empty")
        
        if len(input_data.hook_slide_story.strip()) < 10:
            raise ValidationError("hook_slide_story must be at least 10 characters")
        
        # Validate hook_slide_text (can be minimal or empty for some formats)
        if input_data.hook_slide_text is None:
            raise ValidationError("hook_slide_text cannot be None")
        
        if not isinstance(input_data.hook_slide_text, str):
            raise ValidationError("hook_slide_text must be a string")
        
        # Validate body_slides_story
        if not input_data.body_slides_story:
            raise ValidationError("body_slides_story cannot be empty")
        
        if not isinstance(input_data.body_slides_story, list):
            raise ValidationError("body_slides_story must be a list")
        
        if len(input_data.body_slides_story) < 2:
            raise ValidationError("body_slides_story must contain at least 2 slides")
        
        if len(input_data.body_slides_story) > 9:
            raise ValidationError("body_slides_story cannot contain more than 9 slides")
        
        # Validate body_slides_text
        if not input_data.body_slides_text:
            raise ValidationError("body_slides_text cannot be empty")
        
        if not isinstance(input_data.body_slides_text, list):
            raise ValidationError("body_slides_text must be a list")
        
        # Check array length match
        if len(input_data.body_slides_story) != len(input_data.body_slides_text):
            raise ValidationError(
                f"body_slides_story ({len(input_data.body_slides_story)}) and "
                f"body_slides_text ({len(input_data.body_slides_text)}) must have the same length"
            )
        
        # Validate each body slide story
        for i, slide in enumerate(input_data.body_slides_story):
            if not slide or not isinstance(slide, str) or not slide.strip():
                raise ValidationError(f"body_slides_story[{i}] is empty or invalid")
            
            if len(slide.strip()) < 5:
                raise ValidationError(
                    f"body_slides_story[{i}] must be at least 5 characters"
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
            total_slides = 1 + len(input_data.body_slides_story)
            self.logger.debug(f"Generating {total_slides} images with text overlays for carousel")
            
            # Generate hook slide image from text only (no reference)
            self.logger.debug("Generating hook slide image from text")
            hook_image, hook_rationale = await self._generate_hook_image(
                input_data=input_data
            )
            
            # Generate body slide images using hook image as reference
            body_images: List[str] = []
            body_rationales: List[str] = []
            for i, (story, text) in enumerate(zip(
                input_data.body_slides_story,
                input_data.body_slides_text
            )):
                self.logger.debug(f"Generating body slide {i+1}/{len(input_data.body_slides_story)} with hook reference")
                body_image, body_rationale = await self._generate_body_image(
                    input_data=input_data,
                    hook_image_base64=hook_image,
                    slide_story=story,
                    slide_text=text,
                    slide_index=i
                )
                body_images.append(body_image)
                body_rationales.append(body_rationale)
            
            # Combine all rationales for logging
            all_rationales = [hook_rationale] + body_rationales
            
            self.logger.info(
                f"Image generation completed: "
                f"1 hook (text-only) + {len(body_images)} body images (with hook reference)"
            )
            self.logger.info("Image Rationales:")
            self.logger.info(f"  [0] Hook: {hook_rationale}")
            for i, rationale in enumerate(body_rationales, 1):
                self.logger.info(f"  [{i}] Body {i}: {rationale}")
            
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
        return f"""Create a visually striking hook slide image for a {input_data.format_type} carousel using the reference template.

COMPLETE CAROUSEL STORY:
{input_data.complete_story}

HOOK SLIDE STORY:
{input_data.hook_slide_story}

HOOK SLIDE TEXT TO DISPLAY:
"{input_data.hook_slide_text}"

CAROUSEL FORMAT:
{input_data.format_type}

VISUAL REQUIREMENTS:
- Match the visual style, layout structure, and design aesthetic of the reference image
- Create a scroll-stopping, attention-grabbing first slide
- Capture the essence and mood of both the complete story and hook story
- Adapt the template to reflect this specific carousel's narrative
- Maintain 4:5 vertical format optimized for mobile

TEXT RENDERING:
- Display "{input_data.hook_slide_text}" prominently on the image
- Use the typography style and placement from the reference
- Ensure high contrast and mobile readability
- Position text for maximum impact and clarity

Blend the story content with the reference template's design language to create the hook slide."""
    
    def _build_body_prompt(
        self,
        input_data: ImageGeneratorInput,
        slide_story: str,
        slide_text: str,
        slide_index: int
    ) -> str:
        """
        Build prompt for body image generation with hook reference.
        
        Args:
            input_data: Full input data with all context
            slide_story: Story for this specific body slide
            slide_text: Caption for this specific body slide
            slide_index: Index of this body slide (0-based)
            
        Returns:
            Prompt string for body image generation
        """
        total_body_slides = len(input_data.body_slides_story)
        slide_number = slide_index + 2  # +1 for 1-based, +1 for hook
        
        return f"""Create body slide {slide_number}/{total_body_slides + 1} using the reference image's visual style.

REFERENCE IMAGE:
The reference image (hook slide) establishes the PRIMARY visual style for this carousel.

COMPLETE CAROUSEL STORY:
{input_data.complete_story}

THIS SLIDE'S STORY:
{slide_story}

THIS SLIDE'S TEXT TO DISPLAY:
"{slide_text}"

CAROUSEL FORMAT:
{input_data.format_type}

CRITICAL DESIGN APPROACH:
- PRIMARY SOURCE: Copy the visual style, color palette, typography, and layout from the reference image
- The reference image defines the design language - match it precisely
- SECONDARY ADAPTATION: Blend this slide's story and text into the established style
- DO NOT redesign or deviate from the reference's aesthetic
- This is a continuation using the same visual template

CONTENT INTEGRATION:
- Adapt imagery/visuals to reflect this slide's story: {slide_story}
- Ensure the story content is represented while maintaining reference style
- Update visual elements to match this slide's message
- Keep the same composition structure and design approach

TEXT RENDERING:
- Display "{slide_text}" prominently on the image
- Match typography style, size, and placement from reference
- Maintain high contrast and mobile readability
- Use the same text positioning approach as reference

The reference image is the style guide - adapt content to fit its design, not the other way around."""
    
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
        slide_story: str,
        slide_text: str,
        slide_index: int
    ) -> tuple[str, str]:
        """
        Generate body slide image using hook image as reference.
        
        Args:
            input_data: Full input data with all context
            hook_image_base64: Base64 encoded hook image to use as reference
            slide_story: Story for this specific body slide
            slide_text: Caption for this specific body slide
            slide_index: Index of this body slide (0-based)
            
        Returns:
            Tuple of (base64 encoded image string, rationale)
            
        Raises:
            ExecutionError: If image generation fails
        """
        try:
            prompt = self._build_body_prompt(input_data, slide_story, slide_text, slide_index)
            
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