@echo off
REM CSIRT Platform Startup Script for Windows

echo ==========================================
echo CSIRT Platform Startup
echo ==========================================

REM Check if .env exists
if not exist .env (
    echo Creating .env file from .env.example...
    python scripts/setup_env.py
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Initialize database
echo Initializing database...
python scripts/init_db.py

REM Start services
echo Starting services...
echo.

echo Starting API server...
start "CSIRT API" cmd /k "python main.py"

echo Starting Celery worker...
start "Celery Worker" cmd /k "celery -A config.celery_app worker --loglevel=info"

echo Starting Celery beat...
start "Celery Beat" cmd /k "celery -A config.celery_app beat --loglevel=info"

echo.
echo ==========================================
echo Services started!
echo ==========================================
echo API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Close the windows to stop services
echo.

pause

