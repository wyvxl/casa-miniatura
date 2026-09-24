"""El corredor (el frente de la casa, con la piedrilla) y la casa de Keylin (la casa amarilla del vecino).

Objetos nuevos dibujados de lado, con la base plana y el mismo contorno que el resto (lecciones de las
correcciones de la dueña: nada visto desde arriba en diagonal, nada flotando, pocos objetos y típicos del lugar).
Colores de la casa tomados del modelo 3D: fachada blanca, columnas, cornisa terracota, enchape de piedra,
puerta de madera clara, cielo raso oscuro; la casa del vecino crema-amarilla con fascias vino y techo rojo.
"""
import math, random, os
from PIL import Image
from pinta import Layer, clump, blade, bevel, glow, cylinder, sphere, C
from pixel import shade
from objetos_lado import bandas
from cuartos import W, H, SUELO, ventana

CONTORNO = (34, 22, 26, 255)
PZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'escenarios', 'piezas')


def obj(w, h):
    return Layer(w, h, wrap=False)


def terminar(L, doble=False):
    M = Layer(L.w + 2, L.h + 2, wrap=False)
    M.im.alpha_composite(L.im, (1, 1))
    M.outline(CONTORNO)
    im = M.im
    if doble:
        im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    return im


def R(s):
    return random.Random(s)


# ================================================================ objetos (se juegan)
def bloque():
    """Bloque de concreto de lado: gris con textura de poros."""
    L = obj(40, 20)
    bandas(L, 0, 0, 39, 19, '#9ea2a2', 1.15, 0.78)
    L.rect(0, 0, 39, 0, '#c4c8c6')
    r = R(3)
    for i in range(26):
        L.px(r.randint(2, 37), r.randint(2, 17), r.choice(['#868a8a', '#b2b6b4']))
    return terminar(L)


def saco():
    """Saco de cemento de papel, acostado: base plana, arriba redondeado."""
    L = obj(46, 24)
    L.ell(0, 0, 45, 30, '#b8aa8a')
    L.rect(0, 12, 45, 23, '#b8aa8a')
    L.ell(3, 2, 42, 20, '#cfc2a2')
    L.rect(0, 20, 45, 23, '#9a8c6c')
    L.rect(12, 8, 33, 16, '#d6342c')                 # la etiqueta roja
    L.rect(14, 10, 31, 10, '#f6f1e4')
    L.rect(14, 13, 27, 13, '#f6f1e4')
    return terminar(L)


def cubeta():
    """Cubeta de pintura blanca con chorreado celeste (de lado)."""
    L = obj(30, 32)
    for y in range(4, 32):
        m = int((y - 4) / 28 * 3)
        bandas(L, 1 + m, y, 28 - m, y, '#eeeee8', 1.05, 0.8)
    L.rect(0, 2, 29, 5, '#d8d8d2')
    L.rect(0, 2, 29, 2, '#ffffff')
    for x in (6, 13, 21):                          # chorreado de pintura
        L.rect(x, 5, x + 2, 5 + (x % 7) + 4, '#7fc0e0')
    L.rect(8, 14, 21, 22, '#2f7fd8')               # etiqueta
    L.rect(10, 17, 19, 18, '#f6f1e4')
    L.line([(0, 3), (15, -2), (29, 3)], '#6f777c')  # asa
    return terminar(L)


def tapete():
    """Tapete de bienvenida (adorno plano en el piso)."""
    L = obj(56, 6)
    bandas(L, 0, 0, 55, 5, '#8a5a34', 1.15, 0.8)
    for x in range(3, 53, 4):
        L.px(x, 2, '#c8945a')
    L.rect(0, 0, 55, 0, '#a8763c')
    return terminar(L)


def tenis():
    """Un par de tenis tirados, de lado: suela blanca, capellada roja, puntera y cordones (adorno)."""
    L = obj(46, 14)
    for x0 in (0, 24):
        L.rect(x0, 11, x0 + 21, 13, '#f4f4ee')                      # suela
        L.rect(x0, 13, x0 + 21, 13, '#c9ccd2')
        L.poly([(x0 + 1, 11), (x0 + 1, 3), (x0 + 8, 2), (x0 + 12, 6), (x0 + 19, 7), (x0 + 21, 11)], '#e8423a')
        L.rect(x0 + 1, 3, x0 + 4, 10, '#c8302a')                    # talón
        L.poly([(x0 + 15, 7), (x0 + 19, 7), (x0 + 21, 11), (x0 + 15, 11)], '#f4f4ee')   # puntera
        for k in range(3):                                          # cordones
            L.px(x0 + 8 + k * 2, 4 + k, '#ffffff')
        L.rect(x0 + 5, 8, x0 + 13, 8, '#f4f4ee')                    # franja
    return terminar(L)


def macetita_sabila():
    """Maceta de barro con sábila (de lado, base plana)."""
    L = obj(34, 44)
    verde, verde_l = '#4f9a5a', '#7cc088'
    for k, (dx, h, lean) in enumerate(((10, 26, -8), (14, 30, -3), (18, 32, 2), (22, 28, 7), (26, 22, 10))):
        pts = [(dx - 2, 22), (dx + lean, 22 - h + 22 - 22 + 2), (dx + 2, 22)]
        L.poly([(dx - 2, 24), (dx + lean, 24 - h), (dx + 2, 24)], verde)
        L.line([(dx - 1, 23), (dx + lean, 24 - h)], verde_l)
    for y in range(24, 44):
        m = int((y - 24) / 20 * 4)
        bandas(L, 2 + m, y, 31 - m, y, '#c0643c')
    bandas(L, 0, 22, 33, 26, '#cf7448', 1.15, 0.75)
    return terminar(L)


def hormiga(paso=0):
    """Hormiga roja de lado: abdomen, cintura, tórax, cabeza con mandíbula, antena y 6 patas negras;
    dos cuadros (las patas se alternan) para caminar."""
    L = obj(30, 16)
    rojo, rojo_d, rojo_l, negro = '#c23a2c', '#8a2418', '#ec6a50', '#1a1210'
    L.ell(0, 2, 11, 11, rojo)                          # abdomen
    L.ell(2, 3, 7, 6, rojo_l)
    L.rect(11, 6, 12, 7, rojo_d)                       # cintura
    L.ell(12, 4, 18, 10, rojo)                         # tórax
    L.rect(19, 6, 19, 7, rojo_d)
    L.ell(19, 2, 27, 10, rojo)                         # cabeza
    L.px(21, 3, rojo_l); L.px(22, 3, rojo_l)
    L.px(24, 5, '#ffffff'); L.px(25, 5, negro)         # ojo
    L.rect(27, 7, 29, 8, rojo_d)                       # mandíbula
    L.line([(23, 2), (26, -1)], negro)                 # antena
    L.line([(26, -1), (29, 0)], negro)
    for i, x in enumerate((12, 15, 18)):               # patas: se alternan
        d = 1 if (i + paso) % 2 else -1
        L.line([(x, 9), (x + d * 2, 12), (x + d * 3, 15)], negro)
    return terminar(L)


def hormiga_aplastada():
    L = obj(26, 6)
    L.ell(0, 0, 25, 5, '#9a2a20')
    L.ell(4, 1, 21, 4, '#b8342a')
    return terminar(L)


# ================================================================ piezas de fondo
def bombillo():
    """Bombillo del corredor colgando del cielo raso, con su luz."""
    L = obj(20, 40)
    L.rect(9, 0, 10, 20, '#2a2420')
    L.rect(6, 20, 13, 25, '#8a8f96')
    L.circ(9.5, 31, 7, '#fff4b0')
    L.circ(8, 29, 3, '#ffffff')
    return terminar(L, doble=True)


def columna(alto):
    L = obj(22, alto)
    bandas(L, 0, 0, 21, alto - 1, '#f6f5f1', 1.04, 0.82)
    L.rect(0, alto - 10, 21, alto - 1, '#e2e0d8')
    return L


DIBUJADOS = {'bloque': bloque, 'saco': saco, 'cubeta': cubeta, 'tapete': tapete, 'tenis': tenis,
             'sabila': macetita_sabila, 'hormiga1': lambda: hormiga(0), 'hormiga2': lambda: hormiga(1),
             'hormiga_aplastada': hormiga_aplastada, 'bombillo': bombillo}


# ================================================================ escenarios
def pz(nombre, achicar=1):
    im = Image.open(os.path.join(PZ, nombre + '.png')).convert('RGBA')
    if achicar > 1:
        im = im.resize((im.width // achicar, im.height // achicar), Image.NEAREST)
    return im


def poner(L, nombre, x, base=None, y=None, achicar=1):
    im = pz(nombre, achicar) if isinstance(nombre, str) else nombre
    L.paste(im, x, y if y is not None else base - im.height)
    return im


def piedrilla(L, base='#b8ad98', seed=7):
    """Piso de piedrilla (gravilla de colores) con el borde de concreto del corredor arriba."""
    b = C(base)
    L.vgrad(0, SUELO, W - 1, H - 1, [shade(b, 1.08), b, shade(b, 0.72)])
    r = R(seed)
    for i in range(1400):
        x, y = r.randint(0, W - 1), r.randint(SUELO + 3, H - 1)
        c = r.choice(['#d8cfbc', '#8f8574', '#a89c86', '#c9b79a', '#77705f', '#e6dfd0'])
        L.rect(x, y, x + r.randint(0, 2), y + r.randint(0, 1), c)
    L.rect(0, SUELO, W - 1, SUELO + 2, '#cfcac0')      # borde del corredor
    L.rect(0, SUELO, W - 1, SUELO, '#ecebe6')


def concreto_rampa(L, seed=9):
    """Rampa de concreto del vecino: gris con juntas y manchas."""
    b = C('#a9aca8')
    L.vgrad(0, SUELO, W - 1, H - 1, [shade(b, 1.1), b, shade(b, 0.76)])
    r = R(seed)
    for x in range(0, W, 128):
        L.line([(x, SUELO + 2), (x - 20, H)], '#8a8d8a')
    for i in range(500):
        x, y = r.randint(0, W - 1), r.randint(SUELO + 3, H - 1)
        L.px(x, y, r.choice(['#b8bbb7', '#979a96', '#c2c4c0']))
    for i in range(8):                                  # manchas de agua / aceite
        x = r.randint(0, W - 60)
        y0 = SUELO + 8 + r.randint(0, 12)
        L.ell(x, y0, x + r.randint(30, 60), y0 + r.randint(4, 8), '#9b9e9a')
    L.rect(0, SUELO, W - 1, SUELO, '#cfd1cd')


def corredor():
    """El frente de la casa: fachada blanca con enchape de piedra, ventana con banquina, la puerta de madera
    y las columnas; arriba el cielo raso oscuro del alero con el bombillo; el piso es la piedrilla."""
    capas = []
    wall = Layer(W, H)
    wall.vgrad(0, 0, W - 1, SUELO, ['#ebe8e0', '#f1efe9', '#eeebe3'])
    # enchape de piedra en tiras (paneles de la fachada, de la mitad para abajo)
    r = R(21)
    for x0 in range(0, W, 192):
        for y in range(92, SUELO, 6):
            x = x0 + (r.randint(0, 20) if (y // 6) % 2 else 0)
            while x < x0 + 150:
                w = r.randint(14, 34)
                c = r.choice(['#9a9085', '#b4aa9c', '#877d72', '#c2b8a8', '#a69a8a'])
                wall.rect(x, y, min(x + w, x0 + 150), y + 4, c)
                wall.rect(x, y, min(x + w, x0 + 150), y, shade(C(c), 1.15))
                x += w + 1
        wall.rect(x0, 88, x0 + 150, 91, '#d9d4c8')        # banquina encima de la piedra
        wall.rect(x0, 88, x0 + 150, 88, '#f2efe8')
    # ventana grande con banquina (una sí, otra no) y la puerta de madera clara
    ventana(wall, 20, 10, 130, 84, seed=22)
    dx = 420
    wall.rect(dx - 6, 0, dx + 116, SUELO, '#8a5e3a')
    wall.rect(dx, 0, dx + 110, SUELO, '#c99459')
    for cx in (dx + 8, dx + 58):
        for (y0, y1) in ((6, 70), (84, 168)):
            bevel(wall, cx, y0, cx + 44, y1, '#bd8750', 0.8, 1.2)
            bevel(wall, cx + 4, y0 + 4, cx + 40, y1 - 4, '#cf9b60', 1.12, 0.82)
    sphere(wall, dx + 100, 96, 5, lambda *_: '#d9b04a')
    # columnas de la casa entre paneles
    for x in (170, 362, 554, 746):
        wall.im.alpha_composite(columna(SUELO).im, (x % W, 0))
    # cielo raso oscuro del alero y la cornisa terracota
    wall.rect(0, 0, W - 1, 7, '#4a4038')
    wall.rect(0, 8, W - 1, 11, '#c9785a')
    wall.rect(0, 11, W - 1, 11, '#a45f44')
    poner(wall, 'bombillo', 300, y=0)
    glow(wall, [(290, 70), (330, 70), (420, SUELO), (200, SUELO)], '#fff3c0', 40)
    wall.fog('#f0ede6', 0.1)
    capas.append(('pared', 0.08, wall))

    # --- plantas colgando del alero y la mecedora del corredor, más cerca
    mid = Layer(W, H)
    poner(mid, 'maceta_colgante', 90, y=-20)
    poner(mid, 'maceta_colgante', 560, y=-34)
    poner(mid, 'mecedora', 250, base=SUELO + 6, achicar=2)
    mid.fog('#ece8e0', 0.3)
    capas.append(('medio', 0.4, mid))

    near = Layer(W, H)
    poner(near, 'tenis', 150, base=SUELO + 3)
    capas.append(('cerca', 0.72, near))

    suelo = Layer(W, H)
    piedrilla(suelo)
    capas.append(('suelo', 1.0, suelo))

    fg = Layer(W, H)                                    # piedras grandes que pasan adelante
    r = R(23)
    for i in range(6):
        x = r.randint(0, W - 30)
        fg.ell(x, H - 10, x + r.randint(18, 30), H + 6, r.choice(['#8f8574', '#a89c86', '#77705f']))
    capas.append(('frente', 1.3, fg))
    return capas


def keylin_asomada():
    """La carita de Keylin (de su sprite) para asomarse por la ventana."""
    import json
    S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sprites')
    m = json.load(open(os.path.join(S, 'sprites.json'), encoding='utf-8'))['keylin']
    im = Image.open(os.path.join(S, 'keylin.png')).convert('RGBA')
    f = m['anims']['pose']['frames'][0]
    cuadro = im.crop((f * m['w'], 0, (f + 1) * m['w'], m['h']))
    return cuadro.crop((0, 0, m['w'], 24)).resize((m['w'] * 2, 48), Image.NEAREST)


def casa_keylin():
    """El frente de la casa amarilla del vecino: la rampa de concreto, el muro de bloques y la casa con su
    techo rojo, fascias vino y cortinas; Keylin se asoma por una ventana, chismeando."""
    capas = []
    sky = Layer(W, H)
    sky.vgrad(0, 0, W - 1, 150, ['#5aa6e0', '#8fcaef', '#cfe9f4', '#f2f0da'])
    sky.rect(0, 151, W - 1, H - 1, '#f2f0da')
    r = R(31)
    for i in range(6):
        x, y = i * 130 + r.randint(0, 40), r.randint(16, 60)
        for k in range(3):
            clump(sky, x + k * 16 - 16, y + r.randint(-4, 4), r.randint(10, 15), ['#a9c9e6', '#e3f0fa', '#ffffff'], seed=i * 5 + k, flat=0.45)
    capas.append(('cielo', 0.0, sky))

    # --- la casa amarilla, cerca: pared crema-amarilla, ventanas con cortinas, fascia vino, techo rojo
    casa = Layer(W, H)
    casa.rect(0, 40, W - 1, SUELO, '#e9d178')
    casa.vgrad(0, 40, W - 1, SUELO, ['#efd98a', '#e9d178', '#dcc36a'])
    for x in range(0, W, 96):                           # columnas del mismo sistema prefabricado
        casa.rect(x, 40, x + 7, SUELO, '#dcc36a')
        casa.rect(x, 40, x + 1, SUELO, '#f3e2a0')
    casa.poly([(-20, 42), (W + 20, 42), (W + 20, 14), (-20, 14)], '#b8452f')      # techo rojo (de canto)
    for x in range(0, W, 8):
        casa.rect(x, 14, x + 3, 30, '#c9563c')
    casa.rect(0, 30, W - 1, 41, '#8e2c32')              # fascia vino
    casa.rect(0, 30, W - 1, 31, '#b24650')
    for wx in (130, 520):
        casa.rect(wx - 5, 48, wx + 125, 112, '#f4f0e6')  # marco
        casa.rect(wx, 53, wx + 120, 107, '#6b8aa4')
        casa.rect(wx, 53, wx + 120, 64, '#8faac0')
        casa.rect(wx - 8, 112, wx + 128, 116, '#d9d4c8')  # repisa
    # Keylin asomada en la ventana izquierda, detrás de la cortina
    kx = 170
    poner(casa, keylin_asomada(), kx, y=107 - 48 + 2)
    for (a, b, tone) in ((130, 190, 0), (208, 250, 1)):
        for x in range(a, b):
            k = (x - a) % 10
            c = '#f1eadc' if k < 6 else ('#dcd2c0' if k < 8 else '#fbf7ee')
            casa.rect(x, 53, x, 107, c)
    for x in range(520, 640):
        k = (x - 520) % 10
        casa.rect(x, 53, x, 107, '#f1eadc' if k < 6 else '#dcd2c0')
    casa.rect(330, 60, 440, SUELO, '#8e2c32')           # puerta vino
    casa.rect(336, 66, 434, SUELO, '#a8404a')
    sphere(casa, 424, 124, 4, lambda *_: '#e6c26a')
    casa.fog('#f4ecd0', 0.12)
    capas.append(('pared', 0.1, casa))

    # --- el muro de bloques de la rampa, más cerca (8 hiladas en la calle; aquí se ve un tramo)
    muro = Layer(W, H)
    muro.rect(0, 118, W - 1, SUELO + 4, '#c8c2b0')                 # mezcla entre los bloques
    for y in range(120, SUELO + 2, 12):
        off = 0 if (y // 12) % 2 else 20
        for x in range(-off, W, 40):
            bevel(muro, x, y, x + 38, y + 10, '#9ea2a2', 1.12, 0.8)
    muro.rect(0, 116, W - 1, 120, '#b8bcba')             # corona del muro
    r = R(33)
    for i in range(14):                                   # monte que asoma sobre el muro
        x = r.randint(0, W)
        blade(muro, x, 118, r.randint(16, 40), r.randint(-10, 10), 6, r.choice(['#3f7a3a', '#4c8a41', '#5a9a48']))
    muro.fog('#e8eee6', 0.2)
    capas.append(('medio', 0.45, muro))

    near = Layer(W, H)
    r = R(34)
    for i in range(10):                                   # zacatito en las orillas de la rampa
        x = r.randint(0, W)
        blade(near, x, SUELO + 3, r.randint(10, 22), r.randint(-6, 6), 5, r.choice(['#4c8a41', '#5a9a48']))
    capas.append(('cerca', 0.72, near))

    suelo = Layer(W, H)
    concreto_rampa(suelo)
    capas.append(('suelo', 1.0, suelo))
    return capas
