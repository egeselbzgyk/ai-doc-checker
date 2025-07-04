"""
AI Doc Checker - Evaluation System V2

Complete evaluation system for student PDF submissions with SAP BW content.

Main components:
- PDFImageExtractor: Extract images from PDF files
- ImageClassifier: EfficientNet-based image classification
- QwenClient: Interface to Qwen 2.5-VL API server
- MetadataGenerator: Generate metadata database for reference solutions
- EvaluationEngine: Main orchestrator for complete evaluation workflow

Usage:
    from evaluation_system_v2 import EvaluationEngine
    
    engine = EvaluationEngine()
    result = engine.evaluate_pdf_submission("student.pdf")
    engine.save_evaluation_result(result)
"""

from .pdf_processor import PDFImageExtractor
from .image_classifier import ImageClassifier
from .qwen_client import QwenClient
from .metadata_generator import MetadataGenerator
from .evaluation_engine import EvaluationEngine

__version__ = "2.0.0"
__author__ = "THM Students"

__all__ = [
    "PDFImageExtractor",
    "ImageClassifier", 
    "QwenClient",
    "MetadataGenerator",
    "EvaluationEngine"
] 