"""
Streamlit Testing Interface - Interactive UI for carousel pipeline testing and monitoring.
Provides a web-based interface for creating carousel requests, monitoring pipeline
progress, viewing results with images, and listing all generated carousels.

Main Functions:
    1. check_backend_health() - Verifies FastAPI backend is accessible
    2. create_carousel_request() - Sends new carousel request to backend
    3. fetch_pipeline_status() - Retrieves status for specific pipeline
    4. fetch_all_pipelines() - Gets list of all pipelines
    5. render_create_page() - UI for creating new carousels with form
    6. render_results_page() - UI for viewing pipeline results and images
    7. render_list_page() - UI for browsing all pipelines
    8. _poll_pipeline_progress() - Real-time progress monitoring with status updates
    9. _display_pipeline_snapshot() - Renders complete pipeline results with images

Connections:
    - Connects to: FastAPI backend at localhost:8000
    - Uses endpoints: /carousel/create, /carousel/{id}, /carousels, /health
    - Started by: run_streamlit.sh
    - Purpose: Development testing and pipeline visualization
"""

import os
import time
from typing import Dict, Any, Optional

import requests
import streamlit as st


API_BASE_URL = "http://localhost:8000/api/v1"


def check_backend_health() -> bool:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def create_carousel_request(payload: Dict[str, Any]) -> Optional[str]:
    try:
        response = requests.post(f"{API_BASE_URL}/carousel/create", json=payload, timeout=20)
        if response.status_code == 200:
            return response.json().get("pipeline_id")
        st.error(f"Create request failed: {response.text}")
    except Exception as error:
        st.error(f"Backend connection error: {error}")
    return None


def fetch_pipeline_status(pipeline_id: str) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(f"{API_BASE_URL}/carousel/{pipeline_id}", timeout=20)
        if response.status_code == 200:
            return response.json()
        st.error(f"Status fetch failed: {response.text}")
    except Exception as error:
        st.error(f"Backend connection error: {error}")
    return None


def fetch_all_pipelines() -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(f"{API_BASE_URL}/carousels", timeout=20)
        if response.status_code == 200:
            return response.json()
        st.error(f"List fetch failed: {response.text}")
    except Exception as error:
        st.error(f"Backend connection error: {error}")
    return None


def render_create_page():
    st.header("Create Carousel")
    with st.form("carousel_form"):
        niche = st.text_input("Niche", value="Social media marketing")
        audience = st.text_input("Target Audience", value="Solopreneurs and small business owners")
        pain_point = st.text_area("Pain Point", value="Overwhelmed with content creation; no time to grow revenue.")
        cta_goal = st.text_input("Call To Action", value="Join the newsletter for weekly playbooks")
        num_slides = st.number_input("Number of Slides", min_value=3, max_value=10, value=5)
        submitted = st.form_submit_button("Generate Carousel")
    if submitted:
        if not all([niche.strip(), audience.strip(), pain_point.strip(), cta_goal.strip()]):
            st.error("Please complete every field before submitting.")
            return
        payload = {
            "niche": niche,
            "target_audience": audience,
            "pain_point": pain_point,
            "cta_goal": cta_goal,
            "num_slides": num_slides,
        }
        with st.spinner("Launching pipeline..."):
            pipeline_id = create_carousel_request(payload)
        if pipeline_id:
            st.success(f"Pipeline started: {pipeline_id}")
            st.session_state.current_pipeline_id = pipeline_id
            _poll_pipeline_progress(pipeline_id)


def _poll_pipeline_progress(pipeline_id: str):
    placeholder = st.empty()
    progress = st.progress(0)
    status_map = {
        "planning": 0.2,
        "carousel_generation": 0.5,
        "image_generation": 0.8,
        "final_assembly": 0.9,
        "completed": 1.0,
        "failed": 0.0,
    }
    for _ in range(40):
        snapshot = fetch_pipeline_status(pipeline_id)
        if not snapshot:
            time.sleep(1)
            continue
        current_status = snapshot.get("status", "unknown")
        placeholder.info(f"Status: {current_status}")
        progress.progress(status_map.get(current_status, 0.1))
        if current_status in {"completed", "failed"}:
            break
        time.sleep(1)


def render_results_page():
    st.header("Pipeline Results")
    pipeline_id = st.text_input("Pipeline ID", value=st.session_state.get("current_pipeline_id", ""))
    if st.button("Load Results") and pipeline_id:
        snapshot = fetch_pipeline_status(pipeline_id)
        if snapshot:
            _display_pipeline_snapshot(snapshot)


def _display_pipeline_snapshot(snapshot: Dict[str, Any]):
    st.subheader("Status")
    st.write(snapshot.get("status", "unknown"))
    request = snapshot.get("request", {})
    st.subheader("Request Context")
    st.json(request)
    carousel_result = snapshot.get("carousel_result")
    if carousel_result:
        st.subheader("Strategy")
        st.json(carousel_result.get("strategy", {}))
        st.subheader("Why This Works")
        for reason in carousel_result.get("why_this_works", []):
            st.write(f"• {reason}")
        st.subheader("Slides")
        for slide in carousel_result.get("slides", []):
            with st.expander(f"Slide {slide.get('slide_number')}: {slide.get('slide_purpose')}"):
                st.write(slide.get("text_on_screen"))
                prompt_text = slide.get("image_generation_prompt")
                if prompt_text:
                    st.markdown("**Image Prompt**")
                    st.write(prompt_text)
                image_path = slide.get("image_path")
                if image_path and os.path.exists(image_path):
                    st.image(image_path, use_column_width=True)


def render_list_page():
    st.header("All Pipelines")
    if st.button("Refresh"):
        snapshots = fetch_all_pipelines()
        if snapshots:
            for pipeline_id, payload in snapshots.items():
                with st.expander(f"Pipeline {pipeline_id}"):
                    st.write(payload.get("status", "unknown"))
                    st.json(payload.get("request", {}))


def main():
    st.set_page_config(page_title="Carousel Pipeline", page_icon="🎠", layout="wide")
    st.title("Carousel Pipeline Tester")
    if not check_backend_health():
        st.error("Backend is not reachable. Start the FastAPI server.")
        st.stop()
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Create", "Results", "Pipelines"])
    if page == "Create":
        render_create_page()
    elif page == "Results":
        render_results_page()
    else:
        render_list_page()


if __name__ == "__main__":
    main()

