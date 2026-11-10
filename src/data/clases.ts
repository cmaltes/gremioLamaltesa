// Fichas del Gremio: 10 tipos de héroe, niveles 1 a 5.
// Reglas propias y muy simples: nada de calcular modificadores. Cada héroe tiene una
// tabla con el número FINAL que suma en cada tirada, nivel por nivel.
// Para añadir o ajustar una clase, edita solo este archivo (ver docs/fichas.md).

export type TalentoId = 'fuerza' | 'agilidad' | 'ingenio' | 'corazon';
export type Rango = 'fuerte' | 'bueno' | 'normal' | 'flojo';
export type Uso = 'siempre' | 'combate' | 'aventura';

export const NIVELES = [1, 2, 3, 4, 5] as const;

export const TALENTOS: { id: TalentoId; nombre: string; emoji: string; sirve: string }[] = [
  { id: 'fuerza', nombre: 'Fuerza', emoji: '💪', sirve: 'Golpear de cerca, empujar, romper cosas, trepar, levantar peso.' },
  { id: 'agilidad', nombre: 'Agilidad', emoji: '🏃', sirve: 'Disparar, esquivar, esconderse, equilibrio, juegos de manos.' },
  { id: 'ingenio', nombre: 'Ingenio', emoji: '🧠', sirve: 'Acertijos, magia, fijarse en detalles, recordar, abrir cerraduras.' },
  { id: 'corazon', nombre: 'Corazón', emoji: '❤️', sirve: 'Convencer, animar a los amigos, calmar animales, ser valiente.' },
];

/** Número que se suma en cada nivel (1 a 5) según lo bueno que seas en un talento. */
export const SUMA: Record<Rango, number[]> = {
  fuerte: [3, 3, 4, 4, 5],
  bueno: [2, 2, 2, 3, 3],
  normal: [1, 1, 1, 1, 2],
  flojo: [0, 0, 0, 0, 1],
};

/** Extra que se suma al dado de daño de cualquier arma, por nivel. */
export const EXTRA_DANO = [0, 1, 1, 2, 2];

export const RANGO_TEXTO: Record<Rango, string> = {
  fuerte: 'Fuerte',
  bueno: 'Bueno',
  normal: 'Normal',
  flojo: 'Flojo',
};

export const USO_TEXTO = (uso: Uso, veces = 1) =>
  uso === 'siempre' ? 'Siempre' : `${veces} ${veces === 1 ? 'vez' : 'veces'} por ${uso === 'combate' ? 'combate' : 'aventura'}`;

export interface Arma {
  nombre: string;
  emoji: string;
  dado: 'd4' | 'd6' | 'd8' | 'd10';
  alcance: 'cuerpo' | 'distancia';
  talento: TalentoId;
  nota: string;
}
export interface Poder {
  nivel: 1 | 3 | 5;
  nombre: string;
  texto: string;
  uso: Uso;
  veces?: number;
}
export interface Clase {
  slug: string;
  nombre: string;
  emoji: string;
  color: string;
  rol: string;
  dificultad: 1 | 2 | 3; // lo fácil que es de llevar: 1 = muy fácil
  frase: string;
  resumen: string;
  talentos: Record<TalentoId, Rango>;
  vida: [base: number, porNivel: number];
  defensa: number;
  armas: [Arma, Arma];
  poderes: [Poder, Poder, Poder];
  equipo: string[];
}

export const clases: Clase[] = [
  {
    slug: 'guerrero', nombre: 'Guerrero', emoji: '🛡️', color: '#3b82f6', rol: 'Protector del grupo', dificultad: 1,
    frase: '¡Detrás de mí, amigos!',
    resumen: 'Aguanta muchos golpes y protege al grupo. El mejor para empezar.',
    talentos: { fuerza: 'fuerte', agilidad: 'normal', ingenio: 'flojo', corazon: 'bueno' },
    vida: [14, 5], defensa: 16,
    armas: [
      { nombre: 'Espada ancha', emoji: '⚔️', dado: 'd8', alcance: 'cuerpo', talento: 'fuerza', nota: 'Tu golpe de siempre.' },
      { nombre: 'Jabalina', emoji: '🔱', dado: 'd6', alcance: 'distancia', talento: 'agilidad', nota: 'Se lanza lejos. Luego hay que recogerla.' },
    ],
    poderes: [
      { nivel: 1, nombre: '¡Detrás de mí!', texto: 'Un amigo a tu lado iba a recibir un golpe: te lo llevas tú, y el daño se reduce a la mitad.', uso: 'combate' },
      { nivel: 3, nombre: 'Guardia alta', texto: 'En vez de atacar, levantas el escudo: hasta tu próximo turno tu Defensa sube +2.', uso: 'siempre' },
      { nivel: 5, nombre: '¡Grito de valor!', texto: 'Todos tus amigos suman +2 a su siguiente tirada.', uso: 'combate' },
    ],
    equipo: ['Armadura de metal', 'Escudo redondo', 'Mochila con comida'],
  },
  {
    slug: 'barbaro', nombre: 'Bárbaro', emoji: '🪓', color: '#ef4444', rol: 'Gran golpeador', dificultad: 1,
    frase: '¡¡RAAAAAH!!',
    resumen: 'Pega más fuerte que nadie y casi no se cansa. Poca cabeza, mucho corazón.',
    talentos: { fuerza: 'fuerte', agilidad: 'bueno', ingenio: 'flojo', corazon: 'normal' },
    vida: [15, 5], defensa: 13,
    armas: [
      { nombre: 'Hachón a dos manos', emoji: '🪓', dado: 'd10', alcance: 'cuerpo', talento: 'fuerza', nota: 'El daño más alto de todos.' },
      { nombre: 'Hachas pequeñas', emoji: '🪃', dado: 'd6', alcance: 'distancia', talento: 'agilidad', nota: 'Las lanzas y vuelven a tu cinturón.' },
    ],
    poderes: [
      { nivel: 1, nombre: '¡Rugido de furia!', texto: 'Durante 3 turnos tus golpes hacen +2 de daño.', uso: 'combate' },
      { nivel: 3, nombre: 'Piel de roble', texto: 'Mientras estés furioso, a cada daño que recibas réstale 2.', uso: 'combate' },
      { nivel: 5, nombre: 'Furia imparable', texto: 'Si te quedas a 0 vidas, no caes: te levantas con 5 vidas.', uso: 'aventura' },
    ],
    equipo: ['Chaleco de pieles', 'Cuerno de beber', 'Cuerda larga'],
  },
  {
    slug: 'explorador', nombre: 'Explorador', emoji: '🏹', color: '#16a34a', rol: 'Tirador', dificultad: 2,
    frase: 'Hay huellas frescas por aquí…',
    resumen: 'Dispara desde lejos y encuentra el camino. Ojo de halcón.',
    talentos: { fuerza: 'normal', agilidad: 'fuerte', ingenio: 'bueno', corazon: 'flojo' },
    vida: [11, 4], defensa: 14,
    armas: [
      { nombre: 'Arco largo', emoji: '🏹', dado: 'd8', alcance: 'distancia', talento: 'agilidad', nota: 'Dispara a lo lejos.' },
      { nombre: 'Cuchillo de caza', emoji: '🔪', dado: 'd6', alcance: 'cuerpo', talento: 'agilidad', nota: 'Para cuando te alcanzan.' },
    ],
    poderes: [
      { nivel: 1, nombre: 'Ojo de halcón', texto: 'Repites un ataque con el arco que hayas fallado y te quedas con el mejor dado.', uso: 'combate' },
      { nivel: 3, nombre: 'Rastreador', texto: 'Tú y tus amigos sumáis +2 a buscar huellas, pistas y caminos.', uso: 'siempre' },
      { nivel: 5, nombre: 'Lluvia de flechas', texto: 'Con una sola acción disparas a 3 enemigos distintos.', uso: 'combate' },
    ],
    equipo: ['Capa verde', 'Carcaj con flechas', 'Mapa y brújula'],
  },
  {
    slug: 'picaro', nombre: 'Pícaro', emoji: '🗡️', color: '#6366f1', rol: 'Sigilo y trucos', dificultad: 3,
    frase: '¿Quién? ¿Yo? Yo no he sido.',
    resumen: 'Se esconde, abre cerraduras y golpea por sorpresa. Frágil pero astuto.',
    talentos: { fuerza: 'flojo', agilidad: 'fuerte', ingenio: 'bueno', corazon: 'normal' },
    vida: [10, 4], defensa: 14,
    armas: [
      { nombre: 'Daga', emoji: '🗡️', dado: 'd6', alcance: 'cuerpo', talento: 'agilidad', nota: 'Rápida y silenciosa.' },
      { nombre: 'Honda', emoji: '🪨', dado: 'd4', alcance: 'distancia', talento: 'agilidad', nota: 'Piedras para atacar sin ser visto.' },
    ],
    poderes: [
      { nivel: 1, nombre: 'Golpe a traición', texto: 'Si un amigo está pegado al enemigo, tu golpe hace +3 de daño.', uso: 'siempre' },
      { nivel: 3, nombre: 'Mano ligera', texto: 'Suma +5 a una tirada de esconderte, robar o abrir una cerradura.', uso: 'aventura', veces: 2 },
      { nivel: 5, nombre: 'Esquiva loca', texto: 'Un golpe que te iba a dar falla, sin tirada. ¡Te escurres!', uso: 'combate' },
    ],
    equipo: ['Capucha oscura', 'Ganzúas', 'Bolsa de bolitas para tropezar'],
  },
  {
    slug: 'mago', nombre: 'Mago', emoji: '🔮', color: '#a855f7', rol: 'Hechizos', dificultad: 3,
    frase: '¡Abracadabra… y un poco de suerte!',
    resumen: 'Poca vida pero muchísimo poder. Lanza chispas y resuelve acertijos.',
    talentos: { fuerza: 'flojo', agilidad: 'normal', ingenio: 'fuerte', corazon: 'bueno' },
    vida: [8, 3], defensa: 11,
    armas: [
      { nombre: 'Varita de chispas', emoji: '🪄', dado: 'd8', alcance: 'distancia', talento: 'ingenio', nota: 'Lanza chispas mágicas. Nunca se acaban.' },
      { nombre: 'Bastón brillante', emoji: '🔆', dado: 'd6', alcance: 'cuerpo', talento: 'ingenio', nota: 'Golpea con magia: usa tu Ingenio.' },
    ],
    poderes: [
      { nivel: 1, nombre: 'Escudo mágico', texto: 'Un golpe que te iban a dar: tu Defensa sube +4 solo contra ese golpe.', uso: 'combate' },
      { nivel: 3, nombre: 'Bola de fuego', texto: 'Todos los enemigos juntos en un círculo de 3 casillas pierden 6 vidas. Sin tirada.', uso: 'combate' },
      { nivel: 5, nombre: 'Sueño profundo', texto: 'Hasta 3 enemigos con pocas vidas (10 o menos) se quedan dormidos.', uso: 'aventura' },
    ],
    equipo: ['Túnica con estrellas', 'Libro de hechizos', 'Gato negro (opcional)'],
  },
  {
    slug: 'clerigo', nombre: 'Clérigo', emoji: '✨', color: '#f59e0b', rol: 'Sanador y apoyo', dificultad: 2,
    frase: 'Tranquilo, ya estoy aquí.',
    resumen: 'Cura a los amigos y brilla contra la oscuridad. Todo grupo lo quiere.',
    talentos: { fuerza: 'normal', agilidad: 'flojo', ingenio: 'bueno', corazon: 'fuerte' },
    vida: [11, 4], defensa: 14,
    armas: [
      { nombre: 'Maza de luz', emoji: '🔨', dado: 'd6', alcance: 'cuerpo', talento: 'fuerza', nota: 'Una maza que brilla al golpear.' },
      { nombre: 'Rayo de luz', emoji: '🌟', dado: 'd6', alcance: 'distancia', talento: 'corazon', nota: 'Sale de tus manos. Nunca se acaba.' },
    ],
    poderes: [
      { nivel: 1, nombre: 'Manos de luz', texto: 'Tocas a un amigo y recupera 5 vidas.', uso: 'combate', veces: 2 },
      { nivel: 3, nombre: 'Bendición', texto: 'Hasta tu próximo turno, 3 amigos suman +2 a todas sus tiradas.', uso: 'combate' },
      { nivel: 5, nombre: 'Luz que despierta', texto: 'Un amigo dormido (a 0 vidas) se levanta con la mitad de su vida.', uso: 'aventura' },
    ],
    equipo: ['Túnica blanca', 'Símbolo de sol', 'Vendas y pociones de manzanilla'],
  },
  {
    slug: 'druida', nombre: 'Druida', emoji: '🌿', color: '#65a30d', rol: 'Magia de la naturaleza', dificultad: 3,
    frase: '¿Oyes eso? Es el bosque hablando.',
    resumen: 'Habla con los animales y se convierte en oso. Un poco mago, un poco fiera.',
    talentos: { fuerza: 'bueno', agilidad: 'flojo', ingenio: 'normal', corazon: 'fuerte' },
    vida: [10, 4], defensa: 12,
    armas: [
      { nombre: 'Bastón florido', emoji: '🌱', dado: 'd8', alcance: 'cuerpo', talento: 'fuerza', nota: 'Del tamaño de un remo.' },
      { nombre: 'Semillas espinosas', emoji: '🌰', dado: 'd6', alcance: 'distancia', talento: 'corazon', nota: 'El bosque te obedece: usa tu Corazón.' },
    ],
    poderes: [
      { nivel: 1, nombre: 'Amigo del bosque', texto: 'Hablas con los animales. Un pájaro distrae a un enemigo: falla su siguiente ataque.', uso: 'combate' },
      { nivel: 3, nombre: 'Forma de oso', texto: 'Te conviertes en oso: ganas 10 vidas extra y tu ataque es un zarpazo d10 con Fuerza.', uso: 'aventura' },
      { nivel: 5, nombre: 'Muro de zarzas', texto: 'Hasta 3 enemigos se enredan y pierden su siguiente turno.', uso: 'combate' },
    ],
    equipo: ['Capa de hojas', 'Flauta de madera', 'Bolsa de bayas'],
  },
  {
    slug: 'bardo', nombre: 'Bardo', emoji: '🎶', color: '#ec4899', rol: 'Músico y animador', dificultad: 2,
    frase: '¡Y ahora, un cuentito!',
    resumen: 'Canta, anima y deja con la boca abierta a los enemigos. El alma del grupo.',
    talentos: { fuerza: 'flojo', agilidad: 'bueno', ingenio: 'normal', corazon: 'fuerte' },
    vida: [10, 4], defensa: 13,
    armas: [
      { nombre: 'Estoque', emoji: '🤺', dado: 'd6', alcance: 'cuerpo', talento: 'agilidad', nota: 'Una espada fina y elegante.' },
      { nombre: 'Cuchillos de malabar', emoji: '🤹', dado: 'd4', alcance: 'distancia', talento: 'agilidad', nota: 'Los lanzas y los recoges al vuelo.' },
    ],
    poderes: [
      { nivel: 1, nombre: 'Canción de ánimo', texto: 'Un amigo suma +3 a su siguiente tirada.', uso: 'combate', veces: 2 },
      { nivel: 3, nombre: 'Burla ingeniosa', texto: 'Insultas con gracia a un enemigo: su próximo ataque falla.', uso: 'combate' },
      { nivel: 5, nombre: '¡Gran final!', texto: 'Todos tus amigos recuperan 5 vidas y repiten una tirada que hayan fallado.', uso: 'aventura' },
    ],
    equipo: ['Laúd', 'Sombrero con pluma', 'Cuaderno de canciones'],
  },
  {
    slug: 'monje', nombre: 'Monje', emoji: '🥋', color: '#0d9488', rol: 'Luchador veloz', dificultad: 2,
    frase: 'Primero respira. Después, ¡pum!',
    resumen: 'Sin armadura, pero tan rápido que casi nadie le toca. Pega con puños y bastón.',
    talentos: { fuerza: 'bueno', agilidad: 'fuerte', ingenio: 'normal', corazon: 'flojo' },
    vida: [11, 4], defensa: 15,
    armas: [
      { nombre: 'Puños veloces', emoji: '👊', dado: 'd6', alcance: 'cuerpo', talento: 'agilidad', nota: 'No necesitas llevar nada.' },
      { nombre: 'Bastón largo', emoji: '🥢', dado: 'd8', alcance: 'cuerpo', talento: 'fuerza', nota: 'Llega a 2 casillas de distancia.' },
    ],
    poderes: [
      { nivel: 1, nombre: 'Paso de viento', texto: 'Te mueves el doble de lejos y puedes correr por paredes bajas.', uso: 'siempre' },
      { nivel: 3, nombre: 'Golpe aturdidor', texto: 'Si aciertas, el enemigo pierde su siguiente turno.', uso: 'combate' },
      { nivel: 5, nombre: 'Mil puños', texto: 'Atacas 3 veces seguidas en una sola acción.', uso: 'combate' },
    ],
    equipo: ['Cinta en la frente', 'Ropa cómoda', 'Cantimplora'],
  },
  {
    slug: 'paladin', nombre: 'Paladín', emoji: '⚜️', color: '#eab308', rol: 'Caballero de la luz', dificultad: 2,
    frase: '¡Por la luz y por mis amigos!',
    resumen: 'Guerrero valiente con poderes de luz. Golpea fuerte y da ánimos con su ejemplo.',
    talentos: { fuerza: 'fuerte', agilidad: 'flojo', ingenio: 'normal', corazon: 'bueno' },
    vida: [13, 5], defensa: 16,
    armas: [
      { nombre: 'Espada sagrada', emoji: '⚔️', dado: 'd8', alcance: 'cuerpo', talento: 'fuerza', nota: 'Brilla suavemente cuando hay peligro.' },
      { nombre: 'Lanza de luz', emoji: '🔱', dado: 'd6', alcance: 'distancia', talento: 'corazon', nota: 'La lanzas y vuelve a tu mano.' },
    ],
    poderes: [
      { nivel: 1, nombre: 'Golpe sagrado', texto: 'Tu siguiente golpe que acierte brilla y hace +4 de daño.', uso: 'combate' },
      { nivel: 3, nombre: 'Aura de valor', texto: 'Tus amigos a 1 casilla de ti suman +1 a su Defensa.', uso: 'siempre' },
      { nivel: 5, nombre: 'Juramento de luz', texto: 'Un amigo recupera 10 vidas y tú recuperas 5.', uso: 'aventura' },
    ],
    equipo: ['Armadura plateada', 'Escudo con un sol', 'Capa blanca'],
  },
];

export const porSlug = (slug: string) => clases.find((c) => c.slug === slug);

export const suma = (c: Clase, t: TalentoId, nivel: number) => SUMA[c.talentos[t]][nivel - 1];
export const vida = (c: Clase, nivel: number) => c.vida[0] + c.vida[1] * (nivel - 1);
export const defensa = (c: Clase, nivel: number) => c.defensa + (nivel >= 4 ? 1 : 0);
export const extraDano = (nivel: number) => EXTRA_DANO[nivel - 1];
export const ataqueArma = (c: Clase, a: Arma, nivel: number) => suma(c, a.talento, nivel);
