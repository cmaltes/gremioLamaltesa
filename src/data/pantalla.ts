// Tarjetas generales de la pantalla del master (valen para cualquier aventura).
// Cada aventura añade las suyas en la cabecera de aventura.md (campo `pantalla`).
export interface Tarjeta { titulo: string; emoji?: string; cabecera?: string[]; filas: string[][]; notas: string[]; pagina?: number }

// Títulos de los 5 paneles (hojas A4 verticales) de la pantalla del master de una aventura.
export const titulosPaneles = ['Antes de empezar', 'La feria', 'Tienda y cueva', 'Combate', 'Reglas y apuros'];

export const tarjetasGenerales: Tarjeta[] = [
  {
    titulo: 'Dificultades', emoji: '🎲', pagina: 5,
    filas: [['Fácil', '5'], ['Normal', '10'], ['Difícil', '15'], ['Heroico', '20']],
    notas: [
      'Tirada = d20 + número de la habilidad. Si iguala o supera la dificultad, ¡éxito!',
      'Ventaja: dos d20 y vale el más alto. Desventaja: dos d20 y vale el más bajo.',
      '20 natural: crítico (el dado de daño se tira dos veces). 1 natural: pifia graciosa.',
    ],
  },
  {
    titulo: 'Combate', emoji: '⚔️', pagina: 4,
    filas: [
      ['Tu turno', 'Moverte y hacer 1 acción: atacar, poder, ayudar, esconderte…'],
      ['Atacar', 'd20 + número del arma. Si iguala o supera la Defensa del enemigo, acierta.'],
      ['Daño', 'Dado del arma + extra de nivel.'],
      ['Ayudar', 'Un amigo que ayuda da ventaja a la tirada.'],
      ['A 0 vidas', 'Se duerme (no muere). Un amigo lo despierta o vuelve con 1 vida al acabar.'],
    ],
    notas: [],
  },
  {
    titulo: '¿Qué tirada pido?', emoji: '🧭', pagina: 5,
    cabecera: ['Habilidad', 'Ejemplos'],
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
  {
    titulo: 'Estados y descansos', emoji: '😴', pagina: 4,
    filas: [
      ['Petrificado', 'Es una estatua: no se mueve ni actúa. Lo cura el Solvente.'],
      ['Dormido', 'No actúa. Despierta si lo sacuden o le hacen daño.'],
      ['Descanso corto', '1 hora: cada héroe recupera la mitad de sus vidas.'],
      ['Descanso largo', '8 horas: todas las vidas y los poderes «por aventura».'],
      ['Subir de nivel', 'Un nivel al terminar cada aventura (o tras un combate importante).'],
    ],
    notas: [],
  },
];
