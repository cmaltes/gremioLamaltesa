// Pequeñas mejoras de uso en móvil. Todo es opcional: la web funciona sin JavaScript.
const guardar = (k: string, v?: string) => {
  try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch { /* modo privado */ }
  return null;
};

/* ---------- Visor de imágenes y mapas con zoom ---------- */
function visor() {
  const enlaces = document.querySelectorAll<HTMLAnchorElement>('a[data-zoom]');
  if (!enlaces.length) return;
  const d = document.createElement('dialog');
  d.className = 'visor';
  d.innerHTML = `<div class="visor-barra"><strong class="visor-titulo"></strong>
    <button type="button" data-z="-" aria-label="Alejar">−</button>
    <button type="button" data-z="+" aria-label="Acercar">+</button>
    <a class="visor-bajar" download aria-label="Descargar">⤓</a>
    <button type="button" data-z="x" aria-label="Cerrar">✕</button></div>
    <div class="visor-lienzo"><img alt=""></div>`;
  document.body.append(d);
  const img = d.querySelector('img')!;
  const bajar = d.querySelector<HTMLAnchorElement>('.visor-bajar')!;
  const pasos = [100, 160, 250, 400];
  let i = 0;
  const poner = () => { img.style.width = pasos[i] + '%'; };
  enlaces.forEach((a) =>
    a.addEventListener('click', (e) => {
      e.preventDefault();
      img.src = a.href; img.alt = a.dataset.titulo || '';
      bajar.href = a.href;
      d.querySelector('.visor-titulo')!.textContent = a.dataset.titulo || '';
      i = 0; poner(); d.showModal();
    }),
  );
  d.addEventListener('click', (e) => {
    const z = (e.target as HTMLElement).closest('[data-z]')?.getAttribute('data-z');
    if (z === 'x' || e.target === d) d.close();
    if (z === '+') i = Math.min(i + 1, pasos.length - 1);
    if (z === '-') i = Math.max(i - 1, 0);
    if (z === '+' || z === '-') poner();
    if (e.target === img) { i = (i + 1) % pasos.length; poner(); }
  });
}

/* ---------- Filtros de la portada ---------- */
function filtros() {
  const chips = document.querySelectorAll<HTMLButtonElement>('[data-filtro]');
  const tarjetas = document.querySelectorAll<HTMLElement>('[data-publico]');
  chips.forEach((c) =>
    c.addEventListener('click', () => {
      chips.forEach((x) => x.setAttribute('aria-pressed', String(x === c)));
      const f = c.dataset.filtro!;
      tarjetas.forEach((t) => { t.hidden = !(f === 'todas' || t.dataset.publico === f || t.dataset.publico === 'familia'); });
    }),
  );
}

/* ---------- Navegación de la aventura: resalta la sección visible ---------- */
function seccionActiva() {
  const links = [...document.querySelectorAll<HTMLAnchorElement>('.pestanas a')];
  if (!links.length || !('IntersectionObserver' in window)) return;
  const mapa = new Map(links.map((l) => [l.hash.slice(1), l]));
  const obs = new IntersectionObserver(
    (es) => es.forEach((e) => {
      if (!e.isIntersecting) return;
      links.forEach((l) => l.removeAttribute('aria-current'));
      const l = mapa.get(e.target.id);
      l?.setAttribute('aria-current', 'true');
      l?.scrollIntoView({ inline: 'center', block: 'nearest' });
    }),
    { rootMargin: '-30% 0px -60% 0px' },
  );
  mapa.forEach((_, id) => { const s = document.getElementById(id); if (s) obs.observe(s); });
}

/* ---------- Lector del guion: tamaño de letra y pantalla encendida ---------- */
function lector() {
  const guion = document.querySelector<HTMLElement>('.guion');
  if (!guion) return;
  let tam = Number(guardar('gremio-tam')) || 0;
  const aplicar = () => { guion.style.fontSize = `${1 + tam * 0.1}em`; };
  aplicar();
  document.querySelector('[data-letra="+"]')?.addEventListener('click', () => { tam = Math.min(tam + 1, 5); guardar('gremio-tam', String(tam)); aplicar(); });
  document.querySelector('[data-letra="-"]')?.addEventListener('click', () => { tam = Math.max(tam - 1, -2); guardar('gremio-tam', String(tam)); aplicar(); });

  const b = document.querySelector<HTMLButtonElement>('[data-pantalla]');
  if (!b) return;
  if (!('wakeLock' in navigator)) { b.hidden = true; return; }
  let cerrojo: WakeLockSentinel | null = null;
  const pedir = async () => { try { cerrojo = await navigator.wakeLock.request('screen'); cerrojo.addEventListener('release', () => { cerrojo = null; }); } catch { /* sin permiso */ } };
  b.addEventListener('click', async () => {
    if (cerrojo) { await cerrojo.release(); b.setAttribute('aria-pressed', 'false'); }
    else { await pedir(); b.setAttribute('aria-pressed', String(!!cerrojo)); }
  });
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && b.getAttribute('aria-pressed') === 'true') pedir(); });
}

/* ---------- Música: carátula en la pantalla de bloqueo y una sola pista a la vez ---------- */
function musica() {
  const audios = document.querySelectorAll<HTMLAudioElement>('audio[data-titulo]');
  audios.forEach((a) => {
    a.addEventListener('play', () => {
      audios.forEach((o) => o !== a && o.pause());
      if ('mediaSession' in navigator) {
        navigator.mediaSession.metadata = new MediaMetadata({
          title: a.dataset.titulo, artist: 'El Gremio',
          artwork: a.dataset.caratula ? [{ src: a.dataset.caratula, sizes: '360x360', type: 'image/jpeg' }] : [],
        });
      }
    });
  });
}

/* ---------- Fichas: elegir nivel y ver todos los números a la vez ---------- */
function fichas() {
  const ficha = document.querySelector<HTMLElement>('[data-ficha]');
  if (!ficha) return;
  const clave = `gremio-nivel-${ficha.dataset.ficha}`;
  const botones = ficha.querySelectorAll<HTMLButtonElement>('[data-nivel]');
  const poner = (n: number) => {
    ficha.dataset.activo = String(n);
    botones.forEach((b) => b.setAttribute('aria-pressed', String(Number(b.dataset.nivel) === n)));
    ficha.querySelectorAll<HTMLElement>('[data-n1]').forEach((e) => { e.textContent = e.dataset['n' + n] ?? ''; });
    ficha.querySelectorAll<HTMLElement>('[data-desde]').forEach((e) => { e.classList.toggle('bloqueado', Number(e.dataset.desde) > n); });
    ficha.querySelectorAll<HTMLElement>('tr[data-fila]').forEach((e) => { e.classList.toggle('actual', Number(e.dataset.fila) === n); });
    guardar(clave, String(n));
  };
  botones.forEach((b) => b.addEventListener('click', () => poner(Number(b.dataset.nivel))));
  poner(Number(guardar(clave)) || 1);
  document.querySelector('[data-imprimir]')?.addEventListener('click', () => window.print());
}

visor(); filtros(); seccionActiva(); lector(); musica(); fichas();
