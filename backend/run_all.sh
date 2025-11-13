#!/bin/bash
# Overview:
# - Purpose: Provision environment, install dependencies, and launch backend plus Streamlit together.
# Key Steps:
# - Initialize virtualenv, install packages, start FastAPI and Streamlit, and manage teardown.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "🚀 Starting Carousel Pipeline backend and frontend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
PYTHON="$SCRIPT_DIR/venv/bin/python3"
PIP="$PYTHON -m pip"
$PYTHON -m pip install --upgrade pip
$PIP install -r requirements.txt
if [ ! -f ".env" ]; then
    cp .env.example .env
fi
"$PYTHON" main.py &
BACKEND_PID=$!
sleep 3
"$SCRIPT_DIR/venv/bin/streamlit" run streamlit_app/main.py &
FRONTEND_PID=$!

cleanup() {
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM
wait