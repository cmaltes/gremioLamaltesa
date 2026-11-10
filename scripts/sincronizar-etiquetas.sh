#!/usr/bin/env bash
# Crea o actualiza en GitHub las etiquetas de .github/labels.yml  (requiere gh y python3)
set -euo pipefail
python3 - <<'PY' | while IFS=$'\t' read -r nombre color desc; do
  gh label create "$nombre" --color "$color" --description "$desc" --force
done
import re
for l in open('.github/labels.yml'):
    m = re.search(r'name: "([^"]+)", color: "([^"]+)", description: "([^"]*)"', l)
    if m: print('\t'.join(m.groups()))
PY
