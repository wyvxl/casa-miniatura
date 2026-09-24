"""Objetos dibujados de lado y con la base plana, a partir de la idea de las hojas de la dueña.

Las hojas traían macetas, taza, especias, cubos, carrito, legos y libros vistos desde arriba en diagonal:
en un juego de lado, su base ovalada (o las piezas de atrás) se veían despegadas del piso. Aquí se
redibujan de lado, con luz a la izquierda, sombra a la derecha y contorno (lo pone objetos.py).
"""
from pinta import Layer, bevel, C
from pixel import shade


def obj(w, h):
    return Layer(w, h, wrap=False)


def bandas(L, x0, y0, x1, y1, base, luz=1.2, sombra=0.72):
    """Relleno con luz a la izquierda y sombra a la derecha, tramado en los cambios."""
    b = C(base)
    w = max(1, x1 - x0)
    for x in range(x0, x1 + 1):
        t = (x - x0) / w
        for y in range(y0, y1 + 1):
            d = ((x * 7 + y * 3) % 4) / 4 * 0.12
            c = shade(b, luz) if t + d < 0.2 else (shade(b, sombra) if t - d > 0.8 else b)
            L.px(x, y, c)


def maceta_barro(w, h):
    L = obj(w, h)
    for y in range(6, h):
        t = (y - 6) / max(1, h - 7)
        m = int(2 + t * 4)
        bandas(L, m, y, w - 1 - m, y, '#c0643c')
    bandas(L, 0, 1, w - 1, 6, '#cf7448', 1.15, 0.75)
    L.rect(0, 1, w - 1, 1, '#e08a5c')
    L.rect(3, 0, w - 4, 0, '#4a2a18')            # la tierra que se asoma
    L.rect(2, 7, w - 3, 7, '#8a4428')            # sombra bajo el borde
    for (x, y) in ((7, 12), (w - 10, h - 6), (w // 2, 16)):
        if y < h - 1:
            L.px(x, y, '#a85432')
    return L, 0


def taza():
    L = obj(40, 26)
    por, sh, az = '#f4f1ea', '#d6d0c4', '#5a7fc0'
    for y in range(4, 22):                       # la taza, redonda abajo
        t = (y - 4) / 17
        m = int(round(max(0, t - 0.55) ** 1.4 * 20))
        bandas(L, 7 + m, y, 30 - m, y, por, 1.03, 0.86)
    L.rect(7, 4, 30, 4, '#ffffff')
    L.rect(8, 5, 29, 5, '#8a5a2e')               # el té
    for x in range(10, 28, 5):                   # florecitas azules
        L.px(x, 11, az); L.px(x + 1, 12, az); L.px(x, 13, az); L.px(x - 1, 12, az)
    L.rect(9, 16, 28, 16, az)
    for y in range(8, 17):                       # oreja
        L.px(31, y, por)
        L.px(34 if 9 < y < 15 else 33, y, por)
    L.rect(31, 8, 33, 8, por)
    L.rect(31, 16, 33, 16, por)
    L.rect(0, 22, 39, 22, '#ffffff')             # plato
    L.rect(1, 23, 38, 23, sh)
    L.rect(10, 24, 29, 25, sh)                   # pie del plato
    return L, 4


def frasco(contenido):
    L = obj(18, 30)
    L.rect(1, 6, 16, 29, '#dfe8ea')             # vidrio
    bandas(L, 2, 12, 15, 28, contenido, 1.15, 0.75)
    L.rect(2, 6, 15, 11, '#eef4f5')
    L.rect(3, 7, 3, 27, '#ffffff')               # brillo del vidrio
    L.rect(1, 15, 16, 22, '#f6f1e4')             # etiqueta
    L.rect(4, 17, 13, 17, contenido)
    L.rect(4, 19, 11, 19, '#9a8f86')
    bandas(L, 2, 0, 15, 5, '#9aa2a8', 1.3, 0.7)  # tapa
    for x in range(3, 15, 2):
        L.px(x, 2, '#6f777c')
    return L, 0


def especiero():
    L = obj(50, 52)
    madera = '#9a6a3e'
    L.rect(5, 5, 44, 23, '#4a3020')
    L.rect(5, 29, 44, 46, '#4a3020')
    cols = ['#c8462c', '#9a6b36', '#e0b23a', '#5a8a3a']
    for fila, ybase in enumerate((23, 46)):
        for k in range(4):
            x = 7 + k * 10
            L.rect(x, ybase - 14, x + 7, ybase, '#dfe8ea')
            L.rect(x + 1, ybase - 9, x + 6, ybase, cols[(k + fila) % 4])
            L.rect(x, ybase - 17, x + 7, ybase - 15, '#9aa2a8')
            L.px(x + 1, ybase - 13, '#ffffff')
    for x0 in (0, 45):
        bevel(L, x0, 4, x0 + 4, 51, madera, 1.2, 0.75)
    for y0 in (24, 47):
        bevel(L, 4, y0, 45, y0 + 4, madera, 1.2, 0.75)
    bevel(L, 0, 0, 49, 4, '#b07a48', 1.2, 0.75)          # tabla de arriba (se puede parar)
    L.rect(4, 14, 45, 15, '#b07a48')                     # baranditas de adelante
    L.rect(4, 37, 45, 38, '#b07a48')
    return L, 0


def letra(L, ch, x, y, c):
    F = {'A': ["010", "101", "111", "101", "101"], 'B': ["110", "101", "110", "101", "110"],
         'C': ["011", "100", "100", "100", "011"], 'L': ["100", "100", "100", "100", "111"]}
    for j, row in enumerate(F[ch]):
        for i, v in enumerate(row):
            if v == '1':
                L.rect(x + i * 3, y + j * 2, x + i * 3 + 2, y + j * 2 + 1, c)


def cubo_letra(ch, color):
    L = obj(26, 26)
    bevel(L, 0, 0, 25, 25, color, 1.25, 0.72)
    L.rect(4, 4, 21, 21, '#fbf5e4')
    L.rect(4, 4, 21, 4, '#ffffff')
    letra(L, ch, 8, 8, color)
    return L, 0


def carrito():
    L = obj(76, 34)
    L.poly([(18, 14), (26, 4), (52, 4), (62, 14)], '#b82a24')            # cabina
    L.poly([(22, 14), (28, 7), (38, 7), (38, 14)], '#bfe3f4')            # ventanas
    L.poly([(41, 14), (41, 7), (50, 7), (57, 14)], '#bfe3f4')
    L.rect(27, 7, 29, 8, '#ffffff')
    bandas(L, 2, 14, 73, 25, '#d6342c', 1.2, 0.75)                       # carrocería
    L.rect(2, 14, 73, 14, '#f06a5c')
    L.rect(4, 19, 71, 19, '#a82620')
    L.rect(70, 16, 73, 18, '#f7d24a')                                    # foco
    L.rect(2, 16, 4, 18, '#f0a0a0')
    L.rect(0, 22, 6, 25, '#b9c0c4')                                      # bumpers
    L.rect(69, 22, 75, 25, '#b9c0c4')
    for cx in (17, 58):                                                  # llantas: tocan el piso
        L.ell(cx - 8, 18, cx + 8, 33, '#232527')
        L.ell(cx - 4, 22, cx + 4, 29, '#9aa2a8')
        L.px(cx - 2, 23, '#ffffff')
    return L, 4


def lego_color(color, n=4):
    w = n * 10 + 2
    L = obj(w, 20)
    bevel(L, 0, 4, w - 1, 19, color, 1.25, 0.72)
    for s in range(n):
        x = 3 + s * 10
        bevel(L, x, 0, x + 5, 4, shade(C(color), 1.08), 1.3, 0.8)
    L.rect(1, 18, w - 2, 18, shade(C(color), 0.6))
    return L, 1


def libro_parado(color, oro='#d9b04a'):
    L = obj(16, 44)
    bandas(L, 0, 0, 15, 43, color, 1.25, 0.72)
    L.rect(0, 0, 15, 1, shade(C(color), 1.3))
    for y in (5, 38):
        L.rect(1, y, 14, y + 1, oro)
    L.rect(4, 14, 11, 28, shade(C(color), 0.8))
    for y in (16, 19, 22):
        L.rect(5, y, 10, y, oro)
    return L, 0


def tabla_picar():
    L = obj(80, 9)
    bandas(L, 12, 1, 79, 8, '#d9a868', 1.12, 0.85)
    bandas(L, 0, 2, 13, 7, '#d9a868', 1.12, 0.85)
    L.ell(3, 3, 7, 6, (0, 0, 0, 0))                       # agujerito para colgarla
    L.rect(12, 1, 79, 1, '#f0c890')
    for x in range(18, 78, 9):
        L.rect(x, 4, x + 5, 4, '#b8864c')
    return L, 0


def cactus_espinas():
    """Cactus que quita vida: tiene que verse peligroso (espinas largas y claras saliendo por todo el borde)."""
    L = obj(62, 72)
    verde, claro, oscuro = '#3f8a3a', '#6cc05a', '#23562a'
    for y in range(56, 72):                              # maceta de barro
        m = int((y - 56) / 16 * 3)
        bandas(L, 13 + m, y, 48 - m, y, '#c0643c')
    bandas(L, 11, 53, 50, 57, '#cf7448', 1.15, 0.75)
    # tronco y brazos, redondeados y con costillas
    L.ell(23, 4, 38, 18, verde); L.rect(23, 11, 38, 53, verde)
    L.ell(9, 18, 18, 27, verde); L.rect(9, 23, 18, 42, verde); L.rect(9, 36, 24, 42, verde)
    L.ell(43, 10, 52, 19, verde); L.rect(43, 15, 52, 34, verde); L.rect(37, 28, 52, 34, verde)
    for x in (27, 31, 35):
        L.rect(x, 9, x, 52, oscuro)
    L.rect(13, 22, 13, 40, oscuro); L.rect(47, 14, 47, 32, oscuro)
    L.rect(24, 10, 24, 52, claro); L.rect(10, 23, 10, 41, claro); L.rect(44, 15, 44, 33, claro)
    # espinas hacia afuera: (x, y, dx, dy)
    esp = [(23, 14, -6, -2), (23, 47, -6, 1), (23, 52, -6, 2), (38, 40, 6, 0), (38, 46, 6, 1), (38, 51, 6, 2),
           (26, 6, -3, -5), (30, 4, 0, -6), (35, 6, 3, -5),
           (9, 26, -6, -1), (9, 32, -6, 0), (9, 38, -6, 1), (11, 19, -3, -5), (16, 19, 3, -5), (13, 42, -3, 5),
           (52, 16, 6, -1), (52, 22, 6, 0), (52, 28, 6, 1), (45, 11, -3, -5), (50, 11, 3, -5), (47, 34, 3, 5)]
    for (x, y, dx, dy) in esp:
        L.line([(x, y), (x + dx * 0.6, y + dy * 0.6)], '#f7e27a', 2)
        L.line([(x, y), (x + dx, y + dy)], '#fff3b0')
        L.px(x + dx, y + dy, '#ffffff')
    for (x, y) in ((26, 20), (33, 27), (28, 36), (34, 45), (12, 30), (46, 21)):   # espinitas en la cara
        L.line([(x, y), (x + 2, y - 2)], '#fff3b0')
        L.px(x + 2, y - 2, '#ffffff')
    for (dx, dy) in ((0, -2), (-2, 0), (2, 0), (0, 2)):  # flor roja arriba
        L.circ(30 + dx, 3 + dy, 2, '#e8342c')
    L.circ(30, 3, 1, '#f5c531')
    return L, 0


def _capa(im):
    """Una imagen ya terminada (con contorno) como capa, para la hoja de objetos."""
    L = obj(im.width - 2, im.height - 2)
    L.im.alpha_composite(im.crop((1, 1, im.width - 1, im.height - 1)))
    return L


LADO = [
    ('cactus_alto', cactus_espinas), ('trampa', lambda: (_capa(__import__('muebles').trampa_raton()), 0)), ('cactus', lambda: __import__('muebles').cactus_bajito_layer()),
    ('maceta_b', lambda: maceta_barro(34, 30)), ('maceta_c', lambda: maceta_barro(26, 22)),
    ('taza', taza), ('frasco_rojo', lambda: frasco('#c8462c')), ('frasco_cafe', lambda: frasco('#9a6b36')),
    ('especiero', especiero), ('cubo_a', lambda: cubo_letra('A', '#d6342c')), ('cubo_b', lambda: cubo_letra('B', '#2f6fc8')),
    ('cubo_c', lambda: cubo_letra('C', '#3a9a4a')), ('cubo_l', lambda: cubo_letra('L', '#e0a02e')), ('carrito', carrito),
    ('lego_rojo', lambda: lego_color('#d6342c')), ('lego_azul', lambda: lego_color('#2f6fc8')),
    ('lego_amarillo', lambda: lego_color('#f0c030')), ('lego_verde', lambda: lego_color('#3a9a4a', 3)),
    ('libro_verde', lambda: libro_parado('#3f6a44')), ('libro_rojo', lambda: libro_parado('#9a3a32')),
    ('tabla', tabla_picar),
]
