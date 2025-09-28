#!/usr/bin/env python3
"""
Test script to verify the installation and functionality of the Microscope Dashboard
"""

import sys
import os
import importlib
import torch

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'flask',
        'flask_cors', 
        'torch',
        'torchvision',
        'numpy',
        'PIL',
        'cv2',
        'pandas',
        'sqlite3'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                importlib.import_module('PIL')
            elif package == 'cv2':
                importlib.import_module('cv2')
            elif package == 'sqlite3':
                importlib.import_module('sqlite3')
            else:
                importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError as e:
            print(f"  ❌ {package}: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0, failed_imports

def test_pytorch():
    """Test PyTorch functionality"""
    print("\n🔥 Testing PyTorch...")
    
    try:
        print(f"  ✅ PyTorch version: {torch.__version__}")
        print(f"  ✅ CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"  ✅ CUDA devices: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"    - Device {i}: {torch.cuda.get_device_name(i)}")
        else:
            print("  💻 Using CPU (compatible with Jetson Nano)")
        
        # Test basic tensor operations
        x = torch.randn(2, 3)
        y = torch.randn(3, 2)
        z = torch.mm(x, y)
        print(f"  ✅ Basic tensor operations working")
        
        return True
    except Exception as e:
        print(f"  ❌ PyTorch test failed: {e}")
        return False

def test_models():
    """Test if model classes can be instantiated"""
    print("\n🤖 Testing model classes...")
    
    try:
        # Test microplastic model
        from app.models.microplastic_model import MicroplasticDetector
        microplastic_model = MicroplasticDetector()
        print("  ✅ Microplastic model loaded")
        
        # Test plankton model
        from app.models.plankton_model import PlanktonAnalyzer
        plankton_model = PlanktonAnalyzer()
        print("  ✅ Plankton model loaded")
        
        return True
    except Exception as e:
        print(f"  ❌ Model loading failed: {e}")
        return False

def test_flask_app():
    """Test if Flask app can be created"""
    print("\n🌐 Testing Flask app...")
    
    try:
        from app import create_app
        app = create_app()
        print("  ✅ Flask app created successfully")
        
        # Test if routes are registered
        with app.app_context():
            routes = [str(rule) for rule in app.url_map.iter_rules()]
            expected_routes = ['/', '/predict/microplastic', '/predict/plankton', '/data']
            
            for route in expected_routes:
                if route in routes:
                    print(f"  ✅ Route {route} registered")
                else:
                    print(f"  ❌ Route {route} missing")
        
        return True
    except Exception as e:
        print(f"  ❌ Flask app test failed: {e}")
        return False

def test_directories():
    """Test if required directories exist or can be created"""
    print("\n📁 Testing directories...")
    
    required_dirs = [
        'app',
        'templates', 
        'static',
        'uploads',
        'results'
    ]
    
    all_good = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}/ exists")
        else:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"  ✅ {directory}/ created")
            except Exception as e:
                print(f"  ❌ {directory}/ creation failed: {e}")
                all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("🔬 Microscope Dashboard - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("PyTorch", test_pytorch),
        ("Model Classes", test_models),
        ("Flask App", test_flask_app),
        ("Directories", test_directories)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The installation is ready.")
        print("\n🚀 To start the application, run:")
        print("   python3 main.py")
        print("   or")
        print("   ./start.sh")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\n💡 Common solutions:")
        print("   - Install missing packages: pip install -r requirements.txt")
        print("   - Check Python version (3.7+ required)")
        print("   - Verify file permissions")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
