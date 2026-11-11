"""Recorta los héroes generados (rembg) y los pone sobre un fondo con el color de su clase: public/fichas/heroes/<clase>-<chico|chica>.jpg (640×800).
Uso: tools/.venv/bin/python tools/heroes.py            (elige la semilla de cada héroe en SEL, por defecto 1)"""
import re, sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image
from rembg import remove, new_session

RAIZ = Path(__file__).resolve().parent.parent
ORI, SAL = RAIZ / "_originales/heroes", RAIZ / "public/fichas/heroes"; SAL.mkdir(parents=True, exist_ok=True)
SEL = {(c, x): 2 for c in ("guerrero","barbaro","explorador","picaro","mago","clerigo","druida","bardo","monje","paladin") for x in ("chico","chica")}   # semilla elegida de cada héroe (la 2 salió mejor: colores propios, armas y trenzas en las chicas)
col = {m[1]: m[2] for m in re.findall(r"slug: '(\w+)'.*?color: '(#\w+)'", (RAIZ / "src/data/clases.ts").read_text())} if False else {}
for m in re.finditer(r"slug: '(\w+)'.*?color: '(#[0-9a-fA-F]{6})'", (RAIZ / "src/data/clases.ts").read_text()): col[m[1]] = m[2]
ses = new_session("isnet-general-use")
W, H = 640, 800
for f in sorted(ORI.glob("*-s*.png")):
    clase, sexo, s = re.match(r"(\w+)-(chico|chica)-s(\d+)", f.stem).groups()
    if int(s) != SEL.get((clase, sexo), 1): continue
    a = np.array(remove(Image.open(f).convert("RGB"), session=ses, post_process_mask=True))
    m = (a[..., 3] > 128).astype(np.uint8); nc, lab, st, _ = cv2.connectedComponentsWithStats(m)
    a[..., 3] = np.where(lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]), a[..., 3], 0)
    ys, xs = np.nonzero(a[..., 3] > 10)
    im = Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    esc = min((W * .92) / im.width, (H * .96) / im.height); im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    c = np.array([int(col[clase][i:i + 2], 16) for i in (1, 3, 5)], float)
    yy = np.linspace(0, 1, H)[:, None, None]; xx = np.linspace(-1, 1, W)[None, :, None]
    fondo = (c * (.55 + .35 * (1 - yy)) + 255 * .10 - 28 * xx ** 2).clip(0, 255).astype(np.uint8)   # degradado suave con el color de la clase
    fondo = np.broadcast_to(fondo, (H, W, 3)).copy()
    lienzo = Image.fromarray(fondo).convert("RGBA")
    lienzo.alpha_composite(im, ((W - im.width) // 2, H - im.height))   # apoyado abajo
    lienzo.convert("RGB").save(SAL / f"{clase}-{sexo}.jpg", quality=88); print(clase, sexo, "s", s, flush=True)
