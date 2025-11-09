"""
CarouselPipeline - Core orchestration engine for multi-agent carousel generation.
Coordinates the end-to-end process of validating requests, generating content strategy, 
creating slides, rendering images, and packaging final output.

Main Functions:
    1. start_pipeline() - Initializes a new carousel generation pipeline
    2. _process_pipeline() - Executes the multi-stage generation workflow asynchronously
    3. _create_final_output() - Packages carousel data and images into output directory
    4. get_pipeline_status() - Retrieves current status of a pipeline by ID
    5. list_pipelines() - Returns all active and completed pipelines

Connections:
    - Agents: OrchestratorAgent (validation), CarouselGeneratorAgent (content), 
              ImageGeneratorAgent (visuals)
    - Models: Uses CarouselRequest, PipelineResult, PipelineStatus from models.pipeline
    - Called by: app.router.routes for REST API endpoints
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from ..agents.orchestrator import OrchestratorAgent
from ..agents.image_generator import ImageGeneratorAgent
from ..agents.carousel_generator import CarouselGeneratorAgent
from ..models.pipeline import CarouselRequest, PipelineResult, PipelineStatus


class CarouselPipeline:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.output_dir = self.config.get("output_dir", "./output")
        self.orchestrator = OrchestratorAgent(config)
        self.carousel_generator = CarouselGeneratorAgent(config)
        self.image_generator = ImageGeneratorAgent(config)
        self.pipeline_storage: Dict[str, PipelineResult] = {}

    async def start_pipeline(self, request: CarouselRequest) -> str:
        result = await self.orchestrator.process(request)
        if result.status == PipelineStatus.FAILED:
            self.pipeline_storage[result.id] = result
            return result.id
        self.pipeline_storage[result.id] = result
        asyncio.create_task(self._process_pipeline(result.id))
        return result.id

    async def _process_pipeline(self, pipeline_id: str):
        try:
            result = self.pipeline_storage[pipeline_id]
            result.status = PipelineStatus.CAROUSEL_GENERATION
            result.updated_at = datetime.utcnow().isoformat()
            result.carousel_result = await self.carousel_generator.process(result.request)
            result.status = PipelineStatus.IMAGE_GENERATION
            result.updated_at = datetime.utcnow().isoformat()
            if result.carousel_result:
                for slide in result.carousel_result.slides:
                    image_input = {
                        "prompt": slide.image_generation_prompt,
                        "pipeline_id": pipeline_id,
                        "slide_number": slide.slide_number,
                    }
                    try:
                        slide.image_path = await self.image_generator.generate_single_image(image_input)
                    except Exception as error:
                        print(f"Image generation failed for slide {slide.slide_number}: {error}")
                        slide.image_path = None
            result.status = PipelineStatus.FINAL_ASSEMBLY
            result.updated_at = datetime.utcnow().isoformat()
            result.output_folder = await self._create_final_output(pipeline_id, result)
            result.status = PipelineStatus.COMPLETED
            result.updated_at = datetime.utcnow().isoformat()
        except Exception as error:
            result = self.pipeline_storage[pipeline_id]
            print(f"Pipeline {pipeline_id} failed: {error}")
            result.status = PipelineStatus.FAILED
            result.error_message = str(error)
            result.updated_at = datetime.utcnow().isoformat()

    async def _create_final_output(self, pipeline_id: str, result: PipelineResult) -> str:
        output_folder = os.path.join(self.output_dir, pipeline_id)
        os.makedirs(output_folder, exist_ok=True)
        output_data = {
            "pipeline_id": pipeline_id,
            "request": result.request.dict(),
            "carousel_result": result.carousel_result.dict() if result.carousel_result else None,
            "created_at": result.created_at,
            "completed_at": result.updated_at,
        }
        output_file = os.path.join(output_folder, "carousel_output.json")
        with open(output_file, "w", encoding="utf-8") as handle:
            json.dump(output_data, handle, indent=2)
        return output_folder

    def get_pipeline_status(self, pipeline_id: str) -> Optional[PipelineResult]:
        return self.pipeline_storage.get(pipeline_id)

    def list_pipelines(self) -> Dict[str, PipelineResult]:
        return self.pipeline_storage