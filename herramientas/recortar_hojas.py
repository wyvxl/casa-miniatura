"""Hojas de cosas por cuarto (referencias/escenarios/*.jpg) -> pixel art del juego.

1) `python recortar_hojas.py analizar`: encuentra cada figura (lo que no es fondo, juntando piezas cercanas)
   y dibuja en _revision/hoja-<cuarto>.png las cajas numeradas.
2) `python recortar_hojas.py`: recorta las que están en PIEZAS (niveles.js/juego.js las usan por nombre),
   las pasa a su resolución de pixel art (cada "pixel" del dibujo mide PP px en la hoja), reduce colores,
   limpia motas, les pone contorno y, si se pide, las agranda en múltiplos enteros (para los muebles
   gigantes del fondo). Salida: ../escenarios/piezas.png + piezas.json.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import muebles

AQUI = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(AQUI, '..', 'referencias', 'escenarios')
REV = os.path.join(AQUI, '..', '_revision')
SAL = os.path.join(AQUI, '..', 'escenarios')
HOJAS = {'cocina': 'cocina.jpg', 'bano': 'bano.jpg', 'sala': 'sala.jpg', 'cuarto': 'habittacion.jpg', 'patio': 'patio.jpg', 'enemigos': 'enemigos.jpg'}
PP = 4.7            # tamaño de un "pixel" del dibujo en la hoja


def cargar(h, cache={}):
    if h not in cache:
        a = np.asarray(Image.open(os.path.join(REF, HOJAS[h])).convert('RGB')).astype(np.int16)
        borde = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
        bg = np.median(borde, axis=0)
        d = np.abs(a - bg).sum(axis=2)
        if h == 'bano':   # celdas blancas con líneas gris azulado: las dos cosas son fondo
            d = np.minimum(d, np.abs(a - np.array([255, 255, 255])).sum(axis=2))
        m = d > 70
        m = ndimage.binary_opening(m, iterations=1)
        cache[h] = (a, m, bg)
    return cache[h]


_FIG = {}


def figuras(h):
    if h in _FIG:
        return _FIG[h]
    _FIG[h] = _figuras(h)
    return _FIG[h]


def _figuras(h):
    a, m, bg = cargar(h)
    junto = ndimage.binary_dilation(m, iterations=7)
    lab, n = ndimage.label(junto)
    cajas = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        ys, xs = sl
        area = m[sl][lab[sl] == i + 1].sum()
        if area < 900:
            continue
        cajas.append((xs.start, ys.start, xs.stop, ys.stop))
    cajas.sort(key=lambda c: (c[1] // 200, c[0]))
    return cajas


def analizar():
    for h in HOJAS:
        a, m, bg = cargar(h)
        im = Image.fromarray(a.astype(np.uint8))
        d = ImageDraw.Draw(im)
        cajas = figuras(h)
        for k, (x0, y0, x1, y1) in enumerate(cajas):
            d.rectangle([x0, y0, x1, y1], outline=(255, 0, 0), width=4)
            d.rectangle([x0, y0, x0 + 44, y0 + 30], fill=(255, 0, 0))
            d.text((x0 + 6, y0 + 6), str(k), fill=(255, 255, 255))
        im.resize((im.width // 2, im.height // 2)).save(os.path.join(REV, f'hoja-{h}.png'))
        print(h, len(cajas), 'figuras, fondo', bg)


# ---------------------------------------------------------------- piezas
# nombre: (hoja, punto dentro de la figura en _revision/hoja-<cuarto>.png (a media escala), escala, tipo, hundir)
#   escala: cuántos px del juego mide cada "pixel" del dibujo (1 = tamaño natural; 2 o 3 = mueble gigante del fondo)
#   tipo: plataforma, rebote, adorno o fondo (solo para pintar las capas de atrás)
#   hundir: cuánto se baja la superficie donde se pisa (lo dibujado en diagonal muestra su cara de arriba)
PIEZAS = {
    # cocina
    'taza_cr':     ('cocina', (455, 115), 1, 'plataforma', 5),
    'molinillo':   ('cocina', (635, 150), 1, 'plataforma', 4),
    'cafe_britt':  ('cocina', (825, 130), 1, 'plataforma', 3),
    'olla':        ('cocina', (430, 320), 1, 'plataforma', 8),
    'gallo_pinto': ('cocina', (640, 310), 1, 'plataforma', 8),
    'tortillas':   ('cocina', (825, 310), 1, 'plataforma', 6),
    'jarro':       ('cocina', (615, 490), 1, 'plataforma', 4),
    'lizano':      ('cocina', (460, 640), 1, 'plataforma', 1),
    'bananos':     ('cocina', (635, 660), 1, 'plataforma', 6),
    'guacal':      ('cocina', (815, 660), 1, 'plataforma', 4),
    'tarrina':     ('cocina', (975, 655), 1, 'plataforma', 5),
    'salero':      ('cocina', (1128, 655), 1, 'plataforma', 2),
    'hierbas':     ('cocina', (295, 470), 1, 'adorno', 0),
    'tabla_tomate': ('cocina', (115, 650), 1, 'adorno', 0),
    'refri':       ('cocina', (1270, 385), 2, 'fondo', 0),
    'cocina_gas':  ('cocina', (1025, 455), 2, 'fondo', 0),
    'chorreador':  ('cocina', (180, 200), 2, 'fondo', 0),
    'molinillo_g': ('cocina', (635, 150), 3, 'fondo', 0),
    # sala
    'mecedora':    ('sala', (170, 165), 2, 'fondo', 0),
    'mesa_redonda': ('sala', (510, 165), 1, 'plataforma', 0),
    'sofa':        ('sala', (910, 175), 2, 'fondo', 0),
    'radio_mesa':  ('sala', (1255, 175), 2, 'fondo', 0),
    'taburete':    ('sala', (175, 415), 1, 'plataforma', 0),
    'abanico':     ('sala', (515, 410), 2, 'fondo', 0),
    'cuadro_iglesia': ('sala', (900, 410), 2, 'fondo', 0),
    'maceta_sala': ('sala', (1250, 440), 1, 'plataforma', 0),
    'tv_mueble':   ('sala', (185, 610), 2, 'fondo', 0),
    'paraguero':   ('sala', (535, 625), 1, 'adorno', 0),
    'cojines':     ('sala', (870, 640), 1, 'rebote', 0),
    # cuarto
    'cama':        ('cuarto', (175, 165), 2, 'fondo', 0),
    'radio':       ('cuarto', (855, 95), 1, 'plataforma', 3),
    'tele':        ('cuarto', (990, 95), 2, 'fondo', 0),
    'bandera':     ('cuarto', (1105, 100), 2, 'fondo', 0),
    'cuadro_volcan': ('cuarto', (1232, 95), 2, 'fondo', 0),
    'comoda':      ('cuarto', (115, 405), 1, 'plataforma', 0),
    'mecedora_playa': ('cuarto', (335, 405), 2, 'fondo', 0),
    'estante':     ('cuarto', (575, 330), 2, 'fondo', 0),
    'crucifijo':   ('cuarto', (740, 350), 2, 'fondo', 0),
    'mochila':     ('cuarto', (820, 390), 1, 'plataforma', 4),
    'libros':      ('cuarto', (920, 440), 1, 'plataforma', 3),
    'ropa_guitarra': ('cuarto', (1215, 410), 2, 'fondo', 0),
    'bola':        ('cuarto', (830, 520), 1, 'plataforma', 2),
    'canasta':     ('cuarto', (1095, 520), 1, 'plataforma', 4),
    'vasija':      ('cuarto', (1180, 520), 1, 'plataforma', 4),
    'baul':        ('cuarto', (115, 645), 1, 'plataforma', 0),
    'abanico_pie': ('cuarto', (325, 640), 2, 'fondo', 0),
    'helecho':     ('cuarto', (480, 595), 1, 'plataforma', 0),
    'silla_azul':  ('cuarto', (745, 600), 1, 'plataforma', 6),
    'silla_roja':  ('cuarto', (485, 705), 1, 'plataforma', 6),
    'silla_morada': ('cuarto', (570, 705), 1, 'plataforma', 6),
    'chancletas':  ('cuarto', (730, 715), 1, 'adorno', 0),
    'calendario':  ('cuarto', (1180, 615), 2, 'fondo', 0),
    'orquidea':    ('cuarto', (1000, 700), 1, 'plataforma', 0),
    # baño
    'ariel':       ('bano', (90, 100), 1, 'plataforma', 2),
    'jabon_soap':  ('bano', (265, 100), 1, 'plataforma', 8),
    'clover':      ('bano', (440, 100), 1, 'plataforma', 6),
    'rexona':      ('bano', (615, 100), 1, 'plataforma', 6),
    'nivea':       ('bano', (790, 100), 1, 'plataforma', 1),
    'papel_pared': ('bano', (965, 100), 2, 'fondo', 0),
    'clorox':      ('bano', (1315, 100), 1, 'plataforma', 2),
    'zest':        ('bano', (90, 290), 1, 'plataforma', 8),
    'balde':       ('bano', (788, 290), 1, 'plataforma', 8),
    'magnesia':    ('bano', (1140, 290), 1, 'plataforma', 3),
    'meneito':     ('bano', (1315, 290), 1, 'plataforma', 1),
    'toalla_verde': ('bano', (90, 480), 2, 'fondo', 0),
    'ducha':       ('bano', (265, 480), 2, 'fondo', 0),
    'toalla_celeste': ('bano', (440, 480), 2, 'fondo', 0),
    'escobilla':   ('bano', (965, 480), 2, 'fondo', 0),
    'espejo':      ('bano', (1315, 480), 2, 'fondo', 0),
    'inodoro':     ('bano', (90, 675), 3, 'fondo', 0),
    'lavamanos':   ('bano', (265, 675), 3, 'fondo', 0),
    'protex':      ('bano', (440, 665), 1, 'plataforma', 1),
    'fabuloso':    ('bano', (615, 665), 1, 'plataforma', 1),
    'toalla_aro':  ('bano', (790, 670), 2, 'fondo', 0),
    'destapador':  ('bano', (965, 670), 2, 'fondo', 0),
    'panuelos':    ('bano', (1140, 665), 1, 'plataforma', 3),
    'suavitel':    ('bano', (1315, 665), 1, 'plataforma', 2),
    'colgate':     ('bano', (1137, 100), 1, 'adorno', 0),
    # enemigos (cuadro normal y el de aplastado)
    'caracol1':    ('enemigos', (74, 95), 1, 'enemigo', 0),
    'caracol2':    ('enemigos', (204, 106), 1, 'enemigo', 0),
    'rana1':       ('enemigos', (67, 225), 1, 'enemigo', 0),
    'rana2':       ('enemigos', (201, 225), 1, 'enemigo', 0),
    'gorgojo1':    ('enemigos', (70, 352), 1, 'enemigo', 0),
    'gorgojo2':    ('enemigos', (190, 352), 1, 'enemigo', 0),
    'oruga1':      ('enemigos', (74, 496), 1, 'enemigo', 0),
    'oruga2':      ('enemigos', (208, 493), 1, 'enemigo', 0),
    'salta1':      ('enemigos', (806, 363), 1, 'enemigo', 0),
    'salta2':      ('enemigos', (943, 366), 1, 'enemigo', 0),
    'larva1':      ('enemigos', (810, 539), 1, 'enemigo', 0),
    'larva_puf':   ('enemigos', (1253, 539), 1, 'enemigo', 0),
    'polilla1':    ('enemigos', (806, 697), 1, 'enemigo', 0),
    'polilla2':    ('enemigos', (1105, 715), 1, 'enemigo', 0),
    # patio
    'heliconia':   ('patio', (110, 150), 1, 'plataforma', 0),
    'regadera':    ('patio', (310, 130), 1, 'plataforma', 3),
    'silla_patio': ('patio', (515, 150), 1, 'plataforma', 4),
    'jarro_patio': ('patio', (1300, 120), 1, 'plataforma', 4),
    'palmera':     ('patio', (905, 340), 1, 'plataforma', 0),
    'botas':       ('patio', (1300, 330), 1, 'plataforma', 3),
    'parrilla':    ('patio', (110, 480), 1, 'plataforma', 6),
    'lena':        ('patio', (310, 505), 1, 'plataforma', 4),
    'gnomo':       ('patio', (510, 500), 1, 'plataforma', 1),
    'bananos_canasta': ('patio', (705, 690), 1, 'plataforma', 6),
    'balde_patio': ('patio', (900, 690), 1, 'plataforma', 5),
    'iguana':      ('patio', (510, 680), 1, 'fondo', 0),
}
SIN_LETRERO = {'cafe_britt', 'molinillo', 'taza_cr', 'olla', 'gallo_pinto', 'tortillas', 'lizano', 'bananos', 'guacal', 'tarrina', 'salero'}
BLANCOS = {'jabon_soap', 'clover', 'protex', 'nivea', 'salero', 'panuelos', 'espejo'}
# cuánto más grande se saca alguna (1.3 = 30 % más)
TAMANO = {'silla_roja': 1.3, 'silla_azul': 1.3, 'silla_morada': 1.3}
# las que tienen huecos de verdad (patas, rejas, aspas): no se rellenan
CON_HUECOS = {'silla_patio', 'estante', 'taburete', 'mesa_redonda', 'parrilla', 'mecedora', 'mecedora_playa', 'abanico',
              'ropa_guitarra', 'abanico_pie', 'silla_azul', 'silla_roja', 'silla_morada', 'regadera', 'radio_mesa',
              'toalla_aro', 'escobilla', 'cama', 'destapador', 'lavamanos', 'papel_pared'}


def pieza(nombre, hoja, punto, escala):
    a, m, bg = cargar(hoja)
    px, py = punto[0] * 2, punto[1] * 2
    caja = next(((x0, y0, x1, y1) for (x0, y0, x1, y1) in figuras(hoja) if x0 <= px < x1 and y0 <= py < y1), None)
    if caja is None:
        raise SystemExit(f'{nombre}: no hay figura en {punto} de {hoja}')
    x0, y0, x1, y1 = caja
    sub, mm = a[y0:y1, x0:x1], m[y0:y1, x0:x1]
    if nombre in BLANCOS:           # blanco sobre fondo blanco: se cierra el contorno y se rellena
        mm = ndimage.binary_fill_holes(ndimage.binary_closing(mm, iterations=5))
    elif nombre not in CON_HUECOS:
        mm = ndimage.binary_fill_holes(mm)
    # solo la figura más grande y lo pegado a ella (fuera letreros y motas)
    # los que tienen el letrero pegado debajo: sin juntar piezas cercanas
    lab, n = ndimage.label(ndimage.binary_dilation(mm, iterations=1 if nombre in SIN_LETRERO else 6))
    if n > 1:
        tam = ndimage.sum(mm, lab, range(1, n + 1))
        mm = mm & (lab == 1 + int(np.argmax(tam)))
    ys, xs = np.where(mm)
    sub, mm = sub[ys.min():ys.max() + 1, xs.min():xs.max() + 1], mm[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    # a la resolución del dibujo: un "pixel" = PP px de la hoja
    pp = PP / TAMANO.get(nombre, 1)
    w, h = max(1, round(sub.shape[1] / pp)), max(1, round(sub.shape[0] / pp))

    def rs(ch):
        return np.asarray(Image.fromarray(ch.astype(np.float32), 'F').resize((w, h), Image.BOX))
    al = rs(mm.astype(np.float32))
    out = np.zeros((h, w, 4), np.uint8)
    for i in range(3):
        out[:, :, i] = (rs(sub[:, :, i] * mm) / np.maximum(al, 1e-4)).clip(0, 255)
    alpha = al > 0.5
    vec = ndimage.convolve(alpha.astype(np.int8), np.ones((3, 3), np.int8), mode='constant') - alpha
    alpha &= vec >= 2
    q = np.asarray(Image.fromarray(out[:, :, :3]).quantize(28, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB'))
    out[:, :, :3] = q
    out[:, :, 3] = alpha * 255
    ring = alpha & ~ndimage.binary_erosion(alpha)
    out[ring, :3] = (34, 22, 26)
    ys, xs = np.where(out[:, :, 3] > 0)
    out = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = Image.fromarray(out)
    if escala > 1:
        im = im.resize((im.width * escala, im.height * escala), Image.NEAREST)
    return im


# ---------------------------------------------------------------- dibujos sueltos del patio (referencias/patio/*.jpg)
# Traen pintado el cuadriculado gris y blanco de "transparente": se quita todo lo gris claro.
# nombre: (archivo, caja en la vista a media escala o None = todo, ancho en el juego, tipo, hundir)
FONDO_BLANCO = {'trampa'}
SUELTOS = {
    'bananos_canasta': ('banana', None, 46, 'plataforma', 3),
    'lena':            ('madera', None, 84, 'plataforma', 1),
    'parrilla':        ('parrilla', (340, 200, 1240, 700), 74, 'plataforma', 3),
    'banca':           ('sillas', (0, 70, 1010, 680), 104, 'plataforma', 3),
    'ratonera':        ('ratonera', None, 44, 'peligro', 0),
    'trampa':          ('trampa', None, 46, 'peligro', 0),
    'silla_patio':     ('sillas', (975, 100, 1440, 670), 46, 'plataforma', 3),
}


# Dibujos que ya son pixel art con su contorno: se toma el color del centro de cada celda de su cuadrícula
# (tamaño de celda en px de la imagen), sin promediar ni volver a ponerle contorno.
NITIDOS = {'trampa': 43.5}


def nitido(nombre):
    archivo = SUELTOS[nombre][0]
    a = np.asarray(Image.open(os.path.join(REF, '..', 'patio', archivo + '.jpg')).convert('RGB')).astype(np.int16)
    sat, lum = a.max(axis=2) - a.min(axis=2), a.mean(axis=2)
    fondo = (sat < 18) & (lum > 232)
    ys, xs = np.where(ndimage.binary_opening(~fondo, iterations=3))
    x0, y0 = xs.min(), ys.min()
    p = NITIDOS[nombre]
    w, h = int(round((xs.max() - x0 + 1) / p)), int(round((ys.max() - y0 + 1) / p))
    out = np.zeros((h, w, 4), np.uint8)
    r = int(p * 0.2)
    for j in range(h):
        for i in range(w):
            cx, cy = int(x0 + (i + 0.5) * p), int(y0 + (j + 0.5) * p)
            cel = a[cy - r:cy + r + 1, cx - r:cx + r + 1].reshape(-1, 3)
            f = fondo[cy - r:cy + r + 1, cx - r:cx + r + 1]
            if f.mean() > 0.5:
                continue
            out[j, i, :3] = np.median(cel, axis=0)
            out[j, i, 3] = 255
    q = np.asarray(Image.fromarray(out[:, :, :3]).quantize(16, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB'))
    out[:, :, :3] = np.where(out[:, :, 3:] > 0, q, 0)
    return Image.fromarray(out)


def suelto(nombre):
    if nombre in NITIDOS:
        return nitido(nombre)
    archivo, caja, ancho, tipo, hundir = SUELTOS[nombre]
    a = np.asarray(Image.open(os.path.join(REF, '..', 'patio', archivo + '.jpg')).convert('RGB')).astype(np.int16)
    if caja:
        x0, y0, x1, y1 = [v * 2 for v in caja]
        a = a[y0:y1, x0:x1]
    sat = a.max(axis=2) - a.min(axis=2)
    lum = a.mean(axis=2)
    if archivo in FONDO_BLANCO:                      # fondo blanco liso: solo se quita el blanco (el metal gris se queda)
        m = ~((sat < 18) & (lum > 232))
    else:
        m = ~((sat < 22) & (lum > 108))              # el cuadriculado (y el humo) fuera
    m = ndimage.binary_opening(m, iterations=3)
    lab, n = ndimage.label(m)
    tam = ndimage.sum(m, lab, range(1, n + 1))
    m = np.isin(lab, np.where(tam >= tam.max() * 0.03)[0] + 1)
    ys, xs = np.where(m)
    sub, mm = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    w = ancho
    h = max(1, round(sub.shape[0] * ancho / sub.shape[1]))

    def rs(ch):
        return np.asarray(Image.fromarray(ch.astype(np.float32), 'F').resize((w, h), Image.BOX))
    al = rs(mm.astype(np.float32))
    out = np.zeros((h, w, 4), np.uint8)
    for i in range(3):
        out[:, :, i] = (rs(sub[:, :, i] * mm) / np.maximum(al, 1e-4)).clip(0, 255)
    alpha = al > 0.5
    vec = ndimage.convolve(alpha.astype(np.int8), np.ones((3, 3), np.int8), mode='constant') - alpha
    alpha &= vec >= 2
    q = np.asarray(Image.fromarray(out[:, :, :3]).quantize(24, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB'))
    out[:, :, :3] = q
    out[:, :, 3] = alpha * 255
    ring = alpha & ~ndimage.binary_erosion(alpha)
    out[ring, :3] = (34, 22, 26)
    im = Image.fromarray(out)
    pad = Image.new('RGBA', (im.width + 2, im.height + 2))     # 1 px de margen y contorno por fuera
    pad.alpha_composite(im, (1, 1))
    al2 = np.asarray(pad)[:, :, 3] > 0
    anillo = ndimage.binary_dilation(al2) & ~al2
    p = np.asarray(pad).copy()
    p[anillo] = (34, 22, 26, 255)
    return Image.fromarray(p)


for _n, (_f, _c, _w, _t, _h) in SUELTOS.items():
    PIEZAS[_n] = ('patio', (0, 0), 1, _t, _h)


def main():
    os.makedirs(os.path.join(SAL, 'piezas'), exist_ok=True)
    ims = {}
    for n, (hoja, punto, escala, tipo, hundir) in PIEZAS.items():
        ims[n] = suelto(n) if n in SUELTOS else muebles.DIBUJADOS[n]() if n in muebles.DIBUJADOS else pieza(n, hoja, punto, escala)
        ims[n].save(os.path.join(SAL, 'piezas', n + '.png'))
    # hoja para el juego: solo lo que se juega (lo de fondo se pinta en las capas)
    jugables = [n for n in PIEZAS if PIEZAS[n][3] != 'fondo']
    Wsheet, x, y, rowh, pos = 512, 0, 0, 0, {}
    for n in jugables:
        im = ims[n]
        if x + im.width > Wsheet:
            x, y, rowh = 0, y + rowh + 2, 0
        pos[n] = (x, y)
        x += im.width + 2
        rowh = max(rowh, im.height)
    sheet = Image.new('RGBA', (Wsheet, y + rowh + 2))
    meta = {}
    for n in jugables:
        im, (px, py) = ims[n], pos[n]
        sheet.alpha_composite(im, (px, py))
        al = np.asarray(im)[:, :, 3] > 0
        hund = PIEZAS[n][4] * PIEZAS[n][2]
        perfil = [int(np.argmax(al[:, c])) + hund if al[:, c].any() else -1 for c in range(im.width)]
        hh = al.shape[0]
        cols = [c for c in range(im.width) if al[max(0, hh - 3):, c].any()]
        meta[n] = dict(x=px, y=py, w=im.width, h=im.height, top=hund, tipo=PIEZAS[n][3], perfil=perfil,
                       pie=[cols[0], cols[-1]] if cols else [0, im.width - 1])
    sheet.save(os.path.join(SAL, 'piezas.png'))
    json.dump(meta, open(os.path.join(SAL, 'piezas.json'), 'w', encoding='utf-8'), indent=1)
    # revisión: todas, con su nombre
    filas, fila, ancho = [], [], 0
    for n, im in ims.items():
        if ancho + im.width + 8 > 1000 and fila:
            filas.append(fila)
            fila, ancho = [], 0
        fila.append((n, im))
        ancho += im.width + 8
    filas.append(fila)
    H = sum(max(im.height for _, im in f) + 14 for f in filas) + 10
    rev = Image.new('RGBA', (1000, H), (150, 170, 190, 255))
    d = ImageDraw.Draw(rev)
    yy = 5
    for f in filas:
        xx = 5
        hmax = max(im.height for _, im in f)
        for n, im in f:
            rev.alpha_composite(im, (xx, yy + hmax - im.height))
            d.text((xx, yy + hmax + 1), n[:12], fill=(20, 20, 30))
            xx += im.width + 8
        yy += hmax + 14
    rev.save(os.path.join(REV, 'piezas.png'))
    print('piezas', len(ims), 'jugables', len(jugables), 'hoja', sheet.size)


if __name__ == '__main__':
    analizar() if sys.argv[1:] == ['analizar'] else main()
