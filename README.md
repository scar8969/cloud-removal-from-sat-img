# Cloud Removal for LISS-IV Satellite Imagery

Generative AI framework for automated cloud removal in LISS-IV satellite imagery using a U-Net denoising autoencoder with skip connections.

## Quick Start

```bash
pip install -r requirements.txt
```

### 1. Prepare Training Data

Place clear optical images (Sentinel-2, Landsat, or any RGB/NIR) in `inputs/clear_images/`.

Or generate synthetic sample data for testing:
```bash
python create_sample_data.py
```

### 2. Train the Model

```bash
python cloud_removal_liss4.py
```

This trains a U-Net on synthetic cloudy/clear pairs. Takes ~2 minutes on CPU.

### 3. Run Inference

Place a cloudy image at the path specified in `config.yaml` (`infer.input_path`), then:

```bash
python cloud_removal_liss4.py infer
```

Output is saved to `outputs/liss4/cleaned.png`.

### 4. Generate Report

```bash
python web_viz.py --input-dir outputs --output report.html
```

## Architecture

- **Model:** U-Net with skip connections + BatchNorm (118K parameters)
- **Input:** 3-channel cloudy image (LISS-IV Green/Red/NIR or RGB)
- **Output:** 3-channel cloud-free image
- **Training:** Synthetic Gaussian-blob clouds overlaid on clear images
- **Loss:** MSE + Adam optimizer with ReduceLROnPlateau scheduling

## Project Structure

| File | Description |
|------|-------------|
| `cloud_removal_liss4.py` | Training and inference script (U-Net) |
| `config.yaml` | Hyperparameters and paths |
| `create_sample_data.py` | Generate synthetic training images |
| `web_viz.py` | HTML report generator |
| `demo.ipynb` | Interactive walkthrough notebook |
| `slides.md` | Presentation slides |
| `inputs/clear_images/` | Clear images for training |
| `inputs/cloudy_images/` | Cloudy images for inference |
| `outputs/` | Generated results and models |

## Results

| Metric | Value |
|--------|-------|
| Best Val PSNR | 28.26 dB |
| Best Val SSIM | 0.58 |
| Inference time | <1 sec/image (CPU) |
| Model size | 118K parameters |
| Training time | ~1 min (500 pairs, 5 epochs) |

## LISS-IV Band Mapping

| LISS-IV Band | Wavelength | Sentinel-2 Equivalent |
|--------------|------------|----------------------|
| Band 2 (Green) | 0.52-0.59 um | B3 |
| Band 3 (Red) | 0.62-0.68 um | B4 |
| Band 4 (NIR) | 0.77-0.86 um | B8 |

## Limitations

- Trained on synthetic clouds, not real cloud patterns
- Single-image inference (no multi-temporal fusion)
- No SAR data integration (optical only)
- Small training set (5 images) limits generalization

## Future Work

- Multi-temporal cloud removal
- SAR-optical fusion (Sentinel-1 + Sentinel-2)
- Attention mechanisms for cloud boundary preservation
- Web deployment (Streamlit/Gradio)
