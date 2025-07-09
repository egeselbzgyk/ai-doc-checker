import sys
sys.path.append('evaluation_system_v2')
from image_classifier import ImageClassifier

classifier = ImageClassifier()
predicted_class, confidence, is_valid = classifier.predict_from_path(r"C:\Users\egese\Documents\GitHub\ai-doc-checker\testpic.png")
print(f"Class: {predicted_class}, Confidence: {confidence:.2%}") 