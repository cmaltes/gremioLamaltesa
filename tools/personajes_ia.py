"""Recorta (rembg) y crea retratos de los personajes generados con el modelo local.
Uso: tools/.venv/bin/python tools/personajes_ia.py <originales_dir> <salida_personajes>"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import cv2
from rembg import remove, new_session

ORI, SAL = Path(sys.argv[1]), Path(sys.argv[2]); SAL.mkdir(parents=True, exist_ok=True)
PJ = {"alarico": "alarico1", "aerion": "aerion1", "fliflas": "fliflasv2_2", "guiverno": "guivernov2_2", "oso-lechuza": "osov2_2"}
RET = {"alarico": .36, "aerion": .32, "fliflas": .36, "guiverno": .62, "oso-lechuza": .68}
ses = new_session("isnet-general-use")
for n, f in PJ.items():
    a = np.array(remove(Image.open(ORI / f"{f}.png").convert("RGB"), session=ses, post_process_mask=True))
    m = (a[..., 3] > 128).astype(np.uint8)
    nc, lab, st, _ = cv2.connectedComponentsWithStats(m)
    a[..., 3] = np.where(lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]), a[..., 3], 0)
    ys, xs = np.nonzero(a[..., 3] > 10)
    im = Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    if im.height > 1400: im = im.resize((round(im.width * 1400 / im.height), 1400), Image.LANCZOS)
    im.save(SAL / f"{n}.png", optimize=True)
    al = np.array(im)[..., 3] > 10; h, w = al.shape
    lado = int(RET[n] * h); top = al[: max(1, int(lado * .9))]
    cx = int(np.mean(np.nonzero(top)[1])) if top.any() else w // 2
    x0 = cx - lado // 2
    liz = Image.new("RGBA", (lado, lado), (0, 0, 0, 0)); liz.paste(im, (-x0, 0))
    yy = np.linspace(0, 1, lado)[:, None, None]
    fondo = np.broadcast_to((np.array([38, 44, 82]) * (1 - yy) + np.array([20, 22, 40]) * yy).astype(np.uint8), (lado, lado, 3)).copy()
    r = Image.fromarray(fondo).convert("RGBA"); r.alpha_composite(liz)
    r.convert("RGB").resize((512, 512), Image.LANCZOS).save(SAL / f"{n}-retrato.jpg", quality=88)
    print(n, im.size, flush=True)
