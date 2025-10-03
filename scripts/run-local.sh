#!/bin/bash

# Local development runner

echo "🔬 Starting Secondary Research Workflow..."

# Activate virtual environment
source .venv/bin/activate

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Run the application
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload