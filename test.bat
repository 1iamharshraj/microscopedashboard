@echo off
REM Microbe Insights - Windows Testing Script

echo ======================================
echo   Microbe Insights - Setup  Testing
echo ======================================
echo.

REM Check Python
echo [1/10] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    exit /b 1
)
echo.

REM Create virtual environment
echo [2/10] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created!
) else (
    echo Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo [3/10] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo [4/10] Upgrading pip...
python -m pip install --upgrade pip -q
echo.

REM Install dependencies
echo [5/10] Installing dependencies...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies!
    exit /b 1
)
echo Dependencies installed!
echo.

REM Create data directories
echo [6/10] Creating data directories...
if not exist "data" mkdir data
if not exist "data\captures" mkdir data\captures
if not exist "data\uploads" mkdir data\uploads
if not exist "data\results" mkdir data\results
echo Directories created!
echo.

REM Initialize database
echo [7/10] Initializing database...
python -c "from services.database import init_database; init_database(); print('Database initialized!')"
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize database!
    exit /b 1
)
echo.

REM Test imports
echo [8/10] Testing imports...
python -c "import flask; print('Flask OK')"
python -c "import cv2; print('OpenCV OK')"
python -c "import numpy; print('NumPy OK')"
python -c "from services.camera import camera_manager; print('Camera service OK')"
python -c "from services.model_microplastics import get_model_info; print('Microplastic model OK')"
python -c "from services.model_plankton import get_model_info; print('Plankton model OK')"
echo.

REM Show configuration
echo [9/10] Configuration Summary:
echo ======================================
python -c "import flask; print('Flask version:', flask.__version__)"
python -c "import cv2; print('OpenCV version:', cv2.__version__)"
python -c "import numpy; print('NumPy version:', numpy.__version__)"
echo ======================================
echo.

REM Final check
echo [10/10] Running final checks...
python -c "from services.database import get_recent_reports; reports = get_recent_reports(); print(f'Database OK - Found {len(reports)} reports')"
echo.

echo ======================================
echo   Setup Complete!
echo ======================================
echo.
echo To start the application, run:
echo   python app.py
echo.
echo Or press any key to start now...
pause > nul

REM Start application
echo.
echo ======================================
echo   Starting Flask Server...
echo ======================================
echo.
echo Server will be available at:
echo   - Local:   http://localhost:5000
echo   - Network: http://%COMPUTERNAME%:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
