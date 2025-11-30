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
    EDUCATIONAL_TUTORIAL = "educational_tutorial"
    TRANSFORMATION_SHOWCASE = "transformation_showcase"
    LISTICLE_TIPS = "listicle_tips"
    PROBLEM_SOLUTION_PITCH = "problem_solution_pitch"
    DATA_INSIGHT_AUTHORITY = "data_insight_authority"


# Format descriptions for LLM context
FORMAT_DESCRIPTIONS: Dict[str, str] = {
    CarouselFormat.EDUCATIONAL_TUTORIAL: "Sequential step-by-step instruction teaching skill/process. Hook/problem → 6-8 learning steps (one per slide) → summary → CTA. High save rates, establishes authority, creates reference content. Use for: how-tos, tutorials, workflows, tool demos, professional development, technical explanations. Slides: 4-6.",
    
    CarouselFormat.TRANSFORMATION_SHOWCASE: "Visual narrative demonstrating measurable change through contrast. Before state → transformation journey → after state with results → CTA. Triggers contrast psychology, builds trust through proof (2x ROAS, 61% higher CTR). Use for: case studies, success stories, portfolio work, ROI demonstrations, customer results. Requires authentic documented results. Slides: 4-6.",
    
    CarouselFormat.LISTICLE_TIPS: "Numbered collection of discrete tips/insights, one per slide. Numbered headline (\"7 Ways to X\") → one item per slide → bonus/CTA. Scannable, save-worthy, satisfies completionist instinct. Use for: quick tips, recommendations, mistake lists, resource compilations, trend summaries, checklists. Slides: 3-5 (match numbered promise).",
    
    CarouselFormat.PROBLEM_SOLUTION_PITCH: "Conversion-focused persuasion leading with pain points. Pain identification → problem amplification + empathy → solution → benefits/features → social proof/results → CTA. Mirrors buyer journey, 116% increase in qualified leads. Use for: product launches, sales, lead generation, objection handling, service offerings. Slides: 4-6.",
    
    CarouselFormat.DATA_INSIGHT_AUTHORITY: "Research/statistics carousel with visualization. Bold statistic → context/methodology → supporting data points (3-5 slides) → implications → conclusions → CTA. Establishes thought leadership, high save rates, 6.60% engagement on LinkedIn, 27% boost from data visualization. Use for: industry reports, trend analysis, research findings, benchmarks. Requires genuine data. Slides: 4-6.",
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

SELECTION PRIORITY RULES (apply in order):
1. If prompt explicitly mentions data/statistics/research → ALWAYS choose data_insight_authority
2. If prompt is conversion/sales-focused → Choose problem_solution_pitch
3. If prompt shows before/after or results → Choose transformation_showcase
4. If prompt asks to teach/explain a process → Choose educational_tutorial
5. If prompt wants quick tips/numbered list → Choose listicle_tips

FORMAT DISTINCTIONS:
- educational_tutorial = Teaching HOW (process-focused)
- transformation_showcase = Showing RESULTS (outcome-focused)
- listicle_tips = Multiple quick items (breadth over depth)
- problem_solution_pitch = Selling solution (conversion-focused)
- data_insight_authority = Establishing credibility (research-focused)

KEYWORD TRIGGERS:
- "how to", "tutorial", "guide", "teach", "explain process", "step-by-step" → educational_tutorial
- "results", "before/after", "success story", "case study", "transformation", "prove", "show impact" → transformation_showcase
- "tips", "list", "ways to", "mistakes", "top X", numbered collection → listicle_tips
- "sell", "promote", "launch", "leads", "solve problem", "overcome", product/service name → problem_solution_pitch
- "data", "research", "statistics", "trends", "analysis", "insights", "study", "report" → data_insight_authority

YOUR TASK:
1. Analyze the user's content request for keyword triggers
2. Apply priority rules to select optimal format
3. Consider brand context to validate format alignment
4. Determine slide count based on format guidelines
5. Provide clear rationale explaining format choice

OUTPUT REQUIREMENTS:
- format_type: One of the format values from above
- num_slides: Integer between 3 and 10 (follow format guidelines)
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