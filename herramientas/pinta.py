"""Kit para pintar capas de fondo en pixel art (sin suavizado) que se repiten de lado a lado."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from pixel import hexc, shade, mix

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def C(c):
    return hexc(c) if isinstance(c, str) else c


class Layer:
    def __init__(self, w, h, wrap=True):
        self.w, self.h, self.wrap = w, h, wrap
        self.im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    # --- repetición: lo que se sale por un lado entra por el otro
    def _offs(self, x0, x1):
        o = [0]
        if self.wrap:
            if x1 >= self.w:
                o.append(-self.w)
            if x0 < 0:
                o.append(self.w)
        return o

    def rect(self, x0, y0, x1, y1, c):
        for o in self._offs(x0, x1):
            self.d.rectangle([x0 + o, y0, x1 + o, y1], fill=C(c))

    def ell(self, x0, y0, x1, y1, c):
        for o in self._offs(x0, x1):
            self.d.ellipse([x0 + o, y0, x1 + o, y1], fill=C(c))

    def circ(self, cx, cy, r, c):
        self.ell(cx - r, cy - r, cx + r, cy + r, c)

    def poly(self, pts, c):
        xs = [p[0] for p in pts]
        for o in self._offs(min(xs), max(xs)):
            self.d.polygon([(x + o, y) for x, y in pts], fill=C(c))

    def line(self, pts, c, w=1):
        xs = [p[0] for p in pts]
        for o in self._offs(min(xs), max(xs)):
            self.d.line([(x + o, y) for x, y in pts], fill=C(c), width=w)

    def px(self, x, y, c):
        x = int(x) % self.w if self.wrap else int(x)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.im.putpixel((x, int(y)), C(c))

    def vgrad(self, x0, y0, x1, y1, stops):
        """Degradado vertical tramado (Bayer 4x4) entre varios colores."""
        stops = [C(s) for s in stops]
        a = np.array(self.im)
        n = len(stops) - 1
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            t = (y - y0) / max(1, y1 - y0) * n
            i = min(n - 1, int(t))
            f = t - i
            # bandas: cuantiza a 4 niveles y trama entre ellas
            q = f * 4
            lo = int(q)
            fr = q - lo
            ca = mix(stops[i], stops[i + 1], lo / 4)
            cb = mix(stops[i], stops[i + 1], min(4, lo + 1) / 4)
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                a[y, x] = cb if fr > BAYER[y % 4, x % 4] else ca
        self.im = Image.fromarray(a)
        self.d = ImageDraw.Draw(self.im)

    def arr(self):
        return np.array(self.im)

    def set_arr(self, a):
        self.im = Image.fromarray(a)
        self.d = ImageDraw.Draw(self.im)

    def paste(self, other, x, y):
        for o in self._offs(x, x + other.width - 1):
            self.im.alpha_composite(other, (int(x + o), int(y))) if 0 <= x + o and x + o + other.width <= self.w \
                else _paste_clip(self.im, other, int(x + o), int(y))
        self.d = ImageDraw.Draw(self.im)

    def fog(self, c, f):
        """Acerca todo lo pintado a un color (distancia)."""
        a = self.arr().astype(np.float32)
        c = np.array(C(c)[:3], np.float32)
        m = a[:, :, 3] > 0
        a[m, :3] = a[m, :3] * (1 - f) + c * f
        self.set_arr(a.astype(np.uint8))

    def outline(self, c, only_alpha=True):
        a = self.arr()
        op = a[:, :, 3] > 0
        out = np.zeros_like(op)
        out[1:, :] |= op[:-1, :]
        out[:-1, :] |= op[1:, :]
        out[:, 1:] |= op[:, :-1]
        out[:, :-1] |= op[:, 1:]
        if self.wrap:
            out[:, 0] |= op[:, -1]
            out[:, -1] |= op[:, 0]
        out &= ~op
        a[out] = C(c)
        self.set_arr(a)

    def speckle(self, x0, y0, x1, y1, c, dens, seed, on=None):
        """Motitas de un color, solo sobre pixeles pintados (o sobre el color `on`)."""
        r = random.Random(seed)
        a = self.arr()
        c = C(c)
        n = int((x1 - x0) * (y1 - y0) * dens)
        for _ in range(n):
            x = r.randint(x0, x1) % self.w
            y = r.randint(y0, y1)
            if not (0 <= y < self.h):
                continue
            if a[y, x, 3] == 0:
                continue
            if on is not None and tuple(a[y, x]) != C(on):
                continue
            a[y, x] = c
        self.set_arr(a)


def _paste_clip(dst, src, x, y):
    sx0 = max(0, -x)
    sx1 = min(src.width, dst.width - x)
    if sx1 <= sx0:
        return
    crop = src.crop((sx0, 0, sx1, src.height))
    dst.alpha_composite(crop, (x + sx0, y))


# ---------------------------------------------------------------- formas compuestas
def clump(L, cx, cy, r, cols, seed, flat=0.8):
    """Follaje / nube: montón de círculos. cols = [sombra, medio, luz(, brillo)]"""
    rnd = random.Random(seed)
    blobs = []
    for _ in range(int(6 + r * 0.6)):
        a = rnd.uniform(0, math.tau)
        d = rnd.uniform(0, r * 0.75)
        br = rnd.uniform(r * 0.3, r * 0.55)
        blobs.append((cx + math.cos(a) * d, cy + math.sin(a) * d * flat, br))
    for x, y, br in blobs:
        L.circ(x, y + 2, br, cols[0])
    for x, y, br in blobs:
        L.circ(x - br * 0.12, y - br * 0.1, br * 0.85, cols[1])
    for x, y, br in blobs:
        if y < cy + r * 0.2:
            L.circ(x - br * 0.3, y - br * 0.35, br * 0.45, cols[2])
    if len(cols) > 3:
        for x, y, br in blobs:
            if y < cy:
                L.circ(x - br * 0.4, y - br * 0.5, max(1, br * 0.15), cols[3])


def blade(L, x, base, h, lean, w, col, seed=0):
    """Hoja de zacate: triángulo curvo."""
    pts_l, pts_r = [], []
    n = 8
    for i in range(n + 1):
        t = i / n
        cx = x + lean * t * t
        ww = w * (1 - t) ** 0.8
        pts_l.append((cx - ww / 2, base - h * t))
        pts_r.append((cx + ww / 2, base - h * t))
    L.poly(pts_l + pts_r[::-1], col)


def dither_rect(L, x0, y0, x1, y1, c1, c2, f):
    """Rectángulo tramado entre dos colores (f = cantidad de c2)."""
    c1, c2 = C(c1), C(c2)
    a = L.arr()
    for y in range(max(0, y0), min(L.h, y1 + 1)):
        for x in range(x0, x1 + 1):
            a[y, x % L.w] = c2 if f > BAYER[y % 4, x % 4] else c1
    L.set_arr(a)


def _lvl(lam, x, y, base, levels=(0.68, 1.0, 1.2), spec=None):
    t = lam + (BAYER[y % 4, x % 4] - 0.5) * 0.14
    if spec is not None and t > 0.97:
        return C(spec)
    if t < 0.28:
        return shade(base, levels[0])
    if t < 0.82:
        return base
    return shade(base, levels[2])


def sphere(L, cx, cy, r, colf, spec='#ffffff', flat=1.0):
    """Esfera sombreada en 3 tonos con tramado. colf(dx, dy, nz) -> color base."""
    lv = (-0.5, -0.62, 0.6)
    for y in range(int(cy - r * flat) - 1, int(cy + r * flat) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / (r * flat)
            d2 = dx * dx + dy * dy
            if d2 > 1:
                continue
            nz = (1 - d2) ** 0.5
            lam = dx * lv[0] + dy * lv[1] + nz * lv[2]
            L.px(x, y, _lvl(lam, x % L.w, y, C(colf(dx, dy, nz)), spec=spec))


def cylinder(L, x0, y0, x1, y1, base, spec=None):
    """Cilindro parado (patas, rollos, botellas): luz a la izquierda."""
    base = C(base)
    w = max(1, x1 - x0)
    for x in range(x0, x1 + 1):
        t = (x - x0) / w
        lam = math.cos((t - 0.3) * math.pi * 0.95)
        for y in range(y0, y1 + 1):
            L.px(x, y, _lvl(lam, x % L.w, y, base, spec=spec))


def glow(L, pts, c, alpha):
    """Rayo de luz o sombra traslúcida encima de lo pintado."""
    ov = Image.new('RGBA', L.im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    col = C(c)[:3] + (alpha,)
    xs = [p[0] for p in pts]
    for o in L._offs(min(xs), max(xs)):
        d.polygon([(x + o, y) for x, y in pts], fill=col)
    a = L.arr()
    base = Image.fromarray(a)
    mask = a[:, :, 3] > 0
    comp = Image.alpha_composite(base, ov)
    ca = np.array(comp)
    a[mask] = ca[mask]
    L.set_arr(a)


def bevel(L, x0, y0, x1, y1, base, light=1.25, dark=0.7, edge=None):
    """Caja con luz arriba-izquierda y sombra abajo-derecha."""
    b = C(base)
    L.rect(x0, y0, x1, y1, b)
    L.rect(x0, y0, x1, y0, shade(b, light))
    L.rect(x0, y0, x0, y1, shade(b, light))
    L.rect(x0, y1, x1, y1, shade(b, dark))
    L.rect(x1, y0, x1, y1, shade(b, dark))
    if edge:
        L.d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], outline=C(edge))
