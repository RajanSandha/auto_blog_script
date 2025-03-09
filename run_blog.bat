@echo off
:: Activate virtual environment and set up environment for auto_blog
set SCRIPT_DIR=%~dp0
call "%SCRIPT_DIR%venv\Scripts\activate.bat"
echo Virtual environment activated. You can now run:
echo     python run_autoblog.py
echo.
echo Or to start a command prompt in the virtual environment:
echo     cmd
