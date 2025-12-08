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

FORMAT_TYPE = "listicle_tips"
NUM_BODY_SLIDES = 5
INCLUDE_CTA = False


async def main():
    input_data = TemplateDeciderInput(
        user_prompt=USER_PROMPT,
        brand_kit=BRAND_KIT,
        format_type=FORMAT_TYPE,
        num_body_slides=NUM_BODY_SLIDES,
        include_cta=INCLUDE_CTA,
    )
    
    result = await template_decider.run(input_data)
    
    print(f"Template ID:  {result.template_id}")
    print(f"Hook Slide:   {result.hook_slide}")
    print(f"Body Slide:   {result.body_slide}")
    print(f"CTA Slide:    {result.cta_slide}")


if __name__ == "__main__":
    asyncio.run(main())

