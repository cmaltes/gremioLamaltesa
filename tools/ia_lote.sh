#!/usr/bin/env bash
# Genera los personajes que faltan con el modelo local. Salida: /tmp/claude-1000/ia/<nombre><semilla>.png
cd "$(dirname "$0")/.."
G="tools/.venv-ia/bin/python tools/ia_personaje.py"
S="warm detailed digital painting, storybook fairground style, standing facing viewer, feet visible, plain light grey background, no ground shadow"
$G /tmp/claude-1000/ia/aerion1.png "full body character illustration, teenage human prince about 16 years old, messy brown hair, wrinkled torn royal clothes in emerald green and gold, frightened but noble expression, hands held forward as if asking for help, $S" 1
$G /tmp/claude-1000/ia/fliflas1.png "full body character illustration, melancholic human minstrel about 40, thin, stubble and tired eyes, wide-brim hat with a worn feather, patched doublet in muted blue and maroon, short cape, holding an old lute with a broken string, sad gentle gaze, $S" 1
$G /tmp/claude-1000/ia/guiverno1.png "full body creature illustration, young emerald green wyvern dragon the size of a horse, two legs and two wings folded, arrow-tipped tail, sad scared big wet eyes, head lowered, broken chain collar, $S" 1
$G /tmp/claude-1000/ia/oso1.png "full body creature illustration, owlbear fantasy creature, big furry brown bear body with an owl head, curved beak, round yellow eyes, cream feathers on head and chest, large claws, young, menacing but kid friendly, three-quarter view, $S" 1
echo FIN
