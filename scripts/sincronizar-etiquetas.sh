#!/usr/bin/env bash
# Crea o actualiza en GitHub las etiquetas de .github/labels.yml  (requiere gh)
set -euo pipefail
grep -E '^- \{' .github/labels.yml | while IFS= read -r l; do
  nombre=$(sed -E 's/.*name: "([^"]+)".*/\1/' <<<"$l")
  color=$(sed -E 's/.*color: "([^"]+)".*/\1/' <<<"$l")
  desc=$(sed -E 's/.*description: "([^"]*)".*/\1/' <<<"$l")
  gh label create "$nombre" --color "$color" --description "$desc" --force
done
