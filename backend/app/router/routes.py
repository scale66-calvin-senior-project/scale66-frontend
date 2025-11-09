from typing import Dict

from fastapi import APIRouter, HTTPException

from ..core.pipeline import CarouselPipeline
from ..models.pipeline import CarouselRequest, PipelineResult


# Overview:
# - Purpose: Expose FastAPI endpoints for managing carousel generation pipelines.
# Key Components:
# - router: registers creation and retrieval routes backed by CarouselPipeline services.


router = APIRouter()
pipeline = CarouselPipeline()


@router.post("/carousel/create", response_model=dict)
async def create_carousel(request: CarouselRequest):
    pipeline_id = await pipeline.start_pipeline(request)
    return {
        "pipeline_id": pipeline_id,
        "status": "started",
        "message": "Carousel generation pipeline started successfully",
    }


@router.get("/carousel/{pipeline_id}", response_model=PipelineResult)
async def get_carousel_status(pipeline_id: str):
    result = pipeline.get_pipeline_status(pipeline_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return result


@router.get("/carousels", response_model=Dict[str, PipelineResult])
async def list_carousels():
    return pipeline.list_pipelines()


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "carousel-pipeline-backend"}

