"""Cocina, sala, cuarto y baño armados con los muebles de las hojas de la dueña (escenarios/piezas/*.png,
hechas por recortar_hojas.py). Los muebles grandes van en las capas de atrás, con la base escondida
detrás del borde del piso (unos pixeles bajo SUELO), para que se vean parados en el piso de su capa y no flotando.
"""
import math, random
from PIL import Image
from pinta import Layer, clump, blade, bevel, glow, cylinder, sphere, C
from pixel import shade
from cuartos import ceramica, rodapie, ventana, W, H, SUELO
import os

PZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'escenarios', 'piezas')
_cache = {}


def pz(nombre, achicar=1):
    k = (nombre, achicar)
    if k not in _cache:
        im = Image.open(os.path.join(PZ, nombre + '.png')).convert('RGBA')
        if achicar > 1:
            im = im.resize((im.width // achicar, im.height // achicar), Image.NEAREST)
        _cache[k] = im
    return _cache[k]


def poner(L, nombre, x, base=None, y=None, achicar=1):
    """Pega una pieza con su base en `base` (o su borde de arriba en `y`)."""
    im = pz(nombre, achicar)
    yy = y if y is not None else base - im.height
    L.paste(im, x, yy)
    return im


def R(s):
    return random.Random(s)


def mosaico(L, a='#b8452f', b='#efe3c8', c='#2f6a8a'):
    """Piso de mosaico como el de las casas viejas de Costa Rica."""
    L.rect(0, SUELO, W - 1, H - 1, b)
    for x0 in range(0, W, 16):
        for y0 in range(SUELO + 2, H, 16):
            L.rect(x0, y0, x0 + 15, y0 + 15, b)
            L.poly([(x0 + 8, y0 + 1), (x0 + 15, y0 + 8), (x0 + 8, y0 + 15), (x0 + 1, y0 + 8)], a)
            L.rect(x0 + 6, y0 + 6, x0 + 9, y0 + 9, c)
            L.rect(x0, y0, x0 + 15, y0, shade(C(b), 0.85))
            L.rect(x0, y0, x0, y0 + 15, shade(C(b), 0.85))
    L.vgrad(0, SUELO, W - 1, SUELO + 1, [shade(C(b), 1.1), shade(C(b), 0.9)])
    # un poco más oscuro hacia adelante
    ov = Layer(W, H)
    ov.rect(0, SUELO + 18, W - 1, H - 1, (40, 20, 10, 50))
    L.im.alpha_composite(ov.im)


def tablas(L, base='#a8703f'):
    """Piso de tablas de madera."""
    b = C(base)
    L.vgrad(0, SUELO, W - 1, H - 1, [shade(b, 1.1), b, shade(b, 0.75)])
    r = R(7)
    for y in range(SUELO + 6, H, 7):
        L.rect(0, y, W - 1, y, shade(b, 0.7))
        off = r.randint(0, 90)
        for x in range(off, W, 96):
            L.rect(x, y - 6, x, y, shade(b, 0.7))
    for i in range(60):
        x, y = r.randint(0, W - 20), r.randint(SUELO + 2, H - 2)
        L.rect(x, y, x + r.randint(4, 14), y, shade(b, 0.88))
    L.rect(0, SUELO, W - 1, SUELO, shade(b, 1.25))


def azulejos(L, y0, y1, fondo='#f3f5f4', junta='#c9d3d3', tam=16, franja=None):
    for x in range(0, W, tam):
        for y in range(y0, y1, tam):
            c = franja[1] if franja and franja[0] <= y < franja[0] + tam else fondo
            L.rect(x, y, x + tam - 1, y + tam - 1, junta)
            L.rect(x + 1, y + 1, x + tam - 1, y + tam - 1, c)
            L.rect(x + 1, y + 1, x + tam - 1, y + 1, shade(C(c), 1.05))


# ================================================================ COCINA
def cocina():
    capas = []
    wall = Layer(W, H)
    wall.vgrad(0, 0, W - 1, SUELO, ['#eadcbc', '#f3e8d0', '#f1e4c8'])
    # azulejo con florcita azul detrás de la cocina y el mueble
    for x in range(0, W, 14):
        for y in range(36, 110, 14):
            wall.rect(x, y, x + 13, y + 13, '#d9d2c2')
            wall.rect(x + 1, y + 1, x + 13, y + 13, '#fbf7ee')
            wall.rect(x + 6, y + 4, x + 8, y + 10, '#4a7fb8')
            wall.rect(x + 4, y + 6, x + 10, y + 8, '#4a7fb8')
            wall.px(x + 7, y + 7, '#f3c64a')
    ventana(wall, 330, 6, 450, 96, seed=51)
    glow(wall, [(330, 96), (450, 96), (540, SUELO), (390, SUELO)], '#fff6d6', 50)
    # mueble de cocina de madera entre la cocina de gas y la refri
    wall.rect(250, SUELO - 70, 548, SUELO + 4, '#8a5a34')
    for x in range(252, 548, 50):
        bevel(wall, x + 2, SUELO - 62, x + 46, SUELO - 4, '#a8703f', 1.15, 0.78)
        wall.rect(x + 22, SUELO - 40, x + 26, SUELO - 38, '#e0c070')
    wall.rect(246, SUELO - 76, 552, SUELO - 69, '#3a3836')
    wall.rect(246, SUELO - 76, 552, SUELO - 76, '#6a6663')
    poner(wall, 'chorreador', 280, base=SUELO - 76, achicar=2)
    poner(wall, 'hierbas', 400, base=SUELO - 76)
    poner(wall, 'cocina_gas', 100, base=SUELO + 4)
    poner(wall, 'refri', 575, base=SUELO + 4)
    wall.fog('#f3ead8', 0.16)
    capas.append(('pared', 0.08, wall))

    # --- el molinillo gigante y el chorreador gigante
    mid = Layer(W, H)
    mid.fog('#efe4cd', 0.22)
    capas.append(('medio', 0.4, mid))

    near = Layer(W, H)
    poner(near, 'hierbas', 520, base=SUELO + 3)
    capas.append(('cerca', 0.72, near))

    suelo = Layer(W, H)
    mosaico(suelo)
    capas.append(('suelo', 1.0, suelo))
    return capas


# ================================================================ SALA
def sala():
    capas = []
    wall = Layer(W, H)
    wall.vgrad(0, 0, W - 1, SUELO, ['#bfd6c8', '#d5e6dc', '#d9e9df'])
    # cenefa de madera arriba
    wall.rect(0, 0, W - 1, 6, '#8a5a34')
    wall.rect(0, 6, W - 1, 7, '#5a3a22')
    poner(wall, 'cuadro_iglesia', 70, y=34, achicar=2)
    ventana(wall, 470, 10, 640, 110, seed=61)
    for (a, b) in ((446, 494), (616, 664)):
        for x in range(a, b):
            k = (x - a) % 10
            c = '#7a3b36' if k < 5 else ('#93504a' if k < 7 else '#5a2b27')
            wall.rect(x, 8, x, 160 + int(3 * math.sin(x / 4)), c)
    wall.rect(436, 7, 674, 11, '#3a2a22')
    glow(wall, [(494, 110), (616, 110), (700, SUELO), (520, SUELO)], '#fff3d2', 55)
    rodapie(wall, '#6b4a34')
    poner(wall, 'tv_mueble', 250, base=SUELO + 2, achicar=2)
    poner(wall, 'abanico', 190, y=-4, achicar=2)
    wall.fog('#e6efe6', 0.14)
    capas.append(('pared', 0.08, wall))

    mid = Layer(W, H)
    poner(mid, 'sofa', 40, base=SUELO + 6, achicar=2)
    poner(mid, 'mecedora', 560, base=SUELO + 6, achicar=2)
    mid.fog('#e3ece2', 0.38)
    capas.append(('medio', 0.4, mid))

    near = Layer(W, H)
    capas.append(('cerca', 0.72, near))

    suelo = Layer(W, H)
    ceramica(suelo, base='#e9e3d8', grout='#c9c0b2', seed=62)
    capas.append(('suelo', 1.0, suelo))
    return capas


# ================================================================ CUARTO
def cuarto():
    capas = []
    wall = Layer(W, H)
    wall.vgrad(0, 0, W - 1, SUELO, ['#bcd0dc', '#d6e3ea', '#dbe7ee'])
    r = R(71)
    for i in range(14):
        x, y = r.randint(0, W), r.randint(4, 140)
        wall.rect(x, y - 2, x, y + 2, '#f3f7fa')
        wall.rect(x - 2, y, x + 2, y, '#f3f7fa')
    poner(wall, 'cuadro_volcan', 150, y=24)
    poner(wall, 'crucifijo', 290, y=26)
    rodapie(wall, '#8a6446')
    poner(wall, 'ropa_guitarra', 440, base=SUELO + 4)
    wall.fog('#e6eef3', 0.14)
    capas.append(('pared', 0.08, wall))

    mid = Layer(W, H)
    poner(mid, 'cama', 40, base=SUELO + 8)
    poner(mid, 'abanico_pie', 470, base=SUELO + 8)
    mid.fog('#e0e9ee', 0.18)
    capas.append(('medio', 0.42, mid))

    near = Layer(W, H)
    poner(near, 'chancletas', 250, base=SUELO + 3)
    capas.append(('cerca', 0.72, near))

    suelo = Layer(W, H)
    tablas(suelo)
    capas.append(('suelo', 1.0, suelo))
    return capas


# ================================================================ BAÑO
def bano():
    capas = []
    wall = Layer(W, H)
    azulejos(wall, 0, SUELO, franja=(112, '#8fd1d0'))
    poner(wall, 'toalla_verde', 30, y=34)
    poner(wall, 'espejo', 340, y=14)
    poner(wall, 'ducha', 680, y=8)
    wall.fog('#eef4f5', 0.12)
    capas.append(('pared', 0.08, wall))

    mid = Layer(W, H)
    poner(mid, 'inodoro', 60, base=SUELO + 8)
    poner(mid, 'lavamanos', 400, base=SUELO + 8)
    mid.fog('#e6eff0', 0.18)
    capas.append(('medio', 0.45, mid))

    near = Layer(W, H)
    capas.append(('cerca', 0.72, near))

    suelo = Layer(W, H)
    ceramica(suelo, base='#b8c4c9', grout='#94a2a8', vetas='#aab7bc', seed=82)
    r = R(83)
    for i in range(6):
        x = r.randint(0, W)
        suelo.ell(x, SUELO + 5, x + r.randint(40, 90), SUELO + 12, '#d5e3e8')
        suelo.rect(x + 8, SUELO + 7, x + 20, SUELO + 7, '#f4fbfd')
    capas.append(('suelo', 1.0, suelo))

    fg = Layer(W, H)
    for i in range(9):
        x, y, rr = r.randint(0, W), r.randint(20, 150), r.randint(5, 12)
        fg.circ(x, y, rr, (200, 235, 245, 150))
        fg.circ(x, y, rr - 1, (0, 0, 0, 0))
        fg.rect(x - rr // 2, y - rr // 2, x - rr // 2 + 1, y - rr // 2 + 1, '#ffffff')
    capas.append(('frente', 1.3, fg))
    return capas
