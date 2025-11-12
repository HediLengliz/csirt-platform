#!/bin/bash

# CSIRT Platform Startup Script

echo "=========================================="
echo "CSIRT Platform Startup"
echo "=========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    python scripts/setup_env.py
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python scripts/init_db.py

# Start services
echo "Starting services..."
echo ""
echo "Starting API server..."
python main.py &
API_PID=$!

echo "Starting Celery worker..."
celery -A config.celery_app worker --loglevel=info &
CELERY_PID=$!

echo "Starting Celery beat..."
celery -A config.celery_app beat --loglevel=info &
BEAT_PID=$!

echo ""
echo "=========================================="
echo "Services started!"
echo "=========================================="
echo "API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "kill $API_PID $CELERY_PID $BEAT_PID; exit" INT TERM
wait

