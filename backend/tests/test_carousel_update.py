"""
Test script for the updated carousel system
Tests the new business-focused input parameters and TikTok content strategist integration
"""

def test_request_format():
    """Test that the new request format works"""
    from app.models.pipeline import StoryRequest
    
    # Test new business-focused parameters
    request = StoryRequest(
        niche="Personal Finance",
        target_audience="Young professionals (25-35) struggling with debt",
        pain_point="Living paycheck to paycheck despite good income",
        cta_goal="save post"
    )
    
    print("StoryRequest with business parameters created successfully")
    print(f"   Niche: {request.niche}")
    print(f"   Target Audience: {request.target_audience}")
    print(f"   Pain Point: {request.pain_point}")
    print(f"   CTA Goal: {request.cta_goal}")
    return request

def test_carousel_models():
    """Test the new carousel-specific models"""
    from app.models.pipeline import CarouselSlide, CarouselResult
    
    # Test CarouselSlide
    slide = CarouselSlide(
        slide_number=1,
        slide_purpose="Hook - Pattern Interrupt",
        text_on_screen="I made this mistake and lost $10,000 in 6 months",
        image_generation_prompt="Close-up of a stressed young professional looking at bank statements on their phone, warm lighting, realistic photography style, showing genuine concern and worry"
    )
    
    print("CarouselSlide model works correctly")
    print(f"   Slide #{slide.slide_number}: {slide.slide_purpose}")
    
    # Test CarouselResult
    result = CarouselResult(
        format_type="Story/Case Study",
        slides=[slide],
        why_this_works=[
            "Strong emotional hook with specific numbers",
            "Targets exact pain point of audience",
            "Creates curiosity gap"
        ]
    )
    
    print("CarouselResult model works correctly")
    print(f"   Format: {result.format_type}")
    print(f"   Number of slides: {len(result.slides)}")
    print(f"   Reasons it works: {len(result.why_this_works)}")
    
    return result

def test_prompt_building():
    """Test the carousel prompt building"""
    from app.agents.carousel_generator import CarouselGeneratorAgent
    
    request = test_request_format()
    agent = CarouselGeneratorAgent({})
    
    prompt = agent._build_carousel_prompt(request)
    
    print("Carousel prompt built successfully")
    print(f"   Prompt length: {len(prompt)} characters")
    
    # Check that business parameters are included
    assert request.niche in prompt, "Niche not found in prompt"
    assert request.target_audience in prompt, "Target audience not found in prompt" 
    assert request.pain_point in prompt, "Pain point not found in prompt"
    assert request.cta_goal in prompt, "CTA goal not found in prompt"
    
    print("All business parameters correctly included in prompt")
    
    # Check that the TikTok strategist instructions are included
    assert "TikTok content strategist" in prompt, "TikTok strategist role not found"
    assert "CAROUSEL FORMAT OPTIONS:" in prompt, "Format options not found"
    assert "WHY THIS WORKS FOR TIKTOK:" in prompt, "Performance analysis section not found"
    
    print("TikTok content strategist prompt structure correctly included")
    
    return prompt

def main():
    """Run all tests"""
    print("Testing Updated Carousel System")
    print("=" * 50)
    
    try:
        # Test 1: New request format
        print("\n1. Testing Business-Focused Request Format:")
        test_request_format()
        
        # Test 2: Carousel models
        print("\n2. Testing Carousel-Specific Models:")
        test_carousel_models()
        
        # Test 3: Prompt building
        print("\n3. Testing TikTok Content Strategist Prompt Integration:")
        test_prompt_building()
        
        print("\n" + "=" * 50)
        print("All tests passed! The carousel system has been successfully updated.")
        print("\nSummary of changes:")
        print("   - Input now focuses on business information (niche, audience, pain point, CTA goal)")
        print("   - Integrated full TikTok content strategist prompt with 12 format options")
        print("   - Added carousel-specific models for structured output")
        print("   - Created new /carousel/create API endpoint")
        print("   - Updated pipeline to generate carousel content and images")
        
        print("\nNext steps:")
        print("   - Install dependencies: pip install -r requirements.txt")
        print("   - Add API keys to .env file for AI services")
        print("   - Test with real API calls: POST /carousel/create")
        
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()