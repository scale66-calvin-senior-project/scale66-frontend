from pydantic import BaseModel, model_validator
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
    story_idea: Optional[str] = None
    niche: Optional[str] = None
    target_audience: Optional[str] = None
    pain_point: Optional[str] = None
    cta_goal: Optional[str] = None
    num_slides: int = 3
    style_preferences: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def ensure_story_idea(self):
        if not self.story_idea:
            descriptive_parts = []
            if self.niche:
                niche_segment = f"the {self.niche} niche"
            else:
                niche_segment = "this business"

            if self.target_audience:
                audience_segment = f" targeting {self.target_audience}"
            else:
                audience_segment = ""

            idea_parts = [f"Create a story for {niche_segment}{audience_segment}."]

            if self.pain_point:
                idea_parts.append(f"Highlight how it solves {self.pain_point}.")

            if self.cta_goal:
                idea_parts.append(f"Encourage viewers to {self.cta_goal}.")

            if any([self.niche, self.target_audience, self.pain_point, self.cta_goal]):
                self.story_idea = " ".join(idea_parts).strip()

        self.num_slides = 3

        if not (self.story_idea and self.story_idea.strip()):
            raise ValueError("Story idea is required. Provide 'story_idea' directly or supply niche, target_audience, pain_point, and cta_goal.")

        return self


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