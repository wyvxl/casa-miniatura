"""Objetos de cada escenario que sirven de plataforma, y la estrella para juntar.

Salida: ../escenarios/objetos.png (todo en una hoja) + objetos.json con el rectángulo de cada uno
y `top`: cuántos pixeles desde arriba empieza la parte donde se puede parar.
"""
import json, math, os
import numpy as np
from PIL import Image
from pinta import Layer, bevel, sphere, cylinder, clump, C
from pixel import shade
from objetos_lado import LADO

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, '..', 'escenarios')


def obj(w, h):
    return Layer(w, h, wrap=False)


def piedra():
    L = obj(56, 26)
    sphere(L, 28, 20, 27, lambda dx, dy, nz: '#9a938a' if (int(dx * 9) + int(dy * 7)) % 5 else '#857d74', flat=0.7)
    return L, 4


def maceta():
    L = obj(40, 64)
    for i, c in enumerate(('#e8423a', '#f5c531', '#f06d8f')):
        clump(L, 12 + i * 8, 10 + (i % 2) * 4, 6, [shade(C(c), 0.7), c, shade(C(c), 1.3)], seed=i)
    L.rect(19, 16, 20, 30, '#3f7a3a')
    L.poly([(2, 30), (38, 30), (32, 63), (8, 63)], '#b8694a')
    L.poly([(2, 30), (12, 30), (15, 63), (8, 63)], '#d08662')
    L.rect(0, 28, 39, 34, '#a45a3c')
    L.rect(0, 28, 39, 28, '#d08662')
    return L, 28


def ladrillo():
    L = obj(48, 18)
    bevel(L, 0, 0, 47, 17, '#b44a32', 1.2, 0.72)
    for (x, y) in ((8, 6), (22, 6), (36, 6)):
        L.ell(x - 4, y - 2, x + 4, y + 4, '#7a2a1a')
    return L, 0


def hoja():
    L = obj(64, 14)
    L.poly([(0, 7), (18, 1), (46, 0), (63, 6), (46, 12), (18, 13)], '#4c8a41')
    L.poly([(0, 7), (18, 1), (46, 0), (63, 6), (46, 4), (18, 5)], '#6cb84a')
    L.line([(2, 7), (60, 6)], '#2f5a2a')
    return L, 1


def esponja():
    L = obj(52, 24)
    bevel(L, 0, 0, 51, 7, '#3fae5c', 1.2, 0.75)
    bevel(L, 0, 8, 51, 23, '#f5d13a', 1.15, 0.8)
    for (x, y) in ((6, 13), (18, 18), (30, 12), (42, 17), (12, 20), (38, 21)):
        L.px(x, y, '#d0a820')
        L.px(x + 1, y, '#d0a820')
    return L, 0


def cereal():
    L = obj(44, 76)
    bevel(L, 0, 0, 43, 75, '#e8423a', 1.15, 0.78)
    L.rect(4, 8, 39, 20, '#f5c531')
    L.rect(6, 11, 37, 17, '#e8423a')
    for (x, y) in ((12, 38), (26, 44), (18, 54), (30, 58)):
        L.circ(x, y, 6, '#e0922e')
        L.circ(x, y, 2, '#f7f3e8')
    L.rect(0, 0, 43, 3, '#c7302a')
    return L, 0


def lata():
    L = obj(30, 40)
    cylinder(L, 0, 4, 29, 39, '#d6342c', spec='#ffd0c8')
    L.rect(0, 16, 29, 27, '#f4f0e6')
    L.rect(6, 20, 22, 23, '#3a8a3a')
    L.ell(0, 0, 29, 8, '#c5cacd')
    L.ell(3, 2, 26, 6, '#9aa0a4')
    return L, 2


def libro():
    L = obj(72, 14)
    L.rect(0, 0, 71, 13, '#3d6fb0')
    L.rect(2, 2, 69, 11, '#f4efe2')
    for y in (4, 7, 10):
        L.rect(3, y, 68, y, '#ddd6c6')
    L.rect(0, 0, 71, 1, '#6c97d0')
    L.rect(66, 0, 71, 13, '#2d558c')
    return L, 0


def cojin():
    L = obj(64, 26)
    sphere(L, 32, 14, 32, lambda *_: '#8ea58a', flat=0.4)
    L.rect(31, 5, 32, 22, '#6f866b')
    return L, 3


def cubo():
    L = obj(30, 30)
    bevel(L, 0, 0, 29, 29, '#2f7fd8', 1.2, 0.75)
    L.rect(4, 4, 25, 25, '#fbf7ea')
    for (x, y) in ((11, 9), (15, 9), (9, 13), (17, 13), (9, 17), (11, 17), (13, 17), (15, 17), (17, 17), (9, 21), (17, 21)):
        L.rect(x, y, x + 1, y + 1, '#2f7fd8')
    return L, 0


def lego():
    L = obj(48, 20)
    bevel(L, 0, 4, 47, 19, '#e8423a', 1.25, 0.75)
    for s in range(4):
        L.rect(3 + s * 12, 0, 10 + s * 12, 4, '#f06a5c')
        L.rect(3 + s * 12, 0, 10 + s * 12, 0, '#ff9a8c')
    return L, 4


def jabon():
    L = obj(40, 16)
    bevel(L, 0, 2, 39, 15, '#f39ab8', 1.2, 0.78)
    L.rect(4, 0, 35, 2, '#f7b6cc')
    L.rect(10, 7, 29, 9, '#e07898')
    return L, 0


def rollo():
    L = obj(40, 44)
    cylinder(L, 0, 6, 39, 43, '#fbfbf7')
    L.ell(0, 0, 39, 12, '#e6e6e0')
    L.ell(12, 3, 27, 9, '#b8a88a')
    return L, 3


def patito():
    L = obj(40, 38)
    sphere(L, 16, 26, 16, lambda *_: '#f7cf2a', flat=0.75)
    sphere(L, 26, 12, 10, lambda *_: '#f7cf2a')
    L.poly([(34, 11), (40, 14), (34, 17)], '#f08a24')
    L.px(28, 9, '#1a1a1a')
    return L, 14


def tachuelas():
    L = obj(34, 14)
    for i, c in enumerate(('#e8423a', '#2f7fd8', '#f5c531')):
        x = 2 + i * 11
        L.poly([(x + 3, 4), (x + 6, 4), (x + 5, 13), (x + 4, 13)], '#c9d0d4')
        L.rect(x + 4, 5, x + 4, 12, '#ffffff')
        sphere(L, x + 4.5, 4, 4.5, lambda *_: c, flat=0.7)
    return L, 0


def puertita():
    """La puertita de ratón al final de cada cuarto."""
    L = obj(40, 52)
    L.ell(0, 0, 39, 40, '#3a2418')
    L.rect(0, 20, 39, 51, '#3a2418')
    L.ell(3, 3, 36, 37, '#9a6a3e')
    L.rect(3, 20, 36, 51, '#9a6a3e')
    for x in (10, 19, 28):
        L.rect(x, 6, x, 51, '#7a5030')
    L.ell(3, 3, 36, 37, (0, 0, 0, 0)) if False else None
    sphere(L, 31, 30, 2.5, lambda *_: '#e6b84a')
    L.rect(14, 12, 25, 22, '#fff2b0')
    L.rect(19, 12, 20, 22, '#9a6a3e')
    L.rect(14, 17, 25, 17, '#9a6a3e')
    return L, 0


def corazon(lleno=True):
    L = obj(9, 8)
    rows = [".XX.XX...", "XRRXRRX..", "XRWRRRX..", "XRRRRRX..", ".XRRRX...", "..XRX....", "...X.....", "........."]
    rows = [".XX.XX.", "XRRXRRX", "XRWRRRX", "XRRRRRX", ".XRRRX.", "..XRX..", "...X..."]
    col = {'X': '#3a1418', 'R': '#e8423a' if lleno else '#5a4a52', 'W': '#ffb0a8' if lleno else '#7a6a72'}
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch in col:
                L.px(i, j, col[ch])
    return L, 0


def mata(alto, seed):
    """Una mata con tallo que sale de la tierra y una hoja ancha arriba (en vez de hojas en el aire)."""
    import random
    r = random.Random(seed)
    L = obj(60, alto + 8)
    base = alto + 7
    L.rect(28, 10, 31, base, '#4f8b3a')
    L.rect(28, 10, 28, base, '#7ab85a')
    for k in range(2):   # hojitas del tallo
        y = r.randint(24, max(26, alto - 10))
        d = -1 if k else 1
        L.poly([(30, y), (30 + d * 14, y - 6), (30 + d * 16, y - 2), (30, y + 3)], '#5a9a44')
    L.poly([(0, 8), (14, 2), (44, 0), (59, 6), (44, 12), (14, 13)], '#4c8a41')
    L.poly([(0, 8), (14, 2), (44, 0), (59, 6), (44, 4), (14, 5)], '#6cb84a')
    L.line([(2, 8), (57, 6)], '#2f5a2a')
    return L, 1


# estrella que gira (4 cuadros), como las 8 escondidas del juego 3D
def estrellas():
    fr = []
    for k in range(6):
        L = obj(16, 16)
        sx = [1.0, 0.7, 0.25, 0.7, 1.0, 0.85][k]
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = 7.5 if i % 2 == 0 else 3.3
            pts.append((8 + math.cos(a) * rr * sx, 8.5 + math.sin(a) * rr))
        L.poly(pts, '#e6a91c')
        L.poly([(8 + (x - 8) * 0.7, 8.5 + (y - 8.5) * 0.7 - 0.6) for x, y in pts], '#ffd84a')
        if sx > 0.5:
            L.px(6, 6, '#fff6c0')
            L.px(7, 5, '#ffffff')
        fr.append(L)
    return fr


OBJETOS = {
    'patio': [('piedra', piedra), ('maceta', maceta), ('ladrillo', ladrillo), ('hoja', hoja),
              ('mata1', lambda: mata(62, 1)), ('mata2', lambda: mata(96, 2)), ('mata3', lambda: mata(130, 3))],
    'cocina': [('esponja', esponja), ('cereal', cereal), ('lata', lata)],
    'sala': [('libro', libro), ('cojin', cojin)],
    'cuarto': [('cubo', cubo), ('lego', lego), ('libro', libro)],
    'bano': [('jabon', jabon), ('rollo', rollo), ('patito', patito)],
    'comun': LADO + [('tachuelas', tachuelas), ('puertita', puertita), ('corazon', corazon), ('corazon_vacio', lambda: corazon(False))],
}


def main():
    items = []
    for esc, lst in OBJETOS.items():
        for name, fn in lst:
            L, top = fn()
            if not name.startswith('corazon'):
                M = Layer(L.w + 2, L.h + 2, wrap=False)   # 1 px de margen para que quepa el contorno
                M.im.alpha_composite(L.im, (1, 1))
                M.outline('#2a1a16')
                L = M
            items.append((esc, name, L.im, top + 1))
    stars = estrellas()
    for s in stars:
        s.outline('#6a3a08')
    # acomodar en filas
    Wsheet, x, y, rowh = 512, 0, 0, 0
    pos = []
    for esc, name, im, top in items:
        if x + im.width > Wsheet:
            x, y = 0, y + rowh + 2
            rowh = 0
        pos.append((esc, name, im, top, x, y))
        x += im.width + 2
        rowh = max(rowh, im.height)
    y += rowh + 2
    sheet = Image.new('RGBA', (Wsheet, y + 18), (0, 0, 0, 0))
    meta = {'estrella': dict(x=0, y=y, w=16, h=16, n=len(stars)), 'objetos': {}}
    for esc, name, im, top, px, py in pos:
        sheet.alpha_composite(im, (px, py))
        al = np.asarray(im)[:, :, 3] > 0
        pf = [int(np.argmax(al[:, x])) if al[:, x].any() else -1 for x in range(im.width)]
        meta['objetos'].setdefault(esc, {})[name] = dict(x=px, y=py, w=im.width, h=im.height, top=top, perfil=pf, pie=[min(c), max(c)] if (c := [x for x in range(im.width) if al[-3:, x].any()]) else [0, im.width - 1])
    for i, s in enumerate(stars):
        sheet.alpha_composite(s.im, (i * 16, y))
    sheet.save(os.path.join(SALIDA, 'objetos.png'))
    json.dump(meta, open(os.path.join(SALIDA, 'objetos.json'), 'w', encoding='utf-8'), indent=1)
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(os.path.join(AQUI, '..', '_revision', 'objetos.png'))
    print('objetos', sheet.size)


if __name__ == '__main__':
    main()
