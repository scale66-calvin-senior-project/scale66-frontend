"""
Image Generator Agent - Step 4 of AI Pipeline

Generates AI images for carousel slides using Google Imagen 4.

Input: ImageGeneratorInput (hook_slide_story, body_slides_story)
Output: ImageGeneratorOutput (hook_slide_image, body_slides_images)
"""

import logging
from typing import List

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import ImageGeneratorInput, ImageGeneratorOutput
from app.services.ai.gemini_service import GeminiServiceError


logger = logging.getLogger(__name__)


class ImageGenerator(BaseAgent[ImageGeneratorInput, ImageGeneratorOutput]):
    """
    Generates AI images for carousel slides based on story content.
    
    Uses Google Imagen 4 for high-quality image generation optimized for social media.
    """
    
    async def _validate_input(self, input_data: ImageGeneratorInput) -> None:
        """
        Validate input data before execution.
        
        Checks:
        - Hook slide story is not empty
        - Body slides story array is not empty and within limits
        - All story strings are valid
        
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
        
        # Validate body_slides_story
        if not input_data.body_slides_story:
            raise ValidationError("body_slides_story cannot be empty")
        
        if not isinstance(input_data.body_slides_story, list):
            raise ValidationError("body_slides_story must be a list")
        
        if len(input_data.body_slides_story) < 2:
            raise ValidationError("body_slides_story must contain at least 2 slides")
        
        if len(input_data.body_slides_story) > 9:
            raise ValidationError("body_slides_story cannot contain more than 9 slides")
        
        # Validate each body slide
        for i, slide in enumerate(input_data.body_slides_story):
            if not slide or not isinstance(slide, str) or not slide.strip():
                raise ValidationError(f"body_slides_story[{i}] is empty or invalid")
            
            if len(slide.strip()) < 5:
                raise ValidationError(
                    f"body_slides_story[{i}] must be at least 5 characters"
                )
        
        self.logger.debug("Input validation passed")
    
    async def _execute(self, input_data: ImageGeneratorInput) -> ImageGeneratorOutput:
        """
        Execute image generation logic using Google Imagen 4.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Generated images as base64 encoded strings
            
        Raises:
            ExecutionError: If image generation fails
        """
        try:
            total_slides = 1 + len(input_data.body_slides_story)
            self.logger.info(f"Generating {total_slides} images for carousel")
            
            # Generate hook slide image
            self.logger.info("Generating hook slide image")
            hook_prompt = self._create_image_prompt(
                input_data.hook_slide_story,
                is_hook=True
            )
            hook_image = await self._generate_single_image(hook_prompt)
            
            # Generate body slide images
            body_images: List[str] = []
            for i, story in enumerate(input_data.body_slides_story):
                self.logger.info(f"Generating body slide {i+1}/{len(input_data.body_slides_story)}")
                body_prompt = self._create_image_prompt(story, is_hook=False)
                body_image = await self._generate_single_image(body_prompt)
                body_images.append(body_image)
            
            self.logger.info(
                f"Image generation completed successfully: "
                f"1 hook + {len(body_images)} body images"
            )
            
            return ImageGeneratorOutput(
                hook_slide_image=hook_image,
                body_slides_images=body_images,
            )
            
        except GeminiServiceError as e:
            raise ExecutionError(f"Image generation service error: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error during image generation: {str(e)}")
    
    def _create_image_prompt(self, story: str, is_hook: bool) -> str:
        """
        Create image generation prompt based on story content.
        
        Transforms narrative text into visual descriptions suitable for image generation.
        
        Args:
            story: The story text for this slide
            is_hook: Whether this is the hook slide (first slide)
            
        Returns:
            Image generation prompt string
        """
        # Base prompt structure for all images
        base_style = (
            "Professional social media carousel image, modern and clean aesthetic, "
            "vibrant colors, high contrast, visually striking, commercial photography style, "
            "suitable for Instagram and TikTok, no text or words visible in the image"
        )
        
        # Create visual interpretation of the story
        # For hook: more attention-grabbing, bold
        # For body: supportive, illustrative
        
        if is_hook:
            visual_emphasis = (
                "Bold and attention-grabbing composition, strong focal point, "
                "dramatic lighting, eye-catching and scroll-stopping visual"
            )
        else:
            visual_emphasis = (
                "Clear and focused composition, supportive visual elements, "
                "professional and engaging, complements the narrative"
            )
        
        # Extract visual concepts from story
        # For MVP: create a generic but professional prompt based on story context
        content_prompt = (
            f"Create a visual representation that captures the essence of: {story}. "
            f"Focus on visual metaphors and abstract concepts rather than literal text. "
            f"The image should evoke the mood and message without using any written words."
        )
        
        full_prompt = f"{content_prompt} {base_style} {visual_emphasis}"
        
        # Ensure prompt is within Imagen 4 limits (max 480 tokens ~ 1920 characters)
        if len(full_prompt) > 1800:
            self.logger.warning(f"Prompt too long ({len(full_prompt)} chars), truncating")
            full_prompt = full_prompt[:1800]
        
        return full_prompt
    
    async def _generate_single_image(self, prompt: str) -> str:
        """
        Generate a single image using Gemini service.
        
        Args:
            prompt: Image generation prompt
            
        Returns:
            Base64 encoded image string
            
        Raises:
            ExecutionError: If image generation fails
        """
        try:
            # Use 1:1 aspect ratio for Instagram/TikTok compatibility
            # Use 2K for higher quality
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