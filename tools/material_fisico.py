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
.sobre-m { background: #e9d8b0; position: relative; justify-content: center; border-color: #8a6410 }
.sobre-m .solapa { position: absolute; left: 0; right: 0; top: 0; height: 52mm; background: #d3ba80; clip-path: polygon(0 0, 100% 0, 50% 100%) }
.sobre-m .para { font-size: 14pt; font-style: italic; color: #4a2c1a; margin-top: 62mm }
.sobre-m .sello-m { position: absolute; top: 44mm; left: 50%; margin-left: -9mm; width: 18mm; height: 18mm; border-radius: 50%; background: radial-gradient(#f3d77a,#b8891c); border: .8mm solid #8a6410; display: flex; align-items: center; justify-content: center; font-size: 10mm; color: #7a5410 }
.sobre-m .vuelta { position: absolute; left: 5mm; right: 5mm; bottom: 5mm; width: auto }
.papel { background: #fbf3de repeating-linear-gradient(to bottom, transparent 0 6.4mm, #e7d7b0 6.4mm 6.7mm); border-color: #b8891c; align-items: stretch; text-align: left }
.papel .velos { text-align: center; color: #b8891c; letter-spacing: .4em; font-size: 10pt; margin-bottom: 5mm }
.papel .v { font-size: 12.5pt; line-height: 1.55; font-style: italic }
.papel .f { margin-top: auto; text-align: right; font-weight: 700; font-style: italic; color: #4a2c6e; font-size: 12pt }
.ini { background: #fff; align-items: stretch; padding: 3mm 4mm }
.ini table { width: 100%; border-collapse: collapse; font-size: 8pt; flex: 1 }
.ini th { font-size: 7pt; text-transform: uppercase; color: #9a6f1d; text-align: left; padding: .5mm 1mm }
.ini td { border: .25mm solid #999 } .ini td.n { width: 6mm; text-align: center; font-weight: 700; color: #4a2c6e }
.ini .ronda { font-size: 8pt; margin-top: 2mm; text-align: center }
.cartel-m { background: linear-gradient(#2b1d5a, #5b2a86); border-color: #ffc93c; padding: 0 !important; overflow: hidden; color: #fff; justify-content: flex-start }
.banderines { display: flex; width: 100%; height: auto; line-height: 0 } .banderines i { display: block; width: 0; height: 0 }
.cartel-m .banderines { margin-bottom: 1mm }
.cf-sup { color: #ffd966; font-size: 8pt; letter-spacing: .12em; text-transform: uppercase; font-family: 'Noto Sans',sans-serif; font-weight: 700 }
.cf-tit { font-size: 19pt; line-height: 1.05; font-weight: 800; color: #ffe08a; text-shadow: .4mm .4mm 0 #b5367a; margin: 1mm 0 2mm }
.cf-fotos { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2mm; padding: 0 4mm; width: 100% }
.cf-fotos img { width: 100%; aspect-ratio: 1.35; object-fit: cover; border-radius: 2mm; border: .5mm solid #ffc93c }
.cf-txt { font-size: 9.5pt; line-height: 1.3; margin: 2.2mm 4mm 0; font-weight: 700 }
.cf-ent { margin-top: 1.5mm; background: #ffc93c; color: #4a2c6e; border-radius: 3mm; padding: .8mm 3mm; font-size: 9.5pt }
.cartel-m .vuelta { margin: auto 3mm 3mm; width: calc(100% - 6mm) }
.cartel-a4 { width: 210mm; height: 297mm; background: linear-gradient(#1f1550, #5b2a86 60%, #b5367a); color: #fff; text-align: center; position: relative; display: flex; flex-direction: column; align-items: center }
.a4-sup { margin-top: 6mm; font-size: 16pt; letter-spacing: .15em; text-transform: uppercase; color: #ffd966; font-weight: 700; font-family: 'Noto Sans',sans-serif }
.a4-tit { font-size: 50pt; line-height: 1.02; font-weight: 800; color: #ffe08a; text-shadow: 1.2mm 1.2mm 0 #b5367a; margin: 4mm 0 6mm }
.a4-fotos { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; padding: 0 14mm; width: 100% }
.a4-fotos figure { position: relative } .a4-fotos img { width: 100%; aspect-ratio: 1.25; object-fit: cover; border-radius: 5mm; border: 1.2mm solid #ffc93c }
.a4-fotos figcaption { position: absolute; left: 4mm; bottom: 3mm; background: #ffc93c; color: #4a2c6e; font-weight: 800; font-size: 14pt; padding: .5mm 4mm; border-radius: 4mm }
.a4-txt { margin-top: 8mm; font-size: 32pt; font-weight: 800; color: #fff }
.a4-sub { margin-top: 2mm; font-size: 17pt; line-height: 1.35 }
.a4-ent { margin-top: 6mm; background: #ffc93c; color: #4a2c6e; border-radius: 6mm; padding: 2mm 8mm; font-size: 14pt; font-weight: 800 }
.banderines.abajo { position: absolute; bottom: 0; transform: rotate(180deg) }
.precio { font-size: 10pt; font-weight: 700; color: #9a6f1d }
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
.vuelta { margin-top: auto; width: 100%; border-radius: 3mm; padding: 2mm 3mm; font-size: 9.5pt; line-height: 1.25; font-family: 'Noto Sans','DejaVu Sans',sans-serif }
.vuelta.tir { background: #4a2c6e; color: #fff } .vuelta.tir b { color: #ffe08a }
.vuelta.libre { background: #e6f3e0; color: #2d5a1e; border: .3mm solid #8cbf78; font-weight: 700 }
.precio { margin-top: 3mm !important }
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
def aviso_vuelta(c):
    """Cartel al pie del frente: qué tirada hace falta para dar la vuelta, o que se puede girar ya."""
    if c.get("tirada"):
        return f"<div class='vuelta tir'>🎲 <b>{e(c['tirada'])}</b><br>Si la superas, dale la vuelta</div>"
    return f"<div class='vuelta libre'>↻ {e(c.get('libre', 'Puedes darle la vuelta ya'))}</div>"


def frente(c):
    if c.get("frente_html"):
        return c["frente_html"](c)
    cuerpo = f"<div class=tipo>{e(c['tipo'])}</div><div class=dibujo>{c['emoji']}</div><div class=nombre>{e(c['nombre'])}</div><div class=desc>{e(c['frente'])}</div>"
    if c.get("precio"):
        cuerpo += f"<div class=precio>{e(c['precio'])}</div>"
    cuerpo += aviso_vuelta(c)
    return f"<div class='carta'><div class='marco frente'>{cuerpo}</div></div>"


IMG = RAIZ / "public/aventuras/la-feria-del-misterio/img"
ATRACCIONES = [("carrusel-zash", "Carrusel"), ("noria-gart", "Noria"), ("diana-glitch", "Diana"), ("tienda-mizzen", "Tienda")]
COLORES = ["#ff6f91", "#ffc93c", "#4fc3f7", "#7bdc8a", "#c084fc", "#ff9a4d"]


def banderines(n, ancho_mm, alto_mm):
    """Guirnalda de banderines de colores (triángulos con bordes CSS)."""
    w = ancho_mm / n
    tri = "".join(f"<i style='border-left:{w/2:.2f}mm solid transparent;border-right:{w/2:.2f}mm solid transparent;border-top:{alto_mm}mm solid {COLORES[k % len(COLORES)]}'></i>" for k in range(n))
    return f"<div class=banderines>{tri}</div>"


def frente_cartel(c):
    fotos = "".join(f"<img src='file://{IMG}/{f}-min.jpg'>" for f, _ in ATRACCIONES)
    cuerpo = (banderines(9, 80, 6) +
              "<div class=cf-sup>★ ¡Gran festival! ★</div><div class=cf-tit>Festival<br>de los Mil Velos</div>"
              f"<div class=cf-fotos>{fotos}</div>"
              "<div class=cf-txt>🎡 ¡Ven y juega! 🎠<br>Premios para valientes, acertijos para curiosos y mil luces que brillan sin vela.</div>"
              "<div class=cf-ent>Entrada: <b>una sonrisa</b> 😊</div>" + aviso_vuelta(c))
    return f"<div class='carta'><div class='marco cartel-m'>{cuerpo}</div></div>"


def cartel_a4():
    """Cartel grande del festival (A4) para enseñarlo en la mesa o colgarlo."""
    fotos = "".join(f"<figure><img src='file://{IMG}/{f}.jpg'><figcaption>{n}</figcaption></figure>" for f, n in ATRACCIONES)
    cuerpo = (f"<div class='cartel-a4'>{banderines(14, 210, 14)}"
              "<div class=a4-sup>★ ¡Hoy, solo esta noche! ★</div><div class=a4-tit>Festival<br>de los Mil Velos</div>"
              f"<div class=a4-fotos>{fotos}</div>"
              "<div class=a4-txt>¡Ven y juega!</div>"
              "<div class=a4-sub>Premios para valientes, acertijos para curiosos<br>y mil luces que brillan sin vela.</div>"
              "<div class=a4-ent>Entrada: una sonrisa 😊 &nbsp;·&nbsp; Cierre: cuando se apaguen las farolas 🏮</div>"
              f"{banderines(14, 210, 14).replace('banderines', 'banderines abajo')}</div>")
    return [pagina(cuerpo)]


def dorso(c):
    if c.get("dorso_html"):
        return c["dorso_html"](c)
    cuerpo = f"<div class=tipo>{e(c['nombre'])}</div><div class=cab>{e(c['dorso_titulo'])}</div>"
    for sub, txt in c["dorso"]:
        if sub:
            cuerpo += f"<div class=sub>{e(sub)}</div>"
        cuerpo += f"<div class=txt>{e(txt)}</div>"
    return f"<div class='carta'><div class='marco dorso'>{cuerpo}</div></div>"


VACIA = "<div class='carta' style='border:none'></div>"

POCION = dict(nombre="Poción Solvente Místico", emoji="🧪", tipo="Objeto", tirada="Inteligencia (arcanos) · DC 13",
              frente="Una poción verde que huele a hierbabuena. La etiqueta está borrosa y no se entiende.",
              dorso_titulo="Lo que descubres",
              dorso=[("", "Es un frasquito de líquido verde que burbujea suavemente. Reconoces el brillo: es un solvente místico, un remedio contra la piedra mágica. En la etiqueta, con letra diminuta, se lee: «Si ves estatua, gris y fría, / devuélvele pronto su día». Un sorbo, o un chorrito sobre quien se haya vuelto de piedra, lo devuelve a la normalidad. Solo alcanza para una persona.")])
MAPA = dict(nombre="Mapa Escondido", emoji="🗺️", tipo="Objeto", tirada="Sabiduría (supervivencia) · DC 13",
            frente="Un mapa lleno de rayas y dibujos de búhos. Una línea de puntos sale de la feria hacia el bosque, pero no sabéis a dónde lleva.",
            dorso_titulo="Lo que descubres",
            dorso=[("", "Entre los garabatos reconoces una roca con forma de búho en mitad del bosque y una línea de puntos que sale de la feria. Es el camino a la Boca del Búho: con este mapa no os perderéis. Junto a la roca hay dibujadas unas garras enormes… quizá allí viva algo que no quiere visitas.")])
PERGAMINO = dict(nombre="Pergamino de Dormir", emoji="📜", tipo="Objeto", tirada="Inteligencia (arcanos) · DC 13",
                 frente="La tinta plateada se mueve sola y huele a lavanda. Parece un hechizo, pero no sabéis cuál.",
                 dorso_titulo="Lo que descubres",
                 dorso=[("", "Las letras plateadas brillan al mirarlas: es un hechizo de Sueño. Si se lee en voz alta señalando a un enemigo, los que tengan pocas fuerzas caen dormidos un buen rato. Solo sirve una vez: al terminar, el pergamino se convierte en polvo.")])
LLAVE = dict(nombre="Llave del Cofre del Tesoro", emoji="🗝️", tipo="Objeto", tirada="Inteligencia (investigación) · DC 13 (con DC 16 verás más)",
             frente="Una llave dorada muy brillante. Sirve para abrir algo.",
             dorso_titulo="Según tu tirada",
             dorso=[("Si sacas 13 o más", "Es una llave dorada con un búho grabado en el mango, de un cofre pequeño y antiguo. Pesa más de lo normal."),
                    ("Si sacas 16 o más (además)", "Mirando de cerca el extremo de la llave ves un polvo gris pegado. Huele a piedra mojada: es polvo de petrificación. El cofre que abra esta llave puede convertir en estatua a quien lo abra. Convendría tener un remedio a mano…")])
DAGA = dict(nombre="Daga Mágica de Cocina", emoji="🍴", tipo="Baratija de Mizzen", precio="1 PO",
            frente="Un tenedor enorme que brilla como una estrella pequeña.",
            libre="Es tuya: dale la vuelta ya", dorso_titulo="Tuya por 1 PO", dorso=[("", "Mizzen te entrega un tenedor enorme que brilla como una estrella pequeña. Al clavarlo en una manzana, ¡la manzana hace «¡ñam, ñam!» y se corta sola en trocitos! No sirve para pelear, pero ¡qué elegante para la cena! Y en la oscuridad alumbra como una vela.")])
ORBE = dict(nombre="Orbe del Vidente", emoji="🔮", tipo="Baratija de Mizzen", precio="3 PO",
            frente="Una bola de cristal muy seria y muy fría. Dice que dentro vive una predicción secretísima.",
            libre="Es tuya: dale la vuelta ya", dorso_titulo="Tuya por 3 PO", dorso=[("", "Es una bola de cristal muy seria y muy fría. Al mirar dentro solo ves tu propia cara, enorme y un poco torcida. Mizzen susurra: «Dentro vive una predicción secretísima… cuando la encuentres, ¡me avisas!». Seguro que da buena suerte, o al menos mucha risa.")])
BOTAS = dict(nombre="Botas de Siete Leguas", emoji="🥾", tipo="Baratija de Mizzen", precio="5 PO",
             frente="Una bota roja con alas bordadas. Solo hay una.",
             libre="Es tuya: dale la vuelta ya", dorso_titulo="Tuya por 5 PO", dorso=[("", "Es una bota roja con alas bordadas que te queda enorme. Al ponértela, ¡das un salto gigante! Pero como solo hay una… ¡giras y giras en círculos hasta marearte! Con la otra bota sería otra historia.")])
ESCAMA = dict(nombre="Escama de Aerion", emoji="🐉", tipo="Premio del Druida", tirada="",
              frente="Una escama verde, muy suave y caliente. Late un poquito, como un corazón pequeño.",
              dorso_titulo="Cómo se usa", dorso=[("", "Una sola vez, en el combate final, quien la tenga puede recuperar 1d6 + 2 vidas como acción adicional.")])
CARTEL = dict(nombre="Cartel del Festival", emoji="🪧", tipo="", tirada="Sabiduría (percepción) · DC 13",
              dorso_titulo="Lo que descubres",
              dorso=[("", "Las letras doradas se mueven despacio, como si respirasen. Al girar el cartel hacia la feria, brilla más fuerte; hacia el bosque, se apaga. Es un cartel hechizado que lleva a quien lo tiene hasta el festival.")])
LLAVE_JAULA = dict(nombre="Llave de la Jaula", emoji="🗝️", tipo="Objeto", tirada="Inteligencia (investigación) · DC 8",
                   frente="Una llave pequeña de hierro oscuro, con un dragón grabado en el mango.",
                   dorso_titulo="Lo que descubres",
                   dorso=[("", "Es una llave pequeña de hierro oscuro con un dragón grabado en el mango. Seguro que abre la jaula de la Bestia.")])
def carta_frente(c):
    return ("<div class='carta'><div class='marco sobre-m'><div class=solapa></div><div class=para>Para Silas</div><div class=sello-m>✦</div>"
            "<div class='vuelta libre'>↻ Ábrela: dale la vuelta</div></div></div>")


def carta_dorso(c):
    return ("<div class='carta'><div class='marco papel'><div class=velos>✦ ✦ ✦</div>"
            "<div class=v>«Silas:<br><br>la feria ya está montada. Mantén encendida la última farola hasta que yo llegue.<br><br>No me falles otra vez.»</div>"
            "<div class=f>La Dama de los Mil Velos</div></div></div>")


CARTA = dict(nombre="Carta sellada", frente_html=carta_frente, dorso_html=carta_dorso)

# Ficha de iniciativa (master): se escribe con lápiz o rotulador borrable
def ini_frente(c):
    filas = "".join("<tr><td class=n>%d</td><td></td><td></td><td></td></tr>" % n for n in range(1, 11))
    return ("<div class='carta'><div class='marco ini'><div class=tipo>Ficha del master</div><div class=nombre style='margin-bottom:2mm'>⚔️ Orden de iniciativa</div>"
            "<table><thead><tr><th>#</th><th>Quién</th><th>Tirada</th><th>Vidas</th></tr></thead><tbody>" + filas + "</tbody></table>"
            "<div class=ronda>Ronda: ☐1 ☐2 ☐3 ☐4 ☐5 ☐6 ☐7 ☐8</div></div></div>")


def ini_dorso(c):
    return ("<div class='carta'><div class='marco dorso'><div class=tipo>Ficha del master</div><div class=cab>Cómo se usa</div>"
            "<div class=txt style='font-style:normal'>"
            "<b>1.</b> Cada héroe tira <b>d20 + Destreza</b>. Tú tiras <b>1 d20 + 2</b> por cada tipo de enemigo.<br><br>"
            "<b>2.</b> Apunta a todos de <b>mayor a menor</b> en la columna «Quién» (empate: primero los héroes).<br><br>"
            "<b>3.</b> Cada turno: 1 movimiento + 1 acción (+ 1 acción adicional si la tienes). Tacha las vidas que se pierden.<br><br>"
            "<b>4.</b> Al acabar el último de la lista, marca la ronda y vuelve a empezar por arriba.<br><br>"
            "<span style='color:#777'>Consejo: escribe con lápiz o con rotulador borrable y plastifícala.</span></div></div></div>")


INICIATIVA = dict(nombre="Iniciativa", frente_html=ini_frente, dorso_html=ini_dorso)


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
    try:
        import fitz
        d = fitz.open(destino)
        d[0].get_pixmap(dpi=60).save(str(destino.with_name(destino.stem + "-min.jpg")))
    except ImportError:
        subprocess.run(["pdftoppm", "-r", "60", "-jpeg", "-singlefile", str(destino), str(destino.with_name(destino.stem + "-min"))], check=True)


if __name__ == "__main__":
    principal = [POCION, MAPA, PERGAMINO, LLAVE, DAGA, ORBE, BOTAS, ESCAMA]
    salidas = [
        pdf("la-feria-del-misterio-cartas-objeto.pdf", pares(principal) + cartel_x4()),
        pdf("la-feria-del-misterio-cartas-objeto-master.pdf", pares([LLAVE_JAULA, CARTA, INICIATIVA, INICIATIVA])),
        pdf("la-feria-del-misterio-nota-dama-master.pdf", nota_dama()),
        pdf("la-feria-del-misterio-cartel-festival.pdf", cartel_a4()),
        pdf("la-feria-del-misterio-acertijos.pdf", [diana(False), noria(False), carrusel(False)]),
        pdf("la-feria-del-misterio-acertijos-master.pdf", [diana(True), noria(True), carrusel(True)]),
        pdf("la-feria-del-misterio-preguntas.pdf", preguntas()),
    ]
    for s in salidas:
        miniatura(s)
