import numpy as np
import cv2
import os

output_dir = os.path.join(os.path.dirname(__file__), "inputs", "clear_images")
os.makedirs(output_dir, exist_ok=True)

def make_gradient(w, h, direction):
    x = np.linspace(0, 1, w)
    y = np.linspace(0, 1, h)
    xx, yy = np.meshgrid(x, y)
    if direction == "vertical":
        return np.stack([xx]*3, axis=-1)
    elif direction == "horizontal":
        return np.stack([yy]*3, axis=-1)
    elif direction == "diagonal":
        return np.stack([(xx+yy)/2]*3, axis=-1)
    return np.stack([xx*yy]*3, axis=-1)

patterns = [
    ("gradient_vertical", lambda: make_gradient(256, 256, "vertical")),
    ("gradient_horizontal", lambda: make_gradient(256, 256, "horizontal")),
    ("gradient_diagonal", lambda: make_gradient(256, 256, "diagonal")),
    ("checkerboard", lambda: np.where(
        (np.indices((256,256)).sum(axis=0)//32) % 2 == 0, 0.8, 0.2
    ).astype(np.float32)[..., None] * np.ones((256, 256, 3), np.float32)),
    ("smooth_noise", lambda: cv2.GaussianBlur(
        np.random.RandomState(42).rand(256, 256, 3).astype(np.float32),
        (31, 31), 0)),
]

for name, gen_fn in patterns:
    img = gen_fn()
    img = np.clip(img, 0, 1)
    img_uint8 = (img * 255).astype(np.uint8)
    path = os.path.join(output_dir, f"{name}.png")
    cv2.imwrite(path, img_uint8)
    print(f"Created {name}.png")

print(f"\nCreated {len(patterns)} clear images in {output_dir}")
