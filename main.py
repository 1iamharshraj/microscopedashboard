#!/usr/bin/env python3
"""
Microscope Dashboard - Main Entry Point
A Flask application for microplastic and plankton analysis
Compatible with Jetson Nano and ARM systems
"""

import os
import sys
import torch
import logging
from flask import Flask
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_system_compatibility():
    """Check system compatibility and provide information"""
    logger.info("🔬 Microscope Dashboard Starting...")
    logger.info("=" * 50)
    
    # Python version
    logger.info(f"🐍 Python version: {sys.version}")
    
    # PyTorch information
    logger.info(f"🔥 PyTorch version: {torch.__version__}")
    logger.info(f"🎯 PyTorch device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    
    # System information
    if hasattr(os, 'uname'):
        uname = os.uname()
        logger.info(f"💻 System: {uname.sysname} {uname.release} ({uname.machine})")
    
    # Memory information
    try:
        import psutil
        memory = psutil.virtual_memory()
        logger.info(f"🧠 Available memory: {memory.total // (1024**3):.1f}GB")
        logger.info(f"🧠 Free memory: {memory.available // (1024**3):.1f}GB")
    except ImportError:
        logger.warning("psutil not available - cannot display memory information")
    
    # Check for GPU
    if torch.cuda.is_available():
        logger.info(f"🎮 CUDA available: {torch.cuda.device_count()} device(s)")
        for i in range(torch.cuda.device_count()):
            logger.info(f"   Device {i}: {torch.cuda.get_device_name(i)}")
    else:
        logger.info("💻 CUDA not available - using CPU")
    
    logger.info("=" * 50)

def load_models():
    """Load ML models at startup for better performance"""
    logger.info("🤖 Loading ML models...")
    
    try:
        # Import models to trigger loading
        from app.models.microplastic_model import microplastic_model
        from app.models.plankton_model import plankton_model
        
        logger.info("✅ Microplastic detection model loaded")
        logger.info("✅ Plankton analysis model loaded")
        
        # Test model inference (dummy test)
        logger.info("🧪 Testing model inference...")
        
        # Create a dummy image for testing
        import numpy as np
        from PIL import Image
        
        dummy_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        test_image = Image.fromarray(dummy_image)
        test_path = "test_image.jpg"
        test_image.save(test_path)
        
        # Test microplastic model
        result = microplastic_model.predict(test_path)
        if result['success']:
            logger.info("✅ Microplastic model test passed")
        else:
            logger.warning(f"⚠️ Microplastic model test failed: {result.get('error', 'Unknown error')}")
        
        # Test plankton model
        result = plankton_model.predict(test_path)
        if result['success']:
            logger.info("✅ Plankton model test passed")
        else:
            logger.warning(f"⚠️ Plankton model test failed: {result.get('error', 'Unknown error')}")
        
        # Clean up test image
        if os.path.exists(test_path):
            os.remove(test_path)
            
    except Exception as e:
        logger.error(f"❌ Model loading failed: {str(e)}")
        logger.warning("⚠️ Continuing without model validation...")

def setup_directories():
    """Create necessary directories"""
    directories = ['uploads', 'results', 'static/css', 'static/js', 'static/images']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"📁 Directory created/verified: {directory}")

def main():
    """Main application entry point"""
    try:
        # System checks
        check_system_compatibility()
        
        # Setup directories
        setup_directories()
        
        # Load models
        load_models()
        
        # Create Flask app
        app = create_app()
        
        # Configuration
        host = os.environ.get('FLASK_HOST', '0.0.0.0')
        port = int(os.environ.get('FLASK_PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        logger.info(f"🚀 Starting Flask server...")
        logger.info(f"🌐 Server will be available at: http://{host}:{port}")
        logger.info(f"📊 Main dashboard: http://{host}:{port}/")
        logger.info(f"📈 Data dashboard: http://{host}:{port}/data")
        logger.info(f"🔧 Debug mode: {debug}")
        logger.info("⚠️  Press Ctrl+C to stop the server")
        logger.info("=" * 50)
        
        # Start the server
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,  # Enable threading for better performance
            use_reloader=False  # Disable reloader in production
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
