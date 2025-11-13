"""
API Routes - FastAPI endpoint definitions for carousel pipeline operations.
Exposes REST API endpoints for creating carousels, checking pipeline status,
listing all pipelines, and health checks.

Main Endpoints:
    1. POST /carousel/create - Initiates new carousel generation pipeline
    2. GET /carousel/{pipeline_id} - Retrieves status and results for specific pipeline
    3. GET /carousels - Lists all pipelines with their current states
    4. GET /health - Returns service health status

Connections:
    - Uses: CarouselPipeline for all carousel operations
    - Uses models: CarouselRequest (input), PipelineResult (output)
    - Mounted at: /api/v1 prefix in main.py
    - Called by: Frontend, Streamlit app, or API clients
"""

from typing import Dict

from fastapi import APIRouter, HTTPException

from ..core.pipeline import CarouselPipeline
from ..models.pipeline import CarouselRequest, PipelineResult


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

