@echo off
REM Activate virtual environment and run the auto_blog system

REM Get the script directory
SET "SCRIPT_DIR=%~dp0"

REM Activate virtual environment
CALL "%SCRIPT_DIR%venv\Scripts\activate.bat"

REM Run the auto_blog system
python "%SCRIPT_DIR%run.py" %*

pause
