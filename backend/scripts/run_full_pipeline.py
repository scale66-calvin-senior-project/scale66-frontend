"""
Full Pipeline Test - End-to-end test with real Supabase and AI APIs.

Creates test data, runs the complete orchestrator pipeline, and saves to Supabase.

Run from backend directory:
    uv run python -m scripts.run_full_pipeline

Requirements:
- SUPABASE_URL, SUPABASE_SERVICE_KEY in .env
- ANTHROPIC_API_KEY, GEMINI_API_KEY in .env
- carousel-slides storage bucket created in Supabase
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.supabase import get_supabase_admin_client
from app.agents.orchestrator import orchestrator
from app.models.pipeline import OrchestratorInput


TEST_USER_ID = "00000000-0000-0000-0000-000000000001"
TEST_BRAND_KIT_DATA = {
    "brand_name": "ProductivityPro",
    "brand_niche": "Productivity and Time Management",
    "brand_style": "professional",
    "customer_pain_points": [
        "Overwhelmed by tasks",
        "Struggling to focus",
        "Poor work-life balance",
        "Procrastination"
    ],
    "product_service_description": (
        "ProductivityPro is a digital coaching service that helps busy professionals "
        "master their time through proven frameworks, personalized strategies, and "
        "accountability coaching."
    )
}
TEST_USER_PROMPT = (
    "Create a carousel about the top 5 morning habits that successful entrepreneurs "
    "use to maximize their productivity before 9 AM"
)


def check_prerequisites():
    """Verify all required setup is complete."""
    print("Checking prerequisites...")
    
    missing = []
    if not settings.supabase_url:
        missing.append("SUPABASE_URL")
    if not settings.supabase_service_key:
        missing.append("SUPABASE_SERVICE_KEY")
    if not settings.anthropic_api_key:
        missing.append("ANTHROPIC_API_KEY")
    if not settings.gemini_api_key:
        missing.append("GEMINI_API_KEY")
    
    if missing:
        print(f"\nERROR: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nAdd these to backend/.env and try again.")
        sys.exit(1)
    
    print("  Environment variables: OK")
    
    # Check storage bucket
    supabase = get_supabase_admin_client()
    try:
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        if 'carousel-slides' not in bucket_names:
            print("\nWARNING: Storage bucket 'carousel-slides' not found!")
            print("Create it in Supabase Dashboard > Storage > New bucket")
            print("  Name: carousel-slides")
            print("  Public: Yes")
            response = input("\nContinue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)
        else:
            print("  Storage bucket: OK")
    except Exception as e:
        print(f"  WARNING: Could not verify storage bucket: {e}")


async def setup_test_data():
    """Create test user and brand kit in Supabase."""
    print("\nSetting up test data...")
    supabase = get_supabase_admin_client()
    
    # Create or update test user
    try:
        existing = supabase.table('users').select('*').eq('id', TEST_USER_ID).execute()
        if existing.data:
            print(f"  Test user exists: {TEST_USER_ID}")
        else:
            supabase.table('users').insert({
                'id': TEST_USER_ID,
                'email': 'test@example.com',
                'subscription_tier': 'free',
                'onboarding_completed': True
            }).execute()
            print(f"  Created test user: {TEST_USER_ID}")
    except Exception as e:
        print(f"  WARNING: User setup: {e}")
    
    # Delete existing test brand kit (if any)
    try:
        supabase.table('brand_kits').delete().eq('user_id', TEST_USER_ID).execute()
    except Exception:
        pass
    
    # Create brand kit
    result = supabase.table('brand_kits').insert({
        'user_id': TEST_USER_ID,
        **TEST_BRAND_KIT_DATA
    }).execute()
    
    brand_kit_id = result.data[0]['id']
    print(f"  Created brand kit: {brand_kit_id}")
    print(f"    Brand: {TEST_BRAND_KIT_DATA['brand_name']}")
    
    return brand_kit_id


async def run_pipeline(brand_kit_id: str):
    """Run the full orchestrator pipeline."""
    print("\n" + "=" * 60)
    print("RUNNING FULL PIPELINE")
    print("=" * 60)
    print(f"\nBrand Kit ID: {brand_kit_id}")
    print(f"User Prompt: {TEST_USER_PROMPT}")
    print("\nPipeline Steps:")
    print("  1. Determine carousel format (Claude)")
    print("  2. Generate story narratives (Claude)")
    print("  3. Generate images (Gemini)")
    print("  4. Analyze images and create text (Claude Vision)")
    print("  5. Overlay text on images (Pillow)")
    print("  6. Upload to Supabase storage")
    print("\nOutput Locations:")
    print(f"  - Logs: backend/logs/scale66.log")
    print(f"  - Local Images: backend/output/carousels/[carousel-id]/")
    print(f"    - Raw slides (no text): raw/slide_*.png")
    print(f"    - Final slides (with text): final/slide_*.png")
    print(f"  - Supabase Storage: carousel-slides bucket")
    print("\nEstimated time: 2-3 minutes")
    print("=" * 60)
    
    result = await orchestrator.run(OrchestratorInput(
        step_name="orchestrator",
        success=True,
        brand_kit_id=brand_kit_id,
        user_prompt=TEST_USER_PROMPT
    ))
    
    return result


def display_results(result):
    """Display pipeline results."""
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    if result.success:
        print(f"\nCarousel ID: {result.carousel_id}")
        print(f"Total Slides: {len(result.carousel_slides_urls)}")
        
        print("\n" + "-" * 60)
        print("SUPABASE STORAGE URLS")
        print("-" * 60)
        for i, url in enumerate(result.carousel_slides_urls):
            slide_type = "Hook" if i == 0 else f"Body {i}"
            print(f"  Slide {i} ({slide_type}): {url}")
        
        print("\n" + "-" * 60)
        print("LOCAL OUTPUT FILES")
        print("-" * 60)
        from app.core.config import settings
        if settings.save_local_output:
            from pathlib import Path
            local_dir = Path(settings.output_dir) / "carousels" / result.carousel_id
            print(f"  Directory: {local_dir}")
            print(f"  Raw slides (no text): {local_dir}/raw/slide_*.png")
            print(f"  Final slides (with text): {local_dir}/final/slide_*.png")
        else:
            print("  Local output saving is disabled")
        
        print("\n" + "-" * 60)
        print("LOGS")
        print("-" * 60)
        if settings.log_to_file:
            print(f"  Log file: {settings.log_file}")
            print(f"  Contains: Detailed pipeline execution logs with all outputs")
        else:
            print("  File logging is disabled (console only)")
        
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        print("  1. View images in Supabase Dashboard > Storage > carousel-slides")
        print("  2. Review local files in backend/output/carousels/")
        print("  3. Check detailed logs in backend/logs/scale66.log")
        print("=" * 60)
    else:
        print(f"\nERROR: {result.error_message}")


async def save_to_posts(brand_kit_id: str, result):
    """Save generated carousel to posts table."""
    print("\nSaving to posts table...")
    supabase = get_supabase_admin_client()
    
    # Create a test campaign first
    campaign_data = {
        'user_id': TEST_USER_ID,
        'campaign_name': 'Test Campaign - Full Pipeline',
        'target_audience': 'Busy professionals seeking productivity tips',
        'goals': 'Test the full pipeline end-to-end'
    }
    campaign = supabase.table('campaigns').insert(campaign_data).execute()
    campaign_id = campaign.data[0]['id']
    print(f"  Created campaign: {campaign_id}")
    
    # Now create the post with campaign_id
    post_data = {
        'user_id': TEST_USER_ID,
        'campaign_id': campaign_id,
        'carousel_slides': result.carousel_slides_urls,
        'carousel_metadata': {
            'carousel_id': result.carousel_id,
            'brand_kit_id': brand_kit_id,
            'prompt': TEST_USER_PROMPT,
            'num_slides': len(result.carousel_slides_urls)
        },
        'final_caption': TEST_USER_PROMPT,
        'platform': 'instagram',
        'status': 'draft'
    }
    
    post = supabase.table('posts').insert(post_data).execute()
    print(f"  Created post: {post.data[0]['id']}")


async def cleanup():
    """Optional: Clean up test data."""
    response = input("\nDelete test data? (y/n): ")
    if response.lower() != 'y':
        return
    
    print("\nCleaning up test data...")
    supabase = get_supabase_admin_client()
    
    # Delete posts, campaigns, and brand kits
    supabase.table('posts').delete().eq('user_id', TEST_USER_ID).execute()
    supabase.table('campaigns').delete().eq('user_id', TEST_USER_ID).execute()
    supabase.table('brand_kits').delete().eq('user_id', TEST_USER_ID).execute()
    print("  Deleted brand kit, campaign, and posts")
    
    # Note: Storage images remain (manual cleanup if needed)
    print("  Storage images remain (cleanup manually if needed)")


async def main():
    """Main execution flow."""
    # Setup logging with file output enabled
    setup_logging(log_level="INFO")
    
    print("=" * 60)
    print("FULL PIPELINE TEST")
    print("=" * 60)
    print(f"\nLogging Configuration:")
    print(f"  - Level: INFO")
    print(f"  - Console: Enabled")
    print(f"  - File: backend/logs/scale66.log")
    print("=" * 60)
    
    check_prerequisites()
    
    brand_kit_id = await setup_test_data()
    
    try:
        result = await run_pipeline(brand_kit_id)
        display_results(result)
        
        if result.success:
            await save_to_posts(brand_kit_id, result)
        
    except Exception as e:
        print(f"\n{'=' * 60}")
        print(f"PIPELINE FAILED")
        print(f"{'=' * 60}")
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print(f"\nCheck logs for details: backend/logs/scale66.log")
    finally:
        await cleanup()


if __name__ == "__main__":
    asyncio.run(main())

