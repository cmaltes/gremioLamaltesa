# El Gremio · gremio.lamaltesa.dev

Partidas de rol listas para jugar, para niños y adultos: guion para leer en el móvil o descargar en PDF, mapas con zoom, música, personajes, ilustraciones, miniaturas y fichas de héroe sencillas. Pensado para que el master solo tenga que disfrutar.

Forma parte de [lamaltesa.dev](https://lamaltesa.dev).

## Qué hay

- **Partidas** (`src/content/aventuras/`): cada una con su guion, mapas, PNJ, música y descargas.
- **Fichas de héroe** (`src/data/clases.ts`): 10 clases propias, nivel 1 a 5, con dos armas fáciles y los números ya sumados. Reglas del Gremio: inspiradas en los juegos de rol clásicos, pero originales y mucho más simples. Ver [`docs/fichas.md`](docs/fichas.md).

## Principios

1. **Móvil y tableta primero.** Botones de 44 px, letra ajustable, tablas que se desplazan. Si algo no se ve bien en 360 px de ancho, no está terminado.
2. **Sin JavaScript imprescindible.** Todo se lee sin JS; el JS solo añade zoom, filtros y comodidades.
3. **El master manda.** Cada partida debe poder dirigirse solo con lo que hay en su página.

## Desarrollo

Requiere Node 20 o superior.

```bash
npm install
npm run dev        # http://localhost:4321
npm run build      # genera dist/ y valida los datos de todas las aventuras
npm run nueva -- mi-aventura "Mi aventura"   # crea la estructura de una partida nueva
```

## Añadir una partida

Mira [`docs/anadir-aventura.md`](docs/anadir-aventura.md). Resumen: `npm run nueva`, rellena `aventura.md`, copia los archivos a `public/aventuras/<slug>/`, abre una Pull Request.

## Organización en GitHub

- **Issues** con plantillas: nueva aventura, recurso (mapa, música, miniatura) y fallo de la web.
- **Etiquetas**: `tipo:*`, `público:*`, `estado:*` y `área:*` (en `.github/labels.yml`; `scripts/sincronizar-etiquetas.sh` las aplica).
- **Hitos**: uno por versión de la web.
- Cada Pull Request pasa la comprobación `build`; al fusionar con `main` se publica sola en GitHub Pages.

## Publicación

GitHub Pages desde GitHub Actions (`.github/workflows/deploy.yml`). El dominio está en `public/CNAME`. En el DNS de `lamaltesa.dev` hace falta un registro `CNAME` de `gremio` hacia `cmaltes.github.io`.

## Licencia y créditos

El contenido (guiones, textos, canciones e imágenes) es de su autor. Las ilustraciones y mapas de la primera partida se han generado con IA. Todavía no hay licencia abierta; se añadirá cuando se decida.
