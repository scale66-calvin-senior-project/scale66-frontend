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

def main():
    st.title("📚 Story Pipeline Tester")
    st.markdown("Test your agentic story generation pipeline")
    
    # Check backend health
    backend_status = check_backend_health()
    if backend_status:
        st.success("✅ Backend is running")
    else:
        st.error("❌ Backend is not running")
        st.info("Start the backend with: `python main.py` or `./run_all.sh`")
        st.stop()
    
    # Create two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🎬 Create New Story")
        
        with st.form("story_form"):
            story_idea = st.text_area(
                "Story Idea",
                placeholder="Enter your story concept here...",
                height=100,
                value="A young wizard discovers a magical library that contains books from the future"
            )
            
            num_slides = st.slider(
                "Number of Slides",
                min_value=1,
                max_value=10,
                value=5
            )
            
            submitted = st.form_submit_button("🚀 Generate Story")
            
            if submitted:
                if not story_idea.strip():
                    st.error("Please enter a story idea")
                else:
                    with st.spinner("Creating story pipeline..."):
                        pipeline_id = create_story(story_idea, num_slides)
                        
                    if pipeline_id:
                        st.success(f"✅ Pipeline created!")
                        st.code(f"Pipeline ID: {pipeline_id}")
                        st.session_state.current_pipeline_id = pipeline_id
                        
                        # Auto-refresh to show status
                        st.rerun()
    
    with col2:
        st.header("📊 Pipeline Status")
        
        # Input for pipeline ID
        pipeline_id = st.text_input(
            "Pipeline ID",
            value=st.session_state.get("current_pipeline_id", ""),
            placeholder="Enter pipeline ID to check status..."
        )
        
        col2a, col2b = st.columns([1, 1])
        with col2a:
            check_status = st.button("🔍 Check Status")
        with col2b:
            auto_refresh = st.button("🔄 Auto Refresh")
        
        if (check_status or auto_refresh) and pipeline_id:
            status = get_pipeline_status(pipeline_id)
            
            if status:
                # Display basic status
                status_text = status.get("status", "unknown")
                if status_text == "completed":
                    st.success(f"Status: {status_text}")
                elif status_text == "failed":
                    st.error(f"Status: {status_text}")
                elif status_text in ["pending", "planning", "story_generation", "style_generation", "content_generation", "final_assembly"]:
                    st.info(f"Status: {status_text}")
                else:
                    st.warning(f"Status: {status_text}")
                
                # Show progress
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
                progress = progress_map.get(status_text, 0.1)
                st.progress(progress)
                
                # Auto-refresh for in-progress pipelines
                if auto_refresh and status_text not in ["completed", "failed"]:
                    time.sleep(2)
                    st.rerun()
    
    # Results section
    if pipeline_id:
        st.header("📋 Pipeline Results")
        
        if st.button("📄 Get Full Results"):
            status = get_pipeline_status(pipeline_id)
            
            if status:
                # Show story request
                if "story_request" in status:
                    st.subheader("📝 Original Request")
                    req = status["story_request"]
                    st.write(f"**Idea:** {req.get('story_idea', 'N/A')}")
                    st.write(f"**Slides:** {req.get('num_slides', 'N/A')}")
                
                # Show complete story
                if status.get("complete_story"):
                    st.subheader("📖 Complete Story")
                    story = status["complete_story"]
                    st.text_area("Generated Story", story, height=200, disabled=True)
                
                # Show style guide
                if status.get("style_guide"):
                    st.subheader("🎨 Style Guide")
                    style_guide = status["style_guide"]
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        st.write(f"**Mood:** {style_guide.get('mood', 'N/A')}")
                        st.write(f"**Imagery Style:** {style_guide.get('imagery_style', 'N/A')}")
                    with col4:
                        if style_guide.get("color_palette"):
                            st.write("**Color Palette:**")
                            colors = style_guide["color_palette"]
                            st.write(", ".join(colors[:5]))
                
                # Show scenes
                if status.get("scenes"):
                    st.subheader("🎬 Scenes")
                    scenes = status["scenes"]
                    
                    for i, scene in enumerate(scenes):
                        with st.expander(f"Scene {scene.get('scene_number', i+1)}"):
                            st.write("**Content:**")
                            st.write(scene.get("content", "No content"))
                            
                            if scene.get("slide_text"):
                                st.write("**Slide Text:**")
                                st.write(scene["slide_text"])
                            
                            if scene.get("image_path"):
                                st.write(f"**Image Path:** {scene['image_path']}")
                
                # Raw JSON
                with st.expander("🔍 Raw JSON Data"):
                    st.json(status)

    # Footer
    st.markdown("---")
    col_footer1, col_footer2, col_footer3 = st.columns(3)
    with col_footer1:
        st.markdown("📖 [API Docs](http://localhost:8000/docs)")
    with col_footer2:
        st.markdown("🔗 [Backend Health](http://localhost:8000/api/v1/health)")
    with col_footer3:
        if st.button("🗑️ Clear Session"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()