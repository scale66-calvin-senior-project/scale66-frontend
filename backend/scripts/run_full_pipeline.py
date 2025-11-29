"""
Full Pipeline Test - End-to-end test with real Supabase and AI APIs.

Creates test data, runs the complete orchestrator pipeline, and saves to Supabase.

Run from backend directory:
    uv run python -m scripts.run_full_pipeline

Requirements:
- SUPABASE_URL, SUPABASE_SERVICE_KEY in .env
- ANTHROPIC_API_KEY, GEMINI_API_KEY in .env
- carousel-slides storage bucket created in Supabase

Pipeline Steps:
1. Fetch Brand Kit from database
2. Determine carousel format (Claude)
3. Generate story narratives (Claude)
4. Generate text captions (Claude)
5. Generate images WITH text rendered (Gemini 3 Pro)
6. Validate quality and upload (Claude Vision + Supabase Storage)
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
    "brand_name": "Scale66",
    "brand_niche": "AI-Powered Social Media Marketing",
    "brand_style": "professional",
    "customer_pain_points": [
        "No time to create social media content",
        "Can't afford designers or agencies",
        "Don't know what content drives engagement",
        "Posts look unprofessional or generic",
        "Social media feels overwhelming and time-consuming"
    ],
    "product_service_description": (
        "Scale66 is an AI-powered platform that helps small businesses create "
        "professional, branded carousel posts for Instagram and TikTok in minutes. "
        "Through a simple chat interface, businesses can generate scroll-stopping "
        "content that drives engagement and sales—no design skills required."
    )
}
TEST_USER_PROMPT = (
    "Create a carousel that doesn't try to sell anything but just tells a story about the importance of social media marketing for businesses"
)


def check_prerequisites():
    """Verify all required setup is complete."""
    print("\n" + "=" * 80)
    print("CHECKING PREREQUISITES")
    print("=" * 80)
    
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
        print("=" * 80)
        sys.exit(1)
    
    print("  Environment variables: OK")
    
    # Check storage bucket
    supabase = get_supabase_admin_client()
    try:
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        if 'carousel-slides' not in bucket_names:
            print("\n  WARNING: Storage bucket 'carousel-slides' not found!")
            print("  Create it in Supabase Dashboard > Storage > New bucket")
            print("    Name: carousel-slides")
            print("    Public: Yes")
            response = input("\n  Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("=" * 80)
                sys.exit(1)
        else:
            print("  Storage bucket: OK")
    except Exception as e:
        print(f"  WARNING: Could not verify storage bucket: {e}")
    
    print("=" * 80)


async def setup_test_data():
    """Create test user and brand kit in Supabase."""
    print("\n" + "=" * 80)
    print("SETTING UP TEST DATA")
    print("=" * 80)
    
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
    print("=" * 80)
    
    return brand_kit_id


async def run_pipeline(brand_kit_id: str):
    """Run the full orchestrator pipeline."""
    print("\n" + "=" * 80)
    print("RUNNING FULL PIPELINE")
    print("=" * 80)
    print(f"\nBrand Kit ID: {brand_kit_id}")
    print(f"User Prompt: {TEST_USER_PROMPT}")
    print("\nPipeline Steps:")
    print("  1. Fetch Brand Kit from database")
    print("  2. Determine carousel format (Claude)")
    print("  3. Generate story narratives (Claude)")
    print("  4. Generate text captions (Claude)")
    print("  5. Generate images WITH text rendered (Gemini 3 Pro)")
    print("  6. Validate quality and upload (Claude Vision + Supabase Storage)")
    print("\nOutput Locations:")
    print(f"  - Logs: backend/logs/scale66_YYYY-MM-DD_HH-MM-SS.log")
    print(f"  - Local Images: backend/output/carousels/[carousel-id]/final/slide_*.png")
    print(f"  - Supabase Storage: carousel-slides bucket")
    print("\nEstimated time: 2-3 minutes")
    print("=" * 80)
    
    result = await orchestrator.run(OrchestratorInput(
        step_name="orchestrator",
        success=True,
        brand_kit_id=brand_kit_id,
        user_prompt=TEST_USER_PROMPT
    ))
    
    return result


def display_results(result):
    """Display pipeline results."""
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    
    if result.success:
        print(f"\nCarousel ID: {result.carousel_id}")
        print(f"Total Slides: {len(result.carousel_slides_urls)}")
        
        # Display evaluation metrics
        if result.evaluation_metrics:
            print("\n" + "=" * 80)
            print("EVALUATION METRICS")
            print("=" * 80)
            
            metrics = result.evaluation_metrics
            
            print("\nFORMAT TYPE:")
            print(f"  {metrics.format_type_evaluation}")
            
            print("\nCOMPLETE STORY:")
            print(f"  {metrics.complete_story_evaluation}")
            
            print("\nHOOK SLIDE STORY:")
            print(f"  {metrics.hook_slide_story_evaluation}")
            
            print("\nBODY SLIDES STORY:")
            for i, eval_text in enumerate(metrics.body_slides_story_evaluation, 1):
                print(f"  [{i}] {eval_text}")
            
            print("\nHOOK SLIDE TEXT:")
            print(f"  {metrics.hook_slide_text_evaluation}")
            
            print("\nBODY SLIDES TEXT:")
            for i, eval_text in enumerate(metrics.body_slides_text_evaluation, 1):
                print(f"  [{i}] {eval_text}")
            
            print("\nHOOK SLIDE IMAGE:")
            print(f"  {metrics.hook_slide_image_evaluation}")
            
            print("\nBODY SLIDES IMAGES:")
            for i, eval_text in enumerate(metrics.body_slides_images_evaluation, 1):
                print(f"  [{i}] {eval_text}")
            
            print("\nBRAND ALIGNMENT:")
            print(f"  {metrics.brand_kit_evaluation}")
        
        print("\n" + "=" * 80)
        print("SUPABASE STORAGE URLS")
        print("=" * 80)
        for i, url in enumerate(result.carousel_slides_urls):
            slide_type = "Hook" if i == 0 else f"Body {i}"
            print(f"  Slide {i} ({slide_type}): {url}")
        
        print("\n" + "=" * 80)
        print("LOCAL OUTPUT FILES")
        print("=" * 80)
        from app.core.config import settings
        if settings.save_local_output:
            from pathlib import Path
            local_dir = Path(settings.output_dir) / "carousels" / result.carousel_id / "final"
            print(f"  Directory: {local_dir}")
            for i in range(len(result.carousel_slides_urls)):
                slide_type = "Hook" if i == 0 else f"Body {i}"
                print(f"    [{i}] {slide_type}: slide_{i}.png")
        else:
            print("  Local output saving is disabled")
        
        print("\n" + "=" * 80)
        print("LOGS")
        print("=" * 80)
        if settings.log_to_file:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            print(f"  Log file: backend/logs/scale66_{timestamp}.log")
            print(f"  Contains: Pipeline execution + evaluation metrics")
        else:
            print("  File logging is disabled (console only)")
        
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("  1. View images in Supabase Dashboard > Storage > carousel-slides")
        print("  2. Review local files in backend/output/carousels/")
        print("  3. Check evaluation metrics above")
        print("  4. Review log file in backend/logs/")
        print("=" * 80)
    else:
        print(f"\nERROR: {result.error_message}")


async def save_to_posts(brand_kit_id: str, result):
    """Save generated carousel to posts table."""
    print("\n" + "=" * 80)
    print("SAVING TO DATABASE")
    print("=" * 80)
    
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
    
    # Build carousel metadata
    carousel_metadata = {
        'carousel_id': result.carousel_id,
        'brand_kit_id': brand_kit_id,
        'prompt': TEST_USER_PROMPT,
        'num_slides': len(result.carousel_slides_urls)
    }
    
    # Add evaluation metrics summary if available
    if result.evaluation_metrics:
        carousel_metadata['evaluation_summary'] = {
            'format_type': result.evaluation_metrics.format_type_evaluation,
            'brand_alignment': result.evaluation_metrics.brand_kit_evaluation,
            'complete_story': result.evaluation_metrics.complete_story_evaluation,
        }
    
    # Now create the post with campaign_id
    post_data = {
        'user_id': TEST_USER_ID,
        'campaign_id': campaign_id,
        'carousel_slides': result.carousel_slides_urls,
        'carousel_metadata': carousel_metadata,
        'final_caption': TEST_USER_PROMPT,
        'platform': 'instagram',
        'status': 'draft'
    }
    
    post = supabase.table('posts').insert(post_data).execute()
    print(f"  Created post: {post.data[0]['id']}")
    print("=" * 80)


async def cleanup():
    """Optional: Clean up test data."""
    response = input("\nDelete test data? (y/n): ")
    if response.lower() != 'y':
        print("\nSkipping cleanup - test data preserved")
        return
    
    print("\n" + "=" * 80)
    print("CLEANING UP TEST DATA")
    print("=" * 80)
    
    supabase = get_supabase_admin_client()
    
    # Delete posts, campaigns, and brand kits
    supabase.table('posts').delete().eq('user_id', TEST_USER_ID).execute()
    supabase.table('campaigns').delete().eq('user_id', TEST_USER_ID).execute()
    supabase.table('brand_kits').delete().eq('user_id', TEST_USER_ID).execute()
    print("  Deleted brand kit, campaign, and posts")
    
    # Note: Storage images remain (manual cleanup if needed)
    print("  Note: Storage images remain (cleanup manually if needed)")
    print("=" * 80)


async def main():
    """Main execution flow."""
    # Setup logging with file output enabled
    setup_logging(log_level="INFO")
    
    print("=" * 80)
    print("FULL PIPELINE TEST")
    print("=" * 80)
    print(f"\nLogging Configuration:")
    print(f"  - Level: INFO")
    print(f"  - Console: Enabled")
    print(f"  - File: backend/logs/scale66.log")
    print("=" * 80)
    
    check_prerequisites()
    
    brand_kit_id = await setup_test_data()
    
    try:
        result = await run_pipeline(brand_kit_id)
        display_results(result)
        
        if result.success:
            await save_to_posts(brand_kit_id, result)
        
    except Exception as e:
        print(f"\n{'=' * 80}")
        print(f"PIPELINE FAILED")
        print(f"{'=' * 80}")
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print(f"\nCheck logs for details in: backend/logs/")
    finally:
        await cleanup()


if __name__ == "__main__":
    asyncio.run(main())

