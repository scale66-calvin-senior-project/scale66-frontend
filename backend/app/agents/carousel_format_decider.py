"""
Carousel Format Decider Agent - Step 2 of AI Pipeline

Analyzes user content request and brand context to determine optimal carousel format.

Input: CarouselFormatDeciderInput (user_prompt, brand_kit)
Output: CarouselFormatDeciderOutput (format_type, num_slides, format_rationale)
"""

import json
import logging
from typing import Dict, List
from enum import Enum

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import CarouselFormatDeciderInput, CarouselFormatDeciderOutput
from app.services.ai.anthropic_service import AnthropicServiceError


logger = logging.getLogger(__name__)


class CarouselFormat(str, Enum):
    """Supported carousel formats optimized for social media engagement."""
    TOP_5 = "top_5"
    STORY_CASE_STUDY = "story_case_study"
    DECISION_TREE = "decision_tree"
    COMMON_MISTAKES = "common_mistakes"
    TRANSFORMATIVE_GRID = "transformative_grid"
    TUTORIAL = "tutorial"
    UNPOPULAR_OPINION = "unpopular_opinion"
    THIS_VS_THAT = "this_vs_that"
    CHECKLIST = "checklist"
    TIMELINE_JOURNEY = "timeline_journey"
    BEFORE_VS_AFTER = "before_vs_after"
    MYTH_VS_REALITY = "myth_vs_reality"


# Format descriptions for LLM context
FORMAT_DESCRIPTIONS: Dict[str, str] = {
    CarouselFormat.TOP_5: "Top 5 reasons/things/signs/mistakes in the product's niche. Great for quick, scannable content.",
    CarouselFormat.STORY_CASE_STUDY: "Hook with relatable problem → struggle → turning point → solution. Builds emotional connection.",
    CarouselFormat.DECISION_TREE: "Should you _____? Each slide asks a question, guiding towards solution. Interactive feel.",
    CarouselFormat.COMMON_MISTAKES: "Are you making these mistakes? How to avoid them. Problem-aware audience.",
    CarouselFormat.TRANSFORMATIVE_GRID: "Side-by-side comparisons on each slide. Visual contrast drives engagement.",
    CarouselFormat.TUTORIAL: "How to achieve _____ without THIS STRUGGLE. Step-by-step actionable guidance.",
    CarouselFormat.UNPOPULAR_OPINION: "Controversial take as the hook. Drives debate and shares.",
    CarouselFormat.THIS_VS_THAT: "Stop doing A, start doing B. Repeat through slides. Clear actionable shifts.",
    CarouselFormat.CHECKLIST: "The ultimate _____ checklist. Each slide is an item. Saves and shares.",
    CarouselFormat.TIMELINE_JOURNEY: "How I went from A to B. Personal transformation narrative.",
    CarouselFormat.BEFORE_VS_AFTER: "Show the struggle before and transformation after. Proof-driven.",
    CarouselFormat.MYTH_VS_REALITY: "Myth on one slide, reality on the next. Educational and corrective.",
}


class CarouselFormatDecider(BaseAgent[CarouselFormatDeciderInput, CarouselFormatDeciderOutput]):
    """
    Decides optimal carousel format based on content request and brand context.
    
    Uses Claude Sonnet 4.5 for intelligent format selection with structured output.
    """
    
    async def _validate_input(self, input_data: CarouselFormatDeciderInput) -> None:
        """
        Validate input data before execution.
        
        Checks:
        - User prompt is not empty and has minimum length
        - Brand kit is complete with required fields
        
        Args:
            input_data: Format decider input schema
            
        Raises:
            ValidationError: If input is invalid
        """
        # Validate user prompt
        if not input_data.user_prompt or not input_data.user_prompt.strip():
            raise ValidationError("user_prompt cannot be empty")
        
        if len(input_data.user_prompt.strip()) < 10:
            raise ValidationError("user_prompt must be at least 10 characters")
        
        # Validate brand kit
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
        
        self.logger.debug("Input validation passed")
    
    async def _execute(self, input_data: CarouselFormatDeciderInput) -> CarouselFormatDeciderOutput:
        """
        Execute format decision logic using Claude Sonnet 4.5.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Format decision with rationale
            
        Raises:
            ExecutionError: If LLM call fails or response is invalid
        """
        try:
            # Build comprehensive prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(input_data)
            
            # Combine prompts for API call
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            self.logger.info(f"Requesting format decision from Claude Sonnet 4.5")
            self.logger.debug(f"User prompt preview: {input_data.user_prompt[:100]}...")
            
            # Call Claude with lower temperature for consistent decisions
            response = await self.anthropic.generate_text(
                prompt=full_prompt,
                max_tokens=1000,
                temperature=0.3,
            )
            
            # Parse and validate response
            decision = self._parse_response(response)
            
            self.logger.info(
                f"Format decision: {decision['format_type']} "
                f"({decision['num_slides']} slides)"
            )
            
            return CarouselFormatDeciderOutput(
                step_name="carousel_format_decider",
                success=True,
                format_type=decision["format_type"],
                num_slides=decision["num_slides"],
                format_rationale=decision["format_rationale"],
            )
            
        except AnthropicServiceError as e:
            raise ExecutionError(f"LLM service error: {str(e)}")
        except json.JSONDecodeError as e:
            raise ExecutionError(f"Failed to parse LLM response: {str(e)}")
        except KeyError as e:
            raise ExecutionError(f"Missing required field in response: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error during execution: {str(e)}")
    
    def _build_system_prompt(self) -> str:
        """
        Build comprehensive system prompt with format descriptions.
        
        Returns:
            System prompt string
        """
        format_list = "\n".join([
            f"- {fmt.value}: {desc}"
            for fmt, desc in FORMAT_DESCRIPTIONS.items()
        ])
        
        return f"""You are an expert social media carousel format strategist. Your role is to analyze content requests and recommend the optimal carousel format that will maximize engagement on Instagram and TikTok.

AVAILABLE FORMATS:
{format_list}

YOUR TASK:
1. Analyze the user's content request
2. Consider the brand's industry, target audience, and tone
3. Select the format that best matches the content type and brand voice
4. Determine optimal slide count (3-10 slides based on content complexity)
5. Provide clear rationale for your decision

DECISION CRITERIA:
- Match format to content intent (educate, inspire, sell, entertain)
- Consider audience sophistication and attention span
- Align with brand tone (professional, playful, authoritative, etc.)
- Optimize for social media engagement patterns
- Simpler concepts = fewer slides (3-5), complex topics = more slides (6-10)

OUTPUT FORMAT:
You must respond with ONLY a valid JSON object in this exact format:
{{
  "format_type": "<one of the format values from above>",
  "num_slides": <integer between 3 and 10>,
  "format_rationale": "<2-3 sentence explanation of why this format works best>"
}}

Do not include any text outside the JSON object. Do not use markdown code blocks."""
    
    def _build_user_prompt(self, input_data: CarouselFormatDeciderInput) -> str:
        """
        Build user prompt with content request and brand context.
        
        Args:
            input_data: Input data with user prompt and brand kit
            
        Returns:
            User prompt string
        """
        brand_kit = input_data.brand_kit
        
        # Format customer pain points as a list
        pain_points = ", ".join(brand_kit.customer_pain_points) if brand_kit.customer_pain_points else "Not provided"
        
        return f"""CONTENT REQUEST:
"{input_data.user_prompt}"

BRAND CONTEXT:
- Brand Name: {brand_kit.brand_name}
- Brand Niche: {brand_kit.brand_niche}
- Brand Style: {brand_kit.brand_style}
- Customer Pain Points: {pain_points}
- Product/Service Description: {brand_kit.product_service_desc}

Based on this content request and brand context, recommend the optimal carousel format. Return your decision as a JSON object."""
    
    def _parse_response(self, response: str) -> Dict[str, any]:
        """
        Parse and validate LLM response.
        
        Extracts JSON from response and validates required fields.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Validated decision dictionary
            
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
            decision = json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                decision = json.loads(cleaned[start_idx:end_idx])
            else:
                raise ExecutionError("No valid JSON found in response")
        
        # Validate required fields
        if "format_type" not in decision:
            raise ExecutionError("Missing 'format_type' in response")
        if "num_slides" not in decision:
            raise ExecutionError("Missing 'num_slides' in response")
        if "format_rationale" not in decision:
            raise ExecutionError("Missing 'format_rationale' in response")
        
        # Validate format_type
        format_type = decision["format_type"]
        valid_formats = [fmt.value for fmt in CarouselFormat]
        if format_type not in valid_formats:
            self.logger.warning(
                f"Invalid format_type '{format_type}', defaulting to 'top_5'"
            )
            decision["format_type"] = CarouselFormat.TOP_5.value
        
        # Validate and clamp num_slides
        try:
            num_slides = int(decision["num_slides"])
            if num_slides < 3:
                self.logger.warning(f"num_slides {num_slides} too low, clamping to 3")
                num_slides = 3
            elif num_slides > 10:
                self.logger.warning(f"num_slides {num_slides} too high, clamping to 10")
                num_slides = 10
            decision["num_slides"] = num_slides
        except (ValueError, TypeError):
            self.logger.warning("Invalid num_slides, defaulting to 5")
            decision["num_slides"] = 5
        
        # Validate rationale
        rationale = decision["format_rationale"]
        if not rationale or not isinstance(rationale, str) or len(rationale.strip()) < 10:
            self.logger.warning("Invalid or missing rationale, generating default")
            decision["format_rationale"] = (
                f"Selected {decision['format_type']} format based on content analysis "
                f"and brand alignment."
            )
        
        return decision


# Create singleton instance for easy import
carousel_format_decider = CarouselFormatDecider()