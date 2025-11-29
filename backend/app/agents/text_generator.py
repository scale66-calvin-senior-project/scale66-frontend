"""
Text Generator Agent - Step 4 of AI Pipeline

Converts verbose story narratives into short, punchy carousel captions.

Runs BEFORE image generation - no image analysis needed.
Pure text transformation: detailed story → concise caption (3-8 words ideal).

Input: TextGeneratorInput (hook_slide_story, body_slides_story)
Output: TextGeneratorOutput (hook_slide_text, body_slides_text)
"""

from typing import List, Optional

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import TextGeneratorInput, TextGeneratorOutput
from app.models.structured import ClaudeTextOutput
from app.services.ai.anthropic_service import AnthropicServiceError


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
        - Hook slide story is not empty
        - Body slides stories array is valid and within limits
        - All story strings are valid
        
        Args:
            input_data: Text generator input schema
            
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
        Execute text generation logic using Claude Sonnet 4.5.
        
        Converts verbose story narratives into short, punchy carousel captions.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Generated short captions (no styling)
            
        Raises:
            ExecutionError: If text generation fails
        """
        try:
            total_slides = 1 + len(input_data.body_slides_story)
            self.logger.debug(f"Generating captions for {total_slides} slides")
            
            # Generate hook slide caption
            self.logger.debug("Generating hook slide caption")
            hook_text, hook_rationale = await self._generate_caption(
                story=input_data.hook_slide_story,
                is_hook=True,
            )
            
            # Generate body slides captions
            body_texts: List[str] = []
            body_rationales: List[str] = []
            
            for i, story in enumerate(input_data.body_slides_story):
                self.logger.debug(f"Generating body slide {i+1}/{len(input_data.body_slides_story)}")
                body_text, body_rationale = await self._generate_caption(
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
            self.logger.info("Caption Rationales:")
            self.logger.info(f"  [0] Hook: {hook_rationale}")
            for i, rationale in enumerate(body_rationales, 1):
                self.logger.info(f"  [{i}] Body {i}: {rationale}")
            
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
        story: str,
        is_hook: bool,
    ) -> tuple[str, str]:
        """
        Generate short, punchy caption from verbose story narrative.
        
        Args:
            story: The verbose story content for this slide
            is_hook: Whether this is the hook slide
            
        Returns:
            Tuple of (caption, rationale)
            
        Raises:
            ExecutionError: If generation fails
        """
        try:
            # Build comprehensive prompt
            system_prompt = self._build_system_prompt(is_hook)
            user_prompt = self._build_user_prompt(story, is_hook)
            
            # Combine prompts for API call
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            self.logger.debug(f"Generating caption for {'hook' if is_hook else 'body'} slide")
            
            # Call Claude with structured output for guaranteed valid response
            text_output = await self.anthropic.generate_structured_output(
                prompt=full_prompt,
                output_model=ClaudeTextOutput,
                max_tokens=500,
                temperature=0.7,
            )
            
            # Validate caption length
            caption = text_output.caption.strip()
            word_count = len(caption.split())
            
            if word_count > 12:
                self.logger.warning(
                    f"Caption is too long ({word_count} words), truncating to first 10 words"
                )
                words = caption.split()[:10]
                caption = " ".join(words)
            
            if len(caption) < 3:
                self.logger.warning(f"Caption is very short ({len(caption)} chars)")
            
            if word_count > 10:
                self.logger.warning(f"Caption exceeds ideal length ({word_count} words, ideal 3-8)")
            
            self.logger.debug(
                f"Generated caption ({len(caption)} chars): {caption}"
            )
            
            return caption, text_output.rationale.strip()
            
        except AnthropicServiceError as e:
            raise ExecutionError(f"Failed to generate caption: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error in caption generation: {str(e)}")
    
    def _build_system_prompt(self, is_hook: bool) -> str:
        """
        Build comprehensive system prompt for caption generation.
        
        Args:
            is_hook: Whether this is the hook slide
            
        Returns:
            System prompt string
        """
        slide_type = "HOOK SLIDE (First Slide)" if is_hook else "BODY SLIDE"
        
        return f"""You are an expert social media content creator specializing in viral carousel posts for Instagram and TikTok. Your role is to extract short, punchy captions from verbose story narratives.

CONTEXT: {slide_type}

CAPTION EXTRACTION PRINCIPLES:

1. TEXT BREVITY:
   - Extract the KEY INSIGHT or MAIN POINT from the story
   - Target: 3-8 words (absolute maximum 10 words)
   - Use power words and emotional triggers
   - Create curiosity or reinforce value proposition
   {'''   - Hook slides: Bold, attention-grabbing statement (e.g., "Done By 9 AM", "Stop Scrolling If...")
   - Must create pattern interrupt and curiosity
   - Preview value without giving everything away''' if is_hook else '''   - Body slides: Actionable insights or key takeaways
   - Can use numbers, questions, or direct statements
   - Each caption should standalone'''}

2. CAPTION QUALITY:
   - Avoid full sentences - use punchy phrases
   - Be specific, not generic
   - Cut filler words ruthlessly
   - Front-load key information
   - Must be instantly readable in <1 second on mobile

3. SOCIAL MEDIA OPTIMIZATION:
   - Mobile-first thinking (vertical 9:16 format)
   - Thumb-stopping appeal
   - Save-worthy or share-worthy phrasing
   - Platform native aesthetic (Instagram/TikTok style)

4. EXTRACTION STRATEGY:
   - Read the full story narrative
   - Identify the core message/insight
   - Distill into shortest possible form
   - Preserve emotional impact and clarity
   - Ensure caption enhances (not duplicates) the story

OUTPUT REQUIREMENTS:
- caption: Short, punchy caption (3-10 words maximum, ideal 3-8 words)
- rationale: Strategic explanation of why this caption works (50-150 characters)
- Extract essence, don't summarize

EXAMPLES:
Story: "Plan your tasks the night before so you wake up with zero decision fatigue and can take immediate action at dawn"
Output: caption="Plan Tonight, Win Tomorrow", rationale="Creates anticipation and implies immediate benefit with simple action-result pairing"

Story: "Do a 20-minute focused work sprint before checking email to get deep work done before distractions hit"
Output: caption="Deep Work Before Distractions", rationale="Establishes priority and sequence, using power words that resonate with productivity-focused audience"

Remember: The caption should ENHANCE the story, not duplicate it verbatim. Focus on the KEY INSIGHT or HOOK that will stop the scroll and drive engagement."""
    
    def _build_user_prompt(self, story: str, is_hook: bool) -> str:
        """
        Build user prompt with story content and task.
        
        Args:
            story: The verbose story content for this slide
            is_hook: Whether this is the hook slide
            
        Returns:
            User prompt string
        """
        slide_type = "hook" if is_hook else "body"
        
        return f"""VERBOSE STORY NARRATIVE:
"{story}"

TASK:
Extract a short, punchy caption from this {slide_type} slide story.

STEPS:
1. Read the full story narrative carefully
2. Identify the core message, key insight, or main point
3. Distill it into the shortest possible form (3-8 words ideal)
4. Ensure it's instantly readable and scroll-stopping
5. Preserve emotional impact and clarity
6. Provide a rationale explaining why your caption works

Remember: The caption should ENHANCE the story, not duplicate it verbatim. Focus on the KEY INSIGHT or HOOK that will stop the scroll and drive engagement."""


# Create singleton instance for easy import
text_generator = TextGenerator()