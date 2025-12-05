import base64
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
        pass
    
    async def _execute(self, input_data: OrchestratorInput) -> OrchestratorOutput:
        brand_kit = await self._fetch_brand_kit(input_data.brand_kit_id)
        
        template_result = await template_decider.run(
            TemplateDeciderInput(
                user_prompt=input_data.user_prompt,
                brand_kit=brand_kit,
            )
        )
        
        caption_result = await caption_generator.run(
            CaptionGeneratorInput(
                format_type=template_result.format_type,
                user_prompt=input_data.user_prompt,
                brand_kit=brand_kit,
                num_body_slides=template_result.num_body_slides,
                template_id=template_result.template_id,
                hook_slide=template_result.hook_slide,
                body_slide=template_result.body_slide,
                cta_slide=template_result.cta_slide,
            )
        )
        
        slide_result = await slide_generator.run(
            SlideGeneratorInput(
                format_type=template_result.format_type,
                num_body_slides=template_result.num_body_slides,
                brand_kit=brand_kit,
                user_prompt=input_data.user_prompt,
                hook_text=caption_result.hook_text,
                body_texts=caption_result.body_texts,
                cta_text=caption_result.cta_text,
                template_id=template_result.template_id,
                hook_slide=template_result.hook_slide,
                body_slide=template_result.body_slide,
                cta_slide=template_result.cta_slide,
            )
        )
        
        output_dir = None
        if settings.save_local_output:
            output_dir = self._save_images_locally(
                hook_image=slide_result.hook_image,
                body_images=slide_result.body_images,
                cta_image=slide_result.cta_image,
                brand_kit_id=input_data.brand_kit_id,
            )
        
        return OrchestratorOutput(
            step_name="orchestrator",
            success=True,
            carousel_id="local-output",
            carousel_slides_urls=[],
        )
    
    async def _fetch_brand_kit(self, brand_kit_id: str) -> BrandKit:
        supabase = get_supabase_admin_client()
        response = supabase.table("brand_kits").select("*").eq("id", brand_kit_id).execute()
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
        
        return brand_kit
    
    def _save_images_locally(
        self,
        hook_image: str,
        body_images: List[str],
        cta_image: Optional[str],
        brand_kit_id: str,
    ) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        brand_id_short = brand_kit_id[:8]
        output_dir = Path(settings.output_dir) / "carousels" / f"{timestamp}_{brand_id_short}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save hook slide
        hook_path = output_dir / "1_hook.png"
        with open(hook_path, "wb") as f:
            f.write(base64.b64decode(hook_image))
        
        # Save body slides
        for i, body_img in enumerate(body_images):
            body_path = output_dir / f"{i + 2}_body.png"
            with open(body_path, "wb") as f:
                f.write(base64.b64decode(body_img))
        
        # Save CTA slide if exists
        if cta_image:
            cta_path = output_dir / f"{len(body_images) + 2}_cta.png"
            with open(cta_path, "wb") as f:
                f.write(base64.b64decode(cta_image))
        
        return output_dir


orchestrator = Orchestrator()
