import base64
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.core.config import settings
from app.models.pipeline import (
    OrchestratorInput,
    OrchestratorOutput,
    TemplateDeciderInput,
    CaptionGeneratorInput,
    SlideGeneratorInput,
)
from app.models.brand_kit import BrandKit
from app.agents.template_decider import template_decider
from app.agents.caption_generator import caption_generator
from app.agents.slide_generator import slide_generator
from app.core.supabase import get_supabase_admin_client


class Orchestrator(BaseAgent[OrchestratorInput, OrchestratorOutput]):
    _instance: Optional['Orchestrator'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        super().__init__()
    
    async def _validate_input(self, input_data: OrchestratorInput) -> None:
        if not input_data.brand_kit_id or not input_data.brand_kit_id.strip():
            raise ValidationError("brand_kit_id cannot be empty")
        
        if not input_data.user_prompt or not input_data.user_prompt.strip():
            raise ValidationError("user_prompt cannot be empty")
        
        if len(input_data.user_prompt.strip()) < 10:
            raise ValidationError("user_prompt must be at least 10 characters")
        
        if len(input_data.user_prompt.strip()) > 1000:
            raise ValidationError("user_prompt cannot exceed 1000 characters")
    
    async def _execute(self, input_data: OrchestratorInput) -> OrchestratorOutput:
        start_time = time.time()
        
        try:
            brand_kit = await self._fetch_brand_kit(input_data.brand_kit_id)
            
            template_result = await template_decider.run(
                TemplateDeciderInput(
                    user_prompt=input_data.user_prompt,
                    brand_kit=brand_kit,
                )
            )
            
            if not template_result.success:
                raise ExecutionError(
                    f"Template decision failed: {template_result.error_message}"
                )
            
            caption_result = await caption_generator.run(
                CaptionGeneratorInput(
                    format_type=template_result.format_type,
                    user_prompt=input_data.user_prompt,
                    brand_kit=brand_kit,
                    num_slides=template_result.num_slides,
                )
            )
            
            if not caption_result.success:
                raise ExecutionError(
                    f"Caption generation failed: {caption_result.error_message}"
                )
            
            slide_result = await slide_generator.run(
                SlideGeneratorInput(
                    format_type=template_result.format_type,
                    num_slides=template_result.num_slides,
                    brand_kit=brand_kit,
                    user_prompt=input_data.user_prompt,
                    slides_text=caption_result.slides_text,
                    template_id=template_result.template_id,
                )
            )
            
            if not slide_result.success:
                raise ExecutionError(
                    f"Slide generation failed: {slide_result.error_message}"
                )
            
            output_dir = None
            if settings.save_local_output:
                output_dir = self._save_images_locally(
                    slides_images=slide_result.slides_images,
                    brand_kit_id=input_data.brand_kit_id,
                )
            
            return OrchestratorOutput(
                step_name="orchestrator",
                success=True,
                carousel_id="local-output",
                carousel_slides_urls=[],
            )
            
        except ExecutionError:
            raise
        except Exception as e:
            raise ExecutionError(f"Pipeline execution failed: {str(e)}")
    
    async def _fetch_brand_kit(self, brand_kit_id: str) -> BrandKit:
        try:
            supabase = get_supabase_admin_client()
            
            response = supabase.table("brand_kits").select("*").eq("id", brand_kit_id).execute()
            
            if not response.data or len(response.data) == 0:
                raise ExecutionError(
                    f"Brand kit not found: {brand_kit_id}"
                )
            
            brand_data = response.data[0]
            
            pain_points = brand_data.get("customer_pain_points", [])
            if isinstance(pain_points, str):
                pain_points = [pain_points] if pain_points else []
            
            brand_kit = BrandKit(
                brand_name=brand_data.get("brand_name", ""),
                brand_niche=brand_data.get("brand_niche", ""),
                brand_style=brand_data.get("brand_style", ""),
                customer_pain_points=pain_points,
                product_service_desc=brand_data.get("product_service_description", ""),
            )
            
            if not brand_kit.brand_name or not brand_kit.brand_name.strip():
                raise ExecutionError("Brand kit missing brand_name")
            
            if not brand_kit.brand_niche or not brand_kit.brand_niche.strip():
                raise ExecutionError("Brand kit missing brand_niche")
            
            if not brand_kit.brand_style or not brand_kit.brand_style.strip():
                raise ExecutionError("Brand kit missing brand_style")
            
            if not brand_kit.product_service_desc or not brand_kit.product_service_desc.strip():
                raise ExecutionError("Brand kit missing product_service_desc")
            
            return brand_kit
            
        except ExecutionError:
            raise
        except Exception as e:
            raise ExecutionError(f"Database error fetching brand kit: {str(e)}")
    
    def _save_images_locally(
        self,
        slides_images: List[str],
        brand_kit_id: str,
    ) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        brand_id_short = brand_kit_id[:8]
        output_dir = Path(settings.output_dir) / "carousels" / f"{timestamp}_{brand_id_short}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, img in enumerate(slides_images):
            slide_type = "hook" if i == 0 else "body"
            slide_path = output_dir / f"{i + 1}_{slide_type}.png"
            with open(slide_path, "wb") as f:
                f.write(base64.b64decode(img))
        
        return output_dir


orchestrator = Orchestrator()
