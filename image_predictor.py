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

image_path = "test_images/5.png"
input_tensor = load_image(image_path).to(device)
input_tensor.requires_grad_(True)

# 3. SINIF TAHMİNİ
output = model(input_tensor)
pred_class = torch.argmax(output, dim=1).item()

# 4. IG – AŞAMALI GÖSTERİM

def interpolate_inputs(baseline, input_tensor, alphas):
    return [(baseline + alpha * (input_tensor - baseline)).detach() for alpha in alphas]

def compute_gradients(input_batch, model, target_class):
    input_batch.requires_grad_(True)
    output = model(input_batch)
    loss = output[0, target_class]
    loss.backward()
    gradients = input_batch.grad.detach()
    return gradients

def visualize_ig_steps(model, input_tensor, baseline, target_class, n_steps=6):
    alphas = torch.linspace(0, 1, steps=n_steps)
    interpolated_inputs = interpolate_inputs(baseline, input_tensor, alphas)

    fig, axes = plt.subplots(2, n_steps, figsize=(n_steps * 2.5, 5))

    for i, inp in enumerate(interpolated_inputs):
        inp = inp.to(input_tensor.device)
        gradients = compute_gradients(inp.clone(), model, target_class)
        gradient_image = gradients.squeeze().cpu().numpy()
        gradient_image = np.mean(gradient_image, axis=0)
        gradient_image = np.abs(gradient_image)
        gradient_image = gradient_image / (np.max(gradient_image) + 1e-8)

        # Görseli inverse normalize et
        orig_img = inp.squeeze().cpu().numpy()
        orig_img = np.transpose(orig_img, (1, 2, 0))
        orig_img = orig_img * [0.229, 0.224, 0.225] + [0.485, 0.456, 0.406]
        orig_img = np.clip(orig_img, 0, 1)

        axes[0, i].imshow(orig_img)
        axes[0, i].set_title(f"α = {alphas[i]:.1f}")
        axes[0, i].axis("off")

        axes[1, i].imshow(gradient_image, cmap='hot')
        axes[1, i].axis("off")

    axes[0, 0].set_ylabel("Interpolated Inputs", fontsize=10)
    axes[1, 0].set_ylabel("Gradients", fontsize=10)
    plt.tight_layout()
    plt.show()

# AŞAMALI GÖRSELLEŞTİRMEYİ ÇAĞIR
baseline = torch.zeros_like(input_tensor).to(device)
visualize_ig_steps(model, input_tensor, baseline, pred_class, n_steps=6)
