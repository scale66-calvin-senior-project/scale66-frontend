#!/bin/bash

echo "🎨 Starting Streamlit Test Frontend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Start Streamlit
echo "🖥️ Starting Streamlit frontend..."
streamlit run streamlit_app/main.py