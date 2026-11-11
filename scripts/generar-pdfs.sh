#!/usr/bin/env bash
# Genera con Chrome los PDF imprimibles a partir de la web: pantalla del master y guion de cada aventura, y las fichas de héroe.
# Uso:  npm run build && ./scripts/generar-pdfs.sh
set -euo pipefail
CHROME=${CHROME:-google-chrome}
PUERTO=4411
npx astro preview --port $PUERTO >/dev/null 2>&1 &
PID=$!
trap 'kill $PID 2>/dev/null || true' EXIT
sleep 4
pdf() {  # pdf <ruta de la web> <salida>
  $CHROME --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer --virtual-time-budget=8000 \
    --print-to-pdf="$2" "http://localhost:$PUERTO$1" >/dev/null 2>&1
  echo "→ $2 ($(du -h "$2" | cut -f1))"
}
for dir in src/content/aventuras/*/; do
  slug=$(basename "$dir")
  mkdir -p "public/aventuras/$slug/descargas"
  [ -f "dist/aventuras/$slug/pantalla/index.html" ] && pdf "/aventuras/$slug/pantalla/" "public/aventuras/$slug/descargas/$slug-pantalla-master.pdf"
  [ -f "dist/aventuras/$slug/imprimir/index.html" ] && pdf "/aventuras/$slug/imprimir/" "public/aventuras/$slug/descargas/$slug-guion.pdf"
done
mkdir -p public/descargas
for v in chico chica dibujo; do
  [ -f "dist/fichas/imprimir/$v/index.html" ] && pdf "/fichas/imprimir/$v/" "public/descargas/fichas-de-heroe-$v.pdf"
done
