"""
Finalizer Agent - Step 6 of AI Pipeline

Overlays text on generated images and uploads final carousel slides to storage.

Input: FinalizerInput (hook_slide_text, body_slides_text, hook_slide_text_style, body_slides_text_styles, hook_slide_image, body_slides_images)
Output: FinalizerOutput (carousel_id, carousel_slides_urls)
"""

import base64
import io
import logging
import re
import uuid
from typing import Dict, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import FinalizerInput, FinalizerOutput
from app.core.supabase import get_supabase_admin_client


logger = logging.getLogger(__name__)


class Finalizer(BaseAgent[FinalizerInput, FinalizerOutput]):
    """
    Finalizes carousel slides by overlaying text on images and uploading to storage.
    
    Uses Pillow for image composition and Supabase Storage for hosting.
    """
    
    async def _validate_input(self, input_data: FinalizerInput) -> None:
        """
        Validate input data before execution.
        
        Checks:
        - Hook slide text and style are not empty
        - Body slides text, styles, and images arrays match in length
        - All required fields are valid
        
        Args:
            input_data: Finalizer input schema
            
        Raises:
            ValidationError: If input is invalid
        """
        # Validate hook_slide_text
        if not input_data.hook_slide_text or not input_data.hook_slide_text.strip():
            raise ValidationError("hook_slide_text cannot be empty")
        
        # Validate hook_slide_text_style
        if not input_data.hook_slide_text_style or not input_data.hook_slide_text_style.strip():
            raise ValidationError("hook_slide_text_style cannot be empty")
        
        # Validate hook_slide_image
        if not input_data.hook_slide_image or not input_data.hook_slide_image.strip():
            raise ValidationError("hook_slide_image cannot be empty")
        
        # Validate body_slides_text
        if not input_data.body_slides_text:
            raise ValidationError("body_slides_text cannot be empty")
        
        if not isinstance(input_data.body_slides_text, list):
            raise ValidationError("body_slides_text must be a list")
        
        if len(input_data.body_slides_text) < 2:
            raise ValidationError("body_slides_text must contain at least 2 slides")
        
        if len(input_data.body_slides_text) > 9:
            raise ValidationError("body_slides_text cannot contain more than 9 slides")
        
        # Validate body_slides_text_styles
        if not input_data.body_slides_text_styles:
            raise ValidationError("body_slides_text_styles cannot be empty")
        
        if not isinstance(input_data.body_slides_text_styles, list):
            raise ValidationError("body_slides_text_styles must be a list")
        
        # Validate body_slides_images
        if not input_data.body_slides_images:
            raise ValidationError("body_slides_images cannot be empty")
        
        if not isinstance(input_data.body_slides_images, list):
            raise ValidationError("body_slides_images must be a list")
        
        # Check array length match
        body_length = len(input_data.body_slides_text)
        if len(input_data.body_slides_text_styles) != body_length:
            raise ValidationError(
                f"body_slides_text ({body_length}) and "
                f"body_slides_text_styles ({len(input_data.body_slides_text_styles)}) must have the same length"
            )
        
        if len(input_data.body_slides_images) != body_length:
            raise ValidationError(
                f"body_slides_text ({body_length}) and "
                f"body_slides_images ({len(input_data.body_slides_images)}) must have the same length"
            )
        
        # Validate each body slide text
        for i, text in enumerate(input_data.body_slides_text):
            if not text or not isinstance(text, str) or not text.strip():
                raise ValidationError(f"body_slides_text[{i}] is empty or invalid")
        
        # Validate each body slide style
        for i, style in enumerate(input_data.body_slides_text_styles):
            if not style or not isinstance(style, str) or not style.strip():
                raise ValidationError(f"body_slides_text_styles[{i}] is empty or invalid")
        
        # Validate each body slide image
        for i, image in enumerate(input_data.body_slides_images):
            if not image or not isinstance(image, str) or not image.strip():
                raise ValidationError(f"body_slides_images[{i}] is empty or invalid")
        
        self.logger.debug("Input validation passed")
    
    async def _execute(self, input_data: FinalizerInput) -> FinalizerOutput:
        """
        Execute finalization logic - overlay text on images and upload to storage.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Carousel ID and URLs of finalized slides
            
        Raises:
            ExecutionError: If finalization fails
        """
        try:
            # Generate unique carousel ID
            carousel_id = str(uuid.uuid4())
            self.logger.info(f"Starting finalization for carousel: {carousel_id}")
            
            total_slides = 1 + len(input_data.body_slides_text)
            self.logger.info(f"Finalizing {total_slides} slides")
            
            # Process hook slide
            self.logger.info("Finalizing hook slide")
            hook_url = await self._finalize_slide(
                text=input_data.hook_slide_text,
                style=input_data.hook_slide_text_style,
                image_base64=input_data.hook_slide_image,
                carousel_id=carousel_id,
                slide_index=0,
            )
            
            # Process body slides
            body_urls: List[str] = []
            for i, (text, style, image) in enumerate(zip(
                input_data.body_slides_text,
                input_data.body_slides_text_styles,
                input_data.body_slides_images
            )):
                self.logger.info(f"Finalizing body slide {i+1}/{len(input_data.body_slides_text)}")
                body_url = await self._finalize_slide(
                    text=text,
                    style=style,
                    image_base64=image,
                    carousel_id=carousel_id,
                    slide_index=i + 1,
                )
                body_urls.append(body_url)
            
            # Combine all URLs
            all_urls = [hook_url] + body_urls
            
            self.logger.info(
                f"Finalization completed successfully: {len(all_urls)} slides uploaded"
            )
            
            return FinalizerOutput(
                step_name="finalizer",
                success=True,
                carousel_id=carousel_id,
                carousel_slides_urls=all_urls,
            )
            
        except Exception as e:
            raise ExecutionError(f"Unexpected error during finalization: {str(e)}")
    
    async def _finalize_slide(
        self,
        text: str,
        style: str,
        image_base64: str,
        carousel_id: str,
        slide_index: int,
    ) -> str:
        """
        Finalize a single slide by overlaying text on image and uploading to storage.
        
        Args:
            text: Text to overlay
            style: Styling specification
            image_base64: Base64 encoded background image
            carousel_id: Unique carousel identifier
            slide_index: Index of this slide (0 = hook, 1+ = body)
            
        Returns:
            Public URL of the finalized slide
            
        Raises:
            ExecutionError: If finalization fails
        """
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Parse style specifications
            style_dict = self._parse_style(style)
            
            # Create text overlay
            final_image = self._overlay_text(image, text, style_dict)
            
            # Convert to bytes
            output_buffer = io.BytesIO()
            final_image.save(output_buffer, format='PNG', optimize=True, quality=95)
            output_bytes = output_buffer.getvalue()
            
            # Upload to Supabase Storage
            file_path = f"carousels/{carousel_id}/slide_{slide_index}.png"
            public_url = await self._upload_to_storage(output_bytes, file_path)
            
            self.logger.debug(f"Slide {slide_index} finalized and uploaded: {public_url}")
            
            return public_url
            
        except Exception as e:
            self.logger.error(f"Failed to finalize slide {slide_index}: {e}")
            raise ExecutionError(f"Failed to finalize slide {slide_index}: {str(e)}")
    
    def _parse_style(self, style: str) -> Dict[str, any]:
        """
        Parse style specification string into dictionary.
        
        Example input:
        "font_size: 18% of slide height, color: #FFFFFF, position: top-center, 
         alignment: center, background: rgba(0,0,0,0.4), text_shadow: 2px 2px 4px rgba(0,0,0,0.8)"
        
        Args:
            style: Style specification string
            
        Returns:
            Dictionary with parsed style parameters
        """
        style_dict = {
            "font_size_percent": 16,  # Default 16% of height
            "color": "#FFFFFF",
            "position": "center",
            "alignment": "center",
            "background": None,
            "text_shadow": None,
            "padding": 20,
        }
        
        # Parse font_size (percentage of slide height)
        font_size_match = re.search(r'font_size:\s*(\d+)%', style)
        if font_size_match:
            style_dict["font_size_percent"] = int(font_size_match.group(1))
        
        # Parse color
        color_match = re.search(r'color:\s*(#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3})', style)
        if color_match:
            style_dict["color"] = color_match.group(1)
        
        # Parse position (top/center/bottom or combinations)
        position_match = re.search(r'position:\s*([\w-]+)', style)
        if position_match:
            style_dict["position"] = position_match.group(1)
        
        # Parse alignment
        alignment_match = re.search(r'alignment:\s*(\w+)', style)
        if alignment_match:
            style_dict["alignment"] = alignment_match.group(1)
        
        # Parse background (rgba or rgb)
        background_match = re.search(r'background:\s*(rgba?\([^)]+\))', style)
        if background_match:
            style_dict["background"] = background_match.group(1)
        
        # Parse text_shadow
        shadow_match = re.search(r'text_shadow:\s*([^,;]+)', style)
        if shadow_match:
            style_dict["text_shadow"] = shadow_match.group(1).strip()
        
        # Parse padding
        padding_match = re.search(r'padding:\s*(\d+)', style)
        if padding_match:
            style_dict["padding"] = int(padding_match.group(1))
        
        return style_dict
    
    def _overlay_text(
        self,
        image: Image.Image,
        text: str,
        style_dict: Dict[str, any],
    ) -> Image.Image:
        """
        Overlay text on image using Pillow with specified styling.
        
        Args:
            image: PIL Image object
            text: Text to overlay
            style_dict: Parsed style specifications
            
        Returns:
            PIL Image with text overlay
        """
        # Create a copy to work with
        img = image.copy()
        width, height = img.size
        
        # Calculate font size based on percentage of height
        font_size = int(height * (style_dict["font_size_percent"] / 100))
        
        # Load font (use default if custom not available)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            self.logger.warning("Could not load custom font, using default")
            font = ImageFont.load_default()
        
        # Create drawing context
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Calculate text bbox for positioning
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Determine text position based on style
        x, y = self._calculate_text_position(
            width, height, text_width, text_height,
            style_dict["position"], style_dict["alignment"], style_dict["padding"]
        )
        
        # Draw background if specified
        if style_dict["background"]:
            bg_padding = 20
            bg_bbox = (
                x - bg_padding,
                y - bg_padding,
                x + text_width + bg_padding,
                y + text_height + bg_padding
            )
            bg_color = self._parse_rgba(style_dict["background"])
            draw.rectangle(bg_bbox, fill=bg_color)
        
        # Draw text shadow if specified
        if style_dict["text_shadow"]:
            shadow_offset = self._parse_text_shadow(style_dict["text_shadow"])
            shadow_color = (0, 0, 0, 128)  # Semi-transparent black
            draw.text(
                (x + shadow_offset[0], y + shadow_offset[1]),
                text,
                font=font,
                fill=shadow_color
            )
        
        # Draw main text
        text_color = style_dict["color"]
        draw.text((x, y), text, font=font, fill=text_color)
        
        return img
    
    def _calculate_text_position(
        self,
        img_width: int,
        img_height: int,
        text_width: int,
        text_height: int,
        position: str,
        alignment: str,
        padding: int,
    ) -> Tuple[int, int]:
        """
        Calculate (x, y) coordinates for text placement.
        
        Args:
            img_width: Image width
            img_height: Image height
            text_width: Text width
            text_height: Text height
            position: Position string (e.g., "top-center", "center", "bottom")
            alignment: Alignment string (left/center/right)
            padding: Padding from edges
            
        Returns:
            Tuple of (x, y) coordinates
        """
        # Default to center
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2
        
        # Parse vertical position
        if "top" in position.lower():
            y = padding
        elif "bottom" in position.lower():
            y = img_height - text_height - padding
        
        # Parse horizontal alignment
        if "left" in alignment.lower():
            x = padding
        elif "right" in alignment.lower():
            x = img_width - text_width - padding
        else:  # center
            x = (img_width - text_width) // 2
        
        return (x, y)
    
    def _parse_rgba(self, rgba_str: str) -> Tuple[int, int, int, int]:
        """
        Parse rgba string to tuple.
        
        Args:
            rgba_str: String like "rgba(0,0,0,0.4)" or "rgb(255,255,255)"
            
        Returns:
            Tuple of (r, g, b, a) values
        """
        # Extract numbers from rgba/rgb string
        numbers = re.findall(r'[\d.]+', rgba_str)
        
        if len(numbers) >= 3:
            r = int(numbers[0])
            g = int(numbers[1])
            b = int(numbers[2])
            a = int(float(numbers[3]) * 255) if len(numbers) > 3 else 255
            return (r, g, b, a)
        
        # Default to semi-transparent black
        return (0, 0, 0, 128)
    
    def _parse_text_shadow(self, shadow_str: str) -> Tuple[int, int]:
        """
        Parse text shadow specification.
        
        Args:
            shadow_str: String like "2px 2px 4px rgba(0,0,0,0.8)"
            
        Returns:
            Tuple of (x_offset, y_offset) in pixels
        """
        # Extract first two numbers as offsets
        numbers = re.findall(r'(\d+)px', shadow_str)
        
        if len(numbers) >= 2:
            return (int(numbers[0]), int(numbers[1]))
        
        # Default offset
        return (2, 2)
    
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