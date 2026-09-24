"""Los cuartos de la casa vistos desde el piso, en miniatura: cocina, sala, cuarto y baño.
Colores tomados del modelo 3D (COL y PAINTS de ../../modelo-3d/index.html)."""
import math, random
from pinta import Layer, clump, blade, dither_rect, bevel, sphere, cylinder, glow, C
from pixel import hexc, shade, mix

W, H, SUELO = 768, 216, 184


def R(s):
    return random.Random(s)


# ---------------------------------------------------------------- piezas comunes
def ceramica(L, base='#e6e0d4', grout='#c4bcae', seed=1, vetas='#d3ccbe', sheen=True):
    b = C(base)
    L.vgrad(0, SUELO, W - 1, H - 1, [shade(b, 1.12), b, shade(b, 0.82)])
    L.rect(0, SUELO, W - 1, SUELO, shade(b, 1.25))
    L.rect(0, SUELO + 1, W - 1, SUELO + 1, shade(b, 0.9))
    for x in range(0, W, 192):
        L.line([(x, SUELO + 2), (x - 36, H)], grout, 1)
    L.rect(0, SUELO + 14, W - 1, SUELO + 14, grout)
    r = R(seed)
    for i in range(30):   # vetas de mármol
        x, y = r.randint(0, W), r.randint(SUELO + 3, H - 2)
        for k in range(r.randint(6, 18)):
            L.px(x + k, y + int(math.sin(k / 3 + i) * 1.5), vetas)
    if sheen:             # brillo del piso encerado
        for x in range(0, W, 128):
            L.rect(x + 20, SUELO + 4, x + 60, SUELO + 4, shade(b, 1.2))


def rodapie(L, c='#6b4a34', y0=174):
    L.rect(0, y0, W - 1, SUELO, c)
    L.rect(0, y0, W - 1, y0, shade(C(c), 1.3))


def ventana(L, x0, y0, x1, y1, marco='#f6f5f1', afuera=True, seed=3):
    L.rect(x0 - 4, y0 - 4, x1 + 4, y1 + 4, marco)
    L.rect(x0 - 4, y1 + 1, x1 + 4, y1 + 4, shade(C(marco), 0.8))
    L.vgrad(x0, y0, x1, y1, ['#7fc0ec', '#bfe3f4', '#e9f5f2'])
    if afuera:
        r = R(seed)
        for i in range(5):
            clump(L, r.randint(x0, x1), y1 - r.randint(2, 20), r.randint(10, 16),
                  ['#3f7a3a', '#5a9a48', '#8cc46a'], seed=seed + i)
        L.rect(x0 - 4, y0 - 4, x1 + 4, y0 - 1, marco)
    L.rect((x0 + x1) // 2 - 1, y0, (x0 + x1) // 2 + 1, y1, marco)
    L.rect(x0, y0, x0 + 3, y1, shade(C(marco), 0.85))


# ================================================================ COCINA
def cocina():
    capas = []
    wall = Layer(W, H)
    wall.vgrad(0, 0, W - 1, SUELO, ['#e6dcc4', '#f1ead8', '#efe6d1'])
    # gabinetes de arriba, azulejo y la ventana del fondo
    for x in range(0, W, 8):
        for y in range(22, 70, 8):
            wall.rect(x + (4 if (y // 8) % 2 else 0), y, x + 7 + (4 if (y // 8) % 2 else 0), y + 6, '#dfe8e4')
    for x in range(0, W, 96):
        if 280 < x < 440:
            continue
        bevel(wall, x + 2, -2, x + 94, 16, '#eeeae3')
        wall.rect(x + 2, 17, x + 94, 19, '#b9b2a4')
        wall.rect(x + 44, 10, x + 52, 11, '#9ba2a6')
    ventana(wall, 304, 0, 426, 58)
    # sobre de la cocina (oscuro) y muebles de abajo
    wall.rect(0, 70, W - 1, 77, '#3a3836')
    wall.rect(0, 70, W - 1, 70, '#6a6663')
    wall.rect(0, 78, W - 1, 79, '#1f1e1d')
    for x in range(0, W, 64):
        bevel(wall, x + 1, 81, x + 62, 99, '#eeeae3', 1.08, 0.82)
        wall.rect(x + 22, 88, x + 40, 90, '#a7aeb2')
        wall.rect(x + 22, 88, x + 40, 88, '#dfe4e6')
        bevel(wall, x + 1, 102, x + 62, 168, '#eeeae3', 1.08, 0.82)
        wall.rect(x + 54, 110, x + 56, 134, '#a7aeb2')
    wall.rect(0, 169, W - 1, SUELO, '#4a4540')
    # la refri, con dibujos de los chiquitos pegados
    fx = 556
    wall.rect(fx - 2, -2, fx + 112, SUELO, '#8f969a')
    bevel(wall, fx, -2, fx + 110, 58, '#f1f3f3', 1.05, 0.8)
    bevel(wall, fx, 61, fx + 110, 176, '#f1f3f3', 1.05, 0.8)
    wall.rect(fx + 2, 177, fx + 108, SUELO, '#2c2a28')
    for y0, y1 in ((20, 50), (70, 130)):
        cylinder(wall, fx + 6, y0, fx + 9, y1, '#b9c0c4')
    wall.rect(fx + 50, 80, fx + 80, 112, '#fbfbf7')           # dibujo
    wall.rect(fx + 60, 78, fx + 70, 81, '#e8dca0')            # cinta
    wall.circ(fx + 58, 90, 4, '#f5c531')
    wall.rect(fx + 64, 96, fx + 76, 106, '#e8423a')
    wall.poly([(fx + 62, 96), (fx + 70, 89), (fx + 78, 96)], '#2f7fd8')
    for (mx, my, mc) in ((fx + 30, 30, '#e8423a'), (fx + 84, 20, '#3fb36a'), (fx + 90, 124, '#f5c531'), (fx + 26, 140, '#2f7fd8')):
        wall.circ(mx, my, 4, mc)
        wall.px(mx - 1, my - 2, '#ffffff')
    glow(wall, [(304, 58), (426, 58), (540, SUELO), (380, SUELO)], '#fff6d6', 55)
    wall.fog('#f3ead8', 0.18)
    capas.append(('pared', 0.08, wall))

    # --- bancos altos de la barra y la escoba
    mid = Layer(W, H)
    for x0 in (80, 340, 600):
        for a, b in ((x0, x0 - 16), (x0 + 60, x0 + 76)):
            mid.line([(a, -6), (b, SUELO + 8)], '#8a9297', 7)
            mid.line([(a - 2, -6), (b - 2, SUELO + 8)], '#c9d0d4', 3)
            mid.line([(a - 2, -6), (b - 2, SUELO + 8)], '#f1f5f7', 1)
        mid.rect(x0 - 12, 112, x0 + 72, 117, '#8a9297')
        mid.rect(x0 - 12, 112, x0 + 72, 113, '#e6ebee')
        mid.rect(x0 - 30, -6, x0 + 90, 6, '#6b4a34')
        mid.rect(x0 - 30, 5, x0 + 90, 6, '#3f2a1c')
    mid.line([(480, -6), (540, SUELO - 46)], '#b93a28', 6)
    mid.line([(478, -6), (538, SUELO - 46)], '#e8604a', 2)
    mid.poly([(522, SUELO - 50), (556, SUELO - 50), (578, SUELO + 6), (500, SUELO + 6)], '#e7c64a')
    for k in range(9):
        mid.line([(526 + k * 3, SUELO - 44), (504 + k * 8, SUELO + 6)], '#b9962a')
    mid.rect(518, SUELO - 56, 560, SUELO - 48, '#3a6fb8')
    mid.fog('#efe4cd', 0.22)
    capas.append(('medio', 0.45, mid))

    # --- cerca: el plato de Marshall, una cuchara, cereal, arroz y una papa
    near = Layer(W, H)
    bx = 120
    near.ell(bx - 4, SUELO - 50, bx + 124, SUELO - 34, '#b4302a')
    near.poly([(bx, SUELO - 42), (bx + 120, SUELO - 42), (bx + 104, SUELO + 4), (bx + 16, SUELO + 4)], '#d8402f')
    near.poly([(bx, SUELO - 42), (bx + 30, SUELO - 42), (bx + 34, SUELO + 4), (bx + 16, SUELO + 4)], '#ec6a54')
    near.poly([(bx + 96, SUELO - 42), (bx + 120, SUELO - 42), (bx + 104, SUELO + 4), (bx + 92, SUELO + 4)], '#a82c22')
    r = R(11)
    for i in range(22):   # croquetas
        x = bx + 10 + r.randint(0, 100)
        y = SUELO - 52 + r.randint(-6, 6) - int(10 * math.sin((x - bx) / 120 * math.pi))
        near.ell(x - 5, y - 4, x + 5, y + 4, '#8a5428')
        near.px(x - 2, y - 2, '#b8804a')
    near.ell(bx - 2, SUELO - 46, bx + 122, SUELO - 40, '#f07a64')
    # cuchara recostada
    near.line([(400, SUELO + 2), (468, SUELO - 96)], '#8e979c', 7)
    near.line([(398, SUELO + 1), (466, SUELO - 97)], '#dfe5e8', 2)
    sphere(near, 478, SUELO - 112, 18, lambda dx, dy, nz: '#b9c1c6', flat=1.3)
    # aros de cereal
    for (x, y) in ((260, SUELO - 7), (285, SUELO - 7), (272, SUELO - 20), (660, SUELO - 7)):
        near.circ(x, y, 9, '#e0922e')
        near.circ(x - 2, y - 2, 6, '#f2b44e')
        near.circ(x, y, 3, (0, 0, 0, 0))
    for i in range(30):
        x = r.randint(300, 720)
        near.ell(x, SUELO - 2, x + 5, SUELO + 1, '#fbf8ee')
    sphere(near, 560, SUELO - 20, 26, lambda dx, dy, nz: '#c19a5c' if (int(dx * 7) + int(dy * 5)) % 4 else '#a67d44', flat=0.8)
    capas.append(('cerca', 0.75, near))

    suelo = Layer(W, H)
    ceramica(suelo, seed=12)
    capas.append(('suelo', 1.0, suelo))

    fg = Layer(W, H)
    cylinder(fg, 250, 0, 282, H, '#2e2622')
    capas.append(('frente', 1.4, fg))
    return capas


# ================================================================ SALA
def sala():
    capas = []
    wall = Layer(W, H)
    wall.vgrad(0, 0, W - 1, SUELO, ['#bfd6c8', '#d5e6dc', '#d9e9df'])
    # puerta principal de madera clara con tableros
    dx = 60
    wall.rect(dx - 10, -2, dx + 200, SUELO, '#8a5e3a')
    wall.rect(dx, -2, dx + 190, SUELO, '#c99459')
    r = R(21)
    for i in range(60):
        x = dx + r.randint(0, 190)
        wall.line([(x, r.randint(-2, 160)), (x, r.randint(-2, SUELO))], r.choice(['#d8a56a', '#b88048']))
    for cx in (dx + 14, dx + 102):
        for (y0, y1) in ((-2, 60), (74, 164)):
            bevel(wall, cx, y0, cx + 74, y1, '#bd8750', 0.8, 1.2)
            bevel(wall, cx + 5, y0 + 5, cx + 69, y1 - 5, '#cf9b60', 1.12, 0.82)
    sphere(wall, dx + 176, 96, 7, lambda *_: '#d9b04a')
    # repisas flotantes con figuritas
    for (x0, y0) in ((300, 40), (330, 88)):
        wall.rect(x0, y0, x0 + 90, y0 + 5, '#3a2a22')
        wall.rect(x0, y0, x0 + 90, y0, '#5a463a')
        for k in range(5):
            c = ['#f1eadc', '#8aa6c8', '#d8b24a', '#c98a8a', '#9cc4a0'][(k + x0) % 5]
            hx = x0 + 8 + k * 17
            wall.rect(hx, y0 - 12, hx + 7, y0 - 1, c)
            wall.circ(hx + 3, y0 - 15, 3, c)
    # ventana con cortinas café
    ventana(wall, 470, 0, 650, 104, seed=22)
    for (a, b) in ((440, 500), (620, 690)):
        for x in range(a, b):
            k = (x - a) % 10
            c = '#6e3b36' if k < 5 else ('#83504a' if k < 7 else '#552b27')
            wall.rect(x, -2, x, 150 + int(3 * math.sin(x / 4)), c)
    wall.rect(430, -2, 700, 3, '#3a2a22')
    glow(wall, [(500, 104), (620, 104), (700, SUELO), (520, SUELO)], '#fff3d2', 60)
    rodapie(wall, '#6b4a34')
    wall.fog('#e6efe6', 0.16)
    capas.append(('pared', 0.08, wall))

    # --- la butaca terracota gigante y la mata
    mid = Layer(W, H)
    x0, x1 = 120, 470
    tc, tl, td, tk = '#b5714a', '#c98a6e', '#8f5238', '#7a4430'
    # respaldo
    mid.rect(x0 + 40, 0, x1 - 40, 90, td)
    mid.ell(x0 + 40, -20, x1 - 40, 20, tc)
    for x in range(x0 + 60, x1 - 50, 58):
        mid.rect(x, 12, x + 1, 88, tk)          # capitoné
        mid.circ(x, 40, 2, tk)
    # cojín del asiento
    mid.rect(x0 + 50, 86, x1 - 50, 124, tc)
    mid.ell(x0 + 50, 78, x1 - 50, 98, tl)
    mid.rect(x0 + 50, 118, x1 - 50, 124, td)
    # faldón
    mid.rect(x0 + 50, 124, x1 - 50, 166, tc)
    mid.rect(x0 + 50, 124, x1 - 50, 127, tl)
    for x in range(x0 + 56, x1 - 50, 6):
        mid.px(x, 160, tl)
    # brazos enrollados
    for (a, b) in ((x0, x0 + 62), (x1 - 62, x1)):
        mid.rect(a, 40, b, 166, tc)
        mid.rect(b - 10, 40, b, 166, td)
        mid.rect(a, 40, a + 5, 166, tl)
        mid.ell(a - 8, 12, b + 8, 70, td)
        mid.ell(a - 6, 12, b + 6, 64, tc)
        mid.ell(a + 2, 18, b - 14, 50, tl)
        mid.ell(a + 18, 30, b - 26, 46, tk)
    mid.rect(x0, 166, x1, 172, '#5e3524')
    for lx in (x0 + 8, x1 - 22):
        mid.poly([(lx, 172), (lx + 14, 172), (lx + 11, SUELO + 6), (lx + 3, SUELO + 6)], '#4a3222')
    # mata en maceta
    px0 = 600
    r = R(23)
    for i in range(14):
        blade(mid, px0 + 50 + r.randint(-20, 20), 110, r.randint(90, 150), r.randint(-80, 80), 16,
              r.choice(['#2f6a3a', '#3f8a48', '#2a5a33']))
    mid.poly([(px0, 104), (px0 + 100, 104), (px0 + 88, SUELO + 6), (px0 + 12, SUELO + 6)], '#b8694a')
    mid.poly([(px0, 104), (px0 + 24, 104), (px0 + 30, SUELO + 6), (px0 + 12, SUELO + 6)], '#d08662')
    mid.rect(px0 - 4, 100, px0 + 104, 112, '#a45a3c')
    mid.fog('#e3ece2', 0.2)
    capas.append(('medio', 0.4, mid))

    # --- cerca: libros, carrito, una media, una canica y un cojín
    near = Layer(W, H)
    for i in range(6):
        near.rect(460 + i * 8, SUELO - 10, 467 + i * 8, SUELO, '#e05a7a' if i % 2 else '#f4f4ee')
    sphere(near, 560, SUELO - 9, 9, lambda dx, dy, nz: '#3f8fd6' if dx < 0.2 else '#6cc0f2')
    near.ell(620, SUELO - 40, 740, SUELO + 4, '#d6a93a')
    near.ell(626, SUELO - 38, 730, SUELO - 12, '#ecc255')
    near.rect(676, SUELO - 34, 680, SUELO - 4, '#b98a2a')
    capas.append(('cerca', 0.72, near))

    # --- piso: la alfombra tejida
    suelo = Layer(W, H)
    suelo.rect(0, SUELO, W - 1, H - 1, '#d7c7ae')
    suelo.vgrad(0, SUELO + 3, W - 1, H - 1, ['#d7c7ae', '#c4b394', '#9e8d70'])
    for x in range(0, W, 24):
        for y in (SUELO + 9, SUELO + 22):
            suelo.poly([(x + 12, y - 5), (x + 20, y), (x + 12, y + 5), (x + 4, y)], '#b5654a' if y < 200 else '#6e7e83')
            suelo.px(x + 12, y, '#f1e4c8')
    for x in range(0, W, 2):
        suelo.px(x, SUELO + 1 + (x // 2) % 2, '#bfae90')
    suelo.rect(0, SUELO, W - 1, SUELO, '#eee2c9')
    capas.append(('suelo', 1.0, suelo))
    return capas


# ================================================================ CUARTO (dormitorio)
def letra(L, ch, x, y, c):
    F = {'A': ["010", "101", "111", "101", "101"], 'B': ["110", "101", "110", "101", "110"],
         'C': ["011", "100", "100", "100", "011"], 'F': ["111", "100", "110", "100", "100"],
         'M': ["10001", "11011", "10101", "10001", "10001"]}
    for j, row in enumerate(F[ch]):
        for i, v in enumerate(row):
            if v == '1':
                L.rect(x + i * 2, y + j * 2, x + i * 2 + 1, y + j * 2 + 1, c)


def cuarto():
    capas = []
    wall = Layer(W, H)
    wall.vgrad(0, 0, W - 1, SUELO, ['#bcd0dc', '#d6e3ea', '#dbe7ee'])
    r = R(31)
    for i in range(18):     # estrellitas pintadas
        x, y = r.randint(0, W), r.randint(4, 150)
        wall.rect(x, y - 2, x, y + 2, '#f3f7fa')
        wall.rect(x - 2, y, x + 2, y, '#f3f7fa')
    ventana(wall, 90, 0, 240, 96, seed=32)
    for (a, b) in ((70, 104), (226, 260)):
        for x in range(a, b):
            wall.rect(x, -2, x, 130, '#7aa6d6' if (x - a) % 8 < 5 else '#5f8ac0')
    # dibujo de los chiquitos pegado en la pared
    wall.rect(300, 40, 360, 84, '#fdfcf6')
    wall.circ(348, 52, 7, '#f5c531')
    wall.rect(310, 64, 334, 80, '#e8423a')
    wall.poly([(306, 64), (322, 52), (338, 64)], '#2f7fd8')
    wall.rect(300, 80, 360, 84, '#6cb84a')
    wall.rect(326, 37, 334, 42, '#e8dca0')
    # ropero de madera
    ox = 470
    wall.rect(ox - 2, -2, ox + 232, SUELO, '#6b4a34')
    for dx in (0, 116):
        bevel(wall, ox + dx + 2, -2, ox + dx + 114, 168, '#b78d63', 1.12, 0.8)
        for k in range(10):
            yy = r.randint(0, 160)
            wall.line([(ox + dx + 8 + k * 10, yy), (ox + dx + 8 + k * 10, yy + r.randint(8, 30))], '#a67c52')
    cylinder(wall, ox + 108, 60, ox + 111, 100, '#d9b04a')
    cylinder(wall, ox + 122, 60, ox + 125, 100, '#d9b04a')
    wall.rect(ox, 170, ox + 230, SUELO, '#4a3222')
    glow(wall, [(90, 96), (240, 96), (360, SUELO), (150, SUELO)], '#fff6dc', 60)
    wall.fog('#e6eef3', 0.16)
    capas.append(('pared', 0.08, wall))

    # --- la cama con la cobija color salvia, oscuro debajo; baúl de juguetes
    mid = Layer(W, H)
    bx0, bx1 = 0, 420
    mid.rect(bx0, 120, bx1, SUELO + 6, '#23252c')
    for lx in (bx0 + 20, bx1 - 40):
        mid.rect(lx, 120, lx + 18, SUELO + 6, '#6b4a34')
        mid.rect(lx, 120, lx + 3, SUELO + 6, '#8a6446')
    for x in range(bx0, bx1 + 1):
        hem = 128 + int(5 * math.sin(x / 14))
        k = (x // 3) % 12
        c = '#8ea58a' if k < 7 else ('#a3b99f' if k < 9 else '#728a6f')
        mid.rect(x, -4, x, hem, c)
        mid.px(x, hem, '#5f755c')
    for i in range(40):
        x, y = r.randint(bx0 + 5, bx1 - 5), r.randint(4, 110)
        mid.rect(x, y, x + 1, y + 1, '#dfe8d8')
    # pantufla perdida debajo de la cama y un conejo de polvo
    mid.ell(200, SUELO - 12, 260, SUELO + 4, '#e58aa6')
    mid.ell(206, SUELO - 10, 240, SUELO, '#f4b6c8')
    clump(mid, 320, SUELO - 4, 8, ['#6a6d78', '#8a8d98', '#a9acb6'], seed=33)
    # baúl de juguetes
    tx = 540
    bevel(mid, tx, 96, tx + 180, SUELO + 6, '#e0a02e', 1.15, 0.78)
    for k, c in enumerate(('#e8423a', '#2f7fd8', '#3fb36a')):
        mid.rect(tx, 116 + k * 20, tx + 180, 121 + k * 20, c)
    bevel(mid, tx - 6, 84, tx + 186, 98, '#c9842a', 1.15, 0.75)
    mid.poly([(tx + 40, 84), (tx + 60, 60), (tx + 70, 64), (tx + 54, 84)], '#8b5cf0')   # algo que asoma
    sphere(mid, tx + 130, 76, 12, lambda *_: '#f06d8f')
    mid.fog('#e0e9ee', 0.18)
    capas.append(('medio', 0.42, mid))

    # --- cerca: cubos con letras, crayolas, legos y un dinosaurio
    near = Layer(W, H)
    for i, c in enumerate(('#e8423a', '#2f7fd8', '#3fb36a', '#8b5cf0', '#f5c531')):
        x = 250 + i * 26
        y = SUELO - 7 - (i % 2) * 3
        near.rect(x, y, x + 20, y + 6, c)
        near.poly([(x + 20, y), (x + 26, y + 3), (x + 20, y + 6)], '#f1d9b0')
        near.rect(x + 3, y + 1, x + 16, y + 1, shade(C(c), 1.3))
    dx0 = 600
    near.ell(dx0, SUELO - 40, dx0 + 70, SUELO - 6, '#5cb85c')
    near.ell(dx0 + 50, SUELO - 70, dx0 + 90, SUELO - 40, '#5cb85c')
    near.poly([(dx0, SUELO - 22), (dx0 - 34, SUELO - 8), (dx0 + 4, SUELO - 12)], '#5cb85c')
    for lx in (dx0 + 12, dx0 + 46):
        near.rect(lx, SUELO - 12, lx + 10, SUELO, '#4a9a4a')
    for s in range(5):
        near.poly([(dx0 + 10 + s * 12, SUELO - 38), (dx0 + 16 + s * 12, SUELO - 48), (dx0 + 22 + s * 12, SUELO - 38)], '#f5c531')
    near.circ(dx0 + 76, SUELO - 60, 3, '#ffffff')
    near.px(dx0 + 77, SUELO - 60, '#111111')
    capas.append(('cerca', 0.72, near))

    # --- piso: alfombra de fomi de rompecabezas
    suelo = Layer(W, H)
    cols = ['#e45b4b', '#4a8fd8', '#f2c53d', '#5cb85c']
    for i, x in enumerate(range(0, W, 64)):
        c = C(cols[i % 4])
        suelo.vgrad(x, SUELO, x + 63, H - 1, [shade(c, 1.1), c, shade(c, 0.75)])
        suelo.rect(x, SUELO, x + 63, SUELO, shade(c, 1.3))
        suelo.rect(x + 26, SUELO - 3, x + 37, SUELO, shade(c, 1.1))   # piquito del rompecabezas
        suelo.rect(x, SUELO, x, H - 1, shade(c, 0.7))
    capas.append(('suelo', 1.0, suelo))
    return capas


# ================================================================ BAÑO
def bano():
    capas = []
    wall = Layer(W, H)
    wall.rect(0, 0, W - 1, SUELO, '#c9d3d3')
    for x in range(0, W, 16):
        for y in range(0, SUELO, 16):
            c = '#8fd1d0' if 112 <= y < 128 else '#f3f5f4'
            wall.rect(x + 1, y + 1, x + 15, y + 15, c)
            wall.rect(x + 1, y + 1, x + 15, y + 1, shade(C(c), 1.05))
            wall.px(x + 3, y + 3, '#ffffff')
    # toalla rosada en su barra
    wall.rect(60, 4, 200, 8, '#b9c0c4')
    for x in range(76, 184):
        k = (x - 76) % 12
        c = '#f39aa8' if k < 8 else '#d9788a'
        bot = 110 + int(4 * math.sin(x / 5))
        wall.rect(x, 8, x, bot, c)
        for yy in (90, 96):
            wall.px(x, yy, '#ffffff')
    # cortina del baño con peces
    cx0 = 460
    for x in range(cx0, cx0 + 260):
        k = math.sin((x - cx0) / 9)
        c = '#e9f3f6' if k > 0.3 else ('#d2e4ea' if k > -0.4 else '#b8d0d8')
        wall.rect(x, -2, x, 176, c)
    r = R(41)
    for i in range(22):
        x, y = r.randint(cx0 + 10, cx0 + 250), r.randint(10, 160)
        c = r.choice(['#f5a23a', '#3fa7d8', '#f06d8f'])
        wall.ell(x, y, x + 8, y + 5, c)
        wall.poly([(x, y + 2), (x - 4, y - 1), (x - 4, y + 6)], c)
        wall.px(x + 6, y + 1, '#1a1a1a')
    wall.rect(cx0 - 4, -2, cx0 + 264, 2, '#b9c0c4')
    wall.fog('#eef4f5', 0.12)
    capas.append(('pared', 0.08, wall))

    # --- el inodoro gigante y el basurero
    mid = Layer(W, H)
    sphere(mid, 235, 28, 120, lambda *_: '#f6f7f5', flat=0.34)
    cylinder(mid, 170, 40, 300, SUELO + 6, '#f2f3f1')
    mid.rect(120, 20, 350, 22, '#dfe3e2')
    mid.rect(150, SUELO - 4, 320, SUELO + 6, '#e3e7e6')
    for bx in (160, 306):
        sphere(mid, bx, SUELO - 8, 6, lambda *_: '#ffffff')
    cylinder(mid, 560, 96, 650, SUELO + 6, '#b6d8d6', spec='#ffffff')
    mid.rect(556, 90, 654, 98, '#8fbcba')
    mid.rect(590, SUELO - 4, 620, SUELO + 6, '#6f8f8d')
    mid.fog('#e6eff0', 0.2)
    capas.append(('medio', 0.45, mid))

    # --- cerca: patito, champú, rollo de papel y jabón
    near = Layer(W, H)
    cylinder(near, 320, SUELO - 86, 356, SUELO, '#8c6bd6', spec='#e6dcfb')
    near.rect(326, SUELO - 94, 350, SUELO - 86, '#5a3fa8')
    near.rect(320, SUELO - 60, 356, SUELO - 34, '#f4f0fb')
    near.rect(326, SUELO - 52, 350, SUELO - 50, '#8c6bd6')
    near.rect(326, SUELO - 46, 344, SUELO - 44, '#8c6bd6')
    for (x, y, rr) in ((652, SUELO - 22, 5), (664, SUELO - 26, 4), (690, SUELO - 20, 3)):
        near.circ(x, y, rr, '#e8f6fb')
        near.px(x - 1, y - 1, '#ffffff')
    capas.append(('cerca', 0.72, near))

    # --- piso de cerámica gris azulado, mojado
    suelo = Layer(W, H)
    ceramica(suelo, base='#b8c4c9', grout='#94a2a8', vetas='#aab7bc', seed=42)
    for i in range(6):
        x = r.randint(0, W)
        suelo.ell(x, SUELO + 5, x + r.randint(40, 90), SUELO + 12, '#d5e3e8')
        suelo.rect(x + 8, SUELO + 7, x + 20, SUELO + 7, '#f4fbfd')
    capas.append(('suelo', 1.0, suelo))

    # --- burbujas de jabón que pasan adelante
    fg = Layer(W, H)
    for i in range(9):
        x, y, rr = r.randint(0, W), r.randint(20, 150), r.randint(5, 12)
        fg.circ(x, y, rr, (200, 235, 245, 150))
        fg.circ(x, y, rr - 1, (0, 0, 0, 0))
        fg.rect(x - rr // 2, y - rr // 2, x - rr // 2 + 1, y - rr // 2 + 1, '#ffffff')
    capas.append(('frente', 1.3, fg))
    return capas
