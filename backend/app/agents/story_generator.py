"""
Story Generator Agent - Step 3 of AI Pipeline

Input: StoryGeneratorInput (format_type, num_slides, brand_kit, user_prompt)
Output: StoryGeneratorOutput (hook_slide_story, body_slides_story)
"""

from typing import Dict, List, Optional

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import StoryGeneratorInput, StoryGeneratorOutput
from app.models.structured import ClaudeStoryOutput
from app.agents.carousel_format_decider import CarouselFormat
from app.services.ai.anthropic_service import AnthropicServiceError


# Format-specific storytelling structures for each carousel type
FORMAT_STRUCTURES: Dict[str, str] = {
    CarouselFormat.EDUCATIONAL_TUTORIAL: "TONE: Clear, authoritative, value-driven. HOOK: Question/problem + promise ('How to [achieve X] without [pain]'). BODY: Sequential learning steps building to mastery. Each slide = ONE discrete concept/action (40-80 chars). Use imperative verbs (Do X, Start with Y, Focus on Z). Maintain instructional clarity - readers should finish with actionable knowledge. End with summary of transformation enabled.",
    
    CarouselFormat.TRANSFORMATION_SHOWCASE: "TONE: Emotional, inspirational, proof-driven. HOOK: Vulnerable 'before' state or bold result claim. BODY: Journey narrative arc - starting struggle → pivotal moments → incremental wins → dramatic after state. Emphasize CONTRAST at each stage. Use sensory details and emotional language. Include concrete metrics/proof points. Build toward aspirational endpoint. Readers should FEEL the transformation, not just see it.",
    
    CarouselFormat.LISTICLE_TIPS: "TONE: Punchy, scannable, immediately actionable. HOOK: Numbered promise ('7 Ways to [benefit]') creating expectation. BODY: One discrete, standalone tip per slide (50-100 chars). Each must deliver instant value without context from other slides. Use parallel structure across slides. Front-load the insight, then brief why/how. Prioritize density over depth. Readers should save for future reference.",
    
    CarouselFormat.PROBLEM_SOLUTION_PITCH: "TONE: Empathetic, persuasive, benefit-focused. HOOK: Pain point audience immediately recognizes. BODY: Amplify problem with specificity → introduce solution as natural answer → break down benefits/features → provide social proof/results → clear next step. Use 'you' language throughout. Address objections preemptively. Build trust through understanding their struggle before pitching. Conversion-oriented - every slide moves toward action.",
    
    CarouselFormat.DATA_INSIGHT_AUTHORITY: "TONE: Analytical, authoritative, insight-driven. HOOK: Bold/surprising statistic that challenges assumptions. BODY: Context for data → supporting data points visualized (one per slide) → implications/analysis → actionable conclusions. Use precise numbers, cite methodology where relevant. Translate data into meaning (what it reveals, why it matters). Professional language, avoid hype. Establish thought leadership through substantiated insights, not opinions.",
}


class StoryGenerator(BaseAgent[StoryGeneratorInput, StoryGeneratorOutput]):
    """
    Generates narrative content for carousel slides based on format and brand.
    
    Uses Claude Sonnet 4.5 for creative storytelling with brand voice alignment.
    Singleton pattern ensures single instance across application.
    """
    
    _instance: Optional['StoryGenerator'] = None
    
    def __new__(cls):
        """Singleton instance creation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize story generator agent."""
        super().__init__()
    
    async def _validate_input(self, input_data: StoryGeneratorInput) -> None:
        """
        Validate input data before execution.
        
        Checks:
        - Format type is valid CarouselFormat enum value
        - Number of slides is in valid range (3-10)
        - Brand kit is complete with required fields
        - User prompt is not empty and has minimum length
        
        Args:
            input_data: Story generator input schema
            
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
    
    async def _execute(self, input_data: StoryGeneratorInput) -> StoryGeneratorOutput:
        """
        Execute story generation logic using Claude Sonnet 4.5.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Story content with hook and body slides
            
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
                f"Generating story for format '{input_data.format_type}' "
                f"with {input_data.num_slides} slides"
            )
            
            # Call Claude with structured output for guaranteed valid response
            story_output = await self.anthropic.generate_structured_output(
                prompt=full_prompt,
                output_model=ClaudeStoryOutput,
                max_tokens=3000,
                temperature=0.7,
            )
            
            # Validate body slide count
            expected_body_count = input_data.num_slides - 1
            actual_body_count = len(story_output.body_slides_story)
            
            if actual_body_count != expected_body_count:
                self.logger.warning(
                    f"Expected {expected_body_count} body slides, got {actual_body_count}. "
                    f"Adjusting to match expected count."
                )
                
                # Handle array length mismatch
                if actual_body_count < expected_body_count:
                    while len(story_output.body_slides_story) < expected_body_count:
                        story_output.body_slides_story.append("[Content continues...]")
                else:
                    # Too many slides - truncate
                    story_output.body_slides_story = story_output.body_slides_story[:expected_body_count]
            
            self.logger.info(
                f"Story generated: hook + {len(story_output.body_slides_story)} body slides"
            )
            self.logger.info(f"Complete Story Rationale: {story_output.complete_story_rationale}")
            
            return StoryGeneratorOutput(
                step_name="story_generator",
                success=True,
                complete_story=story_output.complete_story,
                complete_story_rationale=story_output.complete_story_rationale,
                hook_slide_story=story_output.hook_slide_story,
                body_slides_story=story_output.body_slides_story,
            )
            
        except AnthropicServiceError as e:
            raise ExecutionError(f"LLM service error: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error during execution: {str(e)}")
    
    def _build_system_prompt(self, input_data: StoryGeneratorInput) -> str:
        """
        Build comprehensive system prompt with format-specific guidance.
        
        Args:
            input_data: Input data containing format type
            
        Returns:
            System prompt string
        """
        # Get format-specific structure
        format_structure = FORMAT_STRUCTURES.get(
            input_data.format_type,
            "Hook: Attention-grabbing opening. Body: Sequential content delivery."
        )
        
        return f"""You are an expert social media content creator specializing in carousel posts for Instagram and TikTok.

FORMAT STRUCTURE FOR '{input_data.format_type}':
{format_structure}

HOW TO USE FORMAT STRUCTURE:
1. The tone of the format structure is of paramount importance. DO NOT add emotion where knowledge is being conveyed, and vice versa.
2. The format structure gives an overall picture of the carousel, it is your job to fill in the details and creative a cohesive and engaging story.
3. Do not create captions or be too detailed about what goes into each carousel slide, focus primarly on the story and the flow of the carousel.

STORY LOOP PRINCIPLE:
Each carousel has multiple story loops with two parts:
1. OPENING (Context): Clear, understandable setup that triggers prediction
2. CLOSING (Reveal): Payoff that determines engagement

REVEAL OUTCOMES:
- Worse than expected → viewer tunes out
- Equal to expected → attention fades
- Better than expected → dopamine release, keeps engaging
- Unexpected but confusing → tunes out
- Unexpected but intriguing → dopamine release, keeps engaging

EXECUTION:
- Set clear context so viewer's brain predicts what's next
- Deliver reveals that are either BETTER than expected or INTRIGUING surprises
- Avoid generic/predictable payoffs (equal to expected)
- Chain story loops across slides to maintain momentum
- Each loop's reveal becomes context for the next loop
- The loops can be anywhere from 1 - 3 slides long.

OUTPUT REQUIREMENTS:
- complete_story: Cohesive narrative (200-400 chars) tying entire carousel together
- complete_story_rationale: Strategic explanation (100-200 chars)
- hook_slide_story: First slide opening the best compelling story loop (150-250 chars)
- body_slides_story: Exactly {input_data.num_slides - 1} body slides (each 150-250 chars)
- No slide numbers in content (don't write "Slide 1:", "Step 1:")"""
    
    def _build_user_prompt(self, input_data: StoryGeneratorInput) -> str:
        """
        Build user prompt with content request and brand context.
        
        Args:
            input_data: Input data with format, brand, and user request
            
        Returns:
            User prompt string
        """
        brand_kit = input_data.brand_kit
        
        # Calculate expected body slide count
        body_slide_count = input_data.num_slides - 1
        
        # Format customer pain points as a list
        pain_points = ", ".join(brand_kit.customer_pain_points) if brand_kit.customer_pain_points else "Not provided"
        
        return f"""CONTENT REQUEST:
"{input_data.user_prompt}"

CAROUSEL SPECIFICATIONS:
- Format Type: {input_data.format_type}
- Total Slides: {input_data.num_slides} (1 hook + {body_slide_count} body slides)
- Required Body Slides: {body_slide_count}

BRAND CONTEXT:
- Brand Name: {brand_kit.brand_name}
- Brand Niche: {brand_kit.brand_niche}
- Brand Style: {brand_kit.brand_style}
- Customer Pain Points: {pain_points}
- Product/Service Description: {brand_kit.product_service_desc}

TASK:
1. First, create a COMPLETE STORY - an overarching narrative (200-400 chars) that captures the entire carousel's message and flow
2. Explain your RATIONALE - why this complete story works for this format and brand (100-200 chars)
3. Then, break down the complete story into individual slides:
   - 1 hook slide (attention-grabbing opening)
   - Exactly {body_slide_count} body slides (following the format structure)

Return your response with the complete story, rationale, hook, and {body_slide_count} body slides."""


# Create singleton instance for easy import
story_generator = StoryGenerator()