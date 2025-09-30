#!/bin/bash

# Microbe Insights Startup Script
# This script starts the Flask application

echo "======================================"
echo "  Microbe Insights - Starting..."
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Checking dependencies..."
pip install -q -r requirements.txt

# Create data directories
echo "📁 Setting up data directories..."
mkdir -p data/captures data/uploads data/results

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from services.database import init_database; init_database()" 2>/dev/null || echo "Database already initialized"

echo ""
echo "✅ Setup complete!"
echo ""
echo "======================================"
echo "  Starting Flask Server..."
echo "======================================"
echo ""
echo "🌐 Server will be available at:"
echo "   - Local:   http://localhost:5000"
echo "   - Network: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Flask application
python3 app.py
