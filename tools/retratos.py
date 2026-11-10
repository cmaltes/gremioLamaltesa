"""Paso 2 (cont.): con los recortes `<n>-bruto.png` crea el PNG final (máx. 1400 px de alto) y el retrato cuadrado JPG de 512 px.
Uso: tools/.venv/bin/python tools/retratos.py <dir_brutos> <salida_personajes>"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

BR, SAL = Path(sys.argv[1]), Path(sys.argv[2]); SAL.mkdir(parents=True, exist_ok=True)
LADO = {"glitch": .36, "gart": .40, "zash": .38, "mizzen": .78}  # lado del retrato como fracción del alto (busto: del ancho x1,0 más abajo)
for f in sorted(BR.glob("*-bruto.png")):
    n = f.name[:-10]; im = Image.open(f)
    if im.height > 1400: im = im.resize((round(im.width*1400/im.height), 1400), Image.LANCZOS)
    im.save(SAL / f"{n}.png", optimize=True)
    a = np.array(im)[..., 3] > 10; h, w = a.shape
    lado = int(LADO[n] * h); lado = min(lado, w if n != "mizzen" else max(w, lado))
    top = a[: max(1, int(lado*.9))]; xs = np.nonzero(top.any(0))[0]
    cx = int(np.mean(np.nonzero(top)[1])) if top.any() else w//2      # centro de masas de la parte alta (la cabeza)
    x0 = int(np.clip(cx - lado//2, -lado, w)); y0 = 0
    lienzo = Image.new("RGBA", (lado, lado), (0, 0, 0, 0)); lienzo.paste(im, (-x0, -y0))
    # fondo: degradado azul noche de la feria
    yy = np.linspace(0, 1, lado)[:, None, None]
    fondo = (np.array([38, 44, 82]) * (1 - yy) + np.array([20, 22, 40]) * yy).astype(np.uint8)
    fondo = np.broadcast_to(fondo, (lado, lado, 3)).copy()
    ret = Image.fromarray(fondo).convert("RGBA"); ret.alpha_composite(lienzo)
    ret.convert("RGB").resize((512, 512), Image.LANCZOS).save(SAL / f"{n}-retrato.jpg", quality=88)
    print(n, im.size, (SAL / f"{n}.png").stat().st_size // 1024, "KB")
