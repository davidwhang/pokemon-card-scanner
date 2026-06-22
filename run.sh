#!/bin/bash

# Pokemon Card Scanner - Quick Start

echo "🎴 Pokemon Card Scanner - Starting..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python first."
    exit 1
fi

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set!"
    echo "Get your API key at: https://console.anthropic.com/"
    read -p "Enter your Anthropic API key: " API_KEY
    export ANTHROPIC_API_KEY="$API_KEY"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run the app
echo "✅ Starting server at http://localhost:5000"
python3 app.py
