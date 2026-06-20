from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sys
import base64
import io
import numpy as np
import cv2
import torch
from torchvision import transforms

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_removal_liss4 import UNetCloudRemoval, load_image, save_image, compute_psnr, compute_ssim

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Load model once at startup
MODEL_PATH = "outputs/models/model.pt"
model = None

def load_model():
    global model
    if model is None:
        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(f"Model not found at {MODEL_PATH}. Run training first.")
        model = UNetCloudRemoval()
        model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
        model.eval()
    return model

def image_to_base64(img_array):
    """Convert numpy image (0-255 uint8) to base64 data URI"""
    _, buffer = cv2.imencode('.png', cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR))
    b64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{b64}"

def base64_to_image(b64_string):
    """Convert base64 data URI to numpy image (0-1 float32 RGB)"""
    if ',' in b64_string:
        b64_string = b64_string.split(',')[1]
    data = base64.b64decode(b64_string)
    nparr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    return img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/examples/<path:filename>')
def examples_static(filename):
    return send_from_directory('static/examples', filename)

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "model_loaded": model is not None})

@app.route('/api/model/info')
def model_info():
    load_model()
    param_count = sum(p.numel() for p in model.parameters())
    return jsonify({
        "parameters": int(param_count),
        "model_size_mb": round(param_count * 4 / (1024 * 1024), 2),
        "input_channels": 3,
        "output_channels": 3,
        "architecture": "U-Net with skip connections",
    })

@app.route('/api/infer', methods=['POST'])
def infer():
    load_model()

    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No image provided"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"success": False, "error": "Empty filename"}), 400

    # Read image
    data = file.read()
    nparr = np.frombuffer(data, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        return jsonify({"success": False, "error": "Invalid image format"}), 400

    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

    # Run inference
    import time
    start = time.time()

    tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).float()
    with torch.no_grad():
        out = model(tensor).squeeze().permute(1, 2, 0).numpy()

    proc_time = (time.time() - start) * 1000

    # Compute metrics
    psnr = compute_psnr(out, img)
    ssim = compute_ssim(out, img)

    # Create comparison image
    comparison = np.hstack([img, out])
    comparison_uint8 = (np.clip(comparison, 0, 1) * 255).astype(np.uint8)

    # Convert to base64
    input_b64 = image_to_base64((img * 255).astype(np.uint8))
    cleaned_b64 = image_to_base64((np.clip(out, 0, 1) * 255).astype(np.uint8))
    comparison_b64 = image_to_base64(comparison_uint8)

    return jsonify({
        "success": True,
        "input_image": input_b64,
        "cleaned_image": cleaned_b64,
        "comparison_image": comparison_b64,
        "metrics": {
            "psnr": round(float(psnr), 2),
            "ssim": round(float(ssim), 4),
            "processing_time_ms": round(proc_time, 1),
        }
    })

@app.route('/api/examples')
def list_examples():
    examples_dir = "static/examples"
    if not os.path.exists(examples_dir):
        return jsonify({"examples": []})

    cloudy_files = sorted([f for f in os.listdir(examples_dir) if f.startswith("cloudy_")])
    examples = []
    for cf in cloudy_files:
        idx = cf.split("_")[1].split(".")[0]
        cleaned_name = f"cleaned_{idx}.png"
        if os.path.exists(os.path.join(examples_dir, cleaned_name)):
            examples.append({
                "id": idx,
                "cloudy_url": f"/static/examples/{cf}",
                "cleaned_url": f"/static/examples/{cleaned_name}",
            })
    return jsonify({"examples": examples})

@app.route('/api/metrics')
def get_metrics():
    metrics_path = "outputs/synthetic/loss_history.npy"
    if not os.path.exists(metrics_path):
        return jsonify({"error": "No training metrics found"}), 404

    history = np.load(metrics_path, allow_pickle=True)
    return jsonify({
        "history": [dict(h) for h in history],
    })

if __name__ == '__main__':
    # Pre-load model
    try:
        load_model()
        print("Model loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load model: {e}")

    app.run(debug=True, host='0.0.0.0', port=5000)
