import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from ..agents.orchestrator import OrchestratorAgent
from ..agents.story_generator import StoryGeneratorAgent
from ..agents.style_generator import StyleGeneratorAgent
from ..agents.text_generator import TextGeneratorAgent
from ..agents.image_generator import ImageGeneratorAgent
from ..agents.carousel_generator import CarouselGeneratorAgent
from ..models.pipeline import StoryRequest, PipelineResult, PipelineStatus, CarouselResult


class StoryPipeline:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.output_dir = self.config.get("output_dir", "./output")
        
        # Initialize agents
        self.orchestrator = OrchestratorAgent(config)
        self.story_generator = StoryGeneratorAgent(config)
        self.style_generator = StyleGeneratorAgent(config)
        self.text_generator = TextGeneratorAgent(config)
        self.image_generator = ImageGeneratorAgent(config)
        self.carousel_generator = CarouselGeneratorAgent(config)
        
        # In-memory storage for demo (replace with database in production)
        self.pipeline_storage: Dict[str, PipelineResult] = {}
        
    async def start_pipeline(self, story_request: StoryRequest) -> str:
        """Start the story generation pipeline and return pipeline ID"""
        
        # Step 1: Orchestrator planning
        result = await self.orchestrator.process(story_request)
        
        if result.status == PipelineStatus.FAILED:
            self.pipeline_storage[result.id] = result
            return result.id
            
        self.pipeline_storage[result.id] = result
        
        # Start processing in background
        asyncio.create_task(self._process_pipeline(result.id))
        
        return result.id
        
    async def _process_pipeline(self, pipeline_id: str):
        """Process the complete pipeline asynchronously"""
        try:
            result = self.pipeline_storage[pipeline_id]
            
            # Step 2: Carousel Generation (replaces story generation)
            result.status = PipelineStatus.STORY_GENERATION
            result.updated_at = datetime.utcnow().isoformat()
            
            # Generate carousel content from business information
            carousel_result = await self.carousel_generator.process(result.story_request)
            result.carousel_result = carousel_result
            
            # Step 3: Image Generation for each carousel slide
            result.status = PipelineStatus.CONTENT_GENERATION
            result.updated_at = datetime.utcnow().isoformat()
            
            # Generate images for each carousel slide
            for slide in carousel_result.slides:
                try:
                    image_input = {
                        "prompt": slide.image_generation_prompt,
                        "pipeline_id": pipeline_id,
                        "slide_number": slide.slide_number
                    }
                    image_path = await self.image_generator.generate_single_image(image_input)
                    slide.image_path = image_path
                except Exception as e:
                    print(f"Failed to generate image for slide {slide.slide_number}: {str(e)}")
                    slide.image_path = None
            
            # Step 4: Final Assembly
            result.status = PipelineStatus.FINAL_ASSEMBLY
            result.updated_at = datetime.utcnow().isoformat()
            
            output_folder = await self._create_final_output(pipeline_id, result)
            result.output_folder = output_folder
            
            # Complete
            result.status = PipelineStatus.COMPLETED
            result.updated_at = datetime.utcnow().isoformat()
            
        except Exception as e:
            result = self.pipeline_storage[pipeline_id]
            result.status = PipelineStatus.FAILED
            result.error_message = str(e)
            result.updated_at = datetime.utcnow().isoformat()
            
    async def _create_final_output(self, pipeline_id: str, result: PipelineResult) -> str:
        """Create final output package with JSON and files"""
        output_folder = os.path.join(self.output_dir, pipeline_id)
        os.makedirs(output_folder, exist_ok=True)
        
        # Create output JSON
        output_data = {
            "pipeline_id": pipeline_id,
            "story_request": result.story_request.dict(),
            "complete_story": result.complete_story,
            "style_guide": result.style_guide.dict() if result.style_guide else None,
            "scenes": [scene.dict() for scene in result.scenes],
            "carousel_result": result.carousel_result.dict() if result.carousel_result else None,
            "created_at": result.created_at,
            "completed_at": result.updated_at
        }
        
        output_file = os.path.join(output_folder, "story_output.json")
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
            
        return output_folder
        
    def get_pipeline_status(self, pipeline_id: str) -> Optional[PipelineResult]:
        """Get current status of a pipeline"""
        return self.pipeline_storage.get(pipeline_id)
        
    def list_pipelines(self) -> Dict[str, PipelineResult]:
        """Get all pipelines"""
        return self.pipeline_storage