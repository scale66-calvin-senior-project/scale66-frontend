"""
CarouselGeneratorAgent - High-level carousel composition and performance analysis agent.
Orchestrates the complete carousel creation workflow by coordinating format selection,
content generation, image prompt enhancement, and performance analysis.

Main Functions:
    1. process() - Coordinates all sub-agents to produce complete CarouselResult
    2. _generate_performance_analysis() - Analyzes why carousel will perform well on TikTok
    3. _format_slides_for_analysis() - Formats slide data for performance evaluation

Connections:
    - Inherits from: BaseAgent
    - Coordinates agents: FormatSelectorAgent, ContentGeneratorAgent, ImagePromptEnhancerAgent
    - Uses services: OpenAIService for performance analysis
    - Uses models: CarouselRequest, CarouselResult
    - Called by: CarouselPipeline._process_pipeline()
"""

import json
import re
from typing import Dict, Any, List

from .base_agent import BaseAgent
from .format_selector import FormatSelectorAgent
from .content_generator import ContentGeneratorAgent
from .image_prompt_enhancer import ImagePromptEnhancerAgent
from ..models.pipeline import CarouselRequest, CarouselResult
from ..services.openai_service import OpenAIService


class CarouselGeneratorAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("CarouselGenerator", config)
        self.format_selector = FormatSelectorAgent(config)
        self.content_generator = ContentGeneratorAgent(config)
        self.image_prompt_enhancer = ImagePromptEnhancerAgent(config)
        self.analysis_client = OpenAIService(config)

    async def process(self, request: CarouselRequest) -> CarouselResult:
        self.log_info(f"Selecting format for {request.niche}")
        carousel_format = await self.format_selector.process(request)
        content_data = await self.content_generator.process({
            "request": request,
            "carousel_format": carousel_format,
        })
        strategy = content_data["strategy"]
        slides = content_data["slides"]
        enhanced_slides = await self.image_prompt_enhancer.process({
            "slides": slides,
            "request": request,
            "strategy": strategy,
        })
        analysis = await self._generate_performance_analysis(request, carousel_format, strategy, enhanced_slides)
        return CarouselResult(
            format_type=carousel_format.format_name,
            strategy=strategy,
            why_this_works=analysis,
            slides=enhanced_slides,
        )

    async def _generate_performance_analysis(self, request, carousel_format, strategy, slides) -> List[str]:
        analysis_prompt = f"""
You are a TikTok algorithm expert. Analyze why this carousel will perform well on TikTok.

Format: {carousel_format.format_name}
Target Audience: {request.target_audience}
Niche: {request.niche}
Goal: {request.cta_goal}

Strategy:
- Hook: {strategy.hook_strategy}
- Flow: {strategy.content_flow}
- Tactics: {', '.join(strategy.engagement_tactics)}
- CTA: {strategy.cta_approach}

Slides:
{self._format_slides_for_analysis(slides)}

Return a JSON array of 5 concise reasons.
"""
        try:
            response = await self.analysis_client.generate_text(
                prompt=analysis_prompt,
                max_tokens=600,
                temperature=0.4,
            )
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                return json.loads(match.group())
            lines = [line.strip('- "') for line in response.splitlines() if line.strip()]
            return lines[:7]
        except Exception as error:
            self.log_error(f"Performance analysis fallback: {error}")
            return [
                "Hooks align with platform engagement triggers",
                "Slide flow sustains watch time",
                "Specific insights encourage saves",
                "CTA integrates with audience intent",
                "Visual guidance supports shareability",
            ]

    def _format_slides_for_analysis(self, slides) -> str:
        formatted = [
            f"Slide {slide.slide_number}: {slide.slide_purpose} - {slide.text_on_screen}" for slide in slides
        ]
        return "\n".join(formatted)