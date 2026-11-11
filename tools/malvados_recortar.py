"""Recorta (rembg) las versiones malvadas elegidas de los kobolds y crea retrato.
Uso: tools/.venv/bin/python tools/malvados_recortar.py glitch=2 gart=1 zash=3 mizzen=1   (nombre=semilla)
Salida: public/aventuras/la-feria-del-misterio/personajes/<n>-malvado.png y <n>-malvado-retrato.jpg"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import cv2
from rembg import remove, new_session

RAIZ = Path(__file__).resolve().parent.parent
ORI = RAIZ / "_originales/personajes/malvados"; SAL = RAIZ / "public/aventuras/la-feria-del-misterio/personajes"
RET = .36
ses = new_session("isnet-general-use")
for arg in sys.argv[1:]:
    n, s = arg.split("=")
    a = np.array(remove(Image.open(ORI / f"{n}-s{s}.png").convert("RGB"), session=ses, post_process_mask=True))
    m = (a[..., 3] > 128).astype(np.uint8)
    nc, lab, st, _ = cv2.connectedComponentsWithStats(m)
    a[..., 3] = np.where(lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]), a[..., 3], 0)
    ys, xs = np.nonzero(a[..., 3] > 10)
    im = Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    # igualar la altura con el original para que los muñecos escalen igual
    orig = Image.open(SAL / f"{n}.png"); k = orig.height / im.height
    im = im.resize((round(im.width * k), orig.height), Image.LANCZOS)
    im.save(SAL / f"{n}-malvado.png", optimize=True)
    al = np.array(im)[..., 3] > 10; h, w = al.shape
    lado = int(RET * h); top = al[: max(1, int(lado * .9))]
    cx = int(np.mean(np.nonzero(top)[1])) if top.any() else w // 2
    liz = Image.new("RGBA", (lado, lado), (0, 0, 0, 0)); liz.paste(im, (-(cx - lado // 2), 0))
    yy = np.linspace(0, 1, lado)[:, None, None]
    fondo = np.broadcast_to((np.array([38, 44, 82]) * (1 - yy) + np.array([20, 22, 40]) * yy).astype(np.uint8), (lado, lado, 3)).copy()
    r = Image.fromarray(fondo).convert("RGBA"); r.alpha_composite(liz)
    r.convert("RGB").resize((512, 512), Image.LANCZOS).save(SAL / f"{n}-malvado-retrato.jpg", quality=88)
    print(n, im.size, flush=True)
