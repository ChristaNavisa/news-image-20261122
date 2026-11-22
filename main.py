#!/usr/bin/env python3
"""News image 22 November 2026, round 4.

Draws a one-page visual newspaper (1024x1024 PNG) summing up the
world news of Sunday 22 November 2026: 38 dated stories across
7 regions, 3 illustrated leads, a dot-matrix world map with 10
hotspots, 12 illustrated story cards, a 21-item brief grid, a
"By the numbers" band and a UTC timeline.

Python 3.13, standard library only. Own PNG encoder, own 5x7
bitmap font, own world map. No network, no clock, no randomness
except a fixed-seed generator, so two runs are byte-identical.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes out/entry.png (1024x1024, under 1 MiB).
Without MAKEFUN_OUTPUT_DIR it writes /output/entry.png.
"""

import os
import random
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (250, 246, 236)
PAPER2 = (244, 238, 224)
INK = (24, 24, 22)
NAVY = (18, 35, 63)
NAVY2 = (28, 52, 88)
RED = (178, 34, 34)
RED2 = (205, 60, 50)
GOLD = (201, 162, 39)
TEAL = (15, 118, 110)
SKY = (66, 135, 190)
SKY2 = (135, 180, 215)
SAND = (222, 205, 170)
GREY = (110, 108, 100)
LGREY = (200, 196, 186)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
GREEN = (34, 120, 70)
ORANGE = (214, 110, 20)
PURPLE = (96, 70, 140)
BROWN = (122, 84, 52)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '#' = on. Uppercase + digits + punctuation.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}

CHAR_W = 6  # 5 px glyph + 1 px gap, times scale


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.px), 3):
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def get(self, x, y):
        i = (y * self.w + x) * 3
        return (self.px[i], self.px[i + 1], self.px[i + 2])

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d <= r * r:
                        self.set(xx, yy, c)

    def disc(self, cx, cy, r, c):
        self.circle(cx, cy, r, c, fill=True)

    def ring(self, cx, cy, r, c):
        self.circle(cx, cy, r, c, fill=False)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts

        def interp(y, p, q):
            if q[1] == p[1]:
                return p[0]
            return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])

        for y in range(ay, cy + 1):
            if y < by:
                xa = interp(y, (ax, ay), (bx, by))
            else:
                xa = interp(y, (bx, by), (cx, cy))
            xb = interp(y, (ax, ay), (cx, cy))
            if xa > xb:
                xa, xb = xb, xa
            for x in range(int(xa), int(xb) + 1):
                self.set(x, y, c)

    def vgrad(self, x, y, w, h, top, bot):
        for yy in range(h):
            t = yy / max(1, h - 1)
            c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
            self.rect(x, y + yy, w, 1, c)

    def dither(self, x, y, w, h, c1, c2):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c1 if (xx + yy) % 2 == 0 else c2)

    def grain(self, x, y, w, h, seed, density, amount):
        rng = random.Random(seed)
        n = int(w * h * density)
        for _ in range(n):
            xx = rng.randrange(x, x + w)
            yy = rng.randrange(y, y + h)
            r, g, b = self.get(xx, yy)
            d = rng.choice((-amount, amount))
            self.set(xx, yy, (max(0, min(255, r + d)),
                              max(0, min(255, g + d)),
                              max(0, min(255, b + d))))

    # ------------------------------------------------------------ text
    def glyph(self, x, y, ch, scale, c):
        g = FONT.get(ch)
        if g is None:
            return
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == '1':
                    self.rect(x + col * scale, y + row * scale,
                              scale, scale, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, scale, c)
            cx += CHAR_W * scale
        return cx

    def text_center(self, cx, y, s, scale, c):
        w = text_width(s, scale)
        return self.text(cx - w // 2, y, s, scale, c)

    def text_right(self, x, y, s, scale, c):
        w = text_width(s, scale)
        return self.text(x - w, y, s, scale, c)

    def wrap(self, s, scale, max_w):
        words = s.upper().split(' ')
        lines = []
        cur = ''
        for wd in words:
            trial = wd if not cur else cur + ' ' + wd
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, c, max_w, leading=None):
        if leading is None:
            leading = 7 * scale + 2
        yy = y
        for ln in self.wrap(s, scale, max_w):
            self.text(x, yy, ln, scale, c)
            yy += leading
        return yy


# ---------------------------------------------------------------- PNG out
def chunk(typ, data):
    out = struct.pack('>I', len(data)) + typ + data
    out += struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)
    return out


def write_png(cv, path):
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        start = y * cv.w * 3
        raw += cv.px[start:start + cv.w * 3]
    idat = zlib.compress(bytes(raw), 1)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', idat)
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return png

# ---------------------------------------------------------------- world map
# Equirectangular land spans, 22 rows (lat ~75N to ~-55S), 72 cols
# (lon -180..180, 5 deg per col). Drawn from scratch.
MAP_SPANS = {
    0: [(8, 13), (46, 66)],
    1: [(2, 6), (8, 18), (24, 27), (38, 40), (44, 68)],
    2: [(2, 7), (8, 20), (24, 26), (36, 36), (38, 41), (42, 68)],
    3: [(6, 22), (36, 44), (44, 68)],
    4: [(6, 22), (37, 44), (45, 66)],
    5: [(8, 22), (37, 45), (46, 66), (67, 68)],
    6: [(9, 21), (37, 46), (47, 52), (55, 66)],
    7: [(10, 16), (37, 48), (54, 57), (58, 63)],
    8: [(12, 17), (37, 49), (50, 53), (55, 57), (59, 63)],
    9: [(14, 18), (37, 50), (55, 56), (59, 63)],
    10: [(17, 21), (38, 50), (59, 64)],
    11: [(18, 23), (39, 49), (58, 66)],
    12: [(18, 24), (40, 48), (58, 66)],
    13: [(19, 25), (41, 47), (59, 65)],
    14: [(19, 25), (41, 47), (59, 64)],
    15: [(19, 24), (41, 46), (48, 49), (58, 65)],
    16: [(19, 23), (41, 46), (58, 66)],
    17: [(20, 23), (42, 45), (59, 65)],
    18: [(20, 22), (60, 64), (69, 70)],
    19: [(20, 22), (69, 69)],
    20: [(20, 21)],
    21: [(20, 20)],
}

# (col, row, number, label, sublabel)
HOTSPOTS = [
    (41, 2, 1, "GULF OF FINLAND", "SPARTA II BURNS"),
    (43, 4, 2, "KRYVYI RIH", "TRIPLE-TAP KILLS 2"),
    (37, 4, 3, "BRUSSELS", "EU-INDONESIA DEAL"),
    (42, 6, 4, "ANTALYA", "COP31 FINAL TEXT"),
    (14, 8, 5, "GUASAVE, MEXICO", "'CHAPO ISIDRO' HELD"),
    (46, 8, 6, "BAHRAIN", "IRAN STRIKES BASES"),
    (59, 8, 7, "HONG KONG", "RECORD 98.37% VOTE"),
    (37, 11, 8, "BAYELSA, NIGERIA", "BOAT SINKS, 24 DEAD"),
    (21, 14, 9, "JUNIN, PERU", "QUAKE M6.7"),
    (71, 19, 10, "WELLINGTON", "INDIA 720-9"),
]


def draw_map(cv, x0, y0):
    # ocean background panel
    cv.rect(x0 - 6, y0 - 6, 72 * 8 + 12, 22 * 6 + 12, (226, 236, 242))
    cv.dither(x0 - 6, y0 - 6, 72 * 8 + 12, 22 * 6 + 12,
              (226, 236, 242), (214, 226, 234))
    for r, spans in MAP_SPANS.items():
        for (c0, c1) in spans:
            for c in range(c0, c1 + 1):
                cv.rect(x0 + c * 8, y0 + r * 6, 5, 4, (84, 122, 158))
    # graticule: faint equator line
    cv.hline(x0, y0 + 12 * 6 + 2, 72 * 8, (180, 196, 210))
    for (c, r, n, _lab, _sub) in HOTSPOTS:
        px = x0 + c * 8 + 2
        py = y0 + r * 6 + 2
        cv.disc(px, py, 7, RED)
        cv.ring(px, py, 7, WHITE)
        cv.ring(px, py, 8, RED)
        num = str(n)
        cv.text(px - text_width(num, 1) // 2, py - 3, num, 1, WHITE)


def draw_legend(cv, x, y, w):
    yy = y
    for (_c, _r, n, lab, sub) in HOTSPOTS:
        cv.disc(x + 7, yy + 6, 6, RED)
        cv.text(x + 1, yy + 3, str(n), 1, WHITE)
        cv.text(x + 18, yy, lab, 2, INK)
        cv.text_right(x + w, yy, sub, 1, GREY)
        yy += 15
    return yy


# ---------------------------------------------------------------- scenes
def starburst(cv, cx, cy, r, c1, c2):
    for k in range(12):
        import math
        a = k * math.pi / 6
        x1 = cx + int(r * 0.35 * math.cos(a))
        y1 = cy + int(r * 0.35 * math.sin(a))
        x2 = cx + int(r * math.cos(a))
        y2 = cy + int(r * math.sin(a))
        cv.line(x1, y1, x2, y2, c1)
        cv.line(cx, cy, x2, y2, c2)
    cv.disc(cx, cy, max(2, r // 3), c2)


def scene_cop31(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (20, 48, 84), (52, 96, 140))
    # globe
    gx, gy, gr = x + w - 52, y + 30, 22
    cv.disc(gx, gy, gr, (90, 170, 120))
    cv.disc(gx - 6, gy - 6, 12, (40, 120, 90))
    cv.disc(gx + 8, gy + 8, 8, (40, 120, 90))
    cv.ring(gx, gy, gr, WHITE)
    cv.line(gx - gr, gy, gx + gr, gy, (200, 230, 200))
    # flags row
    cols = [RED2, WHITE, GOLD, TEAL, ORANGE, GREEN, PURPLE]
    for i, fc in enumerate(cols):
        fx = x + 10 + i * 16
        cv.vline(fx, y + 8, 18, (220, 220, 210))
        cv.rect(fx + 1, y + 8, 11, 12, fc)
    # podium + stage
    cv.rect(x + 8, y + h - 26, w - 16, 4, (200, 170, 90))
    cv.rect(x + w // 2 - 14, y + h - 44, 28, 18, (150, 120, 60))
    cv.rect(x + w // 2 - 14, y + h - 50, 28, 6, (220, 190, 100))
    # delegate rows: rows of small heads
    for rr in range(2):
        yy = y + 46 + rr * 12
        for i in range(16):
            xx = x + 12 + i * 18 + (rr * 9)
            if xx < x + w - 70:
                cv.disc(xx, yy, 3, (230, 225, 205))
                cv.rect(xx - 4, yy + 3, 8, 5, (180, 180, 170))
    # big "35%" tag
    cv.rect(x + 8, y + h - 24, 64, 18, RED)
    cv.text(x + 12, y + h - 21, "35% BY 2035", 1, WHITE)


def scene_bahrain(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (8, 14, 34), (30, 44, 80))
    # stars
    rng = random.Random(77)
    for _ in range(40):
        cv.set(x + rng.randrange(w), y + rng.randrange(h // 2),
               (220, 220, 200))
    # radar dish
    rx, ry = x + 52, y + h - 34
    cv.line(rx, ry, rx - 16, ry - 20, (200, 200, 190))
    cv.line(rx, ry, rx + 16, ry - 20, (200, 200, 190))
    cv.line(rx - 16, ry - 20, rx + 16, ry - 20, (200, 200, 190))
    cv.vline(rx, ry - 20, 20, (160, 160, 150))
    cv.rect(rx - 3, ry, 6, 12, (120, 120, 110))
    # missile arcs with trails
    for k, (sx, sy, ex, ey) in enumerate([
            (x + 90, y + 70, x + 180, y + 18),
            (x + 120, y + 74, x + 220, y + 26),
            (x + 150, y + 76, x + 260, y + 34)]):
        mx, my = (sx + ex) // 2, min(sy, ey) - 22
        cv.line(sx, sy, mx, my, (240, 200, 90))
        cv.line(mx, my, ex, ey, (240, 200, 90))
        cv.disc(ex, ey, 3, (255, 220, 120))
        for t in range(1, 5):
            tx = sx + (mx - sx) * t // 5
            ty = sy + (my - sy) * t // 5
            cv.disc(tx, ty, 1, (240, 180, 80))
    # explosion over sea
    starburst(cv, x + w - 48, y + 26, 16, ORANGE, (255, 220, 120))
    # sea + ship
    cv.rect(x, y + h - 16, w, 16, (16, 60, 90))
    cv.rect(x + w - 110, y + h - 30, 90, 12, (30, 30, 30))
    cv.rect(x + w - 100, y + h - 42, 30, 12, (30, 30, 30))
    cv.rect(x + w - 60, y + h - 40, 20, 10, (60, 60, 60))
    # flame on ship
    cv.tri(x + w - 88, y + h - 30, x + w - 80, y + h - 48,
           x + w - 72, y + h - 30, ORANGE)
    cv.tri(x + w - 84, y + h - 30, x + w - 80, y + h - 40,
           x + w - 76, y + h - 30, (255, 220, 120))


def scene_kryvyi(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (120, 60, 40), (210, 140, 70))
    # skyline silhouettes
    heights = [34, 52, 28, 62, 40, 56, 30, 48, 36, 58]
    bx = x + 6
    for ht in heights:
        bw = (w - 12) // len(heights)
        cv.rect(bx, y + h - 20 - ht, bw - 2, ht + 20, (40, 26, 22))
        # lit windows
        for wy in range(y + h - 20 - ht + 6, y + h - 22, 12):
            cv.rect(bx + 3, wy, 3, 4, (255, 200, 90))
        bx += bw
    # drone silhouette
    dx, dy = x + w - 90, y + 22
    cv.rect(dx - 10, dy - 2, 20, 4, (20, 20, 20))
    cv.line(dx - 14, dy - 6, dx - 6, dy - 6, (20, 20, 20))
    cv.line(dx + 6, dy - 6, dx + 14, dy - 6, (20, 20, 20))
    cv.line(dx, dy + 2, dx, dy + 8, (20, 20, 20))
    # explosions
    starburst(cv, x + 70, y + 30, 18, RED2, (255, 220, 120))
    starburst(cv, x + w - 150, y + 44, 12, ORANGE, (255, 220, 120))
    # smoke
    cv.disc(x + 70, y + 14, 8, (90, 80, 76))
    cv.disc(x + 82, y + 10, 6, (110, 100, 94))
    # ambulance cross tag
    cv.rect(x + 8, y + h - 24, 20, 18, WHITE)
    cv.rect(x + 15, y + h - 21, 6, 12, RED)
    cv.rect(x + 11, y + h - 17, 14, 4, RED)
    cv.text(x + 32, y + h - 21, "2 KILLED", 1, WHITE)


# ---------------------------------------------------------------- card icons
def icon_ship(cv, x, y, s):
    cv.rect(x, y, s, s, SKY2)
    cv.rect(x + 6, y + s - 22, s - 12, 10, (40, 40, 40))
    cv.rect(x + 10, y + s - 34, 16, 12, (90, 90, 90))
    cv.rect(x + 30, y + s - 32, 14, 10, (120, 120, 120))
    cv.tri(x + 18, y + s - 34, x + 24, y + s - 52, x + 30, y + s - 34, ORANGE)
    cv.tri(x + 21, y + s - 34, x + 24, y + s - 44, x + 27, y + s - 34,
           (255, 220, 120))
    cv.disc(x + 24, y + 12, 5, (120, 120, 116))
    cv.disc(x + 30, y + 8, 4, (140, 140, 134))


def icon_missile(cv, x, y, s):
    cv.rect(x, y, s, s, (30, 40, 60))
    cv.line(x + 12, y + s - 8, x + s - 12, y + 10, (240, 200, 90))
    cv.line(x + 12, y + s - 8, x + s - 12, y + 10, (240, 200, 90))
    cv.disc(x + s - 12, y + 10, 3, (255, 220, 120))
    cv.disc(x + 14, y + s - 10, 4, ORANGE)
    cv.disc(x + 14, y + s - 10, 2, (255, 220, 120))
    cv.rect(x + s // 2 - 2, y + 8, 4, 4, WHITE)
    cv.rect(x + s // 2 - 2, y + 16, 4, 4, WHITE)


def icon_cricket(cv, x, y, s):
    cv.rect(x, y, s, s, GREEN)
    cv.line(x + 14, y + 8, x + 34, y + s - 14, (240, 220, 170))
    cv.line(x + 17, y + 8, x + 37, y + s - 14, (240, 220, 170))
    cv.line(x + 15, y + 8, x + 35, y + s - 14, (240, 220, 170))
    cv.disc(x + 42, y + 14, 6, RED2)
    cv.disc(x + 42, y + 14, 6, RED2)
    for k in range(3):
        cv.vline(x + 12 + k * 6, y + s - 22, 14, (250, 240, 200))
    cv.hline(x + 10, y + s - 22, 20, (250, 240, 200))


def icon_ballot(cv, x, y, s):
    cv.rect(x, y, s, s, PURPLE)
    cv.rect(x + 12, y + s - 26, s - 24, 18, (250, 240, 210))
    cv.hline(x + 16, y + s - 28, s - 32, (250, 240, 210))
    cv.rect(x + 20, y + 10, 12, 14, WHITE)
    cv.line(x + 22, y + 18, x + 25, y + 22, RED2)
    cv.line(x + 25, y + 22, x + 31, y + 12, RED2)


def icon_quake(cv, x, y, s):
    cv.rect(x, y, s, s, BROWN)
    cv.rect(x + 10, y + 12, 14, 26, (200, 190, 170))
    cv.rect(x + 32, y + 18, 14, 20, (180, 170, 150))
    cv.line(x + 10, y + 38, x + 20, y + 30, INK)
    cv.line(x + 20, y + 30, x + 28, y + 40, INK)
    cv.line(x + 28, y + 40, x + 38, y + 32, INK)
    cv.line(x + 38, y + 32, x + 46, y + 40, INK)
    cv.hline(x + 4, y + s - 10, s - 8, INK)


def icon_boat(cv, x, y, s):
    cv.rect(x, y, s, s, TEAL)
    cv.tri(x + 8, y + 30, x + s - 8, y + 30, x + s - 16, y + 46, (60, 40, 30))
    cv.tri(x + 8, y + 30, x + 16, y + 46, x + s - 16, y + 46, (60, 40, 30))
    for k in range(4):
        cv.disc(x + 14 + k * 8, y + 24, 3, (250, 240, 210))
    cv.line(x + 4, y + 50, x + s - 4, y + 50, WHITE)
    cv.line(x + 8, y + 53, x + s - 8, y + 53, WHITE)


def icon_badge(cv, x, y, s):
    cv.rect(x, y, s, s, NAVY2)
    cv.disc(x + s // 2, y + s // 2 - 4, 14, GOLD)
    cv.disc(x + s // 2, y + s // 2 - 4, 10, (240, 210, 110))
    starburst(cv, x + s // 2, y + s // 2 - 4, 9, GOLD, (255, 240, 160))
    cv.rect(x + 12, y + s - 16, s - 24, 6, WHITE)


def icon_trade(cv, x, y, s):
    cv.rect(x, y, s, s, (200, 170, 60))
    cv.vline(x + s // 2, y + 8, s - 20, INK)
    cv.hline(x + 8, y + 12, s - 16, INK)
    cv.line(x + 10, y + 12, x + 6, y + 26, INK)
    cv.line(x + 10, y + 12, x + 14, y + 26, INK)
    cv.line(x + s - 10, y + 12, x + s - 14, y + 26, INK)
    cv.line(x + s - 10, y + 12, x + s - 6, y + 26, INK)
    cv.tri(x + 2, y + 26, x + 18, y + 26, x + 10, y + 32, GOLD)
    cv.tri(x + s - 18, y + 26, x + s - 2, y + 26, x + s - 10, y + 32, GOLD)
    cv.rect(x + s // 2 - 8, y + s - 12, 16, 6, INK)


def icon_soccer(cv, x, y, s):
    cv.rect(x, y, s, s, (30, 90, 50))
    cv.disc(x + s // 2, y + s // 2, 18, WHITE)
    cv.disc(x + s // 2, y + s // 2, 6, INK)
    for (dx, dy) in [(-12, -8), (12, -8), (-12, 8), (12, 8), (0, -14)]:
        cv.disc(x + s // 2 + dx, y + s // 2 + dy, 3, INK)


def icon_rugby(cv, x, y, s):
    cv.rect(x, y, s, s, (120, 30, 30))
    cv.disc(x + s // 2, y + s // 2, 16, (240, 220, 180))
    cv.disc(x + s // 2, y + s // 2, 16, (240, 220, 180))
    cv.rect(x + s // 2 - 16, y + s // 2 - 4, 32, 8, (120, 30, 30))
    cv.line(x + s // 2 - 10, y + s // 2 - 12, x + s // 2 - 10,
            y + s // 2 + 12, INK)
    cv.line(x + s // 2 + 10, y + s // 2 - 12, x + s // 2 + 10,
            y + s // 2 + 12, INK)


def icon_hospital(cv, x, y, s):
    cv.rect(x, y, s, s, (230, 230, 225))
    cv.rect(x + s // 2 - 4, y + 12, 8, 26, RED)
    cv.rect(x + s // 2 - 13, y + 21, 26, 8, RED)
    cv.hline(x + 8, y + s - 10, s - 16, INK)


def icon_trophy(cv, x, y, s):
    cv.rect(x, y, s, s, (40, 60, 90))
    cv.rect(x + s // 2 - 8, y + 10, 16, 18, GOLD)
    cv.rect(x + s // 2 - 4, y + 28, 8, 8, GOLD)
    cv.rect(x + s // 2 - 12, y + 36, 24, 5, GOLD)
    cv.line(x + s // 2 - 8, y + 12, x + s // 2 - 14, y + 20, GOLD)
    cv.line(x + s // 2 + 8, y + 12, x + s // 2 + 14, y + 20, GOLD)


ICONS = {
    'ship': icon_ship, 'missile': icon_missile, 'cricket': icon_cricket,
    'ballot': icon_ballot, 'quake': icon_quake, 'boat': icon_boat,
    'badge': icon_badge, 'trade': icon_trade, 'soccer': icon_soccer,
    'rugby': icon_rugby, 'hospital': icon_hospital, 'trophy': icon_trophy,
}

# ---------------------------------------------------------------- content
LEADS = [
    ("CLIMATE - ANTALYA, TURKIYE", "COP31 DEAL ERASES FOSSIL FUELS",
     "FINAL TEXT: 10 PAGES, 94 PARAGRAPHS. NO OIL, COAL, GAS. "
     "35% BY 2035.", scene_cop31),
    ("THE GULF - BAHRAIN", "IRAN HITS US BASES, BAHRAIN",
     "IRGC CLAIMS PATRIOT RADARS HIT. BAHRAIN: FACTORY FIRE, NO DEAD.",
     scene_bahrain),
    ("WAR - KRYVYI RIH, UKRAINE", "TRIPLE-TAP KILLS TWO IN KRYVYI RIH",
     "2 MISSILES, THEN JET DRONES HIT RESCUERS. 58-73 HURT.",
     scene_kryvyi),
]

CARDS = [
    ('ship', "BALTIC", "SPARTA II STILL BURNING OFF FINLAND"),
    ('missile', "POLAND", "POLAND SEEKS NATO TALKS AFTER DEBRIS"),
    ('cricket', "CRICKET", "INDIA DECLARE ON RECORD 720-9"),
    ('ballot', "HONG KONG", "HONG KONG VOTE: RECORD 98.37% TURNOUT"),
    ('quake', "PERU", "PERU QUAKE M6.7: 1 DEAD, 16 HURT"),
    ('boat', "NIGERIA", "NIGERIA BOAT SINKS: 24 DEAD"),
    ('badge', "MEXICO", "'CHAPO ISIDRO' CAPTURED IN SINALOA"),
    ('trade', "TRADE", "EU-INDONESIA SIGN TRADE DEAL"),
    ('soccer', "FOOTBALL", "COLUMBUS STUN MESSI'S MIAMI 3-0"),
    ('rugby', "RUGBY", "FRANCE 45-17 ARGENTINA, INTO FINAL"),
    ('hospital', "BRAZIL", "BOLSONARO IN INTENSIVE CARE"),
    ('trophy', "FOOTBALL", "LEEDS ROUT CHELSEA 4-1"),
]

BRIEF = [
    "POLAND SEEKS NATO TALKS AFTER DEBRIS",
    "UKRAINE HITS GUARD HQ IN KRASNODAR",
    "DALLAS 3-0 PORTLAND; NEW ENGLAND 2-0",
    "TRUMP-PUTIN MEETING DRAWS REBUKE",
    "DRONE HITS TRAIN IN CHERNIHIV, 3 HURT",
    "WALES FALL 29-26 TO AUSTRALIA",
    "FINLAND CLOSES GULF AIR AND SEA LANES",
    "ZAPORIZHZHIA POWER STATION HIT",
    "NIGERIA OPENS 40 OIL AND GAS BLOCKS",
    "ESTONIA WARNS MORE GULF ATTACKS MAY COME",
    "COP32 TO BE HELD IN ADDIS ABABA 2027",
    "BURKINA FASO BRINGS 76,169 HOME",
    "SPARTA II: US-SANCTIONED, DEFENCE-LINKED",
    "OCTOBER 2026: 1.8C ABOVE PRE-INDUSTRIAL",
    "KENYA PARTIES TOLD TO REVISE RULES",
    "CENTCOM DENIES IRAN F-16 CLAIM",
    "ARSENAL HELD 2-2 AT NEWCASTLE",
    "MESSI WINS GOLDEN BOOT, 26 GOALS",
    "BOLSONARO DOCTORS WEIGH NEW SURGERY",
    "INDIA: SEVEN 50-PLUS STANDS, A FIRST",
    "HK COMMITTEE PICKS LEADER MARCH 2027",
]

NUMBERS = [
    ("148", "DRONES OVER UKRAINE"),
    ("720-9", "INDIA'S RECORD TOTAL"),
    ("98.37%", "HK TURNOUT, A RECORD"),
    ("35%", "POWER BY 2035"),
    ("6.7", "PERU QUAKE, 152 HOMES"),
    ("24", "DEAD IN BAYELSA BOAT"),
]

TIMELINE = ("TIMELINE (UTC): 00:22 KRYVYI RIH TOLL - 02:00 COP31 TEXT - "
            "03:00 OBJECTIONS DUE - 05:51 PERU AFTERSHOCK M5.0 - 09:00 HK "
            "POLLS OPEN - 17:00 HK TURNOUT 98.37%")


# ---------------------------------------------------------------- build
def build():
    cv = Canvas(W, H, PAPER)
    # paper grain over the whole sheet (deterministic, fixed seed)
    cv.grain(0, 0, W, H, 20261122, 0.05, 7)

    # ---- masthead
    cv.rect(0, 0, W, 84, NAVY)
    cv.rect(0, 0, W, 84, NAVY)
    cv.dither(0, 0, W, 84, NAVY, NAVY2)
    cv.text(16, 10, "THE WORLD", 5, WHITE)
    cv.text(16, 46, "IN ONE DAY", 5, GOLD)
    cv.vline(560, 12, 60, GOLD)
    cv.text(576, 12, "SUNDAY", 3, WHITE)
    cv.text(576, 36, "22 NOVEMBER 2026", 3, WHITE)
    cv.text(576, 60, "36 STORIES - 7 REGIONS", 2, (190, 200, 215))
    cv.rect(0, 84, W, 4, RED)

    # ---- kicker strip
    cv.text_center(512, 94,
                   "COP31 IN DOUBLE OVERTIME - IRAN STRIKES BAHRAIN - "
                   "KRYVYI RIH TRIPLE-TAP", 2, RED)

    # ---- three illustrated leads
    lead_x = [16, 349, 682]
    for i, (kick, head, deck, scene) in enumerate(LEADS):
        x = lead_x[i]
        w = 325
        cv.rect(x, 112, w, 188, WHITE)
        cv.rect(x, 112, w, 188, WHITE)
        cv.rect(x, 112, w, 2, RED)
        scene(cv, x + 4, 116, w - 8, 76)
        cv.text(x + 8, 196, kick, 1, RED)
        cv.para(x + 8, 208, head, 3, INK, w - 16, leading=22)
        cv.para(x + 8, 254, deck, 2, (60, 58, 52), w - 16, leading=14)
        # border
        cv.hline(x, 112, w, INK)
        cv.hline(x, 299, w, INK)
        cv.vline(x, 112, 188, INK)
        cv.vline(x + w - 1, 112, 188, INK)

    # ---- map band
    cv.text(16, 306, "WHERE IT HAPPENED - 10 HOTSPOTS", 2, INK)
    cv.text_right(1008, 306, "ALL PLACES NAMED IN THE DAY'S REPORTING", 1, GREY)
    cv.hline(16, 324, 992, INK)
    draw_map(cv, 24, 330)
    draw_legend(cv, 624, 332, 384)

    # ---- illustrated cards
    cv.text(16, 488, "THE DAY IN PICTURES", 2, INK)
    cv.text_right(1008, 488, "12 STORIES, EACH WITH ITS OWN SCENE", 1, GREY)
    cv.hline(16, 506, 992, INK)
    for i, (key, kick, head) in enumerate(CARDS):
        col = i % 4
        row = i // 4
        x = 16 + col * (244 + 8)
        y = 512 + row * (60 + 6)
        cv.rect(x, y, 244, 62, WHITE)
        ICONS[key](cv, x + 3, y + 3, 56)
        cv.text(x + 64, y + 5, kick, 1, RED)
        cv.para(x + 64, y + 15, head, 2, INK, 244 - 64 - 6, leading=15)
        cv.hline(x, y + 61, 244, LGREY)
        cv.vline(x, y, 62, LGREY)
        cv.vline(x + 243, y, 62, LGREY)

    # ---- brief grid
    cv.text(16, 712, "THE DAY IN BRIEF - 21 MORE STORIES", 2, INK)
    cv.hline(16, 730, 992, INK)
    for i, item in enumerate(BRIEF):
        col = i % 3
        row = i // 3
        x = 16 + col * (325 + 8)
        y = 736 + row * 30
        cv.disc(x + 4, y + 6, 3, RED)
        cv.para(x + 14, y, item, 2, INK, 325 - 14, leading=14)

    # ---- by the numbers
    cv.rect(0, 950, W, 40, NAVY)
    cv.dither(0, 950, W, 40, NAVY, NAVY2)
    seg = W // 6
    for i, (num, lab) in enumerate(NUMBERS):
        x = i * seg + 10
        cv.text(x, 956, num, 3, GOLD)
        cv.text(x, 978, lab, 1, (200, 208, 220))
        if i:
            cv.vline(i * seg, 956, 30, (90, 110, 140))

    # ---- timeline + footer
    cv.text(16, 996, TIMELINE, 1, INK)
    cv.text_center(
        512, 1008,
        "DATE CHECK: EVERY STORY DATED 20-22 NOV 2026 - SOURCES: REUTERS, "
        "AP, CNN, BBC, COP31 PRESIDENCY, HK ELECTIONS OFFICE, BCCI",
        1, GREY)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    cv = build()
    png = write_png(cv, path)
    import hashlib
    print("stories: 36")
    print("wrote: %s bytes: %d sha256: %s" % (
        path, len(png), hashlib.sha256(png).hexdigest()))


if __name__ == "__main__":
    main()
