"""Textura y luz en pixel art para las paredes y los pisos de cada cuarto (2026-11-19).

Se corre DESPUÉS de escenarios.py / cuartos2.py / frente.py y ANTES de datos.py:

    python texturas.py            # todos los cuartos
    python texturas.py sala bano  # solo esos

Qué hace, siempre con pixeles enteros y tramado Bayer (nada de suavizado):
  - paredes (pared.png): manchitas de repello en las partes lisas (solo donde el color es parejo, así no ensucia
    cuadros, muebles ni azulejos), un poco más oscuro arriba (rincón con el cielo raso) y una sombra tramada
    abajo, contra el piso (oclusión), para que la pared no se vea plana;
  - pisos (suelo.png): grano según el material (cerámica, madera, piedrilla, concreto), un brillo tramado arriba
    donde la luz pega y la orilla de adelante más oscura, que da profundidad.

Cada PNG queda marcado ('texturizado' en sus datos de texto). Si se vuelve a correr no se procesa dos veces; si se
vuelve a pintar el fondo con los otros scripts, el PNG nuevo sale sin marca y se procesa otra vez.
"""
import sys, os
import numpy as np
from PIL import Image, PngImagePlugin

AQUI = os.path.dirname(os.path.abspath(__file__))
ESC = os.path.join(AQUI, '..', 'escenarios')
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
MARCA = 'texturizado'

# por cuarto: cuánto repello en la pared (0 = nada), y el material del piso
CUARTOS = {
    'cocina':   {'repello': 0.035, 'piso': 'ceramica'},
    'sala':     {'repello': 0.035, 'piso': 'ceramica'},
    'cuarto':   {'repello': 0.035, 'piso': 'madera'},
    'bano':     {'repello': 0.02, 'piso': 'ceramica'},
    'corredor': {'repello': 0.035, 'piso': 'piedrilla'},
    'keylin':   {'repello': 0.04, 'piso': 'concreto'},
    'patio':    {'repello': 0.0,  'piso': 'tierra'},
}


def ruido(w, h, escala, semilla):
    """Ruido de valores que se repite de lado a lado (las capas se repiten) y se interpola en bloques."""
    r = np.random.default_rng(semilla)
    gw, gh = max(1, w // escala), max(1, h // escala) + 2
    grid = r.random((gh, gw))
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    fx, fy = xs / escala, ys / escala
    x0, y0 = np.floor(fx).astype(int), np.floor(fy).astype(int)
    tx, ty = fx - x0, fy - y0
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a = grid[y0 % gh, x0 % gw]; b = grid[y0 % gh, (x0 + 1) % gw]
    c = grid[(y0 + 1) % gh, x0 % gw]; d = grid[(y0 + 1) % gh, (x0 + 1) % gw]
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


def bayer(w, h):
    ys, xs = np.mgrid[0:h, 0:w]
    return BAYER[ys % 4, xs % 4]


def liso(rgb, alfa):
    """Pixeles cuyo vecindario de 5x5 es del mismo color (con tolerancia): ahí sí va la textura."""
    a = rgb.astype(int)
    ok = alfa > 250
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx == 0 and dy == 0:
                continue
            s = np.roll(np.roll(a, dy, 0), dx, 1)
            ok &= np.abs(s - a).sum(2) <= 12
    return ok


def aplicar(rgb, mask, k):
    """Multiplica el brillo por k (matriz) donde mask."""
    out = rgb.astype(float)
    out[mask] *= k[mask][:, None]
    return np.clip(out, 0, 255)


def pared(im, cfg, semilla):
    a = np.array(im.convert('RGBA'))
    rgb, al = a[..., :3].astype(float), a[..., 3]
    h, w = al.shape
    B = bayer(w, h)
    vis = al > 0
    # 1) grano de repello: pixeles sueltos un tono más claro u oscuro, más una variación muy suave y grande
    if cfg['repello'] > 0:
        r = np.random.default_rng(semilla)
        u = r.random((h, w))
        grande = ruido(w, h, 40, semilla + 1)
        nivel = np.where(u > 0.93, 1, np.where(u < 0.07, -1, 0)).astype(float)
        nivel += np.where(grande > 0.7 + B * 0.1, 0.5, 0) - np.where(grande < 0.3 - B * 0.1, 0.5, 0)
        k = 1 + nivel * cfg['repello']
        rgb = aplicar(rgb, liso(rgb, al), k)
    # 2) luz: arriba un poco más oscuro (rincón del cielo raso), abajo sombra contra el piso
    filas = np.arange(h)[:, None].repeat(w, 1)
    # dónde termina la pared (la última fila con algo pintado, contando columna por columna la mayoría)
    llenas = (al > 0).sum(1)
    base = int(np.nonzero(llenas > w * 0.5)[0].max()) if (llenas > w * 0.5).any() else h - 1
    arriba = np.clip(1 - filas / 22.0, 0, 1)                    # 22 px de penumbra arriba
    abajo = np.clip((filas - (base - 14)) / 14.0, 0, 1)         # 14 px de sombra abajo
    osc = (arriba * 0.07 + abajo * 0.14)
    # tramado: cada pixel se oscurece en saltos (0, mitad, entero) según el umbral Bayer, como en el pixel art
    q = osc / 0.06
    lo = np.floor(q)
    k = 1 - 0.06 * (lo + ((q - lo) > B))
    rgb = aplicar(rgb, vis & (filas <= base), k)
    a[..., :3] = rgb.astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def piso(im, cfg, semilla):
    a = np.array(im.convert('RGBA'))
    rgb, al = a[..., :3].astype(float), a[..., 3]
    h, w = al.shape
    B = bayer(w, h)
    filas = np.arange(h)[:, None].repeat(w, 1)
    vis = al > 0
    llenas = np.nonzero((al > 0).sum(1) > w * 0.5)[0]
    if not len(llenas):
        return im
    top, bot = int(llenas.min()), int(llenas.max())
    alto = max(1, bot - top)
    rel = (filas - top) / alto                     # 0 arriba (contra la pared), 1 adelante
    mat = cfg['piso']
    k = np.ones((h, w))
    if mat == 'ceramica':
        # brillo tramado en la franja de arriba (la luz que entra) y un reflejo suave más abajo
        luz = np.clip(1 - rel / 0.35, 0, 1) * 0.10
        k += np.where(luz > B * 0.12, 0.06, 0)
        k -= np.where(rel > 0.72 + B * 0.2, 0.05, 0)
    elif mat == 'madera':
        # vetas: rayitas horizontales que van y vienen
        n = ruido(w, h, 9, semilla)
        veta = (np.sin(filas * 1.7 + n * 6) > 0.86)
        k -= np.where(veta, 0.07, 0)
        k -= np.where(rel > 0.7 + B * 0.25, 0.07, 0)
    elif mat in ('piedrilla', 'concreto'):
        n = ruido(w, h, 3, semilla) * 0.6 + ruido(w, h, 11, semilla + 3) * 0.4
        k += np.where(n > 0.68 + B * 0.06, 0.04, 0) - np.where(n < 0.32 - B * 0.06, 0.04, 0)
        k -= np.where(rel > 0.7 + B * 0.25, 0.06, 0)
    elif mat == 'tierra':
        k -= np.where(rel > 0.75 + B * 0.2, 0.06, 0)
    # la raya de contacto con la pared, un pelo más oscura (une el piso con la pared)
    k -= np.where(filas == top, 0.08, 0)
    rgb = aplicar(rgb, vis & (rel >= 0), k)
    a[..., :3] = rgb.astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def procesar(cuarto):
    cfg = CUARTOS[cuarto]
    for nombre, f in (('pared', pared), ('suelo', piso)):
        ruta = os.path.join(ESC, cuarto, nombre + '.png')
        if not os.path.exists(ruta):
            continue
        im = Image.open(ruta)
        if im.info.get(MARCA):
            print(f'{cuarto}/{nombre}: ya estaba')
            continue
        nuevo = f(im, cfg, sum((cuarto + nombre).encode()) + 7)
        meta = PngImagePlugin.PngInfo(); meta.add_text(MARCA, '1')
        nuevo.save(ruta, pnginfo=meta, optimize=True)
        print(f'{cuarto}/{nombre}: listo')


if __name__ == '__main__':
    for c in (sys.argv[1:] or CUARTOS):
        procesar(c)
