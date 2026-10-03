<div align="center">

# ☁️ Cloud Removal for LISS-IV Satellite Imagery

**Generative AI framework that removes clouds from LISS-IV satellite imagery with a U-Net denoising autoencoder.**

[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)](https://www.python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

</div>

A U-Net denoising autoencoder with **skip connections** that removes clouds from LISS-IV satellite imagery. Trained on synthetic cloudy/clear pairs, it reconstructs cloud-free optical imagery in under a second per image on CPU.

## ✨ Features

- **U-Net autoencoder** with skip connections + BatchNorm (~118K parameters)
- **3-channel input** — LISS-IV Green/Red/NIR or RGB
- **Synthetic training** — Gaussian-blob clouds overlaid on clear images
- **MSE loss** + Adam optimizer with ReduceLROnPlateau scheduling
- **CLI training & inference** — one command each
- **HTML report generator** — visual before/after comparison
- **Interactive notebook** — `demo.ipynb` walkthrough

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Deep learning | PyTorch 2.0 · torchvision |
| Vision | OpenCV · NumPy |
| Config | PyYAML |
| Visualization | Matplotlib · Flask (web viz) |

## 🚀 Quick Start

```bash
pip install -r requirements.txt
```

### 1. Prepare Training Data

Place clear optical images (Sentinel-2, Landsat, or any RGB/NIR) in `inputs/clear_images/`, or generate synthetic sample data:

```bash
python create_sample_data.py
```

### 2. Train the Model

```bash
python cloud_removal_liss4.py
```

Trains a U-Net on synthetic cloudy/clear pairs. Takes ~2 minutes on CPU.

### 3. Run Inference

Place a cloudy image at the path in `config.yaml` (`infer.input_path`), then:

```bash
python cloud_removal_liss4.py infer
```

Output is saved to `outputs/liss4/cleaned.png`.

### 4. Generate Report

```bash
python web_viz.py --input-dir outputs --output report.html
```

## 📁 Project Structure

| File | Description |
|------|-------------|
| `cloud_removal_liss4.py` | Training and inference script (U-Net) |
| `config.yaml` | Hyperparameters and paths |
| `create_sample_data.py` | Generate synthetic training images |
| `web_viz.py` | HTML report generator |
| `demo.ipynb` | Interactive walkthrough notebook |
| `app.py` | Flask web app |
| `slides.md` | Presentation slides |
| `inputs/` | Clear + cloudy images |
| `outputs/` | Generated results and models |

## 📊 Results

| Metric | Value |
|--------|-------|
| Best Val PSNR | **28.26 dB** |
| Best Val SSIM | **0.58** |
| Inference time | <1 sec/image (CPU) |
| Model size | 118K parameters |
| Training time | ~1 min (500 pairs, 5 epochs) |

## 🛰️ LISS-IV Band Mapping

| LISS-IV Band | Wavelength | Sentinel-2 Equivalent |
|--------------|------------|----------------------|
| Band 2 (Green) | 0.52–0.59 µm | B3 |
| Band 3 (Red) | 0.62–0.68 µm | B4 |
| Band 4 (NIR) | 0.77–0.86 µm | B8 |

## ⚠️ Limitations

- Trained on synthetic clouds, not real cloud patterns
- Single-image inference (no multi-temporal fusion)
- No SAR data integration (optical only)
- Small training set (5 images) limits generalization

## 🔮 Future Work

- Multi-temporal cloud removal
- SAR-optical fusion (Sentinel-1 + Sentinel-2)
- Attention mechanisms for cloud-boundary preservation
- Web deployment (Streamlit/Gradio)

## 📄 License

[MIT](LICENSE) © Priyanshu Rout