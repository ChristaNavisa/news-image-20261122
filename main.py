#!/usr/bin/env python3
"""News image 22 November 2026 r5.

Genre: ONE-DAY TIMELINE infographic (not a newspaper front page).
A dark night-sky canvas, a sun arc from moon to sun across the header,
and the day told as six chapters -- NIGHT, DAWN, MORNING, MIDDAY,
AFTERNOON, EVENING -- each a row of six pictogram-led story cells joined
by a timeline spine that snakes left-to-right, then right-to-left.

36 dated stories, 7 regions. Pure Python 3.13 stdlib: own PNG encoder,
own 5x7 bitmap font, all pictograms drawn from primitives.
Deterministic: no time, no randomness without a fixed seed, so two runs
write byte-identical files.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""
import os
import struct
import zlib
from math import cos, pi, sin, sqrt

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
INK = bytes((245, 241, 230))          # warm white text
MUTED = bytes((170, 180, 208))        # secondary text
GOLD = bytes((242, 193, 78))          # header accent
DARK = bytes((13, 18, 38))            # darkest tone (slots, keyholes)
BG_TOP = (11, 16, 48)
BG_MID = (16, 26, 62)
BG_BOT = (13, 20, 40)

REGION = {
    "CLIMATE": bytes((62, 207, 142)),
    "UKRAINE WAR": bytes((255, 90, 90)),
    "EUROPE": bytes((91, 141, 239)),
    "MIDDLE EAST": bytes((242, 153, 74)),
    "AMERICAS": bytes((187, 107, 217)),
    "ASIA-PACIFIC": bytes((242, 201, 76)),
    "SPORT": bytes((86, 204, 242)),
}
REGION_ORDER = ["CLIMATE", "UKRAINE WAR", "EUROPE", "MIDDLE EAST",
                "AMERICAS", "ASIA-PACIFIC", "SPORT"]

BANDS = [
    ("NIGHT", bytes((126, 141, 176))),
    ("DAWN", bytes((242, 153, 74))),
    ("MORNING", bytes((242, 201, 76))),
    ("MIDDAY", bytes((86, 204, 242))),
    ("AFTERNOON", bytes((62, 207, 142))),
    ("EVENING", bytes((187, 107, 217))),
]

# ---------------------------------------------------------------- stories
# (line1, line2, sub-line, region, icon) -- 6 per day-part, 36 total.
# Every story was reported on Sunday 22 November 2026.
STORIES = [
    # NIGHT
    ("186 DRONES", "HIT UKRAINE", "161 downed or jammed", "UKRAINE WAR", "drone"),
    ("KYIV FLAT", "14 TRAPPED", "apartment block hit", "UKRAINE WAR", "building"),
    ("SPARTA II", "ABLAZE", "crew evacuated, adrift", "UKRAINE WAR", "ship"),
    ("SUMY: 9", "INJURED", "22 settlements struck", "UKRAINE WAR", "explosion"),
    ("KRYVYI RIH", "2 DEAD", "60+ hurt, hospital hit", "UKRAINE WAR", "missile"),
    ("COP31 DRAFT", "AT DAWN", "no fossil fuels yet", "CLIMATE", "document"),
    # DAWN
    ("DEAL OR", "NO DEAL", "double overtime", "CLIMATE", "globe"),
    ("WARMING TO", "PASS 1.5C", "draft concedes 1.5C", "CLIMATE", "sun"),
    ("MISSILES IN", "POLAND", "NATO: every inch", "EUROPE", "shield"),
    ("LVIV MISSILE", "ON CAMERA", "dashcam catches strike", "UKRAINE WAR", "explosion"),
    ("KRASNODAR", "HIT", "guard base struck", "UKRAINE WAR", "drone"),
    ("KALININGRAD", "ALERT", "alert, airport shut", "EUROPE", "radar"),
    # MORNING
    ("IRAN HITS", "BAHRAIN", "plant hit, none hurt", "MIDDLE EAST", "flame"),
    ("PATRIOT", "RADARS HIT", "IRGC claims US bases", "MIDDLE EAST", "radar"),
    ("HONG KONG", "VOTES", "856 vie for 723 seats", "ASIA-PACIFIC", "ballot"),
    ("AEON CREDIT", "HACKED", "after 2-day outage", "ASIA-PACIFIC", "lock"),
    ("DENMARK", "FOILS PLOT", "Russia assassin plot", "EUROPE", "shield"),
    ("EL CHAPO", "ISIDRO HELD", "FBI fugitive seized", "AMERICAS", "handcuffs"),
    # MIDDAY
    ("HK TURNOUT", "89.8%", "polls open 9am-6pm", "ASIA-PACIFIC", "ballot"),
    ("HANG SENG", "SINKS 500", "18-month low", "ASIA-PACIFIC", "chart"),
    ("HK VISITORS", "+12%", "up in first 10 months", "ASIA-PACIFIC", "plane"),
    ("COP31", "PROTESTS", "crowds want fossil text", "CLIMATE", "megaphone"),
    ("TANKER", "ALERTS", "warnings near Hormuz", "MIDDLE EAST", "ship"),
    ("UK BUILDS", "KYIV DRONES", "drones built in UK", "EUROPE", "drone"),
    # AFTERNOON
    ("ROBOT TALKS", "STALL", "Geneva: rules by 2028", "EUROPE", "robot"),
    ("WHITE HOUSE", "GAG ORDER", "ask White House first", "AMERICAS", "document"),
    ("ICE ARREST", "AT AIRPORT", "2 held in Seattle", "AMERICAS", "plane"),
    ("MEASLES", "DEATH IN VA", "5,838 US cases in 2026", "AMERICAS", "virus"),
    ("HK CAR", "KILLS 1", "pavement crash, 3 hurt", "ASIA-PACIFIC", "car"),
    ("OMART", "QUEUES", "6 floors of queues", "ASIA-PACIFIC", "building"),
    # EVENING
    ("ALCARAZ IN", "ATP FINAL", "beats Shelton in Turin", "SPORT", "trophy"),
    ("LAKSHYA", "STREAK ENDS", "13 wins halted", "SPORT", "tennis"),
    ("FONG'S", "RECORD SWIM", "charity swim record", "ASIA-PACIFIC", "swimmer"),
    ("HK OPEN", "FINALS SET", "Pearly-Thinaah in final", "SPORT", "tennis"),
    ("ITALY POLICE", "CHIEF DEAD", "De Gennaro found dead", "EUROPE", "flag"),
    ("HOUSING", "WAIT LOWEST", "10-year low in HK", "ASIA-PACIFIC", "building"),
]

# ---------------------------------------------------------------- framebuffer
fb = bytearray(W * H * 3)


def mix(a, b, t):
    """Blend two RGB bytes-tuples; t=0 -> a, t=1 -> b."""
    return bytes((int(a[0] + (b[0] - a[0]) * t),
                  int(a[1] + (b[1] - a[1]) * t),
                  int(a[2] + (b[2] - a[2]) * t)))


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        fb[i:i + 3] = c


def hline(x0, x1, y, c):
    if y < 0 or y >= H:
        return
    x0 = max(0, x0)
    x1 = min(W - 1, x1)
    if x0 > x1:
        return
    i = (y * W + x0) * 3
    fb[i:i + (x1 - x0 + 1) * 3] = c * (x1 - x0 + 1)


def vline(x, y0, y1, c):
    if x < 0 or x >= W:
        return
    y0 = max(0, y0)
    y1 = min(H - 1, y1)
    for y in range(y0, y1 + 1):
        i = (y * W + x) * 3
        fb[i:i + 3] = c


def fill_rect(x, y, w, h, c):
    if w <= 0 or h <= 0:
        return
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    row = c * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        fb[i:i + len(row)] = row


def fill_circle(cx, cy, r, c):
    if r <= 0:
        set_px(cx, cy, c)
        return
    for dy in range(-r, r + 1):
        dx = int(sqrt(r * r - dy * dy))
        hline(cx - dx, cx + dx, cy + dy, c)


def circle_outline(cx, cy, r, c, a0=0, a1=360):
    step = 4 if r > 12 else 6
    a = a0
    while a <= a1:
        rad = a * pi / 180.0
        set_px(int(round(cx + r * cos(rad))), int(round(cy + r * sin(rad))), c)
        a += step


def fill_ellipse(cx, cy, rx, ry, c):
    for dy in range(-ry, ry + 1):
        t = 1.0 - (dy * dy) / float(ry * ry)
        dx = int(rx * sqrt(max(0.0, t)))
        hline(cx - dx, cx + dx, cy + dy, c)


def ellipse_outline(cx, cy, rx, ry, c):
    for a in range(0, 360, 5):
        rad = a * pi / 180.0
        set_px(int(round(cx + rx * cos(rad))), int(round(cy + ry * sin(rad))), c)


def line(x0, y0, x1, y1, c, w=1):
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    r = max(0, w // 2)
    for i in range(steps + 1):
        x = int(round(x0 + dx * i / steps))
        y = int(round(y0 + dy * i / steps))
        if r:
            fill_circle(x, y, r, c)
        else:
            set_px(x, y, c)


def fill_triangle(x0, y0, x1, y1, x2, y2, c):
    fill_poly([(x0, y0), (x1, y1), (x2, y2)], c)


def fill_poly(pts, c):
    ys = [p[1] for p in pts]
    n = len(pts)
    for y in range(min(ys), max(ys) + 1):
        xs = []
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / float(y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        if len(xs) >= 2:
            xs.sort()
            hline(int(xs[0]), int(xs[-1]), y, c)


def round_rect(x, y, w, h, r, c):
    fill_rect(x + r, y, w - 2 * r, h, c)
    fill_rect(x, y + r, w, h - 2 * r, c)
    for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                   (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
        fill_circle(cx, cy, r, c)


# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows, 5 bits each, MSB = leftmost pixel.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x1F, 0, 0, 0),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    "\u00b7": (0, 0, 0x0C, 0x0C, 0, 0, 0),   # middle dot
    "\u2014": (0, 0, 0, 0x1F, 0, 0, 0),      # em dash
    "\u2019": (0x04, 0x04, 0x08, 0, 0, 0, 0),  # right quote -> apostrophe
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_glyph(x, y, g, scale, c):
    for r in range(7):
        bits = g[r]
        if not bits:
            continue
        y0 = int(y + r * scale)
        y1 = int(y + (r + 1) * scale)
        if y1 <= y0:
            y1 = y0 + 1
        for col in range(5):
            if bits >> (4 - col) & 1:
                x0 = int(x + col * scale)
                x1 = int(x + (col + 1) * scale)
                if x1 <= x0:
                    x1 = x0 + 1
                fill_rect(x0, y0, x1 - x0, y1 - y0, c)


def draw_text(x, y, s, scale, c, align="left"):
    s = s.upper()
    w = text_w(s, scale)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    for i, ch in enumerate(s):
        g = FONT.get(ch)
        if g:
            draw_glyph(x + i * 6 * scale, y, g, scale, c)


def draw_text_v(cx, cy, s, scale, c):
    """Vertical label, reading bottom-to-top (letter tops point left)."""
    s = s.upper()
    n = len(s)
    total = n * 6 * scale - scale
    y_top = cy - total / 2
    for i, ch in enumerate(s):
        g = FONT.get(ch)
        if not g:
            continue
        slot_top = y_top + (n - 1 - i) * 6 * scale
        for r in range(7):
            bits = g[r]
            if not bits:
                continue
            for col in range(5):
                if bits >> (4 - col) & 1:
                    x0 = int(cx + (r - 3) * scale)
                    x1 = int(cx + (r - 2) * scale)
                    y0 = int(slot_top + (4 - col) * scale)
                    y1 = int(slot_top + (5 - col) * scale)
                    if x1 <= x0:
                        x1 = x0 + 1
                    if y1 <= y0:
                        y1 = y0 + 1
                    fill_rect(x0, y0, x1 - x0, y1 - y0, c)


# ---------------------------------------------------------------- pictograms
# Each draws inside a ~52px box centred at (cx, cy). fg = region colour,
# ac = warm-white accent, bg = tile fill colour (for cut-outs).
def ic_drone(cx, cy, s, fg, ac, bg):
    line(cx, cy, cx - 16, cy - 16, fg, 2)
    line(cx, cy, cx + 16, cy - 16, fg, 2)
    line(cx, cy, cx - 16, cy + 16, fg, 2)
    line(cx, cy, cx + 16, cy + 16, fg, 2)
    fill_rect(cx - 8, cy - 3, 16, 6, fg)
    for dx, dy in ((-16, -16), (16, -16), (-16, 16), (16, 16)):
        circle_outline(cx + dx, cy + dy, 5, ac)
    fill_circle(cx, cy + 9, 2, ac)


def ic_flame(cx, cy, s, fg, ac, bg):
    fill_circle(cx, cy + 7, 11, fg)
    fill_triangle(cx - 11, cy + 7, cx + 11, cy + 7, cx, cy - 21, fg)
    fill_circle(cx, cy + 10, 6, ac)
    fill_triangle(cx - 6, cy + 10, cx + 6, cy + 10, cx, cy - 6, ac)


def ic_ship(cx, cy, s, fg, ac, bg):
    fill_poly([(cx - 20, cy + 4), (cx + 20, cy + 4),
               (cx + 14, cy + 17), (cx - 14, cy + 17)], fg)
    line(cx, cy + 4, cx, cy - 19, fg, 2)
    fill_triangle(cx, cy - 19, cx + 13, cy - 14, cx, cy - 9, ac)
    hline(cx - 22, cx - 8, cy + 22, ac)
    hline(cx + 2, cx + 22, cy + 22, ac)
    hline(cx - 14, cx + 14, cy + 26, ac)


def ic_missile(cx, cy, s, fg, ac, bg):
    line(cx - 13, cy + 13, cx + 11, cy - 11, fg, 5)
    fill_triangle(cx + 11, cy - 11, cx + 19, cy - 19, cx + 4, cy - 16, fg)
    fill_triangle(cx - 13, cy + 13, cx - 4, cy + 4, cx - 20, cy + 8, fg)
    fill_triangle(cx - 13, cy + 13, cx - 4, cy + 4, cx - 8, cy + 20, fg)
    fill_circle(cx - 17, cy + 17, 4, ac)
    fill_circle(cx - 20, cy + 20, 2, ac)


def ic_explosion(cx, cy, s, fg, ac, bg):
    for k in range(8):
        a = k * pi / 4
        line(cx, cy, int(cx + 19 * cos(a)), int(cy + 19 * sin(a)), fg, 3)
    fill_circle(cx, cy, 7, ac)


def ic_ballot(cx, cy, s, fg, ac, bg):
    fill_rect(cx - 4, cy - 20, 9, 15, ac)
    fill_rect(cx - 15, cy - 4, 30, 21, fg)
    fill_rect(cx - 9, cy - 4, 18, 3, DARK)
    line(cx - 11, cy + 4, cx - 4, cy + 12, ac, 3)
    line(cx - 4, cy + 12, cx + 12, cy - 8, ac, 3)


def ic_shield(cx, cy, s, fg, ac, bg):
    fill_poly([(cx - 14, cy - 18), (cx + 14, cy - 18), (cx + 14, cy + 1),
               (cx, cy + 20), (cx - 14, cy + 1)], fg)
    line(cx - 7, cy - 1, cx - 1, cy + 6, ac, 3)
    line(cx - 1, cy + 6, cx + 9, cy - 9, ac, 3)


def ic_radar(cx, cy, s, fg, ac, bg):
    circle_outline(cx, cy, 16, fg)
    circle_outline(cx, cy, 9, fg)
    line(cx, cy, cx + 12, cy - 12, ac, 2)
    fill_circle(cx, cy, 3, ac)
    fill_circle(cx - 6, cy + 7, 2, fg)
    fill_circle(cx + 7, cy + 5, 2, fg)


def ic_robot(cx, cy, s, fg, ac, bg):
    line(cx, cy - 12, cx, cy - 21, fg, 2)
    fill_circle(cx, cy - 21, 3, ac)
    fill_rect(cx - 13, cy - 12, 26, 22, fg)
    fill_rect(cx - 16, cy - 6, 3, 10, ac)
    fill_rect(cx + 13, cy - 6, 3, 10, ac)
    fill_rect(cx - 8, cy - 6, 5, 5, DARK)
    fill_rect(cx + 3, cy - 6, 5, 5, DARK)
    hline(cx - 7, cx + 7, cy + 6, DARK)


def ic_document(cx, cy, s, fg, ac, bg):
    fill_rect(cx - 11, cy - 17, 22, 34, fg)
    fill_triangle(cx + 11, cy - 17, cx + 11, cy - 8, cx + 2, cy - 17, ac)
    hline(cx - 7, cx + 7, cy - 6, DARK)
    hline(cx - 7, cx + 7, cy - 1, DARK)
    hline(cx - 7, cx + 2, cy + 4, DARK)
    fill_circle(cx + 5, cy + 11, 4, ac)


def ic_chart(cx, cy, s, fg, ac, bg):
    line(cx - 18, cy + 16, cx + 18, cy + 16, fg, 2)
    line(cx - 18, cy + 16, cx - 18, cy - 16, fg, 2)
    line(cx - 14, cy - 12, cx - 2, cy - 2, ac, 3)
    line(cx - 2, cy - 2, cx + 8, cy + 2, ac, 3)
    line(cx + 8, cy + 2, cx + 15, cy + 12, ac, 3)
    fill_triangle(cx + 15, cy + 12, cx + 9, cy + 8, cx + 17, cy + 5, ac)


def ic_plane(cx, cy, s, fg, ac, bg):
    # Slim fuselage, swept wings and tail fin: a jet in side view.
    fill_ellipse(cx, cy, 16, 5, fg)
    fill_poly([(cx - 4, cy - 1), (cx + 6, cy - 16), (cx + 12, cy - 16),
               (cx + 4, cy - 1)], fg)
    fill_poly([(cx - 15, cy - 1), (cx - 9, cy - 12), (cx - 4, cy - 12),
               (cx - 9, cy - 1)], fg)
    fill_triangle(cx + 14, cy - 2, cx + 19, cy - 3, cx + 14, cy + 3, fg)
    for dx in (-8, -1, 6):
        fill_circle(cx + dx, cy - 1, 1, ac)


def ic_car(cx, cy, s, fg, ac, bg):
    fill_poly([(cx - 10, cy - 2), (cx - 6, cy - 13), (cx + 8, cy - 13),
               (cx + 12, cy - 2)], fg)
    fill_rect(cx - 19, cy - 2, 38, 12, fg)
    fill_circle(cx - 10, cy + 12, 5, DARK)
    fill_circle(cx + 10, cy + 12, 5, DARK)
    fill_circle(cx - 10, cy + 12, 2, ac)
    fill_circle(cx + 10, cy + 12, 2, ac)


def ic_building(cx, cy, s, fg, ac, bg):
    fill_rect(cx - 14, cy - 19, 28, 38, fg)
    for gx in (-9, 0, 9):
        for gy in (-13, -4, 5):
            fill_rect(cx + gx - 3, cy + gy - 2, 6, 5, DARK)
    fill_rect(cx - 4, cy + 11, 8, 8, DARK)


def ic_trophy(cx, cy, s, fg, ac, bg):
    fill_poly([(cx - 12, cy - 17), (cx + 12, cy - 17),
               (cx + 8, cy + 1), (cx - 8, cy + 1)], fg)
    circle_outline(cx - 14, cy - 10, 5, ac)
    circle_outline(cx + 14, cy - 10, 5, ac)
    fill_rect(cx - 2, cy + 1, 4, 11, fg)
    fill_rect(cx - 11, cy + 12, 22, 5, fg)


def ic_tennis(cx, cy, s, fg, ac, bg):
    fill_circle(cx, cy, 15, fg)
    circle_outline(cx - 7, cy, 13, ac, -55, 55)
    circle_outline(cx + 7, cy, 13, ac, 125, 235)


def ic_swimmer(cx, cy, s, fg, ac, bg):
    fill_circle(cx - 7, cy - 9, 5, fg)
    line(cx - 2, cy - 4, cx + 12, cy + 2, fg, 3)
    line(cx + 1, cy - 3, cx + 14, cy - 11, fg, 3)
    hline(cx - 20, cx - 6, cy + 11, ac)
    hline(cx + 2, cx + 20, cy + 11, ac)
    hline(cx - 14, cx + 14, cy + 17, ac)


def ic_megaphone(cx, cy, s, fg, ac, bg):
    fill_poly([(cx - 14, cy - 4), (cx + 10, cy - 17), (cx + 10, cy + 9),
               (cx - 14, cy + 4)], fg)
    fill_rect(cx - 15, cy + 4, 7, 13, fg)
    circle_outline(cx + 16, cy - 4, 6, ac, -60, 60)
    circle_outline(cx + 20, cy - 4, 10, ac, -55, 55)


def ic_handcuffs(cx, cy, s, fg, ac, bg):
    circle_outline(cx - 10, cy, 8, fg)
    circle_outline(cx - 10, cy, 6, fg)
    circle_outline(cx + 10, cy, 8, fg)
    circle_outline(cx + 10, cy, 6, fg)
    line(cx - 3, cy - 6, cx + 3, cy - 6, fg, 2)
    fill_circle(cx - 10, cy, 2, ac)
    fill_circle(cx + 10, cy, 2, ac)


def ic_virus(cx, cy, s, fg, ac, bg):
    for k in range(8):
        a = k * pi / 4
        line(cx, cy, int(cx + 17 * cos(a)), int(cy + 17 * sin(a)), fg, 2)
        fill_circle(int(cx + 19 * cos(a)), int(cy + 19 * sin(a)), 2, ac)
    fill_circle(cx, cy, 9, fg)
    fill_circle(cx - 3, cy - 3, 2, DARK)
    fill_circle(cx + 3, cy + 2, 2, DARK)


def ic_lock(cx, cy, s, fg, ac, bg):
    circle_outline(cx, cy - 3, 9, fg, 180, 360)
    circle_outline(cx, cy - 3, 7, fg, 180, 360)
    fill_rect(cx - 12, cy - 3, 24, 19, fg)
    fill_circle(cx, cy + 4, 3, DARK)
    vline(cx, cy + 4, cy + 9, DARK)


def ic_globe(cx, cy, s, fg, ac, bg):
    circle_outline(cx, cy, 16, fg)
    ellipse_outline(cx, cy, 8, 16, fg)
    hline(cx - 16, cx + 16, cy, fg)
    fill_circle(cx - 5, cy - 7, 2, ac)
    fill_circle(cx + 6, cy + 6, 2, ac)


def ic_sun(cx, cy, s, fg, ac, bg):
    for k in range(8):
        a = k * pi / 4
        line(int(cx + 12 * cos(a)), int(cy + 12 * sin(a)),
             int(cx + 19 * cos(a)), int(cy + 19 * sin(a)), fg, 2)
    fill_circle(cx, cy, 9, ac)


def ic_flag(cx, cy, s, fg, ac, bg):
    line(cx - 9, cy - 19, cx - 9, cy + 19, fg, 2)
    fill_poly([(cx - 9, cy - 19), (cx + 15, cy - 14), (cx - 9, cy - 9)], fg)
    hline(cx - 14, cx - 4, cy + 19, fg)


ICONS = {
    "drone": ic_drone, "flame": ic_flame, "ship": ic_ship,
    "missile": ic_missile, "explosion": ic_explosion, "ballot": ic_ballot,
    "shield": ic_shield, "radar": ic_radar, "robot": ic_robot,
    "document": ic_document, "chart": ic_chart, "plane": ic_plane,
    "car": ic_car, "building": ic_building, "trophy": ic_trophy,
    "tennis": ic_tennis, "swimmer": ic_swimmer, "megaphone": ic_megaphone,
    "handcuffs": ic_handcuffs, "virus": ic_virus, "lock": ic_lock,
    "globe": ic_globe, "sun": ic_sun, "flag": ic_flag,
}

# ---------------------------------------------------------------- drawing
BG_DARK = bytes((13, 20, 40))


def lcg(state):
    return (state * 1103515245 + 12345) & 0x7FFFFFFF


def draw_background():
    for y in range(H):
        t = y / float(H - 1)
        if t < 0.45:
            u = t / 0.45
            c = mix(bytes(BG_TOP), bytes(BG_MID), u)
        else:
            u = (t - 0.45) / 0.55
            c = mix(bytes(BG_MID), bytes(BG_BOT), u)
        i = y * W * 3
        fb[i:i + W * 3] = c * W


def draw_stars():
    state = 12345
    for _ in range(170):
        state = lcg(state)
        x = state % W
        state = lcg(state)
        y = state % 150
        state = lcg(state)
        b = 150 + state % 106
        c = bytes((b, b, min(255, b + 20)))
        set_px(x, y, c)
        if state % 5 == 0:
            set_px(x + 1, y, c)
            set_px(x, y + 1, c)


def draw_header():
    draw_text(28, 24, "SUNDAY", 2, GOLD)
    draw_text(28, 50, "22 NOVEMBER 2026", 5, INK)
    draw_text(28, 102, "ONE DAY \u00b7 AROUND THE WORLD", 2, GOLD)
    draw_text(28, 130, "36 STORIES \u00b7 7 REGIONS \u00b7 FROM DAWN TO MIDNIGHT",
              1.5, MUTED)
    # Sun arc: moon (left) -> sun (right) across the header's right side.
    acx, acy, ar = 852, 208, 118
    for deg in range(198, 343, 3):
        rad = deg * pi / 180.0
        x = int(acx + ar * cos(rad))
        y = int(acy + ar * sin(rad))
        t = (deg - 198) / 144.0
        c = mix(bytes((200, 210, 235)), GOLD, t)
        fill_circle(x, y, 2, c)
    for k, (name, bc) in enumerate(BANDS):
        deg = 198 + k * (144.0 / 5.0)
        rad = deg * pi / 180.0
        x = int(acx + ar * cos(rad))
        y = int(acy + ar * sin(rad))
        fill_circle(x, y, 4, bc)
    # Moon at the arc's left end, sun at the right end, both on the rule.
    mx, my = 740, 172
    fill_circle(mx, my, 13, bytes((226, 232, 245)))
    fill_circle(mx + 5, my - 4, 11, bytes(BG_MID))
    sx, sy = 964, 172
    for k in range(8):
        a = k * pi / 4
        line(int(sx + 17 * cos(a)), int(sy + 17 * sin(a)),
             int(sx + 24 * cos(a)), int(sy + 24 * sin(a)), GOLD, 2)
    fill_circle(sx, sy, 14, GOLD)
    fill_circle(sx, sy, 9, bytes((255, 224, 130)))
    # Horizon rule under the header.
    hline(28, 996, 176, mix(GOLD, bytes(BG_MID), 0.55))
    hline(28, 996, 177, mix(GOLD, bytes(BG_MID), 0.75))


def draw_rows():
    y0, row_h, gap = 186, 120, 5
    x0, pitch = 112, 150
    for band_i, (band_name, band_c) in enumerate(BANDS):
        ry = y0 + band_i * (row_h + gap)
        ltr = (band_i % 2 == 0)
        # Day-part colour bar + vertical label.
        fill_rect(14, ry, 5, row_h, band_c)
        draw_text_v(62, ry + row_h // 2, band_name, 2, band_c)
        # Timeline spine through the pictogram tiles, arrow at the end.
        spine_y = ry + 33
        spine_c = mix(band_c, bytes(BG_BOT), 0.55)
        hline(x0, 1012, spine_y - 1, spine_c)
        hline(x0, 1012, spine_y, spine_c)
        hline(x0, 1012, spine_y + 1, spine_c)
        if ltr:
            fill_triangle(1014, spine_y, 1000, spine_y - 7, 1000, spine_y + 7,
                          band_c)
        else:
            fill_triangle(110, spine_y, 124, spine_y - 7, 124, spine_y + 7,
                          band_c)
        # Six story cells.
        for k in range(6):
            story = STORIES[band_i * 6 + k]
            j = k if ltr else 5 - k
            cx = x0 + j * pitch + 73
            l1, l2, sub, region, icon = story
            rc = REGION[region]
            tile = mix(rc, bytes(BG_BOT), 0.78)
            tx, ty = cx - 29, ry + 4
            round_rect(tx, ty, 58, 58, 9, rc)
            round_rect(tx + 2, ty + 2, 54, 54, 8, tile)
            num = "%02d" % (band_i * 6 + k + 1)
            draw_text(tx + 5, ty + 5, num, 1, mix(INK, tile, 0.35))
            ICONS[icon](cx, ty + 30, 26, rc, INK, tile)
            draw_text(cx, ry + 66, l1, 2, INK, align="center")
            draw_text(cx, ry + 82, l2, 2, INK, align="center")
            draw_text(cx, ry + 99, sub, 1, MUTED, align="center")
            fill_rect(cx - 17, ry + 111, 34, 3, rc)


def draw_footer():
    hline(28, 996, 936, mix(GOLD, bytes(BG_MID), 0.55))
    counts = {}
    for s in STORIES:
        counts[s[3]] = counts.get(s[3], 0) + 1
    parts = []
    total_w = 0
    for name in REGION_ORDER:
        label = "%s X%d" % (name, counts[name])
        parts.append((name, label))
        total_w += text_w(label, 1) + 12 + 26
    total_w -= 26
    x = (W - total_w) / 2
    for name, label in parts:
        rc = REGION[name]
        fill_circle(int(x + 5), 956, 5, rc)
        draw_text(x + 14, 952, label, 1, INK)
        x += text_w(label, 1) + 12 + 26
    draw_text(W / 2, 978, "36 STORIES \u00b7 REPORTED SUNDAY 22 NOVEMBER 2026",
              2, GOLD, align="center")
    draw_text(W / 2, 1004,
              "SOURCES: WORLD NEWS SERVICES REPORTING ON 22 NOVEMBER 2026",
              1, MUTED, align="center")


def apply_grain(count=90000):
    state = 987654321
    n = W * H
    for _ in range(count):
        state = lcg(state)
        p = state % n
        d = (state >> 16) % 9 - 4
        if d == 0:
            continue
        i = p * 3
        for k in range(3):
            v = fb[i + k] + d
            fb[i + k] = 0 if v < 0 else (255 if v > 255 else v)


def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += fb[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(tag, data):
        body = tag + data
        return (struct.pack(">I", len(data)) + body +
                struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    draw_background()
    draw_stars()
    draw_header()
    draw_rows()
    draw_footer()
    apply_grain()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes())
    print("wrote", path)


if __name__ == "__main__":
    main()
