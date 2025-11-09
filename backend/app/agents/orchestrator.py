import uuid
from datetime import datetime
from typing import Dict, Any

from .base_agent import BaseAgent
from ..models.pipeline import CarouselRequest, PipelineResult, PipelineStatus


# Overview:
# - Purpose: Validate incoming carousel requests and produce initial pipeline state.
# Key Components:
# - OrchestratorAgent: generates pipeline identifiers, validates slide counts, and seeds status tracking.


class OrchestratorAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("Orchestrator", config)

    async def process(self, request: CarouselRequest) -> PipelineResult:
        self.log_info(f"Planning pipeline for: {request.story_idea[:50]}")
        pipeline_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        result = PipelineResult(
            id=pipeline_id,
            status=PipelineStatus.PLANNING,
            request=request,
            created_at=now,
            updated_at=now,
        )
        if not request.story_idea or not request.story_idea.strip():
            result.status = PipelineStatus.FAILED
            result.error_message = "story_idea cannot be empty"
            return result
        if request.num_slides > 20:
            result.status = PipelineStatus.FAILED
            result.error_message = "num_slides must be 20 or fewer"
            return result
        result.status = PipelineStatus.CAROUSEL_GENERATION
        result.updated_at = datetime.utcnow().isoformat()
        return result