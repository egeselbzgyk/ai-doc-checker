#!/usr/bin/env python3
"""
Qwen2.5-VL 7B API Server
Provides remote access to the model running on university server
"""

from flask import Flask, request, jsonify
import torch
from transformers import AutoTokenizer, AutoProcessor
from transformers.models.qwen2_5_vl.modeling_qwen2_5_vl import Qwen2_5_VLForConditionalGeneration
from PIL import Image
import base64
import io
import json
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Global model variables - loaded once to save memory
model = None
processor = None
tokenizer = None

def load_model():
    """Load Qwen2.5-VL model once at startup"""
    global model, processor, tokenizer
    
    if model is None:
        print("Loading Qwen2.5-VL 7B model...")
        model_path = "./qwen2-vl-7b"
        
        # Load tokenizer and processor first (faster)
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
        
        # Load model with optimal settings
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,  # Memory efficient
            device_map="auto" if torch.cuda.device_count() > 1 else device,
            trust_remote_code=True,
            low_cpu_mem_usage=True  # Reduce RAM usage during loading
        )
        
        print("Model loaded and ready for inference!")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint - test if server is running"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "cuda_available": torch.cuda.is_available(),
        "gpu_count": torch.cuda.device_count(),
        "message": "Qwen2.5-VL 7B API Server is running"
    })

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """
    Main endpoint for image analysis
    
    Expected JSON payload:
    {
        "image_base64": "base64_encoded_image_data",
        "prompt": "Analysis prompt text",
        "max_tokens": 2048
    }
    
    Returns:
    {
        "response": "Model response text",
        "status": "success"
    }
    """
    try:
        data = request.json
        
        # Extract parameters from request
        image_b64 = data.get('image_base64')
        prompt_text = data.get('prompt', 'Analyze this image in detail.')
        max_tokens = data.get('max_tokens', 2048)
        
        if not image_b64:
            return jsonify({"error": "Missing 'image_base64' field in request"}), 400
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(image_b64)
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
        except Exception as e:
            return jsonify({"error": f"Invalid image data: {str(e)}"}), 400
        
        # Create conversation format for Qwen2.5-VL
        conversation = [{
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt_text}
            ]
        }]
        
        # Process conversation with the model
        text_input = processor.apply_chat_template(
            conversation, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # Tokenize and prepare inputs
        inputs = processor(
            text=[text_input], 
            images=[image],
            return_tensors="pt",
            padding=True
        )
        
        # Move tensors to correct device (GPU if available)
        device = next(model.parameters()).device
        if device.type == 'cuda':
            for key in inputs:
                if torch.is_tensor(inputs[key]):
                    inputs[key] = inputs[key].to(device)
        
        # Generate response with controlled parameters
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.1,  # Low temperature for consistent results
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Extract only the new tokens (response)
        generated_ids = [
            output_ids[len(input_ids):] 
            for input_ids, output_ids in zip(inputs['input_ids'], generated_ids)
        ]
        
        # Decode response text
        response_text = tokenizer.batch_decode(
            generated_ids, 
            skip_special_tokens=True
        )[0]
        
        return jsonify({
            "response": response_text,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Analysis failed: {str(e)}",
            "status": "error"
        }), 500

@app.route('/text_only', methods=['POST'])
def text_only():
    """
    Text-only analysis endpoint (no image)
    
    Expected JSON payload:
    {
        "prompt": "Text prompt",
        "max_tokens": 1024
    }
    """
    try:
        data = request.json
        prompt_text = data.get('prompt', 'Hello! Please introduce yourself.')
        max_tokens = data.get('max_tokens', 1024)
        
        # Text-only conversation
        conversation = [{
            "role": "user",
            "content": [{"type": "text", "text": prompt_text}]
        }]
        
        text_input = processor.apply_chat_template(
            conversation, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        inputs = processor(
            text=[text_input], 
            images=None,  # No images for text-only
            return_tensors="pt",
            padding=True
        )
        
        # Move to device
        device = next(model.parameters()).device
        if device.type == 'cuda':
            for key in inputs:
                if torch.is_tensor(inputs[key]):
                    inputs[key] = inputs[key].to(device)
        
        # Generate response
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.1,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Extract response
        response_text = tokenizer.batch_decode(
            [generated_ids[0][len(inputs['input_ids'][0]):]], 
            skip_special_tokens=True
        )[0]
        
        return jsonify({
            "response": response_text,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Text analysis failed: {str(e)}",
            "status": "error"
        }), 500

if __name__ == '__main__':
    print("Starting Qwen2.5-VL 7B API Server...")
    load_model()
    
    print("Server will be accessible at:")
    print("   - Local: http://localhost:5000")
    print("   - Network: http://ki4.mni.thm.de:5000")
    print("   - Health check: GET /health")
    print("   - Image analysis: POST /analyze")
    print("   - Text only: POST /text_only")
    
    # Run server on all interfaces, port 5000
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)