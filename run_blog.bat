@echo off
REM Activation script for the auto_blog virtual environment

REM Get the directory of this script
SET SCRIPT_DIR=%~dp0

REM Activate the virtual environment
call "/var/www/html/github/auto_blog_script/venv\Scripts\activate.bat"

REM Inform the user
echo Virtual environment activated. Run 'python run_autoblog.py' to start the system.
