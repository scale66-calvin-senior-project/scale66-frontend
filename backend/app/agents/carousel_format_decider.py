"""
Carousel Format Decider Agent - Step 2 of AI Pipeline

Takes Brand Kit info and decides the optimal carousel format.

Input: Brand Kit (niche, style, pain points, product)
Output: Selected format with rationale
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class CarouselFormatDecider(BaseAgent):
    """
    Carousel Format Decider Agent.
    
    Responsibilities:
    1. Analyze brand niche and target audience
    2. Consider brand style and pain points
    3. Decide optimal carousel format from predefined options
    4. Return format decision with rationale
    
    Available Carousel Formats:
    - "educational_tips": List of tips/tricks (e.g., "5 Ways to...")
    - "problem_solution": Problem → Solution flow
    - "before_after": Transformation story
    - "step_by_step": Tutorial format
    - "myth_busting": Common myths debunked
    - "stats_facts": Data-driven insights
    - "story_narrative": Emotional storytelling
    - "comparison": Product/concept comparison
    
    Decision Criteria:
    - Content type (educational, promotional, entertaining)
    - Audience sophistication level
    - Brand style (professional, casual, bold)
    - Pain point complexity
    - Product/service type
    
    TODO: Implement format decision logic:
    1. Create comprehensive prompt with format options
    2. Analyze brand context
    3. Call LLM to decide format
    4. Return structured format decision
    """
    
    def __init__(self):
        """Initialize format decider agent."""
        super().__init__()
        # TODO: Load format templates if needed
        pass
    
    async def decide(
        self, 
        brand_kit_data: Dict[str, Any], 
        user_prompt: str
    ) -> Dict[str, Any]:
        """
        Decide carousel format based on brand info and user request.
        
        Args:
            brand_kit_data: Brand niche, colors, style, pain points, product
                {
                    "brand_name": str,
                    "brand_niche": str,
                    "brand_style": str,
                    "customer_pain_points": str,
                    "product_service_desc": str
                }
            user_prompt: User's content request
            
        Returns:
            Format decision:
            {
                "selected_format": str,  # One of the format types above
                "num_slides": int,  # Recommended number of slides (3-10)
                "format_rationale": str,  # Why this format was chosen
                "content_structure": str  # Brief outline of structure
            }
        
        TODO: Implement format decision:
        
        1. Build LLM prompt with:
           - Brand context (niche, style, audience)
           - Available format options with descriptions
           - User's content request
           - Instructions to analyze and decide
        
        2. Call LLM:
           prompt = f'''
           You are a social media content strategist.
           
           Brand: {brand_kit_data["brand_name"]}
           Niche: {brand_kit_data["brand_niche"]}
           Style: {brand_kit_data["brand_style"]}
           Pain Points: {brand_kit_data["customer_pain_points"]}
           Product: {brand_kit_data["product_service_desc"]}
           
           User Request: {user_prompt}
           
           Available Formats:
           1. educational_tips - List of tips/tricks
           2. problem_solution - Problem → Solution flow
           3. before_after - Transformation story
           4. step_by_step - Tutorial format
           5. myth_busting - Common myths debunked
           6. stats_facts - Data-driven insights
           7. story_narrative - Emotional storytelling
           8. comparison - Product/concept comparison
           
           Analyze the brand and user request, then decide:
           1. Which format would be most effective?
           2. How many slides (3-10)?
           3. Why is this format best for this brand?
           
           Return JSON format:
           {{
               "selected_format": "format_name",
               "num_slides": number,
               "format_rationale": "explanation",
               "content_structure": "brief outline"
           }}
           '''
        
        3. Parse LLM response as JSON
        
        4. Validate response:
           - Check format is valid
           - Check num_slides is 3-10
           - Ensure rationale is provided
        
        5. Log decision and return
        
        Example return:
        {
            "selected_format": "problem_solution",
            "num_slides": 5,
            "format_rationale": "Problem-solution format works best for this SaaS product because...",
            "content_structure": "Slide 1: Hook with pain point, Slides 2-3: Elaborate problem, Slide 4: Introduce solution, Slide 5: CTA"
        }
        """
        # TODO: Implement format decision
        await self._log_step("format_decision_start", {
            "brand": brand_kit_data.get("brand_name"),
            "niche": brand_kit_data.get("brand_niche")
        })
        
        # TODO: Build prompt
        # TODO: Call LLM
        # TODO: Parse and validate response
        # TODO: Return format decision
        
        pass
    
    async def _validate_format(self, format_result: Dict[str, Any]) -> bool:
        """
        Validate format decision result.
        
        Args:
            format_result: The format decision from LLM
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If format is invalid
        
        TODO: Implement validation:
        1. Check selected_format is in valid formats
        2. Check num_slides is 3-10
        3. Check rationale is not empty
        """
        valid_formats = [
            "educational_tips",
            "problem_solution",
            "before_after",
            "step_by_step",
            "myth_busting",
            "stats_facts",
            "story_narrative",
            "comparison"
        ]
        
        # TODO: Validate format result
        pass

