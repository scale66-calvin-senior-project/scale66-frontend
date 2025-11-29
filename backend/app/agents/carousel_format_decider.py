"""
Carousel Format Decider Agent - Step 2 of AI Pipeline

Analyzes user content request and brand context to determine optimal carousel format.

Input: CarouselFormatDeciderInput (user_prompt, brand_kit)
Output: CarouselFormatDeciderOutput (format_type, num_slides, format_rationale)
"""

from typing import Dict, List, Optional
from enum import Enum

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import CarouselFormatDeciderInput, CarouselFormatDeciderOutput
from app.models.structured import ClaudeFormatDecisionOutput
from app.services.ai.anthropic_service import AnthropicServiceError


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
    Singleton pattern ensures single instance across application.
    """
    
    _instance: Optional['CarouselFormatDecider'] = None
    
    def __new__(cls):
        """Singleton instance creation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize carousel format decider agent."""
        super().__init__()
    
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
            
            self.logger.debug(f"Requesting format decision from Claude")
            
            # Call Claude with structured output for guaranteed valid response
            format_output = await self.anthropic.generate_structured_output(
                prompt=full_prompt,
                output_model=ClaudeFormatDecisionOutput,
                max_tokens=1000,
                temperature=0.3,
            )
            
            self.logger.debug(
                f"Format decision: {format_output.format_type} "
                f"({format_output.num_slides} slides)"
            )
            
            return CarouselFormatDeciderOutput(
                step_name="carousel_format_decider",
                success=True,
                format_type=format_output.format_type,
                num_slides=format_output.num_slides,
                format_rationale=format_output.format_rationale,
            )
            
        except AnthropicServiceError as e:
            raise ExecutionError(f"LLM service error: {str(e)}")
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

OUTPUT REQUIREMENTS:
- format_type: One of the format values from above
- num_slides: Integer between 3 and 10
- format_rationale: 2-3 sentence explanation of why this format works best for this content and brand"""
    
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

Based on this content request and brand context, recommend the optimal carousel format that will drive maximum engagement."""


# Create singleton instance for easy import
carousel_format_decider = CarouselFormatDecider()