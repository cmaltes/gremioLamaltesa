#!/usr/bin/env bash
# Genera los PDF imprimibles (pantalla del master) a partir de la web con Chrome.
# Uso:  npm run build && ./scripts/generar-pdfs.sh
set -euo pipefail
CHROME=${CHROME:-google-chrome}
PUERTO=4411
npx astro preview --port $PUERTO >/dev/null 2>&1 &
PID=$!
trap 'kill $PID 2>/dev/null || true' EXIT
sleep 4
for dir in src/content/aventuras/*/; do
  slug=$(basename "$dir")
  if [ -f "dist/aventuras/$slug/pantalla/index.html" ]; then
    out="public/aventuras/$slug/descargas/$slug-pantalla-master.pdf"
    $CHROME --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer \
      --print-to-pdf="$out" "http://localhost:$PUERTO/aventuras/$slug/pantalla/" >/dev/null 2>&1
    echo "→ $out"
  fi
done
