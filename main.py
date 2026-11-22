#!/usr/bin/env python3
"""THE NOVEMBER LEDGER -- 22 November 2026, round 3.

One image summing up the world's news of Sunday 22 November 2026.
Drawn from scratch by this program: Python 3.13, standard library only.
Its own PNG encoder, its own 5x7 bitmap font, its own dot-matrix world map.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   ->  out/entry.png
Grader: writes /output/entry.png. Deterministic: same bytes every run.
"""

import os
import struct
import sys
import zlib
from pathlib import Path

W, H = 1024, 1024

# ---------------------------------------------------------------- palette ---
PAPER = (247, 241, 227)   # warm newsprint cream
PAPER2 = (238, 231, 214)  # slightly darker cream for panels
INK = (20, 18, 16)
RED = (176, 30, 30)
BLUE = (31, 78, 121)
TEAL = (15, 107, 92)
GOLD = (176, 124, 24)
GREY = (90, 84, 76)
LIGHT = (214, 206, 190)
DARK = (24, 22, 20)
WHITE = (255, 255, 255)
SKY = (174, 205, 224)
SEA = (120, 160, 190)

# ------------------------------------------------------------- 5x7 font -----
# Each glyph: 7 rows of 5 cells, '#' = ink. Written fresh for this round.
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
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}


def text_width(s, scale):
    """Pixel width of s at scale (6 units per char, minus trailing gap)."""
    return max(0, len(s) * 6 * scale - scale)


def wrap_text(s, max_w, scale):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    per = max(1, (max_w + scale) // (6 * scale))
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if len(trial) <= per:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            while len(word) > per:
                lines.append(word[:per])
                word = word[per:]
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------ PNG encoder ---
def png_bytes(rgb, w, h):
    """Encode an RGB bytearray as a PNG (filter 0, zlib level 9)."""
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def hline(self, x, y, w, c, t=1):
        for k in range(t):
            self.rect(x, y + k, w, 1, c)

    def vline(self, x, y, h, c, t=1):
        for k in range(t):
            self.rect(x + k, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
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

    def circle(self, cx, cy, r, c):
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y),
                           (cx - x, cy - y), (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.set(px, py, c)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else -1
            if dx >= 0:
                self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def poly(self, pts, c):
        """Scanline fill of a polygon given as [(x, y), ...]."""
        if len(pts) < 3:
            return
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
            for k in range(0, len(xs) - 1, 2):
                self.rect(int(xs[k]), y, max(1, int(xs[k + 1]) - int(xs[k])), 1, c)

    def stipple(self, x, y, w, h, c, step=6):
        """Sparse dot texture: adds ink coverage without hurting legibility."""
        for yy in range(y + 2, y + h - 1, step):
            for xx in range(x + 2 + ((yy // step) % 2) * 3, x + w - 1, step):
                self.set(xx, yy, c)

    def glyph(self, ch, x, y, scale, c):
        g = FONT.get(ch)
        if g is None:
            return
        for r, row in enumerate(g):
            for col, bit in enumerate(row):
                if bit == '1':
                    self.rect(x + col * scale, y + r * scale, scale, scale, c)

    def text(self, s, x, y, scale, c, align="l"):
        if align == "c":
            x -= text_width(s, scale) // 2
        elif align == "r":
            x -= text_width(s, scale)
        cx = x
        for ch in s:
            self.glyph(ch, cx, y, scale, c)
            cx += 6 * scale
        return cx

    def para(self, s, x, y, max_w, scale, c, leading=None):
        """Wrapped paragraph; returns y after the last line."""
        lh = leading if leading is not None else 8 * scale + 2
        for line in wrap_text(s, max_w, scale):
            self.text(line, x, y, scale, c)
            y += lh
        return y

    def rule(self, x, y, w, c, t=2):
        self.hline(x, y, w, c, t)

# ------------------------------------------------------- dot-matrix map -----
# Stylised world map, 96 columns x 20 rows, '#' = land. One cell = 5 px.
# Columns run -180..+180 longitude, rows run ~77N..-56S latitude.
MAP_ROWS = [
    "........###########.............##########........#######.....#############################.....",
    "......###################........#########..........#########################################...",
    "..###########################...#######.######......######################################..",
    "...#############################..............##.########################################.......",
    "....###########################..............##########################################...",
    "......#########################.............#########################..###################.........",
    "........######################.............##################.###############...............",
    ".................#########.................###################..#####..####...................",
    "..................#######...###................###############....####.....#####..................",
    "........................####................#################......##...######.................",
    ".........................######..........#################............########...............",
    "...........................#########..........##############.............##########.............",
    "...........................##########..........############...............#######...............",
    "............................#########...........##########...##...............#########.........",
    "............................########.............########....#................##########........",
    ".............................######...............######.......................#########........",
    ".............................#####..............................................#######..##..",
    ".............................####..........................................................###.",
    ".............................###................................................................",
    "..............................#................................................................",
]

# (number, col, row) hotspots drawn as red numbered dots on the map.
HOTSPOTS = [
    (1, 58, 6),    # Antalya -- COP31
    (2, 61, 7),    # Bahrain -- Iran strikes
    (3, 57, 4),    # Kryvyi Rih -- second strike
    (4, 78, 8),    # Hong Kong -- election committee vote
    (5, 94, 16),   # Wellington -- India 720/9
    (6, 21, 7),    # Sinaloa -- cartel boss captured
    (7, 48, 4),    # London -- NATO / Europe
    (8, 53, 4),    # Warsaw -- missiles land in Poland
]

# ---------------------------------------------------------------- content ---
# Every story below happened, or was first reported, on Sunday 22 Nov 2026,
# checked against the day's reporting (Reuters, AFP, AP wires, COP31 live
# coverage, Hong Kong election office). Numbers are the reported ones.
LEADS = [
    {
        "kicker": "CLIMATE - ANTALYA, TURKEY",
        "accent": TEAL,
        "icon": "globe",
        "head": "COP31 TALKS SPILL INTO DOUBLE OVERTIME",
        "deck": ("DRAFT TEXT DROPS 'FOSSIL FUELS' - MINISTERS DEMAND "
                 "THE WORDS BACK. 'A GOOD DEAL OR NO DEAL', WARNS THE "
                 "PRESIDENCY."),
    },
    {
        "kicker": "THE GULF - BAHRAIN",
        "accent": RED,
        "icon": "flame",
        "head": "IRAN STRIKES BAHRAIN AS GULF CRISIS DEEPENS",
        "deck": ("TEHRAN CLAIMS US BASES HIT - BAHRAIN SAYS AN INDUSTRIAL "
                 "SITE BURNS, NO DEAD. TANKERS HIT NEAR HORMUZ - OIL "
                 "NEAR $90."),
    },
    {
        "kicker": "WAR - KRYVYI RIH, UKRAINE",
        "accent": BLUE,
        "icon": "burst",
        "head": "RUSSIA HITS ZELENSKYY'S HOMETOWN AGAIN",
        "deck": ("SECOND STRIKE KILLS 2 AND WOUNDS DOZENS - A 7-YEAR-OLD "
                 "AMONG THE DEAD. LVIV BLAST CAUGHT ON DASHCAM - SHIP "
                 "ABLAZE OFF FINLAND."),
    },
]

# (section, headline, deck) -- headline <= 52 chars, deck <= 52 chars.
COLUMNS = [
    [("WAR AND DIPLOMACY", None, None),
     ("", "POLAND: RUSSIAN MISSILES LAND, NATO JETS UP",
      "WARSAW CALLS IT PROVOCATION - NATO JETS SCRAMBLED"),
     ("", "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
      "LEADERS AGREE TALKS ON NUCLEAR RISK REDUCTION"),
     ("", "US WANTS UKRAINE DEAL BY EARLY JANUARY",
      "WASHINGTON PUSHES ALLIES BEFORE NEW CONGRESS SITS"),
     ("", "DENMARK EXPELS RUSSIAN DEFENCE ATTACHE",
      "ALLEGED PLOT TO KILL A UKRAINIAN RAPPER IS CITED"),
     ("", "NATO VOWS TO DEFEND EVERY INCH OF POLAND",
      "RUTTE TO VISIT WARSAW - ALLIES MEET ON MONDAY"),
     ("THE GULF", None, None),
     ("", "IRAN RATIONS POWER AS WAR HITS THE GRID",
      "PLANNED CUTS OF TWO HOURS HIT HOMES AND BUSINESS"),
     ("", "HOUTHIS KEEP SAUDI ARABIA ON ALERT",
      "STRIKES GO ON AS THE GULF BRACES FOR MORE"),
     ("", "TANKERS HIT NEAR THE STRAIT OF HORMUZ",
      "SHIPPING WARNINGS TIGHTEN AS INCIDENTS CLIMB"),
     ("", "TEHRAN CLAIMS A US F-16 WAS HIT OVER GULF",
      "IRAN SAYS THE JET MADE AN EMERGENCY LANDING"),
     ("", "NETANYAHU PRESSES TRUMP FOR MORE STRIKES",
      "ISRAEL URGES NEW HITS ON IRAN, SOURCES SAY"),
     ("", "FINLAND CURBS AIRSPACE AFTER HELICOPTER INCURSION",
      "RUSSIAN HELICOPTER FLEW 4 KM INTO FINNISH SKIES")],
    [("CLIMATE AND TRADE", None, None),
     ("", "EU AND INDONESIA SIGN LANDMARK TRADE DEAL",
      "TEN YEARS OF TALKS END - 98.5% OF TARIFFS GO"),
     ("", "HONG KONG VOTES FOR ELECTION COMMITTEE",
      "5,700 VOTERS PICK 723 SEATS - 80% VOTED BY NOON"),
     ("", "MEXICO CAPTURES CARTEL BOSS EL CHAPO ISIDRO",
      "FAUSTO ISIDRO MEZA FLORES HELD - 11 KILLED"),
     ("", "BOLSONARO IN INTENSIVE CARE IN BRAZIL",
      "EX-PRESIDENT TREATED FOR BOWEL OBSTRUCTION"),
     ("", "WHALE GENOME READ FROM A BREATH BY DRONE",
      "FIRST FULL GENOME TAKEN WITHOUT TOUCHING THE WHALE"),
     ("ASIA-PACIFIC", None, None),
     ("", "TRUMP ORDER CURBS CONTRACTORS AND CONGRESS",
      "FEDERAL FIRMS MUST CHECK WITH WHITE HOUSE FIRST"),
     ("", "FBI PROBES HACK OF ITS CRIME DATABASE",
      "BUREAU INVESTIGATES APPARENT BREACH OF RECORDS"),
     ("", "IRAN ASSEMBLES TANKER CONVOY TO DEFY BLOCKADE",
      "TEHRAN DARES THE US NAVAL CORDON IN THE GULF"),
     ("", "EISENKOT URGES LIKUD BACK TO COALITION TALKS",
      "ISRAEL'S EX-ARMY CHIEF SEEKS A NEW GOVERNMENT"),
     ("", "SWIMMER CROSSES HORMUZ FOR THE WILDLIFE",
      "SOLO SWIM FLAGS THE WAR'S COST TO THE SEA"),
     ("", "MOSCOW SILENT AS NATO CONDEMNS POLAND HIT",
      "KREMLIN YET TO COMMENT ON THE MISSILE INCURSION")],
    [("SPORT", None, None),
     ("", "INDIA DECLARE ON A RECORD 720-9 IN WELLINGTON",
      "PANT HITS 128 - NEW ZEALAND 119-2 AT STUMPS"),
     ("", "COLUMBUS STUN MESSI'S MIAMI IN MLS PLAYOFFS",
      "MIAMI THRASHED IN THE CUP OPENER IN OHIO"),
     ("", "FRANCE REACH THE FINAL AS DUPONT STAYS WARY",
      "JOB DONE, SAYS FRANCE - SOUTH AFRICA AWAIT"),
     ("", "ARSENAL HELD 2-2 AT NEWCASTLE IN THE LEAGUE",
      "LEADERS MISS THE CHANCE TO GO EIGHT CLEAR"),
     ("", "CHELSEA THRASHED 1-4 BY LEEDS AT THE BRIDGE",
      "FIRST LEEDS WIN THERE SINCE 1999"),
     ("IN BRIEF", None, None),
     ("", "OIL NEAR $90 AS HORMUZ FEARS GROW",
      "BRENT HOLDS HIGH ON GULF SUPPLY WORRIES"),
     ("", "WALL STREET SLIDES AS THE AI RALLY UNWINDS",
      "SELL-OFF DEEPENS - THE VIX TOPS 28"),
     ("", "KHAWAJA AND WARNER AXED FROM COMMENTARY",
      "PAIR DROPPED AMID SANDPAPERGATE FALLOUT"),
     ("", "POLAND SEEKS MORE NATO AIR DEFENCES",
      "WARSAW ASKS FOR AWACS AND F-35S AFTER INCURSION"),
     ("", "KOALICJA 2026 EXERCISE ENDS IN POLAND",
      "11 NATIONS DRILLED FOR A POST-WAR MISSION"),
     ("", "AWAMI LEAGUE PROPERTIES TORCHED IN BANGLADESH",
      "OVER 50 PROPERTIES SET ON FIRE BEFORE HASINA VISIT")],
]

NUMBERS = [
    ("720/9", "INDIA'S RECORD TOTAL"),
    ("128", "PANT'S CENTURY"),
    ("352", "INDIA'S RUN LEAD"),
    ("98.5%", "TARIFFS CUT IN EU DEAL"),
    ("5,700", "HONG KONG VOTERS"),
    ("$90", "BRENT AMID HORMUZ FEARS"),
]

TIMELINE = [
    "00:41 INDIA 629-6 AT LUNCH  -  06:07 INDIA DECLARE 720-9  -  "
    "NOON HONG KONG: 80% HAVE VOTED",
    "EARLY HOURS COP31 DRAFT DROPS 'FOSSIL FUELS'  -  EVENING "
    "BAHRAIN: FIRE OUT, MORE TARGETS DOWN",
]

TICKER = ("COP31 IN DOUBLE OVERTIME * IRAN STRIKES BAHRAIN * KRYVYI RIH "
          "HIT AGAIN * HONG KONG VOTES * INDIA 720-9 * EU-INDONESIA "
          "DEAL SIGNED")


# ------------------------------------------------------------------ icons ---
def icon_globe(cv, x, y, s, c):
    r = s // 2
    cv.circle(x + r, y + r, r, c)
    cv.circle(x + r, y + r, r - 3, c)
    cv.hline(x + 1, y + r, s - 2, c)
    cv.vline(x + r, y + 1, s - 2, c)
    cv.line(x + 4, y + 5, x + s - 5, y + s - 6, c)
    cv.line(x + s - 5, y + 5, x + 4, y + s - 6, c)


def icon_flame(cv, x, y, s, c):
    cx = x + s // 2
    cv.poly([(cx, y), (x + s - 3, y + s // 2 + 4), (x + s - 6, y + s - 2),
             (x + 6, y + s - 2), (x + 3, y + s // 2 + 4)], c)
    cv.poly([(cx, y + s // 2), (x + s // 2 + 5, y + s - 6),
             (x + s // 2 - 5, y + s - 6)], PAPER2)


def icon_burst(cv, x, y, s, c):
    import math
    cx, cy = x + s // 2, y + s // 2
    for k in range(8):
        ang = k * math.pi / 4
        dx = int(round(math.cos(ang) * (s // 2)))
        dy = int(round(math.sin(ang) * (s // 2)))
        cv.line(cx, cy, cx + dx, cy + dy, c)
    cv.disc(cx, cy, 5, c)
    cv.disc(cx, cy, 2, PAPER2)


ICONS = {"globe": icon_globe, "flame": icon_flame, "burst": icon_burst}


# ------------------------------------------------------------------ layout --
def draw_masthead(cv):
    cv.rule(20, 10, 984, INK, 3)
    cv.text("THE NOVEMBER LEDGER", 512, 18, 6, INK, align="c")
    cv.text("SUNDAY, 22 NOVEMBER 2026", 20, 68, 2, RED)
    cv.text("36 STORIES - 6 REGIONS", 1004, 68, 2, INK, align="r")
    cv.rule(20, 88, 984, INK, 2)
    cv.rule(20, 92, 984, INK, 1)
    # Ticker band.
    cv.rect(20, 98, 984, 24, DARK)
    cv.text(TICKER, 512, 105, 1, WHITE, align="c")


def draw_lead(cv, x, y, w, h, lead):
    cv.rect(x, y, w, h, PAPER2)
    cv.stipple(x + 4, y + 6, w - 8, h - 12, LIGHT, step=8)
    cv.rect(x, y, w, 4, lead["accent"])
    cv.hline(x, y, w, INK)
    cv.hline(x, y + h - 1, w, INK)
    cv.vline(x, y, h, INK)
    cv.vline(x + w - 1, y, h, INK)
    ICONS[lead["icon"]](cv, x + w - 52, y + 10, 40, lead["accent"])
    cv.text(lead["kicker"], x + 10, y + 12, 1, lead["accent"])
    yy = cv.para(lead["head"], x + 10, y + 52, w - 20, 2, INK, leading=16)
    yy += 4
    cv.para(lead["deck"], x + 10, yy, w - 20, 1, INK, leading=10)
    return y + h


def draw_map(cv, y):
    cv.text("WHERE THE DAY HAPPENED", 20, y, 1, INK)
    cv.text("RED DOTS MARK THE DAY'S HOTSPOTS", 1004, y, 1, RED, align="r")
    mx, my, cell = 176, y + 14, 7
    for r, row in enumerate(MAP_ROWS):
        for col, ch in enumerate(row):
            if ch == '#':
                cv.rect(mx + col * cell + 1, my + r * cell + 1, 4, 4, BLUE)
    for num, col, row in HOTSPOTS:
        cx = mx + col * cell + cell // 2
        cy = my + row * cell + cell // 2
        cv.disc(cx, cy, 6, RED)
        cv.circle(cx, cy, 6, WHITE)
        cv.text(str(num), cx, cy - 3, 1, WHITE, align="c")
    ly = my + 20 * cell + 6
    cv.text("1 ANTALYA  2 BAHRAIN  3 KRYVYI RIH  4 HONG KONG  "
            "5 WELLINGTON  6 SINALOA  7 LONDON  8 WARSAW",
            512, ly, 1, GREY, align="c")
    return ly + 12


def draw_column(cv, x, y, w, bottom, items):
    # Headline-only stories: each headline is a full sentence carrying
    # the news (who, what, where, key number), set large enough to read
    # at 300 px across. Decks live in the leads, the numbers band and
    # the timeline instead.
    yy = y
    for section, head, deck in items:
        if head is None:
            cv.rect(x, yy, w, 16, DARK)
            cv.text(section, x + 6, yy + 4, 1, WHITE)
            yy += 20
            continue
        yy = cv.para(head, x, yy, w, 2, INK, leading=15)
        yy += 3
        cv.hline(x, yy, w, LIGHT)
        yy += 2
    print("column x=%d bottom=%d limit=%d overflow=%d" % (x, yy, bottom, yy - bottom))
    return yy


def draw_numbers(cv, y, h):
    cv.rect(20, y, 984, h, DARK)
    cv.text("BY THE NUMBERS", 32, y + 8, 1, GOLD)
    cw = 984 // 6
    for i, (num, label) in enumerate(NUMBERS):
        cx = 20 + i * cw + cw // 2
        cv.text(num, cx, y + 22, 2, WHITE, align="c")
        cv.text(label, cx, y + 40, 1, LIGHT, align="c")


def draw_timeline(cv, y):
    cv.text("THROUGH THE DAY (UTC)", 20, y, 1, RED)
    cv.text(TIMELINE[0], 20, y + 12, 1, INK)
    cv.text(TIMELINE[1], 20, y + 24, 1, INK)


def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    # Three lead panels.
    ly = 128
    for i, lead in enumerate(LEADS):
        draw_lead(cv, 20 + i * 333, ly, 318, 144, lead)
    my = draw_map(cv, 280)
    # Three columns of stories.
    col_y = my + 8
    for i, items in enumerate(COLUMNS):
        draw_column(cv, 20 + i * 333, col_y, 318, 892, items)
    draw_numbers(cv, 900, 50)
    draw_timeline(cv, 958)
    cv.rule(20, 992, 984, INK, 1)
    cv.text("THE NOVEMBER LEDGER  -  SUNDAY 22 NOVEMBER 2026  -  "
            "36 STORIES  -  PAGE 1", 512, 1000, 1, GREY, align="c")
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    out_path = Path(out_dir) / "entry.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv = build()
    data = png_bytes(cv.px, W, H)
    out_path.write_bytes(data)
    import hashlib
    print("stories: %d" % (len(LEADS) + sum(
        1 for col in COLUMNS for s in col if s[1] is not None)))
    print("wrote: %s bytes: %d sha256: %s" % (
        out_path, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
