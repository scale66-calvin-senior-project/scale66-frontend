import streamlit as st
import requests
import json
import time
from typing import Optional, Dict, Any

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

def create_story(story_idea: str, num_slides: int) -> Optional[str]:
    """Create a new story pipeline"""
    try:
        payload = {
            "story_idea": story_idea,
            "num_slides": num_slides
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
    
    with st.form("story_form"):
        story_idea = st.text_area(
            "Story Idea",
            placeholder="Enter your story concept here...",
            height=100
        )
        
        num_slides = st.slider(
            "Number of Slides",
            min_value=1,
            max_value=20,
            value=5
        )
        
        submitted = st.form_submit_button("Generate Story")
        
        if submitted:
            if not story_idea.strip():
                st.error("Please enter a story idea")
                return
                
            with st.spinner("Creating story pipeline..."):
                pipeline_id = create_story(story_idea, num_slides)
                
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
                st.subheader("📝 Story Request")
                st.write(f"**Idea:** {status['story_request']['story_idea']}")
                st.write(f"**Slides:** {status['story_request']['num_slides']}")
            
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
            
            # Show scenes
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
                            idea = pipeline_data['story_request'].get('story_idea', '')
                            st.write(f"**Idea:** {idea[:100]}{'...' if len(idea) > 100 else ''}")
                        
                        if st.button(f"View Details", key=f"view_{pipeline_id}"):
                            st.session_state.current_pipeline_id = pipeline_id
                            st.experimental_rerun()

if __name__ == "__main__":
    main()