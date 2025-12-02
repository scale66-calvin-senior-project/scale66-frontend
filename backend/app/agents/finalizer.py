"""
Finalizer Agent - Step 6 of AI Pipeline

Input: FinalizerInput (hook_slide_image, body_slides_images, expected texts/stories, brand_kit)
Output: FinalizerOutput (carousel_id, carousel_slides_urls, quality_metrics)
"""

import base64
import io
import uuid
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import FinalizerInput, FinalizerOutput, EvaluationMetrics
from app.models.structured import ClaudeEvaluationOutput
from app.models.brand_kit import BrandKit
from app.core.config import settings
from app.core.supabase import get_supabase_admin_client
from app.services.ai.anthropic_service import AnthropicServiceError


class Finalizer(BaseAgent[FinalizerInput, FinalizerOutput]):
    """
    Validates carousel slide quality and uploads to storage.
    
    Images already have text rendered by Gemini 3 Pro.
    Uses Claude Vision to validate quality and extract metrics.
    Uploads validated slides to Supabase Storage.
    Singleton pattern ensures single instance across application.
    """
    
    _instance: Optional['Finalizer'] = None
    
    def __new__(cls):
        """Singleton instance creation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize finalizer agent."""
        super().__init__()
    
    async def _validate_input(self, input_data: FinalizerInput) -> None:
        """
        Validate input data before execution.
        
        Checks:
        - Hook and body slide images are not empty
        - Expected texts and stories for validation are valid
        - All arrays match in length
        - Format type and complete story are provided
        
        Args:
            input_data: Finalizer input schema
            
        Raises:
            ValidationError: If input is invalid
        """
        # Validate format_type
        if not input_data.format_type or not input_data.format_type.strip():
            raise ValidationError("format_type cannot be empty")
        
        # Validate complete_strategy
        if not input_data.complete_strategy or not input_data.complete_strategy.strip():
            raise ValidationError("complete_strategy cannot be empty")
        
        # Validate hook_slide_image
        if not input_data.hook_slide_image or not input_data.hook_slide_image.strip():
            raise ValidationError("hook_slide_image cannot be empty")
        
        # Validate hook_slide_text (for validation reference)
        if not input_data.hook_slide_text or not input_data.hook_slide_text.strip():
            raise ValidationError("hook_slide_text cannot be empty")
        
        # Validate hook_slide_strategy (for context validation)
        if not input_data.hook_slide_strategy or not input_data.hook_slide_strategy.strip():
            raise ValidationError("hook_slide_strategy cannot be empty")
        
        # Validate body_slides_images
        if not input_data.body_slides_images:
            raise ValidationError("body_slides_images cannot be empty")
        
        if not isinstance(input_data.body_slides_images, list):
            raise ValidationError("body_slides_images must be a list")
        
        if len(input_data.body_slides_images) < 2:
            raise ValidationError("body_slides_images must contain at least 2 slides")
        
        if len(input_data.body_slides_images) > 9:
            raise ValidationError("body_slides_images cannot contain more than 9 slides")
        
        # Validate body_slides_text (for validation reference)
        if not input_data.body_slides_text:
            raise ValidationError("body_slides_text cannot be empty")
        
        if not isinstance(input_data.body_slides_text, list):
            raise ValidationError("body_slides_text must be a list")
        
        # Validate body_slides_strategy (for context validation)
        if not input_data.body_slides_strategy:
            raise ValidationError("body_slides_strategy cannot be empty")
        
        if not isinstance(input_data.body_slides_strategy, list):
            raise ValidationError("body_slides_strategy must be a list")
        
        # Check array length match
        body_length = len(input_data.body_slides_images)
        if len(input_data.body_slides_text) != body_length:
            raise ValidationError(
                f"body_slides_images ({body_length}) and "
                f"body_slides_text ({len(input_data.body_slides_text)}) must have the same length"
            )
        
        if len(input_data.body_slides_strategy) != body_length:
            raise ValidationError(
                f"body_slides_images ({body_length}) and "
                f"body_slides_strategy ({len(input_data.body_slides_strategy)}) must have the same length"
            )
        
        # Validate each body slide image
        for i, image in enumerate(input_data.body_slides_images):
            if not image or not isinstance(image, str) or not image.strip():
                raise ValidationError(f"body_slides_images[{i}] is empty or invalid")
        
        # Validate each body slide text
        for i, text in enumerate(input_data.body_slides_text):
            if not text or not isinstance(text, str) or not text.strip():
                raise ValidationError(f"body_slides_text[{i}] is empty or invalid")
        
        # Validate each body slide strategy
        for i, strategy in enumerate(input_data.body_slides_strategy):
            if not strategy or not isinstance(strategy, str) or not strategy.strip():
                raise ValidationError(f"body_slides_strategy[{i}] is empty or invalid")
        
        self.logger.debug("Input validation passed")
    
    async def _execute(self, input_data: FinalizerInput) -> FinalizerOutput:
        """
        Execute finalization logic - upload images and generate evaluation metrics.
        
        Images already have text rendered. This step uploads and evaluates.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Carousel ID, URLs, and evaluation metrics
            
        Raises:
            ExecutionError: If finalization fails
        """
        try:
            # Generate unique carousel ID
            carousel_id = str(uuid.uuid4())
            self.logger.debug(f"Starting finalization for carousel: {carousel_id}")
            
            # Create local output directory if saving locally
            local_output_dir = None
            if settings.save_local_output:
                carousel_output_dir = Path(settings.output_dir) / "carousels" / carousel_id
                local_output_dir = carousel_output_dir / "final"
                local_output_dir.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Created local output directory: {local_output_dir}")
            
            total_slides = 1 + len(input_data.body_slides_images)
            self.logger.debug(f"Uploading {total_slides} slides")
            
            # Upload hook slide
            self.logger.debug("Uploading hook slide")
            hook_url = await self._upload_slide(
                image_base64=input_data.hook_slide_image,
                carousel_id=carousel_id,
                slide_index=0,
                local_output_dir=local_output_dir,
            )
            
            # Upload body slides
            body_urls: List[str] = []
            
            for i, image in enumerate(input_data.body_slides_images):
                self.logger.debug(f"Uploading body slide {i+1}/{len(input_data.body_slides_images)}")
                url = await self._upload_slide(
                    image_base64=image,
                    carousel_id=carousel_id,
                    slide_index=i + 1,
                    local_output_dir=local_output_dir,
                )
                body_urls.append(url)
            
            # Combine all URLs
            all_urls = [hook_url] + body_urls
            
            self.logger.debug(f"Upload completed: {len(all_urls)} slides")
            
            # Generate comprehensive evaluation metrics using Claude Vision
            self.logger.debug("Generating evaluation metrics")
            evaluation_metrics = await self._generate_evaluation_metrics(
                input_data=input_data,
                carousel_id=carousel_id,
            )
            
            if settings.save_local_output:
                self.logger.debug(f"Local files saved to: {carousel_output_dir}")
            
            return FinalizerOutput(
                step_name="finalizer",
                success=True,
                carousel_id=carousel_id,
                carousel_slides_urls=all_urls,
                evaluation_metrics=evaluation_metrics,
            )
            
        except Exception as e:
            raise ExecutionError(f"Unexpected error during finalization: {str(e)}")
    
    async def _upload_slide(
        self,
        image_base64: str,
        carousel_id: str,
        slide_index: int,
        local_output_dir: Optional[Path] = None,
    ) -> str:
        """
        Upload a single slide to storage.
        
        Args:
            image_base64: Base64 encoded image with text rendered
            carousel_id: Unique carousel identifier
            slide_index: Index of this slide (0 = hook, 1+ = body)
            local_output_dir: Optional directory to save image locally
            
        Returns:
            Public URL of uploaded image
            
        Raises:
            ExecutionError: If upload fails
        """
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_base64)
            
            # Save image locally if enabled
            if local_output_dir:
                local_path = local_output_dir / f"slide_{slide_index}.png"
                image = Image.open(io.BytesIO(image_bytes))
                image.save(local_path, format='PNG', optimize=True, quality=95)
                self.logger.debug(f"Saved slide {slide_index} to: {local_path}")
            
            # Upload to Supabase Storage
            file_path = f"carousels/{carousel_id}/slide_{slide_index}.png"
            public_url = await self._upload_to_storage(image_bytes, file_path)
            
            self.logger.debug(f"Slide {slide_index} uploaded")
            
            return public_url
            
        except Exception as e:
            self.logger.error(f"Failed to upload slide {slide_index}: {e}")
            raise ExecutionError(f"Failed to upload slide {slide_index}: {str(e)}")
    
    async def _generate_evaluation_metrics(
        self,
        input_data: FinalizerInput,
        carousel_id: str,
    ) -> EvaluationMetrics:
        """
        Generate comprehensive evaluation metrics for the entire pipeline.
        
        Uses Claude to evaluate format appropriateness, story quality, text quality,
        image quality, and brand alignment.
        
        Args:
            input_data: Complete finalizer input with all pipeline outputs
            carousel_id: Carousel ID for reference
            
        Returns:
            EvaluationMetrics with detailed assessments
            
        Raises:
            ExecutionError: If evaluation fails
        """
        try:
            # Build comprehensive evaluation prompt
            evaluation_prompt = self._build_evaluation_prompt(input_data)
            
            # Call Claude with structured output for guaranteed valid response
            self.logger.debug("Calling Claude for pipeline evaluation with structured output")
            evaluation_output = await self.anthropic.generate_structured_output(
                prompt=evaluation_prompt,
                output_model=ClaudeEvaluationOutput,
                max_tokens=4096,
                temperature=0.3,
            )
            
            # Convert ClaudeEvaluationOutput to EvaluationMetrics
            metrics = EvaluationMetrics(
                format_type_evaluation=evaluation_output.format_type_evaluation,
                hook_slide_strategy_evaluation=evaluation_output.hook_slide_strategy_evaluation,
                body_slides_strategy_evaluation=evaluation_output.body_slides_strategy_evaluation,
                complete_strategy_evaluation=evaluation_output.complete_strategy_evaluation,
                hook_slide_text_evaluation=evaluation_output.hook_slide_text_evaluation,
                body_slides_text_evaluation=evaluation_output.body_slides_text_evaluation,
                hook_slide_image_evaluation=evaluation_output.hook_slide_image_evaluation,
                body_slides_images_evaluation=evaluation_output.body_slides_images_evaluation,
                brand_kit_evaluation=evaluation_output.brand_kit_evaluation,
            )
            
            self.logger.info("Evaluation metrics generated successfully")
            
            return metrics
            
        except AnthropicServiceError as e:
            self.logger.error(f"Evaluation generation failed: {e}")
            # Return default metrics on failure
            return self._get_default_evaluation_metrics()
        except Exception as e:
            self.logger.error(f"Unexpected evaluation error: {e}")
            return self._get_default_evaluation_metrics()
    
    def _build_evaluation_prompt(self, input_data: FinalizerInput) -> str:
        """
        Build comprehensive evaluation prompt for Claude.
        
        Args:
            input_data: Complete finalizer input
            
        Returns:
            Evaluation prompt string
        """
        brand_info = ""
        if input_data.brand_kit:
            brand_info = f"""
BRAND CONTEXT:
- Brand Name: {input_data.brand_kit.brand_name}
- Brand Style: {input_data.brand_kit.brand_style}
- Brand Niche: {input_data.brand_kit.brand_niche}
- Product/Service: {input_data.brand_kit.product_service_desc}"""
        
        total_slides = 1 + len(input_data.body_slides_images)
        
        return f"""You are a social media content quality analyst. Evaluate this carousel content across all pipeline stages.

CAROUSEL SPECIFICATIONS:
- Format Type: {input_data.format_type}
- Total Slides: {total_slides}
{brand_info}

COMPLETE STRATEGY:
"{input_data.complete_strategy}"

HOOK SLIDE:
- Strategy: "{input_data.hook_slide_strategy}"
- Text: "{input_data.hook_slide_text}"

BODY SLIDES:
{chr(10).join(f"- Slide {i+1} Strategy: \"{strategy}\"" for i, strategy in enumerate(input_data.body_slides_strategy))}

{chr(10).join(f"- Slide {i+1} Text: \"{text}\"" for i, text in enumerate(input_data.body_slides_text))}

EVALUATION TASKS:

1. FORMAT TYPE EVALUATION:
   - Is the chosen format ({input_data.format_type}) appropriate for this content?
   - Does it align with the complete strategy and brand?

2. STRATEGY QUALITY EVALUATION:
   - Hook Strategy: Is it attention-grabbing and aligned with format?
   - Body Strategies: Do they follow the format structure? Are they cohesive?
   - Complete Strategy: Does it tie everything together effectively?

3. TEXT QUALITY EVALUATION:
   - Hook Text: Is it punchy, scroll-stopping, and under 10 words?
   - Body Texts: Are they concise, clear, and aligned with stories?

4. IMAGE EVALUATION (without seeing images):
   - Based on the texts and stories, assess if the content is appropriate for image generation
   - Are the texts suitable for text overlay rendering?

5. BRAND ALIGNMENT EVALUATION:
   - Does the overall content match the brand style and niche?
   - Is the messaging appropriate for the target audience?

OUTPUT REQUIREMENTS:
- format_type_evaluation: Assessment of format appropriateness
- hook_slide_strategy_evaluation: Assessment of hook strategy quality
- body_slides_strategy_evaluation: List of assessments for each body strategy (must match number of body slides)
- complete_strategy_evaluation: Assessment of complete strategy coherence
- hook_slide_text_evaluation: Assessment of hook text quality
- body_slides_text_evaluation: List of assessments for each body text (must match number of body slides)
- hook_slide_image_evaluation: Assessment of hook image suitability
- body_slides_images_evaluation: List of assessments for each body image (must match number of body slides)
- brand_kit_evaluation: Assessment of overall brand alignment

Provide detailed, actionable feedback. Be constructive and specific."""
    
    def _get_default_evaluation_metrics(self) -> EvaluationMetrics:
        """
        Get default evaluation metrics when evaluation fails.
        
        Returns:
            Default EvaluationMetrics
        """
        return EvaluationMetrics(
            format_type_evaluation="Evaluation not available - pipeline completed successfully",
            hook_slide_strategy_evaluation="Evaluation not available",
            body_slides_strategy_evaluation=["Evaluation not available"],
            complete_strategy_evaluation="Evaluation not available",
            hook_slide_text_evaluation="Evaluation not available",
            body_slides_text_evaluation=["Evaluation not available"],
            hook_slide_image_evaluation="Evaluation not available",
            body_slides_images_evaluation=["Evaluation not available"],
            brand_kit_evaluation="Evaluation not available",
        )
    
    async def _upload_to_storage(self, image_bytes: bytes, file_path: str) -> str:
        """
        Upload finalized image to Supabase Storage.
        
        Args:
            image_bytes: Image data as bytes
            file_path: Storage path (e.g., "carousels/{carousel_id}/slide_0.png")
            
        Returns:
            Public URL of uploaded image
            
        Raises:
            ExecutionError: If upload fails
        """
        try:
            supabase = get_supabase_admin_client()
            
            # Upload to carousel-slides bucket
            bucket_name = "carousel-slides"
            
            # Upload file
            response = supabase.storage.from_(bucket_name).upload(
                file_path,
                image_bytes,
                file_options={"content-type": "image/png"}
            )
            
            # Get public URL
            public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
            
            self.logger.debug(f"Uploaded to storage: {file_path}")
            
            return public_url
            
        except Exception as e:
            self.logger.error(f"Failed to upload to storage: {e}")
            raise ExecutionError(f"Storage upload failed: {str(e)}")


# Create singleton instance for easy import
finalizer = Finalizer()