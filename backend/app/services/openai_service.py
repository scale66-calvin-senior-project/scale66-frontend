from openai import AsyncOpenAI
from typing import Dict, Any, Optional, List
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = settings.openai_model
        
    async def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text using ChatGPT"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
            
    async def generate_story(self, story_idea: str, num_slides: int) -> str:
        """Generate a complete story from an idea"""
        prompt = f"""
        Create a compelling story based on this idea: "{story_idea}"
        
        The story should be suitable for a {num_slides}-slide presentation.
        Make it engaging, well-structured, and appropriate for visual storytelling.
        Include character development, plot progression, and a satisfying conclusion.
        
        Write the complete story in narrative form:
        """
        
        return await self.generate_text(prompt, max_tokens=1500, temperature=0.8)
        
    async def break_story_into_scenes(self, story: str, num_slides: int) -> List[str]:
        """Break a story into individual scenes for slides"""
        prompt = f"""
        Break this story into exactly {num_slides} distinct scenes for presentation slides.
        Each scene should be a logical segment that can stand alone on one slide.
        
        Story: {story}
        
        Format your response as a numbered list:
        1. [Scene 1 content]
        2. [Scene 2 content]
        ...
        
        Make each scene engaging and visually descriptive.
        """
        
        response = await self.generate_text(prompt, max_tokens=1200, temperature=0.7)
        
        # Parse the numbered list into individual scenes
        scenes = []
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('- ')):
                # Remove numbering and clean up
                scene = line.split('.', 1)[-1].strip() if '.' in line else line
                scene = scene.lstrip('- ').strip()
                if scene:
                    scenes.append(scene)
        
        # Ensure we have the right number of scenes
        while len(scenes) < num_slides:
            scenes.append(f"Additional scene content for slide {len(scenes) + 1}")
        
        return scenes[:num_slides]
        
    async def generate_slide_text(self, scene_content: str) -> str:
        """Generate concise slide text from scene content"""
        prompt = f"""
        Create concise, engaging slide text based on this scene content:
        
        {scene_content}
        
        Requirements:
        - Keep it brief but impactful (2-4 bullet points or 1-2 short sentences)
        - Make it presentation-ready
        - Focus on key points that would engage an audience
        - Use clear, compelling language
        
        Slide text:
        """
        
        return await self.generate_text(prompt, max_tokens=200, temperature=0.6)
        
    async def create_image_prompt(self, scene_content: str, style_guide: Dict[str, Any]) -> str:
        """Create detailed image prompts for scene content"""
        style_desc = ""
        if style_guide:
            mood = style_guide.get('mood', '')
            imagery_style = style_guide.get('imagery_style', '')
            colors = ', '.join(style_guide.get('color_palette', [])[:3])
            style_desc = f"Style: {imagery_style}, Mood: {mood}, Colors: {colors}"
        
        prompt = f"""
        Create a detailed image generation prompt for this scene:
        
        Scene: {scene_content}
        {style_desc}
        
        Generate a detailed prompt that includes:
        - Visual description of the scene
        - Art style and mood
        - Composition and lighting
        - Color palette if specified
        
        Make it suitable for AI image generation. Be specific and vivid.
        
        Image prompt:
        """
        
        return await self.generate_text(prompt, max_tokens=300, temperature=0.7)