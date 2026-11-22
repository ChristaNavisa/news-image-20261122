#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - Sunday 22 November 2026.

Draws a classic broadsheet front page summing up the world's news of
Sunday 22 November 2026: 39 dated stories, 7 regions, 3 illustrated
leads, 15 illustrated cards, a world map with numbered pins, an
"also on" list and a date-check box.

Python 3 standard library only. Own PNG encoder, own 5x7 bitmap font,
own drawn scenes. Deterministic: two runs write byte-identical files.

Writes to $MAKEFUN_OUTPUT_DIR/entry.png, else /output/entry.png.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font, glyphs in ASCII order 32..126, '#' = ink, '.' = blank.
_FONT_SRC = """
.....
.....
.....
.....
.....
.....
.....

..#..
..#..
..#..
..#..
..#..
.....
..#..

.#.#.
.#.#.
.#.#.
.....
.....
.....
.....

.#.#.
.#.#.
#####
.#.#.
#####
.#.#.
.#.#.

..#..
.####
#.#.#
.###.
..#.#
####.
..#..

##...
##..#
...#.
..#..
.#...
#..##
...##

.##..
#..#.
#.#..
.#...
#.#.#
#..#.
.##.#

..#..
..#..
.#...
.....
.....
.....
.....

...#.
..#..
.#...
.#...
.#...
..#..
...#.

.#...
..#..
...#.
...#.
...#.
..#..
.#...

.....
..#..
#.#.#
.###.
#.#.#
..#..
.....

.....
..#..
..#..
#####
..#..
..#..
.....

.....
.....
.....
.....
.##..
..#..
.#...

.....
.....
.....
#####
.....
.....
.....

.....
.....
.....
.....
.....
.##..
.##..

....#
...#.
...#.
..#..
.#...
.#...
#....

.###.
#...#
#..##
#.#.#
##..#
#...#
.###.

..#..
.##..
..#..
..#..
..#..
..#..
.###.

.###.
#...#
....#
...#.
..#..
.#...
#####

#####
...#.
..#..
...#.
....#
#...#
.###.

...#.
..##.
.#.#.
#..#.
#####
...#.
...#.

#####
#....
####.
....#
....#
#...#
.###.

..##.
.#...
#....
####.
#...#
#...#
.###.

#####
....#
...#.
..#..
.#...
.#...
.#...

.###.
#...#
#...#
.###.
#...#
#...#
.###.

.###.
#...#
#...#
.####
....#
...#.
.##..

.....
.##..
.##..
.....
.##..
.##..
.....

.....
.##..
.##..
.....
.##..
..#..
.#...

...#.
..#..
.#...
#....
.#...
..#..
...#.

.....
.....
#####
.....
#####
.....
.....

.#...
..#..
...#.
....#
...#.
..#..
.#...

.###.
#...#
....#
...#.
..#..
.....
..#..

.###.
#...#
....#
.###.
#.#.#
#.#.#
.###.

.###.
#...#
#...#
#####
#...#
#...#
#...#

####.
#...#
#...#
####.
#...#
#...#
####.

.###.
#...#
#....
#....
#....
#...#
.###.

####.
#...#
#...#
#...#
#...#
#...#
####.

#####
#....
#....
####.
#....
#....
#####

#####
#....
#....
####.
#....
#....
#....

.###.
#...#
#....
#.###
#...#
#...#
.####

#...#
#...#
#...#
#####
#...#
#...#
#...#

.###.
..#..
..#..
..#..
..#..
..#..
.###.

....#
....#
....#
....#
....#
#...#
.###.

#...#
#..#.
#.#..
##...
#.#..
#..#.
#...#

#....
#....
#....
#....
#....
#....
#####

#...#
##.##
#.#.#
#.#.#
#...#
#...#
#...#

#...#
##..#
#.#.#
#..##
#...#
#...#
#...#

.###.
#...#
#...#
#...#
#...#
#...#
.###.

####.
#...#
#...#
####.
#....
#....
#....

.###.
#...#
#...#
#...#
#.#.#
#..#.
.##.#

####.
#...#
#...#
####.
#.#..
#..#.
#...#

.####
#....
#....
.###.
....#
....#
####.

#####
..#..
..#..
..#..
..#..
..#..
..#..

#...#
#...#
#...#
#...#
#...#
#...#
.###.

#...#
#...#
#...#
#...#
#...#
.#.#.
..#..

#...#
#...#
#...#
#.#.#
#.#.#
##.##
#...#

#...#
#...#
.#.#.
..#..
.#.#.
#...#
#...#

#...#
#...#
.#.#.
..#..
..#..
..#..
..#..

#####
....#
...#.
..#..
.#...
#....
#####

.###.
.#...
.#...
.#...
.#...
.#...
.###.

#....
.#...
.#...
..#..
...#.
...#.
....#

.###.
...#.
...#.
...#.
...#.
...#.
.###.

..#..
.#.#.
#...#
.....
.....
.....
.....

.....
.....
.....
.....
.....
.....
#####

..#..
.#...
.....
.....
.....
.....
.....

.....
.....
.###.
....#
.####
#...#
.####

#....
#....
####.
#...#
#...#
#...#
####.

.....
.....
.###.
#...#
#....
#...#
.###.

....#
....#
.####
#...#
#...#
#...#
.####

.....
.....
.###.
#...#
#####
#....
.###.

..##.
.#...
.#...
#####
.#...
.#...
.#...

.....
.####
#...#
#...#
.####
....#
.###.

#....
#....
####.
#...#
#...#
#...#
#...#

..#..
.....
.##..
..#..
..#..
..#..
.###.

...#.
.....
..##.
...#.
...#.
...#.
.##..

#....
#....
#..#.
#.#..
##...
#.#..
#..#.

.##..
..#..
..#..
..#..
..#..
..#..
.###.

.....
.....
##.#.
#.#.#
#.#.#
#.#.#
#.#.#

.....
.....
####.
#...#
#...#
#...#
#...#

.....
.....
.###.
#...#
#...#
#...#
.###.

.....
.....
####.
#...#
#...#
####.
#....

.....
.....
.####
#...#
#...#
.####
....#

.....
.....
#.##.
##..#
#....
#....
#....

.....
.....
.####
#....
.###.
....#
####.

.#...
.#...
#####
.#...
.#...
#..#.
.##..

.....
.....
#...#
#...#
#...#
#..##
.##.#

.....
.....
#...#
#...#
#...#
.#.#.
..#..

.....
.....
#...#
#.#.#
#.#.#
##.##
#...#

.....
.....
#...#
.#.#.
..#..
.#.#.
#...#

.....
.....
#...#
#...#
.####
....#
.###.

.....
.....
#####
...#.
..#..
.#...
#####

...#.
..#..
..#..
.#...
..#..
..#..
...#.

..#..
..#..
..#..
..#..
..#..
..#..
..#..

.#...
..#..
..#..
...#.
..#..
..#..
.#...

.....
.....
.....
.###.
#.#.#
.....
.....
"""

_FONT_EXTRA = {
    "\u2013": (0, 0, 0, 0x1F, 0, 0, 0),   # en dash
    "\u2014": (0, 0, 0, 0x1F, 0, 0, 0),   # em dash
    "\u00b7": (0, 0, 0, 0x04, 0, 0, 0),   # middle dot
    "\u00b0": (0x0E, 0x11, 0x0E, 0, 0, 0, 0),  # degree
    "\u2019": (0x04, 0x04, 0x08, 0, 0, 0, 0),  # right quote
    "\u2018": (0x08, 0x08, 0x04, 0, 0, 0, 0),  # left quote
    "\u201c": (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),  # left double quote
    "\u201d": (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),  # right double quote
    "\u2713": (0, 0, 0x01, 0x02, 0x14, 0x08, 0),  # check mark
}


def _build_font():
    blocks = [b for b in _FONT_SRC.strip("\n").split("\n\n")]
    glyphs = {}
    for i, block in enumerate(blocks):
        rows = block.split("\n")
        if len(rows) != 7:
            raise ValueError("font block %d has %d rows" % (i, len(rows)))
        vals = []
        for r in rows:
            v = 0
            for ch in r:
                v = (v << 1) | (1 if ch == "#" else 0)
            vals.append(v)
        glyphs[chr(32 + i)] = tuple(vals)
    for ch, vals in _FONT_EXTRA.items():
        glyphs[ch] = vals
    return glyphs


FONT = _build_font()
BLANK = (0, 0, 0, 0, 0, 0, 0)


def text_width(s, scale):
    w = 0
    for ch in s:
        w += 6 * scale
    return w - scale if w else 0


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pix = bytearray(bg * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pix[i:i + 3] = c

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.pix[i:i + (x1 - x0) * 3] = c * (x1 - x0)

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
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.px(xx, yy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0:
                    self.px(xx, yy, c)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return

        def edge(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)

        for y in range(ay, cy + 1):
            if y < by:
                xa = edge(ax, ay, bx, by, y)
                xb = edge(ax, ay, cx, cy, y)
            else:
                xa = edge(bx, by, cx, cy, y)
                xb = edge(ax, ay, cx, cy, y)
            if xa > xb:
                xa, xb = xb, xa
            self.rect(int(xa), y, int(xb) - int(xa) + 1, 1, c)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.rect(int(xs[j]), y, int(xs[j + 1]) - int(xs[j]) + 1, 1, c)

    def ring(self, cx, cy, r, c, t=1):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - t <= d <= r:
                    self.px(xx, yy, c)

    def text(self, x, y, s, txt, c, bold=False):
        cx = x
        for ch in txt:
            g = FONT.get(ch, BLANK)
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * s, y + row * s, s, s, c)
                        if bold:
                            self.rect(cx + col * s + 1, y + row * s, s, s, c)
            cx += 6 * s
        return cx

    def text_c(self, cx, y, s, txt, c, bold=False):
        self.text(cx - text_width(txt, s) // 2, y, s, txt, c, bold)

    def text_r(self, x, y, s, txt, c, bold=False):
        self.text(x - text_width(txt, s), y, s, txt, c, bold)


def wrap(s, width, scale):
    """Wrap text to lines fitting `width` px at given scale."""
    maxch = max(1, width // (6 * scale))
    words = s.split(" ")
    lines = []
    cur = ""
    for wd in words:
        if not cur:
            cur = wd
        elif len(cur) + 1 + len(wd) <= maxch:
            cur += " " + wd
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(c, x, y, w, s, txt, col, lh=None, maxlines=None):
    """Draw wrapped paragraph, return y after last line."""
    if lh is None:
        lh = 7 * s + 4
    lines = wrap(txt, w, s)
    if maxlines is not None:
        lines = lines[:maxlines]
    for ln in lines:
        c.text(x, y, s, ln, col)
        y += lh
    return y


# ---------------------------------------------------------------- PNG
def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(c, path):
    raw0 = bytearray()
    raw2 = bytearray()
    w = c.w
    prev = bytearray(w * 3)
    for y in range(c.h):
        row = c.pix[y * w * 3:(y + 1) * w * 3]
        raw0.append(0)
        raw0 += row
        raw2.append(2)
        up = bytes((row[i] - prev[i]) & 0xFF for i in range(len(row)))
        raw2 += up
        prev = bytearray(row)
    comp0 = zlib.compress(bytes(raw0), 9)
    comp2 = zlib.compress(bytes(raw2), 9)
    data = comp0 if len(comp0) <= len(comp2) else comp2
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, c.h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", data)
    png += _chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- palette
PAPER = bytes((247, 242, 231))
PAPER2 = bytes((238, 231, 214))
INK = bytes((20, 24, 31))
INK2 = bytes((74, 74, 66))
RED = bytes((178, 35, 27))
RED_D = bytes((140, 22, 18))
NAVY = bytes((22, 35, 63))
NAVY2 = bytes((14, 22, 42))
TEAL = bytes((15, 107, 92))
GOLD = bytes((200, 155, 42))
ORANGE = bytes((214, 110, 30))
BLUE = bytes((36, 90, 160))
SKY = bytes((168, 205, 232))
SKY_D = bytes((120, 165, 205))
GREEN = bytes((46, 125, 60))
GREEN_L = bytes((139, 195, 74))
PURPLE = bytes((103, 78, 140))
GREY = bytes((120, 120, 114))
WHITE = bytes((255, 255, 255))
CREAM = bytes((255, 248, 220))
NIGHT = bytes((16, 24, 48))
NIGHT2 = bytes((26, 38, 74))
SUN = bytes((242, 193, 78))
FLAME = bytes((240, 120, 30))
FLAME2 = bytes((245, 190, 40))
SEA = bytes((52, 110, 150))
SEA_D = bytes((32, 80, 120))
LAND = bytes((217, 201, 163))
LAND2 = bytes((198, 178, 132))
BROWN = bytes((122, 82, 40))
WOOD = bytes((150, 104, 52))
TAG_CONF = bytes((27, 94, 32))
TAG_REP = bytes((21, 80, 140))
TAG_CLAIM = bytes((176, 96, 0))
TAG_FORE = bytes((103, 78, 140))

TAG_BG = {"CONFIRMED": TAG_CONF, "REPORTED": TAG_REP, "CLAIM": TAG_CLAIM,
          "FORECAST": TAG_FORE, "PENDING": TAG_FORE}


def tag_chip(c, x, y, tag):
    """Small filled tag chip, returns width used."""
    bg = TAG_BG.get(tag, TAG_REP)
    w = text_width(tag, 1) + 8
    c.rect(x, y, w, 10, bg)
    c.text(x + 4, y + 2, 1, tag, WHITE, bold=True)
    return w


def stars(c, x, y, w, h, n, seed):
    a = 1103515245
    s = seed
    for _ in range(n):
        s = (s * a + 12345) & 0x7FFFFFFF
        sx = x + s % w
        s = (s * a + 12345) & 0x7FFFFFFF
        sy = y + s % h
        c.px(sx, sy, WHITE)
        if s % 3 == 0:
            c.px(sx + 1, sy, WHITE)


def windows(c, x, y, w, h, lit, seed):
    """Lit windows on a dark building."""
    a = 1103515245
    s = seed
    for yy in range(y + 4, y + h - 4, 9):
        for xx in range(x + 4, x + w - 4, 8):
            s = (s * a + 12345) & 0x7FFFFFFF
            if s % 100 < lit:
                c.rect(xx, yy, 4, 5, SUN if s % 5 else CREAM)


def building(c, x, y, w, h, col, lit=55, seed=7):
    c.rect(x, y, w, h, col)
    windows(c, x, y, w, h, lit, seed)


def flame(c, x, y, s):
    """A flame of height ~s at (x,y) base centre."""
    c.tri(x - s // 2, y, x, y - s, x + s // 2, y, FLAME)
    c.tri(x - s // 4, y, x, y - s // 2, x + s // 4, y, FLAME2)
    c.tri(x - s // 6, y, x, y - s // 3, x + s // 6, y, CREAM)


def smoke(c, x, y, r):
    c.circle(x, y, r, GREY)
    c.circle(x + r, y - r // 2, r * 3 // 4, GREY)
    c.circle(x - r, y - r // 2, r * 2 // 3, GREY)


# ---------------------------------------------------------------- scenes
def scene_cop31(c, x, y, w, h):
    c.rect(x, y, w, h, SKY)
    c.circle(x + w - 34, y + 22, 18, SUN)
    c.circle(x + w - 34, y + 22, 12, FLAME2)
    # hills
    c.poly([(x, y + h), (x, y + h - 18), (x + w // 3, y + h - 34),
            (x + 2 * w // 3, y + h - 20), (x + w, y + h - 30),
            (x + w, y + h)], GREEN)
    # hall
    c.rect(x + 14, y + h - 62, w - 28, 52, CREAM)
    c.rect(x + 14, y + h - 62, w - 28, 4, BROWN)
    c.rect(x + 14, y + h - 62, 4, 52, BROWN)
    c.rect(x + w - 18, y + h - 62, 4, 52, BROWN)
    # delegates: heads + shoulders behind the table
    for i in range(5):
        dx = x + 34 + i * (w - 68) // 4
        c.circle(dx, y + h - 66, 7, bytes((198, 150, 110)) if i % 2 == 0 else bytes((120, 90, 60)))
        c.rect(dx - 10, y + h - 60, 20, 12, NAVY if i % 2 else RED_D)
    # table
    c.rect(x + 10, y + h - 46, w - 20, 8, WOOD)
    c.rect(x + 10, y + h - 38, 6, 28, WOOD)
    c.rect(x + w - 16, y + h - 38, 6, 28, WOOD)
    # document on table
    c.rect(x + w // 2 - 14, y + h - 44, 28, 30, WHITE)
    c.rect(x + w // 2 - 14, y + h - 44, 28, 2, RED)
    c.hline(x + w // 2 - 10, y + h - 36, 20, GREY)
    c.hline(x + w // 2 - 10, y + h - 30, 20, GREY)
    c.hline(x + w // 2 - 10, y + h - 24, 14, GREY)
    # globe
    c.circle(x + 30, y + 26, 16, SEA)
    c.ellipse(x + 26, y + 22, 6, 4, LAND)
    c.ellipse(x + 34, y + 30, 5, 3, LAND)


def scene_drones(c, x, y, w, h):
    c.rect(x, y, w, h, NIGHT)
    stars(c, x, y, w, h - 40, 26, 1234)
    c.circle(x + w - 30, y + 18, 10, CREAM)
    # searchlight
    c.tri(x + w // 2, y + h, x + w // 2 - 14, y + 30, x + w // 2 + 14, y + 30,
          bytes((140, 150, 195)))
    # drones: small X bodies with rotor dots
    for dx, dy, s in [(x + 40, y + 30, 7), (x + w // 2, y + 18, 8),
                      (x + w - 60, y + 42, 6), (x + w // 2 + 60, y + 34, 5)]:
        c.line(dx - s, dy - s, dx + s, dy + s, WHITE)
        c.line(dx - s, dy + s, dx + s, dy - s, WHITE)
        c.circle(dx, dy, 2, FLAME2)
        c.px(dx - s - 2, dy - s, WHITE)
        c.px(dx + s + 2, dy - s, WHITE)
    # city skyline
    base = y + h
    for bx, bw, bh in [(x + 6, 34, 34), (x + 44, 26, 48), (x + 74, 40, 30),
                       (x + 118, 30, 56), (x + 152, 36, 40), (x + 192, 28, 50),
                       (x + 224, 34, 36), (x + 262, 30, 44), (x + 296, 22, 30)]:
        building(c, bx, base - bh, bw, bh, NIGHT2, lit=60, seed=bx)
    c.rect(x, y + h - 4, w, 4, NAVY2)
    # fire glow on one block
    flame(c, x + 130, y + h - 56, 14)


def scene_bahrain(c, x, y, w, h):
    # dusk sky bands
    c.rect(x, y, w, h // 2, bytes((90, 60, 90)))
    c.rect(x, y + h // 2, w, h - h // 2, bytes((214, 130, 60)))
    c.circle(x + w - 36, y + 20, 14, SUN)
    # radar dishes: shallow bowls on masts
    for dx in (x + 56, x + w - 80):
        c.rect(dx - 3, y + h - 58, 6, 58, GREY)
        c.tri(dx - 22, y + h - 66, dx + 22, y + h - 66, dx, y + h - 84, WHITE)
        c.line(dx, y + h - 84, dx + 18, y + h - 102, WHITE)
        c.circle(dx + 18, y + h - 102, 2, RED)
    # industrial building, on fire
    c.rect(x + w // 2 - 34, y + h - 46, 68, 46, bytes((70, 70, 78)))
    c.rect(x + w // 2 - 34, y + h - 46, 68, 5, NAVY2)
    flame(c, x + w // 2 - 14, y + h - 46, 20)
    flame(c, x + w // 2 + 16, y + h - 46, 14)
    smoke(c, x + w // 2, y + h - 78, 9)
    # ground + sea
    c.rect(x, y + h - 8, w, 8, SEA_D)


def scene_hk(c, x, y, w, h):
    c.rect(x, y, w, h, SKY)
    c.circle(x + w - 26, y + 16, 11, SUN)
    for bx, bw, bh in [(x + 4, 22, 30), (x + 30, 18, 44), (x + 52, 26, 34),
                       (x + 82, 20, 50), (x + 106, 24, 38), (x + 134, 22, 46),
                       (x + 160, 26, 32)]:
        building(c, bx, y + h - bh - 8, bw, bh, bytes((90, 110, 140)), lit=40, seed=bx)
    c.rect(x, y + h - 8, w, 8, SEA)
    # ballot box
    c.rect(x + w // 2 - 22, y + 8, 44, 30, WHITE)
    c.rect(x + w // 2 - 22, y + 8, 44, 3, RED)
    c.rect(x + w // 2 - 8, y + 12, 16, 3, INK)
    # ballot going in
    c.rect(x + w // 2 - 6, y + 2, 12, 8, CREAM)
    c.line(x + w // 2 - 16, y + 30, x + w // 2 - 6, y + 22, RED)
    c.line(x + w // 2 - 6, y + 22, x + w // 2 + 14, y + 36, RED)


def scene_f1(c, x, y, w, h):
    c.rect(x, y, w, h, NIGHT)
    stars(c, x, y, w, h // 2, 14, 99)
    # neon skyline
    for bx, bw, bh in [(x + 4, 20, 26), (x + 28, 16, 36), (x + 48, 24, 30),
                       (x + 76, 18, 40), (x + 98, 22, 28), (x + 124, 18, 34),
                       (x + 146, 24, 30), (x + 174, 18, 26)]:
        building(c, bx, y + h // 2 - bh + 22, bw, bh, NIGHT2, lit=70, seed=bx + 3)
    # track
    c.rect(x, y + h - 34, w, 34, bytes((40, 40, 48)))
    c.hline(x, y + h - 18, w, bytes((255, 215, 0)))
    for dx in range(x + 6, x + w, 18):
        c.rect(dx, y + h - 19, 9, 2, WHITE)
    # race car
    cx, cy = x + w // 2 - 30, y + h - 40
    c.rect(cx, cy + 6, 62, 10, RED)
    c.rect(cx + 18, cy, 24, 8, RED_D)
    c.rect(cx + 44, cy + 2, 18, 6, INK)
    c.rect(cx - 6, cy + 8, 8, 6, INK)
    c.circle(cx + 12, cy + 18, 5, INK)
    c.circle(cx + 12, cy + 18, 2, GREY)
    c.circle(cx + 50, cy + 18, 5, INK)
    c.circle(cx + 50, cy + 18, 2, GREY)
    # checkered flag
    fx, fy = x + w - 34, y + 8
    for r in range(3):
        for cc in range(4):
            if (r + cc) % 2 == 0:
                c.rect(fx + cc * 6, fy + r * 6, 6, 6, INK)
            else:
                c.rect(fx + cc * 6, fy + r * 6, 6, 6, WHITE)
    c.line(fx, fy, fx - 2, fy + 24, INK)


def scene_cricket(c, x, y, w, h):
    c.rect(x, y, w, h, SKY)
    c.circle(x + w - 24, y + 16, 11, SUN)
    # stands
    c.rect(x, y + 26, w, 16, bytes((120, 40, 40)))
    for dx in range(x + 6, x + w - 6, 10):
        c.circle(dx, y + 34, 2, CREAM)
    # outfield + pitch
    c.rect(x, y + 42, w, h - 42, bytes((70, 140, 70)))
    c.rect(x + w // 2 - 16, y + 42, 32, h - 42, bytes((205, 180, 130)))
    # stumps
    for dx in (x + w // 2 - 6, x + w // 2, x + w // 2 + 6):
        c.vline(dx, y + 50, 12, FLAME2)
    c.hline(x + w // 2 - 6, y + 50, 13, FLAME2)
    # batsman
    bx, by = x + w // 2 - 26, y + 62
    c.circle(bx, by - 8, 4, bytes((198, 150, 110)))
    c.line(bx, by - 4, bx, by + 8, WHITE)
    c.line(bx, by - 2, bx - 8, by + 4, WHITE)
    c.line(bx, by + 8, bx - 5, by + 18, NAVY)
    c.line(bx, by + 8, bx + 5, by + 18, NAVY)
    c.line(bx - 8, by + 4, bx - 14, by + 12, WOOD)
    # ball
    c.circle(x + w // 2 + 22, y + 74, 3, RED)


def scene_sparta(c, x, y, w, h):
    c.rect(x, y, w, h // 2 + 6, SKY)
    c.circle(x + w - 26, y + 16, 11, SUN)
    # sea
    c.rect(x, y + h // 2 + 6, w, h - h // 2 - 6, SEA)
    for dx in range(x + 4, x + w, 26):
        c.line(dx, y + h - 14, dx + 12, y + h - 14, WHITE)
    # ship hull
    hx, hy = x + 14, y + h // 2 + 6
    c.poly([(hx, hy), (hx + w - 28, hy), (hx + w - 44, hy + 22),
            (hx + 8, hy + 22)], bytes((40, 40, 48)))
    c.rect(hx + 6, hy - 22, 30, 22, WHITE)
    c.rect(hx + 6, hy - 22, 30, 4, RED)
    # containers
    cols = [RED, BLUE, GREEN_L, GOLD, ORANGE]
    for i in range(5):
        c.rect(hx + 44 + i * 26, hy - 18, 24, 18, cols[i])
    flame(c, hx + 70, hy - 18, 22)
    flame(c, hx + 122, hy - 18, 16)
    smoke(c, hx + 96, hy - 44, 8)
    # water cannon spray from a small boat
    c.rect(x + w - 34, y + h - 22, 26, 8, WHITE)
    c.line(x + w - 34, y + h - 22, hx + 130, hy - 30, WHITE)
    c.line(x + w - 30, y + h - 22, hx + 118, hy - 26, WHITE)


def scene_cikande(c, x, y, w, h):
    c.rect(x, y, w, h, bytes((60, 50, 60)))
    smoke(c, x + w // 2, y + 12, 10)
    smoke(c, x + w // 2 + 26, y + 8, 8)
    # factory
    c.rect(x + 12, y + h - 46, w - 24, 46, bytes((110, 100, 100)))
    c.rect(x + 12, y + h - 46, w - 24, 4, INK)
    for dx in range(x + 20, x + w - 16, 14):
        c.rect(dx, y + h - 38, 8, 10, FLAME2 if dx % 28 else bytes((60, 50, 60)))
    flame(c, x + w // 2 - 20, y + h - 46, 26)
    flame(c, x + w // 2 + 24, y + h - 46, 20)
    c.rect(x, y + h - 6, w, 6, INK)


def scene_nigeria(c, x, y, w, h):
    c.rect(x, y, w, h // 2, SKY)
    c.circle(x + w - 24, y + 14, 10, SUN)
    c.rect(x, y + h // 2, w, h - h // 2, SEA)
    for dx in range(x + 2, x + w, 22):
        c.line(dx, y + h - 12, dx + 10, y + h - 12, WHITE)
        c.line(dx + 4, y + h - 6, dx + 14, y + h - 6, WHITE)
    # capsized boat: hull upside down
    bx, by = x + w // 2 - 34, y + h // 2 + 8
    c.poly([(bx, by), (bx + 68, by), (bx + 58, by + 10), (bx + 10, by + 10)],
           bytes((90, 60, 30)))
    c.rect(bx + 20, by - 6, 28, 6, bytes((90, 60, 30)))
    # people in water
    for dx in (x + 24, x + w - 30, x + w // 2 + 44):
        c.circle(dx, y + h - 18, 4, bytes((198, 150, 110)))
        c.rect(dx - 5, y + h - 16, 10, 4, ORANGE)
    # lifebuoy
    c.ring(x + 22, y + h // 2 + 4, 6, WHITE, 2)
    c.rect(x + 16, y + h // 2 + 2, 3, 3, RED)
    c.rect(x + 25, y + h // 2 + 2, 3, 3, RED)


def scene_pope(c, x, y, w, h):
    c.rect(x, y, w, h, bytes((240, 220, 180)))
    # dome arc
    c.ellipse(x + w // 2, y + 6, w // 2 - 6, 18, bytes((200, 170, 110)))
    c.rect(x, y + 6, w, 4, bytes((200, 170, 110)))
    # long table
    c.rect(x + 8, y + h - 30, w - 16, 10, WHITE)
    c.rect(x + 8, y + h - 20, w - 16, 4, WOOD)
    for dx in range(x + 18, x + w - 10, 22):
        c.circle(dx, y + h - 32, 3, WHITE)
    # guests: heads along the table
    for i in range(6):
        dx = x + 22 + i * (w - 44) // 5
        c.circle(dx, y + h - 44, 6, bytes((198, 150, 110)) if i % 2 == 0 else bytes((90, 70, 50)))
        c.rect(dx - 8, y + h - 39, 16, 9, NAVY if i % 2 else TEAL)
    # pope in white at centre
    c.circle(x + w // 2, y + h - 52, 6, bytes((230, 200, 170)))
    c.rect(x + w // 2 - 9, y + h - 47, 18, 17, WHITE)
    c.rect(x + w // 2 - 9, y + h - 47, 18, 3, GOLD)


def scene_bepi(c, x, y, w, h):
    c.rect(x, y, w, h, NIGHT)
    stars(c, x, y, w, h, 20, 555)
    # sun rays corner
    for i in range(5):
        c.line(x + w - 4, y + 2 + i * 4, x + w - 22, y + 10 + i * 4, FLAME2)
    # Mercury
    mx, my = x + w // 2 - 8, y + h // 2 + 8
    c.circle(mx, my, 26, bytes((180, 150, 120)))
    c.circle(mx - 8, my - 6, 5, bytes((150, 120, 95)))
    c.circle(mx + 8, my + 4, 4, bytes((150, 120, 95)))
    c.circle(mx + 2, my - 12, 3, bytes((200, 175, 145)))
    c.circle(mx - 12, my + 10, 3, bytes((150, 120, 95)))
    # spacecraft with panels
    sx, sy = x + 22, y + 12
    c.rect(sx, sy, 12, 8, WHITE)
    c.rect(sx - 12, sy + 2, 10, 4, BLUE)
    c.rect(sx + 14, sy + 2, 10, 4, BLUE)
    c.line(sx + 6, sy, sx + 6, sy - 6, WHITE)
    c.circle(sx + 6, sy - 7, 2, FLAME2)
    # orbit arc
    c.ring(mx, my, 34, GREY, 1)


def scene_iranpower(c, x, y, w, h):
    c.rect(x, y, w, h, NIGHT)
    stars(c, x, y, w, h // 2, 8, 77)
    for bx, bw, bh in [(x + 4, 24, 34), (x + 32, 20, 48), (x + 56, 28, 40),
                       (x + 88, 22, 54), (x + 114, 26, 44), (x + 144, 20, 36),
                       (x + 168, 22, 30)]:
        building(c, bx, y + h - bh - 6, bw, bh, NIGHT2, lit=12, seed=bx + 11)
    # one lit window + lightning bolt
    c.rect(x + 92, y + h - 40, 4, 5, SUN)
    bolt = [(x + w - 40, y + 6), (x + w - 30, y + 6), (x + w - 38, y + 20),
            (x + w - 28, y + 20), (x + w - 42, y + 40), (x + w - 34, y + 40),
            (x + w - 40, y + 26), (x + w - 48, y + 26)]
    c.poly(bolt, FLAME2)
    c.rect(x, y + h - 6, w, 6, NAVY2)


def scene_wemby(c, x, y, w, h):
    c.rect(x, y, w, h, bytes((210, 150, 70)))
    c.rect(x, y + h - 26, w, 26, bytes((190, 120, 50)))
    c.ellipse(x + w // 2, y + h - 12, 60, 8, WHITE)
    # hoop
    hx = x + w - 30
    c.rect(hx, y + 10, 4, 30, INK)
    c.rect(hx - 14, y + 10, 16, 12, WHITE)
    c.rect(hx - 14, y + 10, 16, 2, RED)
    c.ellipse(hx - 6, y + 26, 8, 3, ORANGE)
    # player jumping
    px, py = x + w // 2 - 6, y + h - 52
    c.circle(px, py - 10, 5, bytes((120, 80, 50)))
    c.line(px, py - 5, px, py + 10, bytes((10, 30, 90)))
    c.line(px, py - 2, px - 12, py - 12, bytes((10, 30, 90)))
    c.line(px, py + 10, px - 8, py + 24, bytes((10, 30, 90)))
    c.line(px, py + 10, px + 8, py + 22, bytes((10, 30, 90)))
    # ball in hand
    c.circle(px - 14, py - 14, 5, ORANGE)
    c.line(px - 14, py - 19, px - 14, py - 9, INK)
    c.line(px - 19, py - 14, px - 9, py - 14, INK)


def scene_bolsonaro(c, x, y, w, h):
    c.rect(x, y, w, h, bytes((225, 235, 240)))
    # wall cross
    c.rect(x + w - 30, y + 8, 16, 16, WHITE)
    c.rect(x + w - 26, y + 10, 8, 12, RED)
    c.rect(x + w - 29, y + 13, 14, 4, RED)
    # bed
    c.rect(x + 10, y + h - 34, w - 20, 8, WHITE)
    c.rect(x + 10, y + h - 26, 6, 20, INK)
    c.rect(x + w - 16, y + h - 26, 6, 20, INK)
    c.rect(x + 12, y + h - 42, 22, 8, CREAM)
    # patient
    c.circle(x + 24, y + h - 44, 5, bytes((198, 150, 110)))
    c.rect(x + 30, y + h - 42, 44, 8, TEAL)
    # monitor with ECG line
    c.rect(x + w // 2 - 6, y + 6, 44, 26, INK)
    c.rect(x + w // 2 - 4, y + 8, 40, 22, bytes((10, 40, 20)))
    pts = [(x + w // 2 - 2, y + 22), (x + w // 2 + 8, y + 22),
           (x + w // 2 + 12, y + 14), (x + w // 2 + 16, y + 26),
           (x + w // 2 + 20, y + 22), (x + w // 2 + 34, y + 22)]
    for i in range(len(pts) - 1):
        c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], GREEN_L)


def scene_fbi(c, x, y, w, h):
    c.rect(x, y, w, h, NIGHT2)
    # server racks
    for rx in (x + 8, x + w // 2 - 14, x + w - 44):
        c.rect(rx, y + 8, 30, h - 16, bytes((50, 60, 90)))
        for ry in range(y + 12, y + h - 10, 9):
            c.rect(rx + 4, ry, 8, 3, GREEN_L if (ry // 9) % 2 else RED)
            c.rect(rx + 16, ry, 10, 3, GREY)
    # magnifier
    mx, my = x + w // 2, y + h // 2
    c.ring(mx, my, 14, WHITE, 2)
    c.line(mx + 10, my + 10, mx + 22, my + 22, WHITE)
    c.line(mx + 8, my + 8, mx + 20, my + 20, WHITE)


def scene_belgian(c, x, y, w, h):
    c.rect(x, y, w, h, SKY)
    c.circle(x + 22, y + 14, 10, SUN)
    # control tower
    c.rect(x + 16, y + 14, 12, h - 14, GREY)
    c.rect(x + 10, y + 8, 24, 12, NAVY)
    c.rect(x + 13, y + 11, 18, 5, SKY_D)
    # runway
    c.rect(x, y + h - 12, w, 12, bytes((60, 60, 66)))
    for dx in range(x + 6, x + w, 16):
        c.rect(dx, y + h - 7, 8, 2, WHITE)
    # grounded plane
    px, py = x + w // 2 - 10, y + h - 34
    c.ellipse(px + 30, py + 6, 32, 6, WHITE)
    c.tri(px + 56, py + 6, px + 66, py - 6, px + 66, py + 6, WHITE)
    c.tri(px + 10, py + 6, px + 22, py - 10, px + 26, py + 6, WHITE)
    c.rect(px + 26, py + 12, 4, 6, INK)
    c.rect(px + 44, py + 12, 4, 6, INK)
    # picket sign
    c.rect(x + w - 30, y + h - 44, 20, 14, RED)
    c.rect(x + w - 21, y + h - 30, 2, 16, INK)


def scene_manipur(c, x, y, w, h):
    c.rect(x, y, w, h, bytes((240, 230, 210)))
    # bottles
    for bx, col in [(x + 24, GREEN), (x + 62, BROWN), (x + 100, GREEN),
                    (x + 138, BROWN)]:
        c.rect(bx, y + h - 44, 22, 44, col)
        c.rect(bx + 7, y + h - 54, 8, 12, col)
        c.rect(bx + 2, y + h - 34, 18, 8, CREAM)
    # warning triangle
    tx, ty = x + w // 2, y + 8
    c.tri(tx - 16, ty + 22, tx + 16, ty + 22, tx, ty, FLAME2)
    c.tri(tx - 11, ty + 19, tx + 11, ty + 19, tx, ty + 5, INK)
    c.text(tx - 2, ty + 8, 1, "!", FLAME2, bold=True)


def scene_gaza(c, x, y, w, h):
    c.rect(x, y, w, h, SKY)
    c.circle(x + w - 24, y + 14, 10, SUN)
    # ruined wall
    c.rect(x + 8, y + h - 40, 60, 40, bytes((170, 160, 140)))
    c.rect(x + 8, y + h - 40, 60, 6, bytes((140, 130, 110)))
    c.rect(x + 30, y + h - 52, 14, 12, bytes((170, 160, 140)))
    # aid truck
    tx, ty = x + w - 78, y + h - 34
    c.rect(tx, ty, 46, 20, WHITE)
    c.rect(tx + 46, ty + 6, 18, 14, RED)
    c.rect(tx + 50, ty + 8, 10, 6, SKY_D)
    c.circle(tx + 12, ty + 22, 5, INK)
    c.circle(tx + 52, ty + 22, 5, INK)
    # olive branch
    c.line(x + w // 2 - 6, y + 10, x + w // 2 + 20, y + 30, GREEN)
    for dx, dy in [(0, 0), (8, 8), (16, 16)]:
        c.ellipse(x + w // 2 - 6 + dx, y + 10 + dy, 5, 2, GREEN)


SCENES = {
    "cop31": scene_cop31, "drones": scene_drones, "bahrain": scene_bahrain,
    "hk": scene_hk, "f1": scene_f1, "cricket": scene_cricket,
    "sparta": scene_sparta, "cikande": scene_cikande, "nigeria": scene_nigeria,
    "pope": scene_pope, "bepi": scene_bepi, "iranpower": scene_iranpower,
    "wemby": scene_wemby, "bolsonaro": scene_bolsonaro, "fbi": scene_fbi,
    "belgian": scene_belgian, "manipur": scene_manipur, "gaza": scene_gaza,
}

# ---------------------------------------------------------------- stories
# Every story happened or was first reported on Sunday 22 November 2026,
# checked against wire reporting that day (Reuters, AP, AFP, BBC,
# The Guardian, Al Jazeera, Ukrainian Air Force, HK Govt, ESA, F1,
# Cricinfo, Vatican News). Claims are labelled CLAIM; forecasts FORECAST.

LEADS = [
    dict(num=1, scene="cop31", kicker="ANTALYA, TURKIYE \u00b7 CLIMATE",
         tag="CONFIRMED",
         head="COP31 collapses: no deal as EU rejects a text with no fossil fuels",
         body="The final text, out at dawn, dropped the $120bn adaptation "
              "target, kept a 35% power goal for 2035 and admitted 1.5C "
              "will be overshot. By evening the EU refused to endorse it. "
              "(Reuters, BBC)"),
    dict(num=2, scene="drones", kicker="KYIV REGION, UKRAINE \u00b7 WAR",
         tag="REPORTED",
         head="Russia fires 186 drones in the night; 161 are downed",
         body="72 were jet-powered; strikes hit 18 sites. A drone partly "
              "collapsed a five-storey block in Dymer, north of Kyiv: 14 "
              "people were still missing as rescuers dug through the "
              "rubble. (Ukrainian Air Force)"),
    dict(num=3, scene="bahrain", kicker="MANAMA, BAHRAIN \u00b7 IRAN",
         tag="CLAIM",
         head="Iran claims two US radars hit; Bahrain denies it",
         body="The IRGC says its missiles and drones hit Patriot radars "
              "at Al-Riffa and Awali. Bahrain says the strike hit a "
              "civilian site: a fire, two hurt, defences intercepted it. "
              "(Reuters)"),
]

# num, scene, place, beat, tag, headline (<=32 chars), body (<=60 chars)
MEDIUM = [
    (4, "hk", "HONG KONG", "ELECTION", "CONFIRMED",
     "Record turnout in Hong Kong",
     "98.79% vote; 5,640 of 5,709 ballots cast. (HK Govt)"),
    (5, "f1", "LAS VEGAS", "FORMULA 1", "CONFIRMED",
     "Verstappen wins Las Vegas GP",
     "Beats Norris by 0.639s after 35 lead changes. (F1)"),
    (6, "cricket", "WELLINGTON", "CRICKET", "CONFIRMED",
     "India's record 720/9 declared",
     "Rahul 136, Pant 128; NZ 119/2, trail by 233. (Cricinfo)"),
    (7, "sparta", "FINLAND", "SEA", "CONFIRMED",
     "Sparta II burns off Finland",
     "Struck by drones Sat; 16 crew off, tow begins. (Reuters)"),
    (8, "cikande", "CIKANDE", "FIRE", "CONFIRMED",
     "3 dead, 36 missing in fire",
     "Milkita candy plant blaze Sat; search goes on. (Reuters)"),
    (9, "nigeria", "BAYELSA", "DISASTER", "REPORTED",
     "Mourners' boat sinks; 24 dead",
     "Funeral boat capsizes Fri; toll rises Sun. (Reuters)"),
    (10, "pope", "VATICAN CITY", "FAITH", "CONFIRMED",
     "Pope hosts 1,300 poor for lunch",
     "10th World Day of the Poor, Paul VI Hall. (Vatican News)"),
    (11, "bepi", "MERCURY", "SPACE", "CONFIRMED",
     "BepiColombo orbits Mercury",
     "ESA confirms capture Sun after 8-year cruise. (ESA)"),
    (12, "iranpower", "TEHRAN", "ENERGY", "REPORTED",
     "Iran power cuts begin",
     "Up to 2 hours a day as gas output falls. (Reuters)"),
    (13, "wemby", "SAN ANTONIO", "NBA", "CONFIRMED",
     "Wembanyama scores 50",
     "50 pts, 19 rebounds as Spurs beat Pelicans 114-91. (AP)"),
    (14, "bolsonaro", "BRASILIA", "HEALTH", "CONFIRMED",
     "Bolsonaro in intensive care",
     "Bowel obstruction, stable, breathing on his own. (Reuters)"),
    (15, "fbi", "WASHINGTON", "CYBER", "REPORTED",
     "FBI probes database hack",
     "Apparent breach of gun-dealer check system probed. (AP)"),
    (16, "belgian", "BRUSSELS", "TRAVEL", "CONFIRMED",
     "Belgian flights grounded",
     "Most flights grounded 07:00-21:00 on Monday. (Reuters)"),
    (17, "manipur", "MANIPUR", "POISONING", "REPORTED",
     "Toxic-liquor toll hits 19",
     "600 in hospital, six held, toll up from Sat. (Reuters)"),
    (18, "gaza", "GAZA CITY", "CONFLICT", "REPORTED",
     "Hamas seeks urgent talks",
     "Three die in drone strike on food vehicle. (Al Jazeera)"),
]

# num, region, headline, source -- shown in two columns
ALSO = [
    (19, "EUROPE", "Denmark expels Russian attache", "Guardian"),
    (20, "EUROPE", "Estonia to shut 5 Russia crossings", "Reuters"),
    (21, "EUROPE", "Liverpool v Man City 16:30 - FORECAST", "PL"),
    (22, "EUROPE", "England beat New Zealand 27-12", "Reuters"),
    (23, "MID EAST", "Saudi downs Houthi missile", "Anadolu"),
    (24, "MID EAST", "Aoun demands Israel pullout", "Al Jazeera"),
    (25, "MID EAST", "Eisenkot invites Likud to talks", "Israel"),
    (26, "ASIA-PAC", "Nepal PM Shah lands in Delhi", "Reuters"),
    (27, "ASIA-PAC", "Chinese bomber turns back off Manila", "AP"),
    (28, "ASIA-PAC", "Snow strands about 1,500 in Japan village", "dpa"),
    (29, "ASIA-PAC", "Court: Myanmar committed genocide", "Guardian"),
    (30, "ASIA-PAC", "Seoul: AI cheating in exam", "Reuters"),
    (31, "AFRICA", "Sudan army retakes 30 towns in Kordofan", "FT"),
    (32, "AFRICA", "DR Congo cantine attack, 40 killed", "Officials"),
    (33, "AFRICA", "Kenya's last Ebola patient discharged", "Wires"),
    (34, "OCEANIA", "Marles rejects US report on AUKUS subs", "ABC"),
    (35, "OCEANIA", "Melbourne: 70 years since 1956 Games", "ABC"),
    (36, "WORLD", "Nvidia faces SEC probe", "Straits Times"),
    (37, "WORLD", "Bitcoin back above $60,000", "Reuters"),
    (38, "WORLD", "AI claims Riemann proof - REPORTED", "Guardian"),
    (39, "WORLD", "ATP Finals title match later - FORECAST", "ATP"),
]

STATS = [
    ("186", "DRONES FIRED AT UKRAINE"),
    ("161", "DOWNED OR JAMMED"),
    ("98.79%", "HONG KONG TURNOUT"),
    ("720/9", "INDIA'S RECORD TOTAL IN NZ"),
    ("50", "WEMBANYAMA POINTS"),
    ("24", "DEAD, NIGERIA FUNERAL BOAT"),
]

REGIONS = [
    ("EUROPE 8", BLUE), ("MIDDLE EAST 6", RED), ("ASIA-PACIFIC 8", TEAL),
    ("AMERICAS 4", ORANGE), ("AFRICA 4", GREEN), ("OCEANIA 3", PURPLE),
    ("WORLD 6", GREY),
]

UTC_ITEMS = [
    "03:00 COP31 objections due",
    "05:30 Verstappen wins",
    "06:00 161 drones downed",
    "13:00 Pope's lunch",
    "18:00 HK turnout 98.79%",
    "EVENING No deal at COP31",
]

DATE_CHECK = (
    "Left out as other days' news: the 400-drone, 110-missile barrage "
    "(Thu 19-Fri 20 Nov) \u00b7 the Kryvyi Rih double-tap (Fri 20-Sat 21) "
    "\u00b7 'El Chapo Isidro' captured (Fri) \u00b7 Peru quake, M6.7 "
    "(Fri 20 Nov) \u00b7 Nigeria boat capsized Fri, toll reported Sat "
    "\u00b7 Sparta II struck Sat \u00b7 Cikande fire Sat evening "
    "\u00b7 BepiColombo burn Sat, confirmed Sun. Every story on this page "
    "happened or was first reported on Sun 22 Nov 2026, to press time "
    "20:00 UTC.")

# map pins: num -> (lon, lat); 11 is at Mercury, no pin on Earth
PINS = {
    1: (36.9, 30.7), 2: (30.5, 50.4), 3: (50.6, 26.2), 4: (114.2, 22.3),
    5: (-115.1, 36.2), 6: (174.8, -41.3), 7: (25.0, 60.0), 8: (106.3, -6.1),
    9: (6.3, 4.9), 10: (12.45, 41.9), 12: (51.4, 35.7), 13: (-98.5, 29.4),
    14: (-47.9, -15.8), 15: (-77.0, 38.9), 16: (4.35, 50.85),
    17: (94.0, 24.7), 18: (34.45, 31.5),
}

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-55, 60),
     (-60, 47), (-75, 40), (-80, 32), (-85, 26), (-97, 26), (-105, 20),
     (-110, 23), (-125, 40), (-125, 49), (-140, 60), (-165, 60)],
    # South America
    [(-80, 10), (-60, 8), (-50, 0), (-35, -8), (-40, -20), (-48, -28),
     (-58, -35), (-65, -45), (-70, -55), (-73, -40), (-73, -20), (-80, -5)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 60), (28, 62), (30, 70), (25, 71), (18, 69),
     (12, 65), (5, 60), (0, 55), (-5, 50), (-10, 44)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (32, -29),
     (25, -34), (18, -35), (15, -27), (12, -18), (9, -1), (9, 4), (-8, 5)],
    # Asia
    [(30, 70), (40, 68), (55, 68), (70, 72), (90, 75), (110, 76), (130, 72),
     (150, 70), (170, 67), (178, 65), (170, 60), (162, 58), (158, 52),
     (142, 50), (140, 40), (130, 35), (127, 38), (122, 30), (120, 22),
     (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (80, 13),
     (77, 8), (72, 20), (65, 25), (60, 25), (55, 26), (50, 29), (48, 30),
     (43, 28), (40, 36), (35, 36), (30, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
     (140, -38), (147, -39), (150, -37), (153, -27), (146, -19), (142, -11),
     (136, -12), (132, -11), (126, -14), (122, -17), (117, -20)],
]

# ---------------------------------------------------------------- layout
MX = 13
CW = W - 2 * MX  # 998


def frame(c, x, y, w, h, col, t=1):
    c.rect(x, y, w, t, col)
    c.rect(x, y + h - t, w, t, col)
    c.rect(x, y, t, h, col)
    c.rect(x + w - t, y, t, h, col)


def blit_scene(c, fn, x, y, w, h):
    """Draw scene into a 326x110 virtual canvas, scale-blit to target."""
    v = Canvas(326, 110, PAPER)
    fn(v, 0, 0, 326, 110)
    for yy in range(h):
        sy = yy * 110 // h
        for xx in range(w):
            sx = xx * 326 // w
            i = (sy * 326 + sx) * 3
            c.px(x + xx, y + yy, v.pix[i:i + 3])


def kicker_label(c, x, y, w, num, text, tag):
    """Red label strip overlaid on a scene: 'N · PLACE' + tag chip."""
    label = "%d \u00b7 %s" % (num, text)
    tagw = text_width(tag, 1) + 8
    while text_width(label, 1) + 10 + tagw > w - 2 and len(label) > 4:
        label = label[:-1]
    lw = text_width(label, 1) + 10
    c.rect(x, y, lw, 11, RED)
    c.text(x + 5, y + 2, 1, label, WHITE, bold=True)
    tag_chip(c, x + w - tagw, y, tag)


def draw_lead(c, x, y, w, lead):
    h = 222
    frame(c, x, y, w, h, INK)
    blit_scene(c, SCENES[lead["scene"]], x + 1, y + 1, w - 2, 110)
    ky = y + 115
    kick = "%d \u00b7 %s" % (lead["num"], lead["kicker"])
    c.text(x + 6, ky, 1, kick, RED, bold=True)
    tag_chip(c, x + w - 6 - (text_width(lead["tag"], 1) + 8), ky - 1,
             lead["tag"])
    hl = wrap(lead["head"], w - 12, 2)
    hy = ky + 14
    for ln in hl[:3]:
        c.text(x + 6, hy, 2, ln, INK, bold=True)
        hy += 15
    by = hy + 2
    para(c, x + 6, by, w - 12, 1, lead["body"], INK2, lh=11, maxlines=4)


def draw_medium(c, x, y, w, card):
    num, scene, place, beat, tag, head, body = card
    h = 100
    frame(c, x, y, w, h, INK)
    blit_scene(c, SCENES[scene], x + 1, y + 1, w - 2, 44)
    kicker_label(c, x + 1, y + 1, w - 2, num, place, tag)
    hl = wrap(head, w - 8, 2)
    hy = y + 48
    for ln in hl[:2]:
        c.text(x + 4, hy, 2, ln, INK, bold=True)
        hy += 14
    para(c, x + 4, y + 78, w - 8, 1, body, INK2, lh=10, maxlines=2)


NUDGE = {1: (-10, -10), 18: (10, 8), 3: (8, -8), 12: (-6, 10), 2: (8, 4),
         7: (-6, -6), 16: (-10, 4), 10: (6, 10), 17: (-8, -8), 6: (-6, 0)}


def draw_map(c, x, y, w, h):
    c.rect(x, y, w, h, bytes((205, 225, 240)))
    frame(c, x, y, w, h, INK)
    c.text(x + 6, y + 4, 1, "WHERE IT HAPPENED", INK, bold=True)
    c.text_r(x + w - 6, y + 4, 1, "pins = story numbers", INK2)
    my = y + 14
    mh = h - 14
    for cont in CONTINENTS:
        pts = []
        for lon, lat in cont:
            px = x + int((lon + 180) / 360 * w)
            py = my + int((90 - lat) / 180 * mh)
            pts.append((px, py))
        c.poly(pts, LAND)
    for num, (lon, lat) in PINS.items():
        px = x + int((lon + 180) / 360 * w)
        py = my + int((90 - lat) / 180 * mh)
        dx, dy = NUDGE.get(num, (0, 0))
        px += dx
        py += dy
        c.circle(px, py, 7, RED)
        c.ring(px, py, 7, WHITE, 1)
        ns = str(num)
        c.text(px - text_width(ns, 1) // 2, py - 3, 1, ns, WHITE, bold=True)
    c.text(x + 6, y + h - 11, 1, "11 BepiColombo at Mercury: no pin on Earth",
           INK2)


def draw_also(c, x, y, w, h):
    c.text(x, y, 1, "ALSO ON SUNDAY 22 NOVEMBER \u2014 21 MORE STORIES",
           INK, bold=True)
    c.hline(x, y + 11, w, INK)
    colw = (w - 6) // 2
    ry = y + 16
    for i, (num, region, head, src) in enumerate(ALSO):
        col = i // 11
        row = i % 11
        cx = x + col * (colw + 6)
        cy = ry + row * 14
        c.text(cx, cy, 1, str(num), RED, bold=True)
        c.text(cx + 16, cy, 1, region, INK2, bold=True)
        line = "%s (%s)" % (head, src)
        c.text(cx + 16 + text_width(region, 1) + 8, cy, 1, line, INK)


def draw():
    c = Canvas(W, H, PAPER)
    # top bar
    c.rect(0, 0, W, 24, NAVY)
    c.text(MX, 8, 2, "THE WORLD IN ONE DAY", WHITE, bold=True)
    c.text_r(W - MX, 9, 1,
             "39 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026",
             WHITE)
    # masthead
    c.text_c(W // 2, 30, 6, "Sunday 22 November 2026", INK, bold=True)
    c.hline(MX, 76, CW, INK)
    c.text_c(W // 2, 82, 2,
             "COP31 ends with no deal \u00b7 Iran claims US radars hit "
             "\u00b7 186 drones over Ukraine", RED, bold=True)
    # stats strip
    sy = 110
    cellw = CW // 6
    for i, (num, label) in enumerate(STATS):
        cx = MX + i * cellw
        c.text_c(cx + cellw // 2, sy + 4, 3, num, RED, bold=True)
        c.text_c(cx + cellw // 2, sy + 28, 1, label, INK2)
        if i:
            c.vline(cx, sy + 4, 34, GREY)
    c.hline(MX, sy + 40, CW, INK)
    # region strip
    ry = 152
    widths = [143, 143, 143, 143, 142, 142, 142]
    rx = MX
    for (label, col), wd in zip(REGIONS, widths):
        c.rect(rx, ry, wd, 14, col)
        c.text_c(rx + wd // 2, ry + 4, 1, label, WHITE, bold=True)
        rx += wd
    # UTC strip
    uy = 170
    c.rect(MX, uy, CW, 14, NAVY2)
    items = list(UTC_ITEMS)
    while items:
        s = "UTC  " + " \u00b7 ".join(items)
        if text_width(s, 1) <= CW - 8:
            break
        items.pop(len(items) // 2)
    c.text(MX + 4, uy + 4, 1, s, WHITE)
    # leads
    lx = [MX, MX + 326 + 10, MX + 2 * (326 + 10)]
    for x, lead in zip(lx, LEADS):
        draw_lead(c, x, 184, 326, lead)
    # medium cards: 3 rows x 5 cols
    for r in range(3):
        for col in range(5):
            x = MX + col * (193 + 8)
            y = 410 + r * (100 + 5)
            draw_medium(c, x, y, 193, MEDIUM[r * 5 + col])
    # bottom: map + also on
    draw_map(c, MX, 724, 288, 168)
    draw_also(c, MX + 296, 724, CW - 296, 168)
    # date check
    dy = 898
    frame(c, MX, dy, CW, 58, RED, 2)
    c.rect(MX + 2, dy + 2, text_width("DATE CHECK", 1) + 10, 12, RED)
    c.text(MX + 7, dy + 4, 1, "DATE CHECK", WHITE, bold=True)
    para(c, MX + 8, dy + 18, CW - 16, 1, DATE_CHECK, INK, lh=11, maxlines=4)
    # sources + legend
    c.text(MX, 962, 1,
           "Sources: Reuters, BBC, AP, AFP, The Guardian, Al Jazeera, "
           "Ukrainian Air Force, HK Govt, ESA, F1, Cricinfo, Vatican News. "
           "Scenes are drawn illustrations, not photographs.", INK2)
    c.text(MX, 978, 1,
           "TAGS: CONFIRMED official or 2+ outlets \u00b7 REPORTED the "
           "day's wires \u00b7 CLAIM one side's account \u00b7 FORECAST "
           "still to happen when drawn.", INK2)
    # footer
    c.rect(0, 1000, W, 24, NAVY)
    c.text(MX, 1008, 2, "THE WORLD IN ONE DAY", WHITE, bold=True)
    c.text_r(W - MX, 1009, 1, "SUNDAY 22 NOVEMBER 2026 \u00b7 ONE PAGE",
             WHITE)
    return c


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    path = os.path.join(out, "entry.png")
    c = draw()
    n = write_png(c, path)
    print("wrote %s (%d bytes)" % (path, n))


if __name__ == "__main__":
    main()
