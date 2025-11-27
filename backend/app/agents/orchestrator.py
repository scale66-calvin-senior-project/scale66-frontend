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
from app.core.supabase import get_supabase_admin_client


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
            self.logger.info("=" * 80)
            self.logger.info("STEP 1/6: FETCHING BRAND KIT")
            self.logger.info("=" * 80)
            brand_kit = await self._fetch_brand_kit(input_data.brand_kit_id)
            self.logger.info(f"Brand Kit Retrieved:")
            self.logger.info(f"  - Brand Name: {brand_kit.brand_name}")
            self.logger.info(f"  - Niche: {brand_kit.brand_niche}")
            self.logger.info(f"  - Style: {brand_kit.brand_style}")
            self.logger.info(f"  - Pain Points: {', '.join(brand_kit.customer_pain_points)}")
            self.logger.info(f"  - Product/Service: {brand_kit.product_service_desc[:100]}...")
            
            # Step 2: Determine carousel format
            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info("STEP 2/6: DETERMINING CAROUSEL FORMAT")
            self.logger.info("=" * 80)
            self.logger.info(f"User Prompt: {input_data.user_prompt}")
            
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
            
            self.logger.info(f"Format Decision:")
            self.logger.info(f"  - Format Type: {format_result.format_type}")
            self.logger.info(f"  - Number of Slides: {format_result.num_slides}")
            self.logger.info(f"  - Rationale: {format_result.format_rationale}")
            
            # Step 3: Generate story narratives
            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info("STEP 3/6: GENERATING STORY NARRATIVES")
            self.logger.info("=" * 80)
            
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
            
            self.logger.info(f"Story Narratives Generated:")
            self.logger.info(f"  - Hook Slide Story:")
            self.logger.info(f"    {story_result.hook_slide_story}")
            self.logger.info(f"  - Body Slides ({len(story_result.body_slides_story)} total):")
            for i, story in enumerate(story_result.body_slides_story, 1):
                self.logger.info(f"    Slide {i}: {story}")
            
            # Step 4: Generate AI images
            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info("STEP 4/6: GENERATING AI IMAGES")
            self.logger.info("=" * 80)
            
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
            
            self.logger.info(f"AI Images Generated:")
            self.logger.info(f"  - Hook Slide Image: Generated (base64, {len(image_result.hook_slide_image)} chars)")
            self.logger.info(f"  - Body Slide Images: {len(image_result.body_slides_images)} images generated")
            for i in range(len(image_result.body_slides_images)):
                self.logger.info(f"    Slide {i+1}: Generated (base64, {len(image_result.body_slides_images[i])} chars)")
            
            # Step 5: Generate text overlays
            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info("STEP 5/6: GENERATING TEXT OVERLAYS")
            self.logger.info("=" * 80)
            
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
            
            self.logger.info(f"Text Overlays Generated:")
            self.logger.info(f"  - Hook Slide Text: {text_result.hook_slide_text}")
            self.logger.info(f"  - Hook Slide Style: {text_result.hook_slide_text_style}")
            self.logger.info(f"  - Body Slides ({len(text_result.body_slides_text)} total):")
            for i, (text, style) in enumerate(zip(text_result.body_slides_text, text_result.body_slides_text_styles), 1):
                self.logger.info(f"    Slide {i} Text: {text}")
                self.logger.info(f"    Slide {i} Style: {style}")
            
            # Step 6: Finalize slides (overlay text and upload)
            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info("STEP 6/6: FINALIZING CAROUSEL SLIDES")
            self.logger.info("=" * 80)
            
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
            
            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 80)
            self.logger.info(f"Carousel ID: {final_result.carousel_id}")
            self.logger.info(f"Total Slides: {len(final_result.carousel_slides_urls)}")
            self.logger.info(f"Supabase URLs:")
            for i, url in enumerate(final_result.carousel_slides_urls):
                slide_type = "Hook" if i == 0 else f"Body {i}"
                self.logger.info(f"  - Slide {i} ({slide_type}): {url}")
            self.logger.info("=" * 80)
            
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
            supabase = get_supabase_admin_client()
            
            # Fetch from brand_kits table
            response = supabase.table("brand_kits").select("*").eq("id", brand_kit_id).execute()
            
            if not response.data or len(response.data) == 0:
                raise ExecutionError(
                    f"Brand kit not found: {brand_kit_id}"
                )
            
            brand_data = response.data[0]
            
            # Parse into BrandKit model
            # Note: DB column is "product_service_description", model uses "product_service_desc"
            pain_points = brand_data.get("customer_pain_points", [])
            # Handle if pain_points is stored as string (legacy) vs JSONB array
            if isinstance(pain_points, str):
                pain_points = [pain_points] if pain_points else []
            
            brand_kit = BrandKit(
                brand_name=brand_data.get("brand_name", ""),
                brand_niche=brand_data.get("brand_niche", ""),
                brand_style=brand_data.get("brand_style", ""),
                customer_pain_points=pain_points,
                product_service_desc=brand_data.get("product_service_description", ""),
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