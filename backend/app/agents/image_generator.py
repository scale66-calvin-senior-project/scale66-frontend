"""
Image Generator Agent - Step 5 of AI Pipeline

Generates AI images for carousel slides WITH text overlays baked in using Gemini 3 Pro.

Receives both verbose stories (for visual context) and short captions (to render).
Gemini 3 Pro renders text directly in images, eliminating separate overlay processing.

Supported models (configured in settings):
- gemini-3-pro-image-preview (with text rendering capabilities)
- gemini-2.5-flash-image (faster alternative)

Input: ImageGeneratorInput (hook_slide_story, body_slides_story, hook_slide_text, body_slides_text)
Output: ImageGeneratorOutput (hook_slide_image, body_slides_images with text rendered)
"""

from typing import List, Optional

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import ImageGeneratorInput, ImageGeneratorOutput
from app.services.ai.gemini_service import GeminiServiceError


class ImageGenerator(BaseAgent[ImageGeneratorInput, ImageGeneratorOutput]):
    """
    Generates AI images with text overlays baked in for carousel slides.
    
    Uses Gemini 3 Pro to render text directly in images, combining visual context
    from stories with short captions to create final carousel slides.
    
    Optimized for social media (9:16 aspect ratio for Instagram/TikTok).
    Model selection is configured via settings.gemini_image_model.
    Singleton pattern ensures single instance across application.
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
        - Hook slide story and text are not empty
        - Body slides story and text arrays match in length and within limits
        - All story and text strings are valid
        
        Args:
            input_data: Image generator input schema
            
        Raises:
            ValidationError: If input is invalid
        """
        # Validate hook_slide_story
        if not input_data.hook_slide_story or not input_data.hook_slide_story.strip():
            raise ValidationError("hook_slide_story cannot be empty")
        
        if len(input_data.hook_slide_story.strip()) < 10:
            raise ValidationError("hook_slide_story must be at least 10 characters")
        
        # Validate hook_slide_text
        if not input_data.hook_slide_text or not input_data.hook_slide_text.strip():
            raise ValidationError("hook_slide_text cannot be empty")
        
        if len(input_data.hook_slide_text.strip()) < 2:
            raise ValidationError("hook_slide_text must be at least 2 characters")
        
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
        
        # Validate each body slide text
        for i, text in enumerate(input_data.body_slides_text):
            if not text or not isinstance(text, str) or not text.strip():
                raise ValidationError(f"body_slides_text[{i}] is empty or invalid")
            
            if len(text.strip()) < 2:
                raise ValidationError(
                    f"body_slides_text[{i}] must be at least 2 characters"
                )
        
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
            
            # Generate hook slide image with text
            self.logger.debug("Generating hook slide image with text")
            hook_prompt = self._create_image_prompt(
                story=input_data.hook_slide_story,
                text_overlay=input_data.hook_slide_text,
                is_hook=True
            )
            hook_image = await self._generate_single_image(hook_prompt)
            
            # Generate body slide images with text
            body_images: List[str] = []
            for i, (story, text) in enumerate(zip(
                input_data.body_slides_story,
                input_data.body_slides_text
            )):
                self.logger.debug(f"Generating body slide {i+1}/{len(input_data.body_slides_story)} with text")
                body_prompt = self._create_image_prompt(
                    story=story,
                    text_overlay=text,
                    is_hook=False
                )
                body_image = await self._generate_single_image(body_prompt)
                body_images.append(body_image)
            
            self.logger.debug(
                f"Image generation completed: "
                f"1 hook + {len(body_images)} body images (all with text rendered)"
            )
            
            return ImageGeneratorOutput(
                step_name="image_generator",
                success=True,
                hook_slide_image=hook_image,
                body_slides_images=body_images,
            )
            
        except GeminiServiceError as e:
            raise ExecutionError(f"Image generation service error: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error during image generation: {str(e)}")
    
    def _create_image_prompt(self, story: str, text_overlay: str, is_hook: bool) -> str:
        """
        Create image generation prompt with text rendering instructions.
        
        Combines visual context from story with text overlay instructions
        for Gemini 3 Pro to render text directly in the image.
        
        Args:
            story: The verbose story text for visual context
            text_overlay: The short text caption to render on the image
            is_hook: Whether this is the hook slide (first slide)
            
        Returns:
            Image generation prompt string with text rendering instructions
        """
        # Text rendering instructions for Gemini 3 Pro
        text_instructions = (
            f"IMPORTANT: Include the text '{text_overlay}' prominently displayed on the image. "
            f"The text should be large, bold, highly readable, and professionally styled. "
            f"Use high contrast (white text with shadow or dark text on light background). "
            f"Center or strategically place the text for maximum impact and readability on mobile devices. "
            f"The text must be sharp, clear, and instantly readable."
        )
        
        # Base visual style for all images
        base_style = (
            "Professional social media carousel image for Instagram/TikTok, "
            "modern and clean aesthetic, vibrant colors, high contrast, "
            "visually striking, commercial photography style, 9:16 vertical format, "
            "optimized for mobile viewing"
        )
        
        # Visual emphasis based on slide type
        if is_hook:
            visual_emphasis = (
                "Bold and attention-grabbing composition, strong focal point, "
                "dramatic lighting, eye-catching and scroll-stopping visual, "
                "leave space for prominent text display"
            )
        else:
            visual_emphasis = (
                "Clear and focused composition, supportive visual elements, "
                "professional and engaging, complements the narrative, "
                "balanced layout with room for text"
            )
        
        # Visual context from story
        content_prompt = (
            f"Create a visual representation that captures the essence of: {story}. "
            f"Focus on visual metaphors and concepts that support the message. "
            f"Ensure the composition leaves negative space for text overlay."
        )
        
        # Combine all elements
        full_prompt = (
            f"{text_instructions}\n\n"
            f"{content_prompt}\n\n"
            f"{base_style} {visual_emphasis}"
        )
        
        # Ensure prompt is within reasonable limits
        # Gemini 3 Pro supports longer prompts
        max_prompt_length = 2500
        if len(full_prompt) > max_prompt_length:
            self.logger.warning(
                f"Prompt too long ({len(full_prompt)} chars), truncating to {max_prompt_length}"
            )
            full_prompt = full_prompt[:max_prompt_length]
        
        return full_prompt
    
    async def _generate_single_image(self, prompt: str) -> str:
        """
        Generate a single image using configured Gemini service.
        
        Args:
            prompt: Image generation prompt
            
        Returns:
            Base64 encoded image string
            
        Raises:
            ExecutionError: If image generation fails
        """
        try:
            # Use 9:16 aspect ratio for Instagram/TikTok Stories/Reels
            # Use 1K for balance of quality and generation speed
            # Note: gemini-3-pro-image-preview supports up to 4K resolution
            image_base64 = await self.gemini.generate_image(
                prompt=prompt,
                aspect_ratio="9:16",
                image_size="1K",
            )
            
            return image_base64
            
        except GeminiServiceError as e:
            self.logger.error(f"Failed to generate image: {e}")
            raise ExecutionError(f"Image generation failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error generating image: {e}")
            raise ExecutionError(f"Unexpected image generation error: {str(e)}")


# Create singleton instance for easy import
image_generator = ImageGenerator()