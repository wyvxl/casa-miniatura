"""Pasa las hojas de sprites dibujadas con IA (referencias/Gemini_*.jpg) a pixel art de verdad.

Por cada figura: quita el fondo gris azulado, la recorta, la achica a la cuadrícula del juego
(todas con la misma escala, para que se respeten las estaturas), reduce los colores a una paleta
por personaje, limpia los bordes y le pone un contorno de 1 pixel.

Uso:  python recortar.py analizar   -> _revision/figuras-<hoja>.png (cajas numeradas)
      python recortar.py            -> ../sprites/<nombre>.png + sprites.json
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(AQUI, '..', 'referencias')
REV = os.path.join(AQUI, '..', '_revision')
SAL = os.path.join(AQUI, '..', 'sprites')

HOJAS = {'a': 'Gemini_Generated_Image_sdplw5sdplw5sdpl.jpg',   # 5 filas de 9: Franco, Alayna, Amanda, Keylin, Maritza
         'b': 'Gemini_Generated_Image_ogdrr8ogdrr8ogdr.jpg'}   # la de Marshall


def cargar(h):
    im = Image.open(os.path.join(REF, HOJAS[h])).convert('RGB')
    return np.asarray(im).astype(np.int16)


def mascara(a):
    """Lo que no es fondo. El fondo es un gris azulado casi parejo."""
    borde = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
    bg = np.median(borde, axis=0)
    d = np.abs(a - bg).sum(axis=2)
    return d > 42, bg


def tramos(v, minv, gap, minlen):
    """Tramos donde v > minv, uniendo huecos menores que gap."""
    on = v > minv
    out, i, n = [], 0, len(v)
    while i < n:
        if on[i]:
            j = i
            last = i
            while j < n and (on[j] or j - last < gap):
                if on[j]:
                    last = j
                j += 1
            if last - i + 1 >= minlen:
                out.append((i, last + 1))
            i = last + 1
        else:
            i += 1
    return out


def figuras(a, m):
    cajas = []
    for (y0, y1) in tramos(m.sum(axis=1), 3, 12, 60):
        band = m[y0:y1]
        for (x0, x1) in tramos(band.sum(axis=0), 2, 6, 40):
            sub = m[y0:y1, x0:x1]
            ys = np.where(sub.sum(axis=1) > 1)[0]
            cajas.append([x0, y0 + ys[0], x1, y0 + ys[-1] + 1, 0])
    return None, cajas


def analizar():
    for h in HOJAS:
        a = cargar(h)
        m, bg = mascara(a)
        lab, cajas = figuras(a, m)
        im = Image.fromarray(a.astype(np.uint8))
        d = ImageDraw.Draw(im)
        for k, (x0, y0, x1, y1, _) in enumerate(cajas):
            d.rectangle([x0, y0, x1, y1], outline=(255, 0, 0), width=3)
            d.text((x0 + 4, y0 + 4), str(k), fill=(255, 255, 0))
        im.save(os.path.join(REV, f'figuras-{h}.png'))
        print(h, 'fondo', bg, 'figuras', len(cajas))
        for k, c in enumerate(cajas):
            print(' ', k, c[:4], 'alto', c[3] - c[1], 'ancho', c[2] - c[0])


if __name__ == '__main__':
    if sys.argv[1:] == ['analizar']:
        analizar()


# ---------------------------------------------------------------- personajes
# alto final en pixeles del juego (Franco mide 1.10 m, Maritza 1.55 m)
PJ = {
    'franco':  dict(hoja='a', figs=list(range(0, 9)), alto=40),
    'alayna':  dict(hoja='a', figs=list(range(9, 18)), alto=43, colores=48, octree=True),     # con las orejitas de gato
    'amanda':  dict(hoja='a', figs=[18, 19, 20, 21, 22, 23, '24a', '24b', 25], alto=47),
    'keylin':  dict(hoja='a', figs=list(range(26, 35)), alto=48),
    'maritza': dict(hoja='a', figs=[35, 36, 37, 38, '39a', '39b', '40a', '40b'], alto=52),
    'marshall': dict(hoja='b', figs=list(range(13, 21)), alto=17, colores=14),
}
# cuadros de cada animación (índices dentro de la fila)
ANIMS = {
    'franco':  dict(correr=([0, 1, 2, 3, 4], 10), quieto=([5], 1), hola=([6, 7], 4), pose=([8], 1), saltar=([1], 1), caer=([3], 1)),
    'alayna':  dict(correr=([0, 1, 2, 3, 4], 10), quieto=([5], 1), hola=([6, 7], 4), pose=([8], 1), saltar=([1], 1), caer=([3], 1)),
    'amanda':  dict(correr=([0, 1, 2, 3, 4], 10), quieto=([5], 1), hola=([6, 7], 4), pose=([8], 1), saltar=([1], 1), caer=([3], 1)),
    'keylin':  dict(correr=([0, 1, 2, 3, 4], 10), quieto=([5], 1), hola=([7, 8], 3), pose=([6], 1), saltar=([1], 1), caer=([3], 1)),
    'maritza': dict(correr=([0, 1, 2, 3, 4], 9), quieto=([0], 1), sentada=([5, 6], 1), hola=([7], 1), saltar=([1], 1), caer=([3], 1)),
    'marshall': dict(correr=([0, 1, 2, 3, 4], 12), saltar=([5], 1), caer=([6], 1), quieto=([7], 1)),
}


def partir(m, caja, lo, hi):
    x0, y0, x1, y1, _ = caja
    col = m[y0:y1, x0 + lo:x0 + hi].sum(axis=0)
    cut = x0 + lo + int(np.argmin(col))
    return [x0, y0, cut, y1, 0], [cut, y0, x1, y1, 0]


def cajas_de(h, a, m):
    _, cajas = figuras(a, m)
    d = {i: c for i, c in enumerate(cajas)}
    if h == 'a':
        d['24a'], d['24b'] = partir(m, cajas[24], 140, 215)
        d['39a'], d['39b'] = partir(m, cajas[39], 130, 215)
        d['40a'], d['40b'] = partir(m, cajas[40], 200, 320)
    return d


def ajustar(m, c):
    """Recorta la caja a lo que de verdad tiene figura."""
    x0, y0, x1, y1, _ = c
    sub = m[y0:y1, x0:x1]
    xs = np.where(sub.sum(axis=0) > 0)[0]
    ys = np.where(sub.sum(axis=1) > 0)[0]
    return [x0 + xs[0], y0 + ys[0], x0 + xs[-1] + 1, y0 + ys[-1] + 1]


def achicar(a, m, box, k):
    """Achica con promedio ponderado por la máscara (el fondo no ensucia los bordes)."""
    x0, y0, x1, y1 = box
    rgb = a[y0:y1, x0:x1].astype(np.float32)
    mm = m[y0:y1, x0:x1].astype(np.float32)
    w = max(1, round((x1 - x0) * k))
    h = max(1, round((y1 - y0) * k))

    def rs(ch):
        return np.asarray(Image.fromarray(ch, 'F').resize((w, h), Image.BOX))
    al = rs(mm)
    out = np.zeros((h, w, 4), np.float32)
    for i in range(3):
        out[:, :, i] = rs(rgb[:, :, i] * mm) / np.maximum(al, 1e-4)
    out[:, :, 3] = al
    return out


def erosionar(m):
    e = m.copy()
    e[1:, :] &= m[:-1, :]
    e[:-1, :] &= m[1:, :]
    e[:, 1:] &= m[:, :-1]
    e[:, :-1] &= m[:, 1:]
    return e


def limpiar(al):
    """Quita motas sueltas: pixeles con menos de 2 vecinos y pedacitos separados de la figura."""
    from scipy import ndimage
    vec = ndimage.convolve(al.astype(np.int8), np.ones((3, 3), np.int8), mode='constant') - al
    al = al & (vec >= 2)
    lab, n = ndimage.label(al, structure=np.ones((3, 3)))
    if n > 1:
        tam = ndimage.sum(al, lab, range(1, n + 1))
        al = np.isin(lab, np.where(tam >= max(10, tam.max() * 0.02))[0] + 1)
    return al


def hacer(nombre, cfg, cache):
    h = cfg['hoja']
    if h not in cache:
        a = cargar(h)
        m, _ = mascara(a)
        cj = cajas_de(h, a, m)
        cache[h] = (a, erosionar(m), cj)
    a, m, cajas = cache[h]
    boxes = [ajustar(m, cajas[f]) for f in cfg['figs']]
    # misma escala para toda la fila: la manda el cuadro "quieto" de pie (o el primero)
    ref_h = np.median([b[3] - b[1] for b in boxes[:5]])
    k = cfg['alto'] / ref_h
    frames = [achicar(a, m, b, k) for b in boxes]
    # paleta común de la fila
    ops = np.concatenate([f[f[:, :, 3] > 0.5][:, :3] for f in frames])
    pal_img = Image.fromarray(ops.reshape(1, -1, 3).clip(0, 255).astype(np.uint8))
    pal = pal_img.quantize(cfg.get('colores', 30), method=Image.Quantize.FASTOCTREE if cfg.get('octree') else Image.Quantize.MEDIANCUT)
    res = []
    for f in frames:
        rgb = Image.fromarray(f[:, :, :3].clip(0, 255).astype(np.uint8))
        q = np.asarray(rgb.quantize(palette=pal, dither=Image.Dither.NONE).convert('RGB'))
        alpha = limpiar(f[:, :, 3] > 0.5)
        rgba = np.zeros(f.shape, np.uint8)
        rgba[:, :, :3] = q
        rgba[:, :, 3] = alpha * 255
        # borde: el anillo de afuera es donde el color quedó mezclado con el fondo del JPG; se pinta de un
        # contorno oscuro parejo (como el de la referencia), sin motas de colores raros
        ring = alpha & ~erosionar(alpha)
        rgba[ring, :3] = (34, 22, 26)
        res.append(rgba)
    # lienzo común: pies abajo, centrado por el tronco
    W = max(r.shape[1] for r in res) + 4
    H = max(r.shape[0] for r in res) + 2
    sheet = Image.new('RGBA', (W * len(res), H))
    for i, r in enumerate(res):
        al = r[:, :, 3] > 0
        hh = r.shape[0]
        band = al[int(hh * 0.35):int(hh * 0.6)]
        cx = np.where(band.any(axis=0))[0].mean() if band.any() else r.shape[1] / 2
        x = int(round(W / 2 - cx))
        y = H - 1 - hh
        sheet.alpha_composite(Image.fromarray(r), (i * W + x, y))
    sheet.save(os.path.join(SAL, nombre + '.png'))
    an = {k2: dict(frames=v[0], fps=v[1]) for k2, v in ANIMS[nombre].items()}
    return dict(w=W, h=H, n=len(res), anims=an)


def main():
    cache, meta = {}, {}
    for nombre, cfg in PJ.items():
        meta[nombre] = hacer(nombre, cfg, cache)
        print(nombre, meta[nombre]['w'], 'x', meta[nombre]['h'])
    json.dump(meta, open(os.path.join(SAL, 'sprites.json'), 'w', encoding='utf-8'), indent=1)
    # hoja de revisión
    K = 5
    ims = [Image.open(os.path.join(SAL, n + '.png')) for n in PJ]
    Wr = max(i.width for i in ims) * K + 20
    Hr = sum(i.height * K + 10 for i in ims) + 10
    out = Image.new('RGBA', (Wr, Hr), (150, 170, 190, 255))
    y = 10
    for i in ims:
        out.alpha_composite(i.resize((i.width * K, i.height * K), Image.NEAREST), (10, y))
        y += i.height * K + 10
    out.save(os.path.join(REV, 'hoja-sprites.png'))


if __name__ == '__main__' and sys.argv[1:] != ['analizar']:
    main()
