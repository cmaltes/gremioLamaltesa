# Fichas del Gremio: cómo se calculan

Todo está en `src/data/clases.ts`. Las páginas `/fichas/` y `/fichas/<clase>/` se generan solas.

- **Talentos:** Fuerza, Agilidad, Ingenio y Corazón. Cada clase tiene un talento *fuerte*, uno *bueno*, uno *normal* y uno *flojo*.
- **Número que se suma** (tabla `SUMA`): fuerte 3/3/4/4/5 · bueno 2/2/2/3/3 · normal 1/1/1/1/2 · flojo 0/0/0/0/1 (niveles 1 a 5).
- **Extra de daño** (`EXTRA_DANO`): 0/1/1/2/2 para cualquier arma.
- **Vidas:** `base + porNivel × (nivel − 1)`. **Defensa:** fija, +1 desde el nivel 4.
- **Poderes:** tres por clase, en los niveles 1, 3 y 5.
- **Armas:** dos por clase; cada una usa un talento y un dado (d4, d6, d8 o d10).

Para añadir una clase, copia una entrada de `clases`, cambia los datos y ejecuta `npm run build`.

## Compatibilidad con aventuras de estilo clásico

Equivalencias: Destreza → Agilidad · Sabiduría e Inteligencia → Ingenio · Carisma → Corazón · Fuerza → Fuerza. Las dificultades (DC) se usan igual.
