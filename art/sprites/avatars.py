"""Guild avatars v2: mini creatures that live inside the chips, armed with
electronics-inspired weapons. First drafts, to be redrawn in Aseprite.

Inspiration: Hyper Light Drifter and Risk of Rain (small, chunky, readable
silhouettes; flat colour, no outlines). All designs are our own.

Each avatar is a 32x32 grid built from: pre-ops (drawn first, e.g. things
behind the body), an ASCII body ("." = leave empty), then post-ops (weapons,
hands in front). Every grid character maps to a palette colour name.
Front view (facing south), light from the top left.
"""
import math

W, H = 32, 32


class Grid:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.g = [["."] * w for _ in range(h)]

    def set(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = ch

    def ascii(self, rows, y0=0):
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch != ".":
                    self.set(x, y0 + y, ch)

    def line(self, x0, y0, x1, y1, ch):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.set(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), ch)

    def rect(self, x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, ch)

    def rows(self):
        return ["".join(r) for r in self.g]


def run(ops, g):
    for op in ops:
        getattr(g, op[0])(*op[1:])


GUILDS = {}

# ---------------------------------------------------------------- BNF: the stock critter
GUILDS["bnf"] = dict(
    title="BNF",
    blurb="A sturdy stock critter with a camera-module head. Propeller-blade sword and a prop-guard shield: the starter kit.",
    keys={
        "C": "silkscreen shade", "D": "ic grey", "B": "ic dark", "G": "wire blue deep", "g": "glow teal",
        "R": "logo red", "r": "burn red", "S": "silkscreen shade", "s": "ic grey",
        "F": "ic grey", "f": "ic dark", "W": "wire blue", "w": "wire blue deep", "Y": "silkscreen white",
        "h": "copper shadow", "M": "ic dark", "P": "silkscreen white", "p": "silkscreen shade",
    },
    body=[
        "", "", "",
        "...........................WW",
        "..........................WWw",
        "...........CCCCCCCCCC.....WWw",
        "..........CDDDDDDDDDDB...WWWw",
        "..........DDDBBBBBBDDB...WWw",
        "..........DDBBGGGGBBDB..WWWw",
        "..........DDBGgGGGGBDB..WWw",
        "..........DDBGGGGGGBDB.WWWw",
        "..........DDBBGGGGBBDB.WWw",
        "..........DDDBBBBBBDDB.Ww",
        "..........BBBBBBBBBBBB..Y",
        "...........RRRRRRRRRr...hh",
        "....PPPP.RRRRRRRRRRRRRr.hh",
        "...PDDDDpRRRSSSSSSRRRRrMM",
        "..PDDYYDDpRRSSSSSSSRRRrMM",
        "..PDYYYYDpRRSSSSSSSRRRr",
        "..PDDYYDDpRRSSSSSSSRRRr",
        "...pDDDDpRRRSSSSSSRRRrr",
        "....pppp.RRRRssssssRRrr",
        ".........rRRRRRRRRRRrr",
        "..........rrrrrrrrrrr",
        "..........FFF.....FFF",
        "..........FFf.....FFf",
        ".........FFFf....FFFf",
    ],
)

# ---------------------------------------------------------------- DIY Punk: the gremlin
GUILDS["diy"] = dict(
    title="DIY PUNK",
    blurb="A grinning gremlin with a pink wire mohawk, teal goggles, a patched vest, a copper coil on the arm and a JST-plug tail. Soldering-iron lance with a glowing tip.",
    keys={
        "M": "signal pink", "m": "copper", "U": "graffiti purple", "u": "dusk purple", "G": "ic dark",
        "g": "glow teal", "T": "silkscreen white", "B": "ic black", "J": "ic grey", "j": "ic dark",
        "y": "flux", "o": "copper", "W": "silkscreen white", "w": "silkscreen shade", "q": "ic grey",
        "h": "copper", "R": "logo red", "P": "signal pink",
    },
    pre=[],
    body=[
        "",
        "",
        "..............m.m",
        ".............mMmMm",
        "..............MMM",
        ".............MMMMM",
        "..........UUUUMMMUUUu",
        ".....uU..UUUUUUUUUUUUu..Uu",
        "......uUUUGGGGUUUGGGGUUUu",
        ".......uUUGggGUUUGggGUUu",
        ".........UGGGGUUUGGGGUUu",
        ".........UUUUUUUUUUUUUu",
        ".........UBTBTBTBTBTBUu",
        "..........uUBBBBBBBBUu",
        "...........uuUUUUUUuu",
        ".........JJJJJJJJJJJJj",
        ".......UUJJJJyyJJJJJJjUU",
        "......UU.JJJJyyJJJJJJjUUUU",
        ".....UU..JJJJJJJJJJJJj",
        ".....oU..JJJJJJJJJJJJj",
        ".....Uo..jjjjjjjjjjjjj",
        ".....oU...UUUUUUUUUUu",
        "....UUU...UUUUUUUUUUu",
        "..........uUUUUUUUUuu",
        "..........UUu....UUu",
        ".........UUu.....UUu",
        ".........uu.......uu",
        "........UUUu.....UUUu",
    ],
    post=[
        ("line", 10, 23, 6, 26, "u"), ("line", 6, 26, 3, 25, "u"), ("rect", 1, 22, 3, 24, "W"),
        ("set", 3, 24, "w"), ("set", 1, 24, "w"),
        ("line", 26, 6, 26, 17, "W"), ("line", 27, 6, 27, 17, "w"),
        ("line", 26, 18, 26, 28, "q"), ("line", 27, 18, 27, 28, "j"),
        ("rect", 26, 21, 27, 21, "M"), ("rect", 26, 25, 27, 25, "M"),
        ("rect", 26, 4, 27, 5, "h"), ("set", 26, 3, "R"), ("set", 26, 2, "R"), ("set", 26, 1, "P"),
        ("set", 25, 2, "P"), ("set", 27, 1, "P"),
        ("rect", 24, 16, 26, 16, "U"), ("set", 27, 16, "u"), ("rect", 25, 17, 27, 17, "u"),
    ],
)

# ---------------------------------------------------------------- Raiders: the scavenger crow
GUILDS["raider"] = dict(
    title="RAIDER",
    blurb="A hooded scavenger crow: beak respirator, red eyes, a ragged scrap cloak with a LiPo bandolier. Antenna-whip bow, pin-header arrows.",
    keys={
        "E": "fr4 edge", "e": "fr4 shade", "c": "copper shadow", "K": "ic black", "R": "logo red",
        "Q": "ic grey", "q": "ic dark", "Z": "ic black", "b": "wire yellow", "B": "wire blue",
        "L": "ic grey", "l": "ic dark", "S": "silkscreen shade", "s": "ic grey", "w": "copper",
        "a": "ic dark", "G": "enig gold", "p": "oxide red",
    },
    pre=[
        ("rect", 21, 9, 24, 13, "c"),
        ("line", 22, 6, 22, 9, "a"), ("line", 24, 7, 24, 9, "a"), ("line", 23, 5, 23, 9, "a"),
        ("set", 22, 5, "G"), ("set", 24, 6, "G"), ("set", 23, 4, "G"),
    ],
    body=[
        "",
        "...............E",
        "..............EEe",
        ".............EEEEe",
        "............EEEEEee",
        "...........EEEEEEEee",
        "..........EEEKKKKKKee",
        "..........EEKKRKKRKKe",
        "..........EEKKKQQKKKe",
        "..........eEKKQQQqKKe",
        "...........eEKQQqKKe",
        "..........eeEEKQqKEee",
        ".........eEEEEEEqEEEEe",
        "........eEEZEEEEEEEEEEe",
        ".......eEEEEZEEEEEEEEEEe",
        ".......eEEEEEbEEEEEEEEEe",
        "......eEEEEEEEZEEEEEEEEee",
        "......eEEEEEEEEBEEEEEEEee",
        "......eEEEEEEEEEZEEEEEEee",
        "......eeEEEEEEEEEbEEEEeee",
        "......eeeEEEEEEEEEZEEEeee",
        "......eccEEEEEEEEEEEEEcce",
        ".......ceeEEEEEEEEEEEeec",
        ".......c.eeEEEcEEEEEee.c",
        "........c.e.ecE.eEe.e.c",
        "............LL...LL",
        "............Ll...Ll",
        "............Ll...Ll",
        "...........LLLL.LLLL",
        "...........L.L..L.L",
    ],
    post=[("line", 5, 7, 5, 25, "w")]
    + [("set", round(4 - 3 * math.sin(math.pi * (y - 6) / 20)), y, "S") for y in range(6, 27)]
    + [("set", round(4 - 3 * math.sin(math.pi * (y - 6) / 20)) + 1, y, "s") for y in range(8, 25)]
    + [("rect", 1, 15, 3, 16, "p"), ("rect", 4, 16, 6, 16, "e")],
)

# ---------------------------------------------------------------- Racers: the wasp
GUILDS["racer"] = dict(
    title="RACER",
    blurb="A yellow-and-black wasp built for speed: pink compound eyes, teal wings, a stinger. Twin carbon-fibre daggers.",
    keys={
        "Y": "wire yellow", "y": "enig gold", "K": "ic dark", "k": "ic black", "P": "signal pink",
        "p": "graffiti purple", "W": "silkscreen white", "T": "glow teal", "t": "signal teal",
        "q": "ic grey", "C": "ic grey", "G": "wire yellow",
    },
    body=[
        "",
        "...........K.......K",
        "............K.....K",
        ".............K...K",
        "............YYYYYYYy",
        "...........YYYYYYYYYy",
        "..........PPPPYYYPPPPp",
        "..........PWPPYYYPWPPp",
        "..........pPPPYYYPPPpp",
        "...........pppKKKKppp",
        "............KK.KK.KK",
        "......tTT....KKKKKK....TTt",
        ".....tTTTT.KKKKKKKKk.TTTTt",
        "....tTTTTTKKYYYYYYKKkTTTTTt",
        ".....tTTTKKKYYYYYYKKKkTTTt",
        "......tt.K.KKKKKKKKk.K.tt",
        "........K..YYYYYYYYy..K",
        "............KKKKKKKk",
        "............YYYYYYYy",
        "............KKKKKKKk",
        ".............YYYYYy",
        ".............KKKKKk",
        "..............YYYy",
        "..............KKKk",
        "...............Kk",
        "...............K",
    ],
    post=[
        ("set", 11, 17, "q"), ("line", 10, 18, 10, 20, "q"), ("set", 9, 21, "q"),
        ("set", 20, 17, "q"), ("line", 21, 18, 21, 20, "q"), ("set", 22, 21, "q"),
        ("line", 7, 18, 4, 23, "C"), ("line", 8, 18, 5, 23, "W"), ("rect", 8, 17, 9, 17, "G"),
        ("line", 24, 18, 27, 23, "C"), ("line", 23, 18, 26, 23, "W"), ("rect", 22, 17, 23, 17, "G"),
    ],
)


# ---------------------------------------------------------------- Whitespace: the floating egg-bot
def _whitespace():
    g = Grid()
    cx, cy, rx, ry = 15.5, 14.0, 6.6, 10.2
    for y in range(H):
        for x in range(W):
            u, v = (x - cx) / rx, (y - cy) / ry
            if u * u + v * v <= 1:
                k = 0.75 * u + 0.6 * v
                g.set(x, y, "g" if k > 0.85 else "w" if k > 0.35 else "W")
    for x in range(11, 21):
        g.set(x, 9, "V")
        g.set(x, 10, "V")
    for x in (19, 20):
        g.set(x, 9, "v")
        g.set(x, 10, "v")
    for x in (14, 15, 16):
        g.set(x, 17, "V")
    g.rect(14, 25, 16, 25, "V")
    g.set(15, 26, "v")
    g.set(15, 27, "t")
    for (hx, hy) in [(6, 15), (24, 15)]:  # floating hands
        g.rect(hx - 1, hy - 1, hx + 1, hy + 1, "W")
        g.set(hx + 1, hy + 1, "w")
        g.set(hx - 1, hy + 1, "w")
    g.line(26, 8, 26, 27, "W")
    g.line(27, 8, 27, 27, "w")
    g.set(24, 15, "W")
    g.rect(25, 14, 26, 16, "W")
    for a in range(0, 360, 20):  # gimbal ring around a floating orb
        g.set(round(26.5 + 3.4 * math.cos(math.radians(a))), round(4.5 + 3.4 * math.sin(math.radians(a))),
              "w" if 0 < a < 180 else "W")
    g.rect(26, 4, 27, 5, "V")
    g.set(26, 4, "T")
    return g.rows()


GUILDS["whitespace"] = dict(
    title="WHITESPACE",
    blurb="A floating egg-bot, white and glossy, with a teal visor and floating hands. Gimbal staff with a glowing orb: the caster.",
    keys={
        "W": "silkscreen white", "w": "silkscreen shade", "g": "ic grey", "V": "glow teal", "v": "signal teal",
        "T": "silkscreen white", "t": "signal teal deep",
    },
    rows=_whitespace(),
)

ORDER = ["bnf", "diy", "raider", "racer", "whitespace"]


def build(name):
    gd = GUILDS[name]
    if "rows" in gd:
        return gd["rows"]
    g = Grid()
    run(gd.get("pre", []), g)
    g.ascii(gd["body"])
    run(gd.get("post", []), g)
    return g.rows()
