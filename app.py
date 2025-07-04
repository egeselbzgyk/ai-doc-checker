from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import json
import tempfile
import shutil
import zipfile
from datetime import datetime
from werkzeug.utils import secure_filename
import sys

# Evaluation system imports
sys.path.append('./evaluation_system_v2')
try:
    from evaluation_engine import EvaluationEngine
    from pdf_processor import PDFImageExtractor
    from image_classifier import ImageClassifier
    from qwen_client import QwenClient
    from metadata_generator import MetadataGenerator
except ImportError:
    print("⚠️  Evaluation system imports fehlgeschlagen")
    print("   Stelle sicher, dass evaluation_system_v2/ verfügbar ist")
    EvaluationEngine = None

app = Flask(__name__, static_folder='frontend/static', static_url_path='/static')
CORS(app)

# Konfiguration
UPLOAD_FOLDER = './frontend/uploads'
ALLOWED_EXTENSIONS = {'zip', 'pdf', 'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Upload-Ordner erstellen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Evaluation Engine initialisieren
evaluation_engine = None
if EvaluationEngine:
    try:
        evaluation_engine = EvaluationEngine()
        print("✅ Evaluation Engine initialisiert")
    except Exception as e:
        print(f"⚠️  Evaluation Engine Fehler: {e}")
else:
    print("⚠️  Evaluation Engine nicht verfügbar")

def allowed_file(filename):
    """Prüft ob Dateierweiterung erlaubt ist"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, prefix=""):
    """Speichert hochgeladene Datei und gibt Pfad zurück"""
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if prefix:
            filename = f"{prefix}_{filename}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    return None

def extract_pdf_from_zip(zip_path):
    """Extrahiert PDF aus ZIP-Datei"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.filelist:
            if file_info.filename.lower().endswith('.pdf'):
                # PDF in temporäres Verzeichnis extrahieren
                temp_dir = tempfile.mkdtemp()
                pdf_path = zip_ref.extract(file_info, temp_dir)
                return pdf_path
    return None

def process_custom_references(reference_files):
    """Verarbeitet benutzerdefinierte Referenzdateien"""
    temp_metadata = {}
    processed_files = []
    
    for file_path in reference_files:
        if not os.path.exists(file_path):
            continue
            
        filename = os.path.basename(file_path)
        file_ext = filename.split('.')[-1].lower()
        
        if file_ext == 'zip':
            # ZIP extrahieren und PDF finden
            pdf_path = extract_pdf_from_zip(file_path)
            if pdf_path:
                processed_files.append(pdf_path)
        elif file_ext == 'pdf':
            processed_files.append(file_path)
        elif file_ext in ['jpg', 'jpeg', 'png']:
            processed_files.append(file_path)
    
    # Metadata für Referenzdateien generieren
    if processed_files:
        metadata_generator = MetadataGenerator()
        
        for file_path in processed_files:
            try:
                if file_path.lower().endswith('.pdf'):
                    # PDF zu Bildern verarbeiten
                    extractor = PDFImageExtractor()
                    images = extractor.extract_images_as_base64_only(file_path)
                    
                    for img_data in images:
                        # Klassifizierung
                        classifier = ImageClassifier()
                        predicted_class, confidence, is_valid = classifier.predict_from_base64(
                            img_data["image_base64"]
                        )
                        
                        if is_valid:
                            # Metadata generieren
                            qwen_client = QwenClient()
                            metadata_result = qwen_client.extract_metadata(
                                img_data["image_base64"], predicted_class
                            )
                            metadata = metadata_result.get("metadata", {}) if metadata_result.get("status") == "success" else {}
                            
                            if predicted_class not in temp_metadata:
                                temp_metadata[predicted_class] = []
                            
                            temp_metadata[predicted_class].append({
                                "filename": img_data["filename"],
                                "metadata": metadata,
                                "confidence": confidence,
                                "image_base64": img_data["image_base64"]  # Store base64 for comparison
                            })
                
                elif file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                    # Einzelnes Bild verarbeiten
                    import base64
                    with open(file_path, 'rb') as f:
                        img_base64 = base64.b64encode(f.read()).decode()
                    
                    # Klassifizierung
                    classifier = ImageClassifier()
                    predicted_class, confidence, is_valid = classifier.predict_from_base64(img_base64)
                    
                    if is_valid:
                        # Metadata generieren
                        qwen_client = QwenClient()
                        metadata_result = qwen_client.extract_metadata(img_base64, predicted_class)
                        metadata = metadata_result.get("metadata", {}) if metadata_result.get("status") == "success" else {}
                        
                        if predicted_class not in temp_metadata:
                            temp_metadata[predicted_class] = []
                        
                        temp_metadata[predicted_class].append({
                            "filename": os.path.basename(file_path),
                            "metadata": metadata,
                            "confidence": confidence,
                            "image_base64": img_base64  # Store base64 for comparison
                        })
                        
            except Exception as e:
                print(f"Fehler bei Verarbeitung von {file_path}: {e}")
                continue
    
    return temp_metadata

# Routes

@app.route('/')
def index():
    """Serve frontend"""
    return send_from_directory('./frontend', 'index.html')

# Static files handled by Flask's built-in static file serving

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    """Hauptendpoint für Bewertung"""
    try:
        print("📥 Evaluate Request erhalten")
        
        # Use database flag check
        use_database = request.form.get('use_database', 'false').lower() == 'true'
        print(f"🗄️ Use Database: {use_database}")
        
        # Evaluation Engine Check nur für Database Mode
        if use_database and not evaluation_engine:
            return jsonify({'error': 'Standard-Bewertungssystem nicht verfügbar. Qwen Server nicht erreichbar.'}), 503
        
        # Abgabe-Datei prüfen
        if 'submission' not in request.files:
            return jsonify({'error': 'Keine Abgabe-Datei hochgeladen'}), 400
        
        submission_file = request.files['submission']
        if submission_file.filename == '':
            return jsonify({'error': 'Keine Abgabe-Datei ausgewählt'}), 400
        
        print(f"📄 Abgabe-Datei: {submission_file.filename}")
        
        # Abgabe-Datei speichern
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        submission_path = save_uploaded_file(submission_file, f"submission_{timestamp}")
        
        if not submission_path:
            return jsonify({'error': 'Fehler beim Speichern der Abgabe-Datei'}), 400
        
        print(f"💾 Abgabe gespeichert: {submission_path}")
        
        # PDF extrahieren (ZIP oder direkte PDF)
        pdf_path = None
        try:
            if submission_path.lower().endswith('.zip'):
                # ZIP extrahieren
                pdf_path = extract_pdf_from_zip(submission_path)
                if not pdf_path:
                    return jsonify({'error': 'Keine PDF-Datei in der ZIP gefunden'}), 400
                print(f"📋 PDF aus ZIP extrahiert: {pdf_path}")
            elif submission_path.lower().endswith('.pdf'):
                # Direkte PDF verwenden
                pdf_path = submission_path
                print(f"📋 Direkte PDF verwendet: {pdf_path}")
            else:
                return jsonify({'error': 'Ungültiger Dateityp. ZIP oder PDF erwartet.'}), 400
                
        except Exception as e:
            print(f"❌ Datei-Verarbeitung Fehler: {e}")
            return jsonify({'error': f'Fehler beim Verarbeiten der Datei: {str(e)}'}), 400
        
        result = None
        
        if use_database:
            print("🔄 Standard-Bewertung mit Database")
            if not evaluation_engine:
                return jsonify({'error': 'Standard-Bewertungssystem nicht verfügbar'}), 503
            
            try:
                raw_result = evaluation_engine.evaluate_pdf_submission(pdf_path)
                print("✅ Standard-Bewertung abgeschlossen")
                
                # Format für Frontend konvertieren
                if raw_result and 'evaluations' in raw_result:
                    overall_score = raw_result.get('overall_score', 0)
                    result = {
                        "overall_score": overall_score,
                        "passed": overall_score >= 60,
                        "evaluations": raw_result.get('evaluations', [])
                    }
                else:
                    # Fallback wenn unexpected format
                    print("⚠️ Unexpected evaluation result format")
                    result = {
                        "overall_score": 0,
                        "passed": False,
                        "evaluations": [{
                            "category": "Fehler",
                            "score": 0,
                            "evaluation": {
                                "gesamt_bewertung": {
                                    "erreichte_punkte": 0,
                                    "max_punkte": 100,
                                    "prozent": 0.0,
                                    "note": "Nicht bewertet"
                                },
                                "feedback": "Bewertung konnte nicht durchgeführt werden.",
                                "staerken": [],
                                "verbesserungen": ["System-Konfiguration prüfen"]
                            }
                        }]
                    }
                    
            except Exception as e:
                print(f"❌ Standard-Bewertung Fehler: {e}")
                return jsonify({'error': f'Standard-Bewertung fehlgeschlagen: {str(e)}'}), 500
            
        else:
            print("🔄 Benutzerdefinierte Bewertung")
            
            # Reference files processing
            reference_files = []
            # Frontend sends reference files as reference_0, reference_1, etc.
            for key in request.files.keys():
                if key.startswith('reference_'):
                    file = request.files[key]
                    if file.filename != '':
                        ref_path = save_uploaded_file(file, f"reference_{timestamp}")
                        if ref_path:
                            reference_files.append(ref_path)
                            print(f"📁 Reference gespeichert: {file.filename}")
            
            if not reference_files:
                return jsonify({'error': 'Keine Reference-Dateien hochgeladen'}), 400
            
            # Process custom references and get metadata
            print("🔍 Processing custom references...")
            custom_metadata = process_custom_references(reference_files)
            
            if not custom_metadata:
                return jsonify({'error': 'Keine gültigen Reference-Dateien gefunden'}), 400
            
            print(f"✅ Custom references processed: {len(custom_metadata)} categories")
            
            # Custom evaluation mit processed references
            try:
                # Verwende evaluation_engine aber mit custom metadata
                if not evaluation_engine:
                    return jsonify({'error': 'Bewertungssystem nicht verfügbar'}), 503
                
                # Temporarily override reference metadata
                original_metadata = evaluation_engine.metadata_db.copy()
                # Custom metadata format conversion
                custom_db = {"categories": {}}
                for category, items in custom_metadata.items():
                    custom_db["categories"][category] = {"images": items}
                
                evaluation_engine.metadata_db = custom_db
                
                # Use custom_mode_only=True to skip categories not in custom reference
                raw_result = evaluation_engine.evaluate_pdf_submission(pdf_path, custom_mode_only=True)
                
                # Restore original metadata
                evaluation_engine.metadata_db = original_metadata
                
                print("✅ Custom evaluation abgeschlossen")
                
                # Format result
                if raw_result and 'evaluations' in raw_result:
                    overall_score = raw_result.get('overall_score', 0)
                    result = {
                        "overall_score": overall_score,
                        "passed": overall_score >= 60,
                        "evaluations": raw_result.get('evaluations', [])
                    }
                else:
                    result = {
                        "overall_score": 0,
                        "passed": False,
                        "evaluations": []
                    }
                
                # Cleanup reference files
                for ref_file in reference_files:
                    try:
                        if os.path.exists(ref_file):
                            os.remove(ref_file)
                    except:
                        pass
                        
            except Exception as e:
                print(f"❌ Custom evaluation Fehler: {e}")
                return jsonify({'error': f'Custom evaluation fehlgeschlagen: {str(e)}'}), 500
        
        # Cleanup temporäre Dateien
        try:
            if os.path.exists(submission_path):
                os.remove(submission_path)
            if pdf_path and os.path.exists(pdf_path):
                # PDF temp dir cleanup
                temp_dir = os.path.dirname(pdf_path)
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            print("🧹 Cleanup abgeschlossen")
        except Exception as e:
            print(f"⚠️ Cleanup Fehler: {e}")
        
        # Save evaluation result to file
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"results/evaluation_result_{timestamp}.json"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Evaluation result saved to: {output_file}")
        except Exception as e:
            print(f"⚠️ Failed to save result: {e}")
        
        # Ergebnis zurückgeben
        print("📤 Ergebnis wird zurückgegeben")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Bewertungsfehler: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Bewertungsfehler: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    import socket
    
    # SSH tunnel status
    tunnel_active = False
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            result = s.connect_ex(('localhost', 5000))
            tunnel_active = (result == 0)
    except:
        tunnel_active = False
    
    # Qwen server status
    qwen_status = "unavailable"
    if tunnel_active:
        try:
            import requests
            response = requests.get("http://localhost:5000/health", timeout=3)
            if response.status_code == 200:
                qwen_status = "active"
            else:
                qwen_status = f"error_{response.status_code}"
        except:
            qwen_status = "connection_failed"
    
    # Overall status
    status = {
        'status': 'OK' if (tunnel_active and qwen_status == "active") else 'SSH_TUNNEL_REQUIRED',
        'ssh_tunnel': 'active' if tunnel_active else 'inactive',
        'qwen_server': qwen_status,
        'evaluation_engine': 'ready' if evaluation_engine else 'not_initialized',
        'frontend': 'running',
        'timestamp': datetime.now().isoformat()
    }
    
    if not tunnel_active or qwen_status != "active":
        status['instructions'] = [
            "1. Öffne neues Terminal",
            "2. ssh -L 5000:localhost:5000 ebzg73@ki4.mni.thm.de",
            "3. Gib dein Passwort ein",
            "4. Lasse Terminal offen",
            "5. Refresh diese Seite"
        ]
    
    status_code = 200 if (tunnel_active and qwen_status == "active") else 503
    
    return jsonify(status), status_code

@app.route('/api/metadata/generate', methods=['POST'])
def generate_metadata():
    """Metadata-Database neu generieren"""
    try:
        generator = MetadataGenerator()
        generator.generate_metadata_database()
        generator.save_database()
        
        return jsonify({'status': 'Metadata-Database erfolgreich generiert'})
    except Exception as e:
        return jsonify({'error': f'Fehler bei Metadata-Generierung: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Datei zu groß (max. 10MB)'}), 413

if __name__ == '__main__':
    print("🚀 AI Doc Checker Server wird gestartet...")
    print(f"📁 Upload-Ordner: {UPLOAD_FOLDER}")
    print(f"🔧 Max. Dateigröße: {MAX_CONTENT_LENGTH / (1024*1024):.1f}MB")
    print("📄 Frontend verfügbar unter: http://localhost:5001")
    print("🔍 API Health Check: http://localhost:5001/api/health")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 