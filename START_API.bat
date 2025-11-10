@echo off
REM APS Market Intelligence - API Server Launcher

cls
echo ============================================================
echo APS MARKET INTELLIGENCE API SERVER
echo ============================================================
echo.
echo Starting FastAPI backend on http://localhost:8080
echo Press Ctrl+C to stop server
echo.
echo ============================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Start API server on port 8080
py -m uvicorn engine.aps_api:app --reload --port 8080

pause