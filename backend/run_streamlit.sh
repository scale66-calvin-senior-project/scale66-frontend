#!/bin/bash
# Overview:
# - Purpose: Launch the Streamlit dashboard tied to the carousel backend environment.
# Key Steps:
# - Prepare virtual environment, install dependencies, and run Streamlit app.

echo "🎨 Starting Carousel Streamlit Frontend..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app/main.py