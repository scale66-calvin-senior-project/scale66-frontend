"""
Test Text Generator Agent - Standalone test without full pipeline.

Run from backend directory:
    uv run python -m scripts.test_text_generator

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
from app.agents.text_generator import text_generator
from app.models.pipeline import TextGeneratorInput
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

# Test cases: actual strategy generator outputs
# These are real outputs from strategy_generator test runs
TEST_CASES = [
    {
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
    },
    {
        "name": "7 Ways to Grow Instagram Without Ads",
        "format_type": "listicle_tips",
        "complete_strategy": (
            "This carousel targets small businesses and creators who believe Instagram growth requires paid "
            "advertising. The strategy dismantles this myth by revealing organic growth mechanics that leverage "
            "platform algorithms and human psychology. Each tip escalates in sophistication—from immediate "
            "behavioral changes to strategic content approaches—proving that consistent smart action outperforms "
            "budget. The value arc moves from quick wins that build confidence to deeper strategic insights "
            "that shift their entire approach to content creation."
        ),
        "hook_slide_strategy": (
            "The hook should challenge the paid-ads-required assumption while making a clear numbered promise. "
            "It targets budget-conscious accounts who've been told growth requires spending. The strategic "
            "frame is empowerment through knowledge rather than limitation through budget."
        ),
        "body_slides_strategy": [
            "First position establishes the easiest behavioral shift—something about consistency or timing that requires zero new skills. This builds immediate credibility and momentum. The insight should feel like permission to start simple.",
            "Second position introduces a content-type strategy that leverages existing platform features most users underutilize. Focuses on working smarter within current capabilities rather than creating more work.",
            "Third position addresses audience psychology—how to structure content that triggers engagement behaviors. Shifts focus from what they post to why people interact. Slightly more conceptual than previous tips.",
            "Fourth position reveals a counterintuitive algorithmic insight that challenges common practices. This is the 'aha moment' that makes them rethink their entire approach. Most strategic tip so far.",
            "Fifth position focuses on community-building mechanics that compound over time. Introduces the concept of reciprocal engagement and relationship-building as growth infrastructure.",
            "Sixth position addresses content repurposing or efficiency—how to maximize output from minimal input. This naturally positions tools like Scale66 without being salesy. Practical and immediately actionable.",
            "Final position synthesizes previous tips into a sustainable system or mindset shift. Leaves them with a framework for thinking about organic growth long-term. Ends on empowerment and capability rather than a single tactic.",
        ],
    },
    {
        "name": "5 Common Social Media Mistakes",
        "format_type": "listicle_tips",
        "complete_strategy": (
            "This carousel targets overwhelmed small business owners who recognize social media matters but "
            "feel paralyzed by mistakes. The strategic arc moves from validation (you're not alone in these "
            "errors) through education (here's what's going wrong) to empowerment (here's the fix). Each "
            "mistake-solution pair builds confidence while subtly positioning professional tools as the path forward."
        ),
        "hook_slide_strategy": (
            "Hook should validate the struggle while promising concrete fixes. The numbered format creates "
            "completionist appeal and signals practical value over theory. Target audience needs reassurance "
            "these are common errors, not personal failures."
        ),
        "body_slides_strategy": [
            "First mistake should address the most universal error - something nearly every small business does wrong. The fix must feel immediately actionable without requiring new skills or tools. Builds trust through recognition.",
            "Second mistake targets a slightly less obvious error related to consistency or planning. The solution should reveal a simple system or reframe that makes the problem feel solvable with better process.",
            "Third mistake focuses on engagement or audience understanding - a strategic error rather than tactical. The fix should shift mindset from broadcasting to connecting, with clear behavioral changes.",
            "Fourth mistake addresses content quality or professionalism - the visual/presentation layer. Solution subtly points toward tools or systems that elevate output without requiring design expertise.",
            "Fifth mistake tackles the sustainability problem - why social media feels like a hamster wheel. The fix should offer a structural solution that reduces ongoing burden while maintaining results. Ends on empowerment.",
        ],
    },
]


def check_prerequisites():
    """Verify required environment variables."""
    if not settings.anthropic_api_key:
        print("ERROR: Missing ANTHROPIC_API_KEY")
        sys.exit(1)


async def test_text_generator(test_case: dict):
    """Test the text generator agent with a single test case."""
    input_data = TextGeneratorInput(
        brand_kit=TEST_BRAND_KIT,
        format_type=test_case["format_type"],
        complete_strategy=test_case["complete_strategy"],
        hook_slide_strategy=test_case["hook_slide_strategy"],
        body_slides_strategy=test_case["body_slides_strategy"],
    )
    
    result = await text_generator.run(input_data)
    return result


async def main():
    """Main execution flow."""
    setup_logging(log_level="ERROR")  # Suppress logs
    
    check_prerequisites()
    
    results = []
    
    # Run all test cases
    for test_case in TEST_CASES:
        try:
            result = await test_text_generator(test_case)
            results.append({
                "name": test_case["name"],
                "format": test_case["format_type"],
                "num_slides": 1 + len(test_case["body_slides_strategy"]),
                "hook_text": result.hook_slide_text if result.success else "ERROR",
                "body_texts": result.body_slides_text if result.success else None,
                "error": result.error_message if not result.success else None,
            })
        except Exception as e:
            results.append({
                "name": test_case["name"],
                "format": test_case["format_type"],
                "num_slides": 1 + len(test_case["body_slides_strategy"]),
                "hook_text": "ERROR",
                "body_texts": None,
                "error": str(e),
            })
    
    # Display all results
    print("\n" + "=" * 80)
    print("TEXT GENERATOR TEST RESULTS")
    print("=" * 80)
    
    for i, res in enumerate(results, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST {i}: {res['name']} ({res['num_slides']} slides)")
        print(f"{'─' * 80}")
        
        if res["error"]:
            print(f"\nERROR: {res['error']}")
            continue
        
        print(f"\nHook Text:\n  {res['hook_text']}")
        
        if res['body_texts']:
            print(f"\nBody Slides:")
            for j, text in enumerate(res['body_texts'], 1):
                print(f"\n  Slide {j + 1}:\n    {text}")
        
        print()


if __name__ == "__main__":
    asyncio.run(main())

