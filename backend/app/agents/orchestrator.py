"""
Orchestrator Agent - Step 1 of AI Pipeline

Input: OrchestratorInput (brand_kit_id, user_prompt)
Output: OrchestratorOutput (carousel_id, carousel_slides_urls, quality_metrics)
"""

import time
import logging
from typing import Optional

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.core.logging import create_run_log_file
from app.core.config import settings
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


class Orchestrator(BaseAgent[OrchestratorInput, OrchestratorOutput]):
    """
    Orchestrates the complete carousel generation pipeline.
    Singleton pattern ensures single instance across application.
    """
    
    _instance: Optional['Orchestrator'] = None
    
    def __new__(cls):
        """Singleton instance creation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize orchestrator agent."""
        super().__init__()
    
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
        Args:
            input_data: Validated orchestrator input
            
        Returns:
            Final carousel with URLs and metadata
            
        Raises:
            ExecutionError: If any pipeline step fails
        """
        # Track pipeline duration
        start_time = time.time()
        
        # Create a new log file for this pipeline run
        run_log_handler = None
        try:
            run_log_handler = create_run_log_file(input_data.brand_kit_id)
            # Pipeline start separator
            brand_id_short = input_data.brand_kit_id[:8]
            self.logger.info("╔" + "═" * 78 + "╗")
            self.logger.info(f"║ PIPELINE START | Brand Kit: {brand_id_short}                                      ║")
            self.logger.info("╚" + "═" * 78 + "╝")
            self.logger.info("")
            
            # Step 1: Fetch BrandKit from database
            self.logger.info("─── STEP 1/6: BRAND KIT ───")
            brand_kit = await self._fetch_brand_kit(input_data.brand_kit_id)
            
            # Enhanced Brand Kit display
            self.logger.info("Brand Kit Retrieved:")
            self.logger.info(f"  Brand Name       : {brand_kit.brand_name}")
            self.logger.info(f"  Niche            : {brand_kit.brand_niche}")
            self.logger.info(f"  Style            : {brand_kit.brand_style}")
            self.logger.info(f"  Customer Pain Points:")
            for pain_point in brand_kit.customer_pain_points:
                self.logger.info(f"    • {pain_point}")
            self.logger.info(f"  Product/Service  :")
            # Wrap product description for better readability
            desc = brand_kit.product_service_desc
            max_line_length = 70
            words = desc.split()
            lines = []
            current_line = []
            current_length = 0
            for word in words:
                if current_length + len(word) + 1 > max_line_length:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = len(word)
                else:
                    current_line.append(word)
                    current_length += len(word) + 1
            if current_line:
                lines.append(" ".join(current_line))
            for line in lines:
                self.logger.info(f"    {line}")
            
            # Step 2: Determine carousel format
            self.logger.info("")
            self.logger.info("─── STEP 2/6: CAROUSEL FORMAT ───")
            self.logger.info(f"User Prompt: {input_data.user_prompt}")
            
            format_result = await carousel_format_decider.run(
                CarouselFormatDeciderInput(
                    user_prompt=input_data.user_prompt,
                    brand_kit=brand_kit,
                )
            )
            
            if not format_result.success:
                raise ExecutionError(
                    f"Format decision failed: {format_result.error_message}"
                )
            
            self.logger.info(f"Format: {format_result.format_type} ({format_result.num_slides} slides)")
            self.logger.info(f"Rationale: {format_result.format_rationale}")
            
            # Step 3: Generate story narratives
            self.logger.info("")
            self.logger.info("─── STEP 3/6: STORY NARRATIVES ───")
            
            story_result = await story_generator.run(
                StoryGeneratorInput(
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
            
            self.logger.info(f"Complete Story: {story_result.complete_story}")
            self.logger.info(f"Story Rationale: {story_result.complete_story_rationale}")
            self.logger.info(f"Hook: {story_result.hook_slide_story}")
            self.logger.info(f"Body Slides:")
            for i, story in enumerate(story_result.body_slides_story, 1):
                self.logger.info(f"  {i}. {story}")
            
            # Step 4: Generate text captions (NEW ORDER - before images)
            self.logger.info("")
            self.logger.info("─── STEP 4/6: TEXT CAPTIONS ───")
            
            text_result = await text_generator.run(
                TextGeneratorInput(
                    brand_kit=brand_kit,
                    format_type=format_result.format_type,
                    hook_slide_story=story_result.hook_slide_story,
                    body_slides_story=story_result.body_slides_story,
                    complete_story=story_result.complete_story,
                )
            )
            
            if not text_result.success:
                raise ExecutionError(
                    f"Text generation failed: {text_result.error_message}"
                )
            
            self.logger.info(f"Hook Text: {text_result.hook_slide_text}")
            self.logger.info(f"Body Slide Texts:")
            for i, text in enumerate(text_result.body_slides_text, 1):
                self.logger.info(f"  {i}. {text}")
            
            # Step 5: Generate images WITH text (NEW ORDER - after captions)
            self.logger.info("")
            self.logger.info("─── STEP 5/6: AI IMAGES (WITH TEXT) ───")
            
            image_result = await image_generator.run(
                ImageGeneratorInput(
                    brand_kit=brand_kit,
                    format_type=format_result.format_type,
                    hook_slide_story=story_result.hook_slide_story,
                    complete_story=story_result.complete_story,
                    body_slides_story=story_result.body_slides_story,
                    hook_slide_text=text_result.hook_slide_text,
                    body_slides_text=text_result.body_slides_text,
                )
            )
            
            if not image_result.success:
                raise ExecutionError(
                    f"Image generation failed: {image_result.error_message}"
                )
            
            self.logger.info(f"Generated: 1 hook + {len(image_result.body_slides_images)} body images (with text rendered)")
            
            # Step 6: Validate quality and upload
            self.logger.info("")
            self.logger.info("─── STEP 6/6: QUALITY VALIDATION & UPLOAD ───")
            
            final_result = await finalizer.run(
                FinalizerInput(
                    format_type=format_result.format_type,
                    complete_story=story_result.complete_story,
                    hook_slide_story=story_result.hook_slide_story,
                    body_slides_story=story_result.body_slides_story,
                    hook_slide_text=text_result.hook_slide_text,
                    body_slides_text=text_result.body_slides_text,
                    hook_slide_image=image_result.hook_slide_image,
                    body_slides_images=image_result.body_slides_images,
                    brand_kit=brand_kit,
                )
            )
            
            if not final_result.success:
                raise ExecutionError(
                    f"Finalization failed: {final_result.error_message}"
                )
            
            # Calculate total duration
            pipeline_duration = int((time.time() - start_time) * 1000)
            duration_seconds = pipeline_duration / 1000
            duration_str = f"{int(duration_seconds // 60)}m {int(duration_seconds % 60)}s" if duration_seconds >= 60 else f"{duration_seconds:.1f}s"
            
            # Pipeline completion summary
            self.logger.info("")
            slide_count = len(final_result.carousel_slides_urls)
            self.logger.info("╔" + "═" * 78 + "╗")
            self.logger.info(f"║ PIPELINE COMPLETE | Duration: {duration_str:<8} | {slide_count} slides                   ║")
            self.logger.info(f"║ Carousel ID: {final_result.carousel_id}                            ║")
            self.logger.info("╚" + "═" * 78 + "╝")
            self.logger.info("")
            
            # Show local file paths if enabled
            if settings.save_local_output:
                from pathlib import Path
                local_dir = Path(settings.output_dir) / "carousels" / final_result.carousel_id / "final"
                self.logger.info("Output Files:")
                self.logger.info(f"  Location: {local_dir}/")
                for i in range(slide_count):
                    slide_type = "Hook" if i == 0 else f"Body {i}"
                    self.logger.info(f"    [{i}] {slide_type}: slide_{i}.png")
            else:
                self.logger.info("Local output saving is disabled")
                self.logger.info("View slides in Supabase Storage > carousel-slides bucket")
            self.logger.info("")
            
            # Display comprehensive evaluation metrics
            self.logger.info("╔" + "═" * 78 + "╗")
            self.logger.info("║" + " " * 22 + "EVALUATION METRICS" + " " * 38 + "║")
            self.logger.info("╚" + "═" * 78 + "╝")
            self.logger.info("")
            
            metrics = final_result.evaluation_metrics
            
            self.logger.info("FORMAT TYPE:")
            self.logger.info(f"  {metrics.format_type_evaluation}")
            self.logger.info("")
            
            self.logger.info("COMPLETE STORY:")
            self.logger.info(f"  {metrics.complete_story_evaluation}")
            self.logger.info("")
            
            self.logger.info("HOOK SLIDE STORY:")
            self.logger.info(f"  {metrics.hook_slide_story_evaluation}")
            self.logger.info("")
            
            self.logger.info("BODY SLIDES STORY:")
            for i, eval_text in enumerate(metrics.body_slides_story_evaluation, 1):
                self.logger.info(f"  [{i}] {eval_text}")
            self.logger.info("")
            
            self.logger.info("HOOK SLIDE TEXT:")
            self.logger.info(f"  {metrics.hook_slide_text_evaluation}")
            self.logger.info("")
            
            self.logger.info("BODY SLIDES TEXT:")
            for i, eval_text in enumerate(metrics.body_slides_text_evaluation, 1):
                self.logger.info(f"  [{i}] {eval_text}")
            self.logger.info("")
            
            self.logger.info("HOOK SLIDE IMAGE:")
            self.logger.info(f"  {metrics.hook_slide_image_evaluation}")
            self.logger.info("")
            
            self.logger.info("BODY SLIDES IMAGES:")
            for i, eval_text in enumerate(metrics.body_slides_images_evaluation, 1):
                self.logger.info(f"  [{i}] {eval_text}")
            self.logger.info("")
            
            self.logger.info("BRAND ALIGNMENT:")
            self.logger.info(f"  {metrics.brand_kit_evaluation}")
            self.logger.info("")
            
            self.logger.info("═" * 80)
            self.logger.info("")
            
            # Return orchestrator output
            return OrchestratorOutput(
                carousel_id=final_result.carousel_id,
                carousel_slides_urls=final_result.carousel_slides_urls,
                evaluation_metrics=final_result.evaluation_metrics,
            )
            
        except ExecutionError:
            # Re-raise execution errors from pipeline steps
            raise
        except Exception as e:
            # Catch any unexpected errors
            raise ExecutionError(f"Pipeline execution failed: {str(e)}")
        finally:
            # Clean up the run-specific log file handler
            if run_log_handler:
                logging.getLogger().removeHandler(run_log_handler)
                run_log_handler.close()
    
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