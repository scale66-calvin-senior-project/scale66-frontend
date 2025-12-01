"""
Full Pipeline Test - End-to-end test with real Supabase and AI APIs.

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
    "Create a carousel that gives a couple useful tips to solopreneurs on how to improve their social media presence, with a soft CTA for scale66 at the end"
)


def check_prerequisites():
    """Verify required environment variables and storage bucket."""
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
        print(f"\nERROR: Missing environment variables: {', '.join(missing)}")
        print("Add these to backend/.env and try again.")
        print("=" * 80)
        sys.exit(1)
    
    print("  Environment variables: OK")
    
    supabase = get_supabase_admin_client()
    try:
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        if 'carousel-slides' not in bucket_names:
            print("\n  WARNING: Storage bucket 'carousel-slides' not found!")
            print("  Create it in Supabase Dashboard > Storage")
            sys.exit(1)
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
    
    try:
        existing = supabase.table('users').select('*').eq('id', TEST_USER_ID).execute()
        if not existing.data:
            supabase.table('users').insert({
                'id': TEST_USER_ID,
                'email': 'test@example.com',
                'subscription_tier': 'free',
                'onboarding_completed': True
            }).execute()
            print(f"  Created test user")
        else:
            print(f"  Test user exists")
    except Exception as e:
        print(f"  WARNING: User setup failed: {e}")
    
    try:
        supabase.table('brand_kits').delete().eq('user_id', TEST_USER_ID).execute()
    except Exception:
        pass
    
    result = supabase.table('brand_kits').insert({
        'user_id': TEST_USER_ID,
        **TEST_BRAND_KIT_DATA
    }).execute()
    
    brand_kit_id = result.data[0]['id']
    print(f"  Created brand kit: {brand_kit_id}")
    print(f"  Brand: {TEST_BRAND_KIT_DATA['brand_name']}")
    print("=" * 80)
    
    return brand_kit_id


async def run_pipeline(brand_kit_id: str):
    """Run the full orchestrator pipeline."""
    print("\n" + "=" * 80)
    print("RUNNING PIPELINE")
    print("=" * 80)
    print(f"Brand Kit: {brand_kit_id}")
    print(f"Prompt: {TEST_USER_PROMPT}")
    print("\nEstimated time: 2-3 minutes")
    print("=" * 80)
    
    result = await orchestrator.run(OrchestratorInput(
        brand_kit_id=brand_kit_id,
        user_prompt=TEST_USER_PROMPT
    ))
    
    return result


def display_results(result):
    """Display pipeline results."""
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETED")
    print("=" * 80)
    
    if result.success:
        print(f"Status: Image generation complete")
        print(f"Note: Finalizer disabled - images not uploaded")
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("  Review generated images in pipeline logs")
        print("  View logs: backend/logs/")
        print("=" * 80)
    else:
        print(f"\nERROR: {result.error_message}")


async def save_to_posts(brand_kit_id: str, result):
    """Save generated carousel to posts table (DISABLED - no uploads without finalizer)."""
    print("\nSkipping database save - finalizer disabled")
    return


async def cleanup():
    """Clean up test data."""
    response = input("\nDelete test data? (y/n): ")
    if response.lower() != 'y':
        print("Test data preserved")
        return
    
    print("\n" + "=" * 80)
    print("CLEANUP")
    print("=" * 80)
    
    supabase = get_supabase_admin_client()
    
    supabase.table('posts').delete().eq('user_id', TEST_USER_ID).execute()
    supabase.table('campaigns').delete().eq('user_id', TEST_USER_ID).execute()
    supabase.table('brand_kits').delete().eq('user_id', TEST_USER_ID).execute()
    print("  Deleted test data")
    print("  Note: Storage images remain")
    print("=" * 80)


async def main():
    """Main execution flow."""
    setup_logging(log_level="INFO")
    
    print("=" * 80)
    print("FULL PIPELINE TEST")
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
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"Check logs: backend/logs/")
    finally:
        await cleanup()


if __name__ == "__main__":
    asyncio.run(main())

