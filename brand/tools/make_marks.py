#!/usr/bin/env python3
"""Tracewinder Labs: two proposals for a pixel-art ouroboros mark.

A "Trace ouroboros": the snake is a PCB trace routed in a loop with 45-degree
  corners, biting its own tail where the tail ends in a via; a chip sits in the
  middle of the loop, wired to the snake.
B "Coil ouroboros": the snake is a toroid inductor: a ring of wound copper with
  its head biting its tail, standing on two component legs.

Both are drawn at true pixel size (1 px = 1 pixel) in the brand palette, then
scaled with hard pixels. Repaint freely in Aseprite from the 1x files.

    python3 brand/tools/make_marks.py   -> brand/logo/proposals/
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import palette  # noqa: E402
from font3x5 import text_pixels, text_width  # noqa: E402

P = palette.load()
C = {k.upper().replace(" ", "_"): v for k, v in P.items()}
OUT = HERE.parent / "logo" / "proposals"
OUT.mkdir(parents=True, exist_ok=True)
CLEAR = (0, 0, 0, 0)


def rgba(c):
    return tuple(c) + (255,)


def canvas(n):
    im = Image.new("RGBA", (n, n), CLEAR)
    return im, ImageDraw.Draw(im)


def shade_edges(im, body, lit, dark):
    """Pixels of colour `lit` whose south or east neighbour is empty become `dark` (light from the top left)."""
    px = im.load()
    w, h = im.size
    out = []
    for y in range(h):
        for x in range(w):
            if px[x, y] == rgba(lit):
                s = px[x, y + 1] if y + 1 < h else CLEAR
                e = px[x + 1, y] if x + 1 < w else CLEAR
                if s[3] == 0 or e[3] == 0:
                    out.append((x, y))
    for x, y in out:
        px[x, y] = rgba(dark)


def stamp(im, x0, y0, rows, keys):
    px = im.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            if ch == "_":
                px[x0 + x, y0 + y] = CLEAR
            else:
                px[x0 + x, y0 + y] = rgba(keys[ch])


# Snake head facing right, jaws open on the tail: '#' lit, 's' shade, 'e' eye, '_' cut out (the mouth)
HEAD = [
    "...######...",
    ".##########.",
    "##ee#######s",
    "#######_____",
    "######______",
    "#######_____",
    "###########s",
    ".#########s.",
    "..sssssss...",
]


# ================================================================= A: trace ouroboros
def mark_a():
    n = 40
    im, d = canvas(n)
    W_, S_ = C["SILKSCREEN_WHITE"], C["SILKSCREEN_SHADE"]
    # the loop, routed like a PCB trace: straight runs, 45-degree corners; the tail ends at the top
    loop = [(18, 6), (29, 6), (34, 11), (34, 28), (29, 33), (10, 33), (5, 28), (5, 11)]
    d.line(loop, fill=rgba(W_), width=3, joint=None)
    for x, y in loop[1:-1]:
        d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=rgba(W_))
    d.line([(15, 6), (18, 6)], fill=rgba(W_), width=1)          # the tail tapers into the via
    d.line([(17, 5), (18, 5)], fill=rgba(W_), width=1)
    d.line([(17, 7), (18, 7)], fill=rgba(W_), width=1)
    shade_edges(im, None, W_, S_)
    stamp(im, 3, 2, HEAD, {"#": W_, "s": S_, "e": C["LOGO_RED"]})
    px = im.load()
    for x, y in ((12, 5), (13, 5), (14, 5), (12, 6), (14, 6), (12, 7), (13, 7), (14, 7)):   # the via, in its jaws
        px[x, y] = rgba(C["ENIG_GOLD"])
    px[12, 5] = rgba(C["GOLD_HIGHLIGHT"])
    px[13, 6] = rgba(C["BLACK_MASK_DEEP"])
    # a chip in the middle of the loop, wired to the snake
    d.rectangle([15, 15, 24, 24], fill=rgba(C["IC_DARK"]))
    d.rectangle([15, 15, 24, 15], fill=rgba(C["IC_GREY"]))
    px[17, 17] = rgba(C["IC_GREY"])
    for k in (17, 20, 23):
        for (x, y) in ((k, 13), (k, 14), (k, 25), (k, 26), (13, k), (14, k), (25, k), (26, k)):
            px[x, y] = rgba(C["ENIG_GOLD"])
    for y in range(8, 13):                                     # two chip pins routed out to the loop
        px[23, y] = rgba(C["COPPER"])
    for x in range(27, 33):
        px[x, 23] = rgba(C["COPPER"])
    return im


# ================================================================= B: coil ouroboros
def mark_b():
    n = 40
    im, d = canvas(n)
    cx, cy, ro, ri = 20, 20, 14.5, 8.5
    px = im.load()
    COP, COP_D, GOLD, GOLD_HI = C["COPPER"], C["COPPER_SHADOW"], C["ENIG_GOLD"], C["GOLD_HIGHLIGHT"]
    for lx in (15, 25):                                        # a through-hole toroid stands on two leads
        for y in range(31, 39):
            px[lx, y] = rgba(C["SILKSCREEN_SHADE"])
        px[lx, 38] = rgba(C["SILKSCREEN_WHITE"])
    gap0, gap1 = math.radians(-132), math.radians(-60)          # where the head meets the tail
    turns = 26
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if not (ri <= r <= ro):
                continue
            a = math.atan2(dy, dx)
            if gap0 < a < gap1:
                continue
            f = ((a + math.pi) / (2 * math.pi)) * turns
            wire = (f % 1.0) < 0.62                                 # copper turns, with the dark core between them
            if not wire:
                col = C["IC_BLACK"]
            else:
                lit = (-dx * 0.7 - dy) > 2
                col = GOLD if lit else COP
                if r > ro - 1.2:
                    col = COP if lit else COP_D
            px[x, y] = rgba(col)
    # neck: the ring's left end rises into the head
    d.polygon([(10, 14), (12, 9), (18, 9), (16, 12), (13, 15)], fill=rgba(COP))
    d.line([(11, 13), (13, 9)], fill=rgba(GOLD))
    # the tail: tapers from the ring's right end up into the jaws
    d.line([(27, 12), (25, 9), (23, 7)], fill=rgba(COP), width=2)
    d.line([(24, 7), (22, 6)], fill=rgba(COP), width=1)
    d.line([(28, 12), (26, 10)], fill=rgba(COP_D), width=1)
    stamp(im, 11, 2, HEAD, {"#": GOLD, "s": COP_D, "e": C["LOGO_RED"]})
    for x in range(12, 20):                                     # a lit ridge along the head
        if px[x, 3][3]:
            px[x, 3] = rgba(GOLD_HI)
    return im


# ================================================================= sheets
def lockup(mark, scale, bg, words=("TRACEWINDER", "LABS")):
    """Mark plus the name in the site's pixel letters, on a background colour."""
    tw = max(text_width(w, scale) for w in words)
    h = mark.height * scale
    W_ = mark.width * scale + scale * 6 + tw + scale * 8
    im = Image.new("RGBA", (W_, h + scale * 8), rgba(bg))
    m = mark.resize((mark.width * scale, mark.height * scale), Image.NEAREST)
    im.paste(m, (scale * 4, scale * 4), m)
    x0 = mark.width * scale + scale * 8
    y = scale * 4 + (h - (len(words) * 6 - 1) * scale) // 2
    for i, w in enumerate(words):
        for dx, dy in text_pixels(w, scale):
            im.putpixel((x0 + dx, y + i * 6 * scale + dy), rgba(C["SILKSCREEN_WHITE"] if i == 0 else C["SILKSCREEN_SHADE"]))
    return im


def sheet(marks):
    bg = C["BLACK_MASK"]
    rows = []
    for name, m in marks:
        big = m.resize((m.width * 8, m.height * 8), Image.NEAREST)
        lk = lockup(m, 3, bg)
        small = [m.resize((m.width * k, m.height * k), Image.NEAREST) for k in (1, 2)]
        w = big.width + 40 + max(lk.width, 200)
        row = Image.new("RGBA", (w, big.height + 40), rgba(bg))
        row.paste(big, (20, 20), big)
        row.paste(lk, (big.width + 40, 20), lk)
        x = big.width + 40
        for s in small:                                              # actual small sizes: favicon, header
            row.paste(s, (x, 20 + lk.height + 30), s)
            x += s.width + 20
        for dx, dy in text_pixels(name, 2):
            row.putpixel((big.width + 40 + dx, big.height + 4 + dy - 10), rgba(C["SILKSCREEN_SHADE"]))
        rows.append(row)
    W_ = max(r.width for r in rows)
    out = Image.new("RGBA", (W_, sum(r.height for r in rows)), rgba(bg))
    y = 0
    for r in rows:
        out.paste(r, (0, y))
        y += r.height
    return out


if __name__ == "__main__":
    a, b = mark_a(), mark_b()
    for key, m in (("a-trace", a), ("b-coil", b)):
        m.save(OUT / f"mark-{key}-1x.png")
        m.resize((m.width * 8, m.height * 8), Image.NEAREST).save(OUT / f"mark-{key}-8x.png")
        lockup(m, 4, C["BLACK_MASK"]).save(OUT / f"lockup-{key}.png")
    sheet([("A  TRACE OUROBOROS", a), ("B  COIL OUROBOROS", b)]).save(OUT / "proposals-sheet.png")
    print("wrote", sorted(p.name for p in OUT.iterdir()))
