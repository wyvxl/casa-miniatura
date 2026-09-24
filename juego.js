// La casa en miniatura: el juego. Usa DATOS (datos.js), NIVELES (niveles.js) y SON (sonido.js).
'use strict';
const D = window.DATOS;
const cv = document.getElementById('c'), g = cv.getContext('2d');
const VW = 384, VH = 216, SUELO = 184, GRAV = 900;

// ---------- imágenes
const IMG = {};
function img(src) { if (!IMG[src]) { IMG[src] = new Image(); IMG[src].src = src; } return IMG[src]; }
for (const n in D.sprites) img('sprites/' + n + '.png');
const OBJ = img('escenarios/objetos.png'), COSAS = img('escenarios/cosas.png'), PIEZAS = img('escenarios/piezas.png');
for (const k in D.escenarios) D.escenarios[k].capas.forEach(c => img('escenarios/' + c.file));

// ---------- personajes: velocidad y salto (px/s). Maritza salta menos; el revisor de estrellas usa el salto más bajo.
const PJ = {
  franco:  { nombre: 'Franco',  vel: 110, salto: 330 },
  alayna:  { nombre: 'Alayna',  vel: 110, salto: 330 },
  amanda:  { nombre: 'Amanda',  vel: 118, salto: 330 },
  keylin:  { nombre: 'Keylin',  vel: 118, salto: 330 },
  maritza: { nombre: 'Maritza', vel: 92,  salto: 330 },
};
const REBOTE = 480;
// Enemigos (de referencias/escenarios/enemigos.jpg): cuadros, el cuadro cuando se aplastan y cómo se mueven
//   camina: va y viene por el piso · salta: da brincos hacia adelante · vuela: va y viene en el aire, subiendo y bajando
const ENEMIGO = {
  caracol:     { f: ['caracol1'], muerto: 'caracol2', modo: 'camina', vel: 12 },
  gorgojo:     { f: ['gorgojo1'], muerto: 'gorgojo2', modo: 'camina', vel: 32, patitas: true },
  oruga:       { f: ['oruga1'], muerto: 'oruga2', modo: 'camina', vel: 14, estira: true },
  larva:       { f: ['larva1'], muerto: 'larva_puf', modo: 'camina', vel: 9, estira: true },
  rana:        { f: ['rana1'], muerto: 'rana2', modo: 'salta', vel: 60, brinco: 250, espera: 1.1 },
  saltamontes: { f: ['salta1', 'salta2'], muerto: 'salta2', modo: 'salta', vel: 80, brinco: 300, espera: 0.8 },
  polilla:     { f: ['polilla1'], muerto: 'polilla2', modo: 'vuela', vel: 34 },
};

// Busca un objeto por nombre: "o:xxx" en los dibujados por código (del cuarto o comunes), si no en las hojas dibujadas
function pieza(nombre, cuarto) {
  if (nombre.startsWith('o:')) {
    const n = nombre.slice(2), O = D.objetos.objetos;
    const m = (O[cuarto] && O[cuarto][n]) || O.comun[n];
    return m && { hoja: OBJ, ...m, tipo: m.tipo || (['tachuelas', 'cactus', 'trampa'].includes(n) ? 'peligro' : 'plataforma') };
  }
  if (nombre.startsWith('p:')) {        // de las hojas de cada cuarto (recortar_hojas.py)
    const m = D.piezas[nombre.slice(2)];
    return m && { hoja: PIEZAS, ...m };
  }
  const m = D.cosas[nombre];
  return m && { hoja: COSAS, ...m };
}

// ---------- estado
const S = {
  quien: guardado('casa2d-quien') || 'franco', cuarto: 'patio', t: 0, jugando: false,
  p: null, perro: null, cam: 0, cosas: [], enem: [], mon: [], est: [], tes: null, puerta: null,
  vidas: 3, colones: 0, junto: 0, ladridoT: 8, fin: 0, parti: [],
};
if (!PJ[S.quien]) S.quien = 'franco';
function guardado(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function guardar(k, v) { try { localStorage.setItem(k, v); } catch (e) { } }

function nuevoJugador() {
  return { x: 50, y: SUELO, vx: 0, vy: 0, piso: true, mira: 1, hola: 0, tAnim: 0, inv: 0, golpe: 0, suelto: 0, coyote: 0, buffer: 0, enCharco: false };
}

// Pone cada cosa sobre lo que tenga debajo (el piso u otra cosa ya puesta): nada queda en el aire ni a
// pixeles de su apoyo. Se apoya en el punto más alto que encuentre bajo su base (el "pie").
const SOLIDO = t => t === 'plataforma' || t === 'rebote';
function superficie(q, x) {                 // y del mundo donde se pisa q en la columna x (o null)
  const i = Math.round(x - q.x);
  if (i < 0 || i >= q.w) return null;
  const v = q.o.perfil[i];
  return v < 0 ? null : q.y + v;
}
// Lo que lastima de un peligro: en los anchos (la trampa) solo el centro, las mandíbulas; los extremos son base plana
function zonaDano(q) {
  const m = q.w > 40 ? q.w * 0.22 : 5;
  return [q.x + m, q.x + q.w - m];
}
function colocar(cuarto) {
  const lista = [];
  for (const [n, x, forzar] of NIVELES[cuarto].cosas) {
    const o = pieza(n, cuarto);
    if (!o) { console.warn('No existe', n); continue; }
    const tipo = forzar || o.tipo;
    let base = SUELO;
    if (tipo === 'charco') base = SUELO + o.h - 4;          // el charco va pintado sobre el piso
    else if (tipo !== 'adorno') {
      for (const q of lista) {
        if (!SOLIDO(q.tipo)) continue;
        for (let c = x + o.pie[0]; c <= x + o.pie[1]; c++) {
          const s = superficie(q, c);
          if (s != null && s < base) base = s;
        }
      }
    }
    lista.push({ n, o, x, y: base - o.h, w: o.w, h: o.h, tipo });
  }
  return lista;
}

function cargarCuarto(id) {
  S.cuarto = id;
  const N = NIVELES[id];
  S.cosas = colocar(id);
  S.enem = N.enemigos.map(([n, x, rango, alto]) => {
    const E = ENEMIGO[n], o = pieza('p:' + E.f[0], id), y = SUELO - (alto || 0);
    return { n, E, o, x0: x, x1: x + rango, x: x + Math.random() * rango, y, y0: y, vy: 0, dir: Math.random() < 0.5 ? 1 : -1,
      vivo: true, aplast: 0, espera: Math.random(), t: Math.random() * 6, suelo: true };
  });
  S.mon = [];
  N.monedas.forEach(([x, alto, n]) => { for (let i = 0; i < n; i++) S.mon.push({ x: x + i * 16, y: SUELO - alto - 8, ok: false, dos: (i + x) % 5 === 0 }); });
  S.est = N.estrellas.map(([x, alto]) => ({ x, y: SUELO - alto - 10, ok: false }));
  const [tn, tx, ta] = N.tesoro;
  S.tes = { o: pieza(tn, id), n: tn, x: tx, y: SUELO - ta - 10, ok: false };
  S.puerta = { o: pieza('o:puertita', id), x: LARGO - 70 };
  S.junto = 0; S.vidas = 3; S.fin = 0; S.parti = [];
  S.p = nuevoJugador();
  S.perro = { x: 22, y: SUELO, vx: 0, vy: 0, mira: 1, tAnim: 0 };
  S.cam = 0;
  SON.musica(N.musica);
  marcar();
  cartel(N.nombre, 'Junta las 8 estrellas y encuentra el tesoro', 1800);
}

// ---------- avisos en pantalla (DOM, encima del juego)
const avisoEl = document.getElementById('aviso');
let avisoT = 0;
function cartel(t, s, ms, boton) {
  document.getElementById('aviso-t').textContent = t;
  document.getElementById('aviso-s').textContent = s;
  const b = document.getElementById('aviso-b');
  b.hidden = !boton;
  if (boton) { b.textContent = boton.txt; b.onclick = () => { avisoEl.hidden = true; boton.fn(); }; }
  avisoEl.hidden = false;
  clearTimeout(avisoT);
  if (ms) avisoT = setTimeout(() => { avisoEl.hidden = true; }, ms);
}
function marcar() { /* el marcador se dibuja en el lienzo; aquí solo guardamos el personaje */ guardar('casa2d-quien', S.quien); }

// ---------- controles: teclado, botones de pantalla y control de videojuego
const K = {};
let saltoApretado = false;
function apretarSalto() { saltoApretado = true; if (S.p) S.p.buffer = 0.12; }
function soltarSalto() { saltoApretado = false; }
addEventListener('keydown', e => {
  if (!S.jugando) return;
  if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', ' '].includes(e.key)) e.preventDefault();
  if (!K[e.key]) {
    if (e.key === ' ' || e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W' || e.key === 'z' || e.key === 'Z') apretarSalto();
    if (e.key === 'h' || e.key === 'H') saludar();
    if (e.key === 'm' || e.key === 'M') alternarSonido();
    if (e.key === 'Escape') menu();
    const n = parseInt(e.key, 10);
    if (n >= 1 && n <= 5) elegir(Object.keys(PJ)[n - 1]);
  }
  K[e.key] = true;
});
addEventListener('keyup', e => {
  K[e.key] = false;
  if (e.key === ' ' || e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W' || e.key === 'z' || e.key === 'Z') soltarSalto();
});
function boton(id, on, off) {
  const b = document.getElementById(id);
  const fin = e => { b.classList.remove('on'); off && off(); };
  b.addEventListener('pointerdown', e => { e.preventDefault(); b.setPointerCapture && b.setPointerCapture(e.pointerId); b.classList.add('on'); on(); });
  b.addEventListener('pointerup', fin); b.addEventListener('pointercancel', fin); b.addEventListener('lostpointercapture', fin);
  b.addEventListener('contextmenu', e => e.preventDefault());
}
boton('b-izq', () => K.tIzq = true, () => K.tIzq = false);
boton('b-der', () => K.tDer = true, () => K.tDer = false);
boton('b-salto', apretarSalto, soltarSalto);
boton('b-hola', saludar);

// Tocar y deslizar sobre la pantalla del juego (además de los botones):
//   tocar y soltar sin mover el dedo = saltar · deslizar a un lado y dejar el dedo = caminar para ese lado.
// Cada dedo va por su lado: con uno se desliza y con otro se toca para saltar mientras camina.
const DEDOS = new Map();
const MUERTO = 14;                                   // px de pantalla que hay que mover para que cuente como deslizar
let dedoDir = 0;
function dirDedos() {
  dedoDir = 0;
  for (const d of DEDOS.values()) if (d.dir) dedoDir = d.dir;
}
const zona = document.getElementById('juego');
zona.addEventListener('pointerdown', e => {
  if (!S.jugando || e.pointerType === 'mouse') return;
  e.preventDefault();
  zona.setPointerCapture && zona.setPointerCapture(e.pointerId);
  DEDOS.set(e.pointerId, { x0: e.clientX, x: e.clientX, t0: performance.now(), dir: 0, movio: false });
});
zona.addEventListener('pointermove', e => {
  const d = DEDOS.get(e.pointerId);
  if (!d) return;
  const dx = e.clientX - d.x0;
  if (Math.abs(dx) > MUERTO) {
    d.movio = true;
    d.dir = Math.sign(dx);
    d.x0 = e.clientX - d.dir * MUERTO;               // el punto de partida sigue al dedo: devolverlo lo voltea enseguida
  }
  dirDedos();
});
function soltarDedo(e) {
  const d = DEDOS.get(e.pointerId);
  if (!d) return;
  DEDOS.delete(e.pointerId);
  dirDedos();
  if (e.type === 'pointerup' && !d.movio && performance.now() - d.t0 < 450) {
    apretarSalto();                                  // salto entero: se deja "apretado" un momento
    setTimeout(soltarSalto, 220);
  }
}
zona.addEventListener('pointerup', soltarDedo);
zona.addEventListener('pointercancel', soltarDedo);
function saludar() { if (S.p && S.p.piso) { S.p.hola = 1.2; if (Math.random() < 0.6) setTimeout(() => SON.ladrar(2), 400); } }
let padSalto = false;
function leerControl() {
  const gp = navigator.getGamepads ? [...navigator.getGamepads()].find(Boolean) : null;
  if (!gp) return 0;
  const ax = Math.abs(gp.axes[0]) > 0.3 ? gp.axes[0] : 0;
  const dx = (gp.buttons[15] && gp.buttons[15].pressed ? 1 : 0) - (gp.buttons[14] && gp.buttons[14].pressed ? 1 : 0);
  const a = gp.buttons[0] && gp.buttons[0].pressed;
  if (a && !padSalto) apretarSalto();
  if (!a && padSalto) soltarSalto();
  padSalto = a;
  return ax || dx;
}

// La carita del personaje en el botón de cambiar (la parte de arriba de su primer cuadro)
function pintarQuien() {
  const c = document.getElementById('c-quien'), m = D.sprites[S.quien], im = IMG['sprites/' + S.quien + '.png'];
  if (!c || !m) return;
  const x = c.getContext('2d'), f = m.anims.quieto.frames[0];
  const dibu = () => { x.imageSmoothingEnabled = false; x.clearRect(0, 0, 20, 20); x.drawImage(im, f * m.w + Math.floor((m.w - 20) / 2), 1, 20, 20, 0, 0, 20, 20); };
  im.complete ? dibu() : im.addEventListener('load', dibu, { once: true });
  const b = document.getElementById('b-quien');
  if (b) b.setAttribute('aria-label', 'Cambiar de personaje (ahora: ' + PJ[S.quien].nombre + ')');
}
function siguientePJ() {
  const ks = Object.keys(PJ), k = ks[(ks.indexOf(S.quien) + 1) % ks.length];
  elegir(k);
  if (S.jugando && !S.fin) cartel(PJ[k].nombre, '', 900);
}
function elegir(k) {
  S.quien = k; marcar(); pintarQuien();
  document.querySelectorAll('[data-pj]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.pj === k)));
}

// ---------- golpes y premios
function particulas(x, y, color, n, vel) {
  for (let i = 0; i < n; i++) {
    const a = Math.random() * Math.PI * 2, v = (vel || 60) * (0.4 + Math.random() * 0.8);
    S.parti.push({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 40, t: 0.5 + Math.random() * 0.4, c: color });
  }
}
function lastimar(desde) {
  const p = S.p;
  if (p.inv > 0 || S.fin) return;
  S.vidas--; p.inv = 1.6; p.golpe = 0.45;
  p.vx = (p.x < desde ? -1 : 1) * 160; p.vy = -200; p.piso = false;
  SON.efecto('golpe');
  if (S.vidas <= 0) {
    S.fin = 1; SON.efecto('ay');
    cartel('¡Ay!', 'Se acabaron los corazones. Volvemos a empezar el cuarto.', 0, { txt: 'Otra vez', fn: () => cargarCuarto(S.cuarto) });
  }
}
function siguiente() {
  const i = ORDEN.indexOf(S.cuarto), sig = ORDEN[(i + 1) % ORDEN.length];
  cargarCuarto(sig);
}
function llegarPuerta() {
  if (S.fin) return;
  S.fin = 1; SON.efecto('puerta');
  const tes = S.tes.ok ? '¡con el tesoro!' : 'sin el tesoro';
  cartel('¡Lo lograste!', `★ ${S.junto}/8 · ₡${S.colones} · ${tes}`, 0,
    { txt: 'Ir a ' + NIVELES[ORDEN[(ORDEN.indexOf(S.cuarto) + 1) % ORDEN.length]].nombre.toLowerCase(), fn: siguiente });
}

// ---------- física
const toca = (ax, ay, aw, ah, bx, by, bw, bh) => ax < bx + bw && ax + aw > bx && ay < by + bh && ay + ah > by;
function paso(dt) {
  const p = S.p, pj = PJ[S.quien], alto = D.sprites[S.quien].h * 0.8;
  const pad = leerControl();
  const izq = K.ArrowLeft || K.a || K.A || K.tIzq || dedoDir < 0, der = K.ArrowRight || K.d || K.D || K.tDer || dedoDir > 0;
  let quiere = (der ? 1 : 0) - (izq ? 1 : 0) || Math.sign(pad);
  if (S.fin || p.golpe > 0) quiere = 0;
  if (quiere) { p.mira = quiere; p.hola = 0; }
  const agarre = p.enCharco ? 1.6 : p.piso ? 14 : 6;
  p.vx += (quiere * pj.vel - p.vx) * Math.min(1, dt * agarre);
  // salto: con "coyote" (un instante después de dejar la orilla) y con memoria del botón
  p.coyote = p.piso ? 0.09 : Math.max(0, p.coyote - dt);
  p.buffer = Math.max(0, p.buffer - dt);
  if (p.buffer > 0 && p.coyote > 0 && !S.fin) {
    p.vy = -pj.salto; p.piso = false; p.coyote = 0; p.buffer = 0; p.suelto = 0; SON.efecto('salto');
  }
  if (!saltoApretado && p.vy < -140 && !p.rebote) p.vy = -140;   // soltar temprano = salto corto
  const yAntes = p.y, estabaEnPiso = p.piso;
  p.vy = Math.min(p.vy + GRAV * dt, 520);
  p.x += p.vx * dt; p.y += p.vy * dt;
  p.x = Math.max(8, Math.min(LARGO - 8, p.x));
  p.piso = false;
  if (p.y >= SUELO) { p.y = SUELO; p.vy = 0; p.piso = true; }
  p.enCharco = false;
  for (const q of S.cosas) {
    if (q.tipo === 'adorno') continue;
    const dentro = p.x > q.x + 4 && p.x < q.x + q.w - 4;
    if (SOLIDO(q.tipo)) {
      // se pisa la forma de arriba del objeto; se toma lo más alto bajo los dos pies
      let sup = null;
      for (const dx of [-3, 0, 3]) { const v = superficie(q, p.x + dx); if (v != null && (sup == null || v < sup)) sup = v; }
      if (sup == null) continue;
      const cae = p.vy >= 0 && yAntes <= sup + 1 && p.y >= sup;
      const subeGrada = estabaEnPiso && p.vy >= 0 && p.y >= sup && p.y - sup <= 6;   // escaloncito al caminar
      if (cae || subeGrada) {
        p.y = sup; p.vy = 0; p.piso = true;
        if (q.tipo === 'rebote') { p.vy = -REBOTE; p.piso = false; p.rebote = true; q.squash = 0.25; SON.efecto('rebote'); }
      }
    } else if (q.tipo === 'peligro') {
      const [a0, a1] = zonaDano(q);
      if (toca(p.x - 5, p.y - alto, 10, alto, a0, q.y + q.o.top + 3, a1 - a0, q.h - q.o.top - 3)) lastimar(q.x + q.w / 2);
    } else if (q.tipo === 'charco') {
      if (dentro && p.piso && p.y >= SUELO - 1) {
        p.enCharco = true;
        if (!q.pisado) { q.pisado = true; SON.efecto('charco'); particulas(p.x, SUELO - 2, '#bfe6f4', 8, 50); }
      } else q.pisado = false;
    }
  }
  if (p.vy >= 0) p.rebote = false;
  if (p.piso && !estabaEnPiso && yAntes < p.y - 0 && p.vy === 0 && S.t > 0.3) SON.efecto('caer');
  p.hola = Math.max(0, p.hola - dt); p.inv = Math.max(0, p.inv - dt); p.golpe = Math.max(0, p.golpe - dt);
  p.tAnim += dt * (p.piso && Math.abs(p.vx) > 8 ? Math.abs(p.vx) / pj.vel : 1);

  // enemigos: caminan de un lado a otro; si se les cae encima se aplastan
  for (const e of S.enem) {
    if (!e.vivo) {
      e.aplast += dt;
      if (e.cae && e.y < SUELO) { e.vy = (e.vy || 0) + GRAV * dt; e.y = Math.min(SUELO, e.y + e.vy * dt); }
      continue;
    }
    const E = e.E;
    e.t += dt;
    if (E.modo === 'salta') {                   // espera en el piso y brinca hacia adelante
      if (e.suelo) {
        e.espera -= dt;
        if (e.espera <= 0) {
          if ((e.dir > 0 && e.x > e.x1 - 20) || (e.dir < 0 && e.x < e.x0 + 20)) e.dir *= -1;
          e.vy = -E.brinco; e.suelo = false;
        }
      } else {
        e.vy += GRAV * dt; e.y += e.vy * dt; e.x += e.dir * E.vel * dt;
        if (e.y >= e.y0) { e.y = e.y0; e.vy = 0; e.suelo = true; e.espera = E.espera * (0.7 + Math.random() * 0.6); }
      }
    } else {
      e.x += e.dir * E.vel * dt;
      if (E.modo === 'vuela') e.y = e.y0 + Math.sin(e.t * 2.2) * 10;
    }
    if (e.x > e.x1) { e.x = e.x1; e.dir = -1; } else if (e.x < e.x0) { e.x = e.x0; e.dir = 1; }
    const w = e.o.w, h = e.o.h, ex = e.x - w / 2 + 4, ey = e.y - h + 3;
    if (toca(p.x - 5, p.y - alto, 10, alto, ex, ey, w - 8, h - 3)) {
      if (p.vy > 40 && yAntes <= ey + 8) {
        e.vivo = false; p.vy = -260; p.rebote = true; SON.efecto('pisar'); particulas(e.x, e.y - 6, '#e8e0c8', 10, 70);
        if (E.modo !== 'camina') e.cae = true;   // lo que salta o vuela cae al piso aplastado
        S.colones += 2;
      } else lastimar(e.x);
    }
  }
  // monedas, estrellas y tesoro
  const cx = p.x, cy = p.y - alto / 2;
  for (const m of S.mon) if (!m.ok && Math.abs(m.x - cx) < 11 && Math.abs(m.y - cy) < alto / 2 + 6) {
    m.ok = true; S.colones += m.dos ? 2 : 1; SON.efecto('moneda'); particulas(m.x, m.y, '#eef2f4', 4, 40);
  }
  for (const e of S.est) if (!e.ok && Math.abs(e.x - cx) < 12 && Math.abs(e.y - cy) < alto / 2 + 8) {
    e.ok = true; S.junto++; SON.efecto('estrella', S.junto); particulas(e.x, e.y, '#ffd84a', 12, 70);
    if (S.junto === S.est.length) { cartel('¡Las 8 estrellas!', 'Ahora busca la puertita al final', 2200); setTimeout(() => SON.ladrar(3), 300); }
  }
  const T = S.tes;
  if (!T.ok && Math.abs(T.x - cx) < 13 && Math.abs(T.y - cy) < alto / 2 + 8) {
    T.ok = true; SON.efecto('tesoro'); particulas(T.x, T.y, '#fff2a0', 20, 90); setTimeout(() => SON.ladrar(2), 500);
    cartel('¡Un tesoro!', { llave: 'Una llave vieja', brujula: 'Una brújula', reloj: 'Un reloj de bolsillo', mapa: 'Un mapa del tesoro', canica: 'Una canica de colores' }[T.n] || '', 1800);
  }
  if (p.x > S.puerta.x + 8 && p.x < S.puerta.x + 32 && p.piso) llegarPuerta();

  // Marshall lo sigue unos pasos atrás, salta si se queda atrás, y ladra de vez en cuando
  const d = S.perro, meta = p.x - p.mira * 26, dx = meta - d.x;
  const vel = Math.abs(dx) > 90 ? 200 : Math.abs(dx) > 6 ? 125 : 0;
  d.vx += (Math.sign(dx) * vel - d.vx) * Math.min(1, dt * 8);
  d.x += d.vx * dt;
  if (Math.abs(d.vx) > 5) d.mira = Math.sign(d.vx);
  d.vy += GRAV * dt; d.y += d.vy * dt;
  if (d.y >= SUELO) { d.y = SUELO; d.vy = 0; if (Math.abs(dx) > 50 && p.y < SUELO - 30 && Math.random() < dt * 1.2) d.vy = -230; }
  d.tAnim += dt;
  S.ladridoT -= dt;
  if (S.ladridoT < 0) { S.ladridoT = 14 + Math.random() * 16; if (Math.abs(p.vx) > 20) SON.ladrar(1 + (Math.random() * 2 | 0)); }

  for (const q of S.cosas) if (q.squash) q.squash = Math.max(0, q.squash - dt);
  for (const a of S.parti) { a.t -= dt; a.vy += 260 * dt; a.x += a.vx * dt; a.y += a.vy * dt; }
  S.parti = S.parti.filter(a => a.t > 0);

  const quiereCam = Math.max(0, Math.min(LARGO - VW, p.x - VW * 0.42 + p.mira * 30));
  S.cam += (quiereCam - S.cam) * Math.min(1, dt * 5);
}

// ---------- dibujo
function capa(file, factor) {
  const im = IMG['escenarios/' + file];
  if (!im || !im.complete || !im.width) return;
  const w = im.width;
  let x = -((S.cam * factor) % w);
  if (x > 0) x -= w;
  for (; x < VW; x += w) g.drawImage(im, Math.round(x), 0);
}
function sprite(nombre, anim, t, x, y, mira) {
  const m = D.sprites[nombre], im = IMG['sprites/' + nombre + '.png'];
  if (!m || !im.complete) return;
  const a = m.anims[anim] || m.anims.quieto;
  const f = a.frames[Math.floor(t * a.fps) % a.frames.length];
  g.save();
  g.translate(Math.round(x - S.cam), Math.round(y));
  if (mira < 0) g.scale(-1, 1);
  g.drawImage(im, f * m.w, 0, m.w, m.h, -Math.floor(m.w / 2), -m.h + 1, m.w, m.h);
  g.restore();
}
function pieza2d(o, x, y, mira, sy) {
  g.save();
  g.translate(Math.round(x), Math.round(y + o.h));
  if (mira < 0) { g.scale(-1, 1); }
  if (sy) g.scale(1, sy);
  g.drawImage(o.hoja, o.x, o.y, o.w, o.h, mira < 0 ? -o.w : 0, -o.h, o.w, o.h);
  g.restore();
}
function sombra(x, y, w) {
  const k = Math.max(0.35, 1 - Math.max(0, SUELO - y) / 120), ww = Math.round(w * k);
  g.fillStyle = `rgba(20,10,10,${0.28 * k})`;
  g.fillRect(Math.round(x - S.cam - ww / 2), SUELO - 1, ww, 2);
}
// números y letras en pixeles (3x5) para el marcador
const FUENTE = { 0: '111101101101111', 1: '010110010010111', 2: '111001111100111', 3: '111001111001111', 4: '101101111001001',
  5: '111100111001111', 6: '111100111101111', 7: '111001010010010', 8: '111101111101111', 9: '111101111001111', '/': '001001010100100' };
function texto(s, x, y, c) {
  g.fillStyle = '#2a1a16';
  for (const pass of [1, 0]) {
    let cx = x;
    for (const ch of String(s)) {
      const f = FUENTE[ch];
      if (f) for (let i = 0; i < 15; i++) if (f[i] === '1') g.fillRect(cx + (i % 3) + pass, y + (i / 3 | 0) + pass, 1, 1);
      cx += 4;
    }
    g.fillStyle = c;
  }
}
function marcador() {
  const cm = D.objetos.objetos.comun;
  for (let i = 0; i < 3; i++) {
    const o = i < S.vidas ? cm.corazon : cm.corazon_vacio;
    g.drawImage(OBJ, o.x, o.y, o.w, o.h, 6 + i * 11, 6, o.w, o.h);
  }
  const st = D.objetos.estrella;
  g.drawImage(OBJ, st.x, st.y, st.w, st.h, 42, 2, 16, 16);
  texto(S.junto + '/' + S.est.length, 59, 8, '#ffd84a');
  const mo = D.cosas.moneda1;
  g.drawImage(COSAS, mo.x, mo.y, mo.w, mo.h, 84, 4, 12, 12);
  texto(S.colones, 98, 8, '#eef2f4');
  if (S.tes.ok) { const o = S.tes.o; g.drawImage(COSAS, o.x, o.y, o.w, o.h, 124, 3, Math.round(o.w * 13 / o.h), 13); }
}
function dibujar() {
  const E = D.escenarios[S.cuarto], vis = (x, w) => x - S.cam < VW + 10 && x + w - S.cam > -10;
  const frente = [];
  for (const c of E.capas) { if (c.factor > 1) frente.push(c); else capa(c.file, c.factor); }
  // lo que se juega se dibuja unos pixeles más adentro del piso: parado sobre él y no en el borde con la pared
  g.save(); g.translate(0, NIVELES[S.cuarto].hundir || 0);
  for (const q of S.cosas) {
    if (q.tipo !== 'adorno' || !vis(q.x, Math.max(q.w, q.h))) continue;
    if (q.n === 'cuchara') {   // la cuchara va acostada en el piso
      g.save(); g.translate(Math.round(q.x - S.cam), SUELO); g.rotate(-Math.PI / 2);
      g.drawImage(q.o.hoja, q.o.x, q.o.y, q.o.w, q.o.h, 0, 0, q.o.w, q.o.h); g.restore();
    } else pieza2d(q.o, q.x - S.cam, q.y);
  }
  const pu = S.puerta;
  if (vis(pu.x, 40)) pieza2d(pu.o, pu.x - S.cam, SUELO - pu.o.h);
  for (const q of S.cosas) {           // sombrita de contacto: pega cada cosa al piso o a lo que la sostiene
    if (q.tipo === 'adorno' || q.tipo === 'charco' || !vis(q.x, q.w)) continue;
    const a = Math.round(q.x + q.o.pie[0] - S.cam), b = Math.round(q.x + q.o.pie[1] - S.cam), y = Math.round(q.y + q.h);
    g.fillStyle = 'rgba(25,12,10,0.32)'; g.fillRect(a - 1, y - 1, b - a + 3, 2);
    g.fillStyle = 'rgba(25,12,10,0.14)'; g.fillRect(a - 4, y, b - a + 9, 1);
  }
  for (const q of S.cosas) {
    if (q.tipo === 'adorno' || !vis(q.x, q.w)) continue;
    const sq = q.squash ? 1 - Math.sin(q.squash / 0.25 * Math.PI) * 0.15 : 0;
    pieza2d(q.o, q.x - S.cam, q.y, 1, sq || 0);
  }
  const st = D.objetos.estrella;
  for (const e of S.est) {
    if (e.ok || !vis(e.x - 8, 16)) continue;
    const f = Math.floor(S.t * 8 + e.x) % st.n, bob = Math.round(Math.sin(S.t * 3 + e.x) * 2);
    g.drawImage(OBJ, st.x + f * st.w, st.y, st.w, st.h, Math.round(e.x - S.cam - 8), Math.round(e.y - 8 + bob), 16, 16);
  }
  for (const m of S.mon) {
    if (m.ok || !vis(m.x - 8, 16)) continue;
    const o = m.dos ? D.cosas.moneda2 : D.cosas.moneda1, gira = Math.abs(Math.cos(S.t * 4 + m.x * 0.05));
    const w = Math.max(2, Math.round(o.w * gira));
    g.drawImage(COSAS, o.x, o.y, o.w, o.h, Math.round(m.x - S.cam - w / 2), Math.round(m.y - o.h / 2), w, o.h);
  }
  const T = S.tes;
  if (!T.ok && vis(T.x - 12, 24)) {
    const o = T.o, bob = Math.sin(S.t * 2.4) * 2;
    g.fillStyle = `rgba(255,240,150,${0.25 + 0.15 * Math.sin(S.t * 5)})`;
    g.beginPath(); g.arc(T.x - S.cam, T.y + bob, 12, 0, 7); g.fill();
    g.drawImage(COSAS, o.x, o.y, o.w, o.h, Math.round(T.x - S.cam - o.w / 2), Math.round(T.y - o.h / 2 + bob), o.w, o.h);
  }
  for (const e of S.enem) {
    if (!vis(e.x - 30, 60)) continue;
    const E = e.E;
    if (!e.vivo) {                              // su cuadro de aplastado (capullo, concha, ¡puf!) y se desvanece
      if (e.aplast > 1.1) continue;
      const m = pieza('p:' + E.muerto);
      g.globalAlpha = Math.min(1, (1.1 - e.aplast) / 0.4);
      pieza2d(m, e.x - S.cam - m.w / 2, e.y - m.h, e.dir);
      g.globalAlpha = 1; continue;
    }
    // cuadro: el de brincar si va en el aire; si no, alterna
    let fn = E.f[0];
    if (E.modo === 'salta' && !e.suelo && E.f[1]) fn = E.f[1];
    const o = pieza('p:' + fn);
    let sy = 0, bob = 0;
    if (E.estira) sy = 1 + Math.sin(e.t * 6) * 0.08;                 // orugas y larvas se estiran al avanzar
    if (E.patitas) bob = Math.abs(Math.sin(e.t * 14)) * -1;
    if (E.modo === 'vuela') sy = 0.75 + Math.abs(Math.sin(e.t * 16)) * 0.25;   // aleteo
    if (E.modo === 'salta' && e.suelo && e.espera < 0.15) sy = 0.85;  // se agacha antes de brincar
    sombra(e.x, E.modo === 'camina' || e.suelo ? SUELO : e.y, o.w * 0.6);
    pieza2d(o, e.x - S.cam - o.w / 2, e.y - o.h + bob, e.dir, sy);
  }
  for (const [n, anim, x] of NIVELES[S.cuarto].npc) {
    if (n === S.quien || !vis(x - 30, 60)) continue;
    const cerca = Math.abs(S.p.x - x) < 70;
    sprite(n, cerca && D.sprites[n].anims.hola ? 'hola' : anim, S.t, x, SUELO, S.p.x < x ? -1 : 1);
  }
  const d = S.perro, p = S.p;
  sombra(d.x, d.y, 14);
  sprite('marshall', d.y < SUELO - 1 ? (d.vy < 0 ? 'saltar' : 'caer') : Math.abs(d.vx) > 10 ? 'correr' : 'quieto', d.tAnim, d.x, d.y, d.mira);
  sombra(p.x, p.y, 14);
  if (!(p.inv > 0 && Math.floor(S.t * 16) % 2)) {
    const anim = !p.piso ? (p.vy < 0 ? 'saltar' : 'caer') : Math.abs(p.vx) > 8 ? 'correr' : p.hola > 0 ? 'hola' : 'quieto';
    const respira = anim === 'quieto' && Math.floor(S.t * 1.4) % 2 ? 1 : 0;
    sprite(S.quien, anim, p.tAnim, p.x, p.y + respira, p.mira);
  }
  for (const a of S.parti) { g.fillStyle = a.c; g.fillRect(Math.round(a.x - S.cam), Math.round(a.y), 2, 2); }
  g.restore();
  for (const c of frente) capa(c.file, c.factor);
  marcador();
}

// ---------- revisar que cada estrella, moneda y tesoro se pueda alcanzar (con el salto más bajo, el de Maritza)
function revisarAlcance(cuarto) {
  const salto = Math.min(...Object.values(PJ).map(p => p.salto));
  const H = salto * salto / (2 * GRAV) * 0.92;           // lo que sube con margen
  const HR = REBOTE * REBOTE / (2 * GRAV) * 0.92;
  const ALTO = Math.min(...Object.keys(PJ).map(k => D.sprites[k].h)) * 0.8;   // el más bajito
  const N = NIVELES[cuarto], sup = [{ x0: 0, x1: LARGO, top: SUELO, reb: false }];
  colocar(cuarto).forEach(q => {
    if (!SOLIDO(q.tipo)) return;
    // la forma de arriba en tramos de 6 columnas: se puede subir primero a lo bajo (el capó) y luego a lo alto (el techo)
    for (let c = 0; c < q.w; c += 6) {
      const vs = q.o.perfil.slice(c, c + 6).filter(v => v >= 0);
      if (vs.length) sup.push({ x0: q.x + c, x1: q.x + c + 5, top: q.y + Math.min(...vs), reb: q.tipo === 'rebote', n: q.n });
    }
  });
  const ok = new Set([0]);
  let cambio = true;
  const sube = s => s.reb ? HR : H;
  // cuánto se avanza en el aire saltando desde a hasta algo `sube` px más alto (física de verdad, con la
  // velocidad y el salto más bajos y un margen), menos el ancho del personaje
  const vx = Math.min(...Object.values(PJ).map(p => p.vel)) * 0.9;
  const avance = (a, rise) => {
    const v = (a.reb ? REBOTE : salto) * 0.97, disc = v * v - 2 * GRAV * (rise + 2);
    return disc < 0 ? -1 : vx * (v + Math.sqrt(disc)) / GRAV - 12;
  };
  while (cambio) {
    cambio = false;
    sup.forEach((s, i) => {
      if (ok.has(i)) return;
      for (const j of ok) {
        const a = sup[j], gap = Math.max(0, s.x0 - a.x1, a.x0 - s.x1);
        if (s.top >= a.top - sube(a) && gap <= avance(a, a.top - s.top)) { ok.add(i); cambio = true; break; }
      }
    });
  }
  const malos = [];
  const alcanza = (x, y, que) => {
    const bien = [...ok].some(i => {
      const s = sup[i];
      return x >= s.x0 - 40 && x <= s.x1 + 40 && y >= s.top - sube(s) - ALTO && y <= s.top;
    });
    if (!bien) malos.push(`${que} en x=${x}, alto=${SUELO - y}`);
  };
  N.estrellas.forEach(([x, a]) => alcanza(x, SUELO - a - 10, 'estrella'));
  N.monedas.forEach(([x, a, n]) => { for (let i = 0; i < n; i++) alcanza(x + i * 16, SUELO - a - 8, 'moneda'); });
  alcanza(N.tesoro[1], SUELO - N.tesoro[2] - 10, 'tesoro ' + N.tesoro[0]);
  const nombres = new Set(); sup.forEach((s, i) => { if (!ok.has(i)) nombres.add(`${s.n} cerca de x=${s.x0}`); });
  const cosas = [...nombres]; if (cosas.length) malos.push('partes que no se alcanzan: ' + cosas.slice(0, 6).join(', '));
  return malos;
}
window.revisarAlcance = revisarAlcance;

// Cosas apiladas: que se apoyen en buena parte de su base y con el centro encima de lo que las sostiene
function revisarApoyos(cuarto) {
  const lista = colocar(cuarto), malos = [];
  lista.forEach((q, k) => {
    if (q.tipo === 'adorno' || q.tipo === 'charco') return;
    const base = q.y + q.h;
    if (base >= SUELO) return;
    const a = q.x + q.o.pie[0], b = q.x + q.o.pie[1], tocan = [];
    for (let c = a; c <= b; c++) {
      if (lista.slice(0, k).some(r => SOLIDO(r.tipo) && Math.abs((superficie(r, c) ?? -99) - base) <= 2)) tocan.push(c);
    }
    const frac = tocan.length / (b - a + 1), centro = (a + b) / 2;
    if (frac < 0.3 || !tocan.length || centro < tocan[0] - 2 || centro > tocan[tocan.length - 1] + 2)
      malos.push(`${q.n} en x=${q.x} se apoya en ${Math.round(frac * 100)} % de su base`);
  });
  return malos;
}
window.revisarApoyos = revisarApoyos;

// Todo lo que pica se tiene que poder pasar: saltando desde el piso o desde algo que esté antes (con el salto y la
// velocidad más bajos, los de Maritza). Se revisa yendo hacia la puerta (de izquierda a derecha).
function revisarObstaculos(cuarto) {
  const v = Math.min(...Object.values(PJ).map(p => p.salto)) * 0.97, vx = Math.min(...Object.values(PJ).map(p => p.vel)) * 0.95;
  const lista = colocar(cuarto), malos = [];
  const sup = [{ x0: 0, x1: LARGO, y: SUELO }];
  lista.forEach(q => {
    if (!SOLIDO(q.tipo)) return;
    for (let c = 0; c < q.w; c += 4) { const y = superficie(q, q.x + c); if (y != null) sup.push({ x0: q.x + c, x1: q.x + c + 3, y }); }
  });
  lista.forEach(q => {
    if (q.tipo !== 'peligro') return;
    const [hx0, hx1] = zonaDano(q), ht = q.y + q.o.top + 3;     // la caja que lastima
    const pasa = sup.some(s => {
      if (s.x0 > hx0) return false;                    // hay que saltar desde antes
      const need = (s.y - ht) + 3;                       // cuánto hay que subir para pasar por encima
      const disc = v * v - 2 * GRAV * need;
      if (disc < 0) return false;
      const t1 = Math.max(0, (v - Math.sqrt(disc)) / GRAV), t2 = (v + Math.sqrt(disc)) / GRAV;
      const desde = Math.max(s.x0, hx1 + 5 - vx * t2), hasta = Math.min(s.x1, hx0 - 5 - vx * t1);
      return desde <= hasta;
    });
    if (!pasa) malos.push(`${q.n} en x=${q.x} no se puede saltar`);
  });
  return malos;
}
window.revisarObstaculos = revisarObstaculos;
window.__S = S;   // para las pruebas

// ---------- pantalla: ocupa lo más posible; en compu, en múltiplos enteros para que los pixeles queden parejos
function ajustar() {
  const fino = matchMedia('(pointer: coarse)').matches;
  let k = Math.min(innerWidth / VW, innerHeight / VH);
  if (!fino) k = Math.max(1, Math.floor(k * 2) / 2);
  cv.style.width = Math.floor(VW * k) + 'px'; cv.style.height = Math.floor(VH * k) + 'px';
}
addEventListener('resize', ajustar); ajustar();

// ---------- menú y arranque
function menu() {
  S.jugando = false;
  document.getElementById('portada').hidden = false;
  document.body.classList.add('en-menu');
  avisoEl.hidden = true;
}
function alternarSonido() {
  SON.callar(!SON.callado);
  pintarSonido();
}
// los dos botones de sonido (esquina y portada): parlante con ondas, o tachado cuando está apagado
function pintarSonido() {
  document.querySelectorAll('.b-sonido').forEach(b => {
    b.classList.toggle('mudo', SON.callado);
    b.setAttribute('aria-pressed', String(!SON.callado));
    b.setAttribute('aria-label', SON.callado ? 'Prender el sonido' : 'Apagar el sonido');
    const t = b.querySelector('.txt'); if (t) t.textContent = SON.callado ? 'Sonido apagado' : 'Sonido prendido';
  });
}
function jugar() {
  SON.iniciar();
  document.getElementById('portada').hidden = true;
  document.body.classList.remove('en-menu');
  S.jugando = true;
  const cuarto = document.querySelector('[data-cuarto][aria-pressed="true"]').dataset.cuarto;
  S.colones = 0;
  cargarCuarto(cuarto);
  setTimeout(() => SON.ladrar(3), 250);     // Marshall saluda al empezar
  if (matchMedia('(pointer: coarse)').matches && document.documentElement.requestFullscreen && !document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => { });
  }
}

// portada: botones de personajes con su figura
const quienEl = document.getElementById('p-quien');
Object.keys(PJ).forEach((k, i) => {
  const b = document.createElement('button');
  b.type = 'button'; b.dataset.pj = k; b.setAttribute('aria-pressed', String(k === S.quien));
  const c = document.createElement('canvas'), m = D.sprites[k];
  c.width = 44; c.height = 56; c.setAttribute('aria-hidden', 'true');
  const im = IMG['sprites/' + k + '.png'];
  // solo su cuadro de la tira (un recorte más ancho agarraba el borde del cuadro vecino)
  const pintar = () => { const x = c.getContext('2d'), f = m.anims.quieto.frames[0]; x.imageSmoothingEnabled = false; x.clearRect(0, 0, 44, 56); x.drawImage(im, f * m.w, 0, m.w, m.h, Math.floor((44 - m.w) / 2), 56 - m.h, m.w, m.h); };
  im.complete ? pintar() : im.addEventListener('load', pintar);
  b.append(c, document.createTextNode(PJ[k].nombre));
  b.onclick = () => elegir(k);
  quienEl.appendChild(b);
});
const dondeEl = document.getElementById('p-donde');
ORDEN.forEach((k, i) => {
  const b = document.createElement('button');
  b.type = 'button'; b.dataset.cuarto = k; b.textContent = NIVELES[k].nombre.replace(/^(El|La) /, '');
  b.setAttribute('aria-pressed', String(i === 0));
  b.onclick = () => dondeEl.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
  dondeEl.appendChild(b);
});
document.getElementById('p-jugar').onclick = jugar;
document.getElementById('b-menu').onclick = menu;
document.getElementById('b-quien').onclick = e => { siguientePJ(); e.currentTarget.blur(); };
pintarQuien();
// Pantalla completa (donde el navegador lo permite; en el iPhone Safari no deja, y el botón no sale)
const raiz = document.documentElement, bPant = document.getElementById('b-pantalla');
const pedirPC = raiz.requestFullscreen || raiz.webkitRequestFullscreen;
const salirPC = document.exitFullscreen || document.webkitExitFullscreen;
const enPC = () => document.fullscreenElement || document.webkitFullscreenElement;
if (pedirPC) {
  bPant.hidden = false;
  bPant.onclick = () => {
    try {
      const r = enPC() ? salirPC.call(document) : pedirPC.call(raiz);
      if (r && r.catch) r.catch(() => { });
      if (!enPC() && screen.orientation && screen.orientation.lock) screen.orientation.lock('landscape').catch(() => { });
    } catch (e) { }
    bPant.blur();
  };
  const marcarPC = () => {
    bPant.classList.toggle('en', !!enPC());
    bPant.setAttribute('aria-label', enPC() ? 'Salir de pantalla completa' : 'Pantalla completa');
    ajustar();
  };
  document.addEventListener('fullscreenchange', marcarPC);
  document.addEventListener('webkitfullscreenchange', marcarPC);
}
document.querySelectorAll('.b-sonido').forEach(b => b.onclick = alternarSonido);
pintarSonido();

// avisa en la consola si algo quedó fuera de alcance
ORDEN.forEach(k => {
  const m = revisarAlcance(k); if (m.length) console.warn('Fuera de alcance en ' + k + ':\n' + m.join('\n'));
  const a = revisarApoyos(k); if (a.length) console.warn('Mal apoyado en ' + k + ':\n' + a.join('\n'));
  const o = revisarObstaculos(k); if (o.length) console.warn('Obstáculo imposible en ' + k + ':\n' + o.join('\n'));
});

// ---------- bucle
S.cuarto = 'patio';
cargarCuarto('patio');
avisoEl.hidden = true;
let antes = performance.now();
function bucle(ahora) {
  if (window.__quieto) { antes = ahora; requestAnimationFrame(bucle); return; }   // pausa para las pruebas
  const dt = Math.min(0.04, (ahora - antes) / 1000); antes = ahora;
  S.t += dt;
  if (S.jugando) paso(dt);
  else { S.cam = (Math.sin(S.t * 0.12) * 0.5 + 0.5) * (LARGO - VW); const dir = Math.cos(S.t * 0.12) >= 0 ? 1 : -1; S.p.mira = S.perro.mira = dir; S.p.x = S.cam + 192 - dir * 40; S.perro.x = S.p.x - dir * 26; S.p.vx = 60; S.p.tAnim += dt; S.perro.vx = 60; S.perro.tAnim += dt; }
  g.imageSmoothingEnabled = false;
  dibujar();
  requestAnimationFrame(bucle);
}
requestAnimationFrame(bucle);
