#!/bin/bash
# Overview:
# - Purpose: Boot the backend API with dependencies ensured inside a virtual environment.
# Key Steps:
# - Provision venv, install dependencies, create env file, and run FastAPI.

echo "🚀 Starting Carousel Pipeline Backend..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
if [ ! -f ".env" ]; then
    cp .env.example .env
fi
python main.py