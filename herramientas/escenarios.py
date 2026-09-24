"""Escenarios del juego 2D: cada cuarto de la casa visto desde el piso, en miniatura.

Cada escenario tiene capas que se repiten de lado a lado (768 px de ancho, 216 de alto)
y se mueven a distinta velocidad (paralaje). Pantalla del juego: 384 x 216. El piso
donde se juega arranca en y = SUELO.

Uso:  python escenarios.py [nombre ...]  ->  ../escenarios/<nombre>/<capa>.png + escenarios.json
"""
import json, math, os, random, sys
from PIL import Image
from pinta import Layer, clump, blade, dither_rect, bevel, sphere, cylinder, glow, C
from pixel import hexc, shade, mix

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, '..', 'escenarios')
W, H = 768, 216
SUELO = 184


def R(seed):
    return random.Random(seed)


def beach_ball(L, cx, cy, r):
    cols = ['#e8423a', '#ffffff', '#2f7fd8', '#f5c531', '#ffffff', '#3fb36a']

    def f(dx, dy, nz):
        if dy < -0.86:
            return '#f4f4ee'
        lon = math.atan2(dx, nz) + 0.35
        return cols[int((lon + math.pi) / math.tau * 12) % 6]
    sphere(L, cx, cy, r, f)


# ================================================================ PATIO
def patio():
    capas = []
    # --- cielo
    sky = Layer(W, H)
    sky.vgrad(0, 0, W - 1, 150, ['#4f9fe0', '#86c5ef', '#c9e9f6', '#f2f0da'])
    sky.rect(0, 151, W - 1, H - 1, '#f2f0da')
    r = R(1)
    for i in range(7):
        x = i * 110 + r.randint(0, 40)
        y = r.randint(18, 70)
        for k in range(3):
            clump(sky, x + k * 16 - 16, y + r.randint(-4, 4), r.randint(10, 16),
                  ['#a9c9e6', '#e3f0fa', '#ffffff'], seed=i * 7 + k, flat=0.45)
    capas.append(('cielo', 0.0, sky))

    # --- el cerro con cafetal, árboles y la casa amarilla de la vecina
    far = Layer(W, H)
    pts = [(0, H)]
    for x in range(0, W + 1, 4):
        y = 96 + 10 * math.sin(x / W * math.tau * 2) + 6 * math.sin(x / W * math.tau * 5 + 1)
        pts.append((x, y))
    pts.append((W, H))
    far.poly(pts, '#5b8a5c')
    r = R(2)
    for row, y in enumerate(range(104, 190, 6)):
        for x in range(row % 2 * 5, W, 10):
            top = 96 + 10 * math.sin(x / W * math.tau * 2) + 6 * math.sin(x / W * math.tau * 5 + 1)
            if y > top + 4:
                far.ell(x - 4, y - 2, x + 4, y + 2, '#3f6d45')
                far.px(x - 1, y - 2, '#7aa56a')
                if r.random() < 0.25:
                    far.px(x + 1, y - 1, '#b8372e')   # granos de café
    for i in range(9):
        x = i * 86 + r.randint(0, 30)
        top = 96 + 10 * math.sin(x / W * math.tau * 2) + 6 * math.sin(x / W * math.tau * 5 + 1)
        far.rect(x - 1, top - 14, x + 1, top + 4, '#4a3a2c')
        clump(far, x, top - 22, r.randint(12, 18), ['#2f5a37', '#447a47', '#6c9f58', '#9cc478'], seed=20 + i)
    # casa amarilla (la de Keylin), techo rojo, cortinas
    hx, hy = 520, 120
    far.rect(hx, hy, hx + 70, hy + 34, '#e9d178')
    far.rect(hx, hy, hx + 70, hy + 2, '#8e2c32')
    far.poly([(hx - 8, hy + 1), (hx + 35, hy - 20), (hx + 78, hy + 1)], '#b8452f')
    far.poly([(hx - 8, hy + 1), (hx + 35, hy - 20), (hx + 35, hy - 17), (hx - 4, hy + 1)], '#d4654a')
    for wx in (hx + 8, hx + 48):
        far.rect(wx, hy + 9, wx + 13, hy + 22, '#6b8aa4')
        far.rect(wx, hy + 9, wx + 5, hy + 22, '#f1eadc')
    far.rect(hx + 29, hy + 12, hx + 40, hy + 34, '#8e2c32')
    # tapia gris
    for x in range(0, W, 24):
        far.rect(x, 168, x + 22, 186, '#a3a7a4')
        far.rect(x, 168, x + 22, 168, '#c3c7c2')
        far.rect(x + 23, 164, x + 24, 186, '#8a8e8b')
    far.fog('#cfe6ee', 0.42)
    capas.append(('lejos', 0.15, far))

    # --- el patio de juegos gigante (tobogán y hamaca) y matas altas
    mid = Layer(W, H)
    # tobogán: escalera, plataforma, rampa
    sx = 80
    for lx in (sx, sx + 40):
        mid.rect(lx, 20, lx + 7, SUELO + 10, '#e2b33a')
        mid.rect(lx, 20, lx + 1, SUELO + 10, '#f4d36c')
        mid.rect(lx + 6, 20, lx + 7, SUELO + 10, '#b0831e')
    for y in range(40, SUELO, 26):
        mid.rect(sx + 8, y, sx + 39, y + 5, '#d6453c')
        mid.rect(sx + 8, y, sx + 39, y + 1, '#f06d5c')
    pts = []
    for i in range(21):
        t = i / 20
        pts.append((sx + 48 + t * 190, 10 + (SUELO - 20) * (t ** 1.6) - 20 * math.sin(t * math.pi)))
    top = [(x, y) for x, y in pts]
    bot = [(x, y + 22) for x, y in pts]
    mid.poly(top + bot[::-1], '#2f8fd6')
    mid.poly(top + [(x, y + 5) for x, y in pts][::-1], '#6cc0f2')
    mid.poly([(x, y + 17) for x, y in pts] + bot[::-1], '#1f67a8')
    mid.rect(sx + 225, SUELO - 30, sx + 233, SUELO + 10, '#e2b33a')
    # hamaca: marco en A azul, cadenas y asiento
    hx = 470
    for a, b in ((hx, hx + 40), (hx + 200, hx + 160)):
        mid.poly([(a - 6, SUELO + 10), (a + 4, SUELO + 10), (b + 4, -5), (b - 6, -5)], '#3558a8')
        mid.poly([(a - 6, SUELO + 10), (a - 2, SUELO + 10), (b - 2, -5), (b - 6, -5)], '#5b7fcf')
    for cx in (hx + 80, hx + 120):
        for y in range(0, 150, 4):
            mid.rect(cx, y, cx + 1, y + 2, '#8c8f99')
    mid.rect(hx + 72, 150, hx + 128, 158, '#e05a2b')
    mid.rect(hx + 72, 150, hx + 128, 151, '#f48a52')
    # la iguana (garrobo) tomando sol en su piedra, medio escondida entre el zacate
    from PIL import Image as _I
    ig = _I.open(os.path.join(SALIDA, 'piezas', 'iguana.png')).convert('RGBA')
    mid.paste(ig, 360, SUELO + 10 - ig.height)
    r = R(3)
    for i in range(60):
        x = r.randint(0, W)
        blade(mid, x, SUELO + 12, r.randint(40, 110), r.randint(-18, 18), r.randint(5, 9),
              r.choice(['#3f7a3a', '#4c8a41', '#356b33']))
    mid.fog('#cde7ea', 0.18)
    capas.append(('medio', 0.4, mid))

    # --- cerca: zacate gigante, dientes de león, tréboles, la bola de playa, piedritas
    near = Layer(W, H)
    r = R(4)
    for i in range(12):
        x = r.randint(0, W)
        hh = r.randint(90, 140)
        near.rect(x, SUELO - hh, x + 2, SUELO + 6, '#5c9a3e')
        near.rect(x, SUELO - hh, x, SUELO + 6, '#86c258')
        if i % 3 == 0:  # diente de león
            clump(near, x + 1, SUELO - hh - 6, 10, ['#c98a16', '#f1b927', '#ffe36a', '#fff6b0'], seed=40 + i, flat=0.7)
        else:           # esfera de semillas
            near.circ(x + 1, SUELO - hh - 8, 11, '#eef1ea')
            for k in range(16):
                a = k / 16 * math.tau
                near.line([(x + 1, SUELO - hh - 8), (x + 1 + math.cos(a) * 11, SUELO - hh - 8 + math.sin(a) * 11)], '#c9d0c6')
            near.circ(x + 1, SUELO - hh - 8, 2, '#8a7a4a')
    for i in range(10):  # tréboles
        x = r.randint(0, W)
        y = SUELO - r.randint(20, 55)
        near.rect(x, y, x + 1, SUELO + 4, '#4f8b3a')
        for k, (dx, dy) in enumerate(((-9, -2), (9, -2), (0, -11))):
            near.circ(x + dx, y + dy, 7, '#3f7d34')
            near.circ(x + dx - 1, y + dy - 1, 5, '#5da548')
            near.px(x + dx, y + dy, '#9fd07a')
    beach_ball(near, 640, SUELO - 50, 54)
    for i in range(40):
        x = r.randint(0, W)
        near.ell(x, SUELO - 3, x + r.randint(5, 12), SUELO + 4, r.choice(['#9a8f86', '#b5aca2', '#7d736b']))
    near.fog('#d6ecea', 0.06)
    capas.append(('cerca', 0.7, near))

    # --- piso: zacate encima de tierra roja
    suelo = Layer(W, H)
    suelo.rect(0, SUELO, W - 1, H - 1, '#8a3b22')
    suelo.vgrad(0, SUELO + 6, W - 1, H - 1, ['#9a4527', '#7a3019', '#4e1e10'])
    r = R(5)
    for i in range(220):
        x, y = r.randint(0, W), r.randint(SUELO + 8, H - 2)
        c = r.choice(['#b35a32', '#6a2814', '#a44c2a', '#c7b39a'])
        suelo.rect(x, y, x + r.randint(1, 3), y + r.randint(0, 1), c)
    suelo.rect(0, SUELO, W - 1, SUELO + 5, '#4f9a3a')
    suelo.rect(0, SUELO, W - 1, SUELO, '#8bd05a')
    for x in range(0, W, 2):
        hgt = r.randint(1, 5)
        suelo.rect(x, SUELO - hgt, x, SUELO, r.choice(['#4f9a3a', '#6cb84a', '#3d7d2e']))
        if r.random() < 0.5:
            suelo.px(x, SUELO + 6 + r.randint(0, 2), '#3d7d2e')
    capas.append(('suelo', 1.0, suelo))

    # --- adelante: sombras de zacate que pasan frente a la cámara
    fg = Layer(W, H)
    for x in (40, 330, 610):
        for k in range(4):
            blade(fg, x + k * 6, H + 4, r.randint(30, 60), r.randint(-20, 20), 8, '#173119')
    capas.append(('frente', 1.35, fg))
    return capas


import cuartos, cuartos2, frente
ESCENAS = {'patio': patio, 'cocina': cuartos2.cocina, 'sala': cuartos2.sala,
           'cuarto': cuartos2.cuarto, 'bano': cuartos2.bano,
           'corredor': frente.corredor, 'keylin': frente.casa_keylin}


def guardar(nombre, capas):
    d = os.path.join(SALIDA, nombre)
    os.makedirs(d, exist_ok=True)
    meta = []
    for cid, factor, L in capas:
        L.im.save(os.path.join(d, cid + '.png'))
        meta.append(dict(id=cid, file=f'{nombre}/{cid}.png', factor=factor))
    # vista previa para revisar (a 2x, dos pantallas)
    prev = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for cid, factor, L in capas:
        prev.alpha_composite(L.im)
    os.makedirs(os.path.join(AQUI, '..', '_revision'), exist_ok=True)
    prev.resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(AQUI, '..', '_revision', f'esc-{nombre}.png'))
    return meta


def main(names):
    todo = {}
    jp = os.path.join(SALIDA, 'escenarios.json')
    if os.path.exists(jp):
        todo = json.load(open(jp, encoding='utf-8'))
    for n in names or ESCENAS:
        todo[n] = dict(suelo=SUELO, w=W, h=H, capas=guardar(n, ESCENAS[n]()))
        print(n, 'listo')
    json.dump(todo, open(jp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main(sys.argv[1:])
