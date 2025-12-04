import asyncio
import sys
import base64
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.brand_kit import BrandKit
from app.models.pipeline import SlideGeneratorInput
from app.agents.slide_generator import slide_generator


USER_PROMPT = "A carousel showing solopreneurs how to get started with social media marketing"

BRAND_KIT = BrandKit(
    brand_name="Scale66",
    brand_niche="Social Media Marketing for online businesses",
    brand_style="professional",
    customer_pain_points=["I don't know how to get started with social media marketing", "I don't have the time to manage social media", "I don't have the budget to hire a marketing agency"],
    product_service_desc="Helps speed up the process of social media marketing for brand awareness at the fraction of the cost of a marketing agency"
)

FORMAT_TYPE = "listicle_tips"
NUM_SLIDES = 7
TEMPLATE_ID = "carousel-3"

SLIDES_TEXT = [
    "If you're a solopreneur, you need to know these 6 tips to get started with social media marketing",
    "Identify what you want to achieve with social media—whether it's brand awareness, lead generation, or sales. Then research and document your ideal customer profile, including demographics, interests, pain points, and where they spend time online.",
    "Not all platforms are created equal. Select 2-3 platforms where your target audience is most active. Focus on quality over quantity—it's better to master one platform than to spread yourself thin across many.",
    "Plan the types of content you'll post, posting frequency, and themes. A mix of educational, entertaining, and promotional content typically performs best. Consistency in posting schedule helps build audience engagement.",
    "Use a clear profile picture, compelling bio with keywords, and link to your website. Make sure your brand voice and visual style are consistent across all platforms to build recognition.",
    "Don't just broadcast—interact with your audience. Respond to comments, answer questions, and engage with content from accounts in your niche. Building relationships is key to growing organically.",
    "Encourage customers to share their experiences with your product or service. Repost their content and give them credit. This builds trust, increases engagement, and provides authentic social proof."
]


async def main():
    input_data = SlideGeneratorInput(
        user_prompt=USER_PROMPT,
        brand_kit=BRAND_KIT,
        format_type=FORMAT_TYPE,
        num_slides=NUM_SLIDES,
        template_id=TEMPLATE_ID,
        slides_text=SLIDES_TEXT
    )
    
    result = await slide_generator.run(input_data)
    
    print("SLIDE GENERATOR OUTPUT")
    
    print(f"\n  Format Type:       {input_data.format_type}")
    print(f"  Template ID:       {input_data.template_id}")
    print(f"  Num Slides:        {len(result.slides_images)}")
    
    output_dir = Path(__file__).parent.parent / "output" / "slides"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"\n  Saved Images:")
    for i, image_base64 in enumerate(result.slides_images, 1):
        image_data = base64.b64decode(image_base64)
        filename = f"slide_{timestamp}_{i}.png"
        filepath = output_dir / filename
        filepath.write_bytes(image_data)
        print(f"    {i}. {filepath}")
    
    if result.error_message:
        print(f"\n  Error Message:     {result.error_message}")


if __name__ == "__main__":
    asyncio.run(main())

