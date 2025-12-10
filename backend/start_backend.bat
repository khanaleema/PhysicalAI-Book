@echo off
echo Starting Physical AI Book Backend API...
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy env.example to .env and add your API keys
    echo.
    pause
    exit /b 1
)

echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop
echo.

python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

