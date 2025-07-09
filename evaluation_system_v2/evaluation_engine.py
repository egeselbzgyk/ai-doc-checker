import os
import json
import base64
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import tempfile
import shutil

from pdf_processor import PDFImageExtractor
from image_classifier import ImageClassifier
from qwen_client import QwenClient
from metadata_generator import MetadataGenerator

class EvaluationEngine:
    """Main evaluation engine for student submissions"""
    
    def __init__(self, metadata_db_path: str = "metadata_database.json"):
        """
        Initialize evaluation engine
        
        Args:
            metadata_db_path: Path to metadata database file
        """
        self.metadata_db_path = metadata_db_path
        self.pdf_extractor = PDFImageExtractor()
        self.classifier = ImageClassifier()
        
        # Ensure SSH tunnel for Qwen connection
        self._ensure_ssh_tunnel()
        
        # Initialize Qwen client - REQUIRED
        self.qwen_client = QwenClient()
        self._check_qwen_connection()
        
        # Load metadata database
        self.metadata_db = self._load_metadata_database()
        
        print("Evaluation Engine initialized")
    
    def _ensure_ssh_tunnel(self):
        """Ensure SSH tunnel to Qwen server is established"""
        import socket
        
        # Check if port 5000 is accessible
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                result = s.connect_ex(('localhost', 5000))
                if result == 0:
                    print("Port 5000 is accessible (SSH tunnel likely active)")
                    return
        except:
            pass
        
        # Port not accessible - SSH tunnel needed
        print("Qwen server not reachable via localhost:5000")
        print("SSH Tunnel required:")
        print("   1. Open new terminal")  
        print("   2. ssh -L 5000:localhost:5000 ebzg73@ki4.mni.thm.de")
        print("   3. Enter your password")
        print("   4. Keep terminal open")
        print("   5. Restart this server")
        
        raise Exception(
            "SSH Tunnel to Qwen Server required. "
            "Execute: ssh -L 5000:localhost:5000 ebzg73@ki4.mni.thm.de"
        )
    
    def _check_qwen_connection(self):
        """Check Qwen server connection"""
        try:
            health = self.qwen_client.health_check()
            if health.get("status") == "error" or not health.get("model_loaded"):
                raise Exception(f"Qwen server not available or model not loaded: {health}")
            print("Qwen client connected and ready")
            print(f"   Status: {health.get('status')}")
            print(f"   Model Loaded: {health.get('model_loaded')}")
            print(f"   CUDA Available: {health.get('cuda_available', 'Unknown')}")
        except Exception as e:
            raise Exception(f"Qwen server is not available or model not loaded: {str(e)}")
    
    def _load_metadata_database(self) -> Dict[str, Any]:
        """Load metadata database for reference solutions"""
        print(f"Loading metadata database from: {self.metadata_db_path}")
        
        if not os.path.exists(self.metadata_db_path):
            print("Metadata database not found, generating new one...")
            generator = MetadataGenerator(output_path=self.metadata_db_path)
            generator.save_database()
        
        with open(self.metadata_db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        # Debug: Print loaded database structure
        print(f"Metadata database loaded:")
        print(f"   Total categories: {len(db.get('categories', {}))}")
        for cat_name, cat_data in db.get('categories', {}).items():
            images_count = len(cat_data.get('images', []))
            print(f"   - {cat_name}: {images_count} images")
        
        return db
    
    def _find_best_reference_match(self, student_metadata: Dict[str, Any], category: str) -> Optional[Dict[str, Any]]:
        """
        Find best matching reference solution based on metadata similarity
        
        Args:
            student_metadata: Extracted metadata from student image
            category: Image category
            
        Returns:
            Best matching reference metadata or None
        """
        print(f"Looking for references in category: '{category}'")
        print(f"   Available categories: {list(self.metadata_db.get('categories', {}).keys())}")
        
        if category not in self.metadata_db.get("categories", {}):
            print(f"Category '{category}' not found in database")
            return None
        
        reference_images = self.metadata_db["categories"][category].get("images", [])
        print(f"   Found {len(reference_images)} reference images for '{category}'")
        
        if not reference_images:
            print(f"No reference images found for category '{category}'")
            return None
        
        # Simple matching based on structural similarity
        # This can be enhanced with more sophisticated algorithms
        best_match = None
        best_score = 0
        
        for ref_image in reference_images:
            ref_metadata = ref_image.get("metadata", {})
            
            # Calculate similarity score (simplified)
            score = self._calculate_metadata_similarity(student_metadata, ref_metadata)
            
            if score > best_score:
                best_score = score
                best_match = ref_image
        
        return best_match
    
    def _find_top_reference_matches(self, student_metadata: Dict[str, Any], category: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Find top K matching reference solutions for hybrid evaluation
        
        Args:
            student_metadata: Extracted metadata from student image
            category: Image category
            top_k: Number of top matches to return
            
        Returns:
            List of top matching references (sorted by similarity)
        """
        print(f"Finding top {top_k} references for category: '{category}'")
        print(f"   Available categories: {list(self.metadata_db.get('categories', {}).keys())}")
        
        if category not in self.metadata_db.get("categories", {}):
            print(f"Category '{category}' not found in database")
            return []
        
        reference_images = self.metadata_db["categories"][category].get("images", [])
        print(f"   Found {len(reference_images)} reference images for '{category}'")
        
        if not reference_images:
            print(f"No reference images found for category '{category}'")
            return []
        
        # Calculate similarity scores for all references
        scored_references = []
        
        for ref_image in reference_images:
            ref_metadata = ref_image.get("metadata", {})
            score = self._calculate_metadata_similarity(student_metadata, ref_metadata)
            scored_references.append((score, ref_image))
        
        # Sort by score (descending) and take top K
        scored_references.sort(key=lambda x: x[0], reverse=True)
        
        # Return top K references
        top_references = [ref for score, ref in scored_references[:top_k]]
        
        return top_references
    
    def _calculate_metadata_similarity(self, student_meta: Dict[str, Any], reference_meta: Dict[str, Any]) -> float:
        """
        Calculate similarity score between metadata objects
        
        Args:
            student_meta: Student metadata
            reference_meta: Reference metadata
            
        Returns:
            Similarity score (0-1)
        """
        if not student_meta or not reference_meta:
            return 0.0
        
        matches = 0
        total = 0
        
        # Compare nested dictionary values
        def compare_nested(dict1, dict2, path=""):
            nonlocal matches, total
            
            for key in set(dict1.keys()) | set(dict2.keys()):
                if key in dict1 and key in dict2:
                    val1, val2 = dict1[key], dict2[key]
                    
                    if isinstance(val1, dict) and isinstance(val2, dict):
                        compare_nested(val1, val2, f"{path}.{key}")
                    else:
                        total += 1
                        if val1 == val2:
                            matches += 1
        
        compare_nested(student_meta, reference_meta)
        
        return matches / total if total > 0 else 0.0
    
    def evaluate_pdf_submission(self, pdf_path: str, temp_dir: Optional[str] = None, custom_mode_only: bool = False) -> Dict[str, Any]:
        """
        Evaluate complete PDF submission
        
        Args:
            pdf_path: Path to student PDF submission
            temp_dir: Temporary directory for extracted images
            custom_mode_only: If True, only evaluate categories present in metadata_db
            
        Returns:
            Complete evaluation result
        """
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp(prefix="eval_")
        
        evaluation_result = {
            "pdf_path": pdf_path,
            "timestamp": datetime.now().isoformat(),
            "images": [],
            "valid_images": [],
            "evaluations": [],
            "overall_score": 0,
            "passed": False,
            "errors": []
        }
        
        try:
            # Step 1: Extract images from PDF
            print("Extracting images from PDF...")
            extracted_images = self.pdf_extractor.extract_images_from_pdf(pdf_path, temp_dir)
            evaluation_result["images"] = extracted_images
            
            if not extracted_images:
                evaluation_result["errors"].append("No images found in PDF")
                return evaluation_result
            
            print(f"Extracted {len(extracted_images)} images")
            
            # Step 2: Classify images with EfficientNet
            print("Classifying images...")
            valid_images = []
            
            for img_data in extracted_images:
                try:
                    predicted_class, confidence, is_valid = self.classifier.predict_from_base64(
                        img_data["image_base64"]
                    )
                    
                    img_data["predicted_class"] = predicted_class
                    img_data["confidence"] = confidence
                    img_data["is_valid"] = is_valid
                    
                    if is_valid:
                        valid_images.append(img_data)
                        print(f"  ✅ {img_data['filename']}: {predicted_class} ({confidence:.3f})")
                    else:
                        print(f"  ❌ {img_data['filename']}: Low confidence ({confidence:.3f})")
                        
                except Exception as e:
                    print(f"  ❌ Classification failed for {img_data['filename']}: {str(e)}")
                    img_data["error"] = str(e)
            
            evaluation_result["valid_images"] = valid_images
            
            if not valid_images:
                evaluation_result["errors"].append("No valid images after classification")
                return evaluation_result
            
            # Step 3: Check image evaluability
            print("Checking image evaluability...")
            evaluable_images = []
            
            for img_data in valid_images:
                try:
                    evaluability = self.qwen_client.check_image_evaluability(img_data["image_base64"])
                    
                    if evaluability.get("status") == "success" and evaluability.get("is_evaluable"):
                        evaluable_images.append(img_data)
                        print(f"✅ {img_data['filename']}: Evaluable")
                    else:
                        reason = evaluability.get("reason", "Unknown reason")
                        print(f"❌ {img_data['filename']}: Not evaluable - {reason}")
                        img_data["not_evaluable_reason"] = reason
                        
                except Exception as e:
                    print(f"❌ Evaluability check failed for {img_data['filename']}: {str(e)}")
                    img_data["evaluability_error"] = str(e)
            
            if not evaluable_images:
                evaluation_result["errors"].append("No evaluable images found")
                return evaluation_result
            
            # Step 4: Detailed evaluation
            print("Performing detailed evaluations...")
            total_score = 0
            valid_evaluations = 0
            
            for img_data in evaluable_images:
                try:
                    # Extract student metadata
                    category = img_data["predicted_class"]
                    
                    # Custom mode filtering: Skip categories not in custom reference
                    if custom_mode_only:
                        available_categories = list(self.metadata_db.get("categories", {}).keys())
                        if category not in available_categories:
                            print(f"⚠️ SKIP: Category '{category}' not in custom reference (available: {available_categories})")
                            continue
                    
                    student_metadata_result = self.qwen_client.extract_metadata(
                        img_data["image_base64"], category
                    )
                    
                    if student_metadata_result.get("status") != "success":
                        print(f"❌ Metadata extraction failed for {img_data['filename']}")
                        continue
                    
                    student_metadata = student_metadata_result.get("metadata", {})
                    
                    # HYBRID EVALUATION: Find best reference match
                    top_references = self._find_top_reference_matches(student_metadata, category, top_k=1)
                    
                    if not top_references:
                        print(f"❌ No references found for {category}")
                        continue
                    
                    print(f"Evaluating against {len(top_references)} references...")
                    
                    # Perform visual comparison with each reference
                    evaluation_scores = []
                    evaluation_details = []
                    
                    for i, ref_data in enumerate(top_references):
                        ref_path = ref_data.get("file_path")
                        ref_filename = ref_data.get("filename", f"ref_{i}")
                        
                        # Handle custom references (base64) vs database references (file path)
                        temp_ref_path = None
                        
                        if "image_base64" in ref_data:
                            # Custom reference: create temp file from base64
                            temp_ref_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                            temp_ref_path = temp_ref_file.name
                            
                            # Decode and save base64 image
                            image_data = base64.b64decode(ref_data["image_base64"])
                            temp_ref_file.write(image_data)
                            temp_ref_file.close()
                            
                            ref_path = temp_ref_path
                            print(f"     Using custom reference: {ref_filename} (temp: {ref_path})")
                        else:
                            # Database reference: use file path
                            # Fix path issues: normalize separators and relative paths
                            if ref_path:
                                # Normalize path separators (Windows \ to Unix /)
                                ref_path = ref_path.replace("\\", "/")
                                
                                # Fix relative path based on current working directory
                                current_dir = os.getcwd()
                                if ref_path.startswith("../dataset/"):
                                    if current_dir.endswith("evaluation_system_v2"):
                                        # Running from evaluation_system_v2/, keep ../dataset/
                                        pass  
                                    else:
                                        # Running from main directory, remove ../
                                        ref_path = ref_path.replace("../dataset/", "dataset/")
                            

                            
                            if not ref_path or not os.path.exists(ref_path):
                                print(f"⚠️ Reference {ref_filename} not found, skipping...")
                                continue
                            print(f"Using database reference: {ref_filename} ({ref_path})")
                        
                        try:
                            # Detect custom mode based on reference data source
                            is_custom_mode = "image_base64" in ref_data
                            mode_text = "CUSTOM MODE (50% content weight)" if is_custom_mode else "DATABASE MODE"
                            print(f"Evaluation Mode: {mode_text}")
                            
                            # Detailed evaluation using category-specific templates with visual comparison
                            detailed_eval = self.qwen_client.detailed_evaluation(
                                img_data["image_base64"], ref_path, category, is_custom_mode=is_custom_mode
                            )
                            
                            if detailed_eval.get("status") != "success":
                                print(f"❌ Detailed evaluation failed with {ref_filename}")
                                continue
                            
                            eval_result = detailed_eval.get("evaluation", {})
                            
                            # Check if evaluation should be skipped
                            if eval_result.get("skip_evaluation"):
                                skip_reason = eval_result.get("skip_reason", "Poor image quality")
                                print(f"⚠️ Skipped with {ref_filename}: {skip_reason}")
                                continue
                            
                            # Extract score from detailed evaluation format
                            gesamt_bewertung = eval_result.get("gesamt_bewertung", {})
                            ref_score = gesamt_bewertung.get("erreichte_punkte", 0)
                            evaluation_scores.append(ref_score)
                            evaluation_details.append({
                                "reference": ref_filename,
                                "score": ref_score,
                                "evaluation": eval_result
                            })
                            
                            print(f"✅ vs {ref_filename}: {ref_score}/100 points")
                            
                        except Exception as eval_error:
                            print(f"❌ Evaluation error with {ref_filename}: {str(eval_error)}")
                        
                        finally:
                            # Cleanup temp file if created
                            if temp_ref_path and os.path.exists(temp_ref_path):
                                try:
                                    os.remove(temp_ref_path)
                                except:
                                    pass
                    
                    # Calculate hybrid score (average of all reference comparisons)
                    if not evaluation_scores:
                        print(f"❌ No successful evaluations for {img_data['filename']}")
                        continue
                    
                    score = sum(evaluation_scores) / len(evaluation_scores)
                    
                    # Aggregate evaluation details
                    evaluation = {
                        "hybrid_evaluation": True,
                        "reference_count": len(evaluation_scores),
                        "individual_scores": evaluation_scores,
                        "average_score": score,
                        "detailed_comparisons": evaluation_details,
                        "combined_feedback": f"Average of {len(evaluation_scores)} reference comparisons"
                    }
                    
                    evaluation_data = {
                        "filename": img_data["filename"],
                        "category": category,
                        "confidence": img_data["confidence"],
                        "student_metadata": student_metadata,
                        "references_used": [ref["filename"] for ref in top_references[:len(evaluation_scores)]],
                        "evaluation": evaluation,
                        "score": score
                    }
                    
                    evaluation_result["evaluations"].append(evaluation_data)
                    total_score += score
                    valid_evaluations += 1
                    
                    print(f"✅ {img_data['filename']}: {score}/100 points")
                    
                except Exception as e:
                    print(f"❌ Evaluation failed for {img_data['filename']}: {str(e)}")
                    continue
            
            # Calculate overall results
            if valid_evaluations > 0:
                evaluation_result["overall_score"] = total_score / valid_evaluations
                evaluation_result["passed"] = evaluation_result["overall_score"] >= 70
                
                print(f"\nOverall Score: {evaluation_result['overall_score']:.1f}/100")
                print(f"   Result: {'PASSED' if evaluation_result['passed'] else 'FAILED'}")
            else:
                evaluation_result["errors"].append("No successful evaluations")
        
        except Exception as e:
            evaluation_result["errors"].append(f"Evaluation failed: {str(e)}")
            print(f"❌ Evaluation failed: {str(e)}")
        
        finally:
            # Cleanup temporary files
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass  # Ignore cleanup errors
        
        return evaluation_result
    
    def save_evaluation_result(self, result: Dict[str, Any], output_path: str = None) -> str:
        """
        Save evaluation result to JSON file
        
        Args:
            result: Evaluation result dictionary
            output_path: Output file path (auto-generated if None)
            
        Returns:
            Path to saved file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_name = os.path.splitext(os.path.basename(result.get("pdf_path", "unknown")))[0]
            output_path = f"evaluation_result_{pdf_name}_{timestamp}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Evaluation result saved to: {output_path}")
        return output_path
    
    def get_evaluation_summary(self, result: Dict[str, Any]) -> str:
        """
        Generate human-readable evaluation summary
        
        Args:
            result: Evaluation result
            
        Returns:
            Summary string
        """
        summary = f"""
EVALUATION SUMMARY
==================

PDF: {os.path.basename(result.get('pdf_path', 'Unknown'))}
Date: {result.get('timestamp', 'Unknown')}

RESULTS:
- Images extracted: {len(result.get('images', []))}
- Valid classifications: {len(result.get('valid_images', []))}
- Successful evaluations: {len(result.get('evaluations', []))}
- Overall Score: {result.get('overall_score', 0):.1f}/100
- Result: {'PASSED' if result.get('passed') else 'FAILED'}

DETAILED SCORES:
"""
        
        for eval_data in result.get('evaluations', []):
            summary += f"- {eval_data['filename']} ({eval_data['category']}): {eval_data['score']}/100\n"
        
        if result.get('errors'):
            summary += f"\n⚠️  ERRORS:\n"
            for error in result['errors']:
                summary += f"- {error}\n"
        
        return summary

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python evaluation_engine.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    engine = EvaluationEngine()
    
    if os.path.exists(pdf_path):
        print(f"Starting full evaluation for: {pdf_path}")
        print("=" * 50)
        result = engine.evaluate_pdf_submission(pdf_path)
        output_file = engine.save_evaluation_result(result)
        print("\n" + "=" * 50)
        print("EVALUATION COMPLETED")
        print("=" * 50)
        print(engine.get_evaluation_summary(result))
        print(f"\n Full results saved to: {output_file}")
    else:
        print(f"❌ PDF file not found: {pdf_path}") 