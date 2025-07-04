#!/usr/bin/env python3
"""
AI Doc Checker Frontend Starter

Startet das Frontend für das AI Doc Checker System mit automatischen Prüfungen.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Prüft Python Version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ erforderlich!")
        print(f"   Aktuelle Version: {sys.version}")
        return False
    print(f"✅ Python Version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Prüft erforderliche Python-Pakete"""
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
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} fehlt")
            missing_packages.append(package)
    
    return missing_packages

def check_evaluation_system():
    """Prüft ob evaluation_system_v2 verfügbar ist"""
    eval_path = Path('./evaluation_system_v2')
    if not eval_path.exists():
        print("❌ evaluation_system_v2 Ordner nicht gefunden!")
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
            print(f"❌ {file} nicht gefunden in evaluation_system_v2/")
            return False
        print(f"✅ {file}")
    
    return True

def check_model_file():
    """Prüft ob EfficientNet Modell verfügbar ist"""
    model_path = Path('./model/efficientnet_b0_best.pth')
    if not model_path.exists():
        print("⚠️  EfficientNet Modell nicht gefunden!")
        print("   Pfad: ./model/efficientnet_b0_best.pth")
        print("   Bewertung ohne Klassifizierung möglich")
        return False
    print("✅ EfficientNet Modell gefunden")
    return True

def check_frontend_files():
    """Prüft Frontend-Dateien"""
    frontend_files = [
        'frontend/index.html',
        'frontend/static/style.css',
        'frontend/static/script.js',
        'app.py'
    ]
    
    for file in frontend_files:
        if not Path(file).exists():
            print(f"❌ {file} nicht gefunden!")
            return False
        print(f"✅ {file}")
    
    return True

def install_dependencies(missing_packages):
    """Installiert fehlende Abhängigkeiten"""
    if not missing_packages:
        return True
    
    print(f"\n📦 Installiere fehlende Pakete: {', '.join(missing_packages)}")
    
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
        print("✅ Pakete erfolgreich installiert")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation fehlgeschlagen: {e}")
        return False

def start_server():
    """Startet den Flask Server"""
    print("\n🚀 Starte AI Doc Checker Frontend...")
    print("📄 Frontend: http://localhost:5001")
    print("🔍 Health Check: http://localhost:5001/api/health")
    print("⏹️  Beenden mit Ctrl+C")
    print("-" * 50)
    
    try:
        import app
        app.app.run(debug=False, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 Server beendet")
    except Exception as e:
        print(f"\n❌ Server-Fehler: {e}")

def main():
    """Hauptfunktion"""
    print("AI Doc Checker - Frontend Starter")
    print("=" * 40)
    
    # System-Prüfungen
    print("\n🔍 System-Prüfungen:")
    
    if not check_python_version():
        sys.exit(1)
    
    print("\n📦 Abhängigkeiten:")
    missing = check_dependencies()
    
    if missing:
        answer = input(f"\n❓ {len(missing)} Pakete fehlen. Installieren? (j/n): ")
        if answer.lower() in ['j', 'ja', 'y', 'yes']:
            if not install_dependencies(missing):
                sys.exit(1)
        else:
            print("⚠️  Ohne Abhängigkeiten kann das System nicht funktionieren")
            sys.exit(1)
    
    print("\n🔧 System-Komponenten:")
    if not check_evaluation_system():
        sys.exit(1)
    
    check_model_file()  # Warning, aber nicht kritisch
    
    print("\n📁 Frontend-Dateien:")
    if not check_frontend_files():
        sys.exit(1)
    
    print("\n✅ Alle Prüfungen erfolgreich!")
    
    # Server starten
    start_server()

if __name__ == '__main__':
    main() 