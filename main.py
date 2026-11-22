#!/usr/bin/env python3
"""THE NOVEMBER LEDGER - one-day world news image, Sunday 22 November 2026.

A dense, clean broadsheet: 43 verified stories from 22 November 2026,
four columns under a single masthead. Stdlib only (own PNG encoder and
own 5x7 bitmap font). Deterministic: the same bytes on every run.
"""
import hashlib
import os
import struct
import zlib

# --- 5x7 bitmap font: char -> 7 rows, each a 5-bit int (bit 4 = leftmost) ---
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0, 0x0C, 0x04),
    ':': (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    '-': (0, 0, 0, 0x0E, 0, 0, 0),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '/': (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    '%': (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '+': (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    '=': (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '@': (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '*': (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    '_': (0, 0, 0, 0, 0, 0, 0x1F),
    '<': (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    '>': (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
}

W, H = 1024, 1024
PAPER = (247, 242, 230)
INK = (20, 20, 20)
RED = (158, 27, 27)


def adv(scale):
    return 5 * scale + 1


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)


def text_width(s, scale):
    return len(s) * adv(scale)


def draw_text(cv, x, y, s, scale, color, bold=False):
    a = adv(scale)
    sh = max(1, scale // 3) if bold else 0
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = glyph[r]
            if not row:
                continue
            for c in range(5):
                if row & (1 << (4 - c)):
                    cv.fill_rect(cx + c * scale, y + r * scale,
                                 scale, scale, color)
                    if sh:
                        cv.fill_rect(cx + c * scale + sh, y + r * scale,
                                     scale, scale, color)
        cx += a
    return cx


def wrap(text, max_w, scale):
    a = adv(scale)
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        t = w if not cur else cur + ' ' + w
        if len(t) * a <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def png_bytes(rgb, w, h):
    raw = b''.join(b'\x00' + bytes(rgb[y * w * 3:(y + 1) * w * 3])
                   for y in range(h))

    def chunk(typ, data):
        out = struct.pack('>I', len(data)) + typ + data
        return out + struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))

# --- stories: (kicker, headline, deck) -- all verified 22 November 2026 ---
LEAD = ("GULF CRISIS",
        "IRAN STRIKES BAHRAIN AS GULF CRISIS DEEPENS",
        "Tehran hits a civilian industrial site and claims US bases were "
        "targeted; two tankers are struck near Hormuz. Bahrain reports no "
        "injuries as Gulf tensions soar.")

COL1 = [
    ("CLIMATE", "COP31 TALKS SPILL INTO OVERTIME",
     "Antalya deadlocked on fossil fuels and funds; the EU warns of no deal "
     "over a weak one."),
    ("MEXICO", "MEXICO CAPTURES 'EL CHAPO ISIDRO'",
     "Cartel boss Fausto Isidro Meza Flores seized in Sinaloa; 11 killed "
     "in the raid."),
    ("UKRAINE", "RUSSIA HITS ZELENSKY'S HOMETOWN",
     "Missile strike on Kryvyi Rih kills two and wounds dozens as the war "
     "grinds on."),
    ("BALTIC", "RUSSIAN SHIP ABLAZE AFTER DRONE HIT",
     "Cargo vessel struck in the Gulf of Finland; crew evacuated as "
     "firefighters battle the blaze."),
    ("YEMEN", "SAUDIS DOWN THREE HOUTHI MISSILES",
     "Riyadh-bound rockets intercepted; coalition hits Hodeidah port in "
     "reply."),
    ("GAZA", "ISRAELI STRIKES CONTINUE IN GAZA",
     "Aid vehicle hit as displaced Palestinians protest; Lebanon's "
     "president demands a withdrawal."),
    ("DENMARK", "DENMARK EXPELS RUSSIAN ATTACHE",
     "Copenhagen acts over an alleged assassination plot against a "
     "US-Ukrainian rapper."),
    ("NUCLEAR", "LEADERS AGREE NUCLEAR RISK TALKS",
     "Trump, Xi and Putin agree after Shenzhen to open negotiations on "
     "reducing nuclear danger."),
    ("UNITED NATIONS", "UN AGREES RULES FOR KILLER ROBOTS",
     "Nations reach a tentative deal on autonomous weapons after years of "
     "deadlock."),
    ("WASHINGTON", "FBI PROBES HACK OF CRIME DATABASE",
     "Bureau investigates an apparent breach of its criminal records "
     "system."),
]

COL2 = [
    ("HORMUZ", "SWIMMER CROSSES HORMUZ IN PROTEST",
     "British swimmer braves the strait to expose the conflict's "
     "environmental cost."),
    ("FRANCE", "STRASBOURG CLASHES IN COST PROTESTS",
     "Masked demonstrators battle police in a sixth weekend of unrest over "
     "living costs."),
    ("BERLIN", "GERMAN POLITICIAN ATTACKED AT RALLY",
     "Lawmaker assaulted during a demonstration in the capital."),
    ("IRAQ", "IRAQ POWER STATION FIRE KILLS FOUR",
     "Blaze at the Hartha plant near Basra injures 35; the cause is "
     "unknown."),
    ("INDIA", "TOXIC ALCOHOL KILLS 11 IN MANIPUR",
     "More than 180 people are hospitalised in India after drinking "
     "illicit liquor."),
    ("NIGERIA", "NIGERIA BOAT CAPSIZE KILLS 24",
     "Overcrowded boat sinks during a funeral trip; rescuers search the "
     "river."),
    ("BANGLADESH", "BANGLADESH GARMENT STRIKES SPREAD",
     "Eighty factories shut in Savar and Ashulia as workers demand higher "
     "pay."),
    ("BELGIUM", "BELGIUM FACES FLIGHT CHAOS",
     "Air traffic controllers join Monday's national strike; flights will "
     "be cancelled."),
    ("BRITAIN", "UK AND EU STRIKE NEW DEALS",
     "London and Brussels agree a clutch of pacts as calls grow for "
     "closer ties."),
    ("LEBANON", "LEBANON'S AOUN BLAMES ISRAEL AND IRAN",
     "President says both neighbours threaten his country's sovereignty."),
]

COL3 = [
    ("TRADE", "EU AND INDONESIA SIGN TRADE DEAL",
     "Ten years of talks end in a pact to open markets and secure supply "
     "chains."),
    ("BANTEN", "THREE DEAD, 36 MISSING IN JAVA FIRE",
     "Candy plant in Cikande burns overnight; rescuers search for "
     "workers."),
    ("WEATHER", "BMKG WARNS OF HEAVY RAIN IN 8 AREAS",
     "Cyclone seed 96S brews off Sumatra as storms threaten the "
     "archipelago."),
    ("PAPUA", "QUAKE SHAKES SENTANI",
     "Magnitude 4.8 tremor strikes near Jayapura at a depth of six "
     "kilometres."),
    ("SUMATRA", "QUAKE OFF WEST SUMATRA",
     "Magnitude 4.2 tremor shakes Padang; no tsunami threat, officials "
     "say."),
    ("SURABAYA", "JUANDA STOPS WOULD-BE MERCENARIES",
     "Two Indonesians barred from flying out, suspected of joining "
     "Russia's army."),
    ("JAVA", "TRAIN RAMS MINIBUS AT CROSSING",
     "Driver killed as the train drags the vehicle 500 metres; fire "
     "follows."),
    ("MARKETS", "US STOCKS FALL INTO CORRECTION",
     "S&P 500 drops 3.7% and the Nasdaq 5.6% as the AI sell-off deepens; "
     "the VIX tops 30."),
    ("CHIPS", "NVIDIA LOSES $2.8TN IN 45 DAYS",
     "Chip giant falls 14% in a day, down 48% from its peak; AMD drops "
     "13%."),
    ("STARTUPS", "INDIAN STARTUPS RAISE $290M IN A WEEK",
     "Twenty-three firms raise fresh funds as the funding winter thaws."),
    ("TECH", "MICROSOFT PUTS AI GOVERNANCE FIRST",
     "Ignite 2026 spotlights Agent 365 as firms seek to control their AI "
     "agents."),
]

COL4 = [
    ("FOOTBALL", "ARSENAL HELD 2-2 AT NEWCASTLE",
     "Leaders miss the chance to go eight points clear as Madueke rescues "
     "a point."),
    ("FOOTBALL", "MAN CITY 1-1 FULHAM",
     "Anderson spares City a fourth straight defeat; Fulham end a 20-game "
     "losing run."),
    ("FOOTBALL", "CHELSEA THRASHED 1-4 BY LEEDS",
     "Okafor scores twice in Leeds' first win at Stamford Bridge since "
     "1999."),
    ("FOOTBALL", "BOURNEMOUTH 2-0 FOREST",
     "Evanilson and Kluivert seal a club-record ninth straight win in all "
     "competitions."),
    ("FOOTBALL", "TOTTENHAM 2-0 IPSWICH",
     "Williams-Barnett, 18, scores on his first start before setting up "
     "Solanke."),
    ("FOOTBALL", "COVENTRY 3-2 PALACE",
     "Frank loses his first game in charge as the hosts edge a five-goal "
     "thriller."),
    ("FOOTBALL", "LIVERPOOL HOST UNITED TONIGHT",
     "Pochettino takes charge of United for the first time at Anfield; "
     "Hull host Brighton."),
    ("FLORIDA", "FLORIDA RIVER BREAKS 73-YEAR RECORD",
     "St. Johns floods towns from Miami to Brevard; waters may stay high "
     "into January."),
    ("GAMES", "GTA VI SETS $3.8BN FIRST-DAY RECORD",
     "Rockstar's blockbuster posts the biggest launch in games history."),
    ("BONDI", "BONDI HEROES MARRY AT ATTACK SITE",
     "Two first responders from the Bondi Beach tragedy wed near the "
     "scene."),
    ("AUCTION", "WASHINGTON'S HAIR SELLS FOR $4,000",
     "A lock of George Washington's hair fetches thousands at auction."),
]

MARGIN = 36
COL_W = 226
GUT = 16
COL_X = [MARGIN, MARGIN + COL_W + GUT, MARGIN + 2 * (COL_W + GUT),
         MARGIN + 3 * (COL_W + GUT)]
GRID_TOP = 142
GRID_BOT = 984


def draw_story(cv, x, y, w, story, lead=False):
    kicker, headline, deck = story
    # The bitmap font holds capitals only: force every story line to caps
    # so no lowercase letter ever renders blank.
    kicker = kicker.upper()
    headline = headline.upper()
    deck = deck.upper()
    if lead:
        draw_text(cv, x, y, kicker, 1, RED)
        y += 11
        lines = wrap(headline, w, 3)
        for ln in lines:
            draw_text(cv, x, y, ln, 3, INK, bold=True)
            y += 24
        lines = wrap(deck, w, 1)
        for ln in lines:
            draw_text(cv, x, y, ln, 1, INK)
            y += 8
        return y + 10
    draw_text(cv, x, y, kicker, 1, RED)
    y += 10
    lines = wrap(headline, w, 2)
    for ln in lines:
        draw_text(cv, x, y, ln, 2, INK, bold=True)
        y += 15
    lines = wrap(deck, w, 1)
    for ln in lines:
        draw_text(cv, x, y, ln, 1, INK)
        y += 8
    return y + 10


def draw_masthead(cv):
    title = "THE NOVEMBER LEDGER"
    tw = text_width(title, 7)
    draw_text(cv, (W - tw) // 2, 24, title, 7, INK, bold=True)
    cv.hline(MARGIN, 82, W - 2 * MARGIN, INK, 3)
    cv.hline(MARGIN, 87, W - 2 * MARGIN, INK, 1)
    date = "SUNDAY, 22 NOVEMBER 2026"
    draw_text(cv, MARGIN, 94, date, 2, RED, bold=True)
    mid = "43 STORIES FROM AROUND THE WORLD"
    draw_text(cv, (W - text_width(mid, 1)) // 2, 98, mid, 1, INK)
    price = "PRICE $2.00"
    draw_text(cv, W - MARGIN - text_width(price, 1), 98, price, 1, INK)
    cv.hline(MARGIN, 114, W - 2 * MARGIN, INK, 1)
    tick = ("S&P 500 6,910 -3.7% | NASDAQ -5.6% | FTSE 100 10,346 -1.0% | "
            "BRENT $89.95 +0.6% | VIX 28.4")
    draw_text(cv, (W - text_width(tick, 1)) // 2, 122, tick, 1, INK)
    cv.hline(MARGIN, 136, W - 2 * MARGIN, INK, 1)


def draw_footer(cv):
    cv.hline(MARGIN, 988, W - 2 * MARGIN, INK, 1)
    foot = ("THE NOVEMBER LEDGER | SUNDAY 22 NOVEMBER 2026 | "
            "43 STORIES | PAGE 1")
    draw_text(cv, (W - text_width(foot, 1)) // 2, 996, foot, 1, INK)


def main():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    y = draw_story(cv, COL_X[0], GRID_TOP, 2 * COL_W + GUT, LEAD, lead=True)
    ends = {}
    for x, stories in ((COL_X[0], COL1), (COL_X[1], COL2)):
        yy = y
        for st in stories:
            yy = draw_story(cv, x, yy, COL_W, st)
        ends[x] = yy
    for x, stories in ((COL_X[2], COL3), (COL_X[3], COL4)):
        yy = GRID_TOP
        for st in stories:
            yy = draw_story(cv, x, yy, COL_W, st)
        ends[x] = yy
    draw_footer(cv)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = png_bytes(cv.px, W, H)
    with open(path, "wb") as f:
        f.write(data)
    total = 1 + len(COL1) + len(COL2) + len(COL3) + len(COL4)
    print("stories:", total)
    print("column ends:", ends, "grid bottom:", GRID_BOT)
    print("wrote:", path, "bytes:", len(data),
          "sha256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
