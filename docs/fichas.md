# Fichas del Gremio: cómo se calculan

Todo está en `src/data/clases.ts`. Las páginas `/fichas/` y `/fichas/<clase>/` se generan solas.

- **Habilidades** (nombres estándar, con emoji): 💪 Fuerza, 🤸 Destreza, 🧱 Constitución, 🧠 Inteligencia, 🦉 Sabiduría y 🗣️ Carisma. Cada clase tiene una *fuerte*, una *buena*, dos *normales* y dos *flojas*.
- **Número que se suma** (tabla `SUMA`): fuerte 3/3/4/4/5 · bueno 2/2/2/3/3 · normal 1/1/1/1/2 · flojo 0/0/0/0/1 (niveles 1 a 5).
- **Extra de daño** (`EXTRA_DANO`): 0/1/1/2/2 para cualquier arma.
- **Vidas:** `base + porNivel × (nivel − 1)`. **Defensa:** fija, +1 desde el nivel 4.
- **Poderes:** tres por clase, en los niveles 1, 3 y 5.
- **Armas:** dos por clase; cada una usa una habilidad y un dado (d4, d6, d8 o d10).

Para añadir una clase, copia una entrada de `clases`, cambia los datos y ejecuta `npm run build`.

## Compatibilidad con aventuras

Las habilidades usan los nombres estándar, así que las aventuras se escriben tal cual («tirada de Sabiduría (percepción) DC 10») y los jugadores buscan ese número en su ficha. Las dificultades: 5 fácil, 10 normal, 15 difícil, 20 heroico.
