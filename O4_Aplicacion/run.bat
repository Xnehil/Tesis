@echo off
setlocal

REM Settear pwd como Tesis (raiz del proyecto)
cd /d %~dp0

REM chequar pwd
echo %cd%

REM Check if the virtual environment exists
if not exist "validaciones\.venv\Scripts\activate" (
    echo [ERROR] Virtual environment not found. Please create it first.
    exit /b 1
)



REM Activate the virtual environment
echo Activando entorno virtual
call .\validaciones\.venv\Scripts\activate

REM Check if Flask is installed
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Flask is not installed in the virtual environment. Please install it first.
    exit /b 1
)

REM Set environment variables
echo Setteando variables de entorno
set FLASK_APP=validaciones\app.py
set FLASK_ENV=development


REM Run Flask
echo Starting Flask server...
flask run

REM End the script
endlocal