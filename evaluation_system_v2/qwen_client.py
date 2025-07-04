import requests
import json
import base64
from typing import Dict, Any, Optional
import time
from PIL import Image
import io

class QwenClient:
    """Client for communicating with Qwen2.5-VL API server"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize Qwen client
        
        Args:
            base_url: Base URL of the Qwen API server
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if Qwen server is healthy and ready
        
        Returns:
            Health status dictionary
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "model_loaded": False
            }
    
    def analyze_image(self, image_base64: str, prompt: str, max_tokens: int = 2048) -> Dict[str, Any]:
        """
        Analyze image with Qwen2.5-VL
        
        Args:
            image_base64: Base64 encoded image data
            prompt: German prompt for analysis
            max_tokens: Maximum tokens for response
            
        Returns:
            Analysis result dictionary
        """
        payload = {
            "image_base64": image_base64,
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/analyze", 
                json=payload, 
                timeout=60  # Longer timeout for image analysis
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": "Request timeout - server may be busy"
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": f"Request failed: {str(e)}"
            }
    
    def text_only_query(self, prompt: str, max_tokens: int = 1024) -> Dict[str, Any]:
        """
        Send text-only query to Qwen
        
        Args:
            prompt: Text prompt
            max_tokens: Maximum tokens for response
            
        Returns:
            Response dictionary
        """
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/text_only", 
                json=payload, 
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def check_image_evaluability(self, image_base64: str) -> Dict[str, Any]:
        """
        Check if image is suitable for evaluation
        
        Args:
            image_base64: Base64 encoded image
            
        Returns:
            Evaluability check result
        """
        from metadata_templates import evaluability_check
        
        result = self.analyze_image(image_base64, evaluability_check, max_tokens=200)
        
        if result.get("status") == "success":
            try:
                # Parse JSON response
                response_text = result.get("response", "").strip()
                # Remove any markdown code blocks if present
                if response_text.startswith("```json"):
                    response_text = response_text[7:]  # Remove ```json
                elif response_text.startswith("```"):
                    response_text = response_text[3:]  # Remove ```
                    
                # Remove leading newline if present
                if response_text.startswith('\n'):
                    response_text = response_text[1:]
                    
                # Remove trailing ```
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                    
                # Remove trailing newline if present  
                if response_text.endswith('\n'):
                    response_text = response_text[:-1]
                    
                response_text = response_text.strip()
                
                evaluation_result = json.loads(response_text)
                return {
                    "status": "success",
                    "is_evaluable": evaluation_result.get("is_evaluable", False),
                    "reason": evaluation_result.get("reason", "Unknown")
                }
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "error": f"Invalid JSON response: {str(e)}",
                    "raw_response": result.get("response", "")
                }
        else:
            return result
    
    def extract_metadata(self, image_base64: str, category: str) -> Dict[str, Any]:
        """
        Extract metadata from image for given category
        
        Args:
            image_base64: Base64 encoded image
            category: Category name (Excel-Tabelle, Data-Flow, etc.)
            
        Returns:
            Metadata extraction result
        """
        from metadata_templates import metadata_templates
        
        if category not in metadata_templates:
            return {
                "status": "error",
                "error": f"Unknown category: {category}"
            }
        
        prompt = metadata_templates[category]
        result = self.analyze_image(image_base64, prompt, max_tokens=1024)
        
        if result.get("status") == "success":
            try:
                response_text = result.get("response", "").strip()
                # Clean response
                if response_text.startswith("```json"):
                    response_text = response_text[7:]  # Remove ```json
                elif response_text.startswith("```"):
                    response_text = response_text[3:]  # Remove ```
                    
                # Remove leading newline if present
                if response_text.startswith('\n'):
                    response_text = response_text[1:]
                    
                # Remove trailing ```
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                    
                # Remove trailing newline if present  
                if response_text.endswith('\n'):
                    response_text = response_text[:-1]
                    
                response_text = response_text.strip()
                
                metadata = json.loads(response_text)
                return {
                    "status": "success",
                    "metadata": metadata,
                    "category": category
                }
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "error": f"Invalid JSON response: {str(e)}",
                    "raw_response": result.get("response", "")
                }
        else:
            return result
    
    def visual_comparison_evaluation(self, student_image_base64: str, reference_image_path: str, category: str) -> Dict[str, Any]:
        """
        Perform detailed evaluation by comparing two images visually
        
        Args:
            student_image_base64: Student image in base64
            reference_image_path: Path to reference image
            category: Image category
            
        Returns:
            Visual comparison evaluation result
        """
        try:
            # Load and process images
            import base64
            import io
            from PIL import Image
            
            # Decode student image
            student_image_data = base64.b64decode(student_image_base64)
            student_img = Image.open(io.BytesIO(student_image_data))
            
            # Load reference image
            reference_img = Image.open(reference_image_path)
            
            # Resize images to same height for side-by-side comparison
            max_height = 800  # Reasonable height for Qwen
            student_ratio = max_height / student_img.height
            reference_ratio = max_height / reference_img.height
            
            student_width = int(student_img.width * student_ratio)
            reference_width = int(reference_img.width * reference_ratio)
            
            student_resized = student_img.resize((student_width, max_height), Image.Resampling.LANCZOS)
            reference_resized = reference_img.resize((reference_width, max_height), Image.Resampling.LANCZOS)
            
            # Create combined image (side by side)
            combined_width = student_width + reference_width + 20  # 20px separator
            combined_img = Image.new('RGB', (combined_width, max_height), color='white')
            
            # Paste images side by side
            combined_img.paste(student_resized, (0, 0))
            combined_img.paste(reference_resized, (student_width + 20, 0))
            
            # Convert combined image to base64
            buffer = io.BytesIO()
            combined_img.save(buffer, format='JPEG', quality=85)
            combined_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Create comparison prompt
            prompt = f"""
Du siehst zwei SAP BW Bilder nebeneinander:

LINKS: STUDENTEN-BILD (zu bewerten)
RECHTS: REFERENZ-MUSTERLÖSUNG (Vergleichsstandard)

Kategorie: {category}

Vergleiche die beiden Bilder DETAILLIERT und bewerte das linke (Studenten-)Bild basierend auf dem rechten (Referenz-)Bild.

Bewertungskriterien für {category}:
- Strukturelle Ähnlichkeit (25 Punkte)
- Vollständigkeit des Inhalts (25 Punkte)
- Qualität der Umsetzung (25 Punkte)
- Fachliche Korrektheit (25 Punkte)

BEWERTUNGSSKALA:
90-100: Exzellent - entspricht vollständig der Referenz
75-89: Gut - kleinere Abweichungen
60-74: Befriedigend - sichtbare Unterschiede aber akzeptabel  
40-59: Mangelhaft - deutliche Probleme
0-39: Ungenügend - schwerwiegende Mängel

Führe eine ECHTE visuelle Analyse durch und vergib Punkte basierend auf dem tatsächlichen Vergleich.

Antworte NUR mit JSON (ohne Markdown-Blöcke):
{{
  "skip_evaluation": false,
  "punkte_total": [DEINE_ECHTE_BEWERTUNG_0_BIS_100],
  "feedback": "Detaillierte Bewertung basierend auf dem visuellen Vergleich",
  "staerken": ["Spezifische positive Aspekte die im Bild erkennbar sind"],
  "verbesserungen": ["Konkrete Verbesserungsvorschläge basierend auf Referenz-Unterschieden"],
  "referenz_vergleich": "Detaillierter Vergleich zwischen Student und Referenz"
}}

KRITISCH: 
- Vergib ECHTE Punkte basierend auf dem visuellen Vergleich!
- Verwende NIEMALS Beispielwerte!
- Analysiere beide Bilder gründlich!
- Nur JSON - keine Markdown-Formatierung!
"""
            
            # Send combined image to Qwen using standard analyze_image method
            result = self.analyze_image(combined_base64, prompt, max_tokens=1024)
            
            if result.get("status") == "success":
                try:
                    response_text = result.get("response", "").strip()
                    
                    # Clean response
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    elif response_text.startswith("```"):
                        response_text = response_text[3:]
                    
                    if response_text.startswith('\n'):
                        response_text = response_text[1:]
                    
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]
                    
                    if response_text.endswith('\n'):
                        response_text = response_text[:-1]
                    
                    response_text = response_text.strip()
                    
                    evaluation = json.loads(response_text)
                    return {
                        "status": "success",
                        "evaluation": evaluation,
                        "category": category
                    }
                except json.JSONDecodeError as e:
                    return {
                        "status": "error",
                        "error": f"Invalid JSON response: {str(e)}",
                        "raw_response": result.get("response", "")
                    }
            else:
                return result
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"Visual comparison failed: {str(e)}"
            }

    def detailed_evaluation(self, student_image_base64: str, reference_image_path: str, category: str, is_custom_mode: bool = False) -> Dict[str, Any]:
        """
        Perform detailed evaluation comparing student image with reference image visually
        using category-specific templates
        
        Args:
            student_image_base64: Student image in base64
            reference_image_path: Path to reference image
            category: Image category
            is_custom_mode: Whether to use custom mode templates (50% content weight)
            
        Returns:
            Detailed evaluation result with category-specific criteria
        """
        from evaluation_templates import evaluation_templates, custom_evaluation_templates
        
        # Select appropriate template based on mode
        if is_custom_mode:
            templates = custom_evaluation_templates
            mode_info = "CUSTOM MODE"
        else:
            templates = evaluation_templates
            mode_info = "DATABASE MODE"
        
        if category not in templates:
            return {
                "status": "error",
                "error": f"Unknown category: {category} in {mode_info}"
            }
        
        try:
            # Create side-by-side comparison image (same as visual_comparison_evaluation)
            import base64
            import io
            from PIL import Image
            
            # Decode student image
            student_image_data = base64.b64decode(student_image_base64)
            student_img = Image.open(io.BytesIO(student_image_data))
            
            # Load reference image
            reference_img = Image.open(reference_image_path)
            
            # Resize images to same height for side-by-side comparison
            max_height = 800  # Reasonable height for Qwen
            student_ratio = max_height / student_img.height
            reference_ratio = max_height / reference_img.height
            
            student_width = int(student_img.width * student_ratio)
            reference_width = int(reference_img.width * reference_ratio)
            
            student_resized = student_img.resize((student_width, max_height), Image.Resampling.LANCZOS)
            reference_resized = reference_img.resize((reference_width, max_height), Image.Resampling.LANCZOS)
            
            # Create combined image (side by side)
            combined_width = student_width + reference_width + 20  # 20px separator
            combined_img = Image.new('RGB', (combined_width, max_height), color='white')
            
            # Paste images side by side
            combined_img.paste(student_resized, (0, 0))
            combined_img.paste(reference_resized, (student_width + 20, 0))
            
            # Convert combined image to base64
            buffer = io.BytesIO()
            combined_img.save(buffer, format='JPEG', quality=85)
            combined_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Create enhanced prompt with visual comparison + category-specific template
            enhanced_prompt = f"""
Du siehst zwei SAP BW Bilder nebeneinander:

LINKS: STUDENTEN-BILD (zu bewerten)
RECHTS: REFERENZ-MUSTERLÖSUNG (Vergleichsstandard)

Kategorie: {category} ({mode_info})

Führe eine DETAILLIERTE VISUELLE BEWERTUNG durch, basierend auf dem Vergleich zwischen dem linken (Studenten-) und rechten (Referenz-) Bild.

{templates[category].replace('Referenz-Analyse: {reference_analysis}', 'Verwende das rechte Bild als Referenz für den Vergleich.')}
"""
            
            result = self.analyze_image(combined_base64, enhanced_prompt, max_tokens=2048)
            
        except Exception as format_error:
            return {
                "status": "error", 
                "error": f"Template format error: {str(format_error)}",
                "category": category
            }
        
        if result.get("status") == "success":
            try:
                response_text = result.get("response", "").strip()
                # Clean response
                if response_text.startswith("```json"):
                    response_text = response_text[7:]  # Remove ```json
                elif response_text.startswith("```"):
                    response_text = response_text[3:]  # Remove ```
                    
                # Remove leading newline if present
                if response_text.startswith('\n'):
                    response_text = response_text[1:]
                    
                # Remove trailing ```
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                    
                # Remove trailing newline if present  
                if response_text.endswith('\n'):
                    response_text = response_text[:-1]
                    
                response_text = response_text.strip()
                
                evaluation = json.loads(response_text)
                return {
                    "status": "success",
                    "evaluation": evaluation,
                    "category": category
                }
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "error": f"Invalid JSON response: {str(e)}",
                    "raw_response": result.get("response", "")
                }
        else:
            return result
    
    def batch_process_with_retry(self, requests_list: list, max_retries: int = 3, delay: float = 1.0) -> list:
        """
        Process multiple requests with retry logic
        
        Args:
            requests_list: List of request functions to execute
            max_retries: Maximum retry attempts
            delay: Delay between retries
            
        Returns:
            List of results
        """
        results = []
        
        for i, request_func in enumerate(requests_list):
            for attempt in range(max_retries):
                try:
                    result = request_func()
                    results.append(result)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        results.append({
                            "status": "error",
                            "error": f"Failed after {max_retries} attempts: {str(e)}"
                        })
                    else:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
        
        return results

# Example usage
if __name__ == "__main__":
    client = QwenClient()
    
    # Test connection
    health = client.health_check()
    print(f"Server health: {health}")
    
    if health.get("model_loaded"):
        print("✅ Qwen server is ready for evaluation")
    else:
        print("❌ Qwen server is not ready") 