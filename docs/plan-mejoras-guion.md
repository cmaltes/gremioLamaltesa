# Plan de mejoras de «La Feria del Misterio»

Plan en 4 fases pensadas para hacer `/clear` entre ellas. Cada fase termina con `npm run build`, revisión rápida y commit. Archivo principal: `src/content/aventuras/la-feria-del-misterio/aventura.md`.

## Decisiones ya tomadas (Fernando, 12-nov-2026)

- **Fallo 1 (Sueño):** el pergamino funciona contra el Oso Lechuza (dormido 1 minuto), se dice expresamente.
- **Fallo 2 (combate final):** más vidas; Alarico, Glitch y Mizzen pelean **a la vez**; Alarico tiene un efecto distinto o extra (por ejemplo, uno por ronda o por mitad de vidas).
- **Jaula:** NO se abre sola al morir Alarico. Se abre con la **Llave de la Jaula** que suelta Alarico (ya existe en el guion; hay que quitar lo de que Aerion vuelve a ser humano solo al caer Alarico, o decidir en qué momento exacto se rompe la maldición).
- **Kobolds corruptos:** salen con su aspecto corrupto en la emboscada (Gart y Zash) y al volver a la feria tras el oso (Alarico, Glitch, Mizzen). Escena nueva «se rompe el engaño» y, en la emboscada, una tirada de dado para insinuar que «os suenan las caras».
- **Acertijos (fallo 5):** se dejan como están.
- **No** añadir pista de que Alarico miente: la balada basta.
- **Robar:** la consecuencia de que te pillen es **perder monedas** (no desventaja).
- **Ganar monedas:** ejercicios de clase y juego de preguntas.
- **Lucimiento de clase:** tiradas concretas de habilidad que **solo puede intentar un héroe** (el de esa clase).
- **Aerion** reacciona al acercarse a la jaula o al hablar cerca de ella: protesta cuando habla Alarico y se calma con la balada.
- **Escalado** según número de jugadores (3 y 5).
- **Gancho de continuación** al final.
- **Material:** cartas de objeto, material físico de los acertijos, tabla «¿Qué pasa en la feria?», música por escena, hoja de seguimiento del master.

### Estado
- **Fase 1: hecha el 12-nov-2026** (gancho = opción A, el cartel; escrito en el guion, con tabla de lucimientos, monedas, Aerion y sucesos de la feria). Falta la carta imprimible del cartel: va en la fase 3 junto a las cartas de objeto (el cartel se entrega a cada héroe en su inventario).
- **Fase 2: hecha el 12-nov-2026.** Kobolds corruptos en la emboscada (DC 12 «os suenan las caras»), Sueño funciona con el oso, escena «se rompe el engaño» con mapa y tokens corruptos, combate final simultáneo (Alarico 30 vidas con Rayo gris y Furia de terciopelo; Glitch y Mizzen 8), la jaula solo se abre con la Llave y ahí cae la maldición, escalado 3/5 jugadores, gancho de continuación (carta de la «Dama de los Mil Velos») y pantalla del master actualizada. Falta en la fase 3 la carta de la Llave de la Jaula y la carta de la carta sellada.
- **Fase 4: hecha el 12-nov-2026.** Reproductor fijo de música por escena (solo tras confirmar «Soy el master», carga bajo demanda, campo `escena` en `musica`) y hoja de seguimiento A4 de 2 hojas en `/aventuras/<slug>/seguimiento/` + PDF (campo `seguimiento` en la cabecera; incluye lucimientos y la tabla «¿Qué pasa en la feria?» leídos del guion).

### Qué es la tabla «¿Qué pasa en la feria?»
Una lista de 8 sucesos pequeños de feria. Cuando la mesa se atasca, se dispersa o hay un hueco, el master tira 1d8 (o elige) y ocurre algo: un niño pierde un globo, un malabarista pide ayuda, un kobold gasta una broma… Sirve para improvisar sin pensar, repartir pistas y dar ambiente. Unos sucesos son pura risa; otros dan monedas o empujan hacia una atracción que no han visitado.

---

## Fase 1 · Capítulo 1: gancho, monedas, robo, lucimientos y Aerion

Solo toca el capítulo 1 (festival) y la parte de personajes.

1. **Gancho inicial.** Proponer 3 opciones a Fernando y que elija antes de escribir. Borrador de opciones:
   - **A. El cartel.** Cada héroe encuentra el mismo cartel dorado en su pueblo (Festival de los Mil Velos, «entrada: una historia»). Llegan siguiendo las farolas que brillan sin velas.
   - **B. El mercader del camino.** Los héroes escoltan una carreta con globos y chucherías; las ruedas se atascan junto a una feria que no estaba en el mapa el día anterior.
   - **C. El recado del pueblo.** El alcalde pide a los héroes que averigüen por qué desaparecen los niños que van a la feria por la noche (no desaparecen, vuelven riendo y sin recordar nada) o que traigan de allí una pieza que el pueblo ha perdido.
2. **Economía de monedas.** Comprobar cuánto dinero inicial tienen las fichas (`docs/fichas.md`) y cuánto cuestan las pruebas (1 PO por intento, llave 10 PO). Ajustar para que perder monedas duela sin bloquear.
3. **Robar a Mizzen:** si fallan, **pierden monedas** (cantidad por tirada) en lugar de desventaja; el objeto sigue sin entregarse.
4. **Ganar monedas.** Una sección «Cómo ganar monedas en la feria» con:
   - **Juego de preguntas** (el puesto de preguntas de la feria; 8-10 preguntas fáciles y divertidas con premio de 1-2 PO).
   - **Ejercicios de clase** (un reto por clase, p. ej. el Bardo canta, el Guerrero levanta el yunque, el Mago adivina el truco).
5. **Lucimiento de clase.** Tiradas concretas que solo puede intentar un héroe de esa clase en una escena (p. ej. Clérigo bendice la Poción, Pícaro abre el candado del carrusel, Explorador lee huellas, Mago nota el hechizo de la jaula, Druida habla con el búho). Cada una con texto de éxito y de fallo.
6. **Aerion junto a la jaula.** Texto de reacción: si Alarico habla cerca, Aerion gruñe y se agita; si suena la balada de Fliflas (o la cantan los héroes), se calma y levanta la cabeza. Con un efecto de juego pequeño (por ejemplo, ventaja a la primera tirada que hagan los héroes al acercarse durante la canción).
7. **Tabla «¿Qué pasa en la feria?»** (d8, 8 sucesos) al final del capítulo 1.

Cierre: build, relectura, commit. No tocar capítulos 2-3.

## Fase 2 · Capítulos 2 y 3: corrupción, combate final y cierre

1. **Emboscada:** Gart y Zash aparecen ya corruptos (ojos rojos, chispas verdes). Tirada de Inteligencia o Sabiduría (percepción/investigación) **DC 12**: «¡os suenan las caras!» (son los de la noria y el carrusel sin disfraz). Quitar el texto que dice que son los mismos.
2. **Oso Lechuza:** frase expresa de que el Pergamino de Dormir funciona (dormido 1 minuto o hasta que lo dañen).
3. **Escena «se rompe el engaño»** al volver a la feria: la feria cambia a `feria-maldita`; Alarico, Glitch y Mizzen aparecen corrompidos; sacan los muñecos y tokens corrompidos.
4. **Combate final reescrito:** Alarico, Glitch y Mizzen a la vez; más vidas (decidir cifras con el grupo de 4 de nivel 2); Alarico con un efecto o mecánica (por ronda o a mitad de vidas); la jaula, como elemento del combate si encaja (Glitch y Mizzen la sujetan).
5. **Jaula y llave:** quitar «se disuelve y Aerion vuelve a ser humano»; Alarico suelta la **Llave de la Jaula**, hay que abrir la jaula con ella y ahí cae la maldición (decidir si es al abrir o al caer Alarico y ajustar el texto de Aerion).
6. **Escalado según jugadores:** líneas de «3 jugadores» y «5 jugadores» (vidas y número de enemigos) en la emboscada, el oso y el combate final.
7. **Gancho de continuación** en el cierre (un objeto, un nombre o un mensaje sin resolver). Proponer 2-3 y decidir.
8. **Actualizar la pantalla del master** (`pantalla` en el front matter: enemigos y tiradas) con las nuevas cifras y reglas.

Cierre: build, regenerar PDF del guion y de la pantalla (`scripts/generar-pdfs.sh`), commit.

## Fase 3 · Material físico imprimible (HECHA el 12-nov-2026)

Generado con `tools/material_fisico.py` (HTML + Chrome) en `public/aventuras/la-feria-del-misterio/material/`: cartas de objeto (+ master con Llave de la Jaula y carta sellada), acertijos (+ master con soluciones) y tarjetas del Loro Pregonero. Los dibujos de las cartas son emojis; se pueden cambiar por ilustraciones.

Scripts en `tools/` (venv `tools/.venv`), salida en `public/aventuras/la-feria-del-misterio/` y enlaces en `descargas` del front matter.

1. **Cartas de objeto** (Poción, Mapa, Pergamino, Llave del Cofre, Llave de la Jaula, y las baratijas de Mizzen): frente con dibujo y nombre, dorso con texto de éxito y de fallo del guion (que el niño lee). PDF A4 de recortar.
2. **Material de los acertijos:** hoja de la diana (R, D, E, P, A, I), 8 carteles de la noria (un verso por cartel, para esconder en el mapa o en la mesa), 5 carteles del carrusel (palabra oculta). PDF A4 de recortar y versión master con las soluciones.
3. **Tarjetas del juego de preguntas** (si se añade en la fase 1): 8-10 cartas.
4. Añadir miniaturas y descargas a `aventura.md`; revisar a 100 % de escala.

Cierre: build, PDFs, commit.

## Fase 4 · Web: música por escena y hoja de seguimiento

1. **Música por escena.** Un reproductor fijo en la pestaña de la aventura (botón por escena: feria, bosque/cueva, combate final, balada) con reproducir/pausar y bucle, para no cambiar de pestaña. Móvil primero, sin descargar en bloque (carga bajo demanda).
2. **Hoja de seguimiento del master:** PDF A4 (y/o versión en pantalla) con PO gastadas por héroe, objetos conseguidos y quién los examinó, tiradas de lucimiento ya usadas, estado del combate.
3. Mostrar la tabla «¿Qué pasa en la feria?» también en la pantalla del master o como hoja aparte.
4. Si la web ya está en pestañas (ver tarea pendiente de pestañas en memoria), enlazar el reproductor y las nuevas descargas allí; si no, en la página actual.

Cierre: build, `scripts/generar-pdfs.sh`, comprobar en móvil, commit y push.

## Pendiente anterior (no mezclar)
Pestañas de la página de aventura (resumen sin spoilers, guía, personajes, descargas). Se puede hacer antes de la fase 4 para que el reproductor ya viva en su sitio definitivo.
