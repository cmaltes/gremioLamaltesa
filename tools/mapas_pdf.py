"""Paso 5: PDFs de mapas a escala real (1 casilla = 25 mm) en mosaico A4 y A3, con la cuadrícula propia en vectorial.
Uso: tools/.venv/bin/python tools/mapas_pdf.py <slug> [id_mapa ...]  (conserva la rejilla de la IA, corregida: ver mapas_rejilla.py)
Salida: public/aventuras/<slug>/mapas/<id>-A4.pdf y -A3.pdf. Cada hoja solapa 1 casilla con la vecina."""
import io, math, sys, tempfile
from pathlib import Path
import pymupdf as fitz
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
from mapas_rejilla import procesar

SLUG = sys.argv[1] if len(sys.argv) > 1 else "la-feria-del-misterio"
DIR = Path(__file__).resolve().parent.parent / "public/aventuras" / SLUG / "mapas"
# id: (casillas ancho, casillas alto, paso aprox. de la rejilla de la IA en px)
# id: (paso aprox. de la rejilla de la IA en px, imagen base repintada sin rejilla o None). Las casillas se miden solas.
MAPAS = {"feria": (84, None), "feria-variante": (84, None), "encrucijada": (84, None), "cueva-oso-lechuza": (84, None), "bosque-emboscada": (172, "_originales/mapas/bosque-emboscada-ia-sin-rejilla.png")}
PAPEL = {"A4": (210, 297), "A3": (297, 420)}
MARGEN = 8            # mm mínimos sin imprimir
PX_CASILLA = 170      # resolución objetivo (≈170 ppp): se amplía con Lanczos solo lo que esté por debajo
pt = lambda mmv: mmv * 72 / 25.4
LETRAS = lambda i: (chr(65 + i) if i < 26 else "A" + chr(65 + i - 26))

def orientacion(papel, cols, rows):
    """elige apaisado o vertical según cuántas hojas hagan falta; devuelve (ancho_mm, alto_mm, c, r, tx, ty)."""
    mejor = None
    for w, h in (PAPEL[papel][::-1], PAPEL[papel]):
        c, r = int((w - 2 * MARGEN) // 25), int((h - 2 * MARGEN) // 25)
        tx = 1 if cols <= c else math.ceil((cols - 1) / (c - 1)); ty = 1 if rows <= r else math.ceil((rows - 1) / (r - 1))
        if mejor is None or tx * ty < mejor[4] * mejor[5]: mejor = (w, h, c, r, tx, ty)
    return mejor

def inicios(n, c, t):
    if t == 1: return [0]
    return [min(i * (c - 1), n - c) for i in range(t)]

def hacer(mid, cols, rows, p0, papel, limpio):
    w, h, c, r, tx, ty = orientacion(papel, cols, rows)
    xs, ys = inicios(cols, c, tx), inicios(rows, r, ty)
    pw, ph = limpio.width / cols, limpio.height / rows            # px por casilla (ya ampliado)
    doc = fitz.open(); n = 0
    for j, sy in enumerate(ys):
        for i, sx in enumerate(xs):
            n += 1
            cw, ch = min(c, cols - sx), min(r, rows - sy)         # casillas dibujadas en esta hoja
            pg = doc.new_page(width=pt(w), height=pt(h))
            ox, oy = (w - cw * 25) / 2, (h - ch * 25) / 2         # contenido centrado
            crop = limpio.crop((round(sx * pw), round(sy * ph), round((sx + cw) * pw), round((sy + ch) * ph)))
            b = io.BytesIO(); crop.save(b, "JPEG", quality=80); 
            pg.insert_image(fitz.Rect(pt(ox), pt(oy), pt(ox + cw * 25), pt(oy + ch * 25)), stream=b.getvalue())
            sh = pg.new_shape()
            sh.draw_rect(fitz.Rect(pt(ox), pt(oy), pt(ox + cw * 25), pt(oy + ch * 25))); sh.finish(color=(0, 0, 0), width=.5, fill=None)
            for (x, y, dx, dy) in ((ox, oy, -1, -1), (ox + cw * 25, oy, 1, -1), (ox, oy + ch * 25, -1, 1), (ox + cw * 25, oy + ch * 25, 1, 1)):   # marcas de corte
                sh.draw_line((pt(x + dx * 1), pt(y)), (pt(x + dx * 5), pt(y))); sh.draw_line((pt(x), pt(y + dy * 1)), (pt(x), pt(y + dy * 5)))
            sh.finish(color=(0, 0, 0), width=.6)
            sh.commit()
            for k in range(cw):                                     # letras de columna y números de fila
                pg.insert_text((pt(ox + k * 25 + 12.5) - fitz.get_text_length(LETRAS(sx + k), fontsize=6) / 2, pt(oy - 1.2)), LETRAS(sx + k), fontsize=6, color=(.2, .2, .2))
            for k in range(ch):
                pg.insert_textbox(fitz.Rect(pt(ox - 7), pt(oy + k * 25 + 10), pt(ox - 1.5), pt(oy + k * 25 + 16)), str(sy + k + 1), fontsize=7, align=2, color=(.2, .2, .2))
            ty0 = 4.2
            pg.insert_text((pt(MARGEN), pt(ty0 + 2.5)), f"{mid.replace('-', ' ').capitalize()} · hoja {n} de {tx * ty} · columnas {LETRAS(sx)}–{LETRAS(sx + cw - 1)}, filas {sy + 1}–{sy + ch} · {papel} al 100 %", fontsize=8, color=(.1, .1, .1))
            for jj in range(ty):                                    # mini-índice de hojas
                for ii in range(xs.__len__()):
                    rr = fitz.Rect(pt(w - MARGEN - 4 - (len(xs) - ii) * 3.2), pt(ty0 + jj * 3.2 - 1), pt(w - MARGEN - 4 - (len(xs) - ii) * 3.2 + 2.8), pt(ty0 + jj * 3.2 + 1.8))
                    pg.draw_rect(rr, color=(0, 0, 0), fill=(0, 0, 0) if (ii, jj) == (i, j) else None, width=.5)
            # regla de comprobación de 5 casillas (125 mm) y texto de escala
            ry = h - MARGEN + 1.5; x0 = MARGEN
            for k in range(5):
                pg.draw_rect(fitz.Rect(pt(x0 + k * 25), pt(ry), pt(x0 + (k + 1) * 25), pt(ry + 2.5)), color=(0, 0, 0), fill=(.85, .85, .85) if k % 2 == 0 else (1, 1, 1), width=.5)
            pg.insert_text((pt(x0 + 128), pt(ry + 2.3)), "125 mm = 5 casillas de 25 mm: mídelo para comprobar la escala", fontsize=7, color=(.1, .1, .1))
    out = DIR / f"{mid}-{papel}.pdf"; doc.save(out, deflate=True, garbage=3)
    print(f"→ {out.name}: {n} hojas ({tx}×{ty}), {cols}×{rows} casillas = {cols * 25}×{rows * 25} mm, {out.stat().st_size // 1024} KB")
    return n

if __name__ == "__main__":
    ids = sys.argv[2:] or list(MAPAS)
    for mid in ids:
        p0, base = MAPAS[mid]
        origen = DIR / f"{mid}.jpg"
        if base: origen = Path(__file__).resolve().parent.parent / "_originales/mapas" / f"{mid}-antes-arboles.jpg"   # la rejilla se mide en el original; el repintado va como base
        im, cols, rows, P, info = procesar(str(origen), str(Path(__file__).resolve().parent.parent / base) if base else None, p0)
        if base: im.save(DIR / f"{mid}.jpg", quality=90); im.resize((640, 640), Image.LANCZOS).save(DIR / f"{mid}-min.jpg", quality=82)
        print(mid, info)
        up = max(1, PX_CASILLA / P)
        limpio = im.resize((round(cols * P * up), round(rows * P * up)), Image.LANCZOS)
        for papel in PAPEL: hacer(mid, cols, rows, p0, papel, limpio)
