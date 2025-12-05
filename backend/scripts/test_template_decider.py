import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.brand_kit import BrandKit
from app.models.pipeline import TemplateDeciderInput
from app.agents.template_decider import template_decider


USER_PROMPT = "5 tip for getting started with social media marketing, just building brand awareness, not trying to sell anything or make the user do anything"

BRAND_KIT = BrandKit(
   brand_name="Scale66",
   brand_niche="Social Media Marketing for online businesses",
   brand_style="professional",
   customer_pain_points=["I don't know how to get started with social media marketing", "I don't have the time to manage social media", "I don't have the budget to hire a marketing agency"],
   product_service_desc="Helps speed up the process of social media marketing for brand awareness at the fraction of the cost of a marketing agency"
)


async def main():
    input_data = TemplateDeciderInput(
        user_prompt=USER_PROMPT,
        brand_kit=BRAND_KIT
    )
    
    result = await template_decider.run(input_data)
    
    print("TEMPLATE DECIDER OUTPUT")
    
    print(f"\n  Format Type:       {result.format_type}")
    print(f"  Num Body Slides:   {result.num_body_slides}")
    print(f"  Template ID:       {result.template_id}")
    print(f"  CTA Slide:         {result.cta_slide}")
    
    if result.error_message:
        print(f"\n  Error Message:     {result.error_message}")


if __name__ == "__main__":
    asyncio.run(main())

