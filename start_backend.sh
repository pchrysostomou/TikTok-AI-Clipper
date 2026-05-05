#!/bin/bash
cd "$(dirname "$0")/backend"
echo "🚀 Starting AI Clipper Backend on http://localhost:8002"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload
