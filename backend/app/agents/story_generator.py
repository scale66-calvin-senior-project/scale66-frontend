"""
Story Generator Agent - Step 3 of AI Pipeline

Generates compelling hook and body slide narratives based on format decision and brand context.

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
    CarouselFormat.TOP_5: "Hook: Preview the top 5 or reveal #1 with intrigue. Body: One numbered item per slide with brief explanation (50-100 chars).",
    CarouselFormat.STORY_CASE_STUDY: "Hook: Relatable problem statement. Body: Struggle (1-2 slides) → Turning point (1 slide) → Solution (1-2 slides) → Result/transformation (1 slide).",
    CarouselFormat.DECISION_TREE: "Hook: Should you ___? Body: Each slide asks a yes/no question that guides decision-making, building toward the solution.",
    CarouselFormat.COMMON_MISTAKES: "Hook: 'Are you making these mistakes?' Body: Each slide presents one mistake + how to avoid it. Format: 'Mistake: X. Instead: Y.'",
    CarouselFormat.TRANSFORMATIVE_GRID: "Hook: Promise of transformation. Body: Each slide has left/right comparison. Format: 'Before: X | After: Y' or 'Old way: X | New way: Y'.",
    CarouselFormat.TUTORIAL: "Hook: 'How to achieve _____ without [pain point]'. Body: Sequential steps (Step 1, Step 2, etc.) with actionable instructions.",
    CarouselFormat.UNPOPULAR_OPINION: "Hook: Controversial/counterintuitive statement. Body: Supporting arguments, examples, and reframe (build case for the opinion).",
    CarouselFormat.THIS_VS_THAT: "Hook: Stop doing [bad habit]. Body: Repeat pattern across slides: 'Stop: X. Start: Y.' Each slide is one shift.",
    CarouselFormat.CHECKLIST: "Hook: 'The ultimate _____ checklist'. Body: Each slide is one checklist item with brief context or action step.",
    CarouselFormat.TIMELINE_JOURNEY: "Hook: Where you started. Body: Chronological progression showing key milestones and lessons learned along the journey.",
    CarouselFormat.BEFORE_VS_AFTER: "Hook: The 'before' struggle. Body: Show transformation stages, proof points, and the 'after' result.",
    CarouselFormat.MYTH_VS_REALITY: "Hook: Common belief/myth. Body: Alternate between myth slide and reality slide. Format: 'Myth: X' then 'Reality: Y'.",
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
        
        return f"""You are an expert social media content creator specializing in viral carousel posts for Instagram and TikTok. Your role is to write compelling, scroll-stopping narratives that drive engagement and deliver value.

FORMAT STRUCTURE FOR '{input_data.format_type}':
{format_structure}

STORYTELLING PRINCIPLES:

1. HOOK SLIDE (First Slide):
   - Must stop the scroll immediately (pattern interrupt, curiosity gap, bold claim)
   - 40-80 characters ideal (must be readable in <2 seconds)
   - Use proven hooks: "Stop scrolling if...", "The one thing...", "I went from X to Y", "Are you making this mistake?"
   - Create curiosity gap - don't give away everything
   - Speak directly to target audience's pain or desire

2. BODY SLIDES (Remaining Slides):
   - Each slide should standalone (users may not swipe through all)
   - 50-100 characters per slide for optimal readability
   - Deliver immediate value on each slide
   - Use active voice and action-oriented language
   - Build momentum toward conclusion/CTA
   - Maintain narrative flow while keeping independence

3. CONTENT QUALITY:
   - Be specific, not generic (use numbers, examples, concrete details)
   - Cut filler words ruthlessly (every word must earn its place)
   - Use power words for emotional impact
   - Vary sentence structure for rhythm
   - End with actionable insight or strong conclusion

4. BRAND VOICE ALIGNMENT:
   - Embody the brand's style throughout (professional, playful, authoritative, etc.)
   - Use industry-appropriate language
   - Match sophistication level to target audience
   - Maintain consistency across all slides

5. SOCIAL MEDIA OPTIMIZATION:
   - Write for scanners, not readers
   - Front-load key information
   - Use line breaks strategically (implied through brevity)
   - Optimize for mobile viewing
   - Create save-worthy or share-worthy content

OUTPUT REQUIREMENTS:
- complete_story: A cohesive narrative (200-400 characters) that ties the entire carousel together
- complete_story_rationale: Explanation of your strategic choices (100-200 characters)
- hook_slide_story: Compelling first slide that stops the scroll (30-150 characters)
- body_slides_story: Array of exactly {input_data.num_slides - 1} body slide stories (each 30-150 characters)
- Do not include slide numbers in the content (e.g., don't write "Slide 1:", "Step 1:")"""
    
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

Each slide should support the complete story while being able to stand alone.

Return your response with the complete story, rationale, hook, and {body_slide_count} body slides."""


# Create singleton instance for easy import
story_generator = StoryGenerator()