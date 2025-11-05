#!/bin/bash

echo "🚀 Starting Story Pipeline - Backend & Frontend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Verify installation
echo "✅ Verifying installation..."
pip list | grep fastapi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
fi

echo "🏃 Starting backend..."
echo "📡 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🧪 Test Script: python test_pipeline.py"
echo ""
echo "Press Ctrl+C to stop the backend"
echo ""

# Start backend in background
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

echo "✅ Backend started!"
echo "🎨 Starting Streamlit frontend..."

# Start frontend in background
streamlit run streamlit_app/main.py &
FRONTEND_PID=$!

echo ""
echo "🎉 Both services are running:"
echo "  📡 Backend API: http://localhost:8000"
echo "  📖 API Docs: http://localhost:8000/docs"
echo "  🖥️ Frontend: http://localhost:8501"
echo "  🧪 Test Script: python test_pipeline.py"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for either process to exit
wait