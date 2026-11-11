"""Quita el reborde claro de los recortes de personajes y rehace sus retratos.
Uso: tools/.venv/bin/python tools/pulir_bordes.py nombre ...   (p. ej. glitch zash-malvado)
Trabaja sobre public/aventuras/la-feria-del-misterio/personajes/<nombre>.png y <nombre>-retrato.jpg"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent)); from defringe import limpiar

SAL = Path(__file__).resolve().parent.parent / "public/aventuras/la-feria-del-misterio/personajes"
RET = {"alarico": .36, "aerion": .32, "fliflas": .36, "guiverno": .62, "oso-lechuza": .68, "glitch": .36, "gart": .40, "zash": .38, "mizzen": .36}
for n in sys.argv[1:]:
    im = limpiar(Image.open(SAL / f"{n}.png"), 2); im.save(SAL / f"{n}.png", optimize=True)
    al = np.array(im)[..., 3] > 10; h, w = al.shape
    lado = int(RET.get(n.replace("-malvado", ""), .36) * h); top = al[: max(1, int(lado * .9))]
    cx = int(np.mean(np.nonzero(top)[1])) if top.any() else w // 2
    liz = Image.new("RGBA", (lado, lado), (0, 0, 0, 0)); liz.paste(im, (-(cx - lado // 2), 0))
    yy = np.linspace(0, 1, lado)[:, None, None]
    fondo = np.broadcast_to((np.array([38, 44, 82]) * (1 - yy) + np.array([20, 22, 40]) * yy).astype(np.uint8), (lado, lado, 3)).copy()
    r = Image.fromarray(fondo).convert("RGBA"); r.alpha_composite(liz)
    r.convert("RGB").resize((512, 512), Image.LANCZOS).save(SAL / f"{n}-retrato.jpg", quality=88); print(n)
