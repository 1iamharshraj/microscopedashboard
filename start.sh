#!/bin/bash

# Microscope Dashboard Startup Script
# Compatible with Jetson Nano and Linux systems

echo "🔬 Starting Microscope Dashboard..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.7 or higher.${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${BLUE}🐍 Python version: $PYTHON_VERSION${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}📦 Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${YELLOW}📦 Installing requirements...${NC}"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install requirements${NC}"
    echo -e "${YELLOW}💡 Try installing PyTorch separately:${NC}"
    echo "pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p uploads
mkdir -p results
mkdir -p static/css
mkdir -p static/js

echo -e "${GREEN}✅ Directories created${NC}"

# Check for GPU availability (informational)
echo -e "${BLUE}🔍 Checking system information...${NC}"
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}🎮 NVIDIA GPU detected:${NC}"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
else
    echo -e "${YELLOW}💻 No NVIDIA GPU detected, using CPU${NC}"
fi

# Check available memory
if command -v free &> /dev/null; then
    MEMORY_GB=$(free -g | awk 'NR==2{printf "%.1f", $2}')
    echo -e "${BLUE}🧠 Available memory: ${MEMORY_GB}GB${NC}"
fi

# Set environment variables for optimal performance
export FLASK_ENV=production
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Display startup information
echo -e "${GREEN}🚀 Starting Flask application...${NC}"
echo -e "${BLUE}📊 Dashboard will be available at: http://localhost:5000${NC}"
echo -e "${BLUE}📈 Data dashboard: http://localhost:5000/data${NC}"
echo -e "${YELLOW}⚠️  Press Ctrl+C to stop the server${NC}"
echo ""

# Start the application
python3 main.py
