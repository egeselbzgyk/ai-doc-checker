import os
import json
import base64
from typing import Dict, List, Any
from datetime import datetime
from qwen_client import QwenClient
from image_classifier import ImageClassifier
import glob

class MetadataGenerator:
    """Generate metadata database for reference solutions"""
    
    def __init__(self, reference_images_path: str = "../dataset/mapped_train", 
                 output_path: str = "metadata_database.json"):
        """
        Initialize metadata generator
        
        Args:
            reference_images_path: Path to reference images directory
            output_path: Output path for metadata database
        """
        self.reference_path = reference_images_path
        self.output_path = output_path
        self.qwen_client = QwenClient()
        self.classifier = ImageClassifier()
        
        # Check if Qwen server is available
        health = self.qwen_client.health_check()
        if not health.get("model_loaded", False):
            raise Exception("Qwen server is not available or model not loaded")
        
        print("Metadata Generator initialized")
    
    def _image_to_base64(self, image_path: str) -> str:
        """Convert image file to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    
    def _get_image_files(self, category_path: str) -> List[str]:
        """Get all image files from category directory"""
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
        image_files = []
        
        for ext in extensions:
            image_files.extend(glob.glob(os.path.join(category_path, ext)))
        
        return image_files
    
    def generate_category_metadata(self, category: str) -> Dict[str, Any]:
        """
        Generate metadata for all images in a category
        
        Args:
            category: Category name (e.g., 'Excel-Tabelle')
            
        Returns:
            Dictionary with category metadata
        """
        category_path = os.path.join(self.reference_path, category)
        
        if not os.path.exists(category_path):
            raise FileNotFoundError(f"Category path not found: {category_path}")
        
        image_files = self._get_image_files(category_path)
        
        if not image_files:
            print(f"No images found in {category}")
            return {"category": category, "images": [], "count": 0}
        
        print(f"Processing {len(image_files)} images in {category}...")
        
        category_metadata = {
            "category": category,
            "images": [],
            "count": len(image_files),
            "generated_at": datetime.now().isoformat()
        }
        
        for i, image_path in enumerate(image_files):
            try:
                print(f"Processing {i+1}/{len(image_files)}: {os.path.basename(image_path)}")
                
                # Convert to base64
                image_base64 = self._image_to_base64(image_path)
                
                # Verify category with classifier (for reference only, no filtering)
                predicted_class, confidence, is_valid = self.classifier.predict_from_base64(image_base64)
                
                # For reference solutions: process ALL images regardless of confidence
                # Confidence filtering only applies to student submissions during evaluation
                
                if predicted_class != category:
                    print(f"Category mismatch: predicted {predicted_class}, expected {category}")
                    # Continue anyway - reference solutions are pre-categorized correctly
                
                # Extract metadata with Qwen
                metadata_result = self.qwen_client.extract_metadata(image_base64, category)
                
                if metadata_result.get("status") != "success":
                    print(f"Metadata extraction failed: {metadata_result.get('error')}")
                    continue
                
                # Store image metadata
                image_metadata = {
                    "filename": os.path.basename(image_path),
                    "file_path": image_path,
                    "predicted_class": predicted_class,
                    "confidence": confidence,
                    "metadata": metadata_result.get("metadata", {}),
                    "processed_at": datetime.now().isoformat()
                }
                
                category_metadata["images"].append(image_metadata)
                print(f"Metadata extracted successfully")
                
            except Exception as e:
                print(f"Error processing {image_path}: {str(e)}")
                continue
        
        print(f"Completed {category}: {len(category_metadata['images'])} images processed")
        return category_metadata
    
    def generate_full_database(self) -> Dict[str, Any]:
        """
        Generate metadata for all categories
        
        Returns:
            Complete metadata database
        """
        categories = self.classifier.class_names
        
        database = {
            "generated_at": datetime.now().isoformat(),
            "categories": {},
            "total_images": 0,
            "version": "1.0"
        }
        
        for category in categories:
            try:
                category_metadata = self.generate_category_metadata(category)
                database["categories"][category] = category_metadata
                database["total_images"] += len(category_metadata.get("images", []))
                
            except Exception as e:
                print(f" Failed to process category {category}: {str(e)}")
                database["categories"][category] = {
                    "category": category,
                    "images": [],
                    "count": 0,
                    "error": str(e)
                }
        
        return database
    
    def save_database(self, database: Dict[str, Any] = None) -> str:
        """
        Save metadata database to file
        
        Args:
            database: Database to save (if None, generates new one)
            
        Returns:
            Path to saved file
        """
        if database is None:
            print("Generating metadata database...")
            database = self.generate_full_database()
        
        # Save to file
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print(f"Metadata database saved to: {self.output_path}")
        print(f"Total categories: {len(database['categories'])}")
        print(f"Total images: {database['total_images']}")
        
        return self.output_path
    
    def load_database(self) -> Dict[str, Any]:
        """
        Load existing metadata database
        
        Returns:
            Metadata database dictionary
        """
        if not os.path.exists(self.output_path):
            raise FileNotFoundError(f"Metadata database not found: {self.output_path}")
        
        with open(self.output_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        print(f"Loaded metadata database: {database['total_images']} images")
        return database
    
    def update_database(self) -> str:
        """
        Update existing database with new images
        
        Returns:
            Path to updated database
        """
        try:
            existing_db = self.load_database()
            print("Updating existing database...")
        except FileNotFoundError:
            print("Creating new database...")
            return self.save_database()
        
        # Generate new database
        new_db = self.generate_full_database()
        
        # Merge with existing (new data takes precedence)
        updated_db = {
            "generated_at": new_db["generated_at"],
            "categories": new_db["categories"],
            "total_images": new_db["total_images"],
            "version": "1.0",
            "previous_version": existing_db.get("generated_at")
        }
        
        return self.save_database(updated_db)

# Command line interface
if __name__ == "__main__":
    import sys
    
    generator = MetadataGenerator()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "generate":
            generator.save_database()
        elif sys.argv[1] == "update":
            generator.update_database()
        elif sys.argv[1] == "category" and len(sys.argv) > 2:
            category = sys.argv[2]
            metadata = generator.generate_category_metadata(category)
            print(json.dumps(metadata, indent=2, ensure_ascii=False))
        else:
            print("Usage: python metadata_generator.py [generate|update|category <name>]")
    else:
        # Default: generate full database
        generator.save_database() 