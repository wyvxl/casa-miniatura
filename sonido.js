// Música y efectos, hechos con Web Audio (sin archivos), como en el juego 3D.
// Los navegadores no dejan sonar nada hasta que la persona toca la pantalla: SON.iniciar() va en el clic de "Jugar".
'use strict';
const SON = (() => {
  let ctx = null, music, fx, noise, rev;
  let callado = false;
  try { callado = localStorage.getItem('casa2d-callado') === '1'; } catch (e) { }

  function iniciar() {
    if (ctx) { if (ctx.state === 'suspended') ctx.resume(); return; }
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    ctx = new AC();
    const comp = ctx.createDynamicsCompressor();
    comp.connect(ctx.destination);
    music = ctx.createGain(); music.gain.value = callado ? 0 : 0.42; music.connect(comp);
    fx = ctx.createGain(); fx.gain.value = callado ? 0 : 0.9; fx.connect(comp);
    // eco corto para la caja de música y los destellos
    const len = Math.floor(ctx.sampleRate * 1.2), ir = ctx.createBuffer(2, len, ctx.sampleRate);
    for (let c = 0; c < 2; c++) { const d = ir.getChannelData(c); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 3); }
    rev = ctx.createConvolver(); rev.buffer = ir; const rg = ctx.createGain(); rg.gain.value = 0.35; rev.connect(rg); rg.connect(music);
    noise = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
    const nd = noise.getChannelData(0); for (let i = 0; i < nd.length; i++) nd[i] = Math.random() * 2 - 1;
  }
  const hz = m => 440 * Math.pow(2, (m - 69) / 12);
  const ok = () => ctx && !callado && ctx.state === 'running';

  // --- piezas
  function nota(t, m, dur, o, dest) {
    const env = ctx.createGain(), lp = ctx.createBiquadFilter(), a = o.a || 0.004, r = o.r || 0.05, fin = t + Math.max(a, dur);
    lp.type = 'lowpass'; lp.frequency.value = o.cut || 5000; lp.connect(env); env.connect(dest || music);
    if (o.rev) { const s = ctx.createGain(); s.gain.value = o.rev; env.connect(s); s.connect(rev); }
    env.gain.setValueAtTime(0.0001, t);
    env.gain.linearRampToValueAtTime(o.vol, t + a);
    env.gain.setTargetAtTime(o.vol * (o.s == null ? 0.5 : o.s), t + a, (o.d || 0.08) / 3);
    env.gain.setTargetAtTime(0, fin, r / 3);
    (o.harm || [[1, 1]]).forEach(([k, l]) => {
      const osc = ctx.createOscillator(), g = ctx.createGain();
      osc.type = o.type || 'square'; osc.frequency.value = hz(m) * k;
      g.gain.value = l; osc.connect(g); g.connect(lp); osc.start(t); osc.stop(fin + r * 3 + 0.05);
    });
  }
  function barrido(t, type, f0, f1, dur, vol, dest) {
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.type = type; o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(f1, t + dur);
    g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur);
    o.connect(g); g.connect(dest || fx); o.start(t); o.stop(t + dur + 0.02);
  }
  function ruido(t, vol, dur, type, freq, q, dest) {
    const n = ctx.createBufferSource(), f = ctx.createBiquadFilter(), g = ctx.createGain();
    n.buffer = noise; f.type = type; f.frequency.value = freq; f.Q.value = q || 1;
    g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur);
    n.connect(f); f.connect(g); g.connect(dest || fx); n.start(t, Math.random() * 0.5); n.stop(t + dur + 0.02);
  }
  function bombo(t, vol) { barrido(t, 'sine', 150, 45, 0.18, vol, music); }

  // --- efectos
  const E = {
    salto() { const t = ctx.currentTime; barrido(t, 'square', 260, 620, 0.12, 0.09); },
    caer() { const t = ctx.currentTime; barrido(t, 'sine', 140, 60, 0.08, 0.3); ruido(t, 0.08, 0.05, 'lowpass', 900); },
    moneda() { const t = ctx.currentTime; nota(t, 83, 0.05, { vol: 0.12, s: 0.7 }, fx); nota(t + 0.06, 88, 0.18, { vol: 0.12, s: 0.6, r: 0.12 }, fx); },
    estrella(n) {
      const t = ctx.currentTime, b = 72 + (n || 0);
      [0, 4, 7, 12].forEach((k, i) => nota(t + i * 0.05, b + k, 0.12, { type: 'triangle', vol: 0.2, s: 0.4, r: 0.2, rev: 0.4 }, fx));
    },
    tesoro() {
      const t = ctx.currentTime;
      [[72, 0], [76, 0.1], [79, 0.2], [84, 0.3], [79, 0.45], [84, 0.55]].forEach(([m, d], i) =>
        nota(t + d, m, i === 5 ? 0.5 : 0.09, { vol: 0.13, s: 0.6, r: 0.2 }, fx));
      ruido(t + 0.55, 0.05, 0.6, 'highpass', 6000);
    },
    golpe() { const t = ctx.currentTime; barrido(t, 'sawtooth', 420, 90, 0.25, 0.12); ruido(t, 0.18, 0.12, 'bandpass', 900, 0.8); },
    pisar() { const t = ctx.currentTime; barrido(t, 'square', 520, 140, 0.14, 0.12); ruido(t, 0.1, 0.08, 'lowpass', 1200); },
    rebote() {
      const t = ctx.currentTime, o = ctx.createOscillator(), g = ctx.createGain(), v = ctx.createOscillator(), vg = ctx.createGain();
      o.type = 'sine'; o.frequency.setValueAtTime(180, t); o.frequency.exponentialRampToValueAtTime(760, t + 0.3);
      v.frequency.value = 22; vg.gain.value = 40; v.connect(vg); vg.connect(o.frequency);
      g.gain.setValueAtTime(0.35, t); g.gain.exponentialRampToValueAtTime(0.001, t + 0.38);
      o.connect(g); g.connect(fx); o.start(t); v.start(t); o.stop(t + 0.4); v.stop(t + 0.4);
    },
    charco() { const t = ctx.currentTime; ruido(t, 0.25, 0.25, 'bandpass', 1400, 0.7); ruido(t + 0.05, 0.12, 0.2, 'highpass', 3500); },
    puerta() {
      const t = ctx.currentTime; ruido(t, 0.12, 0.4, 'bandpass', 700, 0.6);
      [79, 84, 91].forEach((m, i) => nota(t + 0.1 + i * 0.08, m, 0.2, { type: 'triangle', vol: 0.16, s: 0.3, r: 0.3, rev: 0.5 }, fx));
    },
    furia() {                                   // poder: barrido que sube, golpe y acorde en rojo
      const t = ctx.currentTime;
      barrido(t, 'sawtooth', 110, 880, 0.5, 0.12); ruido(t, 0.18, 0.5, 'highpass', 2500);
      bombo(t + 0.5, 0.6); ruido(t + 0.5, 0.25, 0.35, 'lowpass', 900);
      [48, 55, 60, 64, 67, 72].forEach((m, i) => nota(t + 0.52 + i * 0.03, m, 0.9, { type: 'sawtooth', vol: 0.06, s: 0.6, r: 0.5, cut: 2400, rev: 0.4 }, fx));
    },
    ay() { const t = ctx.currentTime; [72, 67, 64, 60].forEach((m, i) => nota(t + i * 0.14, m, 0.12, { vol: 0.1, s: 0.6 }, fx)); },
    ladrido(veces) {
      const t0 = ctx.currentTime + 0.01, n = veces || 3;
      for (let i = 0; i < n; i++) {
        const t = t0 + i * 0.16 + (i === n - 1 ? 0.02 : 0), o = ctx.createOscillator(), f = ctx.createBiquadFilter(), g = ctx.createGain();
        o.type = 'sawtooth'; o.frequency.setValueAtTime(880, t); o.frequency.exponentialRampToValueAtTime(560, t + 0.08);
        f.type = 'bandpass'; f.frequency.value = 1700; f.Q.value = 1.4;
        g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(0.3, t + 0.008); g.gain.exponentialRampToValueAtTime(0.001, t + 0.1);
        o.connect(f); f.connect(g); g.connect(fx); o.start(t); o.stop(t + 0.12);
        ruido(t, 0.08, 0.05, 'bandpass', 2600);
      }
    },
  };
  function efecto(nombre, arg) { if (ok() && E[nombre]) E[nombre](arg); }
  // el ladrido suena aunque el juego recién arranque (el contexto puede tardar un instante en quedar "running")
  function ladrar(n) { if (!ctx || callado) return; const f = () => E.ladrido(n); ctx.state === 'running' ? f() : ctx.resume().then(f); }

  // --- música: una canción por cuarto (8 compases en corcheas; '-' sostiene, '.' calla)
  const N = s => { const m = /^([A-G])(#|b)?(\d)$/.exec(s); const b = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 }[m[1]]; return 12 * (+m[3] + 1) + b + (m[2] === '#' ? 1 : m[2] === 'b' ? -1 : 0); };
  const AC = { G: ['G3', 'B3', 'D4'], D: ['D3', 'F#3', 'A3'], Em: ['E3', 'G3', 'B3'], C: ['C3', 'E3', 'G3'], F: ['F3', 'A3', 'C4'],
    Dm: ['D3', 'F3', 'A3'], Bb: ['Bb2', 'D3', 'F3'], Am: ['A2', 'C3', 'E3'], Bm: ['B2', 'D3', 'F#3'], A: ['A2', 'C#3', 'E3'], E: ['E3', 'G#3', 'B3'] };
  const CANC = {
    patio: { bpm: 138, acordes: 'G D Em C G D C D', estilo: 'alegre',
      mel: 'D5 - B4 G4 A4 B4 D5 - | A4 - F#4 A4 D5 - C5 B4 | B4 - G4 B4 E5 D5 B4 G4 | A4 - - G4 E4 G4 A4 B4 | D5 - B4 G4 A4 B4 D5 G5 | F#5 - E5 D5 A4 - D5 - | E5 D5 C5 B4 A4 G4 A4 B4 | A4 - - - D5 . . .' },
    cocina: { bpm: 150, acordes: 'F C Dm Bb F C Bb C', estilo: 'saltarina',
      mel: 'F5 . C5 . A4 C5 F5 . | E5 . C5 . G4 C5 E5 . | D5 . A4 . F4 A4 D5 F5 | D5 - C5 Bb4 A4 - G4 . | F5 . C5 . A4 C5 F5 A5 | G5 . E5 . C5 E5 G5 . | F5 E5 D5 C5 Bb4 A4 G4 A4 | C5 - - . C5 . . .' },
    sala: { bpm: 108, acordes: 'C Am F G C Am Dm G', estilo: 'tranquila',
      mel: 'E5 - - D5 C5 - G4 - | A4 - C5 - E5 - - - | F5 - E5 - D5 - C5 - | D5 - - - G4 - - - | E5 - G5 - E5 - C5 - | A5 - G5 - E5 - C5 - | D5 - F5 - A5 - G5 F5 | E5 - D5 - C5 - - -' },
    cuarto: { bpm: 92, acordes: 'D Bm G A D Bm G A', estilo: 'cajita',
      mel: 'F#5 - A5 - D6 - A5 - | F#5 - D5 - B4 - D5 - | G5 - B5 - D6 - B5 - | A5 - - - E5 - - - | F#5 - A5 - D6 - E6 - | F#6 - D6 - B5 - A5 - | G5 - F#5 - E5 - G5 - | A5 - - - D5 - - -' },
    bano: { bpm: 126, acordes: 'Em C G D Em C G D', estilo: 'burbujas',
      mel: 'E5 . G5 . B5 . G5 E5 | C5 . E5 . G5 . E5 C5 | D5 . G5 . B5 A5 G5 D5 | F#5 . A5 . D5 - - . | E5 G5 B5 E6 D6 B5 G5 E5 | C5 E5 G5 C6 B5 G5 E5 C5 | B4 D5 G5 B5 A5 G5 F#5 D5 | E5 - - - . . B4 .' },
    corredor: { bpm: 116, acordes: 'C F G C Am F G C', estilo: 'tranquila',
      mel: 'G4 - C5 - E5 - D5 C5 | A4 - C5 - F5 - E5 D5 | D5 - B4 - G4 - B4 D5 | C5 - - - G4 - - - | E5 - E5 D5 C5 - A4 - | F5 - E5 - D5 - C5 - | D5 - E5 - F5 - D5 B4 | C5 - - - . . . .' },
    keylin: { bpm: 132, acordes: 'Am Dm G C F Dm E Am', estilo: 'saltarina',
      mel: 'A4 . C5 . E5 . C5 A4 | D5 . F5 . A5 . F5 D5 | B4 . D5 . G5 F5 E5 D5 | C5 . E5 . G5 - - . | A5 . F5 . C5 F5 A5 . | F5 E5 D5 . A4 D5 F5 . | E5 . G#4 . B4 . E5 D5 | C5 B4 A4 - - . . .' },
  };
  for (const k in CANC) {
    const c = CANC[k];
    c.pasos = c.mel.split('|').flatMap(b => b.trim().split(/\s+/));
    c.ac = c.acordes.split(' ');
  }
  let actual = null, sig = 0, paso = 0, timer = 0;
  function tocarPaso(c, i, t) {
    const e = 60 / c.bpm / 2;                    // una corchea
    const tok = c.pasos[i], bar = Math.floor(i / 8), enBar = i % 8;
    if (tok !== '-' && tok !== '.') {
      let largo = 1; while (c.pasos[(i + largo) % c.pasos.length] === '-' && largo < 8) largo++;
      const m = N(tok), d = largo * e * 0.92;
      if (c.estilo === 'cajita') nota(t, m, d, { type: 'sine', vol: 0.16, s: 0.25, d: 0.3, r: 0.4, harm: [[1, 1], [2, 0.25], [4, 0.1]], rev: 0.8 });
      else if (c.estilo === 'tranquila') nota(t, m, d, { type: 'triangle', vol: 0.2, s: 0.6, r: 0.15, rev: 0.4 });
      else if (c.estilo === 'burbujas') { nota(t, m, Math.min(d, e * 0.7), { type: 'square', vol: 0.06, s: 0.3, r: 0.1, cut: 2600, rev: 0.3 }); nota(t, m + 12, 0.05, { type: 'sine', vol: 0.05, s: 0.1 }); }
      else nota(t, m, d, { type: 'square', vol: 0.065, s: 0.55, r: 0.06, cut: 3200 });
    }
    const acorde = AC[c.ac[bar % c.ac.length]].map(N);
    // bajo
    if (c.estilo === 'cajita') { if (enBar === 0) nota(t, acorde[0] - 12, e * 7, { type: 'sine', vol: 0.16, s: 0.6, r: 0.3 }); }
    else if (enBar % 2 === 0) nota(t, acorde[0] - 12 + (enBar === 4 && c.estilo !== 'tranquila' ? 7 : 0), e * 0.9, { type: 'triangle', vol: 0.22, s: 0.7, r: 0.04 });
    // arpegio suave
    if (c.estilo === 'alegre' || c.estilo === 'saltarina') nota(t, acorde[enBar % 3] + 12, e * 0.5, { type: 'square', vol: 0.022, s: 0.3, cut: 1800 });
    if (c.estilo === 'tranquila' && enBar % 2 === 1) nota(t, acorde[(enBar >> 1) % 3] + 12, e * 0.9, { type: 'sine', vol: 0.06, s: 0.4, rev: 0.4 });
    if (c.estilo === 'cajita' && enBar % 2 === 1) nota(t, acorde[(enBar >> 1) % 3] + 24, e, { type: 'sine', vol: 0.05, s: 0.2, rev: 0.8 });
    // batería
    if (c.estilo !== 'cajita') {
      if (enBar === 0 || enBar === 4 || (c.estilo === 'saltarina' && enBar === 5)) bombo(t, c.estilo === 'tranquila' ? 0.25 : 0.4);
      if (enBar === 2 || enBar === 6) ruido(t, c.estilo === 'tranquila' ? 0.05 : 0.1, 0.1, 'bandpass', 1800, 0.6, music);
      if (c.estilo !== 'tranquila') ruido(t, 0.03, 0.03, 'highpass', 8000, 1, music);
      if (c.estilo === 'burbujas' && enBar === 7) barrido(t, 'sine', 400, 1400, 0.08, 0.05, music);
    }
  }
  function programar() {
    if (!ctx || !actual) return;
    const c = CANC[actual], e = 60 / c.bpm / 2;
    while (sig < ctx.currentTime + 0.25) {
      if (!callado) tocarPaso(c, paso, sig);
      paso = (paso + 1) % c.pasos.length;
      sig += e;
    }
  }
  function musica(cual) {
    if (!ctx || actual === cual) return;
    actual = cual; paso = 0; sig = ctx.currentTime + 0.15;
    clearInterval(timer); timer = setInterval(programar, 60);
  }
  function callar(v) {
    callado = v;
    try { localStorage.setItem('casa2d-callado', v ? '1' : '0'); } catch (e) { }
    if (ctx) { music.gain.value = v ? 0 : 0.42; fx.gain.value = v ? 0 : 0.9; }
  }
  document.addEventListener('visibilitychange', () => { if (!ctx) return; document.hidden ? ctx.suspend() : ctx.resume(); });
  return { iniciar, efecto, ladrar, musica, callar, get callado() { return callado; } };
})();
