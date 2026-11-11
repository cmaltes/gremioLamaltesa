"""Quita el reborde claro (resto del fondo) de recortes PNG con transparencia.
Uso: tools/.venv/bin/python tools/defringe.py [-n PX] archivo.png ...
Erosiona la silueta PX píxeles (por defecto 2), repinta el borde con el color del interior
(convolución normalizada) y suaviza el alfa para que no queden dientes."""
import sys
import numpy as np, cv2
from PIL import Image

def limpiar(im, px=2):
    a = np.array(im.convert("RGBA")); al = a[..., 3].astype(np.float32) / 255
    m = (al > .5).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * px + 1, 2 * px + 1))
    nucleo = cv2.erode(m, k)
    rgb = a[..., :3].astype(np.float32); w = nucleo.astype(np.float32)[..., None]
    num = cv2.GaussianBlur(rgb * w, (0, 0), 3); den = cv2.GaussianBlur(w, (0, 0), 3)[..., None] if False else cv2.GaussianBlur(nucleo.astype(np.float32), (0, 0), 3)[..., None]
    rel = num / np.maximum(den, 1e-4)
    banda = cv2.dilate(nucleo, k) == 1  # zona del borde original: color del interior
    zona = (m > 0) & (cv2.erode(m, k) == 0) | ~(nucleo > 0)
    rgb = np.where(zona[..., None] & (den > 1e-3), rel, rgb)
    nuevo = cv2.GaussianBlur(nucleo.astype(np.float32), (0, 0), .8)
    nuevo = np.where(nuevo > .02, np.minimum(nuevo * 1.15, 1), 0)
    out = np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), (nuevo * 255).astype(np.uint8)])
    return Image.fromarray(out)

if __name__ == "__main__":
    args = sys.argv[1:]; px = 2
    if args[:1] == ["-n"]: px = int(args[1]); args = args[2:]
    for f in args:
        limpiar(Image.open(f), px).save(f, optimize=True); print(f)
