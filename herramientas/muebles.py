"""Muebles redibujados de frente o de lado (el juego se ve de lado).

En las hojas de la dueña venían vistos desde arriba en diagonal: al lado de los personajes, que se ven de lado,
no calzaba el ángulo. Se usan las hojas solo como idea (colores, forma, detalles ticos).
Los de fondo se dibujan a la mitad y se agrandan al doble, como los demás muebles grandes (pixel más grueso).
"""
from PIL import Image
from pinta import Layer, bevel, C
from pixel import shade
from objetos_lado import bandas

CONTORNO = (34, 22, 26, 255)
MADERA, MAD_L, MAD_D = '#a0643a', '#c0844e', '#6e4024'


def obj(w, h):
    return Layer(w, h, wrap=False)


def terminar(L, doble=False):
    M = Layer(L.w + 2, L.h + 2, wrap=False)          # 1 px de margen para que quepa el contorno
    M.im.alpha_composite(L.im, (1, 1))
    M.outline(CONTORNO)
    im = M.im
    if doble:
        im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    return im


def veta(L, x0, y0, x1, y1, color, paso=7):
    for y in range(y0 + 3, y1, paso):
        L.rect(x0 + 2, y, x1 - 2, y, shade(C(color), 0.86))


# ---------------------------------------------------------------- se juegan (tamaño natural)
def comoda():
    L = obj(72, 62)
    bevel(L, 0, 0, 71, 5, MAD_L, 1.2, 0.72)                 # tabla de arriba, se para encima
    bandas(L, 3, 6, 68, 55, MADERA, 1.15, 0.78)
    for y0 in (9, 32):                                     # dos gavetas
        bevel(L, 7, y0, 64, y0 + 19, MAD_L, 1.15, 0.8)
        veta(L, 7, y0, 64, y0 + 19, MAD_L, 6)
        for kx in (22, 49):
            L.circ(kx, y0 + 9, 2, '#e6c26a')
            L.px(kx - 1, y0 + 8, '#fff2b0')
    L.rect(5, 56, 10, 61, MAD_D)                           # patas
    L.rect(61, 56, 66, 61, MAD_D)
    return terminar(L)


def baul():
    L = obj(76, 60)
    L.ell(0, 0, 75, 26, MADERA)                            # tapa redonda
    L.rect(0, 13, 75, 22, MADERA)
    L.ell(3, 2, 72, 22, MAD_L)
    L.rect(0, 22, 75, 25, MAD_D)
    bandas(L, 1, 26, 74, 59, MADERA, 1.15, 0.75)
    veta(L, 1, 26, 74, 59, MADERA, 7)
    for x in (10, 63):                                     # herrajes
        L.rect(x, 3, x + 3, 59, '#8a7a5a')
        L.rect(x, 3, x, 59, '#c8b890')
    bevel(L, 32, 20, 43, 33, '#e0b84a', 1.3, 0.7)          # candado
    L.rect(37, 26, 38, 29, '#5a4020')
    return terminar(L)


def mesa():
    """Mesita redonda de lado, con su mantelito de encaje."""
    L = obj(112, 84)
    bevel(L, 0, 0, 111, 7, MAD_L, 1.2, 0.72)               # sobre de la mesa
    L.rect(14, 1, 97, 2, '#f7f1e2')                        # mantelito encima
    for x in range(14, 98):                                # que cae con piquitos
        L.rect(x, 3, x, 10 + (2 if (x // 4) % 2 else 0), '#f7f1e2')
    for x in range(18, 96, 12):
        L.px(x, 7, '#e8849a')
        L.px(x + 1, 8, '#6aa060')
    bandas(L, 49, 8, 62, 70, MADERA, 1.2, 0.72)            # pata del centro, torneada
    for y in (20, 44, 62):
        L.rect(46, y, 65, y + 3, MAD_L)
    L.poly([(22, 83), (50, 70), (61, 70), (89, 83)], MAD_D) # pie
    L.poly([(30, 83), (50, 72), (55, 72), (40, 83)], MADERA)
    return terminar(L)


def taburete():
    L = obj(52, 48)
    bevel(L, 0, 0, 51, 7, '#b8864c', 1.2, 0.72)            # asiento de madera
    for x in range(3, 50, 5):
        L.rect(x, 2, x + 2, 5, '#a8763c')
    for x0 in (5, 40):                                     # patas un poco abiertas
        L.poly([(x0, 8), (x0 + 6, 8), (x0 + 6 + (-3 if x0 < 20 else 3), 47), (x0 + (-3 if x0 < 20 else 3), 47)], MADERA)
    L.rect(6, 30, 45, 33, MAD_D)                           # travesaño
    return terminar(L)


def cojin():
    """Cojín tejido de colores (rebota)."""
    L = obj(74, 28)
    L.ell(0, 0, 73, 27, '#e8423a')
    cols = ['#e8423a', '#f5c531', '#2f7fd8', '#3fb36a', '#f06d8f']
    for i, x in enumerate(range(4, 72, 7)):
        for y in range(0, 28):
            if L.im.getpixel((x, y))[3]:
                L.rect(x, y, x + 3, y, cols[i % 5])
    for y in range(1, 27):                                 # sombra de abajo y luz de arriba
        for x in range(74):
            c = L.im.getpixel((x, y))
            if c[3] and y > 18:
                L.px(x, y, shade(c, 0.78))
            elif c[3] and y < 5:
                L.px(x, y, shade(c, 1.2))
    for x in (1, 72):                                      # borlas
        L.rect(x - 1, 11, x + 1, 17, '#f5c531')
    return terminar(L)


def cactus_bajito_layer():
    return _cactus()[0], 0


def cactus_bajito():
    return terminar(_cactus()[0])


def _cactus():
    """El cactus que quita vida, bajito para poder saltarlo (unos 36 px)."""
    L = obj(40, 38)
    verde, claro, oscuro = '#3f8a3a', '#6cc05a', '#23562a'
    for y in range(29, 38):
        m = int((y - 29) / 9 * 2)
        bandas(L, 9 + m, y, 30 - m, y, '#c0643c')
    bandas(L, 7, 27, 32, 30, '#cf7448', 1.15, 0.75)
    L.ell(15, 4, 25, 12, verde); L.rect(15, 8, 25, 27, verde)
    L.ell(8, 11, 14, 16, verde); L.rect(8, 14, 14, 22, verde); L.rect(8, 19, 16, 23, verde)
    L.ell(26, 8, 32, 13, verde); L.rect(26, 11, 32, 19, verde); L.rect(24, 16, 32, 20, verde)
    L.rect(18, 7, 18, 26, oscuro); L.rect(22, 7, 22, 26, oscuro)
    L.rect(16, 8, 16, 26, claro); L.rect(9, 14, 9, 22, claro); L.rect(27, 11, 27, 19, claro)
    esp = [(15, 10, -4, -1), (15, 24, -4, 1), (25, 22, 4, 0), (25, 26, 4, 1), (17, 5, -2, -4), (20, 4, 0, -4), (23, 5, 2, -4),
           (8, 14, -4, -1), (8, 19, -4, 1), (10, 11, -2, -3), (32, 11, 4, -1), (32, 16, 4, 1), (29, 8, 2, -3)]
    for (x, y, dx, dy) in esp:
        L.line([(x, y), (x + dx, y + dy)], '#fff3b0')
        L.px(x + dx, y + dy, '#ffffff')
    for (dx, dy) in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        L.circ(20 + dx, 2 + dy, 1, '#e8342c')
    L.px(20, 2, '#f5c531')
    return L, 0


# ---------------------------------------------------------------- de fondo (a la mitad, luego al doble)
def refri():
    L = obj(62, 128)
    crema = '#ece2cc'
    bandas(L, 0, 0, 61, 121, crema, 1.06, 0.8)
    L.rect(0, 0, 61, 1, '#fbf6ea')
    L.rect(1, 40, 60, 41, '#b8ac94')                       # congelador arriba
    for (y0, y1) in ((8, 30), (50, 92)):                   # agarraderas
        L.rect(52, y0, 54, y1, '#9aa2a8')
        L.rect(52, y0, 52, y1, '#d8dde0')
    for (x, y, c) in ((12, 20, '#e8423a'), (30, 60, '#2f7fd8'), (16, 76, '#f5c531'), (38, 24, '#3fb36a')):
        L.rect(x, y, x + 4, y + 3, c)                       # imanes
    L.rect(20, 50, 38, 70, '#fbfbf7')                      # dibujo de los chiquitos
    L.rect(24, 58, 32, 66, '#e8423a')
    L.poly([(22, 58), (28, 53), (34, 58)], '#2f7fd8')
    L.rect(2, 122, 59, 127, '#3a3836')
    return terminar(L, doble=True)


def cocina_gas():
    L = obj(62, 66)
    acero = '#9aa4ae'
    L.rect(2, 0, 59, 3, '#2a2c30')                         # parrilla de arriba, de canto
    for x in (8, 22, 38, 52):
        L.rect(x - 3, 0, x + 3, 1, '#4a4c52')
    bandas(L, 0, 4, 61, 60, acero, 1.15, 0.78)
    L.rect(0, 4, 61, 13, '#b8c0c8')                        # tablero con perillas
    for x in (9, 22, 39, 52):
        L.circ(x, 8, 2, '#2a2c30')
        L.px(x, 7, '#d8dde0')
    bevel(L, 6, 18, 55, 55, '#8a949e', 1.15, 0.78)         # puerta del horno
    L.rect(12, 26, 49, 44, '#2a2c30')
    L.rect(13, 27, 48, 29, '#5a5c62')
    L.rect(10, 20, 51, 22, '#d8dde0')                      # agarradera
    L.rect(3, 61, 8, 65, '#2a2c30'); L.rect(53, 61, 58, 65, '#2a2c30')
    return terminar(L, doble=True)


def chorreador():
    """Chorreador de café de lado: base de madera, palo, aro con la bolsita de tela y el jarro abajo."""
    L = obj(52, 64)
    bevel(L, 0, 56, 51, 63, MAD_L, 1.2, 0.72)              # base
    bandas(L, 4, 4, 9, 56, MADERA, 1.2, 0.75)              # palo
    L.rect(4, 8, 36, 11, MAD_D)                            # brazo
    L.rect(22, 11, 38, 13, '#4a4c52')                      # aro
    L.poly([(22, 13), (38, 13), (32, 34), (28, 34)], '#e8dcc0')   # bolsita de tela
    L.poly([(22, 13), (26, 13), (29, 34), (28, 34)], '#f7efdc')
    L.rect(29, 34, 31, 40, '#5a3418')                      # el chorrito de café
    bandas(L, 18, 40, 42, 55, '#b8603a', 1.15, 0.75)       # jarro de barro
    L.rect(18, 40, 42, 41, '#d88a5c')
    L.rect(43, 44, 45, 51, '#b8603a')
    return terminar(L, doble=True)


def cama():
    L = obj(134, 72)
    for x0 in (0, 124):                                    # postes
        top = 0 if x0 == 0 else 22
        bevel(L, x0, top, x0 + 9, 71, MADERA, 1.2, 0.72)
    for x in range(12, 124, 1):                            # colchón
        L.rect(x, 26, x, 34, '#f4f1ea')
    bandas(L, 10, 18, 42, 30, '#ffffff', 1.0, 0.85)        # almohada
    L.ell(10, 16, 44, 32, '#f7f5ee')
    cols = ['#e8423a', '#f5a524', '#2f7fd8', '#3fb36a', '#8b3a9a', '#e8423a', '#2fb0c0']
    for i, y in enumerate(range(30, 60, 4)):               # cobija tica de rayas, colgando
        L.rect(38, y, 123, y + 3, cols[i % len(cols)])
    L.poly([(38, 22), (123, 22), (123, 30), (38, 30)], '#e8423a')
    for x in range(40, 123, 3):                            # flequillo
        L.rect(x, 60, x, 63, '#f5c531')
    L.rect(10, 4, 11, 30, MAD_D)                           # cabecera de barrotes
    for x in range(12, 40, 6):
        L.rect(x, 6, x + 2, 26, MAD_L)
    L.rect(9, 2, 38, 6, MADERA)
    L.rect(12, 64, 123, 71, '#2a2420')                     # oscuro debajo
    return terminar(L, doble=True)


def inodoro():
    """Inodoro de lado: tanque atrás, taza redonda adelante."""
    L = obj(64, 80)
    bl = '#f4f5f2'
    bandas(L, 2, 0, 24, 40, bl, 1.05, 0.82)                # tanque
    L.rect(0, 0, 26, 4, '#ffffff')
    L.rect(18, 8, 22, 10, '#b9c0c4')                       # palanca
    L.ell(4, 34, 63, 52, bl)                               # taza
    L.rect(2, 38, 30, 52, bl)
    L.rect(4, 34, 58, 36, '#dfe3e2')                       # tapa
    L.poly([(16, 52), (48, 52), (44, 79), (20, 79)], bl)   # pie
    L.poly([(40, 52), (48, 52), (44, 79), (38, 79)], '#d0d5d4')
    L.rect(14, 76, 50, 79, '#e3e7e6')
    return terminar(L, doble=True)


def lavamanos():
    L = obj(72, 86)
    bl = '#f4f5f2'
    L.rect(33, 0, 38, 10, '#b9c0c4')                       # llave
    L.rect(33, 0, 44, 3, '#b9c0c4')
    L.circ(26, 8, 2, '#e8423a'); L.circ(46, 8, 2, '#2f7fd8')
    bandas(L, 0, 11, 71, 26, bl, 1.05, 0.82)               # pila
    L.rect(0, 11, 71, 12, '#ffffff')
    L.poly([(6, 26), (66, 26), (54, 34), (18, 34)], '#e3e7e6')
    bandas(L, 28, 34, 43, 80, bl, 1.08, 0.8)               # pedestal
    L.rect(22, 80, 49, 85, '#e3e7e6')
    return terminar(L, doble=True)


def tv_mueble():
    """Tele de las de antes, de frente, sobre su mueble de madera."""
    L = obj(92, 80)
    L.line([(36, 0), (44, 12)], '#3a3836'); L.line([(56, 0), (48, 12)], '#3a3836')   # antena de conejo
    bevel(L, 18, 12, 73, 50, '#4a4c52', 1.2, 0.72)                                    # la tele
    L.rect(22, 16, 60, 46, '#1a2a3a')
    L.rect(24, 18, 58, 44, '#5aa0d8')
    L.rect(24, 36, 58, 44, '#6cc05a')                                                  # la novela: un paisaje
    L.circ(50, 24, 3, '#f5c531')
    L.rect(24, 18, 26, 30, '#bfe3f4')
    for y in (22, 30):
        L.circ(67, y, 2, '#9aa2a8')
    L.rect(63, 38, 70, 45, '#3a3c42')
    bevel(L, 0, 50, 91, 55, MAD_L, 1.2, 0.72)                                         # mueble
    bandas(L, 2, 56, 89, 75, MADERA, 1.15, 0.78)
    for x0 in (6, 48):
        bevel(L, x0, 58, x0 + 37, 73, MAD_L, 1.15, 0.8)
        L.rect(x0 + 17, 64, x0 + 20, 66, '#e6c26a')
    L.rect(4, 76, 9, 79, MAD_D); L.rect(82, 76, 87, 79, MAD_D)
    return terminar(L, doble=True)


# ---------------------------------------------------------------- patio, de lado
def tronco(L, x0, y0, largo, alto, seed):
    """Un tronco acostado visto de lado: corteza y, a la izquierda, el corte con sus anillos."""
    corteza, corteza_l, corteza_d = '#6e4a2c', '#8a6038', '#4a3020'
    L.rect(x0 + alto // 2, y0, x0 + largo, y0 + alto - 1, corteza)
    L.rect(x0 + alto // 2, y0, x0 + largo, y0 + 1, corteza_l)
    L.rect(x0 + alto // 2, y0 + alto - 2, x0 + largo, y0 + alto - 1, corteza_d)
    for k in range(4):                                   # grietas de la corteza
        yy = y0 + 3 + (k * 5 + seed) % max(1, alto - 5)
        xx = x0 + alto // 2 + 4 + (k * 13 + seed * 7) % max(1, largo - alto // 2 - 10)
        L.rect(xx, yy, xx + 6, yy, corteza_d)
    L.ell(x0, y0, x0 + alto - 1, y0 + alto - 1, '#d9b07a')   # el corte
    L.ell(x0 + 2, y0 + 2, x0 + alto - 3, y0 + alto - 3, '#c89860')
    L.ell(x0 + 5, y0 + 5, x0 + alto - 6, y0 + alto - 6, '#d9b07a')
    L.px(x0 + alto // 2, y0 + alto // 2, '#8a6038')


def lena():
    """Pila de leña de lado: troncos acostados, la base plana en el piso."""
    L = obj(74, 42)
    tronco(L, 0, 28, 70, 14, 1)
    tronco(L, 6, 14, 62, 14, 3)
    tronco(L, 3, 0, 60, 14, 5)
    return terminar(L)


def parrilla():
    """Parrilla de carbón de lado: la olla redonda, la rejilla arriba y tres patas."""
    L = obj(60, 64)
    negro, negro_l = '#2e2e32', '#4a4a50'
    L.ell(4, -2, 55, 34, negro)                            # olla: la mitad de abajo de un óvalo
    for y in range(0, 16):
        for x in range(60):
            L.px(x, y, (0, 0, 0, 0))
    L.rect(8, 21, 12, 27, negro_l)                        # brillo
    L.rect(2, 15, 57, 17, '#8a8f96')                      # rejilla (de canto)
    for x in range(4, 57, 4):
        L.px(x, 14, '#b9c0c4')
    L.px(46, 26, '#e0602a'); L.px(47, 25, '#f5a524')      # brasita
    for (x0, x1) in ((14, 6), (29, 29), (44, 52)):        # patas
        L.line([(x0, 33), (x1, 63)], '#3a3a40', 2)
    L.rect(10, 50, 48, 51, '#3a3a40')                     # aro de abajo
    return terminar(L)


def silla_patio():
    """Silla de madera pintada de azul, de lado."""
    L = obj(40, 70)
    azul, azul_l, azul_d = '#2f7fd8', '#5aa0f0', '#1f5aa0'
    L.rect(2, 0, 7, 69, azul)                             # pata de atrás que sube al respaldo
    L.rect(2, 0, 3, 69, azul_l)
    for y in (6, 15, 24):                                 # travesaños del respaldo (de canto)
        L.rect(0, y, 9, y + 3, azul_d)
    L.rect(2, 36, 39, 41, azul)                           # asiento
    L.rect(2, 36, 39, 37, azul_l)
    L.rect(32, 41, 37, 69, azul)                          # pata de adelante
    L.rect(32, 41, 33, 69, azul_l)
    L.rect(7, 56, 32, 58, azul_d)                         # travesaño de abajo
    return terminar(L)


def bananos_caja():
    """Racimo de bananos en una caja de madera cuadrada (de frente, bien plantada en el piso)."""
    L = obj(66, 58)
    amarillo, amarillo_l, verde = '#f5c531', '#ffe27a', '#8ab040'
    for (bx, by) in ((2, 16), (30, 16), (14, 6), (40, 6), (26, 0)):       # bananos acostados: medias lunas
        B = obj(34, 16)
        B.ell(0, 0, 33, 15, amarillo)
        B.ell(3, -6, 30, 9, (0, 0, 0, 0))
        for y in range(16):                                               # borrar la parte de arriba (media luna)
            for x in range(34):
                if B.im.getpixel((x, y))[3] and ((x - 16.5) / 16.5) ** 2 + ((y - 1.5) / 7.5) ** 2 < 1:
                    B.px(x, y, (0, 0, 0, 0))
        for x in range(34):                                               # luz arriba del banano
            for y in range(16):
                if B.im.getpixel((x, y))[3]:
                    B.px(x, y, amarillo_l)
                    break
        B.rect(0, 5, 2, 8, '#5a4020'); B.rect(31, 5, 33, 7, verde)
        L.im.alpha_composite(B.im, (bx, by))
    bandas(L, 0, 28, 65, 57, '#b8864c', 1.15, 0.78)       # la caja
    for y in (28, 38, 48):
        L.rect(0, y, 65, y + 1, '#8a5a34')
    L.rect(0, 28, 3, 57, '#8a5a34'); L.rect(62, 28, 65, 57, '#8a5a34')
    L.rect(26, 40, 39, 45, '#f6f1e4')                      # etiqueta
    L.rect(28, 42, 37, 43, '#3a8a3a')
    return terminar(L)


def trampa_raton():
    """Trampa de ratón: base de madera, resorte, la barra y el quesito (hace daño)."""
    L = obj(46, 20)
    bevel(L, 0, 13, 45, 19, '#c8945a', 1.2, 0.72)          # base
    L.rect(2, 16, 43, 16, '#a87840')
    L.rect(4, 8, 40, 9, '#c9d0d4')                         # barra de la trampa (armada)
    L.rect(4, 8, 5, 13, '#c9d0d4'); L.rect(39, 8, 40, 13, '#c9d0d4')
    L.circ(22, 11, 3, '#9aa2a8')                           # resorte
    L.px(21, 10, '#ffffff')
    L.poly([(30, 12), (40, 12), (40, 6)], '#f5c531')       # queso
    L.px(35, 10, '#d8a020'); L.px(38, 9, '#d8a020')
    return terminar(L)


DIBUJADOS = {
    'lena': lena, 'parrilla': parrilla, 'silla_patio': silla_patio, 'bananos_canasta': bananos_caja,
    'tv_mueble': tv_mueble,
    'comoda': comoda, 'baul': baul, 'mesa_redonda': mesa, 'taburete': taburete, 'cojines': cojin,
    'refri': refri, 'cocina_gas': cocina_gas, 'chorreador': chorreador, 'cama': cama,
    'inodoro': inodoro, 'lavamanos': lavamanos,
}
