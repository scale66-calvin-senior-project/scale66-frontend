#!/usr/bin/env python3
"""
Simple test script for the story pipeline API
"""
import requests
import json
import time
import sys

API_BASE = "http://localhost:8000/api/v1"

def test_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def create_story(story_idea, num_slides=5):
    """Create a story pipeline"""
    payload = {
        "story_idea": story_idea,
        "num_slides": num_slides
    }
    
    try:
        response = requests.post(f"{API_BASE}/story/create", json=payload)
        if response.status_code == 200:
            data = response.json()
            pipeline_id = data["pipeline_id"]
            print(f"✅ Pipeline created: {pipeline_id}")
            return pipeline_id
        else:
            print(f"❌ Failed to create story: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating story: {e}")
        return None

def get_status(pipeline_id):
    """Get pipeline status"""
    try:
        response = requests.get(f"{API_BASE}/story/{pipeline_id}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get status: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting status: {e}")
        return None

def monitor_pipeline(pipeline_id, max_wait=60):
    """Monitor pipeline until completion"""
    print(f"🔄 Monitoring pipeline {pipeline_id}...")
    
    for i in range(max_wait):
        status_data = get_status(pipeline_id)
        if not status_data:
            return None
            
        status = status_data.get("status", "unknown")
        print(f"  Status: {status}")
        
        if status == "completed":
            print("✅ Pipeline completed!")
            return status_data
        elif status == "failed":
            error = status_data.get("error_message", "Unknown error")
            print(f"❌ Pipeline failed: {error}")
            return status_data
            
        time.sleep(1)
    
    print("⏰ Pipeline monitoring timed out")
    return get_status(pipeline_id)

def display_results(result):
    """Display pipeline results"""
    print("\n" + "="*50)
    print("📊 PIPELINE RESULTS")
    print("="*50)
    
    # Basic info
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Created: {result.get('created_at', 'unknown')}")
    
    # Story request
    if "story_request" in result:
        req = result["story_request"]
        print(f"\n📝 Original Request:")
        print(f"  Idea: {req.get('story_idea', 'N/A')}")
        print(f"  Slides: {req.get('num_slides', 'N/A')}")
    
    # Complete story
    if result.get("complete_story"):
        print(f"\n📖 Complete Story:")
        story = result["complete_story"]
        print(f"  {story[:200]}{'...' if len(story) > 200 else ''}")
    
    # Scenes
    scenes = result.get("scenes", [])
    if scenes:
        print(f"\n🎬 Scenes ({len(scenes)}):")
        for scene in scenes[:3]:  # Show first 3 scenes
            content = scene.get("content", "")
            print(f"  Scene {scene.get('scene_number', '?')}: {content[:100]}{'...' if len(content) > 100 else ''}")
        if len(scenes) > 3:
            print(f"  ... and {len(scenes) - 3} more scenes")
    
    # Style guide
    if result.get("style_guide"):
        style = result["style_guide"]
        print(f"\n🎨 Style Guide:")
        print(f"  Mood: {style.get('mood', 'N/A')}")
        print(f"  Style: {style.get('imagery_style', 'N/A')}")
        if style.get("color_palette"):
            colors = ", ".join(style["color_palette"][:3])
            print(f"  Colors: {colors}")

def main():
    print("🚀 Story Pipeline Test Script")
    print("-" * 30)
    
    # Test API health
    if not test_health():
        print("\n💡 Make sure the backend is running with: python main.py")
        sys.exit(1)
    
    # Get story idea from user or use default
    if len(sys.argv) > 1:
        story_idea = " ".join(sys.argv[1:])
    else:
        story_idea = input("\n📝 Enter your story idea (or press Enter for default): ").strip()
        if not story_idea:
            story_idea = "A young wizard discovers a magical library that contains books from the future"
    
    print(f"\n🎭 Creating story: {story_idea}")
    
    # Create pipeline
    pipeline_id = create_story(story_idea, 5)
    if not pipeline_id:
        sys.exit(1)
    
    # Monitor pipeline
    result = monitor_pipeline(pipeline_id)
    if result:
        display_results(result)
    
    print(f"\n🔗 API Documentation: http://localhost:8000/docs")
    print(f"🔍 View full result: GET {API_BASE}/story/{pipeline_id}")

if __name__ == "__main__":
    main()