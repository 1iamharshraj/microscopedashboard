@echo off
REM Microscope Dashboard Startup Script for Windows
REM Compatible with Windows 10/11

echo.
echo 🔬 Starting Microscope Dashboard...
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📦 Installing requirements...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install requirements
    echo 💡 Try installing PyTorch separately:
    echo    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "results" mkdir results
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js

echo ✅ Directories created

REM Display startup information
echo.
echo 🚀 Starting Flask application...
echo 📊 Dashboard will be available at: http://localhost:5000
echo 📈 Data dashboard: http://localhost:5000/data
echo ⚠️  Press Ctrl+C to stop the server
echo.

REM Start the application
python main.py

pause
