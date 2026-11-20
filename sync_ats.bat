@echo off
echo Starting JobLens ATS Multi-Company Ingestion Engine...
cd /d "%~dp0"
call .\venv\Scripts\activate.bat
python -m backend.trackers.engine
pause
