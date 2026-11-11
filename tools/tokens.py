"""Paso 3: hoja de tokens redondos (25 mm y 50 mm) con los retratos de los PNJ.
Uso: tools/.venv/bin/python tools/tokens.py <slug>
Salida: public/aventuras/<slug>/miniaturas/<slug>-tokens.{png,pdf} (+ miniatura -min.jpg)
A4 a 300 ppp = 2480 x 3508 px. 1 mm = 300/25,4 px. El PDF sale a esa resolución, así que imprime a 100 %."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SLUG = sys.argv[1] if len(sys.argv) > 1 else "la-feria-del-misterio"
RAIZ = Path(__file__).resolve().parent.parent
DIR = RAIZ / "public/aventuras" / SLUG
PERS = DIR / "personajes"
SAL = DIR / "miniaturas"; SAL.mkdir(parents=True, exist_ok=True)
DPI = 300
mm = lambda v: round(v * DPI / 25.4)
W, H = mm(210), mm(297)

# Un único color de borde para todos: el color no debe delatar quién es aliado o enemigo (spoiler).
ALIADO = ENEMIGO = (150, 112, 45)   # latón
# (archivo, nombre, diámetro mm, bando)
TOKENS = [
    ("alarico", "Alarico", 25, ENEMIGO), ("glitch", "Glitch", 25, ENEMIGO), ("gart", "Gart", 25, ENEMIGO),
    ("zash", "Zash", 25, ENEMIGO), ("mizzen", "Mizzen", 25, ENEMIGO),
    ("aerion", "Aerion", 25, ALIADO), ("fliflas", "Fliflas", 25, ALIADO),
    ("guiverno", "Guiverno", 50, ALIADO), ("oso-lechuza", "Oso Lechuza", 50, ENEMIGO),
]
FUENTE = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
fn = lambda pt: ImageFont.truetype(FUENTE, round(pt * DPI / 72))


def token(arch, d_mm, color):
    # arch: nombre de un PNJ (retrato 512 px) o ruta a la imagen de ficha de un héroe (se recorta el cuadrado de la cabeza)
    """Disco de d_mm exactos: borde de latón de 2,5 mm (o 4 mm en los grandes) y retrato dentro."""
    d = mm(d_mm); S = 4                       # sobremuestreo para bordes suaves
    borde = mm(2.5 if d_mm <= 25 else 4)
    if isinstance(arch, Path): im = Image.open(arch).convert("RGB"); im = im.crop((0, 0, im.width, im.width))
    else: im = Image.open(PERS / f"{arch}-retrato.jpg").convert("RGB")
    lienzo = Image.new("RGBA", (d * S, d * S), (0, 0, 0, 0))
    m = Image.new("L", (d * S, d * S), 0); ImageDraw.Draw(m).ellipse((0, 0, d * S - 1, d * S - 1), fill=255)
    lienzo.paste(Image.new("RGBA", (d * S, d * S), color + (255,)), (0, 0), m)
    di = (d - 2 * borde) * S
    ret = im.resize((di, di), Image.LANCZOS).convert("RGBA")
    mi = Image.new("L", (di, di), 0); ImageDraw.Draw(mi).ellipse((0, 0, di - 1, di - 1), fill=255)
    lienzo.paste(ret, (borde * S, borde * S), mi)
    aro = ImageDraw.Draw(lienzo)               # fino aro claro entre borde y retrato
    aro.ellipse((borde * S, borde * S, d * S - borde * S - 1, d * S - borde * S - 1), outline=(255, 255, 255, 230), width=S * 3)
    return lienzo.resize((d, d), Image.LANCZOS)


def centrar(dib, texto, cx, y, f, fill=(30, 30, 30)):
    w = dib.textlength(texto, font=f); dib.text((cx - w / 2, y), texto, font=f, fill=fill)


def hacer_hoja(titulo, tokens, ajuste):
    hoja = Image.new("RGB", (W, H), "white"); dib = ImageDraw.Draw(hoja)
    margen = mm(12)
    dib.text((margen, mm(10)), titulo, font=fn(15), fill=(30, 30, 30))
    dib.text((margen, mm(18.5)), "Imprime al 100 % (sin «ajustar a página»). Recorta por la línea gris fina.", font=fn(8), fill=(90, 90, 90))
    huecoy = mm(8); sep = mm(6); y = mm(28)
    for grupo in sorted({t[2] for t in tokens}, reverse=True):
        x = margen; fila_h = 0
        for arch, nombre, d_mm, color in [t for t in tokens if t[2] == grupo]:
            d = mm(d_mm)
            if x + d > W - margen:
                x = margen; y += fila_h + huecoy + sep; fila_h = 0
            t = token(arch, d_mm, color)
            hoja.paste(t, (x, y), t)
            dib.ellipse((x, y, x + d, y + d), outline=(140, 140, 140), width=2)   # línea de corte exacta
            centrar(dib, nombre, x + d // 2, y + d + mm(1.5), fn(8 if d_mm <= 25 else 10))
            x += d + sep; fila_h = max(fila_h, d)
        y += fila_h + huecoy + sep + mm(4)
    ry = H - mm(22)
    dib.text((margen, ry - mm(7)), "Comprueba la escala: esta regla mide 125 mm (5 casillas de 25 mm).", font=fn(8), fill=(90, 90, 90))
    for i in range(5):
        dib.rectangle((margen + i * mm(25), ry, margen + (i + 1) * mm(25), ry + mm(8)), outline=(30, 30, 30), fill=(235, 235, 235) if i % 2 == 0 else "white", width=3)
        centrar(dib, "25", margen + i * mm(25) + mm(12.5), ry + mm(1.5), fn(8))
    return hoja

NOMBRES = {"guerrero": "Guerrero", "barbaro": "Bárbaro", "explorador": "Explorador", "picaro": "Pícaro", "mago": "Mago", "clerigo": "Clérigo", "druida": "Druida", "bardo": "Bardo", "monje": "Monje", "paladin": "Paladín"}
NOMBRES_F = {"guerrero": "Guerrera", "barbaro": "Bárbara", "explorador": "Exploradora", "picaro": "Pícara", "mago": "Maga", "clerigo": "Clériga", "druida": "Druida", "bardo": "Barda", "monje": "Monja", "paladin": "Paladina"}
HEROES = [(RAIZ / f"public/fichas/heroes/{c}-{x}.jpg", (NOMBRES_F[c] if x == "chica" else n), 25, ALIADO) for c, n in NOMBRES.items() for x in ("chico", "chica")]
titulo = "Tokens · La Feria del Misterio" if SLUG == "la-feria-del-misterio" else "Tokens · " + SLUG.replace("-", " ").capitalize()
h1 = hacer_hoja(titulo, TOKENS, None)
h2 = hacer_hoja("Tokens · Héroes (chicos y chicas)", HEROES, None) if all(t[0].exists() for t in HEROES) else None
hoja = h1
hoja.save(SAL / f"{SLUG}-tokens.png", dpi=(DPI, DPI), optimize=True)
hoja.save(SAL / f"{SLUG}-tokens.pdf", "PDF", resolution=DPI, save_all=bool(h2), append_images=[h2] if h2 else [])
if h2: h2.save(SAL / f"{SLUG}-tokens-heroes.png", dpi=(DPI, DPI), optimize=True)
mini = hoja.copy(); mini.thumbnail((700, 990)); mini.save(SAL / f"{SLUG}-tokens-min.jpg", quality=85)
print("→", SAL, [p.name for p in sorted(SAL.iterdir())])
