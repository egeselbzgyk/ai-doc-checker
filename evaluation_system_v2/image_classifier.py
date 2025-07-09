import torch
from torchvision import models, transforms
from PIL import Image
import torch.nn.functional as F
import os
import base64
import io
from typing import Tuple, Optional

class ImageClassifier:
    """EfficientNet-based image classifier for SAP BW categories"""
    
    def __init__(self, model_path: str = "./model/efficientnet_b0_best.pth", confidence_threshold: float = 0.6):
        """
        Initialize classifier
        
        Args:
            model_path: Path to trained EfficientNet model
            confidence_threshold: Minimum confidence for valid predictions
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.class_names = [
            'Data Source', 'Data-Flow', 'Data-Transfer-Process', 
            'Excel-Tabelle', 'Info-Object', 'Transformation'
        ]
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained EfficientNet model"""
        try:
            # Create model architecture
            self.model = models.efficientnet_b0(weights=None)
            self.model.classifier[1] = torch.nn.Linear(
                self.model.classifier[1].in_features, 
                len(self.class_names)
            )
            
            # Load trained weights
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            self.model = self.model.to(self.device)
            self.model.eval()
            
            print(f"EfficientNet model loaded from {self.model_path}")
            
        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")
    
    def predict_from_path(self, image_path: str) -> Tuple[str, float, bool]:
        """
        Predict category from image file path
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (predicted_class, confidence, is_valid)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        image = Image.open(image_path).convert("RGB")
        return self._predict_image(image)
    
    def predict_from_base64(self, image_base64: str) -> Tuple[str, float, bool]:
        """
        Predict category from base64 encoded image
        
        Args:
            image_base64: Base64 encoded image data
            
        Returns:
            Tuple of (predicted_class, confidence, is_valid)
        """
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            return self._predict_image(image)
        except Exception as e:
            raise Exception(f"Failed to decode base64 image: {str(e)}")
    
    def _predict_image(self, image: Image.Image) -> Tuple[str, float, bool]:
        """
        Internal prediction method
        
        Args:
            image: PIL Image object
            
        Returns:
            Tuple of (predicted_class, confidence, is_valid)
        """
        try:
            # Preprocess image
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Prediction
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probs = F.softmax(outputs[0], dim=0)
                top_prob, top_class = torch.max(probs, dim=0)
            
            predicted_class = self.class_names[top_class.item()]
            confidence = top_prob.item()
            is_valid = confidence >= self.confidence_threshold
            
            return predicted_class, confidence, is_valid
            
        except Exception as e:
            raise Exception(f"Prediction failed: {str(e)}")
    
    def batch_predict(self, image_data_list: list) -> list:
        """
        Predict categories for multiple images
        
        Args:
            image_data_list: List of image data (paths or base64 strings)
            
        Returns:
            List of prediction results
        """
        results = []
        
        for i, image_data in enumerate(image_data_list):
            try:
                if isinstance(image_data, str) and os.path.exists(image_data):
                    # File path
                    prediction = self.predict_from_path(image_data)
                elif isinstance(image_data, str):
                    # Assume base64
                    prediction = self.predict_from_base64(image_data)
                else:
                    raise ValueError("Invalid image data format")
                
                results.append({
                    "index": i,
                    "predicted_class": prediction[0],
                    "confidence": prediction[1],
                    "is_valid": prediction[2],
                    "status": "success"
                })
                
            except Exception as e:
                results.append({
                    "index": i,
                    "predicted_class": None,
                    "confidence": 0.0,
                    "is_valid": False,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def get_category_mapping(self) -> dict:
        """
        Get mapping between directory names and class names
        
        Returns:
            Dictionary mapping class names to directory names
        """
        return {
            'Data Source': 'Data Source',
            'Data-Flow': 'Data-Flow', 
            'Data-Transfer-Process': 'Data-Transfer-Process',
            'Excel-Tabelle': 'Excel-Tabelle',
            'Info-Object': 'Info-Object',
            'Transformation': 'Transformation'
        }
    
    def filter_valid_predictions(self, predictions: list) -> list:
        """
        Filter predictions based on confidence threshold
        
        Args:
            predictions: List of prediction results
            
        Returns:
            List of valid predictions only
        """
        return [pred for pred in predictions if pred.get("is_valid", False)]

# Example usage
if __name__ == "__main__":
    # Test classifier
    classifier = ImageClassifier()
    
    test_image = r"C:\Users\egese\Documents\GitHub\ai-doc-checker\testpic.png"
    if os.path.exists(test_image):
        try:
            predicted_class, confidence, is_valid = classifier.predict_from_path(test_image)
            print(f"Prediction: {predicted_class}")
            print(f"Confidence: {confidence:.3f}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Test image not found") 