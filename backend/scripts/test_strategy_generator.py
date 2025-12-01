"""
Test Strategy Generator Agent - Standalone test without full pipeline.

Run from backend directory:
    uv run python -m scripts.test_strategy_generator

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
from app.agents.strategy_generator import strategy_generator
from app.models.pipeline import StrategyGeneratorInput
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

# Test cases: (user_prompt, format_type, num_slides)
TEST_CASES = [
    {
        "user_prompt": "Create a carousel that gives a couple useful tips to solopreneurs on how to improve their social media presence, with a soft CTA for scale66 at the end",
        "format_type": "listicle_tips",
        "num_slides": 5,
    },
    {
        "user_prompt": "7 ways to grow your Instagram following without spending money on ads",
        "format_type": "listicle_tips",
        "num_slides": 8,
    },
    {
        "user_prompt": "5 common mistakes small businesses make on social media and how to avoid them",
        "format_type": "listicle_tips",
        "num_slides": 6,
    },
]


def check_prerequisites():
    """Verify required environment variables."""
    if not settings.anthropic_api_key:
        print("ERROR: Missing ANTHROPIC_API_KEY")
        sys.exit(1)


async def test_strategy_generator(test_case: dict):
    """Test the strategy generator agent with a single test case."""
    input_data = StrategyGeneratorInput(
        user_prompt=test_case["user_prompt"],
        format_type=test_case["format_type"],
        num_slides=test_case["num_slides"],
        brand_kit=TEST_BRAND_KIT
    )
    
    result = await strategy_generator.run(input_data)
    return result


async def main():
    """Main execution flow."""
    setup_logging(log_level="ERROR")  # Suppress logs
    
    check_prerequisites()
    
    results = []
    
    # Run all test cases
    for test_case in TEST_CASES:
        try:
            result = await test_strategy_generator(test_case)
            results.append({
                "prompt": test_case["user_prompt"],
                "format": test_case["format_type"],
                "num_slides": test_case["num_slides"],
                "complete_story": result.complete_story if result.success else "ERROR",
                "rationale": result.complete_story_rationale if result.success else result.error_message,
                "hook": result.hook_slide_story if result.success else None,
                "body_slides": result.body_slides_story if result.success else None,
            })
        except Exception as e:
            results.append({
                "prompt": test_case["user_prompt"],
                "format": test_case["format_type"],
                "num_slides": test_case["num_slides"],
                "complete_story": "ERROR",
                "rationale": str(e),
                "hook": None,
                "body_slides": None,
            })
    
    # Display all results
    print("\n" + "=" * 80)
    print("STRATEGY GENERATOR TEST RESULTS")
    print("=" * 80)
    
    for i, res in enumerate(results, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST {i}: {res['format']} ({res['num_slides']} slides)")
        print(f"{'─' * 80}")
        
        print(f"\nPrompt:\n  {res['prompt']}")
        
        print(f"\nComplete Strategy:\n  {res['complete_story']}")
        
        print(f"\nRationale:\n  {res['rationale']}")
        
        print(f"\nHook:\n  {res['hook']}")
        
        if res['body_slides']:
            print(f"\nBody Slides:")
            for j, slide in enumerate(res['body_slides'], 1):
                print(f"\n  Slide {j}:\n    {slide}")
        
        print()


if __name__ == "__main__":
    asyncio.run(main())

