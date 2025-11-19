"""
Text Generator Agent - Step 5 of AI Pipeline

Generates text style and on-screen text for carousel slides.

Has 3 sub-components:
1. Style Generator - Creates font/text style (emotional/catchy)
2. Hook Text Generator - Creates text for Hook Slide (text only)
3. Body Slides Text Generator - Creates text for body slides

NOTE: Style Generator needs hook_image from ImageGenerator (step 4)
Orchestrator must coordinate: ImageGenerator generates hook_image first,
then TextGenerator can use it for style generation.
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class TextGenerator(BaseAgent):
    """
    Text Generator Agent.
    
    Responsibilities:
    1. Generate Text Style - Based on hook image, script, brand style
    2. Generate Hook Text - On-screen text for slide 1
    3. Generate Body Text - On-screen text for slides 2-N
    
    The text generator creates the actual words that will appear
    overlaid on the carousel images. This is different from the
    script - these are short, punchy phrases designed for visual impact.
    
    Text Style Examples:
    - "Bold sans-serif, uppercase, high contrast"
    - "Elegant script, lowercase, soft colors"
    - "Modern minimal, mixed case, clean"
    
    On-Screen Text Examples:
    - Hook: "97% FAIL"
    - Body: "Here's why..." → "Problem #1" → "The Solution"
    
    TODO: Implement 3-step text generation:
    1. Analyze hook image and generate text style
    2. Create hook text (short, impactful)
    3. Create body text for each slide
    """
    
    def __init__(self):
        """Initialize text generator agent."""
        super().__init__()
        pass
    
    async def generate(
        self, 
        story_data: Dict[str, Any], 
        brand_kit_data: Dict[str, Any],
        hook_image_url: str = None
    ) -> Dict[str, Any]:
        """
        Generate all text elements for carousel.
        
        Args:
            story_data: Output from story_generator (hook, script, slides)
                {
                    "hook": str,
                    "script": str,
                    "slides": list[str],
                    "cta": str
                }
            brand_kit_data: Brand context
                {
                    "brand_name": str,
                    "brand_style": str,
                    "brand_colors": list[str],
                    ...
                }
            hook_image_url: URL to hook image from ImageGenerator (needed for style)
            
        Returns:
            All text elements:
            {
                "text_style": str,  # Font/emotion style description
                "hook_text": str,  # On-screen text for slide 1
                "body_slides_text": list[str],  # On-screen text for slides 2-N
                "text_metadata": dict  # Font sizes, colors, positioning hints
            }
        
        TODO: Implement text generation:
        
        STEP 1: Generate text style
        NOTE: This requires hook_image_url from ImageGenerator
        Orchestrator must ensure ImageGenerator runs first
        
        text_style = await self._generate_style(
            hook_image_url,
            story_data["script"],
            brand_kit_data["brand_style"]
        )
        
        STEP 2: Generate hook text (for slide 1)
        hook_text = await self._generate_hook_text(
            story_data["hook"],
            text_style
        )
        
        STEP 3: Generate body text (for slides 2-N)
        body_text = await self._generate_body_text(
            story_data["slides"][1:],  # Skip first slide (hook)
            text_style
        )
        
        STEP 4: Generate metadata
        metadata = {
            "font_family": "...",
            "font_size_hook": "...",
            "font_size_body": "...",
            "text_color": "...",
            "text_effects": ["shadow", "outline", ...]
        }
        
        return {
            "text_style": text_style,
            "hook_text": hook_text,
            "body_slides_text": body_text,
            "text_metadata": metadata
        }
        """
        # TODO: Implement text generation
        await self._log_step("text_generation_start", {
            "num_slides": len(story_data.get("slides", [])),
            "has_hook_image": hook_image_url is not None
        })
        
        # TODO: Generate style (needs hook_image)
        # TODO: Generate hook text
        # TODO: Generate body text
        # TODO: Generate metadata
        # TODO: Return text data
        
        pass
    
    async def _generate_style(
        self, 
        hook_image_url: str, 
        script: str, 
        brand_style: str
    ) -> str:
        """
        Generate text style based on hook image, script, and brand style.
        
        Args:
            hook_image_url: URL to hook image from ImageGenerator
            script: Carousel script
            brand_style: Brand style description
            
        Returns:
            Text style description
        
        TODO: Implement style generation:
        
        NOTE: This is where text and image generators coordinate!
        The LLM analyzes the hook_image to decide text style that
        will look good overlaid on the images.
        
        1. Use vision-capable LLM (GPT-4V or Gemini Vision)
        
        2. Build prompt:
           '''
           Analyze this image and decide the best text style for carousel text.
           
           Image: [hook_image_url]
           
           Script tone: {script first few sentences}
           Brand style: {brand_style}
           
           Decide:
           1. Font style (bold/light, serif/sans-serif)
           2. Text case (uppercase/lowercase/mixed)
           3. Text weight (bold/regular/light)
           4. Emotional tone (energetic/calm/professional)
           5. Text effects needed (shadow/outline/glow)
           
           Consider:
           - Image brightness (need high contrast?)
           - Image complexity (need text background?)
           - Brand style alignment
           - Readability on mobile
           
           Return style description:
           "Bold sans-serif, uppercase, high contrast, drop shadow"
           '''
        
        3. Call vision LLM with image
        
        4. Return style description
        
        Example returns:
        - "Bold sans-serif, uppercase, white with black outline"
        - "Clean minimal, mixed case, dark on light background"
        - "Elegant script, lowercase, gold color"
        """
        # TODO: Implement style generation with vision LLM
        # NOTE: Needs hook_image_url from ImageGenerator
        pass
    
    async def _generate_hook_text(
        self, 
        hook: str, 
        text_style: str
    ) -> str:
        """
        Create on-screen text for hook slide.
        
        Args:
            hook: Hook text from story_generator
            text_style: Text style from _generate_style
            
        Returns:
            Short, punchy on-screen text
        
        TODO: Implement hook text generation:
        
        The hook text should be VERY SHORT - designed to grab
        attention in <1 second. It's different from the hook
        sentence - it's the BIG TEXT that appears on slide 1.
        
        1. Build prompt:
           '''
           Create short, punchy on-screen text for the hook slide.
           
           Hook: "{hook}"
           Text Style: {text_style}
           
           Requirements:
           - 1-5 words maximum
           - High impact
           - Grabs attention instantly
           - Can be read in <1 second
           
           Examples:
           - "97% FAIL"
           - "You're Doing It Wrong"
           - "The Secret?"
           - "I Made $10K"
           
           Return only the on-screen text (no explanation).
           '''
        
        2. Call LLM
        
        3. Ensure text is short (1-5 words)
        
        4. Return hook text
        
        Example:
        Hook: "97% of startups fail at marketing. Here's why."
        → On-screen: "97% FAIL"
        """
        # TODO: Implement hook text generation
        pass
    
    async def _generate_body_text(
        self, 
        slides: List[str], 
        text_style: str
    ) -> List[str]:
        """
        Create on-screen text for body slides.
        
        Args:
            slides: Slide texts from story_generator (slides 2-N)
            text_style: Text style from _generate_style
            
        Returns:
            List of on-screen text (one per body slide)
        
        TODO: Implement body text generation:
        
        Body text is also SHORT - key phrases that complement
        the slide script. Not the full script text.
        
        1. For each slide, build prompt:
           '''
           Create short on-screen text for this slide.
           
           Slide content: "{slide_text}"
           Text style: {text_style}
           
           Requirements:
           - 3-10 words
           - Captures key message
           - Visually readable
           - Complements (doesn't duplicate) caption
           
           Examples:
           - "The Problem: Lost in the Noise"
           - "Solution #1: Know Your Audience"
           - "Here's What Changed"
           
           Return only the on-screen text.
           '''
        
        2. Call LLM for each slide
        
        3. Ensure text is concise (3-10 words)
        
        4. Return list of body texts
        
        Example:
        Slide: "The biggest mistake is trying to reach everyone..."
        → On-screen: "Mistake #1: Too Broad"
        """
        # TODO: Implement body text generation
        # Loop through slides and generate text for each
        pass
    
    async def _generate_text_metadata(
        self, 
        text_style: str,
        brand_kit_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate metadata for text rendering (font sizes, colors, etc.).
        
        Args:
            text_style: Text style description
            brand_kit_data: Brand context with colors
            
        Returns:
            Metadata for text rendering
        
        TODO: Implement metadata generation:
        
        This metadata helps the Finalizer know HOW to render text.
        
        Return format:
        {
            "font_family": "Arial" or "serif" or "sans-serif",
            "font_weight": "bold" or "normal",
            "text_case": "uppercase" or "lowercase" or "mixed",
            "primary_color": "#FFFFFF",
            "secondary_color": "#000000",  # For outline/shadow
            "effects": ["drop_shadow", "outline"],
            "alignment": "center",
            "size_hook": "large",  # Hook text is bigger
            "size_body": "medium"
        }
        
        Consider:
        - Brand colors for text color
        - Text style description for formatting
        - Readability requirements
        """
        # TODO: Implement metadata generation
        pass

