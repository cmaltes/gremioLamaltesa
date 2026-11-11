"""Paso 4: muñecos de papel de pie (A4, 300 ppp, por delante y por detrás).
Uso: tools/.venv/bin/python tools/munecos.py <slug>
Salida: public/aventuras/<slug>/miniaturas/<slug>-munecos.pdf (+ -munecos-min.jpg)
Cada muñeco es una tira vertical: pestaña-peana trasera / figura de espaldas (volteada) / PLIEGUE por la cabeza /
figura de frente / pestaña-peana delantera. Se dobla por la cabeza, se pega por dentro y las dos pestañas se abren
en T: la huella de la peana mide 1 casilla (25 mm) o 2 (50 mm)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

SLUG = sys.argv[1] if len(sys.argv) > 1 else "la-feria-del-misterio"
DIR = Path(__file__).resolve().parent.parent / "public/aventuras" / SLUG
PERS, SAL = DIR / "personajes", DIR / "miniaturas"; SAL.mkdir(parents=True, exist_ok=True)
DPI = 300
mm = lambda v: round(v * DPI / 25.4)
W, H = mm(210), mm(297)
ALIADO = ENEMIGO = (150, 112, 45)   # un solo color neutro: no delata quién es aliado o enemigo
# archivo, nombre, altura de la figura (mm), casillas de peana, bando
MUNECOS = [
    ("alarico", "Alarico", 44, 1, ENEMIGO), ("glitch", "Glitch", 32, 1, ENEMIGO), ("gart", "Gart", 34, 1, ENEMIGO),
    ("zash", "Zash", 32, 1, ENEMIGO), ("mizzen", "Mizzen", 36, 1, ENEMIGO), ("oso-lechuza", "Oso Lechuza", 62, 2, ENEMIGO),
    ("aerion", "Aerion", 42, 1, ALIADO), ("fliflas", "Fliflas", 42, 1, ALIADO), ("guiverno", "Guiverno", 62, 2, ALIADO),
]
FUENTE = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
fn = lambda pt: ImageFont.truetype(FUENTE, round(pt * DPI / 72))
GRIS = (120, 120, 120)


def linea_disc(d, p0, p1, color=GRIS, trazo=mm(1.6), hueco=mm(1.2), w=3):
    (x0, y0), (x1, y1) = p0, p1
    n = max(abs(x1 - x0), abs(y1 - y0)); paso = trazo + hueco; t = 0
    while t < n:
        a, b = t / n, min(t + trazo, n) / n
        d.line((x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b), fill=color, width=w); t += paso


def tira(arch, nombre, h_mm, casillas, color, cartel=False):
    base = mm(25 * casillas); tab = base // 2                     # pestaña = media peana → huella cuadrada
    im = Image.open(arch if isinstance(arch, Path) else PERS / f"{arch}.png").convert("RGBA"); im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox())
    h = mm(h_mm); w = round(im.width * h / im.height)
    if w > mm(25 * casillas * 1.25):                              # no sobresalir demasiado de la peana
        w = mm(25 * casillas * 1.25); h = round(im.height * w / im.width)
    fig = im.resize((w, h), Image.LANCZOS)
    ancho = max(base, w + mm(4)); zona = h + mm(3)                  # zona de arte: figura + 3 mm de aire arriba
    alto = 2 * (zona + tab)
    t = Image.new("RGB", (ancho, alto), (250, 244, 228)); d = ImageDraw.Draw(t)
    fx = (ancho - w) // 2
    # arte: delante abajo del pliegue (cabeza arriba), detrás volteada arriba
    yf = tab + zona + zona - h                                      # pies abajo del bloque frontal
    yf = alto // 2 + mm(3) if False else alto // 2 + (zona - h) - 0
    pegar = lambda im2, y: t.paste(im2, (fx, y), im2)
    # frente: figura apoyada en el borde inferior de su zona (pies en alto - tab)
    pegar(fig, alto - tab - h)
    cart = mm(7)   # héroes (solo medio cuerpo): un cartel con el nombre tapa el corte y queda a propósito
    if cartel:
        d.rectangle((0, alto - tab - cart, ancho, alto - tab), fill=(150, 112, 45)); d.line((0, alto - tab - cart, ancho, alto - tab - cart), fill=(90, 66, 25), width=4)
        f0 = fn(7); tw0 = d.textlength(nombre, font=f0); d.text(((ancho - tw0) / 2, alto - tab - cart + (cart - mm(3)) / 2), nombre, font=f0, fill='white')
    # espalda: la misma figura reflejada respecto al pliegue; ligeramente oscurecida
    atras = ImageOps.flip(fig); atras = Image.eval(atras.convert("RGB"), lambda v: int(v * .85)).convert("RGBA"); atras.putalpha(ImageOps.flip(fig).getchannel("A"))
    pegar(atras, tab)
    if cartel: d.rectangle((0, tab, ancho, tab + cart), fill=(150, 112, 45)); d.line((0, tab + cart, ancho, tab + cart), fill=(90, 66, 25), width=4)
    # pestañas de color con el nombre
    for y0, y1 in ((0, tab), (alto - tab, alto)):
        d.rectangle((0, y0, ancho, y1), fill=color)
    x0 = (ancho - base) // 2
    for y0 in (0, alto - tab):
        d.rectangle((x0, y0, x0 + base, y0 + tab), fill=tuple(int(c * .8 + 255 * .2) for c in color))
    f = fn(7 if casillas == 1 else 9); tw = d.textlength(nombre, font=f)
    d.text(((ancho - tw) / 2, alto - tab + (tab - mm(3)) / 2 - mm(.5)), nombre, font=f, fill="white")
    d.text(((ancho - d.textlength(f"{nombre} (espalda)", font=fn(5.5))) / 2, mm(.8)), "", font=fn(5.5))
    # pliegues (discontinuos): por la cabeza y por los pies de cada lado
    mid = alto // 2
    linea_disc(d, (0, mid), (ancho, mid)); linea_disc(d, (0, tab), (ancho, tab)); linea_disc(d, (0, alto - tab), (ancho, alto - tab))
    d.rectangle((0, 0, ancho - 1, alto - 1), outline=(30, 30, 30), width=4)   # corte
    return t, ancho, alto


def hoja(titulo, grupo):
    pag = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(pag); mg = mm(10)
    d.text((mg, mm(8)), titulo, font=fn(15), fill=(30, 30, 30))
    d.text((mg, mm(16.5)), "Imprime al 100 %. Corta por el borde, dobla por las líneas discontinuas (la central, por la cabeza),\npega las dos mitades por dentro y abre las pestañas en T.", font=fn(7), fill=GRIS)
    tiras = sorted((tira(*m) for m in grupo), key=lambda x: -x[2])
    x, y, fila = mg, mm(29), 0
    for t, ancho, alto in tiras:
        if x + ancho > W - mg:
            x = mg; y += fila + mm(5); fila = 0
        pag.paste(t, (x, y)); x += ancho + mm(5); fila = max(fila, alto)
    # regla de comprobación
    ry = H - mm(16); d.text((mg, ry - mm(6)), "Regla: 5 casillas = 125 mm", font=fn(7), fill=GRIS)
    for i in range(5):
        d.rectangle((mg + i * mm(25), ry, mg + (i + 1) * mm(25), ry + mm(6)), outline=(30, 30, 30), fill=(235, 235, 235) if i % 2 == 0 else "white", width=3)
    return pag, y + fila


NOMBRES = {"guerrero": "Guerrero", "barbaro": "Bárbaro", "explorador": "Explorador", "picaro": "Pícaro", "mago": "Mago", "clerigo": "Clérigo", "druida": "Druida", "bardo": "Bardo", "monje": "Monje", "paladin": "Paladín"}
CUERPOS = Path(__file__).resolve().parent.parent / "public/fichas/heroes"
def heroes(sexo):   # los héroes jugadores: todos de 42 mm, peana de 1 casilla
    return [(CUERPOS / f"{c}-{sexo}-cuerpo.png", n, 42, 1, ALIADO, True) for c, n in NOMBRES.items() if (CUERPOS / f"{c}-{sexo}-cuerpo.png").exists()]

paginas = [("Muñecos · Pequeños y medianos (peana 1 casilla)", [m for m in MUNECOS if m[3] == 1]),
           ("Muñecos · Grandes (peana 2 casillas)", [m for m in MUNECOS if m[3] == 2])]
for sexo, tit in (("chico", "chicos"), ("chica", "chicas")):
    h = heroes(sexo)
    if h: paginas.append((f"Muñecos · Héroes jugadores, {tit} (peana 1 casilla)", h))
res = [hoja(t, g) for t, g in paginas]
imgs = [r[0] for r in res]
print("hojas:", len(imgs), "alto usado (mm):", [round(r[1] / mm(1)) for r in res])
imgs[0].save(SAL / f"{SLUG}-munecos.pdf", "PDF", resolution=DPI, save_all=True, append_images=imgs[1:])
for i, p in enumerate(imgs, 1):
    p.save(SAL / f"{SLUG}-munecos-{i}.png", dpi=(DPI, DPI), optimize=True)
m = imgs[0].copy(); m.thumbnail((700, 990)); m.save(SAL / f"{SLUG}-munecos-min.jpg", quality=85)
