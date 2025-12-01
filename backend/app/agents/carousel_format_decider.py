"""
Carousel Format Decider Agent - Step 2 of AI Pipeline

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
    LISTICLE_TIPS = "listicle_tips"


# Format descriptions for LLM context
FORMAT_DESCRIPTIONS: Dict[str, str] = {
    CarouselFormat.LISTICLE_TIPS: """Numbered collection of discrete, standalone tips/insights, one per slide.

STRUCTURE: Numbered headline ("7 Ways to X") → one item per slide → bonus/CTA
CHARACTERISTICS: Scannable, save-worthy, satisfies completionist instinct
SLIDES: Depends on the number of tips/insights in the prompt

IDEAL FOR PROMPTS LIKE:
- "7 best habits before bed"
- "5 ways to grow social media quickly"
- "10 habits of successful people"
- "10 ways to grow brand awareness just starting out"

KEY CRITERIA (ALL must apply):
1. Content breaks into discrete, standalone items (each tip works independently)
2. Items are relatively unrelated to each other (no narrative thread required)
3. Natural numbered framing ("X ways to...", "X tips for...", "X mistakes...")
4. Each slide delivers complete value without needing other slides

NOT SUITABLE FOR:
- Sequential stories or journeys with a narrative arc
- Before/after transformations requiring context buildup
- Deep-dive explanations of a single concept
- Personal stories or case studies
- Content requiring progressive revelation""",
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
            
            # Log the selected format's description
            format_description = FORMAT_DESCRIPTIONS.get(format_output.format_type, "No description available")
            self.logger.info(f"Format Description: {format_description}")
            
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
            f"### {fmt.value}\n{desc}"
            for fmt, desc in FORMAT_DESCRIPTIONS.items()
        ])
        
        return f"""You are an expert social media marketing strategist with a critical eye for content-format fit.

CRITICAL RULES:

1. You MUST select a format_type from the AVAILABLE FORMATS list below. No other values are permitted.

2. The FORMAT DEFINITIONS below are your PRIMARY source of truth for what each format can and cannot do. Your general marketing knowledge is SECONDARY and should only fill gaps not covered by the definitions.

3. If a request is a poor fit for all available formats, select the CLOSEST fit and explain the mismatch in your rationale.

AVAILABLE FORMATS:
{format_list}

---

DECISION FRAMEWORK:

1. ANALYZE THE USER'S REQUEST
   - What type of content are they asking for?
   - Does it naturally break into discrete items, or is it a continuous narrative?
   - Is there an implied structure (list, story, comparison, etc.)?

2. EVALUATE FORMAT FIT AGAINST DEFINITIONS
   - Check EACH criterion in the format's "KEY CRITERIA" section
   - A format is a STRONG fit only if ALL criteria are met
   - A format is a WEAK fit if some criteria fail—note which ones
   - Compare all available formats and select the best match

3. HANDLE AMBIGUOUS REQUESTS
   - Some prompts could fit multiple formats
   - Note the ambiguity and suggest user clarify their intent

---

OUTPUT REQUIREMENTS:

[PIPELINE OUTPUT - Required for next stage]
- format_type: MUST be one of the exact format values listed above
- num_slides: Integer between 3 and 10 (follow format guidelines for selected format)

[RATIONALE OUTPUT - For prompt tuning only]
- format_rationale: 2-3 sentences explaining your decision:
  1. Which KEY CRITERIA from the format definition the content meets or fails
  2. Why this format is the best available fit (acknowledge if it's a weak fit)
  3. Any ambiguity that could benefit from user clarification"""
    
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

Based on this content request and brand context, recommend the optimal carousel format that captures the user's request and brand context."""


# Create singleton instance for easy import
carousel_format_decider = CarouselFormatDecider()