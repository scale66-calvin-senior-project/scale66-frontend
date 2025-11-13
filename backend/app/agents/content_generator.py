"""
ContentGeneratorAgent - Carousel strategy and slide content generation agent.
Creates comprehensive content strategy (hook, flow, tactics, CTA) and generates
detailed slide scripts including purpose and on-screen text for each slide.

Main Functions:
    1. process() - Generates complete strategy and slides for carousel
    2. _generate_strategy() - Creates CarouselStrategy using OpenAI
    3. _generate_slides() - Generates slide-by-slide content with purposes and text
    4. _parse_strategy_response() - Extracts strategy from AI response with fallback
    5. _parse_slides_response() - Extracts slides from AI response with fallback

Connections:
    - Inherits from: BaseAgent
    - Uses services: OpenAIService for content generation
    - Uses models: CarouselRequest, CarouselFormat, CarouselSlide, CarouselStrategy
    - Called by: CarouselGeneratorAgent.process()
"""

import json
import re
from typing import Dict, Any, List

from .base_agent import BaseAgent
from ..models.pipeline import CarouselRequest, CarouselFormat, CarouselSlide, CarouselStrategy
from ..services.openai_service import OpenAIService


class ContentGeneratorAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ContentGenerator", config)
        self.client = OpenAIService(config)

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request: CarouselRequest = input_data["request"]
        carousel_format: CarouselFormat = input_data["carousel_format"]
        strategy = await self._generate_strategy(request, carousel_format)
        slides = await self._generate_slides(request, carousel_format, strategy)
        return {"strategy": strategy, "slides": slides}

    async def _generate_strategy(self, request: CarouselRequest, carousel_format: CarouselFormat) -> CarouselStrategy:
        prompt = f"""
You are a TikTok content strategist designing a {carousel_format.format_name} carousel.

Niche: {request.niche}
Audience: {request.target_audience}
Pain Point: {request.pain_point}
Goal: {request.cta_goal}

Respond in JSON with hook_strategy, content_flow, engagement_tactics, and cta_approach.
"""
        response = await self.client.generate_text(prompt=prompt, max_tokens=600, temperature=0.4)
        return self._parse_strategy_response(response)

    async def _generate_slides(self, request: CarouselRequest, carousel_format: CarouselFormat, strategy: CarouselStrategy) -> List[CarouselSlide]:
        prompt = f"""
Create {carousel_format.target_slides} slide scripts for a {carousel_format.format_name} carousel.

Niche: {request.niche}
Audience: {request.target_audience}
Pain Point: {request.pain_point}
Goal: {request.cta_goal}

Hook Strategy: {strategy.hook_strategy}
Content Flow: {strategy.content_flow}
Engagement Tactics: {', '.join(strategy.engagement_tactics)}
CTA Approach: {strategy.cta_approach}

Return JSON with a slides array where each item has slide_number, slide_purpose, and text_on_screen.
"""
        response = await self.client.generate_text(prompt=prompt, max_tokens=1800, temperature=0.6)
        return self._parse_slides_response(response)

    def _parse_strategy_response(self, response: str) -> CarouselStrategy:
        try:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            payload = json.loads(match.group() if match else response)
            return CarouselStrategy(
                hook_strategy=payload["hook_strategy"],
                content_flow=payload["content_flow"],
                engagement_tactics=payload["engagement_tactics"],
                cta_approach=payload["cta_approach"],
            )
        except Exception as error:
            self.log_error(f"Strategy parsing fallback: {error}")
            return CarouselStrategy(
                hook_strategy="Lead with a sharp tension in the niche",
                content_flow="Escalate the pain then resolve with clear steps",
                engagement_tactics=["Contrast hook", "Specific proof", "Tease transformation"],
                cta_approach="Invite saves and shares aligned to the promised outcome",
            )

    def _parse_slides_response(self, response: str) -> List[CarouselSlide]:
        try:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            payload = json.loads(match.group() if match else response)
            slides: List[CarouselSlide] = []
            for slide_data in payload.get("slides", []):
                slides.append(
                    CarouselSlide(
                        slide_number=slide_data["slide_number"],
                        slide_purpose=slide_data["slide_purpose"],
                        text_on_screen=slide_data["text_on_screen"],
                        image_generation_prompt="",
                    )
                )
            return slides
        except Exception as error:
            self.log_error(f"Slide parsing fallback: {error}")
            return []

