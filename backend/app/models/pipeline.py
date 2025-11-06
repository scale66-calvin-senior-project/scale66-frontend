from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum


class PipelineStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    STORY_GENERATION = "story_generation"
    STYLE_GENERATION = "style_generation"
    CONTENT_GENERATION = "content_generation"
    FINAL_ASSEMBLY = "final_assembly"
    COMPLETED = "completed"
    FAILED = "failed"


class StoryRequest(BaseModel):
    niche: str
    target_audience: str
    pain_point: str
    cta_goal: str
    num_slides: Optional[int] = None
    style_preferences: Optional[Dict[str, Any]] = None
    
    
class StoryScene(BaseModel):
    scene_number: int
    content: str
    slide_text: Optional[str] = None
    image_path: Optional[str] = None


class StyleGuide(BaseModel):
    color_palette: List[str]
    imagery_style: str
    design_direction: str
    font_suggestions: List[str]
    mood: str
    

class PipelineResult(BaseModel):
    id: str
    status: PipelineStatus
    story_request: StoryRequest
    complete_story: Optional[str] = None
    style_guide: Optional[StyleGuide] = None
    scenes: List[StoryScene] = []
    carousel_result: Optional[CarouselResult] = None
    output_folder: Optional[str] = None
    created_at: str
    updated_at: str
    error_message: Optional[str] = None


class SlideContent(BaseModel):
    scene_number: int
    text: str
    image_prompt: str
    image_path: Optional[str] = None


class CarouselSlide(BaseModel):
    slide_number: int
    slide_purpose: str
    text_on_screen: str
    image_generation_prompt: str
    image_path: Optional[str] = None


class CarouselFormat(BaseModel):
    format_name: str
    format_description: str
    reasoning: str
    target_slides: int


class CarouselStrategy(BaseModel):
    hook_strategy: str
    content_flow: str
    engagement_tactics: List[str]
    cta_approach: str


class CarouselResult(BaseModel):
    format_type: str
    strategy: CarouselStrategy
    why_this_works: List[str]
    slides: List[CarouselSlide]