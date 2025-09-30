# 🧪 Microbe Insights - Complete Testing Guide

This guide provides step-by-step commands to set up and test the Microbe Insights application.

---

## 📋 Prerequisites Check

### Check Python Version
```bash
python --version
# Should be Python 3.6.9 or higher
```

### Check pip
```bash
pip --version
```

### Check if OpenCV is available (optional, will be installed)
```bash
python -c "import cv2; print(cv2.__version__)"
```

---

## 🚀 Complete Setup & Testing Commands

### Step 1: Navigate to Project Directory
```bash
cd h:\projects\microscopedashboard
```

### Step 2: Create Virtual Environment
```bash
# Create venv
python -m venv venv

# Activate venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# OR Activate venv (Windows CMD)
.\venv\Scripts\activate.bat

# OR Activate venv (Linux/Mac)
source venv/bin/activate
```

### Step 3: Upgrade pip (Recommended)
```bash
python -m pip install --upgrade pip
```

### Step 4: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# If you encounter issues with specific packages, install them individually:
pip install Flask==2.0.3
pip install Flask-SQLAlchemy==2.5.1
pip install opencv-python==4.5.5.64
pip install Pillow==8.4.0
pip install numpy==1.21.6
pip install SQLAlchemy==1.4.23
pip install python-dotenv==0.19.2
```

### Step 5: Verify Installation
```bash
# Check installed packages
pip list

# Verify Flask
python -c "import flask; print('Flask version:', flask.__version__)"

# Verify OpenCV
python -c "import cv2; print('OpenCV version:', cv2.__version__)"

# Verify NumPy
python -c "import numpy; print('NumPy version:', numpy.__version__)"
```

### Step 6: Create Data Directories
```bash
# Create all necessary directories
mkdir -p data\captures
mkdir -p data\uploads
mkdir -p data\results

# OR on Linux/Mac:
# mkdir -p data/{captures,uploads,results}
```

### Step 7: Initialize Database
```bash
python -c "from services.database import init_database; init_database(); print('✅ Database initialized successfully')"
```

### Step 8: Test Database Connection
```bash
python -c "from services.database import init_database, get_recent_reports; init_database(); reports = get_recent_reports(); print(f'✅ Database working! Found {len(reports)} reports')"
```

### Step 9: Test Camera Service
```bash
python -c "from services.camera import camera_manager; print('✅ Camera service imported successfully'); print('Camera manager:', camera_manager)"
```

### Step 10: Test AI Models
```bash
# Test microplastic model
python -c "from services.model_microplastics import get_model_info; info = get_model_info(); print('✅ Microplastic model:', info['name'])"

# Test plankton model
python -c "from services.model_plankton import get_model_info; info = get_model_info(); print('✅ Plankton model:', info['name'])"
```

### Step 11: Run the Application
```bash
# Start Flask server
python app.py

# The server should start on http://localhost:5000
# You should see output like:
# * Running on http://127.0.0.1:5000
# * Running on http://192.168.x.x:5000
```

---

## 🌐 Testing the Application

### Access the Application
Open your browser and visit:
- **Local:** http://localhost:5000
- **Network:** http://<your-ip>:5000

### Test Each Page

#### 1. Home Dashboard (/)
```bash
# Test home page API
curl http://localhost:5000/api/dashboard_stats
```
**Expected:** JSON response with statistics

#### 2. Capture Workflow (/capture)
- Navigate to http://localhost:5000/capture
- **Test:** Step through the 7-step workflow
- **Verify:** Each step loads correctly

#### 3. AI Lab (/chat)
```bash
# Test chat API
curl -X POST http://localhost:5000/chat_api -H "Content-Type: application/json" -d "{\"message\":\"Hello\"}"
```
**Expected:** JSON response with AI reply

#### 4. Reports (/reports)
- Navigate to http://localhost:5000/reports
- **Test:** Filter and search functionality
- **Verify:** Reports display correctly

#### 5. Analytics (/analytics)
```bash
# Test analytics API
curl http://localhost:5000/analytics/api/stats
```
**Expected:** JSON response with analytics data

#### 6. Settings (/settings)
```bash
# Test settings save
curl -X POST http://localhost:5000/settings/camera -H "Content-Type: application/json" -d "{\"width\":1280,\"height\":720,\"fps\":30}"
```
**Expected:** Success message

#### 7. Help (/help)
- Navigate to http://localhost:5000/help
- **Verify:** All help sections load

---

## 🧪 Advanced Testing

### Test Camera Streaming
```bash
# Start camera (requires actual camera hardware)
curl -X POST http://localhost:5000/camera/start -H "Content-Type: application/json" -d "{\"camera_id\":0,\"camera_type\":\"usb\",\"width\":1280,\"height\":720,\"fps\":30}"

# Get camera info
curl http://localhost:5000/camera/info

# Stop camera
curl -X POST http://localhost:5000/camera/stop -H "Content-Type: application/json" -d "{}"
```

### Test Database Operations
```python
# Run Python interactive shell
python

# Then run:
from services.database import *
init_database()

# Create test report
report_id = create_report(
    slide_name="Test Sample",
    location="Lab 1",
    user="Tester",
    microplastic_result={"present": True, "count": 5, "confidence": 0.85},
    plankton_result={"summary": {"Diatoms": 10}, "detailed": []},
    image_path="test.jpg"
)
print(f"Created report ID: {report_id}")

# Get report
report = get_report_by_id(report_id)
print(f"Report: {report}")

# Get recent reports
reports = get_recent_reports(limit=10)
print(f"Found {len(reports)} reports")
```

### Test AI Models
```python
# Run Python interactive shell
python

# Then run:
import numpy as np
from services.model_microplastics import analyze_microplastics
from services.model_plankton import classify_plankton

# Create test frame (random image)
test_frame = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)

# Test microplastic detection
result = analyze_microplastics(test_frame)
print("Microplastic result:", result)

# Test plankton classification
result = classify_plankton(test_frame)
print("Plankton result:", result)
```

---

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError
```bash
# Solution: Ensure venv is activated
.\venv\Scripts\activate

# Re-install requirements
pip install -r requirements.txt
```

### Issue: Permission Denied on Linux
```bash
# Solution: Make run script executable
chmod +x run.sh

# Or run with python directly
python app.py
```

### Issue: Port 5000 Already in Use
```bash
# Solution: Use a different port
python -c "from app import create_app; app = create_app(); app.run(host='0.0.0.0', port=8080)"
```

### Issue: Database Locked
```bash
# Solution: Stop all running Flask instances
# Delete the database and recreate it
rm data/reports.db
python -c "from services.database import init_database; init_database()"
```

### Issue: Camera Not Working
```bash
# Solution: Check camera permissions
# On Windows: Check Camera privacy settings
# On Linux: Check /dev/video* permissions
ls -la /dev/video*

# Test camera with OpenCV
python -c "import cv2; cap = cv2.VideoCapture(0); ret, frame = cap.read(); print('Camera working!' if ret else 'Camera failed'); cap.release()"
```

---

## ✅ Verification Checklist

- [ ] Virtual environment created and activated
- [ ] All dependencies installed successfully
- [ ] Data directories created
- [ ] Database initialized
- [ ] Flask application starts without errors
- [ ] Home page loads at http://localhost:5000
- [ ] All 8 pages are accessible
- [ ] API endpoints respond correctly
- [ ] Camera controls work (if camera available)
- [ ] Database operations succeed
- [ ] AI models return results

---

## 📊 Performance Testing

### Test Response Times
```bash
# Install Apache Bench (if not already installed)
# Windows: Download from Apache website
# Linux: sudo apt-get install apache2-utils

# Test home page
ab -n 100 -c 10 http://localhost:5000/

# Test API endpoint
ab -n 100 -c 10 http://localhost:5000/api/dashboard_stats
```

### Monitor Resource Usage
```bash
# Windows PowerShell
Get-Process python | Format-Table -Property CPU, WS, PM, ProcessName

# Linux/Mac
top -p $(pgrep -f "python app.py")
```

---

## 🔄 Reset Everything (Clean Start)

```bash
# Deactivate venv
deactivate

# Remove venv
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows CMD

# Remove database
rm data/reports.db

# Remove uploaded files
rm -rf data/captures/*
rm -rf data/uploads/*
rm -rf data/results/*

# Now start from Step 2 again
```

---

## 📝 Production Deployment (Jetson Nano)

### Transfer Files to Jetson
```bash
# Using scp (from your dev machine)
scp -r microscopedashboard/ jetson@<jetson-ip>:~/

# OR using rsync
rsync -avz --exclude 'venv' microscopedashboard/ jetson@<jetson-ip>:~/microscopedashboard/
```

### On Jetson Nano
```bash
# SSH into Jetson
ssh jetson@<jetson-ip>

# Navigate to project
cd ~/microscopedashboard

# Create venv with system packages (for OpenCV with GStreamer)
python3 -m venv --system-site-packages venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# OR run in background with nohup
nohup python app.py > output.log 2>&1 &
```

### Create Systemd Service (Auto-start)
```bash
# Create service file
sudo nano /etc/systemd/system/microbe-insights.service

# Add content:
[Unit]
Description=Microbe Insights Flask Application
After=network.target

[Service]
Type=simple
User=jetson
WorkingDirectory=/home/jetson/microscopedashboard
Environment="PATH=/home/jetson/microscopedashboard/venv/bin"
ExecStart=/home/jetson/microscopedashboard/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target

# Save and exit (Ctrl+X, Y, Enter)

# Enable and start service
sudo systemctl enable microbe-insights
sudo systemctl start microbe-insights

# Check status
sudo systemctl status microbe-insights
```

---

## 🎉 Success!

If all tests pass, your Microbe Insights application is ready to use!

Access it at: **http://localhost:5000** or **http://<jetson-ip>:5000**

Happy analyzing! 🔬✨
