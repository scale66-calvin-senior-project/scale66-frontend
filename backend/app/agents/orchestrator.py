from typing import Dict, Any
from .base_agent import BaseAgent
from ..models.pipeline import StoryRequest, PipelineResult, PipelineStatus
import uuid
from datetime import datetime


class OrchestratorAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("Orchestrator", config)
        
    async def process(self, input_data: StoryRequest) -> PipelineResult:
        self.log_info(f"Starting pipeline for story: {input_data.story_idea[:50]}...")
        
        # Create initial pipeline result
        pipeline_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        result = PipelineResult(
            id=pipeline_id,
            status=PipelineStatus.PLANNING,
            story_request=input_data,
            created_at=now,
            updated_at=now
        )
        
        # Validate input
        if not input_data.story_idea.strip():
            result.status = PipelineStatus.FAILED
            result.error_message = "Story idea cannot be empty"
            return result
            
        if input_data.num_slides < 1 or input_data.num_slides > 20:
            result.status = PipelineStatus.FAILED
            result.error_message = "Number of slides must be between 1 and 20"
            return result
            
        self.log_info(f"Pipeline {pipeline_id} planned successfully")
        result.status = PipelineStatus.STORY_GENERATION
        result.updated_at = datetime.utcnow().isoformat()
        
        return result
        
    def determine_next_step(self, current_status: PipelineStatus) -> PipelineStatus:
        status_flow = {
            PipelineStatus.PLANNING: PipelineStatus.STORY_GENERATION,
            PipelineStatus.STORY_GENERATION: PipelineStatus.STYLE_GENERATION,
            PipelineStatus.STYLE_GENERATION: PipelineStatus.CONTENT_GENERATION,
            PipelineStatus.CONTENT_GENERATION: PipelineStatus.FINAL_ASSEMBLY,
            PipelineStatus.FINAL_ASSEMBLY: PipelineStatus.COMPLETED
        }
        return status_flow.get(current_status, PipelineStatus.FAILED)