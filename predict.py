import torch
from torchvision import models, transforms
from PIL import Image
import torch.nn.functional as F

class_names = ['Data Source', 'Data-Flow', 'Data-Transfer-Process', 'Excel-Tabelle', 'Info-Object', 'Transformation']

def predict_image(image_path, model_path="model/efficientnet_b0_best.pth"):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])
    
    image = Image.open(image_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.efficientnet_b0(weights=None)
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, len(class_names))
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()

    with torch.no_grad():
        input_tensor = input_tensor.to(device)
        outputs = model(input_tensor)
        probs = F.softmax(outputs[0], dim=0)
        top_prob, top_class = torch.max(probs, dim=0)

    return class_names[top_class.item()], top_prob.item()