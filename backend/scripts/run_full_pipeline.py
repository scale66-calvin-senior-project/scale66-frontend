"""
Full Pipeline Test - End-to-end test with real Supabase and AI APIs.

Run from backend directory:
    uv run python -m scripts.run_full_pipeline

Requirements:
- SUPABASE_URL, SUPABASE_SERVICE_KEY in .env
- ANTHROPIC_API_KEY, GEMINI_API_KEY in .env

Pipeline Steps:
1. Fetch BrandKit from database
2. Carousel Format Decider (Claude)
3. Strategy Generator (Claude)
4. Text Generator (Claude)
5. Image Generator (Gemini)

Note: Finalizer step is disabled - images are saved locally only.
"""

import asyncio
import sys
from pathlib import Path

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
    """Verify required environment variables."""
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
    
    # Verify Supabase connection
    try:
        supabase = get_supabase_admin_client()
        # Simple connectivity check
        supabase.table('users').select('id').limit(1).execute()
        print("  Supabase connection: OK")
    except Exception as e:
        print(f"  WARNING: Supabase connection issue: {e}")
    
    # Check local output directory
    output_dir = Path(settings.output_dir) if settings.output_dir else Path("output")
    print(f"  Local output directory: {output_dir}")
    print(f"  Save local output: {settings.save_local_output}")
    
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
    print("\nPipeline Steps:")
    print("  1. Fetch BrandKit")
    print("  2. Carousel Format Decider (Claude)")
    print("  3. Strategy Generator (Claude)")
    print("  4. Text Generator (Claude)")
    print("  5. Image Generator (Gemini)")
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
    print("PIPELINE RESULTS")
    print("=" * 80)
    
    if result.success:
        print(f"Status: SUCCESS")
        print(f"Images generated and saved locally")
        print("\n" + "-" * 40)
        print("OUTPUT LOCATIONS:")
        print("-" * 40)
        
        # Show output directory info
        output_dir = Path(settings.output_dir) if settings.output_dir else Path("output")
        print(f"  Images: {output_dir}/carousels/<timestamp>/")
        print(f"  Logs:   {backend_path}/logs/")
        
        print("\n" + "-" * 40)
        print("NEXT STEPS:")
        print("-" * 40)
        print("  1. Review generated images in output/carousels/")
        print("  2. Check pipeline logs for detailed execution info")
        print("=" * 80)
    else:
        print(f"Status: FAILED")
        print(f"Error: {result.error_message}")
        print("\n" + "-" * 40)
        print("TROUBLESHOOTING:")
        print("-" * 40)
        print("  1. Check logs in backend/logs/ for details")
        print("  2. Verify API keys are valid")
        print("  3. Check Supabase connection")
        print("=" * 80)


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
    
    try:
        supabase.table('posts').delete().eq('user_id', TEST_USER_ID).execute()
        supabase.table('campaigns').delete().eq('user_id', TEST_USER_ID).execute()
        supabase.table('brand_kits').delete().eq('user_id', TEST_USER_ID).execute()
        print("  Deleted test data from database")
    except Exception as e:
        print(f"  Cleanup warning: {e}")
    
    print("  Note: Local output files are preserved")
    print("=" * 80)


async def main():
    """Main execution flow."""
    setup_logging(log_level="INFO")
    
    print("=" * 80)
    print("FULL PIPELINE TEST")
    print("=" * 80)
    print("Testing end-to-end carousel generation pipeline")
    print("Finalizer disabled - images saved locally only")
    
    check_prerequisites()
    brand_kit_id = await setup_test_data()
    
    try:
        result = await run_pipeline(brand_kit_id)
        display_results(result)
        
    except Exception as e:
        print(f"\n{'=' * 80}")
        print(f"PIPELINE FAILED")
        print(f"{'=' * 80}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"\nCheck logs: backend/logs/")
    finally:
        await cleanup()


if __name__ == "__main__":
    asyncio.run(main())
