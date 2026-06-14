#!/bin/bash

# CreativeApp UI Launcher Script
# Phase 7: Starts the Gradio web interface

set -e

echo "🚀 Starting CreativeApp UI..."
echo "📍 Interface will be available at: http://localhost:7860"
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed"
    exit 1
fi

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import gradio" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -q gradio plotly openai pydantic sentence-transformers faiss-cpu python-dotenv pyyaml
fi

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set"
    echo "    The UI will work but agent analysis will be limited"
    echo ""
fi

# Start the application
echo "Starting Gradio interface..."
python src/ui/app.py
