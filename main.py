#!/usr/bin/env python3
"""Sum up 22 November 2026's world news in one image.

Stdlib-only. Draws a one-page visual newspaper (1024x1024 PNG) to
MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
Deterministic: two runs write byte-identical files.
"""
import binascii
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 227)
INK = (25, 25, 25)
RED = (179, 39, 30)
BLUE = (31, 78, 121)
TEAL = (15, 118, 110)
GOLD = (201, 162, 39)
SKY = (178, 214, 235)
SKY2 = (122, 178, 214)
SEA = (28, 84, 130)
SEA2 = (18, 60, 100)
GREEN = (46, 125, 50)
GREEN2 = (27, 94, 32)
SAND = (232, 213, 165)
ORANGE = (232, 120, 30)
FLAME = (245, 176, 65)
GREY = (120, 124, 128)
DARK = (52, 58, 64)
WHITE = (255, 255, 255)
CREAM = (255, 250, 235)

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 bits, written as strings of 0/1.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap_text(s, scale, max_w):
    """Greedy word wrap; returns list of lines."""
    words = s.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x0, x1, y, c, t=1):
        self.fill_rect(x0, y, x1 - x0, t, c)

    def vline(self, x, y0, y1, c, t=1):
        self.fill_rect(x, y0, t, y1 - y0, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.fill_rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - t <= d <= r:
                    self.set(xx, yy, c)

    def polygon(self, pts, c):
        """Scanline fill for any simple polygon."""
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[j]), y, int(xs[j + 1]) - int(xs[j]) + 1, 1, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == "1":
                        self.fill_rect(cx + col * scale, y + r * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, y, s, scale, c, x0=0, x1=None):
        if x1 is None:
            x1 = self.w
        w = text_width(s, scale)
        self.text(x0 + (x1 - x0 - w) // 2, y, s, scale, c)


# ---------------------------------------------------------------- art panels
def art_cop31(cv, x, y, w, h):
    """Sun over a green globe: the climate summit."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_rect(x, y + h * 2 // 3, w, h // 3, (146, 196, 130))
    # sun with rays
    sx, sy, sr = x + w // 2, y + h // 3, 34
    for k in range(12):
        import math
        a = k * math.pi / 6
        cv.line(int(sx + (sr + 4) * math.cos(a)), int(sy + (sr + 4) * math.sin(a)),
                int(sx + (sr + 16) * math.cos(a)), int(sy + (sr + 16) * math.sin(a)),
                GOLD, 4)
    cv.circle(sx, sy, sr, (245, 200, 60))
    cv.circle(sx, sy, sr - 8, (250, 220, 110))
    # globe
    gx, gy, gr = x + w // 2, y + h * 3 // 4, 58
    cv.circle(gx, gy, gr, (64, 160, 90))
    cv.circle(gx - 18, gy - 12, 20, GREEN)
    cv.circle(gx + 20, gy + 8, 16, GREEN)
    cv.circle(gx + 6, gy - 26, 12, GREEN2)
    cv.circle(gx - 30, gy + 22, 10, GREEN2)
    cv.ring(gx, gy, gr, TEAL, 3)
    # clouds
    cv.circle(x + 52, y + 34, 14, WHITE)
    cv.circle(x + 72, y + 30, 18, WHITE)
    cv.circle(x + w - 60, y + 46, 12, WHITE)
    cv.circle(x + w - 42, y + 42, 15, WHITE)


def art_ship(cv, x, y, w, h):
    """Cargo ship ablaze on a dark sea. Everything stays inside the box."""
    cv.fill_rect(x, y, w, h, (44, 62, 86))
    sea_y = y + h // 2
    cv.fill_rect(x, sea_y, w, h - h // 2, SEA)
    cv.fill_rect(x, sea_y + 4, w, 3, (90, 140, 180))
    # hull
    hx, hy = x + w // 8, sea_y + 10
    hw, hh = w * 3 // 4, h // 5
    cv.polygon([(hx, hy), (hx + hw, hy), (hx + hw - 18, hy + hh),
                (hx + 8, hy + hh)], (70, 76, 84))
    cv.fill_rect(hx, hy - 4, hw, 4, RED)
    # containers
    ch = 22
    for i, col in enumerate(((200, 90, 40), (60, 140, 90), (210, 170, 60),
                             (90, 110, 160))):
        cv.fill_rect(hx + 14 + i * 52, hy - ch, 46, ch, col)
    # bridge
    cv.fill_rect(hx + hw - 52, hy - 40, 40, 36, WHITE)
    cv.fill_rect(hx + hw - 48, hy - 36, 32, 10, (30, 60, 90))
    # flames (short, inside the box)
    fx = hx + hw // 2
    cv.polygon([(fx - 26, hy - 18), (fx - 10, hy - 44), (fx + 2, hy - 28),
                (fx + 12, hy - 48), (fx + 28, hy - 18)], FLAME)
    cv.polygon([(fx - 14, hy - 18), (fx - 3, hy - 38), (fx + 6, hy - 26),
                (fx + 16, hy - 18)], ORANGE)
    # smoke puffs just above the flames
    cv.circle(fx - 6, y + 12, 6, (90, 90, 90))
    cv.circle(fx + 10, y + 9, 7, (110, 110, 110))
    # drones
    for dx, dy in ((x + 40, y + 12), (x + w - 56, y + 10), (x + w - 96, y + 22)):
        cv.circle(dx, dy, 4, INK)
        cv.line(dx - 10, dy, dx + 10, dy, INK, 2)
        cv.line(dx, dy - 8, dx, dy + 8, INK, 2)


def art_gulf(cv, x, y, w, h):
    """Gulf sunset skyline with jets overhead."""
    for i, col in enumerate(((250, 190, 90), (240, 150, 70), (225, 110, 55))):
        cv.fill_rect(x, y + i * h // 3, w, h // 3, col)
    cv.circle(x + w * 3 // 4, y + h // 3, 26, (255, 230, 150))
    # skyline (heights scaled to the box so nothing leaks above it)
    base = y + h
    for bx, bw, bh in ((0, 52, 46), (56, 40, 66), (100, 62, 52), (166, 34, 74),
                       (204, 58, 56), (266, 44, 68), (314, 52, 48),
                       (370, 40, 62), (414, 62, 54)):
        cv.fill_rect(x + bx, base - bh, bw, bh, (58, 38, 44))
    # dome + minaret
    cv.circle(x + 268, base - 64, 12, (58, 38, 44))
    cv.fill_rect(x + 254, base - 64, 28, 5, (58, 38, 44))
    cv.fill_rect(x + 392, base - 72, 7, 72, (58, 38, 44))
    cv.circle(x + 395, base - 73, 5, (58, 38, 44))
    # jets
    for jx, jy in ((x + 70, y + 12), (x + 150, y + 26)):
        cv.polygon([(jx, jy), (jx + 34, jy + 6), (jx, jy + 10)], INK)
        cv.polygon([(jx + 8, jy + 2), (jx + 18, jy - 8), (jx + 22, jy + 4)], INK)
    # sea glint
    cv.fill_rect(x, base - 14, w, 3, (255, 220, 140))


def art_quake(cv, x, y, w, h):
    """Andean mountains, cracked ground, shaken town."""
    cv.fill_rect(x, y, w, h, SKY2)
    cv.circle(x + w - 56, y + 30, 20, (255, 240, 180))
    cv.polygon([(x, y + h), (x + w // 3, y + h // 4), (x + w * 2 // 3, y + h)],
               (120, 130, 150))
    cv.polygon([(x + w // 3, y + h), (x + w * 2 // 3, y + h // 5),
                (x + w, y + h)], (96, 108, 130))
    cv.polygon([(x + w // 3 - 26, y + h // 4 + 26), (x + w // 3, y + h // 4),
                (x + w // 3 + 26, y + h // 4 + 26)], WHITE)
    cv.polygon([(x + w * 2 // 3 - 24, y + h // 5 + 24),
                (x + w * 2 // 3, y + h // 5),
                (x + w * 2 // 3 + 24, y + h // 5 + 24)], WHITE)
    gy = y + h * 3 // 4
    cv.fill_rect(x, gy, w, h // 4, (168, 132, 92))
    # houses
    cv.fill_rect(x + 24, gy - 26, 44, 26, (210, 190, 160))
    cv.polygon([(x + 20, gy - 26), (x + 46, gy - 44), (x + 72, gy - 26)], RED)
    cv.fill_rect(x + 84, gy - 20, 38, 20, (190, 170, 140))
    cv.polygon([(x + 80, gy - 20), (x + 103, gy - 34), (x + 126, gy - 20)], DARK)
    # cracks (short zigzags inside the ground band)
    cv.line(x + 150, gy + 3, x + 172, gy + 12, INK, 3)
    cv.line(x + 172, gy + 12, x + 158, gy + 16, INK, 3)
    cv.line(x + 210, gy + 2, x + 230, gy + 11, INK, 3)
    cv.line(x + 230, gy + 11, x + 220, gy + 16, INK, 3)
    cv.line(x + 256, gy + 4, x + 278, gy + 14, INK, 3)
    # dust
    cv.circle(x + 60, gy - 46, 8, (220, 205, 180))
    cv.circle(x + 110, gy - 40, 6, (220, 205, 180))


def art_arrest(cv, x, y, w, h):
    """City street, police car with flashing lights. Fits a short strip."""
    cv.fill_rect(x, y, w, h, SKY)
    road = y + h * 2 // 3
    cv.fill_rect(x, road, w, h - h * 2 // 3, (90, 90, 96))
    cv.fill_rect(x, road, w, 3, WHITE)
    # buildings (heights scaled to the box so nothing leaks above it)
    for bx, bw, bh in ((8, 56, 30), (72, 44, 42), (240, 52, 34), (296, 44, 28)):
        cv.fill_rect(x + bx, road - bh, bw, bh, (140, 140, 150))
        for wy in range(2):
            for wx in range(2):
                cv.fill_rect(x + bx + 8 + wx * 22, road - bh + 6 + wy * 13,
                             12, 8, (255, 240, 170))
    # police car (small, sits on the road)
    cx, cy = x + w // 2 - 80, road - 12
    cv.polygon([(cx, cy + 14), (cx + 6, cy + 4), (cx + 34, cy),
                (cx + 116, cy), (cx + 146, cy + 6), (cx + 154, cy + 14)],
               WHITE)
    cv.polygon([(cx + 38, cy + 2), (cx + 60, cy + 2), (cx + 57, cy - 12),
                (cx + 42, cy - 12)], (40, 80, 120))
    cv.polygon([(cx + 66, cy + 2), (cx + 90, cy + 2), (cx + 87, cy - 12),
                (cx + 70, cy - 12)], (40, 80, 120))
    cv.fill_rect(cx + 56, cy - 17, 12, 6, RED)
    cv.fill_rect(cx + 71, cy - 17, 12, 6, BLUE)
    cv.circle(cx + 30, cy + 15, 8, INK)
    cv.circle(cx + 30, cy + 15, 3, GREY)
    cv.circle(cx + 124, cy + 15, 8, INK)
    cv.circle(cx + 124, cy + 15, 3, GREY)
    cv.fill_rect(cx + 6, cy + 9, 142, 3, BLUE)
    # figure with hands up
    fx, fy = cx + 178, road - 2
    cv.circle(fx, fy - 22, 7, (210, 170, 130))
    cv.fill_rect(fx - 6, fy - 14, 12, 16, (30, 60, 40))
    cv.line(fx - 5, fy - 12, fx - 14, fy - 26, (30, 60, 40), 3)
    cv.line(fx + 5, fy - 12, fx + 14, fy - 26, (30, 60, 40), 3)


def art_cricket(cv, x, y, w, h):
    """Green outfield, pitch, batsman and stumps."""
    cv.fill_rect(x, y, w, h, (76, 160, 80))
    cv.fill_rect(x, y, w, h // 5, (58, 140, 66))
    cv.fill_rect(x, y + h * 4 // 5, w, h // 5, (58, 140, 66))
    # pitch
    px, py, pw, ph = x + w // 2 - 26, y + 8, 52, h - 16
    cv.fill_rect(px, py, pw, ph, SAND)
    # stumps
    for sx in (px + 12, px + 22, px + 32):
        cv.fill_rect(sx, y + 12, 4, 18, GOLD)
    for sx in (px + 12, px + 22, px + 32):
        cv.fill_rect(sx, y + h - 30, 4, 18, GOLD)
    # batsman (compact, stays inside the strip)
    bx, by = x + w // 2 + 8, y + h - 14
    cv.circle(bx, by - 40, 9, (190, 140, 100))
    cv.fill_rect(bx - 4, by - 46, 8, 5, INK)  # cap
    cv.fill_rect(bx - 9, by - 30, 18, 24, WHITE)
    cv.fill_rect(bx - 9, by - 6, 7, 20, (30, 40, 60))
    cv.fill_rect(bx + 2, by - 6, 7, 20, (30, 40, 60))
    cv.line(bx + 7, by - 26, bx + 22, by - 8, (30, 40, 60), 3)
    cv.line(bx + 22, by - 8, bx + 29, by + 6, (150, 110, 60), 5)
    # ball
    cv.circle(x + w - 34, y + h - 16, 6, RED)
    cv.circle(x + w - 34, y + h - 16, 2, WHITE)
    # boundary rope
    cv.line(x + 6, y + h // 5 + 4, x + w - 6, y + h // 5 + 4, WHITE, 2)


# ---------------------------------------------------------------- layout
def draw_panel(cv, x, y, w, h, art, kicker, headline, body, ah):
    cv.fill_rect(x, y, w, h, CREAM)
    cv.rect(x, y, w, h, INK, 2)
    art(cv, x + 2, y + 2, w - 4, ah)
    cv.hline(x, x + w, y + ah + 2, INK, 2)
    tx = x + 12
    tw = w - 24
    cy = y + ah + 12
    cv.text(tx, cy, kicker, 2, RED)
    cy += 20
    for ln in wrap_text(headline, 3, tw):
        cv.text(tx, cy, ln, 3, INK)
        cy += 25
    cy += 4
    # draw only the body lines that fit inside the panel
    max_lines = max(0, (y + h - 8 - cy) // 15)
    for ln in wrap_text(body, 2, tw)[:max_lines]:
        cv.text(tx, cy, ln, 2, INK)
        cy += 15


def main():
    cv = Canvas(W, H, PAPER)
    M = 24
    # ---- masthead
    cv.text_center(26, "THE WORLD IN ONE DAY", 5, INK)
    cv.hline(M, W - M, 74, RED, 4)
    cv.text_center(84, "SUNDAY 22 NOVEMBER 2026", 4, RED)
    cv.text_center(120, "ONE DAY. ONE IMAGE. THE WORLD'S NEWS.", 2, INK)
    cv.hline(M, W - M, 142, INK, 3)
    cv.hline(M, W - M, 148, INK, 1)

    # ---- lead story: COP31
    lx, ly, lw, lh = M, 160, W - 2 * M, 292
    cv.fill_rect(lx, ly, lw, lh, CREAM)
    cv.rect(lx, ly, lw, lh, INK, 3)
    art_cop31(cv, lx + 3, ly + 3, 372, lh - 6)
    cv.vline(lx + 378, ly, ly + lh, INK, 2)
    tx = lx + 396
    tw = W - M - tx
    cv.text(tx, ly + 16, "CLIMATE SUMMIT - ANTALYA, TURKIYE", 2, RED)
    cy = ly + 44
    for ln in ("COP31 NEARS A", "FINAL DEAL"):
        cv.text(tx, cy, ln, 4, INK)
        cy += 36
    cy += 6
    body = ("AFTER TALKS RAN PAST FRIDAY'S DEADLINE, NEGOTIATORS "
            "UNVEIL A LAST PACKAGE. DELEGATES HAVE UNTIL 03:00 GMT "
            "TO OBJECT, WITH AN APPROVAL SESSION SET FOR SUNDAY MORNING.")
    for ln in wrap_text(body, 2, tw):
        cv.text(tx, cy, ln, 2, INK)
        cy += 17
    cy += 8
    cv.hline(tx, W - M - 12, cy, RED, 2)
    cy += 10
    cv.text(tx, cy, "194 DELEGATIONS MUST AGREE.", 2, BLUE)

    # ---- row 2: Baltic + Gulf
    ry, rh = 464, 200
    draw_panel(cv, M, ry, 476, rh, art_ship, "BALTIC SEA",
               "DRONES HIT RUSSIAN SHIP",
               "THE SPARTA II IS ABLAZE IN THE GULF OF FINLAND. "
               "FINLAND TIGHTENS SECURITY; UKRAINE IS BLAMED.", 80)
    draw_panel(cv, 524, ry, 476, rh, art_gulf, "THE GULF",
               "IRAN STRIKES REPORTED",
               "TEHRAN IS REPORTED TO HAVE HIT A U.S. BASE IN KUWAIT "
               "AS TANKERS ARE ATTACKED OFF OMAN.", 80)

    # ---- row 3: Peru, Mexico, cricket
    ry3, rh3 = 676, 208
    draw_panel(cv, M, ry3, 317, rh3, art_quake, "PERU",
               "M6.8 QUAKE SHAKES ANDES",
               "LIMA RESIDENTS RUSH OUT. NO DEATHS REPORTED.", 72)
    draw_panel(cv, 353, ry3, 317, rh3, art_arrest, "MEXICO",
               "CARTEL KINGPIN SEIZED",
               "ARRESTED IN A SHOOT-OUT. 11 KILLED IN SINALOA.", 72)
    draw_panel(cv, 682, ry3, 317, rh3, art_cricket, "CRICKET - WELLINGTON",
               "INDIA'S RECORD DAY",
               "INDIA PASS 520 IN NEW ZEALAND. RAHUL 136.", 72)

    # ---- also today ticker
    ty = 896
    cv.hline(M, W - M, ty, INK, 3)
    ticker = ("ALSO TODAY:  ZELENSKY CALLS CRIMEA BRIDGE STRIKES A 'FAIR RESPONSE'  -  "
              "DENMARK ACCUSES RUSSIA OF AN ASSASSINATION PLOT  -  ESTONIA TO SHUT ITS "
              "BORDER WITH RUSSIA  -  TRUMP IN SHENZHEN FOR APEC TALKS  -  FBI PROBES A "
              "HACK OF ITS CRIME DATABASE  -  JUDGE CLEARS $7.25BN ROUNDUP PAYOUT")
    cy = ty + 10
    for ln in wrap_text(ticker, 2, W - 2 * M):
        cv.text(M, cy, ln, 2, INK)
        cy += 16
    cv.hline(M, W - M, cy + 4, INK, 3)

    # ---- footer
    cv.text_center(cy + 14, "THE WORLD'S NEWS OF SUNDAY 22 NOVEMBER 2026", 2, RED)

    # ---- encode PNG (deterministic: no time chunk)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw.extend(cv.px[yy * W * 3:(yy + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b"")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(png)
    print("wrote", os.path.join(outdir, "entry.png"), len(png), "bytes")


if __name__ == "__main__":
    main()
