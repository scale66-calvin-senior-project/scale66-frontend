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
    story_idea: str
    num_slides: int
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
    output_folder: Optional[str] = None
    created_at: str
    updated_at: str
    error_message: Optional[str] = None


class SlideContent(BaseModel):
    scene_number: int
    text: str
    image_prompt: str
    image_path: Optional[str] = None