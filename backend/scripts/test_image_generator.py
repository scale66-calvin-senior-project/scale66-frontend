"""
Test Image Generator Agent - Standalone test without full pipeline.

Run from backend directory:
    uv run python -m scripts.test_image_generator

Requirements:
- GEMINI_API_KEY in .env
"""

import asyncio
import base64
import sys
from datetime import datetime
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.core.config import settings
from app.core.logging import setup_logging
from app.agents.image_generator import image_generator
from app.models.pipeline import ImageGeneratorInput
from app.models.brand_kit import BrandKit


# Test brand kit
TEST_BRAND_KIT = BrandKit(
    brand_name="Scale66",
    brand_niche="AI-Powered Social Media Marketing",
    brand_style="professional",
    customer_pain_points=[
        "No time to create social media content",
        "Can't afford designers or agencies",
        "Don't know what content drives engagement",
        "Posts look unprofessional or generic",
        "Social media feels overwhelming and time-consuming"
    ],
    product_service_desc=(
        "Scale66 is an AI-powered platform that helps small businesses create "
        "professional, branded carousel posts for Instagram and TikTok in minutes. "
        "Through a simple chat interface, businesses can generate scroll-stopping "
        "content that drives engagement and sales—no design skills required."
    )
)

# Single test case with strategy + text already generated
TEST_CASE = {
    "name": "Solopreneur Social Media Tips",
    "format_type": "listicle_tips",
    "complete_strategy": (
        "This carousel targets time-strapped solopreneurs who feel social media success is out of reach "
        "without a team or budget. It delivers immediately actionable tips that progress from foundational "
        "mindset shifts to tactical execution strategies. The value arc moves from quick-win validation to "
        "sustainable systems, culminating in recognition that AI tools can amplify their efforts without "
        "replacing their voice."
    ),
    "hook_slide_strategy": (
        "The hook should signal immediate relief to solopreneurs drowning in content creation pressure. "
        "It promises a specific number of practical tips that respect their time constraints while "
        "addressing their core frustration of appearing unprofessional or inconsistent."
    ),
    "body_slides_strategy": [
        "First tip addresses the most common mental block—perfectionism versus consistency. This slide validates their struggle while reframing success metrics. It builds trust by acknowledging their reality before offering direction.",
        "Second tip focuses on strategic content repurposing—extracting maximum value from minimal input. This position leverages the confidence from tip one to introduce a slightly more sophisticated workflow concept that still feels achievable.",
        "Third tip introduces audience-centric thinking—shifting from broadcasting to conversation. This deepens strategic thinking while remaining tactical. It prepares them to see content creation as relationship-building rather than task completion.",
        "Final tip positions AI assistance as leverage for their existing efforts, not replacement of their expertise. The soft CTA emerges naturally as the solution to implementing all previous tips efficiently while maintaining their authentic voice.",
    ],
    # Pre-generated text from text_generator
    "hook_slide_text": "5 social media tips that work without a team or budget",
    "body_slides_text": [
        "Done beats perfect. Post that imperfect content and iterate as you grow.",
        "Repurpose ruthlessly. Turn one piece of content into five formats across three platforms.",
        "Engage before you broadcast. Comment on 5 posts in your niche before sharing your own content.",
        "Let AI handle the repetitive work. Use tools to draft captions, repurpose content, and schedule posts while you focus on strategy and connection.",
    ],
}


def check_prerequisites():
    """Verify required environment variables."""
    if not settings.gemini_api_key:
        print("ERROR: Missing GEMINI_API_KEY")
        sys.exit(1)


def save_images(output_dir: Path, hook_image: str, body_images: list[str]):
    """Save base64 images to files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save hook slide
    hook_path = output_dir / "1_hook.png"
    with open(hook_path, "wb") as f:
        f.write(base64.b64decode(hook_image))
    print(f"  Saved: {hook_path}")
    
    # Save body slides
    for i, img in enumerate(body_images):
        body_path = output_dir / f"{i + 2}_body.png"
        with open(body_path, "wb") as f:
            f.write(base64.b64decode(img))
        print(f"  Saved: {body_path}")


async def test_image_generator():
    """Test the image generator agent."""
    input_data = ImageGeneratorInput(
        brand_kit=TEST_BRAND_KIT,
        format_type=TEST_CASE["format_type"],
        complete_strategy=TEST_CASE["complete_strategy"],
        hook_slide_strategy=TEST_CASE["hook_slide_strategy"],
        body_slides_strategy=TEST_CASE["body_slides_strategy"],
        hook_slide_text=TEST_CASE["hook_slide_text"],
        body_slides_text=TEST_CASE["body_slides_text"],
    )
    
    result = await image_generator.run(input_data)
    return result


async def main():
    """Main execution flow."""
    setup_logging(log_level="INFO")
    
    check_prerequisites()
    
    print("\n" + "=" * 80)
    print("IMAGE GENERATOR TEST")
    print("=" * 80)
    print(f"\nTest: {TEST_CASE['name']}")
    print(f"Format: {TEST_CASE['format_type']}")
    print(f"Slides: 1 hook + {len(TEST_CASE['body_slides_strategy'])} body")
    print("\nGenerating images...")
    
    try:
        result = await test_image_generator()
        
        if not result.success:
            print(f"\nERROR: {result.error_message}")
            return
        
        # Save to output/test_carousels/<timestamp>/
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = backend_path / "output" / "test_carousels" / timestamp
        
        print(f"\nSaving images to: {output_dir}")
        save_images(output_dir, result.hook_slide_image, result.body_slides_images)
        
        print(f"\nGeneration complete: {1 + len(result.body_slides_images)} images saved")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

