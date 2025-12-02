"""
Strategy Generator Agent - Step 3 of AI Pipeline

Input: StrategyGeneratorInput (format_type, num_slides, brand_kit, user_prompt)
Output: StrategyGeneratorOutput (complete_strategy, hook_slide_strategy, body_slides_strategy)
"""

from typing import Dict, List, Optional

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import StrategyGeneratorInput, StrategyGeneratorOutput
from app.models.structured import ClaudeStoryOutput
from app.agents.carousel_format_decider import CarouselFormat
from app.services.ai.anthropic_service import AnthropicServiceError


# Format-specific strategies defining HOW to construct slide guidance
FORMAT_STRATEGY_GUIDES: Dict[str, str] = {
    CarouselFormat.LISTICLE_TIPS: """Strategic framework for a numbered tips/insights carousel.

STRATEGIC PLAN COMPONENTS:
- Define the strategic purpose and value
- Describe WHY each slide exists and what role it plays
- Provide directional guidance for Text Generator and Image Generator
- Focus on INTENT and OBJECTIVES, not content

COMPLETE STRATEGY STRUCTURE:
The complete strategy should capture:
1. The core value proposition (what problem does this solve?)
2. The target audience and their mindset (who is this for?)
3. The overall objective (educate, inspire action, build trust, etc.)

HOOK SLIDE STRATEGY:
- Define what the hook should signal and to whom
- Describe the promise being made (numbered expectation: "X ways to...")
- Explain why this approach works for the target audience
- NO actual hook text - just strategic direction

BODY SLIDE STRATEGY (per slide):
- Describe what type of content belongs here
- Explain why this position in the sequence matters
- Note any special characteristics (e.g., "most surprising insight", "obvious but often forgotten")
- NO actual tip content - just strategic direction

GOOD EXAMPLE:
Complete Strategy: "This carousel provides actionable social media tips for overwhelmed small business owners who view social media as a time sink. Tips range from dead-simple daily habits (posting consistently) to more strategic investments (content batching, engagement strategies). The objective is to make social media feel approachable and manageable, not overwhelming. Each tip should feel like a small win they can implement today."

Hook Strategy: "The hook targets time-strapped business owners with a clear numbered promise. It signals 'no fluff, just actionable steps' through clean visuals and direct language. The number creates completionist drive - they'll want all X tips."

Slide 1 Strategy: "First tip should be the easiest quick-win - something they can do in 5 minutes today. This builds momentum and trust. The insight should feel obvious but have a slight twist in framing that makes it memorable."

Slide 2 Strategy: "Second tip focuses on a slightly more complex topic - still actionable but requires a bit more thought. Builds on the confidence from tip 1."

[More slides here...]""",
}


class StrategyGenerator(BaseAgent[StrategyGeneratorInput, StrategyGeneratorOutput]):
    """
    Generates strategic guidance for carousel slides based on format and brand.
    
    Provides directional strategy (WHY and PURPOSE) for downstream agents,
    NOT actual slide content. Uses Claude Sonnet 4.5 for strategic planning.
    Singleton pattern ensures single instance across application.
    """
    
    _instance: Optional['StrategyGenerator'] = None
    
    def __new__(cls):
        """Singleton instance creation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize strategy generator agent."""
        super().__init__()
    
    async def _validate_input(self, input_data: StrategyGeneratorInput) -> None:
        """
        Validate input data before execution.
        
        Checks:
        - Format type is valid CarouselFormat enum value
        - Number of slides is in valid range (3-10)
        - Brand kit is complete with required fields
        - User prompt is not empty and has minimum length
        
        Args:
            input_data: Strategy generator input schema
            
        Raises:
            ValidationError: If input is invalid
        """
        # Validate format_type
        if not input_data.format_type:
            raise ValidationError("format_type is required")
        
        valid_formats = [fmt.value for fmt in CarouselFormat]
        if input_data.format_type not in valid_formats:
            raise ValidationError(
                f"Invalid format_type '{input_data.format_type}'. "
                f"Must be one of: {', '.join(valid_formats)}"
            )
        
        # Validate num_slides
        if input_data.num_slides < 3 or input_data.num_slides > 10:
            raise ValidationError(
                f"num_slides must be between 3 and 10, got {input_data.num_slides}"
            )
        
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
    
    async def _execute(self, input_data: StrategyGeneratorInput) -> StrategyGeneratorOutput:
        """
        Execute strategy generation logic using Claude Sonnet 4.5.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Strategy content with hook and body slides
            
        Raises:
            ExecutionError: If LLM call fails or response is invalid
        """
        try:
            # Build comprehensive prompt
            system_prompt = self._build_system_prompt(input_data)
            user_prompt = self._build_user_prompt(input_data)
            
            # Combine prompts for API call
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            self.logger.debug(
                f"Generating strategy for format '{input_data.format_type}' "
                f"with {input_data.num_slides} slides"
            )
            
            # Log the format structure being used
            format_structure = FORMAT_STRATEGY_GUIDES.get(
                input_data.format_type,
                "Hook: Attention-grabbing opening. Body: Sequential content delivery."
            )
            self.logger.info(f"Format Structure: {format_structure}")
            
            # Call Claude with structured output for guaranteed valid response
            strategy_output = await self.anthropic.generate_structured_output(
                prompt=full_prompt,
                output_model=ClaudeStoryOutput,
                max_tokens=3000,
                temperature=0.7,
            )
            
            # Validate body slide count
            expected_body_count = input_data.num_slides - 1
            actual_body_count = len(strategy_output.body_slides_strategy)
            
            if actual_body_count != expected_body_count:
                self.logger.warning(
                    f"Expected {expected_body_count} body slides, got {actual_body_count}. "
                    f"Adjusting to match expected count."
                )
                
                # Handle array length mismatch
                if actual_body_count < expected_body_count:
                    while len(strategy_output.body_slides_strategy) < expected_body_count:
                        strategy_output.body_slides_strategy.append("[Content continues...]")
                else:
                    # Too many slides - truncate
                    strategy_output.body_slides_strategy = strategy_output.body_slides_strategy[:expected_body_count]
            
            self.logger.info(
                f"Strategy generated: hook + {len(strategy_output.body_slides_strategy)} body slides"
            )
            
            return StrategyGeneratorOutput(
                step_name="strategy_generator",
                success=True,
                complete_strategy=strategy_output.complete_strategy,
                complete_strategy_rationale=strategy_output.complete_strategy_rationale,
                hook_slide_strategy=strategy_output.hook_slide_strategy,
                body_slides_strategy=strategy_output.body_slides_strategy,
            )
            
        except AnthropicServiceError as e:
            raise ExecutionError(f"LLM service error: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error during execution: {str(e)}")
    
    def _build_system_prompt(self, input_data: StrategyGeneratorInput) -> str:
        """
        Build comprehensive system prompt with format-specific guidance.
        
        Args:
            input_data: Input data containing format type
            
        Returns:
            System prompt string
        """
        # Get format-specific structure
        format_structure = FORMAT_STRATEGY_GUIDES.get(
            input_data.format_type,
            "Provide strategic guidance for each slide's purpose and role in the carousel."
        )
        
        return f"""You are an expert social media content strategist who creates STRATEGIC PLANS for carousel creation.

YOUR OUTPUT CHARACTERISTICS:
- Abstract and directional, not concrete and prescriptive
- Focuses on PURPOSE and APPROACH
- Guides without constraining
- No character names, no specific statistics, no quotes, no dialogue

CRITICAL RULES:

1. You provide STRATEGIC DIRECTION, not content. Your output guides downstream agents (Text Generator, Image Generator) - you do NOT write the actual slide content.

2. You define PURPOSE and APPROACH, not narrative. You specify WHY each slide exists and what role it plays, not WHAT text or visuals appears on it.

3. ABSOLUTELY PROHIBITED - these patterns will cause pipeline failure:
   - Fictional characters or names ("Sarah opened her laptop...", "John's agency...")
   - Specific numbers or statistics ("Revenue up 240%", "47k followers", "200 likes")
   - Dialogue or quotes ("She said: '...'", "A customer told her...")
   - Actual slide text or captions (ready-to-use content)
   - Narrative/storytelling style (mini-sentences, plot progression)
   - Visual style descriptions (photorealistic, abstract, minimalist)

4. Your output should be ABSTRACT and DIRECTIONAL:
   - Describe the purpose, not the content
   - Explain the approach, not the execution
   - Guide without constraining
   - Focus on WHY, leave WHAT to downstream agents

---

STRATEGIC FRAMEWORK FOR '{input_data.format_type}':
{format_structure}

---

HOW TO USE THIS FRAMEWORK:
1. The STRATEGIC FRAMEWORK above shows how to structure guidance for this format type.
2. Follow the GOOD EXAMPLE pattern - abstract, directional, purpose-focused.
3. Match your output style to the examples provided.

VALUE ARC PRINCIPLE:
Each carousel should have a clear value progression:
1. ENTRY POINT: What draws the target audience in? What promise is made?
2. VALUE DELIVERY: How does each slide deliver value to the target audience?
3. CULMINATION: What does the reader walk away with? What action or mindset shift?

OUTPUT REQUIREMENTS:

[PIPELINE OUTPUT - Required for downstream agents]
- complete_strategy: The overarching strategic plan for the entire carousel (200-400 chars). Describes WHO this is for, WHAT value it provides, and HOW it progresses.
- hook_slide_strategy: Strategic direction for the hook slide (100-200 chars). Describes what the hook should ACCOMPLISH, not what it should SAY.
- body_slides_strategy: Exactly {input_data.num_slides - 1} strategic guidance entries (each 100-200 chars). Each describes the ROLE and PURPOSE of that slide position.

[RATIONALE OUTPUT - For debugging/tuning]
- complete_strategy_rationale: Why this strategic approach works for this format and brand (100-200 chars)

REMEMBER: You are providing a BLUEPRINT, not a DRAFT. Text Generator creates the words. Image Generator creates the visuals. You define the strategy that guides them both."""
    
    def _build_user_prompt(self, input_data: StrategyGeneratorInput) -> str:
        """
        Build user prompt with content request and brand context.
        
        Args:
            input_data: Input data with format, brand, and user request
            
        Returns:
            User prompt string
        """
        brand_kit = input_data.brand_kit
        body_slide_count = input_data.num_slides - 1
        pain_points = ", ".join(brand_kit.customer_pain_points) if brand_kit.customer_pain_points else "Not provided"
        
        return f"""CONTENT REQUEST:
"{input_data.user_prompt}"

CAROUSEL SPECIFICATIONS:
- Format Type: {input_data.format_type}
- Total Slides: {input_data.num_slides} (1 hook + {body_slide_count} body slides)

BRAND CONTEXT:
- Brand Name: {brand_kit.brand_name}
- Brand Niche: {brand_kit.brand_niche}
- Brand Style: {brand_kit.brand_style}
- Customer Pain Points: {pain_points}
- Product/Service Description: {brand_kit.product_service_desc}

Based on this content request, carousel specifications, and brand context, create a strategic plan for this carousel."""


# Create singleton instance for easy import
strategy_generator = StrategyGenerator()

