"""
Text Generator Agent - Step 4 of AI Pipeline

Input: TextGeneratorInput (hook_slide_story, body_slides_story)
Output: TextGeneratorOutput (hook_slide_text, body_slides_text)
"""

from typing import Dict, List, Optional

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import TextGeneratorInput, TextGeneratorOutput
from app.models.structured import ClaudeTextOutput
from app.agents.carousel_format_decider import CarouselFormat
from app.services.ai.anthropic_service import AnthropicServiceError


# Format-specific caption tone and structure guides
FORMAT_CAPTION_GUIDES: Dict[str, str] = {
    CarouselFormat.LISTICLE_TIPS: "Detailed, standalone tips. Each caption complete - reader gets full value without context. Can be longer to explain thoroughly. Parallel structure across slides.",
}


class TextGenerator(BaseAgent[TextGeneratorInput, TextGeneratorOutput]):
    """
    Converts verbose story narratives into short, punchy carousel captions.
    
    Uses Claude Sonnet 4.5 for text refinement and caption extraction.
    No image analysis - runs before image generation.
    Singleton pattern ensures single instance across application.
    """
    
    _instance: Optional['TextGenerator'] = None
    
    def __new__(cls):
        """Singleton instance creation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize text generator agent."""
        super().__init__()
    
    async def _validate_input(self, input_data: TextGeneratorInput) -> None:
        """
        Validate input data before execution.
        
        Checks:
        - Brand kit is complete with required fields
        - Format type is valid
        - Complete story is not empty
        - Hook slide story is not empty
        - Body slides stories array is valid and within limits
        - All story strings are valid
        
        Args:
            input_data: Text generator input schema
            
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
        
        # Validate body_slides_story
        if not input_data.body_slides_story:
            raise ValidationError("body_slides_story cannot be empty")
        
        if not isinstance(input_data.body_slides_story, list):
            raise ValidationError("body_slides_story must be a list")
        
        if len(input_data.body_slides_story) < 2:
            raise ValidationError("body_slides_story must contain at least 2 slides")
        
        if len(input_data.body_slides_story) > 9:
            raise ValidationError("body_slides_story cannot contain more than 9 slides")
        
        # Validate each body slide story
        for i, story in enumerate(input_data.body_slides_story):
            if not story or not isinstance(story, str) or not story.strip():
                raise ValidationError(f"body_slides_story[{i}] is empty or invalid")
            
            if len(story.strip()) < 5:
                raise ValidationError(
                    f"body_slides_story[{i}] must be at least 5 characters"
                )
        
        self.logger.debug("Input validation passed")
    
    async def _execute(self, input_data: TextGeneratorInput) -> TextGeneratorOutput:
        """
        Args:
            input_data: Validated input data
            
        Returns:
            Generated captions for the hook and body slides
            
        Raises:
            ExecutionError: If text generation fails
        """
        try:
            total_slides = 1 + len(input_data.body_slides_story)
            self.logger.debug(f"Generating captions for {total_slides} slides")
            
            # Log the caption guide being used
            caption_guide = FORMAT_CAPTION_GUIDES.get(input_data.format_type, "Default caption approach")
            self.logger.info(f"Caption Guide: {caption_guide}")
            
            # Generate hook slide caption
            self.logger.debug("Generating hook slide caption")
            hook_text, hook_rationale = await self._generate_caption(
                input_data=input_data,
                story=input_data.hook_slide_story,
                is_hook=True,
            )
            
            # Generate body slides captions
            body_texts: List[str] = []
            body_rationales: List[str] = []
            
            for i, story in enumerate(input_data.body_slides_story):
                self.logger.debug(f"Generating body slide {i+1}/{len(input_data.body_slides_story)}")
                body_text, body_rationale = await self._generate_caption(
                    input_data=input_data,
                    story=story,
                    is_hook=False,
                )
                body_texts.append(body_text)
                body_rationales.append(body_rationale)
            
            # Combine all rationales for logging
            all_rationales = [hook_rationale] + body_rationales
            
            self.logger.info(
                f"Caption generation completed: "
                f"1 hook + {len(body_texts)} body captions"
            )
            
            return TextGeneratorOutput(
                step_name="text_generator",
                success=True,
                hook_slide_text=hook_text,
                body_slides_text=body_texts,
                captions_rationale=all_rationales,
            )
            
        except AnthropicServiceError as e:
            raise ExecutionError(f"Text generation service error: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error during text generation: {str(e)}")
    
    async def _generate_caption(
        self,
        input_data: TextGeneratorInput,
        story: str,
        is_hook: bool,
    ) -> tuple[str, str]:
        """
        Generate short, punchy caption from verbose story narrative.
        
        Args:
            input_data: Full input data for context
            story: The story for this slide
            is_hook: Whether this is the hook slide
            
        Returns:
            Tuple of (caption, rationale)
            
        Raises:
            ExecutionError: If generation fails
        """
        try:
            system_prompt = self._build_system_prompt(input_data.format_type, is_hook)
            user_prompt = self._build_user_prompt(
                complete_story=input_data.complete_story,
                slide_story=story,
                is_hook=is_hook
            )
            
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            self.logger.debug(f"Generating caption for {'hook' if is_hook else 'body'} slide")
            
            # Call Claude with structured output for guaranteed valid response
            text_output = await self.anthropic.generate_structured_output(
                prompt=full_prompt,
                output_model=ClaudeTextOutput,
                max_tokens=4096,
                temperature=0.9,
            )
            
            caption = text_output.caption.strip()
            
            self.logger.debug(
                f"Generated caption ({len(caption)} chars): {caption}"
            )
            
            return caption, text_output.rationale.strip()
            
        except AnthropicServiceError as e:
            raise ExecutionError(f"Failed to generate caption: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error in caption generation: {str(e)}")
    
    def _build_system_prompt(self, format_type: str, is_hook: bool) -> str:
        """
        Build system prompt for caption generation.
        
        Args:
            format_type: The carousel format type
            is_hook: Whether this is the hook slide
            
        Returns:
            System prompt string
        """
        caption_guide = FORMAT_CAPTION_GUIDES.get(format_type)
        
        slide_context = "HOOK (First Slide): Pattern interrupt. Stop scroll. Create curiosity." if is_hook else "BODY: Deliver value. Build on narrative flow."
        
        return f"""Expert carousel caption writer for Instagram/TikTok. Create captions optimized for each format's needs.

FORMAT: {format_type}
CAPTION APPROACH: {caption_guide}

SLIDE TYPE: {slide_context}

CAPTION PRINCIPLES:
- Length serves purpose: short for impact, long for clarity, minimal when visuals lead
- Format-appropriate tone
- Each caption serves the slide's specific role
- Front-load key information

OUTPUT:
- caption: Length determined by format needs and slide purpose
- rationale: Why this caption works for this format"""
    
    def _build_user_prompt(self, complete_story: str, slide_story: str, is_hook: bool) -> str:
        """
        Build user prompt for caption generation.
        
        Args:
            complete_story: The complete carousel story for context
            slide_story: The story for this slide
            is_hook: Whether this is the hook slide
            
        Returns:
            User prompt string
        """
        return f"""COMPLETE STORY (context):
"{complete_story}"

SLIDE STORY (focus):
"{slide_story}"

Generate caption:
1. Use COMPLETE STORY for narrative flow and positioning
2. Use SLIDE STORY for this slide's specific message
3. Match format's caption approach
4. Determine optimal length for this slide's purpose
5. {'Hook: Create curiosity, preview value' if is_hook else 'Body: Deliver insight, maintain momentum'}"""


text_generator = TextGenerator()