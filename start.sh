#!/bin/bash
# start.sh - Manual startup script

echo "🚀 Starting Option Chain Analyzer..."
cd backend

# Activate virtual environment if exists
if [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Check if running in Codespaces
if [ -n "$CODESPACE_NAME" ]; then
    echo "🌐 Codespaces Environment Detected"
    python codespaces_app.py
else
    echo "💻 Local Environment Detected" 
    python run.py
fi
