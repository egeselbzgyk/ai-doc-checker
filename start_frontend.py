#!/usr/bin/env python3
"""
AI Doc Checker Frontend Starter

Starts the frontend for the AI Doc Checker System with automatic checks.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("Python 3.8+ required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"Python Version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check required Python packages"""
    required_packages = [
        'flask',
        'flask_cors',
        'PIL',
        'fitz',  # PyMuPDF
        'requests',
        'numpy',
        'torch',
        'torchvision'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'fitz':
                import fitz
            elif package == 'flask_cors':
                import flask_cors
            else:
                importlib.import_module(package)
            print(f"{package}")
        except ImportError:
            print(f"{package} missing")
            missing_packages.append(package)
    
    return missing_packages

def check_evaluation_system():
    """Check if evaluation_system_v2 is available"""
    eval_path = Path('./evaluation_system_v2')
    if not eval_path.exists():
        print("evaluation_system_v2 folder not found!")
        return False
    
    required_files = [
        'evaluation_engine.py',
        'pdf_processor.py', 
        'image_classifier.py',
        'qwen_client.py',
        'metadata_generator.py'
    ]
    
    for file in required_files:
        if not (eval_path / file).exists():
            print(f"{file} not found in evaluation_system_v2/")
            return False
        print(f"{file}")
    
    return True

def check_model_file():
    """Check if EfficientNet model is available"""
    model_path = Path('./model/efficientnet_b0_best.pth')
    if not model_path.exists():
        print("EfficientNet model not found!")
        print("   Path: ./model/efficientnet_b0_best.pth")
        print("   Evaluation without classification possible")
        return False
    print("EfficientNet model found")
    return True

def check_frontend_files():
    """Check frontend files"""
    frontend_files = [
        'frontend/index.html',
        'frontend/static/style.css',
        'frontend/static/script.js',
        'app.py'
    ]
    
    for file in frontend_files:
        if not Path(file).exists():
            print(f"{file} not found!")
            return False
        print(f"{file}")
    
    return True

def install_dependencies(missing_packages):
    """Install missing dependencies"""
    if not missing_packages:
        return True
    
    print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
    
    try:
        # Map package names for pip
        pip_packages = []
        for pkg in missing_packages:
            if pkg == 'PIL':
                pip_packages.append('Pillow')
            elif pkg == 'fitz':
                pip_packages.append('PyMuPDF')
            elif pkg == 'flask_cors':
                pip_packages.append('Flask-CORS')
            else:
                pip_packages.append(pkg)
        
        cmd = [sys.executable, '-m', 'pip', 'install'] + pip_packages
        subprocess.run(cmd, check=True)
        print("Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Installation failed: {e}")
        return False

def start_server():
    """Start the Flask Server"""
    print("\nStarting AI Doc Checker Frontend...")
    print("Frontend: http://localhost:5001")
    print("Health Check: http://localhost:5001/api/health")
    print("Stop with Ctrl+C")
    print("-" * 50)
    
    try:
        import app
        app.app.run(debug=False, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"\nServer error: {e}")

def main():
    """Main function"""
    print("AI Doc Checker - Frontend Starter")
    print("=" * 40)
    
    # System checks
    print("\nSystem checks:")
    
    if not check_python_version():
        sys.exit(1)
    
    print("\nDependencies:")
    missing = check_dependencies()
    
    if missing:
        answer = input(f"\n{len(missing)} packages missing. Install? (y/n): ")
        if answer.lower() in ['j', 'ja', 'y', 'yes']:
            if not install_dependencies(missing):
                sys.exit(1)
        else:
            print("Without dependencies the system cannot function")
            sys.exit(1)
    
    print("\nSystem components:")
    if not check_evaluation_system():
        sys.exit(1)
    
    check_model_file()  # Warning, but not critical
    
    print("\nFrontend files:")
    if not check_frontend_files():
        sys.exit(1)
    
    print("\nAll checks successful!")
    
    # Start server
    start_server()

if __name__ == '__main__':
    main() 