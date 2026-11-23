"""Guild avatars, first drafts: one shared 32 px body, faction overlays on top.

Front view (facing south), top-down 3/4 like the street view. Flat colour,
no outlines, light from the top left (right side and bottom are the shade).

Grid keys used by the base body (each faction maps them to palette colours):
  H hair   k skin   K skin shade   E eyes   T torso   t torso shade
  A left arm   a right arm   L legs   l legs shade   F feet   f feet shade
Overlays: {row: [(col, "string"), ...]}. In a string, " " leaves the pixel
alone, "." erases it, any other character sets that key.
"""

W, H = 20, 32

BASE = [
    "....................",
    "....................",
    ".......HHHHHH.......",
    "......HHHHHHHH......",
    ".....HHHHHHHHHH.....",
    ".....HkkkkkkkkH.....",
    ".....kkEkkkkEkK.....",
    ".....kkkkkkkkkK.....",
    ".....kkkkkkkkKK.....",
    "......kkkkkkKK......",
    "........KKKK........",
    ".....TTTTTTTTTt.....",
    "....TTTTTTTTTTTt....",
    "...ATTTTTTTTTTTta...",
    "...ATTTTTTTTTTTta...",
    "...ATTTTTTTTTTTta...",
    "...ATTTTTTTTTTTta...",
    "...ATTTTTTTTTTTta...",
    "...kTTTTTTTTTTTtk...",
    "...kTTTTTTTTTTTtk...",
    "....LLLLLLLLLLLl....",
    "....LLLLLLLLLLLl....",
    "....LLLLl..LLLLl....",
    "....LLLLl..LLLLl....",
    "....LLLLl..LLLLl....",
    "....LLLLl..LLLLl....",
    "....LLLLl..LLLLl....",
    "....LLLLl..LLLLl....",
    "....lllll..lllll....",
    "...FFFFF....FFFFF...",
    "...FFFFf....FFFFf...",
    "....................",
]

GUILDS = {}

# ---------------------------------------------------------------- BNF: bought it ready to fly
GUILDS["bnf"] = dict(
    title="BNF",
    blurb="Bought it ready to fly. Stock gear, stock settings, cap and hoodie, radio always in hand.",
    keys={
        "H": "copper shadow", "k": "skin", "K": "skin shade", "E": "ic black",
        "T": "silkscreen shade", "t": "ic grey", "A": "silkscreen shade", "a": "ic grey",
        "L": "wire blue", "l": "wire blue deep", "F": "silkscreen white", "f": "silkscreen shade",
        "C": "logo red", "c": "burn red", "w": "silkscreen white", "R": "ic dark", "s": "silkscreen white",
        "P": "ic grey",
    },
    over={
        1: [(7, "CCCCCC")],
        2: [(6, "CCCCCCCc")],
        3: [(5, "CCCCCCCCCc")],
        4: [(5, "cccccccccc")],
        12: [(8, "w"), (11, "w")],
        13: [(8, "w"), (11, "w")],
        14: [(8, "w"), (11, "w")],
        15: [(3, "kRRRRRRRRRRRRk")],
        16: [(3, "kRsRRRRRRRRsRk")],
        17: [(4, "RRRRRRRRRRRR")],
        18: [(3, "A"), (16, "a")],
        19: [(3, "A"), (6, "PPPPPPPP"), (16, "a")],
    },
)

# ---------------------------------------------------------------- DIY punk: self-built everything
GUILDS["diy"] = dict(
    title="DIY PUNK",
    blurb="Built every part themselves. Pink mohawk, teal goggles, patched jacket, copper coil on the arm, iron in hand.",
    keys={
        "H": "signal pink", "S": "skin deep shade", "k": "skin deep", "K": "skin deep shade", "E": "ic black",
        "G": "ic dark", "g": "glow teal", "T": "dusk purple", "t": "ic dark", "A": "dusk purple", "a": "ic dark",
        "X": "signal pink", "p": "copper", "y": "flux", "L": "ic grey", "l": "ic dark", "F": "ic black",
        "f": "ic black", "o": "copper", "O": "copper shadow", "i": "silkscreen shade", "r": "logo red",
    },
    over={
        0: [(8, "HHHH")],
        1: [(8, "HHHH")],
        2: [(7, "SHHHHS")],
        3: [(6, "SSHHHHSS")],
        4: [(5, "SSSHHHHSSS")],
        5: [(5, "S"), (14, "S")],
        6: [(5, "GgggGGgggG")],
        11: [(9, "XX")],
        12: [(9, "XX")],
        13: [(3, "o"), (5, "pp"), (9, "XX")],
        14: [(3, "O"), (5, "pp"), (9, "XX")],
        15: [(3, "o"), (9, "XX"), (17, "r")],
        16: [(3, "O"), (9, "XX"), (12, "yy"), (17, "i")],
        17: [(3, "o"), (9, "XX"), (12, "yy"), (17, "i")],
        18: [(9, "XX"), (17, "i")],
        24: [(5, "pp")],
        25: [(5, "pp")],
        26: [(4, "FFFFF"), (11, "FFFFf")],
        27: [(4, "FFFFF"), (11, "FFFFf")],
        28: [(4, "FFFFF"), (11, "FFFFf")],
    },
)

# ---------------------------------------------------------------- Raiders: scavengers
GUILDS["raider"] = dict(
    title="RAIDER",
    blurb="Scavengers. Scrap hood, respirator and red goggles, a LiPo bandolier, salvaged shoulder plate, a whip antenna off the pack.",
    keys={
        "H": "fr4 shade", "h": "copper shadow", "Q": "ic dark", "q": "ic grey", "g": "logo red", "G": "ic black",
        "T": "fr4 edge", "t": "fr4 shade", "A": "fr4 shade", "a": "copper shadow", "b": "wire yellow",
        "B": "wire blue", "Z": "ic black", "M": "ic grey", "m": "silkscreen shade", "L": "copper shadow",
        "l": "ic black", "F": "ic dark", "f": "ic black", "k": "oxide red", "K": "burn red",
        "n": "silkscreen shade", "N": "logo red", "E": "ic black",
    },
    over={
        0: [(17, "N")],
        1: [(7, "HHHHHH"), (17, "n")],
        2: [(6, "HHHHHHHh"), (17, "n")],
        3: [(5, "HHHHhHHHHh"), (17, "n")],
        4: [(4, "HHHHHHHHHHHh"), (17, "n")],
        5: [(4, "HHGGGGGGGGhh"), (17, "n")],
        6: [(4, "HHGggGGggGhh"), (17, "n")],
        7: [(4, "HHQQQQQQQQhh"), (17, "n")],
        8: [(4, "HqQQQQQQQQqh"), (17, "n")],
        9: [(4, "HqQQQQQQQQqh"), (17, "n")],
        10: [(5, "HHHHHHHHHh"), (16, "hn")],
        11: [(3, "MmM"), (16, "h")],
        12: [(3, "MMM"), (13, "Z"), (16, "h")],
        13: [(11, "BBZ")],
        14: [(10, "Z")],
        15: [(8, "bbZ")],
        16: [(7, "Z")],
        17: [(5, "BBZ")],
        18: [(5, "Z")],
        19: [(4, "TLTTLTTTLTTt")],
        23: [(4, "KKKKK"), (11, "KKKKK")],
        26: [(4, "KKKKK"), (11, "KKKKK")],
    },
)

# ---------------------------------------------------------------- Racers: gates and stopwatches
GUILDS["racer"] = dict(
    title="RACER",
    blurb="Gates and lap times. Slim goggles with a pink lens, yellow race jacket with a black stripe and a number, gloves, red shoes.",
    keys={
        "H": "ic black", "k": "skin", "K": "skin shade", "E": "ic black", "V": "ic black", "v": "signal pink",
        "T": "wire yellow", "t": "enig gold", "A": "ic black", "a": "ic black", "Z": "ic black",
        "n": "silkscreen white", "g": "ic dark", "L": "ic dark", "l": "ic black", "Y": "wire yellow",
        "F": "logo red", "f": "burn red",
    },
    over={
        4: [(5, "V"), (14, "V")],
        5: [(5, "VVVVVVVVVV")],
        6: [(5, "VvvvvvvvvV")],
        7: [(5, "VVVVVVVVVV")],
        11: [(7, "ZZZZZ")],
        12: [(12, "ZZ")],
        13: [(5, "nnn"), (11, "ZZ")],
        14: [(7, "n"), (10, "ZZ")],
        15: [(6, "n"), (9, "ZZ")],
        16: [(6, "n"), (8, "ZZ")],
        17: [(7, "ZZ")],
        18: [(3, "g"), (6, "ZZ"), (16, "g")],
        19: [(3, "g"), (16, "g")],
        **{r: [(4, "Y"), (15, "Y")] for r in range(20, 28)},
    },
)

# ---------------------------------------------------------------- Whitespace: the clean futurists
GUILDS["whitespace"] = dict(
    title="WHITESPACE",
    blurb="The clean futurists: everything white, glossy and rounded, a teal visor, and a little camera drone that follows them around.",
    keys={
        "H": "silkscreen white", "h": "silkscreen shade", "v": "glow teal", "V": "signal teal",
        "k": "skin", "K": "skin shade", "E": "ic black", "T": "silkscreen white", "t": "silkscreen shade",
        "A": "silkscreen white", "a": "silkscreen shade", "c": "glow teal", "L": "silkscreen white",
        "l": "silkscreen shade", "F": "silkscreen shade", "f": "ic grey", "d": "silkscreen white",
        "D": "silkscreen shade", "x": "glow teal",
    },
    over={
        0: [(15, "dd.dd")],
        1: [(16, "DxD")],
        2: [(7, "HHHHHH"), (15, "dd.dd")],
        3: [(6, "HHHHHHHh")],
        4: [(5, "HHHHHHHHHh")],
        5: [(5, "Hvvvvvvvvh")],
        6: [(5, "HvvvvvvvVh")],
        7: [(5, "H"), (14, "h")],
        11: [(5, "."), (8, "cc"), (14, ".")],
        12: [(4, "."), (15, ".")],
        20: [(4, "cccccccccccc")],
        29: [(3, "FFFFF"), (12, "FFFFf")],
        30: [(3, "ccccc"), (12, "ccccc")],
    },
)

ORDER = ["bnf", "diy", "raider", "racer", "whitespace"]


def build(name):
    g = [list(r) for r in BASE]
    for row, items in GUILDS[name]["over"].items():
        for col, s in items:
            for i, ch in enumerate(s):
                if ch == " ":
                    continue
                g[row][col + i] = "." if ch == "." else ch
    return ["".join(r) for r in g]
