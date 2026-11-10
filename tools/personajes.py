"""Paso 2: recorta personajes (fondo transparente con rembg) y saca retratos cuadrados.
Uso: tools/.venv/bin/python tools/personajes.py <escenas_dir> <salida_dir>
Cada entrada: escena, caja (x0,y0,x1,y1 en fracción de la imagen) donde está SOLO ese personaje."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import cv2
from rembg import remove, new_session

ESC, SAL = Path(sys.argv[1]), Path(sys.argv[2]); SAL.mkdir(parents=True, exist_ok=True)
PJ = {  # nombre: (escena, caja, retrato (cx, cy, lado) en fracción del recorte limpio)
    "glitch": ("diana-glitch", (0.38, 0.34, 0.76, 0.95)),
    "gart":   ("noria-gart",   (0.60, 0.30, 0.95, 0.96)),
    "zash":   ("carrusel-zash",(0.38, 0.62, 0.62, 0.98)),
    "mizzen": ("tienda-mizzen",(0.34, 0.33, 0.66, 0.66)),
}
BORRAR = {"glitch": [(0, 0, 0.11, 0.345)], "zash": [(0, 0, 0.075, 0.265)]}  # fracciones del recorte
BORRAR2 = {"glitch": [(0, 0, 0.10, 0.36), (0, 0, 0.085, 0.38), (0.08, 0.24, 0.17, 0.31), (0.03, 0.2, 0.13, 0.27)], "zash": [(0, 0, 0.065, 0.265), (0, 0.24, 0.07, 0.30)]}
sesion = new_session("isnet-general-use")
for n, (esc, (a, b, c, d)) in PJ.items():
    im = Image.open(ESC / f"{esc}.jpg").convert("RGB"); W, H = im.size
    rec = im.crop((int(a*W), int(b*H), int(c*W), int(d*H)))
    out = remove(rec, session=sesion, post_process_mask=True)
    a = np.array(out)
    # quedarse solo con el cuerpo principal: erosiona (separa lo que está pegado por poco), toma el mayor
    # componente, y recupera su forma con una dilatación limitada a la máscara original
    m = (a[..., 3] > 128).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))
    e = cv2.erode(m, k)
    nc, lab, st, _ = cv2.connectedComponentsWithStats(e)
    mayor = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    cuerpo = cv2.dilate((lab == mayor).astype(np.uint8), k) & m
    a[..., 3] = np.where(cuerpo > 0, a[..., 3], 0)
    if n == "mizzen":  # busto: difumina el borde inferior (el mostrador)
        h = a.shape[0]; y = np.arange(h)[:, None]
        a[..., 3] = (a[..., 3] * np.clip((h - y) / (0.12 * h), 0, 1)).astype(np.uint8)
    out = Image.fromarray(a)
    ys, xs = np.nonzero(a[..., 3] > 10)
    out = out.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    a = np.array(out); h, w = a.shape[:2]
    for x0, y0, x1, y1 in BORRAR.get(n, []):  # restos del fondo que se han quedado pegados
        a[int(y0*h):int(y1*h), int(x0*w):int(x1*w), 3] = 0
    ys, xs = np.nonzero(a[..., 3] > 10)
    out = Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    a = np.array(out); h, w = a.shape[:2]
    for x0, y0, x1, y1 in BORRAR2.get(n, []):  # segunda pasada, sobre el recorte ya ajustado
        a[int(y0*h):int(y1*h), int(x0*w):int(x1*w), 3] = 0
    nc, lab, st, _ = cv2.connectedComponentsWithStats((a[..., 3] > 10).astype(np.uint8))
    for c in range(1, nc):  # fuera los trozos sueltos pequeños
        if st[c, cv2.CC_STAT_AREA] < 0.03 * st[1:, cv2.CC_STAT_AREA].max(): a[lab == c, 3] = 0
    ys, xs = np.nonzero(a[..., 3] > 10)
    out = Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    if n == "glitch":  # restos oscuros del palo de la diana junto a la mano (ya en el recorte final)
        a = np.array(out); h, w = a.shape[:2]; r = a[int(.25*h):int(.345*h), int(.09*w):int(.15*w)]
        r[(r[..., :3].astype(int).sum(2) < 330), 3] = 0; out = Image.fromarray(a)
    out.save(SAL / f"{n}-bruto.png")
    print(n, out.size, flush=True)
