"""
Orchestrator Agent - Step 1 of AI Pipeline

Coordinates the entire carousel generation pipeline by executing agents sequentially
and managing state flow between steps.

Input: OrchestratorInput (brand_kit_id, user_prompt)
Output: OrchestratorOutput (carousel_id, carousel_slides_urls)

Pipeline Flow:
1. Fetch BrandKit from database
2. CarouselFormatDecider → determine format and slide count
3. StoryGenerator → create hook and body slide narratives
4. ImageGenerator → generate AI images for each slide
5. TextGenerator → analyze images and create text overlays
6. Finalizer → compose final slides and upload to storage
"""

import logging
from typing import Optional

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import (
    OrchestratorInput,
    OrchestratorOutput,
    CarouselFormatDeciderInput,
    StoryGeneratorInput,
    ImageGeneratorInput,
    TextGeneratorInput,
    FinalizerInput,
)
from app.models.brand_kit import BrandKit
from app.agents.carousel_format_decider import carousel_format_decider
from app.agents.story_generator import story_generator
from app.agents.image_generator import image_generator
from app.agents.text_generator import text_generator
from app.agents.finalizer import finalizer
from app.core.supabase import get_supabase_admin


logger = logging.getLogger(__name__)


class Orchestrator(BaseAgent[OrchestratorInput, OrchestratorOutput]):
    """
    Orchestrates the complete carousel generation pipeline.
    
    Coordinates sequential execution of all AI agents and manages state flow
    between pipeline steps. Handles brand kit fetching, validation, and error
    recovery.
    """
    
    async def _validate_input(self, input_data: OrchestratorInput) -> None:
        """
        Validate orchestrator input before pipeline execution.
        
        Checks:
        - brand_kit_id is not empty
        - user_prompt is not empty and meets minimum length
        - brand_kit exists in database (will fetch and validate)
        
        Args:
            input_data: Orchestrator input schema
            
        Raises:
            ValidationError: If input is invalid
        """
        # Validate brand_kit_id
        if not input_data.brand_kit_id or not input_data.brand_kit_id.strip():
            raise ValidationError("brand_kit_id cannot be empty")
        
        # Validate user_prompt
        if not input_data.user_prompt or not input_data.user_prompt.strip():
            raise ValidationError("user_prompt cannot be empty")
        
        if len(input_data.user_prompt.strip()) < 10:
            raise ValidationError("user_prompt must be at least 10 characters")
        
        if len(input_data.user_prompt.strip()) > 1000:
            raise ValidationError("user_prompt cannot exceed 1000 characters")
        
        self.logger.debug("Input validation passed")
    
    async def _execute(self, input_data: OrchestratorInput) -> OrchestratorOutput:
        """
        Execute the complete carousel generation pipeline.
        
        Pipeline steps:
        1. Fetch and validate brand kit from database
        2. Determine carousel format (CarouselFormatDecider)
        3. Generate story narratives (StoryGenerator)
        4. Generate AI images (ImageGenerator)
        5. Generate text overlays (TextGenerator)
        6. Finalize and upload slides (Finalizer)
        
        Args:
            input_data: Validated orchestrator input
            
        Returns:
            Final carousel with URLs and metadata
            
        Raises:
            ExecutionError: If any pipeline step fails
        """
        try:
            self.logger.info(
                f"Starting pipeline execution for brand_kit_id: {input_data.brand_kit_id}"
            )
            
            # Step 1: Fetch BrandKit from database
            brand_kit = await self._fetch_brand_kit(input_data.brand_kit_id)
            self.logger.info(f"Fetched brand kit: {brand_kit.brand_name}")
            
            # Step 2: Determine carousel format
            self.logger.info("Step 2/6: Determining carousel format")
            format_result = await carousel_format_decider.run(
                CarouselFormatDeciderInput(
                    step_name="carousel_format_decider",
                    success=True,
                    user_prompt=input_data.user_prompt,
                    brand_kit=brand_kit,
                )
            )
            
            if not format_result.success:
                raise ExecutionError(
                    f"Format decision failed: {format_result.error_message}"
                )
            
            self.logger.info(
                f"Format decided: {format_result.format_type} "
                f"({format_result.num_slides} slides)"
            )
            
            # Step 3: Generate story narratives
            self.logger.info("Step 3/6: Generating story narratives")
            story_result = await story_generator.run(
                StoryGeneratorInput(
                    step_name="story_generator",
                    success=True,
                    format_type=format_result.format_type,
                    num_slides=format_result.num_slides,
                    brand_kit=brand_kit,
                    user_prompt=input_data.user_prompt,
                )
            )
            
            if not story_result.success:
                raise ExecutionError(
                    f"Story generation failed: {story_result.error_message}"
                )
            
            self.logger.info(
                f"Story generated: hook + {len(story_result.body_slides_story)} body slides"
            )
            
            # Step 4: Generate AI images
            self.logger.info("Step 4/6: Generating AI images")
            image_result = await image_generator.run(
                ImageGeneratorInput(
                    step_name="image_generator",
                    success=True,
                    hook_slide_story=story_result.hook_slide_story,
                    body_slides_story=story_result.body_slides_story,
                )
            )
            
            if not image_result.success:
                raise ExecutionError(
                    f"Image generation failed: {image_result.error_message}"
                )
            
            self.logger.info(
                f"Images generated: {1 + len(image_result.body_slides_images)} total"
            )
            
            # Step 5: Generate text overlays
            self.logger.info("Step 5/6: Generating text overlays")
            text_result = await text_generator.run(
                TextGeneratorInput(
                    step_name="text_generator",
                    success=True,
                    hook_slide_story=story_result.hook_slide_story,
                    body_slides_story=story_result.body_slides_story,
                    hook_slide_image=image_result.hook_slide_image,
                    body_slides_images=image_result.body_slides_images,
                )
            )
            
            if not text_result.success:
                raise ExecutionError(
                    f"Text generation failed: {text_result.error_message}"
                )
            
            self.logger.info(
                f"Text overlays generated: {1 + len(text_result.body_slides_text)} total"
            )
            
            # Step 6: Finalize slides (overlay text and upload)
            self.logger.info("Step 6/6: Finalizing carousel slides")
            final_result = await finalizer.run(
                FinalizerInput(
                    step_name="finalizer",
                    success=True,
                    hook_slide_text=text_result.hook_slide_text,
                    body_slides_text=text_result.body_slides_text,
                    hook_slide_text_style=text_result.hook_slide_text_style,
                    body_slides_text_styles=text_result.body_slides_text_styles,
                    hook_slide_image=image_result.hook_slide_image,
                    body_slides_images=image_result.body_slides_images,
                )
            )
            
            if not final_result.success:
                raise ExecutionError(
                    f"Finalization failed: {final_result.error_message}"
                )
            
            self.logger.info(
                f"Pipeline completed successfully! Carousel ID: {final_result.carousel_id}"
            )
            
            # Return orchestrator output
            return OrchestratorOutput(
                step_name="orchestrator",
                success=True,
                carousel_id=final_result.carousel_id,
                carousel_slides_urls=final_result.carousel_slides_urls,
            )
            
        except ExecutionError:
            # Re-raise execution errors from pipeline steps
            raise
        except Exception as e:
            # Catch any unexpected errors
            raise ExecutionError(f"Pipeline execution failed: {str(e)}")
    
    async def _fetch_brand_kit(self, brand_kit_id: str) -> BrandKit:
        """
        Fetch brand kit from database and validate.
        
        Args:
            brand_kit_id: UUID of the brand kit
            
        Returns:
            BrandKit model with brand information
            
        Raises:
            ExecutionError: If brand kit not found or invalid
        """
        try:
            supabase = get_supabase_admin()
            
            # Fetch from brand_kits table
            response = supabase.table("brand_kits").select("*").eq("id", brand_kit_id).execute()
            
            if not response.data or len(response.data) == 0:
                raise ExecutionError(
                    f"Brand kit not found: {brand_kit_id}"
                )
            
            brand_data = response.data[0]
            
            # Parse into BrandKit model
            brand_kit = BrandKit(
                brand_name=brand_data.get("brand_name", ""),
                brand_niche=brand_data.get("brand_niche", ""),
                brand_style=brand_data.get("brand_style", ""),
                customer_pain_points=brand_data.get("customer_pain_points", []),
                product_service_desc=brand_data.get("product_service_desc", ""),
            )
            
            # Validate required fields
            if not brand_kit.brand_name or not brand_kit.brand_name.strip():
                raise ExecutionError("Brand kit missing brand_name")
            
            if not brand_kit.brand_niche or not brand_kit.brand_niche.strip():
                raise ExecutionError("Brand kit missing brand_niche")
            
            if not brand_kit.brand_style or not brand_kit.brand_style.strip():
                raise ExecutionError("Brand kit missing brand_style")
            
            if not brand_kit.product_service_desc or not brand_kit.product_service_desc.strip():
                raise ExecutionError("Brand kit missing product_service_desc")
            
            self.logger.debug(f"Brand kit validated: {brand_kit.brand_name}")
            
            return brand_kit
            
        except ExecutionError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            self.logger.error(f"Failed to fetch brand kit: {e}")
            raise ExecutionError(f"Database error fetching brand kit: {str(e)}")


# Create singleton instance for easy import
orchestrator = Orchestrator()