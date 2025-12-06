import asyncio
import sys
import base64
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.brand_kit import BrandKit
from app.models.pipeline import SlideGeneratorInput
from app.agents.slide_generator import slide_generator


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
NUM_BODY_SLIDES = 3
TEMPLATE_ID = "carousel-2"

HOOK_TEXT = "Coffee isn't just delicious—it's secretly boosting your health in ways you never knew"

BODY_TEXTS = [
    "Coffee contains powerful antioxidants that help protect your liver from damage and reduce risk of cirrhosis and liver cancer by up to 40 percent",
    "Regular coffee consumption is linked to lower rates of Parkinson's disease because caffeine helps protect dopamine-producing neurons in your brain",
    "Coffee can significantly reduce your risk of developing type 2 diabetes by improving insulin sensitivity and helping regulate blood sugar levels over time",

]

CTA_TEXT = "Visit Joe's Coffee Corner to enjoy freshly roasted coffee that tastes amazing and supports your health—your body will thank you"


async def main():
    input_data = SlideGeneratorInput(
        user_prompt=USER_PROMPT,
        brand_kit=BRAND_KIT,
        format_type=FORMAT_TYPE,
        num_body_slides=NUM_BODY_SLIDES,
        template_id=TEMPLATE_ID,
        hook_text=HOOK_TEXT,
        body_texts=BODY_TEXTS,
        cta_text=CTA_TEXT,
        hook_slide="1_hook.png",
        body_slide="1_body.png",
        cta_slide="1_cta.png",
    )
    
    result = await slide_generator.run(input_data)
    
    print("SLIDE GENERATOR OUTPUT")
    
    print(f"\n  Format Type:       {input_data.format_type}")
    print(f"  Template ID:       {input_data.template_id}")
    print(f"  Num Body Slides:   {input_data.num_body_slides}")
    print(f"  Total Slides:      {input_data.num_slides}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    carousel_dir = Path(__file__).parent.parent / "output" / "carousels" / f"carousel_{timestamp}"
    carousel_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n  Carousel Folder:   {carousel_dir}")
    print(f"\n  Saved Images:")
    
    # Save hook
    hook_path = carousel_dir / "1_hook.png"
    hook_path.write_bytes(base64.b64decode(result.hook_image))
    print(f"    1. {hook_path}")
    
    # Save body slides
    for i, body_image in enumerate(result.body_images, 2):
        body_path = carousel_dir / f"{i}_body.png"
        body_path.write_bytes(base64.b64decode(body_image))
        print(f"    {i}. {body_path}")
    
    # Save CTA if exists
    if result.cta_image:
        cta_num = len(result.body_images) + 2
        cta_path = carousel_dir / f"{cta_num}_cta.png"
        cta_path.write_bytes(base64.b64decode(result.cta_image))
        print(f"    {cta_num}. {cta_path}")
    
    if result.error_message:
        print(f"\n  Error Message:     {result.error_message}")


if __name__ == "__main__":
    asyncio.run(main())

