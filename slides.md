# Cloud Removal for LISS-IV Satellite Imagery
## Generative AI Solution for Cloud Contamination

---

## Problem
- Persistent cloud cover in LISS-IV imagery over NER India
- Blocks land use mapping, disaster monitoring, environmental assessment
- No ground truth available for training

---

## Approach: U-Net Denoising Autoencoder
- **Architecture**: U-Net with skip connections + BatchNorm
- **Parameters**: 118K (lightweight, CPU-friendly)
- **Training**: Synthetic Gaussian-blob clouds on clear images
- **Input**: 3-channel cloudy image (LISS-IV Green/Red/NIR)
- **Output**: 3-channel cloud-free image
- **Hardware**: CPU-only, no GPU required

---

## Key Innovation
- **No Ground Truth Needed**: Train on synthetic cloudy/clear pairs
- **Skip Connections**: Preserve spatial details lost in encoding
- **BatchNorm**: Stabilizes training, faster convergence
- **LR Scheduling**: ReduceLROnPlateau with patience=3

---

## Pipeline
```
Clear S2 Image -> Synthetic Cloud Overlay -> U-Net Training -> Cloud-Free Output
                                         -> Validation (PSNR/SSIM)
                                         -> Apply to Real LISS-IV
```

---

## Results (Synthetic Benchmark)
| Metric | Value |
|--------|-------|
| Val PSNR | 28.26 dB |
| Val SSIM | 0.58 |
| Inference time | <1 sec/image (CPU) |
| Model size | 118K parameters |
| Training time | ~1 min |

---

## LISS-IV Band Mapping
| LISS-IV Band | Wavelength | Sentinel-2 |
|--------------|------------|-----------|
| Band 2 (Green) | 0.52-0.59 um | B3 |
| Band 3 (Red) | 0.62-0.68 um | B4 |
| Band 4 (NIR) | 0.77-0.86 um | B8 |

---

## Files
- `cloud_removal_liss4.py` - Training + inference (U-Net)
- `config.yaml` - Hyperparameters
- `create_sample_data.py` - Generate test data
- `web_viz.py` - HTML report generator
- `demo.ipynb` - Interactive walkthrough
- `README.md` - Documentation

---

## Limitations & Future Work
- Synthetic clouds only (need real cloud datasets)
- Single-image (no multi-temporal fusion)
- No SAR integration
- Future: Attention mechanisms, Transformer encoder, SAR fusion

---

## Thank You
