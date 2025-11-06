import json
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent
from ..models.pipeline import StoryRequest, CarouselFormat, CarouselSlide, CarouselStrategy
from ..services.openai_service import OpenAIService


class ContentGeneratorAgent(BaseAgent):
    """Agent responsible for generating carousel content and strategy using OpenAI"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.openai_service = OpenAIService(config)
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content strategy and slides for the selected format"""
        
        story_request = input_data["story_request"]
        carousel_format = input_data["carousel_format"]
        
        # Step 1: Generate strategy
        strategy = await self._generate_strategy(story_request, carousel_format)
        
        # Step 2: Generate slide content
        slides = await self._generate_slides(story_request, carousel_format, strategy)
        
        return {
            "strategy": strategy,
            "slides": slides
        }
    
    async def _generate_strategy(self, story_request: StoryRequest, carousel_format: CarouselFormat) -> CarouselStrategy:
        """Generate the overall content strategy"""
        
        strategy_prompt = f"""You are a TikTok content strategist creating an engagement strategy for a {carousel_format.format_name} carousel.

## BUSINESS CONTEXT:
**Niche:** {story_request.niche}
**Target Audience:** {story_request.target_audience}
**Pain Point:** {story_request.pain_point}
**Goal:** {story_request.cta_goal}

## SELECTED FORMAT:
**Format:** {carousel_format.format_name}
**Description:** {carousel_format.format_description}
**Reasoning:** {carousel_format.reasoning}

## YOUR TASK:
Create a strategic framework for this carousel that maximizes engagement and achieves the content goal.

Respond in JSON format:
{{
    "hook_strategy": "specific strategy for the opening hook that stops the scroll",
    "content_flow": "how the content should flow between slides to maintain engagement",
    "engagement_tactics": ["tactic1", "tactic2", "tactic3"],
    "cta_approach": "how to naturally incorporate the call-to-action to achieve the goal"
}}

Focus on:
- Psychology of the target audience
- What will make them stop scrolling
- How to build emotional tension and release
- Specific engagement triggers for TikTok algorithm"""
        
        try:
            response = await self.openai_service.generate_text(
                prompt=strategy_prompt,
                max_tokens=800,
                temperature=0.4
            )
            
            return self._parse_strategy_response(response)
            
        except Exception as e:
            raise Exception(f"Failed to generate strategy: {str(e)}")
    
    async def _generate_slides(self, story_request: StoryRequest, carousel_format: CarouselFormat, strategy: CarouselStrategy) -> List[CarouselSlide]:
        """Generate individual slide content"""
        
        slides_prompt = f"""You are a TikTok content creator generating {carousel_format.target_slides} slides for a {carousel_format.format_name} carousel.

## BUSINESS CONTEXT:
**Niche:** {story_request.niche}
**Target Audience:** {story_request.target_audience}
**Pain Point:** {story_request.pain_point}
**Goal:** {story_request.cta_goal}

## STRATEGY TO FOLLOW:
**Hook Strategy:** {strategy.hook_strategy}
**Content Flow:** {strategy.content_flow}
**Engagement Tactics:** {', '.join(strategy.engagement_tactics)}
**CTA Approach:** {strategy.cta_approach}

## CONTENT REQUIREMENTS:

### Slide 1 (Hook):
- Must stop the scroll in 0.5 seconds
- Use {strategy.hook_strategy}
- Target the specific pain point: {story_request.pain_point}
- Examples: "I made [specific mistake] and lost [consequence]", "If you [specific sign], stop [action] immediately"

### Middle Slides:
- Follow the {carousel_format.format_name} structure
- Build emotional tension that resolves by the end
- Use specific numbers, timeframes, concrete details
- Avoid generic advice - provide fresh perspectives

### Final Slide:
- Implement {strategy.cta_approach}
- Natural call-to-action for: {story_request.cta_goal}
- Low-friction engagement request

## TEXT REQUIREMENTS:
- 2-4 lines maximum per slide (except hook can be longer)
- Scannable and emotionally resonant
- Voice that matches the target audience
- No clichés or generic platitudes

Respond in JSON format:
{{
    "slides": [
        {{
            "slide_number": 1,
            "slide_purpose": "Hook - Pattern Interrupt",
            "text_on_screen": "exact text for the slide"
        }},
        {{
            "slide_number": 2,
            "slide_purpose": "purpose of this slide",
            "text_on_screen": "exact text for the slide"
        }}
    ]
}}

Generate exactly {carousel_format.target_slides} slides following the {carousel_format.format_name} format."""
        
        try:
            response = await self.openai_service.generate_text(
                prompt=slides_prompt,
                max_tokens=2000,
                temperature=0.6
            )
            
            return self._parse_slides_response(response)
            
        except Exception as e:
            raise Exception(f"Failed to generate slides: {str(e)}")
    
    def _parse_strategy_response(self, response: str) -> CarouselStrategy:
        """Parse strategy response into CarouselStrategy"""
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                strategy_data = json.loads(json_str)
            else:
                strategy_data = json.loads(response)
            
            return CarouselStrategy(
                hook_strategy=strategy_data["hook_strategy"],
                content_flow=strategy_data["content_flow"],
                engagement_tactics=strategy_data["engagement_tactics"],
                cta_approach=strategy_data["cta_approach"]
            )
            
        except Exception as e:
            self.log_error(f"Failed to parse strategy response: {e}")
            # Fallback strategy
            return CarouselStrategy(
                hook_strategy="Use specific numbers and relatable pain point",
                content_flow="Build tension and provide resolution",
                engagement_tactics=["Use specific examples", "Create curiosity gaps", "Include actionable tips"],
                cta_approach="Natural request related to the content value"
            )
    
    def _parse_slides_response(self, response: str) -> List[CarouselSlide]:
        """Parse slides response into list of CarouselSlide"""
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                slides_data = json.loads(json_str)
            else:
                slides_data = json.loads(response)
            
            slides = []
            for slide_data in slides_data.get("slides", []):
                slide = CarouselSlide(
                    slide_number=slide_data["slide_number"],
                    slide_purpose=slide_data["slide_purpose"],
                    text_on_screen=slide_data["text_on_screen"],
                    image_generation_prompt=""  # Will be generated by image prompt agent
                )
                slides.append(slide)
            
            return slides
            
        except Exception as e:
            self.log_error(f"Failed to parse slides response: {e}")
            # Return empty list, will be handled by calling agent
            return []