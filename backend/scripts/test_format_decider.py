"""
Test Carousel Format Decider Agent - Standalone test without full pipeline.

Run from backend directory:
    uv run python -m scripts.test_format_decider

Requirements:
- ANTHROPIC_API_KEY in .env
"""

import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.core.config import settings
from app.core.logging import setup_logging
from app.agents.carousel_format_decider import carousel_format_decider
from app.models.pipeline import CarouselFormatDeciderInput
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

# Test prompts
TEST_PROMPTS = [
    "Create a carousel that gives a couple useful tips to solopreneurs on how to improve their social media presence, with a soft CTA for scale66 at the end",
    "Create a carousel that shows the story of a motivational person achieving social media success and growing their business",
    "Show some amazing pictures of a business with no captions just high quality images of behind the scenes"
]


def check_prerequisites():
    """Verify required environment variables."""
    if not settings.anthropic_api_key:
        print("ERROR: Missing ANTHROPIC_API_KEY")
        sys.exit(1)


async def test_format_decider(user_prompt: str):
    """Test the carousel format decider agent with a single prompt."""
    input_data = CarouselFormatDeciderInput(
        user_prompt=user_prompt,
        brand_kit=TEST_BRAND_KIT
    )
    
    result = await carousel_format_decider.run(input_data)
    return result


async def main():
    """Main execution flow."""
    setup_logging(log_level="ERROR")  # Suppress logs
    
    check_prerequisites()
    
    results = []
    
    # Run all prompts
    for prompt in TEST_PROMPTS:
        try:
            result = await test_format_decider(prompt)
            results.append({
                "prompt": prompt,
                "format": result.format_type if result.success else "ERROR",
                "rationale": result.format_rationale if result.success else result.error_message
            })
        except Exception as e:
            results.append({
                "prompt": prompt,
                "format": "ERROR",
                "rationale": str(e)
            })
    
    # Display all results
    print("\n" + "=" * 80)
    print("FORMAT DECIDER TEST RESULTS")
    print("=" * 80 + "\n")
    
    for i, res in enumerate(results, 1):
        print(f"TEST {i}:")
        print(f"Prompt: {res['prompt']}")
        print(f"Format: {res['format']}")
        print(f"Rationale: {res['rationale']}")
        print()


if __name__ == "__main__":
    asyncio.run(main())

