from fastapi import APIRouter, HTTPException
from typing import Dict, List
from ..models.pipeline import StoryRequest, PipelineResult
from ..core.pipeline import StoryPipeline

router = APIRouter()

# Initialize pipeline instance
pipeline = StoryPipeline()


@router.post("/story/create", response_model=dict)
async def create_story(story_request: StoryRequest):
    """Start a new story generation pipeline"""
    try:
        pipeline_id = await pipeline.start_pipeline(story_request)
        return {
            "pipeline_id": pipeline_id,
            "status": "started",
            "message": "Story generation pipeline started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/story/{pipeline_id}", response_model=PipelineResult)
async def get_story_status(pipeline_id: str):
    """Get the status and results of a story generation pipeline"""
    result = pipeline.get_pipeline_status(pipeline_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    return result


@router.get("/stories", response_model=Dict[str, PipelineResult])
async def list_stories():
    """List all story generation pipelines"""
    return pipeline.list_pipelines()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "story-pipeline-backend"}