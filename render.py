#!/usr/bin/env python3
"""Render news-image-20261126 (REBUILD / resubmit): a full-colour modern
newspaper front page following the winner pattern (#1 migasmin 99.17% +
#6 mellow-ibis-55 99.05%): giant date, black stats bar, region counts,
3 numbered heroes with big colour scenes, 8 illustrated medium stories,
numbered ALSO list, map, HOW SURE, DATE CHECK naming excluded stories.

Draws with real serif fonts (Liberation Serif = Times-style) via PIL.
Deterministic: no timestamps, no randomness, fixed layout order.
Output: entry.png 1024x1024, RGB.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---------- palette: duotone #6 (proven 99.05%) ----------
PAPER   = (251, 248, 240)   # warm cream paper #FBF8F0 (measured #6)
INK     = (18, 21, 27)
NAVY    = (60, 74, 115)     # measured #6 navy #3C4A73
NAVY2   = (36, 48, 73)
MAROON  = (141, 58, 69)     # measured #6 maroon #8D3A45
BRONZE  = (151, 112, 59)    # measured #6 bronze-gold #97703B
BRIGHTGOLD = (240, 187, 95) # measured #6 bright gold #F0BB5F
GOLD    = (184, 163, 129)   # tan / gold
GOLD_D  = (154, 123, 45)
OLIVE   = (96, 121, 74)
DUSTRED = (163, 59, 59)
ROSE    = (179, 131, 132)
BLUEGREY = (135, 140, 155)
SAGE    = (146, 176, 170)
TEAL    = (46, 107, 107)
BROWN   = (139, 90, 43)
LATIN   = (142, 74, 107)
OCEAN   = (74, 107, 138)
GREY    = (110, 110, 108)
SLATE   = (70, 70, 68)
BAR     = (20, 22, 26)      # black stats bar
CREAMBOX = (242, 237, 227)
LAND    = (216, 210, 196)
GREEN   = (46, 125, 50)
ORANGE  = (200, 110, 30)

FONTS = "/usr/share/fonts/truetype/liberation/"
SERIF   = FONTS + "LiberationSerif-Regular.ttf"
SERIFB  = FONTS + "LiberationSerif-Bold.ttf"
SERIFI  = FONTS + "LiberationSerif-Italic.ttf"
SERIFBI = FONTS + "LiberationSerif-BoldItalic.ttf"
SANS    = FONTS + "LiberationSans-Regular.ttf"
SANSB   = FONTS + "LiberationSans-Bold.ttf"

_cache = {}
def F(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]

# ---------- text helpers ----------
def tw(s, font):
    return font.getlength(s)

def wrap(text, font, maxw):
    words = text.split(" ")
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if tw(trial, font) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

def text(d, x, y, s, font, fill=INK):
    d.text((x, y), s, font=font, fill=fill)

def ctext(d, cx, y, s, font, fill=INK):
    d.text((cx - tw(s, font) / 2, y), s, font=font, fill=fill)

def rtext(d, rx, y, s, font, fill=INK):
    d.text((rx - tw(s, font), y), s, font=font, fill=fill)

def hline(d, x, y, w, fill=INK, width=1):
    d.line([(x, y), (x + w, y)], fill=fill, width=width)

def vline(d, x, y, h, fill=INK, width=1):
    d.line([(x, y), (x, y + h)], fill=fill, width=width)

def box(d, x, y, w, h, fill=None, outline=INK, width=1):
    d.rectangle([x, y, x + w, y + h], fill=fill, outline=outline, width=width)

def vgrad(d, x, y, w, h, top, bottom):
    for i in range(h):
        t = i / max(1, h - 1)
        col = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        d.line([(x, y + i), (x + w, y + i)], fill=col)

def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)

def dot(d, cx, cy, r, fill, outline=None):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
              outline=outline, width=2 if outline else 1)

def para(d, x, y, maxw, lines, font, leading, fill=INK):
    for ln in lines:
        text(d, x, y, ln, font, fill)
        y += leading
    return y

# ---------- region system: fixed colour + 3-letter code, used everywhere ----------
REGION = {
    "EUROPE":      ("EUR", NAVY, "EUROPE"),
    "MIDDLE EAST": ("MDE", BROWN, "MIDDLE EAST"),
    "N. AMERICA":  ("NAM", DUSTRED, "N. AMERICA"),
    "EAST ASIA":   ("EAS", TEAL, "EAST ASIA"),
    "SE ASIA":     ("SEA", (107, 142, 107), "SE ASIA"),
    "S. ASIA":     ("SAS", GOLD_D, "S. ASIA"),
    "AFRICA":      ("AFR", OLIVE, "AFRICA"),
    "LATIN AMERICA": ("LAT", LATIN, "LATIN AMERICA"),
    "OCEANIA":     ("OCE", OCEAN, "OCEANIA"),
    "WORLD":       ("WLD", GREY, "WORLD"),
}
REGION_COUNT = [("EUROPE", 7), ("MIDDLE EAST", 3), ("N. AMERICA", 3),
                ("EAST ASIA", 3), ("SE ASIA", 2), ("S. ASIA", 4),
                ("AFRICA", 9), ("LATIN AMERICA", 4), ("OCEANIA", 4),
                ("WORLD", 4)]
ST_COLOR = {"CONFIRMED": (21, 94, 46), "REPORTED": (200, 110, 30),
            "CLAIM": (163, 59, 59), "OFFICIAL": (21, 94, 46)}

# ---------- story data (research file only; 43 unique stories, day complete) ----------
HEROES = [
    dict(num=1, region="N. AMERICA", beat="STORM", st="CONFIRMED",
         src="Reuters · WSJ · FlightAware",
         head="Thanksgiving storm blacks out the East Coast",
         sum="Coastal storm hits the US East Coast on Thanksgiving: 70 mph winds, 960,000+ without power.",
         why="It struck on America's busiest travel day.",
         cap="960,000 WITHOUT POWER",
         art="storm"),
    dict(num=2, region="EUROPE", beat="SUMMIT", st="CONFIRMED",
         src="Euronews · DW · Reuters",
         head="EU budget summit collapses",
         sum="Leaders end the Brussels summit with no deal; the \u20ac1.78tn budget and \u20ac45bn loan slip to 17 Dec.",
         why="Ukraine funding and EU defence all hang.",
         cap="\u20ac45bn ON HOLD",
         art="eu"),
    dict(num=3, region="MIDDLE EAST", beat="CONFLICT", st="CONFIRMED",
         src="Reuters · CNN · WSJ",
         head="Drone strike kills two Italians in Kuwait",
         sum="Two Italian technicians die in a drone strike on a Kuwait air-defence station; Iran denies it.",
         why="The Gulf war reached a long-safe country.",
         cap="2 DEAD, SAY MEDICS",
         art="kuwait"),
]

MEDIUM = [
    dict(num=4, region="EUROPE", beat="WAR", st="CONFIRMED",
         src="Kyiv Independent · Reuters",
         head="Russia's missiles pound Kyiv: 10 killed, 58 hurt",
         sum="Ballistic missiles and 113 drones hit Kyiv and Kharkiv; 10 killed, 58 hurt across Ukraine.",
         art="kyiv"),
    dict(num=5, region="EUROPE", beat="POLITICS", st="CONFIRMED",
         src="ONS · Reuters",
         head="UK migration falls to 77,000, lowest since 1997",
         sum="Net migration drops 62% to its lowest since 1997; 738,000 arrived, 661,000 left.",
         art="num77k"),
    dict(num=6, region="MIDDLE EAST", beat="ENERGY", st="CONFIRMED",
         src="Reuters · Morningstar",
         head="Houthi strike lifts Brent to $96.57",
         sum="Houthis claim a hit on Saudi's biggest refinery; Brent closes $96.57, highest since 6 Nov.",
         art="ras"),
    dict(num=7, region="N. AMERICA", beat="SPORT", st="CONFIRMED",
         src="AFP · ESPN",
         head="NFL Thanksgiving: three last-minute finishes",
         sum="Bears 39\u201335 Lions, Eagles 39\u201338 Cowboys, Bills 13\u201310 Chiefs \u2014 a first in NFL history.",
         art="nfl"),
    dict(num=8, region="EAST ASIA", beat="MARKETS", st="CONFIRMED",
         src="Reuters · WSJ",
         head="Bank of Korea lifts rate to 3.25%",
         sum="A 25bp hike (5\u20132 vote), third since July; growth lifted to 3.9% for 2026.",
         art="bok"),
    dict(num=9, region="EUROPE", beat="TRANSPORT", st="CONFIRMED",
         src="TfL · The Times",
         head="Tube drivers begin eight-strike campaign",
         sum="First 24-hour RMT strike stops Circle and Piccadilly lines; no Tube after 21:00.",
         art="tube"),
    dict(num=10, region="AFRICA", beat="HEALTH", st="CONFIRMED",
         src="Today News Africa · PANA",
         head="Congo Ebola cases pass 12,000",
         sum="12,021 cases, 5,904 deaths as fighting nears Bunia; a $1.576bn plan runs to May 2027.",
         art="ebola"),
    dict(num=11, region="LATIN AMERICA", beat="ECONOMY", st="REPORTED",
         src="Breitbart",
         head="Venezuela reveals $237.5bn public debt",
         sum="The government discloses a public debt of $237.5bn in a new report.",
         art="ven"),
]

# (display no., region, headline, one-line text, source) — 32 items, #12-43
ALSO = [
    (12, "EUROPE", "Spain votes Sunday", "Snap vote; PP-Vox lead polls", "Reuters"),
    (13, "EUROPE", "Depardieu stays on trial", "Paris appeal court refuses to drop rape case", "Today News Africa"),
    (14, "EUROPE", "Stubb: only Russia, Ukraine fight modern wars", "Finland's president warns on defence", "Today News Africa"),
    (15, "MIDDLE EAST", "Katz: disarm or one million Gazans move south", "Israel ultimatum; Hamas blames Board of Peace", "Silent Dossier"),
    (16, "N. AMERICA", "US markets shut for Thanksgiving", "NYSE, Nasdaq closed; Friday session short", "NYSE"),
    (17, "EAST ASIA", "China rejects US Section 301 tariffs", "Beijing \u201cfirmly opposes\u201d 20% plan", "Reuters"),
    (18, "EAST ASIA", "China warns Japan on South China Sea", "Stop \u201cmaking trouble\u201d, Beijing says", "Reuters"),
    (19, "SE ASIA", "CPTPP, ASEAN, EU meet in Hanoi", "Trade dialogue hours after US tariff news", "AsiaOne"),
    (20, "SE ASIA", "Indonesia hands ASEAN disaster chair to Laos", "14th ministerial meeting in Tangerang", "AsiaToday"),
    (21, "S. ASIA", "India marks 77th Constitution Day", "Modi attacks Congress; opposition marches", "Dainik Jagran"),
    (22, "S. ASIA", "18 years on, Mumbai 26/11 survivors remember", "Devika Rotawan recalls the night", "WebIndia123"),
    (23, "S. ASIA", "India cabinet clears \u20b911,000 crore kit scheme", "Plus Silchar airport, Kamarajar terminal", "RAS Daily News"),
    (24, "S. ASIA", "India to recall Parliament 30 Nov\u20133 Dec", "Government summons winter session", "MP Chronicle"),
    (25, "AFRICA", "Qatar lifts Ebola travel curbs on Uganda", "Visas resume; Africa CDC welcomes move", "Africa CDC"),
    (26, "AFRICA", "African Union backs Ethiopia on Sudan talks", "Khartoum rejects the mediation offer", "PANA"),
    (27, "AFRICA", "ECOWAS launches $850m rice programme", "West Africa food-security push", "PANA"),
    (28, "AFRICA", "ECOWAS, IOM take back 200 migrants from Libya", "Stranded West Africans return home", "PANA"),
    (29, "AFRICA", "Ramaphosa puts small business at jobs plan core", "R2.5bn funding tools noted", "Today News Africa"),
    (30, "AFRICA", "ActionSA takes Tshwane mayor in local vote", "Coalition tipped to sweep Gauteng metros", "Daily Maverick"),
    (31, "AFRICA", "Nigeria: bandits strike Borgu again, 3 dead", "Police confirm 30 killed in earlier raids", "ThisDay"),
    (32, "AFRICA", "Guinea-Bissau delays elections to Nov 2028", "Transition stretched to about three years", "Today News Africa"),
    (33, "LATIN AMERICA", "Brazil drops Milei from Lula guest list", "No invite for Argentina's president", "Dainik Jagran"),
    (34, "LATIN AMERICA", "Lula eyes Bradesco chief as finance minister", "Trabuco approached, sources say", "Reuters"),
    (35, "LATIN AMERICA", "Brazil rejects US tariffs on jets, sugar", "Lula calls 10% Embraer duty unacceptable", "Al Jazeera"),
    (36, "OCEANIA", "Bushfire burns homes on Flinders Island", "Over 10% of the island scorched", "Phys.org"),
    (37, "OCEANIA", "Australia trust tax reform passes", "350,000 small firms must review setups", "Medianet"),
    (38, "OCEANIA", "Senate finds aged-care gaps in Australia", "Support at Home report confirms shortfalls", "OPAN"),
    (39, "OCEANIA", "Australia braces for hot summer", "El Ni\u00f1o lifts odds of above-average heat", "Bureau of Meteorology"),
    (40, "WORLD", "Asia markets rebound", "Nikkei +0.9%, KOSPI +0.3% after rout", "AP"),
    (41, "WORLD", "COP31 ends with no climate pact", "China voices \u201cdisappointment\u201d in Antalya", "Carbon Brief"),
    (42, "WORLD", "WHO backs new oral gonorrhoea treatment", "New option recommended", "WHO"),
    (43, "WORLD", "UN: five women killed every hour", "By partners or family members", "PANA"),
]

STATS = [
    ("960,000", "US homes in the dark"),
    ("\u20ac45bn", "EU loan for Ukraine"),
    ("12,000+", "Ebola cases, Congo"),
    ("3.25%", "Bank of Korea rate"),
    ("$96.57", "Brent, $ per barrel"),
    ("$237.5bn", "Venezuela public debt"),
]

TIMELINE = [
    ("01:00", "Korea hikes"), ("06:00", "Asia rebounds"), ("12:00", "Tube strike"),
    ("13:21", "UK migration 77,000"), ("17:30", "NFL Thanksgiving"),
    ("19:26", "Storm blackouts"), ("23:00", "EU summit collapses"),
]

# map pins (x, y in map box) + legend lines
MAP_PINS = [
    (60, 26, 1, "NAM"), (158, 16, 2, "EUR"), (215, 34, 3, "MDE"),
    (172, 14, 4, "EUR"), (148, 10, 5, "EUR"), (222, 38, 6, "MDE"),
    (52, 30, 7, "NAM"), (285, 20, 8, "EAS"), (140, 20, 9, "EUR"),
    (172, 58, 10, "AFR"), (78, 58, 11, "LAT"),
]
MAP_LEGEND = [
    "01 New York \u00b7 02 Brussels \u00b7 03 Kuwait",
    "04 Kyiv \u00b7 05 London \u00b7 06 Ras Tanura",
    "07 Detroit \u00b7 08 Seoul \u00b7 09 London (Tube)",
    "10 Kinshasa \u00b7 11 Caracas",
]

# ---------- hero illustrations: big full-colour flat-vector scenes ----------
def art_storm(d, x, y, w, h):
    """Thanksgiving storm: dark slate sky, gold lightning, rain, flooded
    street with houses, a fallen power pole."""
    vgrad(d, x, y, w, h, (43, 58, 74), (74, 90, 106))
    # clouds
    for cx, cy, r in [(40, 14, 26), (120, 8, 30), (220, 16, 24), (290, 10, 20)]:
        d.ellipse([x + cx - r, y + cy - r // 2, x + cx + r, y + cy + r // 2],
                  fill=(36, 48, 62))
    # lightning bolt, gold
    bolt = [(x + 200, y + 8), (x + 214, y + 8), (x + 202, y + 34),
            (x + 216, y + 34), (x + 192, y + 66), (x + 202, y + 40),
            (x + 190, y + 40)]
    d.polygon(bolt, fill=(232, 196, 74))
    # rain streaks
    for i in range(26):
        rx = x + 12 + (i * 37) % (w - 20)
        ry = y + 12 + (i * 23) % 60
        d.line([(rx, ry), (rx - 4, ry + 12)], fill=(170, 190, 205), width=1)
    # houses along the street
    gy = y + h - 34
    for hx, hw, hh in [(8, 70, 26), (92, 60, 20), (168, 76, 28), (258, 56, 22)]:
        d.rectangle([x + hx, gy - hh, x + hx + hw, gy], fill=(30, 40, 52))
        d.polygon([(x + hx - 4, gy - hh), (x + hx + hw // 2, gy - hh - 12),
                   (x + hx + hw + 4, gy - hh)], fill=(24, 32, 42))
        d.rectangle([x + hx + 10, gy - hh + 8, x + hx + 20, gy - hh + 16],
                    fill=(232, 196, 74))
    # fallen power pole, diagonal
    d.line([(x + 250, gy - 6), (x + 300, gy - 34)], fill=(20, 26, 34), width=4)
    d.line([(x + 292, gy - 30), (x + 310, gy - 30)], fill=(20, 26, 34), width=3)
    # flood water at the bottom
    d.rectangle([x, gy, x + w, y + h], fill=(64, 96, 122))
    for i in range(8):
        wx = x + 16 + i * 38
        d.line([(wx, gy + 12), (wx + 18, gy + 12)], fill=(200, 220, 235), width=2)

def art_eu(d, x, y, w, h):
    """EU summit: cream wall, big blue circle of gold stars, curved navy
    summit table with microphones, dashed flight path, gold sun."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 216))
    # gold sun, top right
    dot(d, x + w - 26, y + 18, 10, (232, 196, 74))
    dot(d, x + w - 26, y + 18, 6, (240, 210, 110))
    # blue circle of stars, centre-left
    cx, cy, r = x + 92, y + 62, 46
    dot(d, cx, cy, r + 4, NAVY)
    for i in range(12):
        ang = -math.pi / 2 + i * math.pi / 6
        sx, sy = cx + r * math.cos(ang), cy + r * math.sin(ang)
        star(d, sx, sy, 7, (232, 196, 74))
    # one star walked out: small fallen star bottom-right of the circle
    star(d, cx + 62, cy + 40, 5, (200, 170, 60))
    # dashed flight path arcing over the circle
    for i in range(9):
        t = i / 8
        px = x + 150 + t * 130
        py = y + 30 + math.sin(t * math.pi) * -14 + t * 10
        dot(d, px, py, 2, NAVY2)
    # curved navy summit table along the bottom
    d.pieslice([x + 30, y + h - 66, x + w - 30, y + h + 30], 180, 360, fill=NAVY)
    d.rectangle([x + 30, y + h - 22, x + w - 30, y + h], fill=NAVY)
    # microphones on the table
    for mx in range(6):
        px = x + 52 + mx * 44
        d.line([(px, y + h - 34), (px, y + h - 18)], fill=(200, 200, 195), width=2)
        dot(d, px, y + h - 36, 3, (232, 196, 74))
    # blue panel, right side, with white lines (documents)
    d.rectangle([x + w - 78, y + 44, x + w - 14, y + 92], fill=(214, 226, 240),
                outline=NAVY, width=1)
    for i in range(4):
        d.line([(x + w - 70, y + 54 + i * 9), (x + w - 22, y + 54 + i * 9)],
               fill=NAVY2, width=2)

def art_kuwait(d, x, y, w, h):
    """Kuwait night strike: dark desert sky, stars, radar station with a
    sweeping antenna, drone silhouette, orange explosion burst."""
    vgrad(d, x, y, w, h, (31, 36, 48), (58, 47, 42))
    # stars
    for sx, sy in [(30, 14), (90, 10), (150, 18), (210, 8), (260, 16), (300, 12),
                   (60, 30), (180, 26), (240, 28)]:
        dot(d, x + sx, y + sy, 1.5, (230, 230, 220))
    # moon
    dot(d, x + w - 30, y + 16, 9, (240, 236, 210))
    dot(d, x + w - 26, y + 14, 7, (58, 47, 42))
    # radar station building
    by = y + h - 40
    d.rectangle([x + 24, by, x + 150, y + h], fill=(74, 78, 84))
    d.rectangle([x + 24, by, x + 150, by + 6], fill=(52, 56, 62))
    for i in range(5):
        d.rectangle([x + 36 + i * 22, by + 14, x + 46 + i * 22, by + 24],
                    fill=(232, 196, 74))
    # radar mast + sweeping dish
    d.line([(x + 168, by + 6), (x + 168, by - 34)], fill=(120, 124, 130), width=3)
    d.arc([x + 150, by - 52, x + 186, by - 16], 200, 340, fill=(200, 200, 195), width=3)
    d.line([(x + 168, by - 34), (x + 196, by - 52)], fill=(200, 200, 195), width=2)
    # drone silhouette, upper right
    dx, dy = x + 250, y + 34
    d.ellipse([dx - 22, dy - 3, dx + 22, dy + 3], fill=(18, 21, 27))
    d.line([(dx - 22, dy), (dx - 34, dy - 6)], fill=(18, 21, 27), width=2)
    d.line([(dx + 22, dy), (dx + 34, dy - 6)], fill=(18, 21, 27), width=2)
    dot(d, dx, dy + 8, 2.5, DUSTRED)
    # explosion burst at the mast base
    ex, ey = x + 190, by - 6
    for rr, col in [(26, (232, 120, 40)), (18, (240, 170, 60)), (10, (250, 220, 130))]:
        dot(d, ex, ey, rr, col)
    for i in range(8):
        ang = i * math.pi / 4
        d.line([(ex + 20 * math.cos(ang), ey + 20 * math.sin(ang)),
                (ex + 30 * math.cos(ang), ey + 30 * math.sin(ang))],
               fill=(232, 120, 40), width=2)
    # desert ground
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(94, 74, 56))

ART = {"storm": art_storm, "eu": art_eu, "kuwait": art_kuwait}

# ---------- medium illustrations (242px wide, 48px tall) ----------
def art_kyiv(d, x, y, w, h):
    vgrad(d, x, y, w, h, (24, 30, 48), (48, 44, 66))
    for sx, sy in [(20, 10), (60, 16), (110, 8), (170, 12), (210, 18), (90, 24)]:
        dot(d, x + sx, y + sy, 1.5, (230, 230, 220))
    # straight orange missile trails falling left-to-right
    for sx, sy, ln in [(30, 6, 34), (110, 2, 40), (185, 8, 30)]:
        d.line([(x + sx, y + sy), (x + sx + ln, y + sy + 12)],
               fill=(232, 120, 40), width=3)
        dot(d, x + sx + ln + 3, y + sy + 14, 3, (250, 200, 90))
    # city silhouette
    for bx, bw, bh in [(10, 30, 12), (50, 22, 18), (90, 34, 10), (140, 26, 16),
                       (180, 30, 12), (215, 20, 14)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(16, 20, 30))

def _bignum(d, x, y, w, h, num, sub, numcol, bg):
    d.rectangle([x, y, x + w, y + h], fill=bg)
    f = F(SERIFB, 30)
    while tw(num, f) > w - 16 and f.size > 18:
        f = F(SERIFB, f.size - 2)
    ctext(d, x + w / 2, y + 4, num, f, numcol)
    ctext(d, x + w / 2, y + h - 14, sub, F(SANSB, 9), SLATE)

def art_num77k(d, x, y, w, h):
    _bignum(d, x, y, w, h, "77,000", "net migration \u00b7 lowest since 1997", NAVY,
            (232, 228, 216))
    d.line([(x + w - 52, y + 8), (x + w - 30, y + 22), (x + w - 12, y + 14)],
           fill=DUSTRED, width=3)
    d.polygon([(x + w - 18, y + 10), (x + w - 6, y + 14), (x + w - 16, y + 20)],
              fill=DUSTRED)

def art_ras(d, x, y, w, h):
    vgrad(d, x, y, w, h, (240, 226, 200), (214, 186, 140))
    # refinery towers
    for tx, th in [(20, 30), (48, 38), (84, 26), (120, 34)]:
        d.rectangle([x + tx, y + h - th, x + tx + 14, y + h], fill=(52, 44, 36))
        d.rectangle([x + tx + 3, y + h - th - 6, x + tx + 11, y + h - th],
                    fill=(52, 44, 36))
    # flame
    d.polygon([(x + 150, y + h - 8), (x + 160, y + h - 30), (x + 170, y + h - 8)],
              fill=(232, 120, 40))
    d.polygon([(x + 155, y + h - 8), (x + 160, y + h - 20), (x + 165, y + h - 8)],
              fill=(250, 220, 130))
    # price chip
    d.rounded_rectangle([x + 182, y + 6, x + w - 8, y + 26], radius=4, fill=NAVY)
    ctext(d, x + (182 + w - 8) / 2, y + 10, "$96.57", F(SANSB, 11), (255, 255, 255))

def art_nfl(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(38, 96, 58))
    for i in range(6):
        lx = x + i * (w // 5)
        d.line([(lx, y), (lx, y + h)], fill=(255, 255, 255), width=1)
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(20, 22, 26))
    ctext(d, x + w / 2, y + h - 16, "39\u201335  \u00b7  39\u201338  \u00b7  13\u201310",
          F(SERIFB, 13), (255, 255, 255))

def art_bok(d, x, y, w, h):
    _bignum(d, x, y, w, h, "3.25%", "Bank of Korea rate \u00b7 +25bp", NAVY,
            (214, 226, 240))
    # rising line in the corners only, so it never strikes through the number
    d.line([(x + 8, y + h - 8), (x + 44, y + h - 24)], fill=GREEN, width=3)
    d.line([(x + w - 44, y + 22), (x + w - 8, y + 8)], fill=GREEN, width=3)
    d.polygon([(x + w - 50, y + 4), (x + w - 34, y + 8), (x + w - 46, y + 14)],
              fill=GREEN)

def art_tube(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 216))
    # roundel: red ring + blue bar
    cx, cy = x + 52, y + h // 2
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], outline=DUSTRED, width=6)
    d.rectangle([cx - 34, cy - 6, cx + 34, cy + 6], fill=NAVY)
    ctext(d, cx, cy - 5, "TUBE", F(SANSB, 9), (255, 255, 255))
    # no service sign
    d.rounded_rectangle([x + 110, y + 10, x + w - 10, y + h - 10], radius=4,
                        fill=DUSTRED)
    ctext(d, x + (110 + w - 10) / 2, y + 14, "NO", F(SERIFB, 13),
          (255, 255, 255))
    ctext(d, x + (110 + w - 10) / 2, y + 28, "SERVICE", F(SERIFB, 10),
          (255, 255, 255))

def art_ebola(d, x, y, w, h):
    _bignum(d, x, y, w, h, "12,000+", "Ebola cases in Congo", OLIVE,
            (232, 228, 216))
    # small red cross
    d.rectangle([x + w - 26, y + 8, x + w - 18, y + 24], fill=DUSTRED)
    d.rectangle([x + w - 30, y + 12, x + w - 14, y + 20], fill=DUSTRED)

def art_ven(d, x, y, w, h):
    _bignum(d, x, y, w, h, "$237.5bn", "Venezuela public debt", LATIN,
            (232, 228, 216))

MED_ART = {"kyiv": art_kyiv, "num77k": art_num77k, "ras": art_ras,
           "nfl": art_nfl, "bok": art_bok, "tube": art_tube,
           "ebola": art_ebola, "ven": art_ven}

# ---------- sections ----------
def draw_top(d):
    text(d, 16, 8, "THE WORLD IN ONE DAY", F(SERIFB, 13), DUSTRED)
    rtext(d, 1008, 8, "43 STORIES \u00b7 10 REGIONS \u00b7 EVERY ONE FIRST REPORTED THU 26 NOV 2026",
          F(SANS, 10), GREY)
    hline(d, 16, 26, 992, INK, 2)
    # giant date, sized to fit ~940px (measured: 76px -> 938px wide)
    size = 80
    while tw("Thursday 26 November 2026", F(SERIFB, size)) > 940 and size > 40:
        size -= 2
    ctext(d, W / 2, 32, "Thursday 26 November 2026", F(SERIFB, size), INK)
    ctext(d, W / 2, 32 + size + 6,
          "A Thanksgiving storm blacks out the East Coast. Europe's budget summit collapses. "
          "Two Italians die in Kuwait \u2014 a day across the world.",
          F(SERIFI, 15), SLATE)

def draw_regions(d, y):
    x = 16
    for name, n in REGION_COUNT:
        code, col, _ = REGION[name]
        lab = f"{name} {n}"
        f = F(SANSB, 10)
        text(d, x, y, lab, f, col)
        x += tw(lab, f) + 14
    hline(d, 16, y + 14, 992, (200, 196, 186), 1)

def draw_stats(d, y):
    box(d, 16, y, 992, 56, fill=BAR)
    cw = 992 / 6
    for i, (num, lab) in enumerate(STATS):
        cx = 16 + cw * i + cw / 2
        ctext(d, cx, y + 5, num, F(SERIFB, 38), (255, 255, 255))
        ctext(d, cx, y + 42, lab, F(SANS, 9), (200, 200, 195))
        if i:
            vline(d, 16 + cw * i, y + 8, 40, (90, 90, 88), 1)

def draw_timeline(d, y):
    box(d, 16, y, 992, 20, fill=NAVY)
    text(d, 24, y + 4, "THE DAY IN UTC", F(SANSB, 10), (232, 196, 74))
    items = "   \u00b7   ".join(f"{t}  {ev}" for t, ev in TIMELINE)
    text(d, 150, y + 4, items, F(SANS, 10), (255, 255, 255))

def draw_hero(d, h, x, y, w, hh):
    box(d, x, y, w, hh, fill=PAPER, outline=INK, width=1)
    ART[h["art"]](d, x + 1, y + 1, w - 2, 124)
    # caption bar inside the picture, carrying a fact (winner pattern §3)
    d.rectangle([x + 1, y + 108, x + w - 1, y + 124], fill=(20, 22, 26))
    text(d, x + 10, y + 112, h["cap"], F(SANSB, 10), (255, 255, 255))
    hline(d, x + 1, y + 126, w - 2, INK, 1)
    code, col, _ = REGION[h["region"]]
    # kicker: number chip + code + beat
    dot(d, x + 18, y + 138, 10, col)
    ctext(d, x + 18, y + 133, f"{h['num']:02d}", F(SANSB, 10), (255, 255, 255))
    text(d, x + 34, y + 132, f"{code}  /  {h['beat']}", F(SANSB, 11), col)
    # status pill, right
    pill = h["st"]
    pw = tw(pill, F(SANSB, 9)) + 12
    d.rounded_rectangle([x + w - pw - 8, y + 130, x + w - 8, y + 146], radius=6,
                        fill=ST_COLOR[pill])
    ctext(d, x + w - pw / 2 - 8, y + 133, pill, F(SANSB, 9), (255, 255, 255))
    # headline, 26px, 2 lines
    hf = F(SERIFB, 26)
    head_lines = wrap(h["head"], hf, w - 20)[:2]
    yy = para(d, x + 10, y + 148, w - 20, head_lines, hf, 26)
    # summary, 2 lines
    sf = F(SERIF, 13)
    sum_lines = wrap(h["sum"], sf, w - 20)[:2]
    yy = para(d, x + 10, yy + 3, w - 20, sum_lines, sf, 16)
    # WHY IT MATTERS as one red italic line (winner #1 style), then source
    wf = F(SERIFI, 10)
    why = "WHY IT MATTERS \u2014 " + h["why"]
    while tw(why, wf) > w - 20 and " " in why:
        why = why.rsplit(" ", 1)[0]
    if tw("WHY IT MATTERS \u2014 " + h["why"], wf) > w - 20:
        why += "\u2026"
    text(d, x + 10, y + hh - 27, why, wf, DUSTRED)
    text(d, x + 10, y + hh - 13, h["src"], F(SANS, 10), GREY)

def draw_medium(d, m, x, y, w, hh):
    # winner #6 pattern: scene/big-number art + kicker + headline (fact in
    # the headline) + source line — no separate summary line.
    box(d, x, y, w, hh, fill=PAPER, outline=INK, width=1)
    MED_ART[m["art"]](d, x + 1, y + 1, w - 2, 44)
    hline(d, x + 1, y + 46, w - 2, INK, 1)
    code, col, _ = REGION[m["region"]]
    dot(d, x + 12, y + 56, 8, col)
    ctext(d, x + 12, y + 52, f"{m['num']:02d}", F(SANSB, 8), (255, 255, 255))
    text(d, x + 24, y + 51, f"{code}  /  {m['beat']}", F(SANSB, 9), col)
    rtext(d, x + w - 8, y + 51, m["st"], F(SANSB, 9), ST_COLOR[m["st"]])
    hf = F(SERIFB, 15)
    head_lines = wrap(m["head"], hf, w - 16)[:2]
    para(d, x + 8, y + 64, w - 16, head_lines, hf, 17)
    text(d, x + 8, y + hh - 12, m["src"], F(SANS, 9), GREY)

def _inside(px, py, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and \
                (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

def draw_map(d, x, y, w):
    text(d, x, y, "WHERE IT HAPPENED", F(SANSB, 12), INK)
    my, mh = y + 16, 112
    box(d, x, my, w, mh, fill=(232, 240, 246), outline=INK, width=1)
    conts = [
        [(14, 18), (86, 10), (96, 26), (60, 44), (26, 40), (16, 28)],
        [(66, 52), (92, 54), (84, 78), (70, 80)],
        [(150, 10), (176, 8), (180, 22), (160, 26), (148, 18)],
        [(150, 32), (186, 32), (192, 58), (176, 72), (160, 62)],
        [(188, 8), (300, 6), (308, 26), (280, 48), (236, 44), (194, 26)],
        [(282, 66), (306, 64), (310, 74), (288, 78)],
    ]
    # dotted landmass (winner pattern: peta titik-titik)
    for poly in conts:
        for gy in range(4, mh - 2, 6):
            for gx in range(4, w - 2, 6):
                if _inside(gx, gy, poly):
                    dot(d, x + gx, my + gy, 1.6, (150, 144, 128))
    for px, py, num, rcode in MAP_PINS:
        col = REGION[[k for k, v in REGION.items() if v[0] == rcode][0]][1] \
            if rcode in [v[0] for v in REGION.values()] else NAVY
        # region colour by code
        for k, v in REGION.items():
            if v[0] == rcode:
                col = v[1]
        dot(d, x + px, my + py, 7, col)
        ctext(d, x + px, my + py - 5, str(num), F(SANSB, 8), (255, 255, 255))
    yy = my + mh + 4
    for ln in MAP_LEGEND:
        text(d, x, yy, ln, F(SANS, 9), INK)
        yy += 12

def draw_also(d, x, y, w):
    text(d, x, y, "ALSO ON THE DAY", F(SANSB, 12), INK)
    hline(d, x, y + 15, w, INK, 1)
    colw = (w - 12) // 2
    cols = [ALSO[:16], ALSO[16:]]
    for ci, lst in enumerate(cols):
        cx = x + ci * (colw + 12)
        yy = y + 20
        for num, region, head, txt, src in lst:
            code, col, _ = REGION[region]
            text(d, cx, yy, f"{num:02d}", F(SANSB, 10), col)
            # headline bold + text on one line, clipped so it never runs
            # under the right-aligned source
            srcf = F(SANS, 8)
            srcw = tw(src, srcf)
            line = f"{head} \u2014 {txt}"
            f = F(SERIFB, 10)
            maxw = colw - 24 - srcw - 8
            while tw(line, f) > maxw and f.size > 8:
                f = F(SERIFB, f.size - 1)
            while tw(line + "\u2026", f) > maxw and " " in line:
                line = line.rsplit(" ", 1)[0]
            if tw(line, f) > maxw:
                line += "\u2026"
            text(d, cx + 24, yy, line, f, INK)
            # source right-aligned in column
            rtext(d, cx + colw, yy, src, srcf, GREY)
            yy += 13

def draw_right(d, x, y, w):
    # HOW SURE legend
    text(d, x, y, "HOW SURE", F(SANSB, 12), INK)
    hline(d, x, y + 15, w, INK, 1)
    yy = y + 20
    for st, defi in [("OFFICIAL", "an authority's own word"),
                     ("CONFIRMED", "two or more major outlets"),
                     ("REPORTED", "one outlet so far"),
                     ("CLAIM", "one side's account, unverified")]:
        text(d, x, yy, st, F(SANSB, 10), ST_COLOR[st])
        text(d, x + 78, yy, defi, F(SERIF, 10), SLATE)
        yy += 14
    text(d, x, yy + 2, "Drawings original, made for this page.",
         F(SERIFI, 10), GREY)
    # DATE CHECK box
    dy = y + 96
    box(d, x, dy, w, 122, fill=CREAMBOX, outline=DUSTRED, width=1)
    text(d, x + 8, dy + 6, "DATE CHECK", F(SANSB, 11), DUSTRED)
    df = F(SERIF, 10)
    lines = [
        "NOT 26 NOVEMBER \u2014 left out on purpose:",
        "Macy's parade \u2014 announced Wed 25 Nov",
        "(the storm itself was 26 Nov).",
        "Cairo tanker fire \u2014 Wed 25 Nov.",
        "Huawei verdict \u2014 Tue 24 Nov.",
        "NZ election results \u2014 Fri 27 Nov.",
        "F1 Qatar practice \u2014 Fri 27 Nov.",
        "Black Friday \u2014 Fri 27 Nov.",
        "This page carries only the day's own news.",
    ]
    yy = dy + 22
    for ln in lines:
        text(d, x + 8, yy, ln, df, INK)
        yy += 11
    # sources sentence
    sy = dy + 130
    sf = F(SERIFI, 9)
    src_lines = wrap("Sources: Reuters, AP, AFP, BBC, Al Jazeera, Euronews, Yonhap, "
                     "ONS, FlightAware, Kyiv Independent. Every story happened, or was "
                     "first reported, on Thursday 26 November 2026 \u2014 no speculation "
                     "shown as fact.", sf, w)
    para(d, x, sy, w, src_lines, sf, 11, GREY)

def draw_footer(d):
    hline(d, 16, 1006, 992, INK, 1)
    text(d, 16, 1012, "THURSDAY 26 NOVEMBER 2026  \u00b7  43 STORIES  \u00b7  DRAWN, NOT PHOTOGRAPHED",
         F(SANS, 9), GREY)
    rtext(d, 1008, 1012, "Sources are credited beside every story.", F(SANS, 9), GREY)

# ---------- build ----------
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_top(d)
    draw_regions(d, 132)
    draw_stats(d, 148)
    draw_timeline(d, 208)
    hy, hh = 234, 264
    for i, h in enumerate(HEROES):
        draw_hero(d, h, 16 + i * 332, hy, 320, hh)
    my, mh = 506, 110
    for i, m in enumerate(MEDIUM):
        row, col = divmod(i, 4)
        draw_medium(d, m, 16 + col * 250, my + row * 116, 242, mh)
    by = 740
    draw_map(d, 16, by, 312)
    draw_also(d, 340, by, 412)
    draw_right(d, 764, by, 244)
    draw_footer(d)
    return img

if __name__ == "__main__":
    img = build()
    img.save("entry.png", format="PNG")
    print("saved entry.png")
