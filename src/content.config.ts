import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

export const tarjeta = z.object({
  titulo: z.string(),
  emoji: z.string().optional(),
  cabecera: z.array(z.string()).optional(),
  filas: z.array(z.array(z.string())).default([]),
  notas: z.array(z.string()).default([]),
  pagina: z.number().int().min(1).max(6).optional(), // panel (hoja A4 vertical) de la pantalla del master
});

const recurso = z.object({
  titulo: z.string(),
  archivo: z.string(),
  miniatura: z.string().optional(),
  nota: z.string().optional(),
});

const hojas = z.object({ archivo: z.string(), hojas: z.number().int() });
// Mapa con ficha de impresión: 1 casilla = 25 mm, en mosaico A4 y A3
const mapa = recurso.extend({
  casillas: z.string().optional(), // «34 × 17»
  tamano: z.string().optional(), // «85 × 42,5 cm»
  a4: hojas.optional(),
  a3: hojas.optional(),
});

// Cada aventura vive en src/content/aventuras/<slug>/aventura.md:
// la cabecera (frontmatter) son los datos y el cuerpo es el guion que se lee online.
// Los archivos (PDF, mapas, audio…) van en public/aventuras/<slug>/.
const aventuras = defineCollection({
  loader: glob({
    pattern: '*/aventura.md',
    base: './src/content/aventuras',
    generateId: ({ entry }) => entry.split('/')[0],
  }),
  schema: z.object({
    titulo: z.string(),
    subtitulo: z.string().optional(),
    resumen: z.string(),
    gancho: z.string().optional(), // presentación sin spoilers (pestaña Resumen)
    publico: z.enum(['ninos', 'adultos', 'familia']),
    edad: z.string(),
    nivel: z.string(),
    jugadores: z.string(),
    duracion: z.string(),
    ambientacion: z.string(),
    portada: z.string(),
    etiquetas: z.array(z.string()).default([]),
    estado: z.enum(['borrador', 'publicada']).default('publicada'),
    fecha: z.coerce.date(),
    pnj: z
      .array(z.object({ nombre: z.string(), rol: z.string(), descripcion: z.string(), imagen: z.string().optional() }))
      .default([]),
    mapas: z.array(mapa).default([]),
    ilustraciones: z.array(recurso).default([]),
    musica: z
      .array(
        z.object({
          titulo: z.string(),
          archivo: z.string(),
          caratula: z.string().optional(),
          cuando: z.string().optional(),
          letra: z.array(z.string()).optional(),
        }),
      )
      .default([]),
    miniaturas: z.array(recurso).default([]),
    pantalla: z.array(tarjeta).default([]),
    descargas: z
      .array(z.object({ titulo: z.string(), archivo: z.string(), tipo: z.string(), descripcion: z.string().optional() }))
      .default([]),
  }),
});

export const collections = { aventuras };
