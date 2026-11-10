# Plan: imágenes, personajes, miniaturas, muñecos, mapas y PDFs

Se hace **de uno en uno**, en este orden. Cada paso termina con commit, publicación y revisión en móvil.
Estado: **Paso 0 hecho**; el resto pendiente (solo existen el PDF de la pantalla del master y el PDF original del guion).

## Decisiones tomadas (10-nov-2026)

| Tema | Decisión |
|---|---|
| Escala de la cuadrícula | **1 casilla = 25 mm** (1 pulgada, para miniaturas de 25-28 mm). |
| Mapas | **A escala real en mosaico de hojas** (versiones A4 y A3, con marcas de corte y solapes). No se hace la versión «ajustada a una hoja», salvo que se pida más adelante. |
| PDFs generados | **Se suben al repo** (en `public/aventuras/<slug>/descargas/`). Vigilar el peso total y no subir PDF intermedios. |
| Estilo común | El de las ilustraciones actuales: pintura digital cálida de feria nocturna, con luces. Los personajes nuevos se piden con ese mismo estilo. |
| Personajes que faltan | **No puedo generar imágenes.** Escribo prompts con el mismo estilo (`docs/prompts-imagenes.md`) para generarlos con Gemini u otra IA, y yo los proceso (recorte, color, tamaño). |
| Herramientas | Entorno Python aparte (`tools/`, fuera de la web) con OpenCV, rembg (modelo de ~170 MB), Real-ESRGAN (la GPU GTX 1650 de 4 GB sirve con tiles) y una librería de PDF. |

## Lo que hay ahora (para no volver a investigarlo)

- 9 imágenes de Gemini en `public/aventuras/la-feria-del-misterio/`: 4 ilustraciones de atracciones con su kobold (`img/`) y 5 mapas (`mapas/`). Todas llevan la marca ✦ de Gemini abajo a la derecha. Se guardaron como JPG q84 a su tamaño original (1024², 1408×736 y 2048²), con `-min.jpg` de 640 px.
- No existen imágenes de Alarico, Aerion (humano ni guiverno), Fliflas ni el Oso Lechuza.
- Los originales en alta (PNG de hasta 11 MB) siguen dentro del `.docx` de la carpeta del proyecto, fuera de git (`/*.docx`).
- Las cuadrículas de los mapas son de IA: puede que no sean regulares ni del mismo tamaño en todos. El análisis rápido que hice por frecuencias fue **inconcluyente** (dio periodos incoherentes); hay que medirlas bien en el paso 5.
- Los PDF se generan con Chrome desde la web: `npm run build && ./scripts/generar-pdfs.sh`. Las páginas de impresión usan `@page` con nombre (ver `.pantalla-pag` en `src/styles/global.css`).
- Esquema de `aventura.md`: `pnj[].imagen`, `mapas`, `ilustraciones`, `miniaturas`, `descargas` (ver `src/content.config.ts`).

## Pasos

### Paso 0 · Herramientas
- Crear `tools/` con `requirements.txt` y un entorno virtual (no se sube): opencv-python, numpy, pillow, rembg, realesrgan (o alternativa), pymupdf o reportlab.
- Guardar los originales en `_originales/` (ignorado por git) antes de tocar nada.
- **Hecho cuando:** un script de prueba limpia una imagen y genera un PDF.
- **Estado: HECHO (10-nov-2026).** `tools/.venv` con opencv-headless, numpy, pillow, pymupdf y rembg[cpu] (856 MB, ignorado por git); `tools/prueba.py` limpia la esquina por inpainting y crea un PDF A4. Originales copiados a `_originales/` (ignorado). **Pendiente al llegar al Paso 1:** instalar Real-ESRGAN (necesita torch; el disco tiene solo ~10 GB libres, así que instalar torch con CUDA ~3 GB solo entonces). El modelo de rembg (~170 MB) se descarga la primera vez que se use (Paso 2).

### Paso 1 · Limpiar y unificar las 9 imágenes
- Quitar la marca ✦ (relleno por inpainting o recorte de esquina; revisar a ojo cada una).
- Subir resolución ×2 con Real-ESRGAN (ilustraciones 1024 → 2048, mapas 1408 → 2816) y afinar.
- Unificar color: misma temperatura, contraste y saturación entre las 4 escenas; mapas entre sí.
- Regenerar `-min.jpg`, vigilar el peso (objetivo < 1,5 MB por imagen).
- **Hecho cuando:** ninguna imagen tiene marca, se ven nítidas al hacer zoom y las 4 escenas parecen de la misma serie.

### Paso 2 · Personajes aparte
- Con lo que hay: recortar a Glitch, Gart, Zash y Mizzen de sus escenas (fondo transparente) y sacar un retrato cuadrado de cada uno.
- Para Alarico, Aerion (humano y guiverno), Fliflas y el Oso Lechuza: escribir prompts en `docs/prompts-imagenes.md` (cuerpo completo, de frente, fondo liso, mismo estilo). El usuario los genera; yo los proceso igual.
- Guardar en `public/aventuras/<slug>/personajes/<personaje>.png` y `<personaje>-retrato.jpg`; actualizar `pnj[].imagen` y la sección Personajes de la web.
- **Hecho cuando:** los 11 PNJ de la aventura tienen retrato y recorte, y se ven en la web.

### Paso 3 · Miniaturas (fichas redondas, «tokens»)
- Hoja de tokens con el retrato de cada personaje: redondos de **25 mm** (pequeños y medianos) y **50 mm** (Oso Lechuza, Guiverno), con borde de color según sean aliados o enemigos y el nombre.
- Descarga en PNG y PDF. Rellenar la sección Miniaturas de la web (el issue #1 ya existe).
- **Hecho cuando:** se pueden imprimir y recortar a la medida exacta, y salen en la web y en Descargas.

### Paso 4 · Muñecos imprimibles (de pie, de papel)
- PDF A4 con cada personaje por delante y por detrás (espejo), peana plegable con pestaña y líneas de corte.
- Altura según el tamaño: el ancho de la peana es 1 casilla (25 mm) para pequeños y medianos, 2 casillas para grandes.
- Una hoja por grupo (enemigos, aliados) para aprovechar papel. Probar imprimiendo al 100 % y comprobar con una regla.
- **Hecho cuando:** un PDF se imprime, se recorta y se tiene de pie sobre un mapa.

### Paso 5 · Mapas en A4 y A3 con la cuadrícula bien
- Medir la cuadrícula real de cada mapa (detección de líneas, no a ojo); anotar píxeles por casilla y número de casillas.
- Si la cuadrícula de la IA no es regular, dibujar una cuadrícula propia en vectorial de 25 mm encima (y, si hace falta, atenuar la original).
- PDF a escala 1 casilla = 25 mm en mosaico, en dos versiones: hojas A4 y hojas A3, con solapes, marcas de corte y numeración de hojas.
- Incluir una regla de 5 casillas (125 mm) impresa en cada hoja para comprobar la escala.
- Tener en cuenta el margen no imprimible (5-10 mm).
- **Hecho cuando:** cada mapa tiene sus PDFs, con una ficha de «tamaño, casillas y hojas», y se comprueba que 25 mm miden 25 mm al imprimir.

### Paso 6 · PDFs finales y Descargas
- Guion completo: nueva vista imprimible `/aventuras/<slug>/imprimir/` (con imágenes y bloques del master) → PDF. Sustituir el PDF original de 3,6 MB.
- Fichas de héroe: una hoja A4 por clase + hoja de reglas.
- Reunir en `descargas` del frontmatter: guion, pantalla del master, fichas, mapas (A4/A3), tokens, muñecos.
- Ampliar `scripts/generar-pdfs.sh` (los PDF se suben al repo).
- **Hecho cuando:** todo se descarga desde la página de la aventura y coincide con la versión actual de la web.

## Retomar después de `/clear`

Di: «Lee `docs/plan-recursos.md` y empezamos por el Paso 0» (o el paso que toque). Los issues de GitHub de la etiqueta `tipo:recurso` reflejan estos pasos.
