import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.brand_kit import BrandKit
from app.models.pipeline import CaptionGeneratorInput
from app.agents.caption_generator import caption_generator


USER_PROMPT = "A carousel talking about the benefits of coffee"

BRAND_KIT = BrandKit(
    brand_name="Joe's Coffee Corner",
    brand_niche="Local artisanal coffee shop",
    brand_style="friendly and community-focused",
    customer_pain_points=[
        "Not sure where to find fresh, locally roasted coffee",
        "Looking for a cozy spot to relax or work",
        "Frustrated with long waits and impersonal service at big chains"
    ],
    product_service_desc="A neighborhood coffee shop serving freshly roasted coffee, homemade pastries, and providing a welcoming space for the community"
)

FORMAT_TYPE = "listicle_tips"
NUM_SLIDES = 4


async def main():
    input_data = CaptionGeneratorInput(
        user_prompt=USER_PROMPT,
        brand_kit=BRAND_KIT,
        format_type=FORMAT_TYPE,
        num_slides=NUM_SLIDES
    )
    
    result = await caption_generator.run(input_data)
    
    print("CAPTION GENERATOR OUTPUT")
    
    print(f"\n  Format Type:       {input_data.format_type}")
    print(f"  Num Slides:        {len(result.slides_text)}")
    
    print("\n  Slides Text:")
    for i, text in enumerate(result.slides_text, 1):
        print(f"    {i}. {text}")
    
    if result.error_message:
        print(f"\n  Error Message:     {result.error_message}")


if __name__ == "__main__":
    asyncio.run(main())

