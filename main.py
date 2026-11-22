#!/usr/bin/env python3
"""THE WORLD TODAY -- one page of world news, Sunday 22 November 2026.

Draws a classic broadsheet front page (1024x1024 PNG) with a hand-drawn
serif bitmap masthead, gradient-and-shade illustrated scenes, 39 dated
stories, a numbered world map, an ALSO ON list and a date check.
Python 3.13, standard library only. Deterministic: two runs write
identical bytes.
"""
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 231)
INK = (26, 26, 26)
INK_SOFT = (58, 54, 46)
GREY = (112, 106, 94)
RED = (163, 22, 33)
BLUE = (31, 78, 121)
GREEN = (30, 107, 52)
AMBER = (156, 107, 0)
PURPLE = (91, 45, 142)
CREAM = (255, 251, 240)
RULE = (26, 26, 26)

# ---------------------------------------------------------------- canvas
buf = bytearray(W * H * 3)
CLIP = None


def px(x, y, c):
    if CLIP is not None and not (CLIP[0] <= x < CLIP[2]
                                 and CLIP[1] <= y < CLIP[3]):
        return
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def fill(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if CLIP is not None:
        x0 = max(x0, CLIP[0])
        y0 = max(y0, CLIP[1])
        x1 = min(x1, CLIP[2])
        y1 = min(y1, CLIP[3])
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i] = c[0]
            buf[i + 1] = c[1]
            buf[i + 2] = c[2]


def rect(x, y, w, h, c, t=1):
    fill(x, y, w, t, c)
    fill(x, y + h - t, w, t, c)
    fill(x, y, t, h, c)
    fill(x + w - t, y, t, h, c)


def hline(x, y, w, c):
    fill(x, y, w, 1, c)


def vline(x, y, h, c):
    fill(x, y, 1, h, c)


def mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def vgrad(x, y, w, h, top, bottom):
    if h <= 1:
        fill(x, y, w, h, top)
        return
    for yy in range(h):
        fill(x, y + yy, w, 1, mix(top, bottom, yy / (h - 1)))


def hgrad(x, y, w, h, left, right):
    if w <= 1:
        fill(x, y, w, h, left)
        return
    for xx in range(w):
        fill(x + xx, y, 1, h, mix(left, right, xx / (w - 1)))


def disc(cx, cy, r, c):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        hline(cx - dx, cy + dy, 2 * dx + 1, c)


def ellipse(cx, cy, rx, ry, c):
    for dy in range(-ry, ry + 1):
        t = 1 - (dy * dy) / float(ry * ry)
        dx = int(rx * (t ** 0.5)) if t > 0 else 0
        hline(cx - dx, cy + dy, 2 * dx + 1, c)


def ring(cx, cy, r, c, t=2):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        hline(cx - dx, cy + dy, t, c)
        hline(cx + dx - t + 1, cy + dy, t, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def poly(points, c):
    for a, b in zip(points, points[1:]):
        line(a[0], a[1], b[0], b[1], c)


# ------------------------------------------------------- serif bitmap font
# 7 wide x 9 tall, caps + digits + punctuation. Stems carry small serif
# feet; horizontals are thin; curves are stepped. Drawn for the masthead
# and headlines, the way a newspaper sets its name in Times-like type.
SERIF = {
"A": ("...#...", "..#.#..", ".#...#.", ".#...#.", ".#####.", ".#...#.", ".#...#.", ".#...#.", "##...##"),
"B": ("####...", "#...#..", "#...#..", "####...", "#...#..", "#...#..", "#...#..", "####...", "#####.."),
"C": ("..####.", ".#....#", "#......", "#......", "#......", "#......", "#......", ".#....#", "..####."),
"D": ("####...", "#...#..", "#...#..", "#...#..", "#...#..", "#...#..", "#...#..", "#...#..", "####..."),
"E": ("#####..", "#......", "#......", "####...", "#......", "#......", "#......", "#####..", "#####.."),
"F": ("#####..", "#......", "#......", "####...", "#......", "#......", "#......", "#......", "#......"),
"G": ("..####.", ".#....#", "#......", "#......", "#..###.", "#...#..", "#...#..", ".#...#.", "..###.."),
"H": ("#...#..", "#...#..", "#...#..", "#####..", "#...#..", "#...#..", "#...#..", "#...#..", "##...##"),
"I": ("..###..", "...#...", "...#...", "...#...", "...#...", "...#...", "...#...", "...#...", "..###.."),
"J": ("....#..", "....#..", "....#..", "....#..", "....#..", "....#..", "#...#..", ".#..#..", "..##..."),
"K": ("#...#..", "#..#...", "#.#....", "##.....", "#.#....", "#..#...", "#...#..", "#...#..", "##...##"),
"L": ("#......", "#......", "#......", "#......", "#......", "#......", "#......", "#......", "#####.."),
"M": ("##...##", "#.#.#.#", "#.#.#.#", "#..#..#", "#.....#", "#.....#", "#.....#", "#.....#", "##...##"),
"N": ("#...#..", "##..#..", "##..#..", "#.#.#..", "#..##..", "#...#..", "#...#..", "#...#..", "##...##"),
"O": ("..###..", ".#...#.", "#.....#", "#.....#", "#.....#", "#.....#", "#.....#", ".#...#.", "..###.."),
"P": ("####...", "#...#..", "#...#..", "####...", "#......", "#......", "#......", "#......", "#......"),
"Q": ("..###..", ".#...#.", "#.....#", "#.....#", "#.....#", "#..#..#", "#...#.#", ".#...#.", "..##.#."),
"R": ("####...", "#...#..", "#...#..", "####...", "#.#....", "#..#...", "#...#..", "#...#..", "##...##"),
"S": ("..####.", ".#....#", "#......", ".####..", ".....#.", ".....#.", "#....#.", ".####..", "......."),
"T": ("#######", "...#...", "...#...", "...#...", "...#...", "...#...", "...#...", "...#...", "..###.."),
"U": ("#...#..", "#...#..", "#...#..", "#...#..", "#...#..", "#...#..", "#...#..", ".#...#.", "..###.."),
"V": ("#...#..", "#...#..", "#...#..", "#...#..", "#...#..", ".#.#...", ".#.#...", "..#....", "..#...."),
"W": ("#.....#", "#.....#", "#.....#", "#.....#", "#..#..#", "#.#.#.#", "#.#.#.#", "##...##", "......."),
"X": ("#...#..", ".#.#...", "..#....", "..#....", "..#....", "..#....", ".#.#...", "#...#..", "##...##"),
"Y": ("#...#..", "#...#..", ".#.#...", "..#....", "..#....", "..#....", "..#....", "..#....", "..#...."),
"Z": ("#####..", "....#..", "...#...", "..#....", "..#....", ".#.....", "#......", "#####..", "#####.."),
"0": (".......", "..###..", ".#...#.", "#...#.#", "#..#..#", "#.#...#", ".#...#.", "..###..", "......."),
"1": (".......", "...#...", "..##...", "...#...", "...#...", "...#...", "...#...", "..###..", "......."),
"2": (".......", "..###..", ".#...#.", "....#..", "...#...", "..#....", ".#.....", ".#####.", "......."),
"3": (".......", "..###..", ".#...#.", "....#..", "..##...", "....#..", ".#...#.", "..###..", "......."),
"4": (".......", "...#...", "..##...", ".#.#...", "#..#...", ".#####.", "...#...", "...#...", "......."),
"5": (".......", ".#####.", ".#.....", ".####..", "....#..", "....#..", ".#...#.", "..###..", "......."),
"6": (".......", "..###..", ".#.....", ".#.....", ".####..", ".#...#.", ".#...#.", "..###..", "......."),
"7": (".......", ".#####.", "....#..", "...#...", "...#...", "..#....", "..#....", "..#....", "......."),
"8": (".......", "..###..", ".#...#.", ".#...#.", "..###..", ".#...#.", ".#...#.", "..###..", "......."),
"9": (".......", "..###..", ".#...#.", ".#...#.", "..####.", "....#..", "....#..", "..###..", "......."),
".": (".......", ".......", ".......", ".......", ".......", ".......", ".......", "..##...", "..##..."),
",": (".......", ".......", ".......", ".......", ".......", ".......", "..##...", "..##...", "...#...", "..#...."),
":": (".......", ".......", "..##...", "..##...", ".......", "..##...", "..##...", ".......", "......."),
";": (".......", ".......", "..##...", "..##...", ".......", "..##...", "..##...", "...#...", "..#...."),
"!": (".......", "...#...", "...#...", "...#...", "...#...", "...#...", ".......", "..##...", "..##..."),
"?": (".......", "..###..", ".#...#.", "....#..", "...#...", "..#....", ".......", "..##...", "..##..."),
"'": (".......", "...#...", "...#...", "..#....", ".......", ".......", ".......", ".......", "......."),
'"': (".......", ".#.#...", ".#.#...", ".......", ".......", ".......", ".......", ".......", "......."),
"(": (".......", "....#..", "...#...", "..#....", "..#....", "..#....", "...#...", "....#..", "......."),
")": (".......", "..#....", "...#...", "....#..", "....#..", "....#..", "...#...", "..#....", "......."),
"-": (".......", ".......", ".......", ".......", ".#####.", ".......", ".......", ".......", "......."),
"\u2014": (".......", ".......", ".......", ".......", "#######", ".......", ".......", ".......", "......."),
"/": (".......", "......#", ".....#.", "....#..", "...#...", "..#....", ".#.....", "#......", "......."),
"%": (".......", ".#...#.", ".#..#..", "....#..", "...#...", "..#....", ".#..#..", "#...#..", "......."),
"&": (".......", "..#....", ".#.#...", "#...#..", ".#.#...", "..#....", ".#.#.#.", "#...#.#", ".#...#."),
"\u2022": (".......", ".......", ".......", "..###..", ".#####.", "..###..", ".......", ".......", "......."),
" ": (".......", ".......", ".......", ".......", ".......", ".......", ".......", ".......", "......."),
}

# --------------------------------------------------------- small sans font
# 5 wide x 7 tall, mixed case, for body copy, labels and captions.
SANS = {
"a": (".....", ".###.", "....#", ".####", "#...#", "#...#", ".###."),
"b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
"c": (".....", ".###.", "#...#", "#....", "#....", "#...#", ".###."),
"d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
"e": (".....", ".###.", "#...#", "#####", "#....", "#...#", ".###."),
"f": ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."),
"g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
"h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
"i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
"j": ("...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".#..."),
"k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
"l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
"m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
"n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
"o": (".....", ".###.", "#...#", "#...#", "#...#", "#...#", ".###."),
"p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
"q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
"r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
"s": (".....", ".####", "#....", ".###.", "....#", "#...#", ".###."),
"t": ("..#..", "..#..", "####.", "..#..", "..#..", "..#..", "..##."),
"u": (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".###."),
"v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
"w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
"x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
"y": (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."),
"z": (".....", ".....", "####.", "...#.", "..#..", ".#...", "####."),
"A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
"B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
"C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
"D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
"E": ("####.", "#....", "#....", "###..", "#....", "#....", "####."),
"F": ("####.", "#....", "#....", "###..", "#....", "#....", "#...."),
"G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
"H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
"I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
"J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
"K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
"L": ("#....", "#....", "#....", "#....", "#....", "#....", "####."),
"M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
"N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
"O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
"Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
"R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
"S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
"T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
"U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"V": ("#...#", "#...#", "#...#", "#...#", ".#.#.", ".#.#.", "..#.."),
"W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
"X": ("#...#", "#...#", ".#.#.", "..#..", "..#..", ".#.#.", "#...#"),
"Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
"Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
"0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
"1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
"2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
"3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
"4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
"5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
"6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
"7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
"8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
"9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
",": (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
"!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
"?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
"'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
'"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
"(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
"-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
"\u2014": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
"/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
"%": ("#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"),
"$": ("..#..", ".###.", "#.#.#", ".###.", "#.#.#", ".###.", "..#.."),
"&": (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
"\u2022": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
"+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
"=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
" ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


def _norm(ch):
    if ch in ("\u2019", "\u2018"):
        return "'"
    if ch in ("\u2013",):
        return "-"
    return ch


def glyph_w(font):
    return len(next(iter(font.values()))[0])


def text_w(text, font, scale=1):
    gw = glyph_w(font)
    return len(text) * (gw + 1) * scale - scale


def draw_char(x, y, ch, font, color, scale=1):
    g = font.get(_norm(ch))
    if g is None:
        return
    gw = len(g[0])
    for r, row in enumerate(g):
        for c in range(gw):
            if row[c] != ".":
                fill(x + c * scale, y + r * scale, scale, scale, color)


def draw_text(x, y, text, font, color, scale=1):
    gw = glyph_w(font)
    cx = x
    for ch in text:
        draw_char(cx, y, ch, font, color, scale)
        cx += (gw + 1) * scale
    return cx


def wrap(text, font, scale, max_w):
    gw = glyph_w(font)
    cw = (gw + 1) * scale
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) * cw - scale <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, text, font, color, scale, max_w, leading):
    lines = wrap(text, font, scale, max_w)
    for i, ln in enumerate(lines):
        draw_text(x, y + i * leading, ln, font, color, scale)
    return y + len(lines) * leading


# ------------------------------------------------------------ scene helpers
def sky(x, y, w, h, top, bottom):
    vgrad(x, y, w, h, top, bottom)


def glow(cx, cy, r, core, halo):
    for k in range(5, 0, -1):
        disc(cx, cy, r * k // 5, mix(halo, core, k / 5.0))
    disc(cx, cy, r // 3 + 2, core)


def buildings(x, y, w, h, base, color, lit, seed):
    # dark skyline with lit windows; seed keeps it deterministic
    bx = x
    n = 0
    while bx < x + w - 8:
        bw = 14 + (seed * 7 + n * 13) % 22
        bh = h // 3 + (seed * 11 + n * 17) % (h // 2)
        by = y + h - bh
        fill(bx, by, bw, bh, color)
        for wy in range(by + 4, y + h - 4, 9):
            for wx in range(bx + 3, bx + bw - 3, 7):
                if (wx * 7 + wy * 13 + seed) % 5 == 0:
                    fill(wx, wy, 3, 4, lit)
        bx += bw + 3
        n += 1


def hills(x, y, w, h, colors):
    # layered hills, far = lighter, near = darker
    n = len(colors)
    for i, c in enumerate(colors):
        yy = y + h * (i + 1) // (n + 1)
        ellipse(x + w // 2, yy + h // 3, w // 2 + 20, h // 3, c)


def shadow(x, y, w, c=(0, 0, 0)):
    ellipse(x + w // 2, y, w // 2, max(2, w // 14), c)


def flag(x, y, pole_c, cloth):
    vline(x, y, 22, pole_c)
    fill(x + 1, y, 16, 10, cloth)
    fill(x + 1, y + 10, 16, 2, mix(cloth, (0, 0, 0), 0.35))


# ------------------------------------------------------------------- scenes
def scene_summit(x, y, w, h):
    # COP31 plenary hall at dusk: gradient sky, low sun, flags, hall, globe
    sky(x, y, w, h, (38, 54, 96), (232, 164, 96))
    glow(x + w - 52, y + 42, 26, (255, 214, 130), (240, 150, 80))
    hills(x, y + h - 46, w, 46, [(122, 96, 110), (74, 62, 84)])
    # hall: long low building with colonnade and lit windows
    fill(x + 18, y + h - 62, w - 36, 46, (44, 40, 52))
    fill(x + 18, y + h - 62, w - 36, 4, (88, 80, 96))
    for i in range(9):
        fx = x + 30 + i * (w - 60) // 9
        fill(fx, y + h - 54, 8, 34, (255, 214, 130))
        fill(fx, y + h - 54, 8, 3, (255, 240, 200))
    # flags in front
    for i, c in enumerate([(163, 22, 33), (31, 78, 121), (30, 107, 52),
                           (232, 164, 96), (120, 60, 140)]):
        flag(x + 26 + i * 20, y + h - 84, INK, c)
    # globe on a stand at right
    disc(x + w - 44, y + h - 40, 16, (46, 110, 160))
    disc(x + w - 49, y + h - 45, 7, (90, 170, 120))
    disc(x + w - 38, y + h - 34, 4, (90, 170, 120))
    fill(x + w - 46, y + h - 24, 4, 8, (200, 170, 110))


def scene_drones(x, y, w, h):
    # Night barrage over a city: dark gradient, drone lights, glow, skyline
    sky(x, y, w, h, (10, 14, 34), (96, 52, 44))
    glow(x + w // 3, y + h - 46, 30, (255, 150, 60), (200, 90, 40))
    glow(x + 2 * w // 3, y + h - 60, 18, (255, 190, 110), (220, 110, 50))
    # drone lights with trails
    for i in range(11):
        dx = x + 12 + (i * 29) % (w - 24)
        dy = y + 10 + (i * 17) % (h // 2)
        disc(dx, dy, 2, (255, 220, 140))
        line(dx, dy, dx - 14, dy + 8, (255, 180, 100))
    buildings(x, y + h // 2, w, h // 2, y, (16, 16, 24),
              (255, 200, 110), 3)
    fill(x, y + h - 8, w, 8, (8, 8, 14))


def scene_gulf(x, y, w, h):
    # Gulf at dawn: sea gradient, warship silhouette, missile arcs, smoke
    sky(x, y, w, h * 3 // 5, (250, 200, 130), (150, 120, 110))
    glow(x + w // 4, y + 26, 20, (255, 230, 170), (240, 180, 110))
    vgrad(x, y + h * 3 // 5, w, h * 2 // 5, (52, 96, 110), (18, 44, 66))
    for i in range(4):
        wy = y + h * 3 // 5 + 8 + i * 9
        hline(x + 8 + i * 6, wy, w - 16 - i * 12, (180, 210, 220))
    # warship silhouette with shadow
    sx, sy = x + w // 5, y + h * 3 // 5 + 6
    fill(sx, sy, w // 2, 10, (30, 34, 40))
    fill(sx + 14, sy - 12, 60, 12, (30, 34, 40))
    fill(sx + 30, sy - 22, 8, 10, (30, 34, 40))
    ellipse(sx + w // 4, sy + 12, w // 4, 4, (10, 26, 40))
    # missile arcs (dotted) + smoke puffs
    for i in range(3):
        ax = x + w - 30 - i * 34
        for k in range(6):
            disc(ax - k * 6, y + 14 + k * k // 2, 2, (255, 240, 200))
    for i in range(3):
        disc(x + w - 44 - i * 26, y + 34 + i * 4, 7, (220, 220, 215))
        disc(x + w - 40 - i * 26, y + 30 + i * 4, 4, (240, 240, 235))


def scene_ballot(x, y, w, h):
    # Polling station: warm gradient, ballot box, hand, paper, flag strip
    sky(x, y, w, h, (250, 226, 190), (196, 160, 120))
    fill(x, y + h - 12, w, 12, (120, 84, 56))
    # ballot box with slot and shadow, sized to fit the art rect
    bx, by = x + w // 2 - 30, y + h - 34
    ellipse(bx + 30, by + 28, 34, 4, (90, 60, 38))
    fill(bx, by, 60, 28, (146, 74, 46))
    fill(bx, by, 60, 5, (120, 56, 34))
    fill(bx + 12, by - 2, 36, 4, INK)
    # paper going in + hand
    fill(bx + 18, by - 16, 22, 16, CREAM)
    line(bx + 22, by - 11, bx + 36, by - 11, RED)
    disc(bx + 46, by - 19, 7, (232, 190, 150))
    # small flags above
    for i, c in enumerate([(163, 22, 33), (255, 255, 255), (31, 78, 121)]):
        fill(x + 12 + i * 16, y + 8, 13, 8, c)
    disc(x + w - 22, y + 18, 8, (255, 214, 130))


def scene_ship(x, y, w, h):
    # Sparta II ablaze off Finland: cold sea, burning ship, smoke, rescue
    sky(x, y, w, h * 2 // 5, (140, 160, 180), (210, 190, 170))
    vgrad(x, y + h * 2 // 5, w, h * 3 // 5, (70, 110, 130), (24, 52, 74))
    for i in range(3):
        wy = y + h * 2 // 5 + 10 + i * 12
        hline(x + 10 + i * 8, wy, w - 20 - i * 16, (170, 200, 210))
    sx, sy = x + w // 6, y + h // 2
    fill(sx, sy, w * 2 // 3, 12, (24, 26, 32))
    fill(sx + 20, sy - 14, 40, 14, (24, 26, 32))
    fill(sx + 70, sy - 22, 10, 22, (24, 26, 32))
    # flames with layered glow
    for fx, fr in ((sx + 90, 16), (sx + 110, 12), (sx + 74, 10)):
        disc(fx, sy - 8, fr, (255, 120, 30))
        disc(fx, sy - 4, fr // 2, (255, 200, 80))
    # smoke column, kept short so it stays inside the art
    disc(sx + 100, sy - 14, 6, (120, 120, 118))
    disc(sx + 104, sy - 22, 5, (120, 120, 118))
    disc(x + w - 30, y + 20, 3, (255, 255, 255))


def scene_quake(x, y, w, h):
    # Quake: dusty sky, tilted buildings, cracks, rubble
    sky(x, y, w, h, (232, 210, 170), (190, 150, 110))
    glow(x + w - 30, y + 24, 18, (255, 220, 150), (240, 190, 120))
    # tilted buildings
    fill(x + 12, y + h - 58, 34, 58, (120, 104, 88))
    fill(x + 52, y + h - 44, 30, 44, (96, 82, 68))
    fill(x + 88, y + h - 66, 36, 66, (136, 118, 98))
    line(x + 12, y + h - 58, x + 30, y + h - 70, (90, 76, 60))
    # cracks in the ground
    poly([(x + 8, y + h - 6), (x + 40, y + h - 16), (x + 70, y + h - 8),
          (x + 110, y + h - 18), (x + 150, y + h - 6)], (70, 58, 44))
    poly([(x + 30, y + h - 16), (x + 46, y + h - 26), (x + 60, y + h - 18)],
         (70, 58, 44))
    # dust clouds + rubble
    for i in range(3):
        disc(x + 30 + i * 44, y + h - 22, 8, (210, 190, 160))
    fill(x + 60, y + h - 12, 26, 8, (96, 82, 68))
    fill(x + 96, y + h - 10, 18, 6, (120, 104, 88))


def scene_cricket(x, y, w, h):
    # Cricket: green field gradient, pitch, stumps, batsman, ball
    vgrad(x, y, w, h, (150, 200, 120), (70, 130, 70))
    ellipse(x + w // 2, y + h - 14, w // 2, 10, (52, 110, 58))
    fill(x + w // 2 - 12, y + 26, 24, h - 40, (214, 190, 150))
    fill(x + w // 2 - 12, y + 26, 24, 3, (255, 255, 255))
    # stumps
    for i in range(3):
        vline(x + w // 2 - 8 + i * 8, y + 30, 14, (240, 220, 160))
    # batsman silhouette + bat
    fill(x + w // 2 - 22, y + h - 52, 12, 26, (26, 26, 26))
    disc(x + w // 2 - 16, y + h - 58, 6, (26, 26, 26))
    line(x + w // 2 - 12, y + h - 44, x + w // 2 + 4, y + h - 26,
         (200, 170, 110))
    disc(x + w - 24, y + 22, 4, (163, 22, 33))


def scene_race(x, y, w, h):
    # Las Vegas GP at night: neon gradient, race car, speed lines, lights
    sky(x, y, w, h, (24, 16, 54), (90, 30, 90))
    for i in range(5):
        disc(x + 20 + i * 34, y + 16, 3, (255, 200, 90))
    fill(x, y + h - 34, w, 34, (40, 40, 46))
    fill(x, y + h - 34, w, 3, (255, 255, 255))
    # checkered strip
    for i in range(12):
        fill(x + i * (w // 12), y + h - 31, w // 24, 6,
             (255, 255, 255) if i % 2 == 0 else (10, 10, 10))
    # car body (low wedge) + wheels + shadow
    cx, cy = x + w // 2 - 34, y + h - 58
    ellipse(cx + 34, cy + 22, 40, 5, (0, 0, 0))
    poly([(cx, cy + 14), (cx + 8, cy), (cx + 52, cy), (cx + 68, cy + 14)],
         (200, 30, 40))
    fill(cx + 2, cy + 6, 66, 9, (200, 30, 40))
    fill(cx + 14, cy - 2, 30, 8, (30, 30, 40))
    disc(cx + 14, cy + 15, 7, (12, 12, 12))
    disc(cx + 54, cy + 15, 7, (12, 12, 12))
    disc(cx + 14, cy + 15, 3, (180, 180, 190))
    disc(cx + 54, cy + 15, 3, (180, 180, 190))
    for i in range(3):
        hline(x + 8, cy + 2 + i * 5, 22, (255, 220, 120))


def scene_arrest(x, y, w, h):
    # Arrest: street at dusk, police car, light bar, handcuffs
    sky(x, y, w, h, (90, 80, 110), (220, 170, 120))
    fill(x, y + h - 26, w, 26, (60, 58, 54))
    buildings(x, y + 8, w, h // 2, y, (52, 48, 56), (255, 200, 110), 7)
    cx, cy = x + w // 2 - 40, y + h - 52
    ellipse(cx + 40, cy + 20, 44, 5, (0, 0, 0))
    fill(cx, cy + 6, 80, 12, (20, 30, 60))
    fill(cx + 12, cy - 4, 44, 10, (20, 30, 60))
    fill(cx + 30, cy - 12, 20, 4, (200, 40, 40))
    fill(cx + 50, cy - 12, 20, 4, (40, 80, 220))
    disc(cx + 16, cy + 18, 7, (12, 12, 12))
    disc(cx + 64, cy + 18, 7, (12, 12, 12))
    ring(x + w - 30, y + 22, 8, (220, 220, 220), 2)
    ring(x + w - 16, y + 30, 8, (220, 220, 220), 2)


def scene_trade(x, y, w, h):
    # Trade deal: two flags, handshake, crates, coins
    sky(x, y, w, h, (210, 228, 240), (150, 180, 200))
    # EU flag (blue + stars) and Indonesia flag (red over white)
    fill(x + 14, y + 14, 34, 22, (20, 40, 110))
    for i in range(5):
        disc(x + 22 + (i % 3) * 9, y + 20 + (i // 3) * 9, 1,
             (255, 220, 90))
    fill(x + 54, y + 14, 34, 11, (200, 30, 40))
    fill(x + 54, y + 25, 34, 11, (255, 255, 255))
    # handshake: two arms meeting
    line(x + 30, y + h - 30, x + w // 2, y + h - 52, (232, 190, 150))
    line(x + w - 30, y + h - 30, x + w // 2, y + h - 52, (210, 170, 130))
    disc(x + w // 2, y + h - 52, 8, (232, 190, 150))
    # crates + coins
    fill(x + 16, y + h - 26, 22, 18, (160, 120, 70))
    fill(x + 42, y + h - 20, 18, 12, (140, 104, 60))
    for i in range(3):
        disc(x + w - 24 - i * 12, y + h - 14, 5, (255, 214, 130))
        disc(x + w - 24 - i * 12, y + h - 14, 2, (200, 150, 60))


def scene_boat(x, y, w, h):
    # Nigeria boat: sea gradient, hull, waves, lifebuoy
    vgrad(x, y, w, h, (170, 200, 215), (30, 70, 100))
    glow(x + w - 26, y + 20, 14, (255, 230, 170), (240, 190, 120))
    for i in range(3):
        wy = y + h // 2 + 6 + i * 12
        hline(x + 8 + i * 6, wy, w - 16 - i * 12, (190, 220, 230))
    # hull + passengers + lifebuoy
    bx, by = x + w // 2 - 40, y + h // 2 + 4
    poly([(bx, by), (bx + 80, by), (bx + 70, by + 16), (bx + 10, by + 16)],
         (90, 50, 30))
    fill(bx + 4, by + 2, 72, 12, (110, 62, 36))
    for i in range(3):
        disc(bx + 18 + i * 22, by - 8, 5, (26, 26, 26))
    ring(x + 24, y + h - 24, 10, (255, 80, 40), 3)
    ring(x + 24, y + h - 24, 4, (255, 255, 255), 2)


def scene_fire(x, y, w, h):
    # Factory fire: dark smoke sky, factory silhouette, flames
    sky(x, y, w, h, (60, 52, 48), (180, 120, 70))
    for i in range(4):
        disc(x + 30 + i * 40, y + 14 + (i % 2) * 8, 10, (90, 84, 78))
    # factory + stacks
    fill(x + 10, y + h - 46, w - 20, 34, (36, 32, 30))
    fill(x + 20, y + h - 66, 10, 22, (36, 32, 30))
    fill(x + w - 34, y + h - 72, 10, 28, (36, 32, 30))
    for i in range(4):
        fill(x + 22 + i * 26, y + h - 38, 10, 8, (255, 200, 110))
    # flames
    for fx, fr in ((x + w // 3, 14), (x + 2 * w // 3, 11), (x + w // 2, 9)):
        disc(fx, y + h - 48, fr, (255, 120, 30))
        disc(fx, y + h - 44, fr // 2, (255, 200, 80))


def scene_market(x, y, w, h):
    # Market sell-off: pale gradient, falling chart, candlesticks
    sky(x, y, w, h, (240, 238, 230), (200, 200, 190))
    # grid
    for i in range(1, 4):
        hline(x + 6, y + i * h // 4, w - 12, (200, 198, 188))
    # candlesticks
    for i in range(6):
        cx = x + 16 + i * (w - 32) // 6
        top = y + 12 + i * 7
        fill(cx, top, 8, 22, (163, 22, 33) if i % 2 == 0 else (30, 107, 52))
        vline(cx + 4, top - 5, 32, INK_SOFT)
    # falling line + arrow
    poly([(x + 10, y + 14), (x + w // 3, y + h // 2),
          (x + 2 * w // 3, y + h - 30), (x + w - 12, y + h - 14)],
         (163, 22, 33))
    disc(x + w - 12, y + h - 14, 4, (163, 22, 33))
    disc(x + 22, y + 22, 10, (255, 214, 130))


def scene_soccer(x, y, w, h):
    # Football: green pitch gradient, goal, ball, players
    vgrad(x, y, w, h, (120, 180, 110), (50, 110, 55))
    fill(x, y + h - 20, w, 20, (44, 100, 50))
    # goal posts + net
    gx, gy = x + w // 2 - 26, y + 16
    fill(gx, gy, 52, 3, (255, 255, 255))
    fill(gx, gy, 3, 26, (255, 255, 255))
    fill(gx + 49, gy, 3, 26, (255, 255, 255))
    for i in range(4):
        hline(gx + 4, gy + 8 + i * 5, 44, (230, 230, 230))
    # ball + players
    disc(x + w // 2, y + h - 34, 7, (255, 255, 255))
    disc(x + w // 2, y + h - 34, 3, INK)
    for px_, py_, c in ((x + 24, y + h - 40, (200, 30, 40)),
                        (x + w - 30, y + h - 44, (30, 60, 180)),
                        (x + 40, y + 44, (255, 255, 255))):
        fill(px_, py_, 10, 16, c)
        disc(px_ + 5, py_ - 6, 5, (232, 190, 150))


def scene_rugby(x, y, w, h):
    # Rugby: pitch, H posts, oval ball, scrum
    vgrad(x, y, w, h, (130, 185, 115), (60, 115, 60))
    fill(x, y + h - 18, w, 18, (50, 100, 55))
    # H posts
    px_, py_ = x + w // 2 - 20, y + 12
    fill(px_, py_, 3, 40, (255, 255, 255))
    fill(px_ + 37, py_, 3, 40, (255, 255, 255))
    fill(px_, py_ + 26, 40, 3, (255, 255, 255))
    # oval ball + players
    ellipse(x + w // 2, y + h - 34, 10, 6, (150, 90, 50))
    for i in range(4):
        fill(x + 18 + i * 22, y + h - 52, 12, 18,
             (30, 60, 140) if i % 2 == 0 else (220, 220, 220))
        disc(x + 24 + i * 22, y + h - 58, 5, (232, 190, 150))


def scene_hospital(x, y, w, h):
    # Hospital: pale sky, building, red cross, ambulance
    sky(x, y, w, h, (215, 230, 240), (170, 195, 210))
    fill(x + w // 2 - 34, y + 22, 68, h - 40, (240, 240, 238))
    fill(x + w // 2 - 34, y + 22, 68, 4, (31, 78, 121))
    for r in range(3):
        for c in range(4):
            fill(x + w // 2 - 26 + c * 15, y + 34 + r * 16, 9, 10,
                 (255, 220, 130) if (r + c) % 2 == 0 else (180, 210, 225))
    # cross sign
    fill(x + w // 2 - 5, y + h - 34, 10, 26, (163, 22, 33))
    fill(x + w // 2 - 12, y + h - 27, 24, 10, (163, 22, 33))
    # ambulance dot + road
    fill(x, y + h - 14, w, 14, (70, 70, 74))
    fill(x + 16, y + h - 10, 26, 7, (255, 255, 255))
    disc(x + 22, y + h - 13, 3, (12, 12, 12))
    disc(x + 36, y + h - 13, 3, (12, 12, 12))


SCENES = {
    "summit": scene_summit, "drones": scene_drones, "gulf": scene_gulf,
    "ballot": scene_ballot, "ship": scene_ship, "quake": scene_quake,
    "cricket": scene_cricket, "race": scene_race, "arrest": scene_arrest,
    "trade": scene_trade, "boat": scene_boat, "fire": scene_fire,
    "market": scene_market, "soccer": scene_soccer, "rugby": scene_rugby,
    "hospital": scene_hospital,
}


# --------------------------------------------------------------------- data
TAG_COLORS = {"CONFIRMED": GREEN, "REPORTED": BLUE, "CLAIM": AMBER,
              "FORECAST": PURPLE}
TAG_MEANING = {"CONFIRMED": "verified by wires",
               "REPORTED": "as reported",
               "CLAIM": "one side says so",
               "FORECAST": "expected next"}

LEADS = [
    {"kicker": "CLIMATE — ANTALYA", "scene": "summit",
     "title": "COP31 ENDS WITH NO DEAL",
     "body": "Talks in Antalya stall as the plenary fails to agree a final "
             "text. No consensus on finance or fossil fuels; delegates "
             "leave with no deal.",
     "source": "COP31 plenary, Antalya", "tag": "CONFIRMED"},
    {"kicker": "WAR — UKRAINE", "scene": "drones",
     "title": "186 DRONES OVER UKRAINE",
     "body": "Russia fires 186 drones overnight; Kryvyi Rih takes 148 "
             "drones and 3 missiles. Two killed and dozens hurt; flats "
             "collapse near Kyiv.",
     "source": "Ukraine air force / wires", "tag": "REPORTED"},
    {"kicker": "GULF — BAHRAIN", "scene": "gulf",
     "title": "IRAN CLAIMS BAHRAIN STRIKES",
     "body": "Tehran says its missiles hit US bases in Bahrain. Bahrain "
             "disputes the account as Gulf capitals urge calm and watch "
             "the Strait of Hormuz.",
     "source": "IRGC / Bahrain", "tag": "CLAIM"},
]

CARDS = [
    {"scene": "ballot", "title": "HONG KONG VOTES",
     "body": "Final turnout 98.79%, a record for the city.",
     "tag": "CONFIRMED"},
    {"scene": "ship", "title": "SPARTA II ABLAZE",
     "body": "Russian ship burns off Finland; 16 crew evacuated.",
     "tag": "REPORTED"},
    {"scene": "quake", "title": "PERU QUAKE M6.7",
     "body": "One dead, 16 hurt, 152 homes damaged.",
     "tag": "CONFIRMED"},
    {"scene": "cricket", "title": "INDIA 720/9",
     "body": "Pant 128 and Rahul 136 pile up a record total.",
     "tag": "CONFIRMED"},
    {"scene": "race", "title": "VERSTAPPEN WINS VEGAS",
     "body": "Red Bull driver takes the Las Vegas Grand Prix.",
     "tag": "CONFIRMED"},
    {"scene": "arrest", "title": "EL CHAPO ISIDRO HELD",
     "body": "Drug lord arrested; 11 die in the operation.",
     "tag": "REPORTED"},
    {"scene": "trade", "title": "EU-INDONESIA DEAL",
     "body": "Trade pact covers 98.5% of goods, worth EUR 650m.",
     "tag": "REPORTED"},
    {"scene": "boat", "title": "NIGERIA BOAT DISASTER",
     "body": "Boat capsizes; 24 dead.",
     "tag": "REPORTED"},
    {"scene": "fire", "title": "CIKANDE FACTORY FIRE",
     "body": "Blaze hits a factory in Cikande, Indonesia.",
     "tag": "REPORTED"},
    {"scene": "market", "title": "WALL STREET AI SELL-OFF",
     "body": "AI shares slide as investors take profits.",
     "tag": "REPORTED"},
    {"scene": "soccer", "title": "COLUMBUS 3-0 MIAMI",
     "body": "Tapia scores twice; Miami's season ends.",
     "tag": "CONFIRMED"},
    {"scene": "soccer", "title": "LEEDS 4-1 CHELSEA",
     "body": "Leeds stun Chelsea at home.",
     "tag": "CONFIRMED"},
    {"scene": "soccer", "title": "ARSENAL 2-2 NEWCASTLE",
     "body": "Arsenal and Newcastle share four goals.",
     "tag": "CONFIRMED"},
    {"scene": "rugby", "title": "FRANCE 45-17 ARGENTINA",
     "body": "France run away with it in Paris.",
     "tag": "CONFIRMED"},
    {"scene": "hospital", "title": "BOLSONARO IN ICU",
     "body": "Brazil's ex-president in intensive care.",
     "tag": "REPORTED"},
]

ALSO_ON = [
    "Nigeria: 40 blocks",
    "Baduy forest fire",
    "Iran power cuts",
    "COP draft rejected",
    "Flats fall near Kyiv",
    "COP31 into day two",
    "Fossil fuels dropped",
    "Rescue reaches Peru",
    "No vote in plenary",
    "Sparta II crew safe",
    "Kyiv: drones downed",
    "Brent crude near $90",
    "Hormuz shipping",
    "Iran: 2 radars hit",
    "Final text tabled",
    "Hong Kong count",
    "Peru aftershocks",
    "Asia markets mixed",
    "Columbus advance",
    "Leeds climb table",
    "Delegates await draft",
]

MAP_GRID = [
    "....#####...............................########....",
    "...##########...###...............###########...",
    "..############..###.....####......############..",
    "...###########.........######....##########.....",
    "....#########..........#######....########......",
    ".....######....##......######.....######.........",
    "......####......##....########....####..........",
    ".......##.......##....#########.................",
    ".......##.......##....##########.....##.........",
    ".......##.......##.....#########....###.........",
    ".......##........#.....########.....##..........",
    "........#........#......######..................",
    "........##.......#.......####........###........",
    ".........##..............###........#####.......",
    ".........##...............##.........####.......",
    "..........#..........................##........",
    "................................................",
    "................................................",
]

MAP_PINS = [
    (0.60, 0.28, "1"), (0.57, 0.20, "2"), (0.63, 0.36, "3"),
    (0.87, 0.40, "4"), (0.22, 0.58, "5"), (0.50, 0.52, "6"),
    (0.56, 0.10, "7"), (0.75, 0.40, "8"), (0.10, 0.30, "9"),
    (0.83, 0.55, "10"),
]
MAP_KEY = ["1 ANTALYA", "2 KYIV", "3 BAHRAIN", "4 HONG KONG", "5 PERU",
           "6 NIGERIA", "7 FINLAND", "8 INDIA", "9 LAS VEGAS", "10 JAKARTA"]

STATS = ("39 STORIES  \u2022  7 REGIONS  \u2022  186 DRONES  \u2022  98.79% HK "
         "TURNOUT  \u2022  720/9 INDIA  \u2022  24 DEAD IN NIGERIA BOAT")
DATE_CHECK = ("Every story here is dated Sunday 22 November 2026. COP31 "
              "ended with no deal. Hong Kong turnout 98.79% final. Nothing "
              "here predates 13 Nov 2026.")

# -------------------------------------------------------------------- layout
MX = 22
CW = 980


def tag_chip(x, y, tag):
    c = TAG_COLORS[tag]
    w = text_w(tag, SANS, 1) + 10
    fill(x, y, w, 12, c)
    draw_text(x + 5, y + 2, tag, SANS, (255, 255, 255), 1)
    return w


def art_box(x, y, w, h, scene):
    global CLIP
    fill(x, y, w, h, PAPER)
    CLIP = (x + 2, y + 2, x + w - 2, y + h - 2)
    SCENES[scene](x + 2, y + 2, w - 4, h - 4)
    CLIP = None
    rect(x, y, w, h, INK, 2)


def draw_lead(x, y, w, s):
    art_box(x, y, w, 168, s["scene"])
    draw_text(x, y + 176, s["kicker"], SANS, RED, 1)
    draw_para(x, y + 190, s["title"], SERIF, INK, 2, w, 20)
    draw_para(x, y + 232, s["body"], SANS, INK_SOFT, 1, w, 10)
    draw_text(x, y + 266, s["source"], SANS, GREY, 1)
    tw = text_w(s["tag"], SANS, 1) + 10
    tag_chip(x + w - tw, y + 264, s["tag"])


def draw_card(x, y, w, s):
    art_box(x, y, w, 60, s["scene"])
    draw_para(x, y + 66, s["title"], SERIF, INK, 1, w, 11)
    draw_para(x, y + 90, s["body"], SANS, INK_SOFT, 1, w, 9)
    tag_chip(x, y + 110, s["tag"])


def draw_map_panel(x, y, w, h):
    rect(x, y, w, h, INK, 1)
    draw_text(x + 10, y + 8, "WHERE IT HAPPENED", SANS, INK, 1)
    mx, my = x + 10, y + 26
    cell = 7
    for r, row in enumerate(MAP_GRID):
        for c, ch in enumerate(row[:48]):
            if ch == "#":
                fill(mx + c * cell, my + r * cell, cell - 1, cell - 1,
                     (120, 140, 130))
    # pins with numbers
    mw, mh = 48 * cell, len(MAP_GRID) * cell
    for fx, fy, num in MAP_PINS:
        cx, cy = mx + int(fx * mw), my + int(fy * mh)
        disc(cx, cy, 8, RED)
        disc(cx, cy, 8, RED)
        tw = text_w(num, SANS, 1)
        draw_text(cx - tw // 2, cy - 3, num, SANS, (255, 255, 255), 1)
    # key list on the right
    kx = mx + mw + 12
    ky = my + 2
    for i, item in enumerate(MAP_KEY):
        draw_text(kx, ky + i * 12, item, SANS, INK_SOFT, 1)


def draw_also_panel(x, y, w, h):
    rect(x, y, w, h, INK, 1)
    draw_text(x + 10, y + 8, "ALSO ON — 21 MORE", SANS, INK, 1)
    hline(x + 10, y + 20, w - 20, GREY)
    col_w = (w - 20 - 8) // 2
    half = 11
    for col in range(2):
        cx = x + 10 + col * (col_w + 8)
        cy = y + 28
        for item in ALSO_ON[col * half:(col + 1) * half]:
            lines = wrap("\u2022 " + item, SANS, 1, col_w)
            for ln in lines:
                draw_text(cx, cy, ln, SANS, INK_SOFT, 1)
                cy += 9
            cy += 2


def draw_right_panel(x, y, w, h):
    rect(x, y, w, h, INK, 1)
    draw_text(x + 10, y + 8, "DATE CHECK", SANS, RED, 1)
    draw_para(x + 10, y + 22, DATE_CHECK, SANS, INK_SOFT, 1, w - 20, 9)
    ly = y + 78
    draw_text(x + 10, ly, "HOW SURE ARE WE", SANS, INK, 1)
    ly += 14
    for tag in ("CONFIRMED", "REPORTED", "CLAIM", "FORECAST"):
        tag_chip(x + 10, ly, tag)
        draw_text(x + 78, ly + 2, TAG_MEANING[tag], SANS, INK_SOFT, 1)
        ly += 17


def build_page():
    fill(0, 0, W, H, PAPER)
    # masthead: serif nameplate
    name = "THE WORLD TODAY"
    nw = text_w(name, SERIF, 5)
    draw_text((W - nw) // 2, 14, name, SERIF, INK, 5)
    hline(MX, 66, CW, RULE)
    hline(MX, 69, CW, RULE)
    date_line = "SUNDAY, 22 NOVEMBER 2026"
    dw = text_w(date_line, SERIF, 2)
    draw_text((W - dw) // 2, 76, date_line, SERIF, INK, 2)
    sub = "ONE DAY \u2014 ONE PAGE \u2014 THE WORLD IN FULL"
    sw = text_w(sub, SANS, 1)
    draw_text((W - sw) // 2, 98, sub, SANS, GREY, 1)
    hline(MX, 108, CW, RULE)
    # stats strip
    fill(MX, 114, CW, 24, INK)
    sw = text_w(STATS, SANS, 1)
    draw_text((W - sw) // 2, 122, STATS, SANS, (255, 255, 255), 1)
    # three leads
    ly = 146
    lw = 318
    for i, s in enumerate(LEADS):
        draw_lead(MX + i * (lw + 13), ly, lw, s)
    # fifteen cards: 5 x 3
    cw = 188
    for r in range(3):
        for c in range(5):
            s = CARDS[r * 5 + c]
            draw_card(MX + c * (cw + 10), 438 + r * 132, cw, s)
    # bottom band
    by = 838
    draw_map_panel(MX, by, 470, 168)
    draw_also_panel(MX + 482, by, 296, 168)
    draw_right_panel(MX + 790, by, 190, 168)
    foot = ("ALL STORIES DATED SUNDAY 22 NOVEMBER 2026  \u2022  SOURCES "
            "NAMED ON PAGE")
    fw = text_w(foot, SANS, 1)
    draw_text((W - fw) // 2, 1012, foot, SANS, GREY, 1)


# ---------------------------------------------------------------------- png
def chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return out


def encode_png():
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += buf[yy * W * 3:(yy + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    build_page()
    data = encode_png()
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)
    print("wrote %d bytes" % len(data))


if __name__ == "__main__":
    main()
