import json
import os
import time
from typing import Optional, Dict, Any

import streamlit as st
import requests

# Configure page
st.set_page_config(
    page_title="Story Pipeline Tester",
    page_icon="📚",
    layout="wide"
)

# Backend API URL
API_BASE_URL = "http://localhost:8000/api/v1"

def check_backend_health() -> bool:
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def create_story(niche: str, target_audience: str, pain_point: str, cta_goal: str, num_slides: Optional[int] = None) -> Optional[str]:
    """Create a new story pipeline"""
    try:
        story_idea = (
            f"Create a story for the {niche} niche targeting {target_audience}. "
            f"Highlight how it solves {pain_point} and encourage viewers to {cta_goal}."
        )

        payload = {
            "story_idea": story_idea,
            "niche": niche,
            "target_audience": target_audience,
            "pain_point": pain_point,
            "cta_goal": cta_goal,
            "num_slides": num_slides,
        }
            
        response = requests.post(f"{API_BASE_URL}/story/create", json=payload)
        if response.status_code == 200:
            return response.json()["pipeline_id"]
        else:
            st.error(f"Error creating story: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None

def get_pipeline_status(pipeline_id: str) -> Optional[Dict[str, Any]]:
    """Get pipeline status"""
    try:
        response = requests.get(f"{API_BASE_URL}/story/{pipeline_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error getting status: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None

def list_all_pipelines() -> Optional[Dict[str, Any]]:
    """List all pipelines"""
    try:
        response = requests.get(f"{API_BASE_URL}/stories")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error listing stories: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None

def main():
    st.title("📚 Story Pipeline Tester")
    st.markdown("Test the agentic story generation pipeline")
    
    # Check backend health
    backend_status = check_backend_health()
    if backend_status:
        st.success("✅ Backend is running")
    else:
        st.error("❌ Backend is not running. Start the backend with: `python main.py`")
        st.stop()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Create Story", "View Results", "All Pipelines"])
    
    if page == "Create Story":
        create_story_page()
    elif page == "View Results":
        view_results_page()
    elif page == "All Pipelines":
        all_pipelines_page()

def create_story_page():
    st.header("🎬 Create New Story")
    st.markdown("Enter your business context to generate a targeted story and carousel:")
    
    with st.form("story_form"):
        st.subheader("📊 Business Context")
        
        niche = st.text_input(
            "Niche",
            value="Social media marketing",
            placeholder="e.g., Fitness coaching, SaaS for restaurants, Real estate...",
            help="What industry or market are you in?"
        )
        
        target_audience = st.text_input(
            "Target Audience", 
            value="Solopreneurs and small business owners",
            placeholder="e.g., Busy professionals aged 25-40, Small restaurant owners...",
            help="Who is your ideal customer?"
        )
        
        pain_point = st.text_area(
            "Pain Point",
            value=(
                "Can't afford marketing agency, seeing no social media awareness, spending too much time "
                "creating social media content, not being able to work on the business since they are too "
                "busy creating marketing content instead, no customers, no money."
            ),
            placeholder="e.g., Struggling to find time for exercise, Managing inventory is complex...",
            height=80,
            help="What problem does your audience face?"
        )
        
        cta_goal = st.text_input(
            "Goal (Call-to-Action)",
            value="Brand Awareness through useful tips",
            placeholder="e.g., Book a free consultation, Sign up for 7-day trial...",
            help="What action do you want them to take?"
        )
        
        st.subheader("⚙️ Optional Settings")
        num_slides = 3
        
        submitted = st.form_submit_button("Generate Story & Carousel")
        
        if submitted:
            # Validate required fields
            if not all([niche.strip(), target_audience.strip(), pain_point.strip(), cta_goal.strip()]):
                st.error("Please fill in all business context fields")
                return
                
            with st.spinner("Creating story pipeline..."):
                pipeline_id = create_story(niche, target_audience, pain_point, cta_goal, num_slides)
                
            if pipeline_id:
                st.success(f"✅ Pipeline created! ID: `{pipeline_id}`")
                st.session_state.current_pipeline_id = pipeline_id
                
                # Show real-time status
                status_placeholder = st.empty()
                progress_bar = st.progress(0)
                
                for i in range(30):  # Check for 30 seconds
                    status = get_pipeline_status(pipeline_id)
                    if status:
                        current_status = status.get("status", "unknown")
                        status_placeholder.info(f"Status: {current_status}")
                        
                        # Update progress bar based on status
                        progress_map = {
                            "pending": 0.1,
                            "planning": 0.2,
                            "story_generation": 0.4,
                            "style_generation": 0.6,
                            "content_generation": 0.8,
                            "final_assembly": 0.9,
                            "completed": 1.0,
                            "failed": 0.0
                        }
                        progress_bar.progress(progress_map.get(current_status, 0.1))
                        
                        if current_status in ["completed", "failed"]:
                            break
                            
                    time.sleep(1)
                
                st.info(f"💡 Go to 'View Results' page and enter pipeline ID: `{pipeline_id}`")

def view_results_page():
    st.header("📊 View Pipeline Results")
    
    pipeline_id = st.text_input(
        "Pipeline ID",
        value=st.session_state.get("current_pipeline_id", ""),
        placeholder="Enter pipeline ID..."
    )
    
    if st.button("Get Status") and pipeline_id:
        status = get_pipeline_status(pipeline_id)
        
        if status:
            # Display basic info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Status", status.get("status", "unknown"))
            with col2:
                st.metric("Slides", len(status.get("scenes", [])))
            with col3:
                created_at = status.get("created_at", "")
                st.metric("Created", created_at[:10] if created_at else "unknown")
            
            # Show story request
            if "story_request" in status:
                st.subheader("📝 Business Context")
                request = status['story_request']
                st.write(f"**Niche:** {request.get('niche', 'N/A')}")
                st.write(f"**Target Audience:** {request.get('target_audience', 'N/A')}")
                st.write(f"**Pain Point:** {request.get('pain_point', 'N/A')}")
                st.write(f"**Goal:** {request.get('cta_goal', 'N/A')}")
                if request.get('num_slides'):
                    st.write(f"**Slides:** {request['num_slides']}")
            
            # Show complete story
            if status.get("complete_story"):
                st.subheader("📖 Complete Story")
                st.text_area("Story", status["complete_story"], height=200, disabled=True)
            
            # Show style guide
            if status.get("style_guide"):
                st.subheader("🎨 Style Guide")
                style_guide = status["style_guide"]
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Mood:** {style_guide.get('mood', 'N/A')}")
                    st.write(f"**Imagery Style:** {style_guide.get('imagery_style', 'N/A')}")
                with col2:
                    if style_guide.get("color_palette"):
                        st.write("**Color Palette:**")
                        cols = st.columns(len(style_guide["color_palette"]))
                        for i, color in enumerate(style_guide["color_palette"]):
                            cols[i].color_picker("", color, disabled=True)
            
            # Show carousel result and images
            carousel = status.get("carousel_result")
            if carousel:
                st.subheader("🖼️ Carousel Slides")
                slides = carousel.get("slides", []) or []
                for slide in slides:
                    slide_number = slide.get("slide_number")
                    slide_title = slide.get("slide_purpose", "Slide")
                    expander_label = f"Slide {slide_number}: {slide_title}" if slide_number else slide_title
                    with st.expander(expander_label, expanded=False):
                        if slide.get("text_on_screen"):
                            st.markdown(f"**Text on Screen:** {slide['text_on_screen']}")
                        if slide.get("image_generation_prompt"):
                            with st.expander("Prompt", expanded=False):
                                st.write(slide["image_generation_prompt"])

                        image_path = slide.get("image_path")
                        if image_path:
                            resolved_path = image_path
                            if not os.path.isabs(resolved_path):
                                resolved_path = os.path.abspath(os.path.join(os.getcwd(), resolved_path))

                            if os.path.exists(resolved_path):
                                st.image(resolved_path, caption=f"Slide {slide_number}" if slide_number else None, use_column_width=True)
                            else:
                                st.warning(f"Image file not found: {resolved_path}")
                        else:
                            st.info("Image not yet generated for this slide.")

            # Show scenes (legacy story data)
            if status.get("scenes"):
                st.subheader("🎬 Scenes")
                for scene in status["scenes"]:
                    with st.expander(f"Scene {scene['scene_number']}"):
                        st.write("**Content:**")
                        st.write(scene["content"])
                        if scene.get("slide_text"):
                            st.write("**Slide Text:**")
                            st.write(scene["slide_text"])
                        if scene.get("image_path"):
                            st.write(f"**Image Path:** {scene['image_path']}")
            
            # Show raw JSON
            with st.expander("🔍 Raw JSON"):
                st.json(status)

def all_pipelines_page():
    st.header("📚 All Pipelines")
    
    if st.button("Refresh"):
        pipelines = list_all_pipelines()
        
        if pipelines:
            if not pipelines:
                st.info("No pipelines found")
            else:
                for pipeline_id, pipeline_data in pipelines.items():
                    with st.expander(f"Pipeline: {pipeline_id[:8]}..."):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Status:** {pipeline_data.get('status', 'unknown')}")
                        with col2:
                            st.write(f"**Slides:** {len(pipeline_data.get('scenes', []))}")
                        with col3:
                            created = pipeline_data.get('created_at', '')
                            st.write(f"**Created:** {created[:10] if created else 'unknown'}")
                        
                        if pipeline_data.get('story_request'):
                            request = pipeline_data['story_request']
                            niche = request.get('niche', '')
                            st.write(f"**Niche:** {niche[:50]}{'...' if len(niche) > 50 else ''}")
                            target = request.get('target_audience', '')
                            if target:
                                st.write(f"**Target:** {target[:50]}{'...' if len(target) > 50 else ''}")
                        
                        if st.button(f"View Details", key=f"view_{pipeline_id}"):
                            st.session_state.current_pipeline_id = pipeline_id
                            st.experimental_rerun()

if __name__ == "__main__":
    main()