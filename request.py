import requests
import base64

# Health check
response = requests.get('http://ki4.mni.thm.de:5000/health')
print(response.json())

# Image analysis
with open('image.png', 'rb') as f:
    image_b64 = base64.b64encode(f.read()).decode()

payload = {
    "image_base64": image_b64,
    "prompt": "Analyze this SAP BW screenshot in detail.",
    "max_tokens": 2048
}

response = requests.post('http://ki4.mni.thm.de:5000/analyze', json=payload)
print(response.json())