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
    print("Evaluation system imports failed")
    print("   Make sure evaluation_system_v2/ is available")
    EvaluationEngine = None

app = Flask(__name__, static_folder='frontend/static', static_url_path='/static')
CORS(app)

# Configuration
UPLOAD_FOLDER = './frontend/uploads'
ALLOWED_EXTENSIONS = {'zip', 'pdf', 'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Evaluation Engine
evaluation_engine = None
if EvaluationEngine:
    try:
        evaluation_engine = EvaluationEngine()
        print("Evaluation Engine initialized")
    except Exception as e:
        print(f"Evaluation Engine Error: {e}")
else:
    print("Evaluation Engine not available")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, prefix=""):
    """Save uploaded file and return path"""
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if prefix:
            filename = f"{prefix}_{filename}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    return None

def extract_pdf_from_zip(zip_path):
    """Extract PDF from ZIP file"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.filelist:
            if file_info.filename.lower().endswith('.pdf'):
                # Extract PDF to temporary directory
                temp_dir = tempfile.mkdtemp()
                pdf_path = zip_ref.extract(file_info, temp_dir)
                return pdf_path
    return None

def process_custom_references(reference_files):
    """Process custom reference files"""
    temp_metadata = {}
    processed_files = []
    
    for file_path in reference_files:
        if not os.path.exists(file_path):
            continue
            
        filename = os.path.basename(file_path)
        file_ext = filename.split('.')[-1].lower()
        
        if file_ext == 'zip':
            # Extract ZIP and find PDF
            pdf_path = extract_pdf_from_zip(file_path)
            if pdf_path:
                processed_files.append(pdf_path)
        elif file_ext == 'pdf':
            processed_files.append(file_path)
        elif file_ext in ['jpg', 'jpeg', 'png']:
            processed_files.append(file_path)
    
    # Generate metadata for reference files
    if processed_files:
        metadata_generator = MetadataGenerator()
        
        for file_path in processed_files:
            try:
                if file_path.lower().endswith('.pdf'):
                    # Process PDF to images
                    extractor = PDFImageExtractor()
                    images = extractor.extract_images_as_base64_only(file_path)
                    
                    for img_data in images:
                        # Classification
                        classifier = ImageClassifier()
                        predicted_class, confidence, is_valid = classifier.predict_from_base64(
                            img_data["image_base64"]
                        )
                        
                        if is_valid:
                            # Generate metadata
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
                    # Process single image
                    import base64
                    with open(file_path, 'rb') as f:
                        img_base64 = base64.b64encode(f.read()).decode()
                    
                    # Classification
                    classifier = ImageClassifier()
                    predicted_class, confidence, is_valid = classifier.predict_from_base64(img_base64)
                    
                    if is_valid:
                        # Generate metadata
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
                print(f"Error processing {file_path}: {e}")
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
    """Main endpoint for evaluation"""
    try:
        print("Evaluate Request received")
        
        # Use database flag check
        use_database = request.form.get('use_database', 'false').lower() == 'true'
        print(f"Use Database: {use_database}")
        
        # Evaluation Engine Check only for Database Mode
        if use_database and not evaluation_engine:
            return jsonify({'error': 'Standard evaluation system not available. Qwen Server not reachable.'}), 503
        
        # Check submission file
        if 'submission' not in request.files:
            return jsonify({'error': 'No submission file uploaded'}), 400
        
        submission_file = request.files['submission']
        if submission_file.filename == '':
            return jsonify({'error': 'No submission file selected'}), 400
        
        print(f"Submission file: {submission_file.filename}")
        
        # Save submission file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        submission_path = save_uploaded_file(submission_file, f"submission_{timestamp}")
        
        if not submission_path:
            return jsonify({'error': 'Error saving submission file'}), 400
        
        print(f"Submission saved: {submission_path}")
        
        # Extract PDF (ZIP or direct PDF)
        pdf_path = None
        try:
            if submission_path.lower().endswith('.zip'):
                # Extract ZIP
                pdf_path = extract_pdf_from_zip(submission_path)
                if not pdf_path:
                    return jsonify({'error': 'No PDF file found in ZIP'}), 400
                print(f"PDF extracted from ZIP: {pdf_path}")
            elif submission_path.lower().endswith('.pdf'):
                # Use direct PDF
                pdf_path = submission_path
                print(f"Direct PDF used: {pdf_path}")
            else:
                return jsonify({'error': 'Invalid file type. ZIP or PDF expected.'}), 400
                
        except Exception as e:
            print(f"File processing error: {e}")
            return jsonify({'error': f'Error processing file: {str(e)}'}), 400
        
        result = None
        
        if use_database:
            print("Standard evaluation with Database")
            if not evaluation_engine:
                return jsonify({'error': 'Standard evaluation system not available'}), 503
            
            try:
                raw_result = evaluation_engine.evaluate_pdf_submission(pdf_path)
                print("Standard evaluation completed")
                
                # Convert for frontend
                if raw_result and 'evaluations' in raw_result:
                    overall_score = raw_result.get('overall_score', 0)
                    result = {
                        "overall_score": overall_score,
                        "passed": overall_score >= 60,
                        "evaluations": raw_result.get('evaluations', [])
                    }
                else:
                    # Fallback if unexpected format
                    print("Unexpected evaluation result format")
                    result = {
                        "overall_score": 0,
                        "passed": False,
                        "evaluations": [{
                            "category": "Error",
                            "score": 0,
                            "evaluation": {
                                "total_evaluation": {
                                    "achieved_points": 0,
                                    "max_points": 100,
                                    "percentage": 0.0,
                                    "note": "Not evaluated"
                                },
                                "feedback": "Evaluation could not be performed.",
                                "strengths": [],
                                "improvements": ["Check system configuration"]
                            }
                        }]
                    }
                    
            except Exception as e:
                print(f"Standard evaluation error: {e}")
                return jsonify({'error': f'Standard evaluation failed: {str(e)}'}), 500
            
        else:
            print("Custom evaluation")
            
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
                            print(f"Reference saved: {file.filename}")
            
            if not reference_files:
                return jsonify({'error': 'No reference files uploaded'}), 400
            
            # Process custom references and get metadata
            print("Processing custom references...")
            custom_metadata = process_custom_references(reference_files)
            
            if not custom_metadata:
                return jsonify({'error': 'No valid reference files found'}), 400
            
            print(f"Custom references processed: {len(custom_metadata)} categories")
            
            # Custom evaluation with processed references
            try:
                # Use evaluation_engine but with custom metadata
                if not evaluation_engine:
                    return jsonify({'error': 'Evaluation system not available'}), 503
                
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
                
                print("Custom evaluation completed")
                
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
                print(f"Custom evaluation error: {e}")
                return jsonify({'error': f'Custom evaluation failed: {str(e)}'}), 500
        
        # Cleanup temporary files
        try:
            if os.path.exists(submission_path):
                os.remove(submission_path)
            if pdf_path and os.path.exists(pdf_path):
                # PDF temp dir cleanup
                temp_dir = os.path.dirname(pdf_path)
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            print("Cleanup completed")
        except Exception as e:
            print(f"Cleanup error: {e}")
        
        # Save evaluation result to file
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"results/evaluation_result_{timestamp}.json"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Evaluation result saved to: {output_file}")
        except Exception as e:
            print(f"Failed to save result: {e}")
        
        # Return result
        print("Result is being returned")
        return jsonify(result)
        
    except Exception as e:
        print(f"Evaluation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Evaluation error: {str(e)}'}), 500

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
            "1. Open new Terminal",
            "2. ssh -L 5000:localhost:5000 ebzg73@ki4.mni.thm.de",
            "3. Enter your password",
            "4. Keep Terminal open",
            "5. Refresh this page"
        ]
    
    status_code = 200 if (tunnel_active and qwen_status == "active") else 503
    
    return jsonify(status), status_code

@app.route('/api/metadata/generate', methods=['POST'])
def generate_metadata():
    """Regenerate metadata database"""
    try:
        generator = MetadataGenerator()
        generator.generate_metadata_database()
        generator.save_database()
        
        return jsonify({'status': 'Metadata-Database successfully generated'})
    except Exception as e:
        return jsonify({'error': f'Error generating metadata: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large (max. 10MB)'}), 413

if __name__ == '__main__':
    print("AI Doc Checker Server is starting...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Max file size: {MAX_CONTENT_LENGTH / (1024*1024):.1f}MB")
    print("Frontend available at: http://localhost:5001")
    print("API Health Check: http://localhost:5001/api/health")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 