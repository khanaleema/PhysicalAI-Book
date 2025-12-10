#!/bin/bash

echo "Starting Physical AI Book Backend API..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy env.example to .env and add your API keys"
    exit 1
fi

echo "Starting FastAPI server on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

