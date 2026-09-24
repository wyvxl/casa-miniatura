"""Utilidades de pixel art: lienzo RGBA, cuadrículas de letras, líneas gruesas y contorno."""
import numpy as np
from PIL import Image


def hexc(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def shade(c, k):
    """Oscurece (k<1) o aclara (k>1) un color RGBA."""
    r, g, b, a = c
    if k < 1:
        return (int(r * k), int(g * k), int(b * k), a)
    t = k - 1
    return (int(r + (255 - r) * t), int(g + (255 - g) * t), int(b + (255 - b) * t), a)


def mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), dtype=np.uint8)
        # capa de "parte" para contornos internos (0 = vacío)
        self.part = np.zeros((h, w), dtype=np.int16)

    def px(self, x, y, c, part=1):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h and c is not None:
            self.a[y, x] = c
            self.part[y, x] = part

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return tuple(self.a[y, x])
        return (0, 0, 0, 0)

    def rect(self, x0, y0, x1, y1, c, part=1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c, part)

    def grid(self, rows, pal, x, y, part=1, flip=False):
        """Pinta una cuadrícula de letras. '.' o ' ' = transparente."""
        for j, row in enumerate(rows):
            n = len(row)
            for i, ch in enumerate(row):
                if ch in '. ':
                    continue
                if ch not in pal:
                    raise KeyError(f'letra {ch!r} sin color')
                xx = x + (n - 1 - i if flip else i)
                self.px(xx, y + j, pal[ch], part)

    def limb(self, pts, colors, width=2, part=1, fwd=1):
        """Traza una línea quebrada (hombro-codo-mano o cadera-rodilla-pie) de `width` pixeles.
        colors: lista de (fracción_hasta, color) a lo largo del largo total."""
        segs = list(zip(pts[:-1], pts[1:]))
        lens = [max(1e-6, ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5) for a, b in segs]
        total = sum(lens)
        done = 0
        for (a, b), L in zip(segs, lens):
            n = max(2, int(L * 3))
            for k in range(n + 1):
                t = k / n
                fx = a[0] + (b[0] - a[0]) * t
                fy = a[1] + (b[1] - a[1]) * t
                f = (done + L * t) / total
                col = colors[-1][1]
                for lim, cc in colors:
                    if f <= lim:
                        col = cc
                        break
                x0 = int(round(fx - (width - 1) / 2 if fwd > 0 else fx - width / 2 + 0.5))
                for d in range(width):
                    self.px(x0 + d, fy, col, part)
            done += L

    def outline(self, col, inner=None):
        """Contorno de 1 pixel alrededor de la silueta. `inner`: dict parte->True para
        marcar bordes entre partes (brazo delante del cuerpo, etc.) con un tono oscuro."""
        a = self.a
        op = a[:, :, 3] > 0
        out = np.zeros_like(op)
        out[1:, :] |= op[:-1, :]
        out[:-1, :] |= op[1:, :]
        out[:, 1:] |= op[:, :-1]
        out[:, :-1] |= op[:, 1:]
        out &= ~op
        a[out] = col
        if inner:
            h, w = self.part.shape
            add = []
            for y in range(h):
                for x in range(w):
                    p = self.part[y, x]
                    if p not in inner or not op[y, x]:
                        continue
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        xx, yy = x + dx, y + dy
                        if 0 <= xx < w and 0 <= yy < h and op[yy, xx]:
                            q = self.part[yy, xx]
                            if q != p and q not in inner and q != 0:
                                add.append((xx, yy))
            for x, y in add:
                c = tuple(a[y, x])
                a[y, x] = shade(c, 0.62)

    def image(self):
        return Image.fromarray(self.a, 'RGBA')


def upscale(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)
