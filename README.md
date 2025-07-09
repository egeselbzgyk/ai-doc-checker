<<<<<<< HEAD
# AI Doc Checker - Evaluation System V2

Complete automated evaluation system for student PDF submissions containing SAP BW diagrams and content.

## System Overview

The evaluation system processes student PDF submissions through multiple stages:

1. **PDF Processing**: Extract images from student PDF files
2. **Classification**: Use EfficientNet to classify images into 6 SAP BW categories
3. **Quality Check**: Use Qwen 2.5-VL to verify image evaluability
4. **Metadata Matching**: Find best reference solutions based on content similarity
5. **Detailed Evaluation**: Compare student work with references and provide detailed scoring
6. **Final Assessment**: Generate overall score (0-100) with pass/fail determination (≥70)

## Categories Supported

- **Excel-Tabelle**: Excel tables and spreadsheets
- **Data-Flow**: Data flow diagrams and process flows
- **Data-Transfer-Process**: DTP (Data Transfer Process) configurations
- **Transformation**: Data transformation mappings and rules
- **Data Source**: Data source definitions and connections
- **Info-Object**: InfoCubes, DSOs, and other info objects

## Quick Start

    1. In ki4.mni.thm.de muss "python qwen_api_server.py" ausgeführt werden.

    2. Um lokal und Server zu verbinden: ssh -L 5000:localhost:5000 benutzerName@ki4.mni.thm.de

    3. app.py ausführen.

    4. Dann zu http://localhost:5001/

### Prerequisites

1. **Qwen 2.5-VL Server**: Running on `http://ki4.mni.thm.de:5000`
2. **EfficientNet Model**: Located at `../model/efficientnet_b0_best.pth`
3. **Reference Images**: Located at `../dataset/mapped_train/`
4. **Python Environment**: Python 3.8+ with required packages

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize the system
python metadata_generator.py generate  # Generate metadata database (one-time)
```

### Basic Usage

```python
from evaluation_system_v2 import EvaluationEngine

# Initialize evaluation engine
engine = EvaluationEngine()

# Evaluate a student PDF submission
result = engine.evaluate_pdf_submission("student_submission.pdf")

# Save results and display summary
output_file = engine.save_evaluation_result(result)
print(engine.get_evaluation_summary(result))

# Check if student passed
if result["passed"]:
    print("✅ BESTANDEN")
else:
    print("❌ NICHT BESTANDEN")
```

### Jupyter Notebook Demo

Open `evaluation_demo.ipynb` for an interactive demonstration and testing interface.

## System Architecture

### Core Components

#### 1. PDFImageExtractor

- Extracts images from PDF files using PyMuPDF
- Filters images by minimum size
- Converts to base64 for API processing
- Supports dynamic image count (1-N images per PDF)

#### 2. ImageClassifier

- EfficientNet B0 model trained on SAP BW images
- 6-class classification with confidence thresholding
- 60% confidence threshold for valid predictions
- GPU/CPU support with automatic device selection

#### 3. QwenClient

- Interface to Qwen 2.5-VL API server
- Image evaluability assessment
- Metadata extraction for content analysis
- Detailed evaluation with reference comparison
- Robust error handling and retry logic

#### 4. MetadataGenerator

- Batch processing of reference solutions
- Metadata extraction for fast content matching
- Database generation and maintenance
- Incremental updates support

#### 5. EvaluationEngine

- Main orchestrator for complete evaluation workflow
- Multi-stage processing pipeline
- Error handling and recovery
- Comprehensive result reporting

### Evaluation Pipeline

```
PDF Input
    ↓
[Extract Images] → Filter by size
    ↓
[Classify Images] → EfficientNet (6 classes)
    ↓
[Filter by Confidence] → Keep predictions ≥ 60%
    ↓
[Check Evaluability] → Qwen quality assessment
    ↓
[Extract Metadata] → Qwen content analysis
    ↓
[Find Best Reference] → Metadata similarity matching
    ↓
[Detailed Evaluation] → Qwen comparison & scoring
    ↓
[Calculate Final Score] → Average scores, pass/fail
    ↓
JSON Results + Summary
```

## Configuration

### Qwen Server Configuration

- Default URL: `http://ki4.mni.thm.de:5000`
- Endpoints: `/health`, `/analyze`, `/text_only`
- Timeout: 60 seconds for image analysis

### Classification Thresholds

- Confidence threshold: 60% (configurable)
- Pass threshold: 70 points (configurable)
- Image minimum size: 100x100 pixels

### File Paths

- Model path: `../model/efficientnet_b0_best.pth`
- Reference images: `../dataset/mapped_train/`
- Metadata database: `metadata_database.json`

## Output Format

### Evaluation Result JSON

```json
{
  "pdf_path": "student_submission.pdf",
  "timestamp": "2025-01-27T19:32:00",
  "images": [...],
  "valid_images": [...],
  "evaluations": [
    {
      "filename": "page_1_img_1.png",
      "category": "Excel-Tabelle",
      "confidence": 0.89,
      "score": 85,
      "evaluation": {
        "gesamt_bewertung": {
          "punkte_total": 85,
          "bestanden": true,
          "feedback": "Detailed feedback...",
          "staerken": ["Good structure"],
          "verbesserungen": ["Add more detail"]
        }
      }
    }
  ],
  "overall_score": 85.0,
  "passed": true,
  "errors": []
}
```

## Advanced Usage

### Custom Configuration

```python
# Custom confidence threshold
classifier = ImageClassifier(confidence_threshold=0.7)

# Custom Qwen server
qwen_client = QwenClient(base_url="http://custom-server:5000")

# Custom metadata database path
engine = EvaluationEngine(metadata_db_path="custom_metadata.json")
```

### Batch Processing

```python
# Process multiple PDFs
pdf_files = ["student1.pdf", "student2.pdf", "student3.pdf"]

results = []
for pdf_file in pdf_files:
    result = engine.evaluate_pdf_submission(pdf_file)
    results.append(result)
    engine.save_evaluation_result(result)
```

### Metadata Database Management

```python
from evaluation_system_v2 import MetadataGenerator

# Generate new database
generator = MetadataGenerator()
generator.save_database()

# Update existing database
generator.update_database()

# Generate metadata for specific category
metadata = generator.generate_category_metadata("Excel-Tabelle")
```
