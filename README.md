# La casa en miniatura · juego 2D

Juego de plataformas en pixel art (pedido de la dueña, 2026-09-23). Franco, Alayna, Amanda, Keylin y Maritza se encogieron y
cruzan la casa en miniatura, con Marshall detrás: el patio, la cocina, la sala, el cuarto y el baño. Es un juego aparte del
modelo 3D (`../modelo-3d`).

**Versión en línea** (publicado a pedido de la dueña el 2026-09-24): https://wyvxl.github.io/casa-miniatura/ —
repositorio https://github.com/wyvxl/casa-miniatura (aparte del modelo 3D). El `.gitignore` deja fuera `referencias/`
(las hojas y dibujos de trabajo), `_revision/` y `herramientas/viejo/`. Para actualizar: `git add . && git commit -m "…" && git push`;
GitHub Pages tarda uno o dos minutos.

**Vista previa en WhatsApp** (2026-09-24): las etiquetas `og:` del `<head>` y `vista-previa.jpg` (1200 × 630: el patio con Franco
saltando sobre la leña y Marshall, sin botones ni marcador). WhatsApp guarda la vista previa de cada link por un tiempo.

## Cómo abrirlo

Doble clic en `index.html`. Funciona desde el disco (`file://`) y sin internet: nada de módulos, `fetch` ni CDNs. Por eso los
datos de los `.json` van juntos en `datos.js` (lo arma `herramientas/datos.py`).

En el teléfono: **tocar la pantalla salta** (al soltar, si el dedo no se movió) y **deslizar a un lado camina** para ese lado
mientras el dedo siga ahí (cada dedo va por su lado: con uno se camina y con otro se salta). Siguen los botones grandes (◀ ▶ abajo
a la izquierda, 👋 y ▲ a la derecha), pantalla completa al tocar *Jugar* y un aviso para girar el teléfono si está parado.
Arriba a la derecha: **cambiar de personaje** (con su carita), **pantalla completa** (no sale en el iPhone, Safari no lo permite),
sonido y menú. En la compu: ← → caminar, espacio / ↑ / W / Z saltar (más tiempo apretado, más alto),
H saludar, 1–5 cambiar de personaje, M sonido, Esc menú. También sirve un control de videojuego (palanca o cruz y botón A).

## Cómo se juega

- En cada cuarto hay **8 estrellas**, **monedas de colón** (de ₡1 y de ₡2), un **tesoro** (patio: la llave; cocina: la
  brújula; sala: el reloj de bolsillo; cuarto: el mapa; baño: la canica) y al final una **puertita de ratón** que lleva al siguiente cuarto.
- **Enemigos** (hoja `referencias/escenarios/enemigos.jpg`), uno o dos tipos por cuarto: patio, caracol arcoíris y
  saltamontes; cocina, gorgojo del café; sala, polilla (vuela); cuarto, oruga de seda; baño, rana de vidrio (brinca).
  Caminan, brincan o vuelan (`ENEMIGO` en `juego.js`). Si se les cae encima se aplastan (el caracol se mete en la concha,
  la oruga queda de capullo) y dan ₡2; si se chocan de lado quitan un corazón. **Peligros:** cactus (bajito, con espinas
  largas, para que se vea que pica) y trampas de mandíbula (el dibujo de la dueña, `referencias/patio/trampa.jpg`; solo muerde el centro, `zonaDano`, para que
  se pueda saltar). En el patio, una
  iguana toma sol en su piedra en la capa del medio, medio escondida entre el zacate. El **hongo rojo** es un trampolín y los
  **charcos** resbalan. Hay **3 corazones**; sin corazones se empieza el cuarto otra vez.
- **Marshall** sigue al personaje, salta si se queda atrás y ladra al empezar, al juntar el tesoro o las 8 estrellas y de vez en cuando.
- **Keylin** anda en el patio y **Maritza** está sentada en su butaca en la sala (si no son las que se juegan); saludan al pasar cerca.
- Música propia en cada cuarto y efectos de sonido, todo hecho con Web Audio en `sonido.js` (sin archivos de audio). El botón del parlante (en la esquina y en la portada) lo apaga, se tacha y lo recuerda; también la tecla M.

## Archivos

```
juego-2d/
├── index.html      portada, botones, estilos
├── juego.js        física, enemigos, cámara, dibujo, marcador, controles y las revisiones automáticas
├── niveles.js      qué hay en cada cuarto (cosas, enemigos, monedas, estrellas, tesoro, personajes)
├── sonido.js       música por cuarto y efectos (Web Audio)
├── datos.js        hecho por herramientas/datos.py
├── sprites/        tiras de cada personaje + sprites.json (tamaño de cuadro y animaciones)
├── escenarios/     capas de cada cuarto (<cuarto>/*.png), objetos.png (dibujados por código), cosas.png (de las hojas dibujadas) y sus .json
├── referencias/    imágenes de estilo y hojas dibujadas con IA que mandó la dueña (fuente de sprites y cosas)
├── herramientas/   los scripts de Python que arman todo lo anterior
└── _revision/      hojas agrandadas para revisar (no las usa el juego)
```

## Cómo se hizo cada cosa (y cómo volver a generarla)

Todo con Python 3 + Pillow + numpy (+ scipy para `recortar_objetos.py`). Desde `herramientas/`:

1. `python escenarios.py [cuarto …]` — pinta las capas de fondo con `pinta.py` (degradados tramados, follaje, esferas y
   cilindros sombreados, niebla por distancia). Cada capa mide 768 × 216, se repite de lado a lado y tiene su velocidad de
   paralaje (`factor`): pared o cielo 0.08, lejos 0.15, medio 0.4, cerca 0.7, piso 1 y *frente* 1.3 (pasa delante del personaje).
   El patio está en `escenarios.py` y los cuartos en `cuartos.py`, con los colores del modelo 3D (butacas terracota, camas
   salvia, gabinetes blancos con sobre oscuro, paredes marfil / verde agua / celeste).
2. `python recortar.py` — pasa las hojas de personajes dibujadas con IA (`referencias/Gemini_…sdplw5…` y `…ogdrr8…`) a pixel
   art de verdad: quita el fondo, corta cada figura, la achica con la **estatura de cada uno** (Franco 40 px, Alayna 43 con las
   orejitas, Amanda 47, Keylin 48, Maritza 52, Marshall 17), reduce a una paleta por personaje, le pone contorno y la acomoda por los pies.
   Las animaciones de cada uno están en `ANIMS`. `python recortar.py analizar` dibuja las cajas numeradas en `_revision/`.
3. `python recortar_objetos.py` — igual con las hojas de objetos (`…948k…` y `…9z4x…`): una caja por objeto en `COSAS`, con
   su tamaño en el juego y su tipo. Guarda de cada uno su **perfil** (la forma de arriba, por donde se camina) y su **pie** (lo
   que toca abajo). `HUNDIR` baja unos pixeles la superficie de lo que está dibujado en diagonal, para pisar el medio de la cara de arriba.
4. `python objetos.py` — objetos dibujados por código: piedra, ladrillo, matas con tallo, esponja, cereal, lata, cojín, libro
   acostado, cubo, lego, jabón, rollo, patito, tachuelas, puertita, corazones y la estrella que gira. Más los de
   `objetos_lado.py` (van en `comun`): macetas, taza con plato, frascos de especias, especiero, cubos con letras, carrito,
   legos de colores, libros parados y tabla de picar. **Las hojas de la dueña son solo idea**: lo que en ellas venía dibujado
   en diagonal (base ovalada, piezas de atrás más arriba) se veía despegado del piso, así que se redibujó de lado y con la base plana.
5. `python recortar_hojas.py` — las hojas de cosas por cuarto y de enemigos (`referencias/escenarios/*.jpg`): cada pieza
   se escoge por un punto dentro de su figura (`PIEZAS`; `python recortar_hojas.py analizar` numera las figuras en
   `_revision/hoja-*.png`), se pasa a su resolución de pixel art (un "pixel" del dibujo = `PP` px de la hoja) y, los muebles
   de fondo, se agrandan al doble. Lo blanco sobre fondo blanco se cierra y rellena (`BLANCOS`) y a lo que tiene el letrero
   pegado no se le juntan piezas vecinas (`SIN_LETRERO`). Salida: `escenarios/piezas/*.png` (una por pieza, para pintar los
   fondos) y `escenarios/piezas.png` + `piezas.json` (las que se juegan y los enemigos).
   - `muebles.py`: los muebles que en las hojas venían vistos desde arriba en diagonal (refri, cocina de gas, chorreador,
     cama, cómoda, baúl, mesa, taburete, cojín, inodoro, lavamanos, tele, y en el patio la leña, la parrilla, la silla azul y
     los bananos en su caja) están **redibujados de frente o de lado** para
     que el ángulo calce con el juego; reemplazan a los recortados con el mismo nombre. También el cactus bajito.
   - `cuartos2.py`: pinta la cocina, la sala, el cuarto y el baño con esas piezas (el patio sigue en `escenarios.py`).
6. `python datos.py` — junta los `.json` en `datos.js`. **Hay que correrlo después de cualquiera de los anteriores.**

Los sprites que hice primero por código (antes de las hojas de la dueña) están en `herramientas/viejo/`.

## Reglas de los niveles (`niveles.js`)

- Las cosas **no llevan altura**: cada una cae sobre lo que tenga debajo (el piso o una cosa anterior de la lista), así que
  para apilar se pone primero la de abajo. Así nada queda en el aire ni a pixeles de su apoyo (pedido de la dueña).
- Al abrir, `juego.js` revisa cada cuarto y avisa en la consola:
  - `revisarAlcance`: que **cada estrella, moneda y tesoro se pueda alcanzar** con el salto más bajo y la velocidad más
    baja (la de Maritza) y el personaje más bajito; de una cosa a otra calcula con física de verdad cuánto se avanza en
    el aire según lo que haya que subir (antes daba por buena cualquier distancia de hasta 70 px y se colaban saltos imposibles), subiendo por el perfil de las cosas (primero al capó y luego al techo del carro, por ejemplo);
  - `revisarApoyos`: que lo apilado se apoye en buena parte de su base y con el centro encima de lo que lo sostiene.
  - `revisarObstaculos`: que **todo lo que pica se pueda pasar**, saltando desde el piso o desde algo que esté antes.
  Después de cambiar un nivel, abrir la página y ver que la consola no diga *Fuera de alcance*, *Mal apoyado* ni *Obstáculo imposible*.
- Pocas cosas por cuarto (unas 16) y solo las típicas de cada lugar; los fondos, igual: no saturar (pedido de la dueña).
- Cada cosa lleva una sombrita de contacto en su base (sobre el piso o sobre lo que la sostiene), que la pega visualmente.
- Las capas de fondo no repiten objetos que se pueden pisar (si no, parece que resbalan, porque se mueven a otra velocidad).
- `hundir` en cada nivel: cuántos pixeles más adentro del piso se dibuja lo que se juega (cosas, personajes, enemigos),
  para que se vea parado sobre el piso y no en el borde con la pared (la cocina, 9; el patio, 2). Solo es visual.
- Los dibujos sueltos de `referencias/patio/` (bananos, leña, parrilla de ladrillo, banca, silla y ratonera) traen pintado
  el cuadriculado de "transparente"; `SUELTOS` en `recortar_hojas.py` lo quita y los deja del tamaño del juego. Los que ya
  son pixel art limpio (la trampa) se leen a su cuadrícula real (`NITIDOS`, tamaño de celda en px). `TAMANO` agranda alguna
  pieza de las hojas (las sillitas del cuarto, 1.3).
- Pantalla de 384 × 216, piso en y = 184, cada cuarto mide 2304 px (`LARGO`).

## Pendiente / ideas

- Probarlo en el teléfono de verdad (tamaño de los botones, que suene al tocar *Jugar* en el iPhone).
- Más cuartos: el corredor y el frente con la piedrilla, la losa, la casa amarilla de Keylin.
- Guardar el avance (estrellas y tesoros por cuarto) y una pantalla final con los cinco tesoros.
- Animaciones propias de saltar y caer (hoy usan cuadros de caminar) y de los enemigos (hoy se mecen).
