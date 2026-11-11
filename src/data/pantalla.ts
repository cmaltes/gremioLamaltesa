// Tarjetas generales de la pantalla del master (valen para cualquier aventura): reglas, no guion.
// Cada aventura añade solo sus datos de combate (enemigos…) en la cabecera de aventura.md (campo `pantalla`).
// El guion (orden de la aventura, pistas, respuestas…) va aparte, en el guion de la aventura.
import { clases, TALENTOS, suma, vida, defensa, ataqueArma, SUMINISTROS, ALCANCE, metros } from './clases';

export interface Tarjeta { titulo: string; emoji?: string; cabecera?: string[]; filas: string[][]; notas: string[]; pagina?: number; flujo?: boolean }

// Títulos de los 6 paneles (hojas A4 verticales) de la pantalla del master de una aventura.
export const titulosPaneles = ['El combate', 'Acciones', 'Movimiento y alcance', 'Los héroes', 'Números y descansos', 'Enemigos y tiradas'];

const mas = (n: number) => `+${n}`;
const armasFilas = () => {
  // Agrupado por alcance: [casillas, armas (quién las usa)]. Lo que no tiene alcance propio es cuerpo a cuerpo (1 casilla).
  const grupos = new Map<number, string[]>([[1, []]]);
  for (const c of clases) for (const a of c.armas) {
    const r = ALCANCE[a.nombre] ?? 1;
    if (!grupos.has(r)) grupos.set(r, []);
    grupos.get(r)!.push(r === 1 ? a.nombre : `${a.nombre} (${c.nombre})`);
  }
  return [...grupos.entries()].sort((a, b) => a[0] - b[0]).map(([r, l]) => [r === 1 ? '1 (1,5 m)' : metros(r), r === 1 ? [...new Set(l)].join(', ') : l.join(', ')]);
};

export const tarjetasGenerales: Tarjeta[] = [
  // ---------- Panel 1: el combate ----------
  { titulo: 'Diagrama de un combate', emoji: '⚔️', pagina: 1, flujo: true, filas: [], notas: [] },

  // ---------- Panel 2: acciones ----------
  {
    titulo: 'Ejemplos de ACCIÓN (1 por turno)', emoji: '✋', pagina: 2, cabecera: ['Acción', 'Cómo funciona'],
    filas: [
      ['Atacar', 'd20 + número del arma contra la Defensa. Si aciertas, dado del arma + extra.'],
      ['Usar un poder', 'Los de la ficha. Algunos solo 1 vez por combate.'],
      ['Ayudar', 'Un amigo tira con ventaja (2 d20, vale el mejor).'],
      ['Esconderte', 'Destreza DC 12. Si sales bien, tu próximo ataque va con ventaja.'],
      ['Curar o despertar', 'Poción (5 vidas) o poder de curar. Tocar a un dormido: vuelve con 1 vida.'],
      ['Empujar o derribar', 'Fuerza DC 12. Cae al suelo y gasta movimiento en levantarse.'],
      ['Usar un objeto', 'Abrir un cofre con llave, leer un pergamino, activar un mecanismo…'],
    ],
    notas: [],
  },
  {
    titulo: 'Ejemplos de ACCIÓN ADICIONAL (1 por turno)', emoji: '⚡', pagina: 2, cabecera: ['Acción adicional', 'Cómo funciona'],
    filas: [
      ['Cambiar de arma', 'Guardas la que llevas y sacas la otra.'],
      ['Sacar o guardar un objeto', 'Una poción, una cuerda, una antorcha.'],
      ['Abrir o cerrar', 'Una puerta, una trampilla, una palanca.'],
      ['Gritar o avisar', 'Una orden o frase corta a un amigo.'],
      ['Recoger algo', 'Un objeto del suelo a tu lado (una jabalina, una llave).'],
      ['Esconderse (kobolds)', 'Algunos enemigos lo hacen así, sin gastar acción.'],
    ],
    notas: ['Reacción (1 por ronda, fuera de tu turno): poderes como «¡Detrás de mí!», «Escudo mágico» o «Esquiva loca».', 'Ejemplo de turno: el Guerrero se mueve 4 casillas, ataca con la espada (acción) y cambia a la jabalina (acción adicional).'],
  },

  // ---------- Panel 3: movimiento y alcance ----------
  {
    titulo: 'La cuadrícula', emoji: '🔲', pagina: 3,
    filas: [
      ['1 casilla', '1,5 m en el juego = 25 mm en el mapa impreso. La diagonal cuenta como 1.'],
      ['Pasar por otros', 'Por amigos sí (sin acabar encima). Por enemigos no.'],
      ['Tamaño', 'Pequeños y medianos: 1 casilla. Grandes: 2×2.'],
    ],
    notas: [],
  },
  {
    titulo: 'Moverse', emoji: '🦶', pagina: 3, cabecera: ['Situación', 'Casillas'],
    filas: [
      ['Velocidad normal', '6 por turno (9 m), partidas como quieras'],
      ['Correr (gastando la acción)', '12 en total'],
      ['Terreno difícil, trepar o nadar', 'Cada casilla cuenta doble'],
      ['Levantarte del suelo', 'Gastas 3 casillas de movimiento'],
      ['Saltar (con carrerilla)', 'Hasta 3 de largo (Fuerza DC 10 si hay peligro)'],
    ],
    notas: [],
  },
  {
    titulo: 'Alcance de las armas', emoji: '🎯', pagina: 3, cabecera: ['Casillas', 'Armas'], filas: armasFilas(),
    notas: ['Hasta el alcance, tiras normal; del alcance al doble, con desventaja; más lejos no llegas. Con un enemigo pegado, atacar a distancia también va con desventaja.'],
  },

  // ---------- Panel 4: los héroes ----------
  {
    titulo: 'Los 10 héroes (nivel 1)', emoji: '🦸', pagina: 4, cabecera: ['Héroe', '❤️', '🛡️', 'Arma 1 · Arma 2', 'Poder de nivel 1'],
    filas: clases.map((c) => [
      `${c.emoji} ${c.nombre}`, String(vida(c, 1)), String(defensa(c, 1)),
      c.armas.map((a) => `${a.nombre} d20${mas(ataqueArma(c, a, 1))}, ${a.dado}`).join(' · '),
      c.poderes[0].nombre,
    ]),
    notas: ['Daño de nivel 1: sin extra. Sube +1 en el nivel 2 y +2 en el nivel 4.'],
  },

  // ---------- Panel 5: números y descansos ----------
  {
    titulo: 'Qué suma cada héroe (nivel 1)', emoji: '🔢', pagina: 5, cabecera: ['Héroe', ...TALENTOS.map((t) => t.emoji), '💰 PO'],
    filas: clases.map((c) => [`${c.emoji} ${c.nombre}`, ...TALENTOS.map((t) => mas(suma(c, t.id, 1))), String(c.dinero)]),
    notas: ['Tirada = d20 + el número de la habilidad que pidas. 💰 = monedas de oro con las que empieza.'],
  },
  {
    titulo: 'Estados, descansos y suministros', emoji: '😴', pagina: 5,
    filas: [
      ['Petrificado', 'Es una estatua: no se mueve ni actúa.'],
      ['Dormido (a 0 vidas)', 'No actúa. Despierta si un amigo lo toca o al acabar el combate con 1 vida.'],
      ['Descanso corto', '1 hora: cada héroe recupera la mitad de sus vidas.'],
      ['Descanso largo', '8 horas: todas las vidas y los poderes «por aventura».'],
      ...SUMINISTROS.map((x) => [`${x.emoji} ${x.nombre}`, x.regla]),
      ['Subir de nivel', 'Un nivel al terminar cada aventura (o tras un combate importante).'],
    ],
    notas: [],
  },

  // ---------- Panel 6: tiradas ----------
  {
    titulo: 'Dificultades y dados', emoji: '🎲', pagina: 6,
    filas: [['Fácil', '5'], ['Normal', '10'], ['Difícil', '15'], ['Heroico', '20']],
    notas: [
      'Tirada = d20 + número de la habilidad. Si iguala o supera la dificultad, ¡éxito!',
      'Ventaja: dos d20 y vale el más alto. Desventaja: dos d20 y vale el más bajo.',
      '20 natural: crítico (el dado de daño se tira dos veces). 1 natural: pifia graciosa.',
    ],
  },
  {
    titulo: '¿Qué tirada pido?', emoji: '🧭', pagina: 6, cabecera: ['Habilidad', 'Ejemplos'],
    filas: [
      ['💪 Fuerza', 'Atletismo, trepar, empujar, romper'],
      ['🤸 Destreza', 'Acrobacias, juego de manos, sigilo, esquivar, disparar'],
      ['🧱 Constitución', 'Aguantar veneno, frío o cansancio'],
      ['🧠 Inteligencia', 'Arcanos, investigación, historia, acertijos'],
      ['🦉 Sabiduría', 'Percepción, supervivencia, medicina, intuición'],
      ['🗣️ Carisma', 'Persuasión, engaño, intimidación, actuar'],
    ],
    notas: [],
  },
];
