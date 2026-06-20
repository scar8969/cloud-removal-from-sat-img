# cloud_removal_liss4.py
# ------------------------------------------------------------
# U-Net denoising autoencoder for cloud removal
# Hackathon version: CPU-only, fast training
# ------------------------------------------------------------

import os
import sys
import yaml
import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

# ----------------------------
# Config
# ----------------------------
CFG = None

def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    root = os.path.dirname(os.path.abspath(path))
    def expand(v):
        if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
            return os.path.join(root, v[2:-1])
        if isinstance(v, str):
            return v.replace("\\", "/")
        return v
    def rec(d):
        if isinstance(d, dict):
            return {k: rec(v) for k, v in d.items()}
        if isinstance(d, list):
            return [rec(x) for x in d]
        return expand(d)
    return rec(cfg)

# ----------------------------
# Image utilities
# ----------------------------
def load_image(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Cannot load image: {path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    return img

def save_image(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(path, img_bgr)

def random_crop(img, size):
    h, w = img.shape[:2]
    if h <= size and w <= size:
        return cv2.resize(img, (size, size))
    y = np.random.randint(0, h - size + 1)
    x = np.random.randint(0, w - size + 1)
    return img[y:y+size, x:x+size]

# ----------------------------
# Synthetic cloud generation
# ----------------------------
def generate_cloud_mask(h, w, n_blobs, sigma):
    mask = np.zeros((h, w), dtype=np.float32)
    for _ in range(n_blobs):
        cx = np.random.randint(0, w)
        cy = np.random.randint(0, h)
        yy, xx = np.ogrid[:h, :w]
        blob = np.exp(-((yy - cy)**2 + (xx - cx)**2) / (2 * sigma**2))
        mask += blob * np.random.uniform(0.3, 1.0)
    mask = np.clip(mask / max(mask.max(), 1e-6), 0, 1)
    mask = cv2.GaussianBlur(mask, (51, 51), 0)
    return mask

def overlay_clouds(img, cloud_cfg):
    h, w = img.shape[:2]
    n_blobs = np.random.randint(*cloud_cfg["n_blobs"])
    sigma = np.random.randint(*cloud_cfg["sigma_range"])
    cloudiness = np.random.uniform(*cloud_cfg["cloudiness_range"])
    mask = generate_cloud_mask(h, w, n_blobs, sigma)
    mask = (mask > (1 - cloudiness)).astype(np.float32)
    mask = cv2.GaussianBlur(mask, (7, 7), 0)
    cloud_val = np.full_like(img, 0.9, dtype=np.float32)
    return img * (1 - mask[..., None]) + cloud_val * mask[..., None]

# ----------------------------
# Dataset
# ----------------------------
class CloudRemovalDataset(Dataset):
    def __init__(self, clear_paths, cloud_cfg, patch_size=128, synth_pairs=5000):
        self.clear_paths = clear_paths
        self.cloud_cfg = cloud_cfg
        self.patch_size = patch_size
        self.synth_pairs = synth_pairs

    def __len__(self):
        return self.synth_pairs

    def __getitem__(self, idx):
        path = self.clear_paths[idx % len(self.clear_paths)]
        clear = load_image(path)
        clear = random_crop(clear, self.patch_size)
        cloudy = overlay_clouds(clear, self.cloud_cfg)
        cloudy_tensor = torch.from_numpy(cloudy).permute(2, 0, 1).float()
        clear_tensor = torch.from_numpy(clear).permute(2, 0, 1).float()
        return cloudy_tensor, clear_tensor

# ----------------------------
# Model: U-Net with Skip Connections
# ----------------------------
class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1), nn.BatchNorm2d(out_ch), nn.ReLU(True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1), nn.BatchNorm2d(out_ch), nn.ReLU(True),
        )
    def forward(self, x):
        return self.conv(x)

class UNetCloudRemoval(nn.Module):
    def __init__(self, in_ch=3, out_ch=3, base_ch=16):
        super().__init__()
        self.enc1 = DoubleConv(in_ch, base_ch)
        self.enc2 = DoubleConv(base_ch, base_ch * 2)
        self.pool = nn.MaxPool2d(2)
        self.bottleneck = DoubleConv(base_ch * 2, base_ch * 4)
        self.up2 = nn.ConvTranspose2d(base_ch * 4, base_ch * 2, 2, stride=2)
        self.dec2 = DoubleConv(base_ch * 4, base_ch * 2)
        self.up1 = nn.ConvTranspose2d(base_ch * 2, base_ch, 2, stride=2)
        self.dec1 = DoubleConv(base_ch * 2, base_ch)
        self.out_conv = nn.Conv2d(base_ch, out_ch, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        b = self.bottleneck(self.pool(e2))
        d2 = self.up2(b)
        d2 = self.dec2(torch.cat([d2, e2], dim=1))
        d1 = self.up1(d2)
        d1 = self.dec1(torch.cat([d1, e1], dim=1))
        return self.sigmoid(self.out_conv(d1))

# ----------------------------
# Metrics
# ----------------------------
def compute_psnr(pred, target):
    mse = np.mean((pred - target) ** 2)
    if mse == 0:
        return 100.0
    return 10.0 * np.log10(1.0 / mse)

def compute_ssim(pred, target):
    mu_p, mu_t = pred.mean(), target.mean()
    sig_p, sig_t = pred.std(), target.std()
    sig_pt = ((pred - mu_p) * (target - mu_t)).mean()
    c1, c2 = (0.01 * 1.0) ** 2, (0.03 * 1.0) ** 2
    ssim = ((2 * mu_p * mu_t + c1) * (2 * sig_pt + c2)) / \
           ((mu_p**2 + mu_t**2 + c1) * (sig_p**2 + sig_t**2 + c2))
    return float(ssim)

# ----------------------------
# Training
# ----------------------------
def find_images(root):
    exts = (".png", ".jpg", ".jpeg", ".tif", ".tiff")
    paths = []
    if os.path.isdir(root):
        for f in sorted(os.listdir(root)):
            if f.lower().endswith(exts):
                paths.append(os.path.join(root, f))
    return paths

def train(cfg):
    torch.manual_seed(42)
    np.random.seed(42)

    clear_paths = find_images(cfg["train"]["dataset_root"])
    if not clear_paths:
        raise RuntimeError(
            f"No clear images found in {cfg['train']['dataset_root']}. "
            "Place clear optical images there first."
        )
    print(f"Found {len(clear_paths)} clear images")

    split = int(0.8 * len(clear_paths))
    train_paths = clear_paths[:split]
    val_paths = clear_paths[split:] if split < len(clear_paths) else clear_paths[:1]

    train_ds = CloudRemovalDataset(
        train_paths, cfg["cloud"],
        patch_size=cfg["train"]["patch_size"],
        synth_pairs=cfg["train"]["synthetic_pairs"],
    )
    val_ds = CloudRemovalDataset(
        val_paths, cfg["cloud"],
        patch_size=cfg["train"]["patch_size"],
        synth_pairs=min(200, cfg["train"]["synthetic_pairs"]),
    )
    train_loader = DataLoader(train_ds, batch_size=cfg["train"]["batch_size"], shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=1, shuffle=False, num_workers=0)

    model = UNetCloudRemoval()
    param_count = sum(p.numel() for p in model.parameters())
    print(f"Model parameters: {param_count:,}")

    opt = optim.Adam(model.parameters(), lr=cfg["train"]["lr"])
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(opt, patience=3, factor=0.5)
    loss_fn = nn.MSELoss()

    os.makedirs(os.path.dirname(cfg["train"]["model_path"]), exist_ok=True)
    best_val_loss = float("inf")
    loss_history = []

    model.train()
    for epoch in range(cfg["train"]["epochs"]):
        epoch_loss = 0.0
        for cloudy, clear in tqdm(train_loader, desc=f"Epoch {epoch+1}/{cfg['train']['epochs']}"):
            opt.zero_grad()
            out = model(cloudy)
            loss = loss_fn(out, clear)
            loss.backward()
            opt.step()
            epoch_loss += loss.item()
        avg_train_loss = epoch_loss / len(train_loader)

        model.eval()
        val_loss = 0.0
        val_psnr = 0.0
        val_ssim = 0.0
        with torch.no_grad():
            for cloudy, clear in val_loader:
                out = model(cloudy)
                val_loss += loss_fn(out, clear).item()
                val_psnr += compute_psnr(out.numpy(), clear.numpy())
                val_ssim += compute_ssim(out.numpy(), clear.numpy())
        val_loss /= len(val_loader)
        val_psnr /= len(val_loader)
        val_ssim /= len(val_loader)
        model.train()

        scheduler.step(val_loss)

        loss_history.append({
            "train": avg_train_loss, "val": val_loss,
            "val_psnr": val_psnr, "val_ssim": val_ssim,
        })
        print(f"Epoch {epoch+1}/{cfg['train']['epochs']} | "
              f"Train: {avg_train_loss:.6f} | "
              f"Val: {val_loss:.6f} | "
              f"PSNR: {val_psnr:.2f} dB | "
              f"SSIM: {val_ssim:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), cfg["train"]["model_path"])

    loss_path = os.path.join(cfg["outputs"], "synthetic", "loss_history.npy")
    os.makedirs(os.path.dirname(loss_path), exist_ok=True)
    np.save(loss_path, loss_history)
    print(f"Loss history saved to {loss_path}")
    print(f"Best model saved to {cfg['train']['model_path']}")

# ----------------------------
# Inference
# ----------------------------
def infer(cfg):
    model_path = cfg["train"]["model_path"]
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No trained model found at {model_path}. Run training first.")

    model = UNetCloudRemoval()
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()

    input_path = cfg["infer"]["input_path"]
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")

    img = load_image(input_path)
    tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).float()
    with torch.no_grad():
        out = model(tensor).squeeze().permute(1, 2, 0).numpy()

    save_image(out, cfg["infer"]["output_path"])
    print(f"Saved cleaned image to {cfg['infer']['output_path']}")

    comparison = np.hstack([img, out])
    comp_path = cfg["infer"]["output_path"].replace(".png", "_comparison.png")
    save_image(comparison, comp_path)
    print(f"Comparison saved to {comp_path}")

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    CFG = load_config()
    if len(sys.argv) > 1 and sys.argv[1] == "infer":
        infer(CFG)
    else:
        train(CFG)
