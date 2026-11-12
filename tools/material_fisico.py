"""Fase 3: material físico imprimible de «La Feria del Misterio» (cartas de objeto, acertijos, tarjetas de preguntas).
Genera HTML y lo imprime con Chrome a PDF A4 (imprimir al 100 %). Dorsos ya reflejados para imprimir a doble cara (borde largo).
Uso: python tools/material_fisico.py     (necesita google-chrome; para las miniaturas, pymupdf del venv)
Salida: public/aventuras/la-feria-del-misterio/material/*.pdf + miniaturas *-min.jpg"""
import html, subprocess, tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAL = RAIZ / "public/aventuras/la-feria-del-misterio/material"
SAL.mkdir(parents=True, exist_ok=True)
CHROME = "google-chrome"
e = html.escape

CSS = """
@page { size: A4; margin: 0 }
* { box-sizing: border-box; margin: 0; padding: 0 }
body { font-family: 'Noto Serif','DejaVu Serif',serif; color: #2b2233; -webkit-print-color-adjust: exact; print-color-adjust: exact }
.pag { width: 210mm; height: 297mm; position: relative; page-break-after: always; overflow: hidden }
.pag:last-child { page-break-after: auto }
.rejilla { position: absolute; left: 15mm; top: 23.5mm; display: grid }
.nota { position: absolute; left: 15mm; top: 8mm; font-size: 8pt; color: #777 }
.pie { position: absolute; left: 15mm; bottom: 7mm; font-size: 7.5pt; color: #777 }
.corte { border: .25mm dashed #aaa }
/* cartas de objeto 90 x 125 */
.carta { width: 90mm; height: 125mm; padding: 4mm; border: .25mm dashed #aaa }
.marco { height: 100%; border: 1.2mm double #9a6f1d; border-radius: 4mm; padding: 5mm 5mm; display: flex; flex-direction: column; align-items: center; text-align: center }
.frente { background: #fbf3de }
.dorso { background: #efe8f7 }
.tipo { font-size: 7.5pt; letter-spacing: .15em; text-transform: uppercase; color: #9a6f1d }
.dibujo { width: 46mm; height: 46mm; border-radius: 50%; background: radial-gradient(#fff8e0, #ecd9a2); border: 1mm solid #9a6f1d; display: flex; align-items: center; justify-content: center; font-size: 30mm; margin: 4mm 0 }
.nombre { font-size: 16pt; font-weight: 700; color: #4a2c6e; line-height: 1.15 }
.desc { font-size: 10.5pt; line-height: 1.35; margin-top: 4mm }
.precio { margin-top: auto; font-size: 10pt; font-weight: 700; color: #9a6f1d }
.cartel-txt { font-size: 13pt; line-height: 1.3; font-weight: 700; color: #6b3d00; margin-top: 4mm }
.dorso .cab { font-size: 12pt; font-weight: 700; color: #4a2c6e; margin-bottom: 2mm }
.tirada { font-size: 9pt; background: #4a2c6e; color: #fff; border-radius: 3mm; padding: 1.2mm 3mm; margin: 2mm 0 3mm }
.txt { font-size: 10.5pt; line-height: 1.35; text-align: left; font-style: italic }
.sub { font-size: 8.5pt; color: #4a2c6e; font-weight: 700; margin: 3mm 0 1mm; align-self: flex-start }
/* tarjetas de preguntas 90 x 50 */
.preg { width: 90mm; height: 50mm; padding: 3mm; border: .25mm dashed #aaa }
.preg .marco { padding: 3mm; justify-content: center }
.preg .q { font-size: 12.5pt; font-weight: 700; color: #4a2c6e; line-height: 1.25 }
.preg .r { font-size: 20pt; font-weight: 700; color: #4a2c6e }
.preg .n { font-size: 8pt; color: #9a6f1d; margin-bottom: 2mm }
/* diana */
.diana { position: absolute; left: 15mm; top: 28mm; width: 180mm; height: 180mm }
.tit { position: absolute; left: 0; width: 210mm; text-align: center; font-size: 22pt; font-weight: 700; color: #4a2c6e; top: 14mm }
.sol { position: absolute; left: 15mm; right: 15mm; top: 218mm; font-size: 11pt; line-height: 1.5 }
/* tiras de la noria y del carrusel */
.tira { width: 180mm; height: 29mm; border: .25mm dashed #aaa; display: flex; align-items: center; gap: 5mm; padding: 2mm 5mm }
.tira .et { width: 30mm; font-size: 8pt; color: #9a6f1d; font-weight: 700; text-align: center }
.tira .verso { flex: 1; font-size: 14pt; font-style: italic; color: #3a2a1a; line-height: 1.25 }
.orden { width: 11mm; height: 11mm; border-radius: 50%; background: #4a2c6e; color: #fff; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 11pt; font-style: normal }
.tira.carr { height: 44mm }
.tira.carr .pal { flex: 1; text-align: center; font-size: 38pt; font-weight: 700; letter-spacing: .2em; color: #d9d2c3 }
.tira.carr .ant { width: 50mm; text-align: center; font-size: 11pt; color: #4a2c6e; font-weight: 700 }
"""


def doc(paginas):
    return f"<!doctype html><html lang='es'><meta charset='utf-8'><style>{CSS}</style><body>{''.join(paginas)}</body></html>"


def pagina(cuerpo, nota="", pie=""):
    return f"<div class='pag'>{'<div class=nota>'+e(nota)+'</div>' if nota else ''}{cuerpo}{'<div class=pie>'+e(pie)+'</div>' if pie else ''}</div>"


def reflejar(items, cols):
    """Reordena para el dorso: invierte las columnas de cada fila (impresión a doble cara por el borde largo)."""
    out = []
    for i in range(0, len(items), cols):
        fila = items[i:i + cols]
        fila += [""] * (cols - len(fila))
        out += fila[::-1]
    return out


def rejilla(items, cols, w, h):
    return f"<div class='rejilla' style='grid-template-columns:repeat({cols},{w}mm);grid-auto-rows:{h}mm'>{''.join(items)}</div>"


# ---------- cartas de objeto ----------
def frente(c):
    cuerpo = f"<div class=tipo>{e(c['tipo'])}</div><div class=dibujo>{c['emoji']}</div><div class=nombre>{e(c['nombre'])}</div><div class=desc>{e(c['frente'])}</div>"
    if c.get("precio"):
        cuerpo += f"<div class=precio>{e(c['precio'])}</div>"
    return f"<div class='carta'><div class='marco frente'>{cuerpo}</div></div>"


def frente_cartel(c):
    cuerpo = (f"<div class=tipo>Festival de los Mil Velos</div><div class=dibujo>{c['emoji']}</div>"
              f"<div class=cartel-txt>¡Ven y juega!<br>Premios para valientes, acertijos para curiosos y mil luces que brillan sin vela.<br><br>Entrada: una sonrisa.<br>Cierre: cuando se apaguen las farolas.</div>")
    return f"<div class='carta'><div class='marco frente'>{cuerpo}</div></div>"


def dorso(c):
    cuerpo = f"<div class=tipo>{e(c['nombre'])}</div><div class=cab>{e(c['dorso_titulo'])}</div>"
    if c.get("tirada"):
        cuerpo += f"<div class=tirada>{e(c['tirada'])}</div>"
    for sub, txt in c["dorso"]:
        if sub:
            cuerpo += f"<div class=sub>{e(sub)}</div>"
        cuerpo += f"<div class=txt>{e(txt)}</div>"
    return f"<div class='carta'><div class='marco dorso'>{cuerpo}</div></div>"


VACIA = "<div class='carta' style='border:none'></div>"

POCION = dict(nombre="Poción Solvente Místico", emoji="🧪", tipo="Objeto", tirada="Inteligencia (arcanos) · DC 13",
              frente="Una poción verde que huele a hierbabuena. La etiqueta está borrosa y no se entiende.",
              dorso_titulo="Si superas la tirada, dale la vuelta",
              dorso=[("", "Es un frasquito de líquido verde que burbujea suavemente. Reconoces el brillo: es un solvente místico, un remedio contra la piedra mágica. En la etiqueta, con letra diminuta, se lee: «Si ves estatua, gris y fría, / devuélvele pronto su día». Un sorbo, o un chorrito sobre quien se haya vuelto de piedra, lo devuelve a la normalidad. Solo alcanza para una persona.")])
MAPA = dict(nombre="Mapa Escondido", emoji="🗺️", tipo="Objeto", tirada="Sabiduría (supervivencia) · DC 13",
            frente="Un mapa lleno de rayas y dibujos de búhos. Una línea de puntos sale de la feria hacia el bosque, pero no sabéis a dónde lleva.",
            dorso_titulo="Si superas la tirada, dale la vuelta",
            dorso=[("", "Entre los garabatos reconoces una roca con forma de búho en mitad del bosque y una línea de puntos que sale de la feria. Es el camino a la Boca del Búho: con este mapa no os perderéis. Junto a la roca hay dibujadas unas garras enormes… quizá allí viva algo que no quiere visitas.")])
PERGAMINO = dict(nombre="Pergamino de Dormir", emoji="📜", tipo="Objeto", tirada="Inteligencia (arcanos) · DC 13",
                 frente="La tinta plateada se mueve sola y huele a lavanda. Parece un hechizo, pero no sabéis cuál.",
                 dorso_titulo="Si superas la tirada, dale la vuelta",
                 dorso=[("", "Las letras plateadas brillan al mirarlas: es un hechizo de Sueño. Si se lee en voz alta señalando a un enemigo, los que tengan pocas fuerzas caen dormidos un buen rato. Solo sirve una vez: al terminar, el pergamino se convierte en polvo.")])
LLAVE = dict(nombre="Llave del Cofre del Tesoro", emoji="🗝️", tipo="Objeto", tirada="Inteligencia (investigación)",
             frente="Una llave dorada muy brillante. Sirve para abrir algo.",
             dorso_titulo="Según tu tirada, dale la vuelta",
             dorso=[("Si sacas 13 o más", "Es una llave dorada con un búho grabado en el mango, de un cofre pequeño y antiguo. Pesa más de lo normal."),
                    ("Si sacas 16 o más (además)", "Mirando de cerca el extremo de la llave ves un polvo gris pegado. Huele a piedra mojada: es polvo de petrificación. El cofre que abra esta llave puede convertir en estatua a quien lo abra. Convendría tener un remedio a mano…")])
DAGA = dict(nombre="Daga Mágica de Cocina", emoji="🍴", tipo="Baratija de Mizzen", precio="1 PO",
            frente="Un tenedor enorme que brilla como una estrella pequeña.",
            dorso_titulo="Tuya por 1 PO", dorso=[("", "Mizzen te entrega un tenedor enorme que brilla como una estrella pequeña. Al clavarlo en una manzana, ¡la manzana hace «¡ñam, ñam!» y se corta sola en trocitos! No sirve para pelear, pero ¡qué elegante para la cena! Y en la oscuridad alumbra como una vela.")])
ORBE = dict(nombre="Orbe del Vidente", emoji="🔮", tipo="Baratija de Mizzen", precio="3 PO",
            frente="Una bola de cristal muy seria y muy fría. Dice que dentro vive una predicción secretísima.",
            dorso_titulo="Tuya por 3 PO", dorso=[("", "Es una bola de cristal muy seria y muy fría. Al mirar dentro solo ves tu propia cara, enorme y un poco torcida. Mizzen susurra: «Dentro vive una predicción secretísima… cuando la encuentres, ¡me avisas!». Seguro que da buena suerte, o al menos mucha risa.")])
BOTAS = dict(nombre="Botas de Siete Leguas", emoji="🥾", tipo="Baratija de Mizzen", precio="5 PO",
             frente="Una bota roja con alas bordadas. Solo hay una.",
             dorso_titulo="Tuya por 5 PO", dorso=[("", "Es una bota roja con alas bordadas que te queda enorme. Al ponértela, ¡das un salto gigante! Pero como solo hay una… ¡giras y giras en círculos hasta marearte! Con la otra bota sería otra historia.")])
ESCAMA = dict(nombre="Escama de Aerion", emoji="🐉", tipo="Premio del Druida", tirada="",
              frente="Una escama verde, muy suave y caliente. Late un poquito, como un corazón pequeño.",
              dorso_titulo="Cómo se usa", dorso=[("", "Una sola vez, en el combate final, quien la tenga puede recuperar 1d6 + 2 vidas como acción adicional.")])
CARTEL = dict(nombre="Cartel del Festival", emoji="🪧", tipo="", tirada="Sabiduría (percepción) · DC 13",
              dorso_titulo="Si superas la tirada, dale la vuelta",
              dorso=[("", "Las letras doradas se mueven despacio, como si respirasen. Al girar el cartel hacia la feria, brilla más fuerte; hacia el bosque, se apaga. Es un cartel hechizado que lleva a quien lo tiene hasta el festival.")])
LLAVE_JAULA = dict(nombre="Llave de la Jaula", emoji="🗝️", tipo="Objeto", tirada="Inteligencia (investigación) · DC 8",
                   frente="Una llave pequeña de hierro oscuro, con un dragón grabado en el mango.",
                   dorso_titulo="Si superas la tirada, dale la vuelta",
                   dorso=[("", "Es una llave pequeña de hierro oscuro con un dragón grabado en el mango. Seguro que abre la jaula de la Bestia.")])
CARTA = dict(nombre="Carta sellada", emoji="✉️", tipo="Hallazgo", tirada="",
             frente="Una carta cerrada con un sello de velo dorado. Huele a perfume viejo.",
             dorso_titulo="La carta dice…",
             dorso=[("", "«Silas: la feria ya está montada. Mantén encendida la última farola hasta que yo llegue. No me falles otra vez.»"),
                    ("Firmado", "la Dama de los Mil Velos")])


def pares(cartas, hechas_con=frente):
    """Devuelve páginas de frentes y dorsos (4 por página)."""
    pags = []
    for i in range(0, len(cartas), 4):
        grupo = cartas[i:i + 4]
        fr = [hechas_con(c) if c is not CARTEL else frente_cartel(c) for c in grupo]
        do = [dorso(c) for c in grupo]
        fr += [VACIA] * (4 - len(fr)); do += [VACIA] * (4 - len(do))
        pags.append(pagina(rejilla(fr, 2, 90, 125), "Frentes · imprime al 100 % y recorta por las líneas"))
        pags.append(pagina(rejilla(reflejar(do, 2), 2, 90, 125), "Dorsos · imprime a doble cara (borde largo) o pega cada dorso detrás de su frente"))
    return pags


def cartel_x4():
    c = CARTEL
    fr = [frente_cartel(c)] * 4
    do = [dorso(c)] * 4
    return [pagina(rejilla(fr, 2, 90, 125), "Cartel del Festival · un cartel por héroe (imprime dos veces si sois 5)"),
            pagina(rejilla(reflejar(do, 2), 2, 90, 125), "Dorsos del cartel")]


# ---------- acertijos ----------
LETRAS = ["R", "D", "E", "P", "A", "I"]
ORDEN = {"P": 1, "I": 2, "E": 3, "D": 4, "R": 5, "A": 6}


def svg_diana(master):
    import math
    cx = cy = 90
    s = ["<svg class='diana' viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'>"]
    for r, col in [(88, "#4a2c6e"), (70, "#efe8f7"), (52, "#9a6f1d"), (34, "#fbf3de")]:
        s.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='{col}' stroke='#2b2233' stroke-width='.6'/>")
    s.append(f"<circle cx='{cx}' cy='{cy}' r='12' fill='#6fb34a' stroke='#2b2233' stroke-width='.6'/><circle cx='{cx}' cy='{cy}' r='4' fill='#fff'/>")
    for i, L in enumerate(LETRAS):
        a = math.radians(-90 + i * 60)
        x, y = cx + 61 * math.cos(a), cy + 61 * math.sin(a)
        s.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='10.5' fill='#fff' stroke='#2b2233' stroke-width='.8'/>"
                 f"<text x='{x:.1f}' y='{y+5.2:.1f}' text-anchor='middle' font-size='15' font-weight='700' font-family='DejaVu Serif,serif' fill='#4a2c6e'>{L}</text>")
        if master:
            s.append(f"<circle cx='{x+8:.1f}' cy='{y-8:.1f}' r='4.2' fill='#c0392b'/><text x='{x+8:.1f}' y='{y-6.4:.1f}' text-anchor='middle' font-size='5.5' font-weight='700' fill='#fff' font-family='DejaVu Sans,sans-serif'>{ORDEN[L]}</text>")
    s.append("</svg>")
    return "".join(s)


def diana(master):
    c = "<div class=tit>La Diana del Saber</div>" + svg_diana(master)
    if master:
        c += "<div class=sol><b>Solución:</b> las letras forman <b>PIEDRA</b>. Hay que golpearlas en orden P-I-E-D-R-A (números rojos). Tiro a una letra: Destreza DC 5. Tiro al centro: DC 15 y dobla la apuesta. Si se falla una letra o se golpea una fuera de orden, se pierde el progreso.</div>"
    else:
        c += "<div class=sol style='text-align:center;color:#777;font-size:9pt'>Pega o coloca esta hoja junto a la atracción de Glitch. Los héroes dicen a qué letra tiran.</div>"
    return pagina(c)


NORIA = [("Dragón Negro", "Para hallar la riqueza que el Mago ha robado,", 1), ("Dragón Azul", "Debéis ir a la Cueva del Búho Veloz.", 2),
         ("Dragón Oro", "En la roca más vieja estará marcado", 3), ("Dragón Bronce", "El camino al tesoro, sin rastro ni voz.", 4),
         ("Dragón Rojo", "El Grito de Noche jamás se apacigua,", 5), ("Dragón Blanco", "Su furia de garras no tiene medida.", 6),
         ("Dragón Verde", "Si el Reposo le ofreces, su rabia se mitiga,", 7), ("Dragón Plata", "Y el cofre preciado evitará la herida.", 8)]


def noria(master):
    tiras = []
    for cab, verso, n in NORIA:
        marca = f"<span class=orden>{n}</span>" if master else ""
        tiras.append(f"<div class='tira'><div class=et>Cabina<br>{e(cab)}</div><div class=verso>{e(verso)}</div>{marca}</div>")
    tit = "<div class=tit style='top:8mm;font-size:16pt'>Noria de los Versos Perdidos · 8 carteles</div>"
    pie = ("Recorta cada cartel y escóndelo en la cabina que dice la etiqueta. En el cartel de los héroes la etiqueta se puede doblar hacia atrás. "
           + ("Los números rojos son el orden correcto del verso.") if master else
           "Recorta cada cartel y escóndelo en la cabina que dice la etiqueta (puedes doblar la etiqueta hacia atrás).")
    return pagina(tit + f"<div class='rejilla' style='top:20mm;grid-template-columns:180mm;grid-auto-rows:32mm'>{''.join(tiras)}</div>", "", pie)


CARRUSEL = [("El Grifo Alado", "RUIDO", "SILENCIO"), ("La Mantícora Sonriente", "VALIENTE", "COBARDE"), ("El Buhochú Veloz", "AMIGO", "ENEMIGO"),
            ("El Hipogrifo Noble", "LENTO", "RÁPIDO"), ("El Espectador Brumoso", "DURO", "BLANDO")]


def carrusel(master):
    tiras = []
    for fig, pal, ant in CARRUSEL:
        extra = f"<div class=ant>Antónimo:<br>{e(ant)}</div>" if master else ""
        tiras.append(f"<div class='tira carr'><div class=et>Poste<br>{e(fig)}</div><div class=pal>{e(pal)}</div>{extra}</div>")
    tit = "<div class=tit style='top:8mm;font-size:16pt'>Carrusel de los Contrasentidos · 5 carteles</div>"
    pie = "La palabra oculta va en gris claro para que cueste verla. Pega cada cartel en la base de su figura."
    return pagina(tit + f"<div class='rejilla' style='top:20mm;grid-template-columns:180mm;grid-auto-rows:48mm'>{''.join(tiras)}</div>", "", pie)


# ---------- preguntas ----------
PREGUNTAS = [("¿Cuántas patas tiene una araña?", "8"), ("¿De qué color sale si mezclas azul y amarillo?", "Verde"), ("¿Qué planeta es el planeta rojo?", "Marte"),
             ("¿En qué estación del año se caen las hojas de los árboles?", "Otoño"), ("¿Cuántos lados tiene un triángulo?", "3"),
             ("¿Qué mamífero vuela por la noche?", "El murciélago"), ("¿Cuántos días tiene una semana?", "7"), ("¿Cuántos dedos hay en las dos manos?", "10"),
             ("¿Qué tiene dientes pero no muerde?", "Un peine"), ("¿De qué color es la nieve?", "Blanco")]


def preguntas():
    fr = [f"<div class='preg'><div class='marco frente'><div class=n>EL LORO PREGONERO · {i+1}</div><div class=q>{e(q)}</div></div></div>" for i, (q, r) in enumerate(PREGUNTAS)]
    do = [f"<div class='preg'><div class='marco dorso'><div class=n>RESPUESTA · {i+1}</div><div class=r>{e(r)}</div></div></div>" for i, (q, r) in enumerate(PREGUNTAS)]
    return [pagina(rejilla(fr, 2, 90, 50), "Preguntas del Loro Pregonero · imprime al 100 % y recorta"),
            pagina(rejilla(reflejar(do, 2), 2, 90, 50), "Respuestas (dorso) · cada acierto da 1 PO; 3 preguntas por héroe")]


def nota_dama():
    """La carta de la Dama de los Mil Velos como accesorio de mesa: sobre sellado y carta para leer (1 hoja A4)."""
    css = (".sobre{position:absolute;left:25mm;top:18mm;width:160mm;height:90mm;border:.25mm dashed #aaa;background:#e9d8b0;"
           "border-radius:2mm;display:flex;align-items:center;justify-content:center;flex-direction:column}"
           ".sobre .para{font-size:15pt;font-style:italic;color:#4a2c1a;margin-bottom:6mm}"
           ".sello{width:26mm;height:26mm;border-radius:50%;background:radial-gradient(#f3d77a,#b8891c);border:1mm solid #8a6410;"
           "display:flex;align-items:center;justify-content:center;font-size:15mm;color:#7a5410}"
           ".carta-h{position:absolute;left:25mm;top:122mm;width:160mm;height:150mm;border:.25mm dashed #aaa;background:#fbf3de;"
           "padding:14mm 16mm;display:flex;flex-direction:column}"
           ".carta-h .v{font-size:17pt;line-height:1.5;font-style:italic;color:#2b2233}"
           ".carta-h .f{margin-top:auto;text-align:right;font-size:16pt;font-weight:700;color:#4a2c6e;font-style:italic}"
           ".carta-h .velos{text-align:center;font-size:12pt;letter-spacing:.4em;color:#b8891c;margin-bottom:8mm}")
    cuerpo = (f"<style>{css}</style>"
              "<div class='sobre'><div class='para'>Para Silas</div><div class='sello'>✦</div></div>"
              "<div class='carta-h'><div class='velos'>✦ ✦ ✦</div>"
              "<div class='v'>«Silas:<br><br>la feria ya está montada. Mantén encendida la última farola hasta que yo llegue.<br><br>No me falles otra vez.»</div>"
              "<div class='f'>La Dama de los Mil Velos</div></div>")
    return [pagina(cuerpo, "Sobre y carta de la Dama de los Mil Velos (solo master) · imprime al 100 % y recorta; dobla la carta y mete en el sobre")]


def pdf(nombre, paginas):
    with tempfile.TemporaryDirectory() as t:
        h = Path(t) / "x.html"
        h.write_text(doc(paginas), encoding="utf-8")
        destino = SAL / nombre
        subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=5000",
                        f"--print-to-pdf={destino}", f"file://{h}"], check=True, capture_output=True)
    print("→", destino)
    return destino


def miniatura(destino):
    import fitz
    d = fitz.open(destino)
    pm = d[0].get_pixmap(dpi=60)
    pm.save(str(destino.with_name(destino.stem + "-min.jpg")))


if __name__ == "__main__":
    principal = [POCION, MAPA, PERGAMINO, LLAVE, DAGA, ORBE, BOTAS, ESCAMA]
    salidas = [
        pdf("la-feria-del-misterio-cartas-objeto.pdf", pares(principal) + cartel_x4()),
        pdf("la-feria-del-misterio-cartas-objeto-master.pdf", pares([LLAVE_JAULA, CARTA])),
        pdf("la-feria-del-misterio-nota-dama-master.pdf", nota_dama()),
        pdf("la-feria-del-misterio-acertijos.pdf", [diana(False), noria(False), carrusel(False)]),
        pdf("la-feria-del-misterio-acertijos-master.pdf", [diana(True), noria(True), carrusel(True)]),
        pdf("la-feria-del-misterio-preguntas.pdf", preguntas()),
    ]
    for s in salidas:
        miniatura(s)
