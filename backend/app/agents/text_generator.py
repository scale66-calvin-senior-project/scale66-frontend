"""
Text Generator Agent - Step 5 of AI Pipeline

Generates on-screen text overlays and styling for carousel slides based on story content and image analysis.

Input: TextGeneratorInput (hook_slide_story, body_slides_story, hook_slide_image, body_slides_images)
Output: TextGeneratorOutput (hook_slide_text, body_slides_text, hook_slide_text_style, body_slides_text_styles)
"""

import json
import logging
from typing import Dict, List

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import TextGeneratorInput, TextGeneratorOutput
from app.services.ai.anthropic_service import AnthropicServiceError


logger = logging.getLogger(__name__)


class TextGenerator(BaseAgent[TextGeneratorInput, TextGeneratorOutput]):
    """
    Generates text overlays and styling for carousel slides.
    
    Uses Claude Sonnet 4.5 for text generation and Claude Vision for image analysis
    to create optimal text placement and styling.
    """
    
    async def _validate_input(self, input_data: TextGeneratorInput) -> None:
        """
        Validate input data before execution.
        
        Checks:
        - Hook slide story and image are not empty
        - Body slides stories and images arrays match in length
        - All stories and images are valid
        
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
        
        # Validate hook_slide_image
        if not input_data.hook_slide_image or not input_data.hook_slide_image.strip():
            raise ValidationError("hook_slide_image cannot be empty")
        
        # Validate body_slides_story
        if not input_data.body_slides_story:
            raise ValidationError("body_slides_story cannot be empty")
        
        if not isinstance(input_data.body_slides_story, list):
            raise ValidationError("body_slides_story must be a list")
        
        if len(input_data.body_slides_story) < 2:
            raise ValidationError("body_slides_story must contain at least 2 slides")
        
        if len(input_data.body_slides_story) > 9:
            raise ValidationError("body_slides_story cannot contain more than 9 slides")
        
        # Validate body_slides_images
        if not input_data.body_slides_images:
            raise ValidationError("body_slides_images cannot be empty")
        
        if not isinstance(input_data.body_slides_images, list):
            raise ValidationError("body_slides_images must be a list")
        
        # Check array length match
        if len(input_data.body_slides_story) != len(input_data.body_slides_images):
            raise ValidationError(
                f"body_slides_story ({len(input_data.body_slides_story)}) and "
                f"body_slides_images ({len(input_data.body_slides_images)}) must have the same length"
            )
        
        # Validate each body slide story
        for i, story in enumerate(input_data.body_slides_story):
            if not story or not isinstance(story, str) or not story.strip():
                raise ValidationError(f"body_slides_story[{i}] is empty or invalid")
            
            if len(story.strip()) < 5:
                raise ValidationError(
                    f"body_slides_story[{i}] must be at least 5 characters"
                )
        
        # Validate each body slide image
        for i, image in enumerate(input_data.body_slides_images):
            if not image or not isinstance(image, str) or not image.strip():
                raise ValidationError(f"body_slides_images[{i}] is empty or invalid")
        
        self.logger.debug("Input validation passed")
    
    async def _execute(self, input_data: TextGeneratorInput) -> TextGeneratorOutput:
        """
        Execute text generation logic using Claude Sonnet 4.5 and Claude Vision.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Generated text overlays with styling information
            
        Raises:
            ExecutionError: If text generation fails
        """
        try:
            total_slides = 1 + len(input_data.body_slides_story)
            self.logger.info(f"Generating text overlays for {total_slides} slides")
            
            # Generate hook slide text and style
            self.logger.info("Generating hook slide text")
            hook_result = await self._generate_slide_text(
                story=input_data.hook_slide_story,
                image_base64=input_data.hook_slide_image,
                is_hook=True,
            )
            
            # Generate body slides text and styles
            body_texts: List[str] = []
            body_styles: List[str] = []
            
            for i, (story, image) in enumerate(zip(
                input_data.body_slides_story,
                input_data.body_slides_images
            )):
                self.logger.info(f"Generating body slide {i+1}/{len(input_data.body_slides_story)}")
                body_result = await self._generate_slide_text(
                    story=story,
                    image_base64=image,
                    is_hook=False,
                )
                body_texts.append(body_result["text"])
                body_styles.append(body_result["style"])
            
            self.logger.info(
                f"Text generation completed successfully: "
                f"1 hook + {len(body_texts)} body texts with styling"
            )
            
            return TextGeneratorOutput(
                hook_slide_text=hook_result["text"],
                body_slides_text=body_texts,
                hook_slide_text_style=hook_result["style"],
                body_slides_text_styles=body_styles,
            )
            
        except AnthropicServiceError as e:
            raise ExecutionError(f"Text generation service error: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error during text generation: {str(e)}")
    
    async def _generate_slide_text(
        self,
        story: str,
        image_base64: str,
        is_hook: bool,
    ) -> Dict[str, str]:
        """
        Generate text overlay and styling for a single slide using Claude Vision.
        
        Args:
            story: The story content for this slide
            image_base64: Base64 encoded image
            is_hook: Whether this is the hook slide
            
        Returns:
            Dictionary with 'text' and 'style' keys
            
        Raises:
            ExecutionError: If generation fails
        """
        try:
            # Build comprehensive prompt
            system_prompt = self._build_system_prompt(is_hook)
            user_prompt = self._build_user_prompt(story, is_hook)
            
            # Combine prompts for API call
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Convert base64 image to data URL format for Claude Vision
            image_data_url = f"data:image/png;base64,{image_base64}"
            
            self.logger.debug(f"Analyzing image and generating text for {'hook' if is_hook else 'body'} slide")
            
            # Call Claude Vision with image analysis
            response = await self.anthropic.analyze_image(
                image_url=image_data_url,
                prompt=full_prompt,
                max_tokens=1000,
            )
            
            # Parse and validate response
            result = self._parse_response(response)
            
            self.logger.debug(
                f"Generated text ({len(result['text'])} chars) with style: {result['style'][:50]}..."
            )
            
            return result
            
        except AnthropicServiceError as e:
            raise ExecutionError(f"Failed to generate slide text: {str(e)}")
        except json.JSONDecodeError as e:
            raise ExecutionError(f"Failed to parse text generation response: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error in slide text generation: {str(e)}")
    
    def _build_system_prompt(self, is_hook: bool) -> str:
        """
        Build comprehensive system prompt for text generation.
        
        Args:
            is_hook: Whether this is the hook slide
            
        Returns:
            System prompt string
        """
        slide_type = "HOOK SLIDE (First Slide)" if is_hook else "BODY SLIDE"
        
        return f"""You are an expert social media designer specializing in carousel text overlays for Instagram and TikTok. Your role is to analyze images and create compelling, readable text overlays that enhance engagement.

CONTEXT: {slide_type}

TEXT OVERLAY PRINCIPLES:

1. TEXT CONTENT:
   - CRITICAL: Text should ENHANCE the story, not repeat it verbatim
   - Extract the KEY INSIGHT or MAIN POINT from the story (3-8 words ideal)
   - Use power words and emotional triggers
   - Create curiosity or reinforce value proposition
   {'''   - Hook slides: Bold, attention-grabbing statement (e.g., "Stop Scrolling If...")
   - Must create pattern interrupt and curiosity''' if is_hook else '''   - Body slides: Actionable insights or key takeaways
   - Can use numbers, questions, or direct statements'''}
   - Avoid full sentences if possible - punch, don't prose
   - Maximum 10 words (ideal 3-6 words)

2. READABILITY REQUIREMENTS:
   - Must be instantly readable in <1 second on mobile
   - High contrast with background (analyze image composition)
   - Large enough for mobile viewing
   - No fancy fonts that compromise legibility
   - Strategic placement based on image composition

3. IMAGE ANALYSIS:
   - Identify key visual elements and focal points
   - Determine optimal text placement zones (top/center/bottom)
   - Ensure text doesn't obscure important visual elements
   - Consider negative space for text placement
   - Account for busy vs clean backgrounds

4. STYLING SPECIFICATIONS:
   - Font size: Describe as percentage of slide height (e.g., "20% height")
   - Color: Specific hex code or high-contrast description
   - Position: top/center/bottom based on image composition
   - Alignment: left/center/right based on visual balance
   - Background: Transparent overlay if needed (rgba specification)
   - Text effects: Shadow, outline, or backdrop for visibility

5. SOCIAL MEDIA OPTIMIZATION:
   - Mobile-first design (vertical 9:16 format)
   - Thumb-stopping visual hierarchy
   - Save-worthy or share-worthy appeal
   - Platform native aesthetic (Instagram/TikTok style)

OUTPUT FORMAT:
You must respond with ONLY a valid JSON object in this exact format:
{{
  "text": "<3-10 word overlay text>",
  "style": "<complete styling specification>"
}}

STYLE FORMAT EXAMPLE:
"font_size: 18% of slide height, color: #FFFFFF, position: top-center, alignment: center, background: rgba(0,0,0,0.4), text_shadow: 2px 2px 4px rgba(0,0,0,0.8), padding: 20px"

CRITICAL REQUIREMENTS:
- Text must be 3-10 words maximum
- Style must include: font_size, color, position, alignment
- Analyze the image carefully to determine optimal placement
- Ensure high contrast for readability
- Do not include any text outside the JSON object
- Do not use markdown code blocks"""
    
    def _build_user_prompt(self, story: str, is_hook: bool) -> str:
        """
        Build user prompt with story content and task.
        
        Args:
            story: The story content for this slide
            is_hook: Whether this is the hook slide
            
        Returns:
            User prompt string
        """
        slide_type = "hook" if is_hook else "body"
        
        return f"""SLIDE STORY CONTENT:
"{story}"

TASK:
Analyze the provided image and create an optimal text overlay for this {slide_type} slide.

STEPS:
1. Examine the image composition (focal points, negative space, color distribution)
2. Identify the best text placement zone that doesn't obscure key visual elements
3. Extract the core message from the story (3-10 words maximum)
4. Determine styling that ensures high contrast and readability
5. Provide complete styling specifications for the Finalizer agent

Remember: The text should complement and enhance the story, not duplicate it. Focus on the KEY INSIGHT or HOOK that will stop the scroll and drive engagement.

Return your text and styling as a JSON object."""
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        """
        Parse and validate LLM response.
        
        Extracts JSON from response and validates text and style.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Validated text and style dictionary
            
        Raises:
            ExecutionError: If response is invalid
        """
        # Clean response - remove potential markdown code blocks
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        # Parse JSON
        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                result = json.loads(cleaned[start_idx:end_idx])
            else:
                raise ExecutionError("No valid JSON found in response")
        
        # Validate required fields
        if "text" not in result:
            raise ExecutionError("Missing 'text' in response")
        if "style" not in result:
            raise ExecutionError("Missing 'style' in response")
        
        # Validate text
        text = result["text"]
        if not text or not isinstance(text, str) or not text.strip():
            raise ExecutionError("text must be a non-empty string")
        
        # Check text length
        text_stripped = text.strip()
        word_count = len(text_stripped.split())
        
        if word_count > 15:
            self.logger.warning(
                f"Text is too long ({word_count} words), truncating to first 10 words"
            )
            words = text_stripped.split()[:10]
            result["text"] = " ".join(words)
        
        if len(text_stripped) < 3:
            self.logger.warning(f"Text is very short ({len(text_stripped)} chars)")
        
        # Validate style
        style = result["style"]
        if not style or not isinstance(style, str) or not style.strip():
            self.logger.warning("Style is empty or invalid, using default")
            result["style"] = (
                "font_size: 16% of slide height, color: #FFFFFF, "
                "position: center, alignment: center, "
                "background: rgba(0,0,0,0.3), "
                "text_shadow: 2px 2px 4px rgba(0,0,0,0.8)"
            )
        
        # Basic validation that style contains key properties
        required_style_props = ["font_size", "color", "position"]
        missing_props = [
            prop for prop in required_style_props
            if prop not in result["style"].lower()
        ]
        
        if missing_props:
            self.logger.warning(
                f"Style missing properties: {', '.join(missing_props)}. "
                f"Finalizer may need to infer defaults."
            )
        
        return result


# Create singleton instance for easy import
text_generator = TextGenerator()