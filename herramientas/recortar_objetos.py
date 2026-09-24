"""Recorta los objetos de las hojas dibujadas con IA (referencias/Gemini_*948k* y *9z4x*) y los pasa
a pixel art del tamaño del juego: coleccionables, plataformas, enemigos y peligros.

Cada caja va en coordenadas de la hoja vista a 2000 px de ancho (se multiplican por 3042/2000).
El fondo de cada caja se saca de su borde (sirve igual con el gris azulado que con el verde).

Uso:  python recortar_objetos.py  ->  ../escenarios/cosas.png + cosas.json
"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage

AQUI = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(AQUI, '..', 'referencias')
SAL = os.path.join(AQUI, '..', 'escenarios')
REV = os.path.join(AQUI, '..', '_revision')
A = 'Gemini_Generated_Image_948kjm948kjm948k.jpg'
B = 'Gemini_Generated_Image_9z4xig9z4xig9z4x.jpg'
K = 3042 / 2000

# nombre: (hoja, caja x0 y0 x1 y1, ancho en el juego, tipo)
#   tipo: moneda / tesoro (se junta), plataforma, enemigo, peligro, adorno
COSAS = {
    'moneda1':   (B, (518, 776, 642, 898), 14, 'moneda'),
    'moneda2':   (A, (1836, 730, 2000, 900), 16, 'moneda'),
    'llave':     (B, (640, 650, 834, 780), 24, 'tesoro'),
    'mapa':      (B, (36, 500, 240, 668), 24, 'tesoro'),
    'brujula':   (B, (1020, 776, 1140, 904), 16, 'tesoro'),
    'reloj':     (B, (1586, 726, 1720, 904), 16, 'tesoro'),
    'canica':    (B, (1305, 786, 1410, 900), 13, 'tesoro'),
    'peon':      (B, (720, 766, 846, 900), 14, 'tesoro'),
    'macetas':   (A, (580, 300, 846, 470), 70, 'plataforma'),
    'hongo':     (A, (846, 288, 1010, 472), 44, 'rebote'),
    'hongo2':    (A, (1012, 288, 1160, 472), 36, 'plataforma'),
    'pala':      (B, (258, 514, 742, 806), 112, 'plataforma'),
    'carro':     (B, (804, 494, 1086, 666), 88, 'plataforma'),
    'taza':      (B, (1014, 636, 1140, 746), 36, 'plataforma'),
    'libro':     (B, (1560, 580, 1706, 720), 38, 'plataforma'),
    'libro2':    (B, (872, 736, 1006, 906), 32, 'plataforma'),
    'lego':      (B, (1424, 776, 1580, 892), 42, 'plataforma'),
    'cubos':     (A, (334, 500, 494, 664), 52, 'plataforma'),
    'tabla':     (A, (306, 776, 530, 904), 70, 'plataforma'),
    'especias':  (A, (530, 736, 644, 900), 30, 'plataforma'),
    'especiero': (A, (640, 686, 780, 860), 44, 'plataforma'),
    'patito':    (B, (1876, 776, 1990, 900), 24, 'plataforma'),
    'cuchara':   (A, (200, 686, 266, 904), 16, 'adorno'),
    'pan':       (A, (866, 836, 1004, 904), 30, 'adorno'),
    'pelusa':    (A, (1710, 514, 1866, 646), 24, 'enemigo'),
    'caracol':   (A, (1740, 310, 1966, 456), 44, 'enemigo'),
    'soldadito': (B, (1426, 540, 1566, 726), 26, 'enemigo'),
    'cactus':    (B, (1730, 686, 1866, 906), 30, 'peligro'),
    'charco':    (A, (610, 100, 732, 166), 44, 'charco'),
}


UNO = ('moneda1', 'moneda2', 'pala', 'carro')  # solo la pieza más grande (y umbral bajo: plateado sobre gris)


def cargar(f, cache={}):
    if f not in cache:
        cache[f] = np.asarray(Image.open(os.path.join(REF, f)).convert('RGB')).astype(np.int16)
    return cache[f]


def cortar(nombre, hoja, caja, ancho):
    a = cargar(hoja)
    x0, y0, x1, y1 = [int(round(v * K)) for v in caja]
    sub = a[y0:y1, x0:x1]
    borde = np.concatenate([sub[:4].reshape(-1, 3), sub[-4:].reshape(-1, 3), sub[:, :4].reshape(-1, 3), sub[:, -4:].reshape(-1, 3)])
    bg = np.median(borde, axis=0)
    d = np.abs(sub - bg).sum(axis=2)
    solo = nombre in UNO
    m = d > (22 if solo else 48)
    m = ndimage.binary_opening(m, iterations=2)
    lab, n = ndimage.label(m)
    if n:
        areas = ndimage.sum(m, lab, range(1, n + 1))
        keep = np.isin(lab, np.where(areas >= areas.max() * (0.999 if solo else 0.04))[0] + 1)
        m = ndimage.binary_fill_holes(keep) if nombre not in ('taza', 'llave') else keep
    m = ndimage.binary_erosion(m, iterations=1)
    if nombre in ('carro', 'pala'):   # la sombra verde del fondo de la hoja no es parte del objeto
        r_, g_, b_ = sub[:, :, 0], sub[:, :, 1], sub[:, :, 2]
        m &= ~((g_ > r_ + 20) & (g_ > b_ + 12))
        m = ndimage.binary_opening(m, iterations=2)
    ys, xs = np.where(m)
    sub, m = sub[ys.min():ys.max() + 1, xs.min():xs.max() + 1], m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = ancho / sub.shape[1]
    w, h = ancho, max(1, round(sub.shape[0] * k))

    def rs(ch):
        return np.asarray(Image.fromarray(ch.astype(np.float32), 'F').resize((w, h), Image.BOX))
    al = rs(m.astype(np.float32))
    out = np.zeros((h, w, 4), np.uint8)
    for i in range(3):
        out[:, :, i] = (rs(sub[:, :, i] * m) / np.maximum(al, 1e-4)).clip(0, 255)
    alpha = al > 0.5
    vec = ndimage.convolve(alpha.astype(np.int8), np.ones((3, 3), np.int8), mode='constant') - alpha
    alpha &= vec >= 2                         # sin motas sueltas
    rgb = Image.fromarray(out[:, :, :3])
    q = np.asarray(rgb.quantize(24, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB'))
    out[:, :, :3] = q
    out[:, :, 3] = alpha * 255
    if nombre.startswith('moneda'):   # plata que brille sobre cualquier fondo
        o = out[:, :, :3].astype(np.float32)
        o = 110 + (o - o.mean()) * 1.6 + 60
        out[:, :, :3] = o.clip(0, 255).astype(np.uint8)
    ring = alpha & ~ndimage.binary_erosion(alpha)
    out[ring, :3] = (34, 22, 26)
    return out


def perfil(al):
    """Por cada columna, la primera fila con algo pintado (-1 si la columna está vacía): la forma de arriba,
    que es por donde se camina encima."""
    out = []
    for x in range(al.shape[1]):
        ys = np.where(al[:, x])[0]
        out.append(int(ys[0]) if len(ys) else -1)
    return out


# Objetos dibujados en diagonal (se les ve la cara de arriba): se pisa el medio de esa cara, no el borde de atrás.
HUNDIR = {'lego': 6, 'libro': 7, 'libro2': 6, 'carro': 8, 'cubos': 3, 'taza': 4, 'tabla': 6, 'macetas': 4,
          'especias': 3, 'especiero': 2, 'hongo': 3, 'hongo2': 3}


def pie(al):
    """Columnas (primera y última) que llegan hasta abajo: lo que se apoya en el piso o en otra cosa."""
    h = al.shape[0]
    cols = [x for x in range(al.shape[1]) if al[max(0, h - 3):, x].any()]
    return [cols[0], cols[-1]] if cols else [0, al.shape[1] - 1]


def main():
    ims = {n: cortar(n, *v[:3]) for n, v in COSAS.items()}
    Wsheet, x, y, rowh, pos = 512, 0, 0, 0, {}
    for n, im in ims.items():
        h, w = im.shape[:2]
        if x + w > Wsheet:
            x, y, rowh = 0, y + rowh + 2, 0
        pos[n] = (x, y)
        x += w + 2
        rowh = max(rowh, h)
    sheet = Image.new('RGBA', (Wsheet, y + rowh + 2))
    meta = {}
    for n, im in ims.items():
        px, py = pos[n]
        sheet.alpha_composite(Image.fromarray(im), (px, py))
        al = im[:, :, 3] > 0
        cov = al.mean(axis=1)
        top = int(np.argmax(cov >= 0.4))   # desde dónde se puede parar encima
        meta[n] = dict(x=px, y=py, w=im.shape[1], h=im.shape[0], top=top, tipo=COSAS[n][3], perfil=[v + HUNDIR.get(n, 0) if v >= 0 else -1 for v in perfil(al)], pie=pie(al))
    sheet.save(os.path.join(SAL, 'cosas.png'))
    json.dump(meta, open(os.path.join(SAL, 'cosas.json'), 'w', encoding='utf-8'), indent=1)
    big = sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST)
    bg = Image.new('RGBA', big.size, (150, 170, 190, 255))
    bg.alpha_composite(big)
    bg.save(os.path.join(REV, 'cosas.png'))
    print('cosas', sheet.size, len(meta))


if __name__ == '__main__':
    main()
