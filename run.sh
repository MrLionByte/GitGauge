#!/bin/bash
# run.sh - Start FastAPI in development mode

echo "🚀 Starting FastAPI development server..."

# Activate virtual environment if exists
if [ -d ".git-gauge" ]; then
  source .git-gauge/bin/activate
fi

# Run FastAPI using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload