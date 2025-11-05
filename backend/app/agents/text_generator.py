from typing import Dict, Any, List
from .base_agent import BaseAgent
from ..models.pipeline import StoryScene, SlideContent
from ..services.openai_service import OpenAIService
from ..core.config import settings


class TextGeneratorAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("TextGenerator", config)
        self.openai_service = None
        if settings.openai_api_key:
            try:
                self.openai_service = OpenAIService()
            except ValueError as e:
                self.log_error(f"Failed to initialize OpenAI service: {e}")
        
    async def process(self, input_data: Dict[str, Any]) -> List[SlideContent]:
        scenes = input_data.get("scenes", [])
        style_guide = input_data.get("style_guide")
        
        self.log_info(f"Generating slide text for {len(scenes)} scenes")
        
        slide_contents = []
        for scene in scenes:
            slide_content = await self._generate_slide_text(scene, style_guide)
            slide_contents.append(slide_content)
            
        return slide_contents
        
    async def _generate_slide_text(self, scene: StoryScene, style_guide) -> SlideContent:
        self.log_info(f"Generating text for scene {scene.scene_number}")
        
        if self.openai_service:
            slide_text = await self.openai_service.generate_slide_text(scene.content)
            image_prompt = await self.openai_service.create_image_prompt(
                scene.content, 
                style_guide.dict() if style_guide else {}
            )
        else:
            slide_text = await self._create_slide_text_placeholder(scene.content)
            image_prompt = await self._create_image_prompt_placeholder(scene.content, style_guide)
        
        return SlideContent(
            scene_number=scene.scene_number,
            text=slide_text,
            image_prompt=image_prompt
        )
        
    async def _create_slide_text_placeholder(self, scene_content: str) -> str:
        return f"Key points from scene content would be extracted and formatted for slide presentation using ChatGPT"
        
    async def _create_image_prompt_placeholder(self, scene_content: str, style_guide) -> str:
        style_desc = ""
        if style_guide:
            style_desc = f"in {style_guide.imagery_style} style with {style_guide.mood} mood"
            
        return f"Generate an image that represents the scene content {style_desc}"