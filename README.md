# AI-Document-Checker – EfficientNet-B0

This is a machine learning project developed as part of a university assignment. The goal is to classify screenshots from SAP BW into one of six predefined categories using a convolutional neural network.

## Task Description (Aufgabe 2)

- Classify SAP-related screenshots into the following categories:
  - Excel-Tabelle
  - Data-Flow
  - Info-Object
  - Transformation
  - Data-Transfer-Process
  - Data Source
- Use the dataset provided via Moodle.
- Apply data augmentation and prepare the dataset accordingly.
- Train a deep learning model and integrate it into the overall workflow so that extracted images can be automatically classified.

## Project Progress

- Dataset cleaned and mapped to 6 target classes
- Data augmentation applied (rotation, flipping, color jitter)
- Model trained using EfficientNet-B0 (PyTorch)
- Early stopping implemented to prevent overfitting
- Single image classification function (`predict_image()`) completed
- Ready for folder-level batch prediction and PDF integration

## Dependencies

- Python 3.9+
- PyTorch
- torchvision
- Pillow
- matplotlib
