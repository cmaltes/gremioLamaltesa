#!/usr/bin/env node
// Crea la estructura de una aventura nueva:  npm run nueva -- mi-aventura "Título de la aventura"
import { mkdirSync, writeFileSync, existsSync } from 'node:fs';

const [slug, ...resto] = process.argv.slice(2);
const titulo = resto.join(' ') || 'Título de la aventura';
if (!slug || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug)) {
  console.error('Uso: npm run nueva -- <slug-en-minusculas-con-guiones> "Título"');
  process.exit(1);
}
const contenido = `src/content/aventuras/${slug}`;
const publico = `public/aventuras/${slug}`;
if (existsSync(contenido)) { console.error(`Ya existe ${contenido}`); process.exit(1); }
for (const d of ['mapas', 'img', 'musica', 'descargas', 'miniaturas']) {
  mkdirSync(`${publico}/${d}`, { recursive: true });
  writeFileSync(`${publico}/${d}/.gitkeep`, '');
}
mkdirSync(contenido, { recursive: true });

writeFileSync(`${contenido}/aventura.md`, `---
titulo: ${titulo}
subtitulo: Una frase que enganche.
resumen: Dos o tres frases para la tarjeta de la portada.
publico: ninos        # ninos | adultos | familia
edad: 7-12 años
nivel: 1-2
jugadores: 4 (3-5)
duracion: 2-3 horas
ambientacion: Dónde y cuándo ocurre.
portada: /aventuras/${slug}/portada.jpg   # 16:9, unos 1200x675
etiquetas: []
estado: borrador      # cambia a "publicada" cuando esté lista
fecha: ${new Date().toISOString().slice(0, 10)}
pnj: []
#  - nombre: Nombre
#    rol: Papel en la historia
#    descripcion: Cómo es y qué quiere.
#    imagen: /aventuras/${slug}/img/nombre-min.jpg
mapas: []
#  - titulo: Nombre del mapa
#    archivo: /aventuras/${slug}/mapas/mapa.jpg
#    miniatura: /aventuras/${slug}/mapas/mapa-min.jpg
ilustraciones: []
musica: []
#  - titulo: Nombre de la canción
#    archivo: /aventuras/${slug}/musica/cancion.mp3
#    caratula: /aventuras/${slug}/musica/cancion.jpg
#    cuando: Cuándo ponerla.
miniaturas: []
descargas: []
#  - titulo: Guion completo
#    archivo: /aventuras/${slug}/descargas/${slug}-guion.pdf
#    tipo: pdf
---

## 1. Configuración

- **Nivel:**
- **Jugadores:**
- **Duración:**

> [!DM]
> **La aventura en un minuto.** Resumen para que el master se la sepa de un vistazo.

## 2. Capítulo 1

> Texto que el master lee en voz alta a los jugadores.

> [!REGLA]
> Tirada de Inteligencia **DC 10** para…
`);
console.log(`Listo. Edita ${contenido}/aventura.md y mete los archivos en ${publico}/ (guía: docs/anadir-aventura.md).`);
