// La casa en miniatura: efectos de ambiente, todos en pixel art (2026-11-19).
// Se carga antes de juego.js y usa sus globales (g, S, VW, VH, SUELO, NIVELES, D) solo cuando se llama.
//   - aire de cada cuarto: semillas y mariposas en el patio, vapor de la comida en la cocina, polvito en la luz de
//     la ventana en la sala y el cuarto, burbujas en el baño, palomillas alrededor del bombillo en el corredor;
//   - luces tramadas (el bombillo del corredor titila, el sol de las ventanas);
//   - reflejo de los personajes en los pisos que brillan (sala, baño, cocina);
//   - viñeta tramada en las esquinas, sacudida de pantalla al golpe o al aplastar, números "+1" al juntar monedas;
//   - un marco oscuro detrás del marcador, para que se lea sobre cualquier fondo.
// Todo se dibuja en la resolución del juego (384 × 216) con pixeles enteros: al agrandar queda nítido.
'use strict';
const FX = (() => {
  const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map(v => (v + 0.5) / 16);
  const bay = (x, y) => BAYER[(y & 3) * 4 + (x & 3)];
  // Por cuarto. luces: [x en la capa de la pared, y, radio, color, titila]; ventanas: zona de polvito [x0, x1, y0, y1]
  // (la pared se mueve con factor 0.08/0.1: así la luz queda pegada al bombillo o a la ventana pintada)
  const CFG = {
    patio:    { aire: 'semillas', mariposas: 2, vin: [20, 30, 10], brillo: 0 },
    cocina:   { aire: 'vapor', vin: [40, 22, 12], brillo: 0.10, ventanas: [[334, 450, 6, 120]] },
    sala:     { aire: 'polvo', vin: [30, 20, 14], brillo: 0.18, ventanas: [[494, 615, 12, 175]], luces: [[555, 80, 70, [40, 32, 14], 0]] },
    cuarto:   { aire: 'polvo', vin: [24, 18, 30], brillo: 0, ventanas: [[160, 249, 42, 175]], luces: [[205, 62, 52, [38, 30, 16], 0]] },
    bano:     { aire: 'burbujas', vin: [16, 26, 32], brillo: 0.22 },
    corredor: { aire: 'palomillas', vin: [26, 18, 12], brillo: 0, luces: [[320, 66, 62, [70, 52, 20], 1]] },
    keylin:   { aire: 'semillas', mariposas: 1, vin: [26, 20, 12], brillo: 0 },
  };
  const cfg = () => CFG[S.cuarto] || {};
  const parteDePared = () => { const E = D.escenarios[S.cuarto]; const c = E.capas.find(c => /pared/.test(c.file)); return c ? c.factor : 0.08; };

  // ---------- luz tramada: un círculo de pixeles sueltos, más tupido al centro
  const luzCache = {};
  function luz(r, col) {
    const k = r + '|' + col;
    if (luzCache[k]) return luzCache[k];
    const c = document.createElement('canvas'); c.width = c.height = r * 2;
    const x = c.getContext('2d'), im = x.createImageData(r * 2, r * 2);
    for (let j = 0; j < r * 2; j++) for (let i = 0; i < r * 2; i++) {
      const d = Math.hypot(i - r + 0.5, j - r + 0.5) / r;
      if (d >= 1) continue;
      const f = Math.pow(1 - d, 1.4);                     // cae hacia la orilla
      const lvl = f * 2.2;                                // dos tonos: entero en el centro, tramado afuera
      const on = lvl >= 1 ? 1 : (lvl > bay(i, j) ? 0.55 : 0);
      if (!on) continue;
      const o = (j * r * 2 + i) * 4;
      im.data[o] = col[0]; im.data[o + 1] = col[1]; im.data[o + 2] = col[2]; im.data[o + 3] = Math.round(255 * on);
    }
    x.putImageData(im, 0, 0);
    return (luzCache[k] = c);
  }

  // ---------- viñeta: dos escalones tramados en las esquinas, del color de cada cuarto
  const vinCache = {};
  function vineta(col) {
    const k = col.join();
    if (vinCache[k]) return vinCache[k];
    const c = document.createElement('canvas'); c.width = VW; c.height = VH;
    const x = c.getContext('2d'), im = x.createImageData(VW, VH);
    for (let j = 0; j < VH; j++) for (let i = 0; i < VW; i++) {
      const ex = (i - VW / 2) / (VW / 2), ey = (j - VH / 2) / (VH / 2);
      const e = Math.sqrt(ex * ex * 0.75 + ey * ey * 0.6);
      let a = 0;
      if (e > 1.06) a = 0.22; else if (e > 0.96) a = bay(i, j) < (e - 0.96) / 0.10 ? 0.22 : 0.11; else if (e > 0.9) a = bay(i, j) < (e - 0.9) / 0.06 ? 0.11 : 0;
      if (!a) continue;
      const o = (j * VW + i) * 4;
      im.data[o] = col[0]; im.data[o + 1] = col[1]; im.data[o + 2] = col[2]; im.data[o + 3] = Math.round(255 * a);
    }
    x.putImageData(im, 0, 0);
    return (vinCache[k] = c);
  }

  // ---------- partículas de ambiente (en coordenadas del mundo)
  let aire = [], cuartoAire = null, sac = 0, sacA = 0, numeros = [];
  const R = Math.random;
  function nuevo(tipo) {
    const C = cfg(), cam = S.cam, f = parteDePared();
    if (tipo === 'semillas') return { tipo, x: cam - 20 + R() * (VW + 40), y: 20 + R() * 130, vx: 6 + R() * 8, vy: -2 + R() * 4, t: 0, vida: 8 + R() * 6, fase: R() * 6 };
    if (tipo === 'polvo') {
      // dentro del sol de una ventana (en la capa de la pared) si hay, si no por todo el cuarto
      const v = C.ventanas && C.ventanas[(R() * C.ventanas.length) | 0];
      let x = cam + R() * VW, y = 20 + R() * 150;
      if (v && R() < 0.75) {
        let sx = (((v[0] + R() * (v[1] - v[0]) - cam * f) % 768) + 768) % 768;
        if (sx > VW + 20) sx -= 768;
        x = sx + cam + (R() - 0.5) * 16; y = v[2] + R() * (v[3] - v[2]);
      }
      return { tipo, x, y, vx: (R() - 0.5) * 3, vy: (R() - 0.5) * 3, t: 0, vida: 5 + R() * 5, fase: R() * 6 };
    }
    if (tipo === 'burbujas') return { tipo, x: cam + R() * VW, y: SUELO - 2, vx: (R() - 0.5) * 4, vy: -(8 + R() * 10), t: 0, vida: 6 + R() * 6, fase: R() * 6, r: R() < 0.3 ? 2 : 1 };
    if (tipo === 'vapor') {
      const fuentes = S.cosas.filter(q => /olla|gallo_pinto|taza|tarrina|cafe/.test(q.n) && q.x + q.w > cam - 10 && q.x < cam + VW + 10);
      if (!fuentes.length) return null;
      const q = fuentes[(R() * fuentes.length) | 0];
      return { tipo, x: q.x + q.w * (0.3 + R() * 0.4), y: q.y + 3, vx: 0, vy: -(10 + R() * 6), t: 0, vida: 1.6 + R() * 1.2, fase: R() * 6 };
    }
    if (tipo === 'palomillas') {
      const L = (C.luces || [])[0]; if (!L) return null;
      return { tipo, cx: L[0], cy: L[1], t: 0, vida: 99, fase: R() * 6, rad: 10 + R() * 16, w: 2 + R() * 2 };
    }
    return null;
  }
  function mariposa(i) { return { tipo: 'mariposa', x: S.cam + 60 + i * 140 + R() * 60, y: 60 + R() * 60, t: R() * 9, vida: 999, col: ['#f29b30', '#5aa7e0', '#f2e14a'][i % 3], dir: 1 }; }

  function paso(dt) {
    const C = cfg();
    if (cuartoAire !== S.cuarto) {
      cuartoAire = S.cuarto; aire = []; numeros = [];
      for (let i = 0; i < (C.mariposas || 0); i++) aire.push(mariposa(i));
      if (C.aire === 'palomillas') for (let i = 0; i < 3; i++) { const p = nuevo('palomillas'); p && aire.push(p); }
    }
    const meta = { semillas: 14, polvo: 22, burbujas: 7, vapor: 16 }[C.aire] || 0;
    let n = aire.filter(a => a.tipo === C.aire).length;
    for (let k = 0; k < 2 && n < meta; k++, n++) { const a = nuevo(C.aire); if (a) aire.push(a); }
    for (const a of aire) {
      a.t += dt;
      if (a.tipo === 'semillas') { a.x += (a.vx + Math.sin(a.t * 1.3 + a.fase) * 4) * dt; a.y += (a.vy + Math.sin(a.t * 2 + a.fase) * 5) * dt; }
      else if (a.tipo === 'polvo') { a.x += (a.vx + Math.sin(a.t * 0.7 + a.fase) * 2) * dt; a.y += (a.vy + Math.cos(a.t * 0.9 + a.fase) * 2) * dt; }
      else if (a.tipo === 'burbujas') { a.x += (a.vx + Math.sin(a.t * 3 + a.fase) * 6) * dt; a.y += a.vy * dt; if (a.y < 30) a.vida = 0; }
      else if (a.tipo === 'vapor') { a.x += Math.sin(a.t * 5 + a.fase) * 6 * dt; a.y += a.vy * dt; }
      else if (a.tipo === 'mariposa') {
        a.x += (Math.sin(a.t * 0.4) * 22 + 6) * dt; a.y += Math.sin(a.t * 1.7) * 14 * dt;
        a.y = Math.max(30, Math.min(150, a.y));
        if (a.x < S.cam - 40) a.x += VW + 60; if (a.x > S.cam + VW + 40) a.x -= VW + 60;
        a.dir = Math.cos(a.t * 0.4) >= 0 ? 1 : -1;
      }
    }
    aire = aire.filter(a => a.t < a.vida && a.x > S.cam - 80 && a.x < S.cam + VW + 80 || a.tipo === 'palomillas');
    for (const m of numeros) { m.t += dt; m.y -= 18 * dt; }
    numeros = numeros.filter(m => m.t < 0.8);
    sac = Math.max(0, sac - dt);
  }

  // luces de la pared: van detrás de lo que se juega (encima del fondo)
  function fondo() {
    const C = cfg(); if (!C.luces) return;
    const f = parteDePared();
    g.save(); g.globalCompositeOperation = 'lighter';
    for (const [lx, ly, r, col, titila] of C.luces) {
      let a = 1;
      if (titila) { const t = S.t; a = (Math.sin(t * 13) > 0.97 || Math.sin(t * 2.3 + 1) > 0.995) ? 0.45 : 0.9 + Math.sin(t * 7) * 0.1; }
      g.globalAlpha = a;
      let x = lx - ((S.cam * f) % 768); if (x > VW + r) x -= 768;
      for (; x < VW + r; x += 768) if (x > -r) g.drawImage(luz(r, col), Math.round(x - r), Math.round(ly - r));
    }
    g.restore();
  }

  // el aire: encima de los personajes (dentro del corrimiento del piso)
  function delante() {
    const C = cfg(), f = parteDePared();
    for (const a of aire) {
      if (a.tipo === 'palomillas') {
        let bx = a.cx - ((S.cam * f) % 768); if (bx > VW + 30) bx -= 768;
        const x = Math.round(bx + Math.cos(a.t * a.w + a.fase) * a.rad), y = Math.round(a.cy + 8 + Math.sin(a.t * a.w * 1.3 + a.fase) * a.rad * 0.6);
        g.fillStyle = '#e9dcc0'; g.fillRect(x, y, 1, 1);
        if (Math.floor(a.t * 20) % 2) { g.fillRect(x - 1, y - 1, 1, 1); g.fillRect(x + 1, y - 1, 1, 1); }
        continue;
      }
      const x = Math.round(a.x - S.cam), y = Math.round(a.y);
      const fade = Math.min(1, a.t / 0.6, (a.vida - a.t) / 0.8);
      if (a.tipo === 'semillas') {
        g.globalAlpha = 0.85 * fade; g.fillStyle = '#fbf6e6'; g.fillRect(x, y, 1, 1);
        g.fillStyle = '#d8cfb4'; g.fillRect(x - 1, y + 1, 1, 1);
      } else if (a.tipo === 'polvo') {
        g.globalAlpha = (0.35 + 0.35 * Math.abs(Math.sin(a.t * 2 + a.fase))) * fade; g.fillStyle = '#fff3cf'; g.fillRect(x, y, 1, 1);
      } else if (a.tipo === 'burbujas') {
        g.globalAlpha = 0.7 * fade; g.fillStyle = '#e8f8ff';
        if (a.r === 2) { g.fillRect(x - 1, y - 2, 2, 1); g.fillRect(x - 1, y + 1, 2, 1); g.fillRect(x - 2, y - 1, 1, 2); g.fillRect(x + 1, y - 1, 1, 2); g.fillStyle = '#ffffff'; g.fillRect(x - 1, y - 1, 1, 1); }
        else { g.fillRect(x, y - 1, 1, 1); g.fillRect(x - 1, y, 1, 1); g.fillRect(x + 1, y, 1, 1); g.fillRect(x, y + 1, 1, 1); }
      } else if (a.tipo === 'vapor') {
        const k = a.t / a.vida;                            // se abre y se apaga al subir (tramado: pixeles que faltan)
        g.globalAlpha = 0.45 * (1 - k); g.fillStyle = '#ffffff';
        g.fillRect(x, y, 1, 2);
        if (k > 0.3 && (x + y) & 1) g.fillRect(x + 1, y + 1, 1, 1);
      } else if (a.tipo === 'mariposa') {
        g.globalAlpha = 1; const ala = Math.floor(a.t * 12) % 2;
        g.fillStyle = a.col;
        if (ala) { g.fillRect(x - 2, y - 1, 2, 2); g.fillRect(x + 1, y - 1, 2, 2); }
        else { g.fillRect(x - 1, y - 2, 1, 2); g.fillRect(x + 1, y - 2, 1, 2); }
        g.fillStyle = '#2a1a16'; g.fillRect(x, y - 1, 1, 3);
      }
    }
    g.globalAlpha = 1;
    // números que suben al juntar monedas
    for (const m of numeros) {
      if (m.t > 0.55 && Math.floor(m.t * 20) % 2) continue;   // parpadea antes de irse
      texto(m.s, Math.round(m.x - S.cam - m.s.length * 2), Math.round(m.y), m.c);
    }
  }

  // reflejo de un sprite en el piso que brilla: volteado hacia abajo, aplastado y transparente
  function reflejo(fuente, sx, sy, w, h, x, y, mira) {
    const k = cfg().brillo; if (!k) return;
    const alto = SUELO - y; if (alto > 40) return;          // muy arriba ya no se refleja
    g.save();
    g.beginPath(); g.rect(0, SUELO + 1, VW, VH - SUELO); g.clip();
    g.globalAlpha = k * (1 - alto / 40);
    g.translate(Math.round(x - S.cam), SUELO + 1 + Math.round(alto * 0.6));
    g.scale(mira < 0 ? -1 : 1, -0.6);
    g.drawImage(fuente, sx, sy, w, h, -Math.floor(w / 2), -h, w, h);
    g.restore();
  }

  function pantalla() { const C = cfg(); if (C.vin) g.drawImage(vineta(C.vin), 0, 0); }

  // marco detrás del marcador: rectángulo oscuro con esquinas recortadas y un borde claro de 1 px
  function panel(w) {
    const x = 2, y = 2, h = 16;
    g.fillStyle = 'rgba(23,19,28,0.55)';
    g.fillRect(x + 1, y, w - 2, h); g.fillRect(x, y + 1, w, h - 2);
    g.fillStyle = 'rgba(243,234,216,0.22)';
    g.fillRect(x + 1, y, w - 2, 1); g.fillRect(x + 1, y + h - 1, w - 2, 1); g.fillRect(x, y + 1, 1, h - 2); g.fillRect(x + w - 1, y + 1, 1, h - 2);
  }

  function sacudir(t, a) { if (t >= sac) { sac = t; sacA = a; } }
  function desplazo() {
    if (sac <= 0) return [0, 0];
    const a = Math.ceil(sacA * Math.min(1, sac / 0.15));
    return [Math.round((Math.random() * 2 - 1) * a), Math.round((Math.random() * 2 - 1) * a)];
  }
  function numero(x, y, s, c) { numeros.push({ x, y, s, c: c || '#eef2f4', t: 0 }); }
  function estallido(x, y, c) {   // aro de 8 pixeles que se abre (estrellas y tesoro)
    for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2; S.parti.push({ x, y, vx: Math.cos(a) * 90, vy: Math.sin(a) * 90 + 40, t: 0.35, c }); }
  }

  return { paso, fondo, delante, reflejo, pantalla, panel, sacudir, desplazo, numero, estallido, CFG };
})();
