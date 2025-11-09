"""
FormatSelectorAgent - Carousel format recommendation agent.
Analyzes business context (niche, audience, pain point, CTA) and selects the most
effective carousel format using AI-driven strategy selection.

Main Functions:
    1. process() - Selects optimal carousel format for the given request
    2. _build_prompt() - Constructs format selection prompt for OpenAI
    3. _parse_response() - Extracts CarouselFormat from AI response with fallback

Connections:
    - Inherits from: BaseAgent
    - Uses services: OpenAIService for format recommendation
    - Uses models: CarouselRequest, CarouselFormat
    - Called by: CarouselGeneratorAgent.process()
"""

import json
import re
from typing import Dict, Any

from .base_agent import BaseAgent
from ..models.pipeline import CarouselRequest, CarouselFormat
from ..services.openai_service import OpenAIService


class FormatSelectorAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("FormatSelector", config)
        self.client = OpenAIService(config)

    async def process(self, request: CarouselRequest) -> CarouselFormat:
        prompt = self._build_prompt(request)
        response = await self.client.generate_text(prompt=prompt, max_tokens=900, temperature=0.3)
        format_choice = self._parse_response(response)
        format_choice.target_slides = request.num_slides
        return format_choice

    def _build_prompt(self, request: CarouselRequest) -> str:
        return f"""
You are a TikTok carousel strategist choosing the highest performing format.

Niche: {request.niche}
Audience: {request.target_audience}
Pain Point: {request.pain_point}
Goal: {request.cta_goal}

Respond in JSON with format_name, format_description, reasoning, and target_slides.
Choose from Top 5, Story/Case Study, Yes/No Decision Tree, Common Mistakes,
Transformative Grid, Tutorial, Unpopular Opinion, This vs That, Checklist,
Timeline/Journey, Before vs After, or Myth vs Reality.
"""

    def _parse_response(self, response: str) -> CarouselFormat:
        try:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            payload = json.loads(match.group() if match else response)
            return CarouselFormat(
                format_name=payload["format_name"],
                format_description=payload["format_description"],
                reasoning=payload["reasoning"],
                target_slides=payload.get("target_slides", 3),
            )
        except Exception as error:
            self.log_error(f"Format parsing fallback: {error}")
            return CarouselFormat(
                format_name="Common Mistakes",
                format_description="Highlight critical mistakes and fixes across the carousel.",
                reasoning="Default format applied after parsing error.",
                target_slides=3,
            )

