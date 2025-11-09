from typing import Dict, Any, List

from .base_agent import BaseAgent
from ..models.pipeline import CarouselSlide, CarouselRequest, CarouselStrategy
from ..services.openai_service import OpenAIService


# Overview:
# - Purpose: Enrich slide-level image prompts for consistent carousel visuals.
# Key Components:
# - ImagePromptEnhancerAgent: crafts base prompts and refines them into production-ready image instructions.


class ImagePromptEnhancerAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ImagePromptEnhancer", config)
        self.client = OpenAIService(config)

    async def process(self, input_data: Dict[str, Any]) -> List[CarouselSlide]:
        slides: List[CarouselSlide] = input_data["slides"]
        request: CarouselRequest = input_data["request"]
        strategy: CarouselStrategy = input_data["strategy"]
        enhanced: List[CarouselSlide] = []
        for slide in slides:
            base_prompt = await self._generate_base_prompt(slide, request, strategy)
            slide.image_generation_prompt = await self._enhance_prompt(base_prompt)
            enhanced.append(slide)
        return enhanced

    async def _generate_base_prompt(self, slide: CarouselSlide, request: CarouselRequest, strategy: CarouselStrategy) -> str:
        prompt = f"""
Create an image prompt for a TikTok carousel slide.

Slide {slide.slide_number}: {slide.slide_purpose}
On-screen Text: {slide.text_on_screen}
Audience: {request.target_audience}
Niche: {request.niche}
CTA Goal: {request.cta_goal}
Strategy Hook: {strategy.hook_strategy}

Describe subject, emotion, setting, lighting, palette, camera angle, and ensure no text appears in the image.
"""
        try:
            response = await self.client.generate_text(prompt=prompt, max_tokens=260, temperature=0.7)
            return response.strip()
        except Exception as error:
            self.log_error(f"Image prompt fallback: {error}")
            return f"Dynamic lifestyle scene for {request.niche} targeting {request.target_audience}."

    async def _enhance_prompt(self, base_prompt: str) -> str:
        prompt = f"""
Enhance this image prompt with vivid specifics while keeping it under 150 words.
Highlight lighting, camera work, subject detail, environment, and color mood.
Ensure the generated image contains no text.

Original Prompt: {base_prompt}
"""
        try:
            response = await self.client.generate_text(prompt=prompt, max_tokens=220, temperature=0.6)
            return response.strip()
        except Exception as error:
            self.log_error(f"Image prompt enhancement fallback: {error}")
            return base_prompt

