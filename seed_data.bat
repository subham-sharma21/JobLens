@echo off
echo Seeding JobLens Database with sample jobs...
cd /d "%~dp0"
call .\venv\Scripts\activate.bat
python -m backend.seed_data
pause
