"""
Finalizer Agent - Step 6 of AI Pipeline

Validates image quality using Claude Vision and uploads carousel slides to storage.

Images already have text rendered by Gemini 3 Pro - no text overlay needed.
Uses Claude Vision to validate quality, extract rendered text, and check brand alignment.
Stores metrics for pipeline improvement (no retry logic in MVP).

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
from app.models.pipeline import FinalizerInput, FinalizerOutput, SlideQualityMetrics
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
        
        Args:
            input_data: Finalizer input schema
            
        Raises:
            ValidationError: If input is invalid
        """
        # Validate hook_slide_image
        if not input_data.hook_slide_image or not input_data.hook_slide_image.strip():
            raise ValidationError("hook_slide_image cannot be empty")
        
        # Validate hook_slide_text (for validation reference)
        if not input_data.hook_slide_text or not input_data.hook_slide_text.strip():
            raise ValidationError("hook_slide_text cannot be empty")
        
        # Validate hook_slide_story (for context validation)
        if not input_data.hook_slide_story or not input_data.hook_slide_story.strip():
            raise ValidationError("hook_slide_story cannot be empty")
        
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
        
        # Validate body_slides_story (for context validation)
        if not input_data.body_slides_story:
            raise ValidationError("body_slides_story cannot be empty")
        
        if not isinstance(input_data.body_slides_story, list):
            raise ValidationError("body_slides_story must be a list")
        
        # Check array length match
        body_length = len(input_data.body_slides_images)
        if len(input_data.body_slides_text) != body_length:
            raise ValidationError(
                f"body_slides_images ({body_length}) and "
                f"body_slides_text ({len(input_data.body_slides_text)}) must have the same length"
            )
        
        if len(input_data.body_slides_story) != body_length:
            raise ValidationError(
                f"body_slides_images ({body_length}) and "
                f"body_slides_story ({len(input_data.body_slides_story)}) must have the same length"
            )
        
        # Validate each body slide image
        for i, image in enumerate(input_data.body_slides_images):
            if not image or not isinstance(image, str) or not image.strip():
                raise ValidationError(f"body_slides_images[{i}] is empty or invalid")
        
        # Validate each body slide text
        for i, text in enumerate(input_data.body_slides_text):
            if not text or not isinstance(text, str) or not text.strip():
                raise ValidationError(f"body_slides_text[{i}] is empty or invalid")
        
        # Validate each body slide story
        for i, story in enumerate(input_data.body_slides_story):
            if not story or not isinstance(story, str) or not story.strip():
                raise ValidationError(f"body_slides_story[{i}] is empty or invalid")
        
        self.logger.debug("Input validation passed")
    
    async def _execute(self, input_data: FinalizerInput) -> FinalizerOutput:
        """
        Execute finalization logic - validate images and upload to storage.
        
        Images already have text rendered. This step validates quality and uploads.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Carousel ID, URLs, and quality metrics
            
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
            self.logger.debug(f"Validating and uploading {total_slides} slides")
            
            # Process hook slide
            self.logger.debug("Validating hook slide")
            hook_metrics, hook_url = await self._validate_and_upload_slide(
                image_base64=input_data.hook_slide_image,
                expected_text=input_data.hook_slide_text,
                story_context=input_data.hook_slide_story,
                carousel_id=carousel_id,
                slide_index=0,
                is_hook=True,
                brand_kit=input_data.brand_kit,
                local_output_dir=local_output_dir,
            )
            
            # Process body slides
            body_metrics: List[SlideQualityMetrics] = []
            body_urls: List[str] = []
            
            for i, (image, text, story) in enumerate(zip(
                input_data.body_slides_images,
                input_data.body_slides_text,
                input_data.body_slides_story
            )):
                self.logger.debug(f"Validating body slide {i+1}/{len(input_data.body_slides_images)}")
                metrics, url = await self._validate_and_upload_slide(
                    image_base64=image,
                    expected_text=text,
                    story_context=story,
                    carousel_id=carousel_id,
                    slide_index=i + 1,
                    is_hook=False,
                    brand_kit=input_data.brand_kit,
                    local_output_dir=local_output_dir,
                )
                body_metrics.append(metrics)
                body_urls.append(url)
            
            # Combine all URLs and metrics
            all_urls = [hook_url] + body_urls
            all_metrics = [hook_metrics] + body_metrics
            
            # Calculate overall quality score
            overall_quality = sum(m.image_quality_score for m in all_metrics) / len(all_metrics)
            
            self.logger.debug(
                f"Finalization completed: {len(all_urls)} slides uploaded, "
                f"overall quality: {overall_quality:.2f}"
            )
            
            if settings.save_local_output:
                self.logger.debug(f"Local files saved to: {carousel_output_dir}")
            
            return FinalizerOutput(
                step_name="finalizer",
                success=True,
                carousel_id=carousel_id,
                carousel_slides_urls=all_urls,
                quality_metrics=all_metrics,
            )
            
        except Exception as e:
            raise ExecutionError(f"Unexpected error during finalization: {str(e)}")
    
    async def _validate_and_upload_slide(
        self,
        image_base64: str,
        expected_text: str,
        story_context: str,
        carousel_id: str,
        slide_index: int,
        is_hook: bool,
        brand_kit: BrandKit,
        local_output_dir: Optional[Path] = None,
    ) -> Tuple[SlideQualityMetrics, str]:
        """
        Validate a single slide using Claude Vision and upload to storage.
        
        Image already has text rendered by Gemini 3 Pro.
        This method validates quality and uploads.
        
        Args:
            image_base64: Base64 encoded image with text rendered
            expected_text: The text that should be in the image
            story_context: The story context for this slide
            carousel_id: Unique carousel identifier
            slide_index: Index of this slide (0 = hook, 1+ = body)
            is_hook: Whether this is the hook slide
            brand_kit: Brand kit for brand compliance validation
            local_output_dir: Optional directory to save image locally
            
        Returns:
            Tuple of (quality_metrics, public_url)
            
        Raises:
            ExecutionError: If validation or upload fails
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
            
            # Validate image quality using Claude Vision
            self.logger.debug(f"Validating slide {slide_index} quality")
            quality_metrics = await self._validate_slide_quality(
                image_base64=image_base64,
                expected_text=expected_text,
                story_context=story_context,
                slide_index=slide_index,
                is_hook=is_hook,
                brand_kit=brand_kit,
            )
            
            # Upload to Supabase Storage
            file_path = f"carousels/{carousel_id}/slide_{slide_index}.png"
            public_url = await self._upload_to_storage(image_bytes, file_path)
            
            self.logger.debug(
                f"Slide {slide_index} validated (quality: {quality_metrics.image_quality_score:.2f}) "
                f"and uploaded"
            )
            
            return (quality_metrics, public_url)
            
        except Exception as e:
            self.logger.error(f"Failed to validate/upload slide {slide_index}: {e}")
            raise ExecutionError(f"Failed to validate/upload slide {slide_index}: {str(e)}")
    
    async def _validate_slide_quality(
        self,
        image_base64: str,
        expected_text: str,
        story_context: str,
        slide_index: int,
        is_hook: bool,
        brand_kit: BrandKit,
    ) -> SlideQualityMetrics:
        """
        Validate slide quality using Claude Vision.
        
        Checks text readability, accuracy, image quality, and brand alignment.
        
        Args:
            image_base64: Base64 encoded image to validate
            expected_text: The text that should appear in the image
            story_context: The story context for this slide
            slide_index: Index of this slide
            is_hook: Whether this is the hook slide
            brand_kit: Brand kit for brand compliance
            
        Returns:
            SlideQualityMetrics with validation results
            
        Raises:
            ExecutionError: If validation fails
        """
        try:
            # Build validation prompt
            validation_prompt = self._build_validation_prompt(
                expected_text=expected_text,
                story_context=story_context,
                is_hook=is_hook,
                brand_kit=brand_kit,
            )
            
            # Convert base64 to data URL for Claude Vision
            image_data_url = f"data:image/png;base64,{image_base64}"
            
            # Call Claude Vision
            response = await self.anthropic.analyze_image(
                image_url=image_data_url,
                prompt=validation_prompt,
                max_tokens=1000,
            )
            
            # Parse validation response
            metrics = self._parse_validation_response(
                response=response,
                slide_index=slide_index,
                expected_text=expected_text,
            )
            
            return metrics
            
        except AnthropicServiceError as e:
            self.logger.error(f"Claude Vision validation failed: {e}")
            # Return default metrics on failure (MVP: accept all)
            return SlideQualityMetrics(
                slide_index=slide_index,
                text_readable=True,
                text_matches_expected=True,
                text_accuracy_score=0.5,
                image_quality_score=0.5,
                brand_alignment_score=None,
                issues=["Validation failed - using default metrics"],
                suggestions=[],
            )
        except Exception as e:
            self.logger.error(f"Unexpected validation error: {e}")
            return SlideQualityMetrics(
                slide_index=slide_index,
                text_readable=True,
                text_matches_expected=True,
                text_accuracy_score=0.5,
                image_quality_score=0.5,
                brand_alignment_score=None,
                issues=[f"Validation error: {str(e)}"],
                suggestions=[],
            )
    
    def _build_validation_prompt(
        self,
        expected_text: str,
        story_context: str,
        is_hook: bool,
        brand_kit: BrandKit,
    ) -> str:
        """
        Build validation prompt for Claude Vision.
        
        Args:
            expected_text: Text that should be in the image
            story_context: Story context for this slide
            is_hook: Whether this is the hook slide
            brand_kit: Brand kit for compliance checking
            
        Returns:
            Validation prompt string
        """
        brand_info = ""
        if brand_kit:
            brand_info = f"""
BRAND CONTEXT:
- Brand Name: {brand_kit.brand_name}
- Brand Style: {brand_kit.brand_style}
- Brand Niche: {brand_kit.brand_niche}
"""
        
        slide_type = "HOOK SLIDE (first slide)" if is_hook else "BODY SLIDE"
        
        return f"""You are a quality assurance expert for social media carousel images. Analyze this {slide_type} and provide detailed quality metrics.

EXPECTED TEXT: "{expected_text}"
STORY CONTEXT: "{story_context}"
{brand_info}

VALIDATION TASKS:

1. TEXT READABILITY:
   - Is the text clearly visible and readable on mobile?
   - Is there sufficient contrast between text and background?
   - Is the text size appropriate for quick scanning?

2. TEXT ACCURACY:
   - Extract the text you see in the image
   - Compare it to the expected text: "{expected_text}"
   - Calculate similarity (0-1, where 1 = perfect match)

3. IMAGE QUALITY:
   - Overall visual quality and professionalism
   - Image clarity and resolution
   - Composition and visual appeal
   - Appropriate for Instagram/TikTok

4. BRAND ALIGNMENT:
   - Does the visual style match the brand style?
   - Is it appropriate for the brand niche?
   - Professional and on-brand appearance?

5. ISSUES & SUGGESTIONS:
   - List any problems or concerns
   - Suggest improvements

OUTPUT FORMAT (JSON only):
{{
  "text_readable": true/false,
  "extracted_text": "the text you see in the image",
  "text_accuracy_score": 0.0-1.0,
  "image_quality_score": 0.0-1.0,
  "brand_alignment_score": 0.0-1.0 or null,
  "issues": ["issue 1", "issue 2"],
  "suggestions": ["suggestion 1", "suggestion 2"]
}}

Provide detailed, actionable feedback. Be honest but constructive."""
    
    def _parse_validation_response(
        self,
        response: str,
        slide_index: int,
        expected_text: str,
    ) -> SlideQualityMetrics:
        """
        Parse Claude Vision validation response.
        
        Args:
            response: Raw response from Claude Vision
            slide_index: Index of this slide
            expected_text: Expected text for fallback
            
        Returns:
            SlideQualityMetrics
        """
        import json
        
        # Clean response
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        # Parse JSON
        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to extract JSON
            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                result = json.loads(cleaned[start_idx:end_idx])
            else:
                # Return default metrics
                return SlideQualityMetrics(
                    slide_index=slide_index,
                    text_readable=True,
                    text_matches_expected=True,
                    text_accuracy_score=0.7,
                    image_quality_score=0.7,
                    brand_alignment_score=None,
                    issues=["Could not parse validation response"],
                    suggestions=[],
                )
        
        # Extract text match
        extracted_text = result.get("extracted_text", "")
        text_matches = extracted_text.lower().strip() == expected_text.lower().strip()
        
        return SlideQualityMetrics(
            slide_index=slide_index,
            text_readable=result.get("text_readable", True),
            text_matches_expected=text_matches,
            text_accuracy_score=result.get("text_accuracy_score", 0.7),
            image_quality_score=result.get("image_quality_score", 0.7),
            brand_alignment_score=result.get("brand_alignment_score"),
            issues=result.get("issues", []),
            suggestions=result.get("suggestions", []),
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