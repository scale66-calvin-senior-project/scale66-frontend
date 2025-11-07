import json
import re
from typing import Dict, Any
from .base_agent import BaseAgent
from ..models.pipeline import StoryRequest, CarouselFormat
from ..services.openai_service import OpenAIService


class FormatSelectorAgent(BaseAgent):
    """Agent responsible for selecting the optimal carousel format based on business information"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.openai_service = OpenAIService(config)
        
    async def process(self, story_request: StoryRequest) -> CarouselFormat:
        """Select the best carousel format for the business use case"""
        
        format_prompt = self._build_format_selection_prompt(story_request)
        
        try:
            response = await self.openai_service.generate_text(
                prompt=format_prompt,
                max_tokens=1000,
                temperature=0.3  # Lower temperature for more consistent format selection
            )
            
            carousel_format = self._parse_format_response(response)
            carousel_format.target_slides = story_request.num_slides or 3
            return carousel_format
            
        except Exception as e:
            raise Exception(f"Failed to select carousel format: {str(e)}")
    
    def _build_format_selection_prompt(self, story_request: StoryRequest) -> str:
        """Build the format selection prompt"""
        
        prompt = f"""You are a TikTok content strategist expert at selecting the optimal carousel format for maximum engagement.

## BUSINESS CONTEXT:
**Niche/Industry:** {story_request.niche}
**Target Audience:** {story_request.target_audience}
**Primary Pain Point:** {story_request.pain_point}
**Content Goal:** {story_request.cta_goal}

## AVAILABLE CAROUSEL FORMATS:

1. **Top 5** - Reasons/things/signs/mistakes in the product's niche
   - Best for: Educational content, listicles, quick value delivery
   - Engagement: High save rate, easy to consume

2. **Story/Case Study** - Hook with relatable problem, struggle, turning point, solution
   - Best for: Building trust, showcasing transformation, emotional connection
   - Engagement: High watch time, strong emotional response

3. **Yes/No Decision Tree** - Should you _____, each slide asks a question, guides towards solution
   - Best for: Interactive content, guiding decisions, qualification
   - Engagement: High interaction, decision-making value

4. **Common Mistakes** - Are you making these mistakes? How to avoid them (solution)
   - Best for: Pain point focus, authority building, problem-solving
   - Engagement: High relatability, save-worthy advice

5. **Transformative Grid** - Side-by-side comparisons on each slide
   - Best for: Before/after showcases, contrasting approaches
   - Engagement: Visual impact, clear value demonstration

6. **Tutorial** - How to achieve _____ without THIS STRUGGLE
   - Best for: Step-by-step guidance, educational content
   - Engagement: High save rate, actionable value

7. **Unpopular Opinion** - Controversial take as the hook
   - Best for: Pattern interrupt, thought leadership, engagement bait
   - Engagement: High comment activity, shareability

8. **This vs That** - Stop doing A, start doing B, repeat through slides
   - Best for: Behavior change, direct comparisons
   - Engagement: Clear actionables, decision-making help

9. **Checklist Format** - The ultimate _____ checklist, each slide is an item
   - Best for: Comprehensive guides, reference content
   - Engagement: High save rate, reference value

10. **Timeline/Journey** - How I went from A to B
    - Best for: Personal branding, inspiration, credibility
    - Engagement: Storytelling appeal, relatability

11. **Before vs After** - Show the struggle before and transformation after
    - Best for: Transformation showcases, hope/inspiration
    - Engagement: Emotional impact, aspirational content

12. **Myth vs Reality** - Myth on one slide, reality on the next
    - Best for: Education, myth-busting, authority building
    - Engagement: "Aha moments", educational value

## YOUR TASK:
Analyze the business context and select the ONE format that will perform best for this specific audience and goal.

Consider:
- What will stop the scroll for this target audience?
- What format best addresses their pain point?
- What format aligns with the content goal ({story_request.cta_goal})?
- What format will drive the desired engagement behavior?

Respond in JSON format:
{{
    "format_name": "selected format name",
    "format_description": "brief description of how this format works",
    "reasoning": "detailed explanation of why this format is optimal for this business case",
    "target_slides": number_of_slides_recommended
}}"""
        
        return prompt
    
    def _parse_format_response(self, response: str) -> CarouselFormat:
        """Parse the AI response into a CarouselFormat"""
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                format_data = json.loads(json_str)
            else:
                # Fallback: try to parse the entire response as JSON
                format_data = json.loads(response)
            
            return CarouselFormat(
                format_name=format_data["format_name"],
                format_description=format_data["format_description"],
                reasoning=format_data["reasoning"],
                target_slides=format_data["target_slides"]
            )
            
        except Exception as e:
            # Fallback to a default format if parsing fails
            self.log_error(f"Failed to parse format response: {e}")
            return CarouselFormat(
                format_name="Story/Case Study",
                format_description="Hook with relatable problem, struggle, turning point, solution",
                reasoning="Fallback format selected due to parsing error",
                target_slides=story_request.num_slides or 3
            )