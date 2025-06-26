import torch
from torchvision import models, transforms
from captum.attr import IntegratedGradients
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# 1. MODELİ YÜKLE
model_path = r"C:\Users\egese\Documents\GitHub\ai-doc-checker\model\efficientnet_b0_best.pth"

model = models.efficientnet_b0(weights=None)
model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, 6)
model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
model.eval()

device = torch.device("cpu")
model.to(device)

# 2. GÖRSELİ YÜKLE
def load_image(img_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])
    img = Image.open(img_path).convert("RGB")
    return transform(img).unsqueeze(0)

image_path = "test_images/4.png"
input_tensor = load_image(image_path).to(device)
input_tensor.requires_grad_(True)

# 3. SINIF TAHMİNİ
output = model(input_tensor)
pred_class = torch.argmax(output, dim=1).item()

# 4. IG HESABI (düşük adım sayısı ile)
baseline = torch.zeros_like(input_tensor).to(device)
ig = IntegratedGradients(model)

attributions, delta = ig.attribute(
    input_tensor,
    baselines=baseline,
    target=pred_class,
    n_steps=2,
    return_convergence_delta=True
)

# 5. GÖRSALLEŞTİRME
attr = attributions.squeeze().detach().cpu().numpy()
attr = np.mean(attr, axis=0)
attr = np.maximum(attr, 0)
attr = attr / (np.max(attr) + 1e-8)

def show_image_attr(img_tensor, attr_map):
    img = img_tensor.squeeze().detach().cpu().numpy()
    img = np.transpose(img, (1, 2, 0))
    img = img * [0.229, 0.224, 0.225] + [0.485, 0.456, 0.406]
    img = np.clip(img, 0, 1)

    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.imshow(img)
    plt.title("Original")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(img)
    plt.imshow(attr_map, cmap="hot", alpha=0.5)
    plt.title("Integrated Gradients")
    plt.axis("off")

    plt.tight_layout()
    plt.show()

show_image_attr(input_tensor, attr)
