// Convierte las citas de Markdown del guion en bloques con estilo propio:
//   > texto                → «Lee en voz alta» (narración para los jugadores)
//   > [!DM] texto          → nota solo para el master
//   > [!REGLA] texto       → regla o tirada
//   > [!PISTA] texto       → pista para los jugadores atascados
//   > [!MUSICA] texto      → cuándo poner música
import { visit } from 'unist-util-visit';

const TIPOS = {
  DM: ['dm', 'Para el master'],
  REGLA: ['regla', 'Regla'],
  PISTA: ['pista', 'Pista'],
  MUSICA: ['musica', 'Música'],
};

export default function remarkBloques() {
  return (tree) => {
    visit(tree, 'blockquote', (node) => {
      let tipo = ['leer', 'Lee en voz alta'];
      const p = node.children[0];
      const t = p?.type === 'paragraph' ? p.children[0] : null;
      if (t?.type === 'text') {
        const m = t.value.match(/^\[!(DM|REGLA|PISTA|MUSICA)\]\s*/);
        if (m) {
          tipo = TIPOS[m[1]];
          t.value = t.value.slice(m[0].length);
        }
      }
      node.data = {
        hName: 'aside',
        hProperties: { className: ['bloque', `bloque-${tipo[0]}`], 'data-titulo': tipo[1] },
      };
    });
  };
}
