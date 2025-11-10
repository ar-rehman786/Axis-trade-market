@REM @echo off
@REM REM APS One-Click Runner
@REM setlocal
@REM set ENGINE_DIR=%~dp0engine
@REM set CSV=%~dp0input\test.csv

@REM if not exist "%CSV%" (
@REM   echo [ERROR] Missing input\test.csv
@REM   echo Put a small CSV named test.csv into the input folder, then run again.
@REM   pause
@REM   exit /b 1
@REM )

@REM where py >nul 2>nul
@REM if %errorlevel%==0 (
@REM   py "%ENGINE_DIR%\aps_pipeline.py" "%CSV%"
@REM ) else (
@REM   python "%ENGINE_DIR%\aps_pipeline.py" "%CSV%"
@REM )
@REM echo.
@REM echo ===== Open APS_Market_Intelligence_Live\test_DEMO.pdf to view the report =====
@REM pause



@echo off
REM APS Market Intelligence - One-Click Runner
REM Phase 2 Complete: CSV Processing + Database + PDF + API

cls
echo ============================================================
echo APS MARKET INTELLIGENCE - ONE-CLICK RUNNER
echo ============================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Run main pipeline
echo Running pipeline...
echo.
py aps_main.py input\test.csv

echo.
echo ============================================================
echo PIPELINE COMPLETE
echo ============================================================
echo.
echo To start API server, run:
echo   py -m uvicorn engine.aps_api:app --reload --port 8080
echo.
echo Or simply run: START_API.bat
echo.
echo ============================================================
pause