"""Oscurece y enfría el repintado de la feria maldita (de ia_feria_maldita.py) y lo deja como base para mapas_pdf.py.
Uso: tools/.venv/bin/python tools/feria_maldita_color.py   (lee -raw.png, escribe -ia-sin-rejilla.png)"""
from pathlib import Path
import numpy as np
from PIL import Image
D = Path(__file__).resolve().parent.parent / "_originales/mapas"
im = np.array(Image.open(D / "feria-maldita-raw.png").convert("RGB"), np.float32) / 255
g = im.mean(2, keepdims=True)
im = g * 0.35 + im * 0.65
im = im ** 1.15
im = im * np.array([0.78, 0.74, 0.92])
H, W, _ = im.shape
y, x = np.mgrid[0:H, 0:W]; r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
im = im * np.clip(1.08 - 0.3 * r ** 1.8, 0.6, 1)[..., None]
lum = im.mean(2, keepdims=True); im = np.where(lum > 0.5, im * np.array([0.88, 0.86, 0.98]), im)
im = np.clip(im * 1.2, 0, 1)
Image.fromarray((im * 255).astype(np.uint8)).save(D / "feria-maldita-ia-sin-rejilla.png")
