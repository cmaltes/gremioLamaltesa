# Añadir una aventura

1. **Crea la estructura**

   ```bash
   npm run nueva -- el-faro-hueco "El Faro Hueco"
   ```

   Crea `src/content/aventuras/el-faro-hueco/aventura.md` y las carpetas de `public/aventuras/el-faro-hueco/`.

2. **Rellena `aventura.md`**. La cabecera (entre `---`) son los datos: público, edad, nivel, PNJ, mapas, música, descargas… El cuerpo es el guion, en Markdown. Si algo no cuadra con el esquema, `npm run build` dice qué.

3. **Copia los archivos** a `public/aventuras/<slug>/`:

   | Carpeta | Contenido |
   |---|---|
   | `portada.jpg` | 16:9, unos 1200×675 |
   | `mapas/` | mapa a tamaño completo + `-min.jpg` de 640 px |
   | `img/` | ilustraciones de escenas y PNJ (+ `-min.jpg`) |
   | `musica/` | MP3 y carátula JPG |
   | `miniaturas/` | figuras, fichas recortables, STL |
   | `descargas/` | PDF del guion y otros |

4. **Pon `estado: publicada`** cuando esté lista (mientras sea `borrador` no sale en la portada).

5. **Pull Request**. La comprobación `build` debe pasar.

## Escribir el guion

Markdown normal (títulos `##` y `###`, listas, tablas). Para destacar tipos de texto se usan citas:

```markdown
> Texto que el master lee en voz alta.

> [!DM]
> Nota solo para el master.

> [!REGLA]
> Tirada de Inteligencia **DC 10**.

> [!PISTA]
> Si se atascan, di que…

> [!MUSICA]
> Aquí pon la canción del juglar.
```

Una cita sin etiqueta se muestra como «Lee en voz alta». Las imágenes: `![texto](/aventuras/<slug>/img/archivo-min.jpg)`.

## Buenas prácticas para el master

- Cada escena: qué ven, qué pueden hacer, qué tirada y qué pasa si fallan.
- Dificultades: 5 fácil, 10 normal, 15 difícil, 20 heroico.
- Para niños: sin muerte (a 0 vidas se duermen), retos que se resuelven hablando, y humor.

## Pantalla del master

Añade tarjetas en la cabecera de `aventura.md` con el campo `pantalla` (mira el de La Feria del Misterio como ejemplo): cada tarjeta tiene `titulo`, `emoji`, `cabecera` (opcional), `filas`, `notas` y `pagina` (1-5: el panel o hoja donde va). Con ello se crea `/aventuras/<slug>/pantalla/`: 5 hojas A4 verticales con letra grande (una por panel, títulos en `titulosPaneles` de `src/data/pantalla.ts`), junto con las tarjetas generales de ese archivo. Comprueba tras `./scripts/generar-pdfs.sh` que el PDF sigue teniendo 5 páginas.

Para generar el PDF descargable (requiere Chrome): `npm run build && ./scripts/generar-pdfs.sh`, y añade el PDF a `descargas`.
