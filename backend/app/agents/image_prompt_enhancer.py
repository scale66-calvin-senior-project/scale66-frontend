import json
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent
from ..models.pipeline import CarouselSlide, StoryRequest, CarouselStrategy
from ..services.openai_service import OpenAIService


class ImagePromptEnhancerAgent(BaseAgent):
    """Agent responsible for creating and enhancing image generation prompts using OpenAI only"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.openai_service = OpenAIService(config)
    
    async def process(self, input_data: Dict[str, Any]) -> List[CarouselSlide]:
        """Generate and enhance image prompts for carousel slides using OpenAI only"""
        
        slides = input_data["slides"]
        story_request = input_data["story_request"]
        strategy = input_data["strategy"]
        
        enhanced_slides = []
        
        for slide in slides:
            # Generate base image prompt using OpenAI
            base_prompt = await self._generate_base_image_prompt(slide, story_request, strategy)
            
            # Enhance the prompt using OpenAI
            enhanced_prompt = await self._enhance_with_openai(base_prompt, slide)
            
            # Update slide with enhanced prompt
            slide.image_generation_prompt = enhanced_prompt
            enhanced_slides.append(slide)
        
        return enhanced_slides
    
    async def _generate_base_image_prompt(self, slide: CarouselSlide, story_request: StoryRequest, strategy: CarouselStrategy) -> str:
        """Generate base image prompt using OpenAI"""
        
        prompt_generation_prompt = f"""You are an expert at creating image generation prompts for TikTok carousel content.

## CONTEXT:
**Slide #{slide.slide_number}:** {slide.slide_purpose}
**Text on Screen:** {slide.text_on_screen}
**Target Audience:** {story_request.target_audience}
**Niche:** {story_request.niche}
**Content Goal:** {story_request.cta_goal}

## YOUR TASK:
Create a detailed image generation prompt that:
1. Visually reinforces the slide's message
2. Appeals to the target audience
3. Uses appropriate visual metaphors
4. Maintains brand consistency across slides
5. NO TEXT should appear in the generated image

## REQUIREMENTS:
- Main subject and their emotional state/body language
- Lighting conditions and mood
- Setting/environment details  
- Color palette (warm/cool/dramatic/bright)
- Camera angle and composition
- Photography style (cinematic, documentary, lifestyle, etc.)
- Specific visual metaphors that reinforce the message

## EXAMPLE OUTPUT:
"Close-up of a confident young professional in modern office setting, warm natural lighting streaming through windows, showing determination and focus, realistic photography style, clean minimalist background, professional attire, shot from slightly below to convey empowerment"

Generate the image prompt:"""
        
        try:
            response = await self.openai_service.generate_text(
                prompt=prompt_generation_prompt,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.strip()
            
        except Exception as e:
            self.log_error(f"Failed to generate base image prompt: {e}")
            return f"Professional image related to {story_request.niche}, clean modern style, {story_request.target_audience} demographic"
    
    async def _enhance_with_openai(self, base_prompt: str, slide: CarouselSlide) -> str:
        """Enhance image prompt using OpenAI"""
        
        enhancement_prompt = f"""Enhance this image generation prompt to be more specific and visually compelling:

Original: {base_prompt}

Make it more detailed with:
- Specific lighting (golden hour, studio lighting, natural light, etc.)
- Precise camera work (close-up, wide shot, over-shoulder, etc.)  
- Detailed subject description (age, expression, posture, clothing)
- Environmental specifics (background, setting, props)
- Color mood that matches the message

Keep under 150 words. Ensure NO TEXT in the image.

Enhanced prompt:"""
        
        try:
            response = await self.openai_service.generate_text(
                prompt=enhancement_prompt,
                max_tokens=200,
                temperature=0.6
            )
            
            return response.strip()
            
        except Exception as e:
            self.log_error(f"Failed to enhance with OpenAI: {e}")
            return base_prompt