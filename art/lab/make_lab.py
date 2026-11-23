#!/usr/bin/env python3
"""The Lab: luci3D's workshop, the shop page's header (and the game's lab).

Half e-waste pile, half slapped-together supercomputer. Cables sag from the
ceiling with FPV goggles hanging off them, ready to grab. Server racks built
from salvaged boards blink at the back, a workbench sits under a magnifier lamp,
and piles of boards, packs, props and frames wait to be fixed.

One-point perspective, drawn at the street-view resolution (480 x 270) and
scaled up with hard pixels. Flat shapes, no outlines, palette colours only.
Inspired by the cyberpunk back-alley clinic look; all designs are our own.

    python3 art/lab/make_lab.py   -> art/lab/out/lab-v1.png (1440 x 810), lab-v1-1x.png
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "brand" / "tools"))
import palette  # noqa: E402
from font3x5 import text_pixels, text_width  # noqa: E402

P = palette.load()
globals().update({k.upper().replace(" ", "_"): v for k, v in P.items()})

W, H, S = 480, 270, 3
rng = random.Random(5)
im = Image.new("RGB", (W, H), VOID_DEEP)
d = ImageDraw.Draw(im)

VP = (240, 112)                       # vanishing point
BW = (100, 30, 380, 172)              # back wall: x0, y0, x1, y1


def R(x0, y0, x1, y1, c):
    d.rectangle([round(x0), round(y0), round(x1), round(y1)], fill=c)


def poly(pts, c):
    d.polygon([(round(x), round(y)) for x, y in pts], fill=c)


def line(pts, c, w=1):
    d.line([(round(x), round(y)) for x, y in pts], fill=c, width=w)


def ell(cx, cy, rx, ry, c):
    d.ellipse([round(cx - rx), round(cy - ry), round(cx + rx), round(cy + ry)], fill=c)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        im.putpixel((int(x), int(y)), c)


def text(s, x, y, c, scale=1):
    for dx, dy in text_pixels(s, scale):
        px(x + dx, y + dy, c)


def toward_vp(x, y, t):
    """A point t of the way from (x, y) to the vanishing point."""
    return x + (VP[0] - x) * t, y + (VP[1] - y) * t


def sag(x0, y0, x1, y1, dip, n=24):
    return [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n + dip * math.sin(math.pi * i / n)) for i in range(n + 1)]


# ================================================================= the room
x0, y0, x1, y1 = BW
poly([(0, 0), (W, 0), (x1, y0), (x0, y0)], IC_BLACK)                    # ceiling
poly([(x0, y1), (x1, y1), (W, H), (0, H)], BLACK_MASK)                  # floor
poly([(0, 0), (x0, y0), (x0, y1), (0, H)], VOID)                        # left wall
poly([(W, 0), (x1, y0), (x1, y1), (W, H)], VOID)                        # right wall
R(x0, y0, x1, y1, VOID_MID)                                             # back wall
for k in range(1, 9):                                                    # floor tiles
    t = (k / 9) ** 1.7
    yy = y1 + (H - y1) * t
    line([(x0 - (x0 - 0) * t, yy), (x1 + (W - x1) * t, yy)], BLACK_TRACE)
for xb in range(0, W + 1, 60):
    line([(xb, H), toward_vp(xb, H, 0.58)], BLACK_TRACE)
for xb in (60, 180, 300, 420):                                          # ceiling cable trays
    a, b = (xb, 0), toward_vp(xb, 0, 0.73)
    line([a, b], IC_DARK, 3)
    line([(a[0] + 2, a[1]), (b[0] + 1, b[1])], IC_GREY)
for k in range(1, 5):                                                    # tray rungs
    t = 0.73 * (k / 5) ** 1.3
    yy = toward_vp(0, 0, t)[1]
    line([toward_vp(0, 0, t), toward_vp(W, 0, t)], IC_DARK)
R(x0, y0, x1, y0 + 1, SIGNAL_PINK)                                       # neon strip along the back wall
R(x0, y0 + 2, x1, y0 + 4, GRAFFITI_PURPLE)
R(x0, y0 + 5, x1, y0 + 7, DUSK_PURPLE)

# ================================================================= back wall: the slapped-together supercomputer
LEDS = [GLOW_TEAL, SIGNAL_PINK, WIRE_YELLOW, SIGNAL_TEAL, LOGO_RED]


def rack(x, y, w, h, kind):
    R(x - 1, y - 1, x + w + 1, y + h, IC_DARK)
    R(x, y, x + w, y + h, IC_BLACK)
    yy = y + 2
    while yy < y + h - 6:
        uh = rng.choice([5, 6, 8, 10])
        style = rng.random()
        if kind == "salvage" and style < 0.35:                          # a bare green board, bolted in
            R(x + 2, yy, x + w - 2, yy + uh - 2, MASK)
            for i in range(3):
                line([(x + 4, yy + 1 + i * 2), (x + w - 4 - rng.randrange(0, 8), yy + 1 + i * 2)], TRACE_HIGHLIGHT)
            R(x + w // 2 - 3, yy + 1, x + w // 2 + 3, yy + uh - 3, IC_DARK)
        elif style < 0.6:                                               # a black board, gold pads
            R(x + 2, yy, x + w - 2, yy + uh - 2, BLACK_TRACE)
            for i in range(x + 4, x + w - 4, 4):
                px(i, yy + uh - 3, ENIG_GOLD)
        else:                                                           # a server blade
            R(x + 2, yy, x + w - 2, yy + uh - 2, IC_DARK)
            R(x + 2, yy, x + w - 2, yy, IC_GREY)
        for i in range(rng.randrange(1, 5)):                            # blinking LEDs
            px(x + 4 + rng.randrange(0, w - 8), yy + rng.randrange(1, max(2, uh - 2)), rng.choice(LEDS))
        yy += uh
    for i in range(2):                                                  # cable loops out of the front
        cx = x + 3 + rng.randrange(0, w - 6)
        line(sag(cx, y + 6 + 20 * i, cx + rng.randrange(-8, 8), y + h - 2, rng.randrange(4, 10)),
             rng.choice([IC_GREY, WIRE_BLUE, LOGO_RED, WIRE_YELLOW]))


def fan(cx, cy, r):
    ell(cx, cy, r, r, IC_DARK)
    ell(cx, cy, r - 1, r - 1, IC_BLACK)
    for a in range(0, 360, 60):
        line([(cx, cy), (cx + (r - 1) * math.cos(math.radians(a + 20)), cy + (r - 1) * math.sin(math.radians(a + 20)))],
             IC_GREY)
    ell(cx, cy, 1, 1, IC_GREY)


def screen(x, y, w, h, content):
    R(x - 2, y - 2, x + w + 2, y + h + 3, IC_GREY)                       # bezel
    R(x - 2, y + h + 2, x + w + 2, y + h + 3, IC_DARK)
    R(x, y, x + w, y + h, SIGNAL_TEAL_DEEP)
    for yy in range(y, y + h, 2):                                         # scanlines
        line([(x, yy), (x + w, yy)], VOID if content == "dark" else SIGNAL_TEAL_DEEP)
    if content == "logo":
        grid = (ROOT / "brand" / "tools" / "make_logo.py").read_text().split('GRID = """')[1].split('"""')[0]
        rows = grid.strip("\n").splitlines()
        ox, oy = x + (w - len(rows[0])) // 2, y + (h - len(rows)) // 2
        for yy, row in enumerate(rows):
            for xx, ch in enumerate(row):
                if ch == "#":
                    px(ox + xx, oy + yy, GLOW_TEAL)
                elif ch == "r":
                    px(ox + xx, oy + yy, SIGNAL_PINK)
    elif content == "osd":                                                # an FPV feed with OSD
        line([(x + 2, y + h // 2 + 3), (x + w - 2, y + h // 2 - 2)], GLOW_TEAL)
        text("REC", x + w - 13, y + 2, SIGNAL_PINK)
        R(x + w // 2 - 1, y + h // 2 - 1, x + w // 2 + 1, y + h // 2 + 1, GLOW_TEAL)
    elif content == "code":
        for i in range(0, h - 2, 3):
            line([(x + 2 + rng.randrange(0, 6), y + 2 + i), (x + 2 + rng.randrange(8, w - 3), y + 2 + i)], SIGNAL_TEAL)
    elif content == "wave":
        line([(x + i, y + h / 2 + math.sin(i / 2.2) * (h / 3) * math.sin(i / 9)) for i in range(0, w + 1)], GLOW_TEAL)


# light from the screens on the back wall
ell(240, 92, 74, 40, DUSK_PURPLE)
rack(106, 48, 46, 124, "salvage")
rack(158, 66, 28, 106, "blade")
rack(294, 66, 28, 106, "salvage")
rack(328, 48, 46, 124, "blade")
# middle shelf: monitors and a heap of boards
R(192, 116, 288, 118, SILKSCREEN_SHADE)                                  # shelf
R(192, 119, 288, 119, IC_GREY)
for xx in (194, 286):
    R(xx, 54, xx + 1, 172, SILKSCREEN_SHADE)
screen(208, 60, 64, 40, "logo")
screen(194 + 2, 124, 26, 18, "osd")
screen(226, 124, 26, 18, "code")
screen(258, 124, 26, 18, "wave")
for i in range(5):                                                       # small boards stacked under the shelf
    bx = 196 + i * 18
    R(bx, 150, bx + 14, 152 + 0, BLACK_TRACE)
    R(bx, 153, bx + 14, 160, MASK if i % 2 else BLACK_TRACE)
    px(bx + 2 + i, 155, rng.choice(LEDS))
    px(bx + 10, 157, rng.choice(LEDS))
for xx in range(198, 286, 7):                                            # cable fall from the shelf to the floor
    line(sag(xx, 160, xx + rng.randrange(-6, 6), 172 + rng.randrange(0, 6), rng.randrange(2, 6), 8),
         rng.choice([IC_DARK, IC_GREY, WIRE_BLUE, LOGO_RED]))

# ================================================================= ceiling: cables and hanging goggles
CABLE = [IC_DARK, IC_DARK, IC_GREY, LOGO_RED, WIRE_YELLOW, WIRE_BLUE, IC_DARK, SIGNAL_TEAL_DEEP]
anchors = []
for i in range(16):                                                      # sagging runs across the ceiling
    xa = rng.randrange(-40, W + 40)
    xb = xa + rng.choice([-1, 1]) * rng.randrange(60, 200)
    ya = max(0, toward_vp(xa, 0, rng.uniform(0.0, 0.5))[1])
    yb = max(0, toward_vp(xb, 0, rng.uniform(0.0, 0.5))[1])
    pts = sag(xa, ya, xb, yb, rng.randrange(14, 56))
    col = rng.choice(CABLE)
    line(pts, col, rng.choice([1, 1, 2]))
    anchors.append(pts)
for i in range(9):                                                       # drops that end in a plug
    x = rng.randrange(20, W - 20)
    top = max(0, toward_vp(x, 0, 0.3)[1])
    bot = rng.randrange(40, 110)
    col = rng.choice(CABLE)
    line([(x, top), (x + rng.randrange(-2, 3), bot)], col)
    plug = rng.choice(["xt60", "jst", "usb"])
    if plug == "xt60":
        R(x - 2, bot, x + 2, bot + 5, WIRE_YELLOW)
        R(x - 2, bot + 5, x + 2, bot + 5, ENIG_GOLD)
    elif plug == "jst":
        R(x - 1, bot, x + 2, bot + 3, SILKSCREEN_WHITE)
    else:
        R(x - 1, bot, x + 1, bot + 4, IC_GREY)
        R(x - 1, bot + 4, x + 1, bot + 5, SILKSCREEN_SHADE)


def goggles(cx, top, size, body=IC_DARK, foam=DUSK_PURPLE, ant=LOGO_RED):
    """FPV goggles hanging by their strap, face side toward us: foam, two lenses,
    a nose cut-out, antennas on top and the power LED on. size ~ 1.0 for the near ones."""
    w, h = round(38 * size), round(17 * size)
    hang = round(12 * size)
    line([(cx - w * 0.42, top + hang + 2), (cx, top), (cx + w * 0.42, top + hang + 2)], IC_GREY, max(1, round(2 * size)))
    y = top + hang
    for sx in (-1, 1):                                                    # antennas
        ax = cx + sx * w * 0.3
        line([(ax, y), (ax + sx * 2 * size, y - 7 * size)], IC_GREY, max(1, round(size)))
        ell(ax + sx * 2 * size, y - 7 * size - 1, max(1, 2.2 * size), max(1, 1.6 * size), ant)
    R(cx - w / 2, y, cx + w / 2, y + h, body)                             # shell
    R(cx - w / 2, y, cx + w / 2, y + max(1, h // 7), SHADE_LIT.get(body, IC_GREY))
    R(cx - w / 2 + 2 * size, y + h * 0.22, cx + w / 2 - 2 * size, y + h - 1, foam)   # foam faceplate
    for sx in (-1, 1):                                                    # lenses
        lx = cx + sx * w * 0.22
        ell(lx, y + h * 0.58, w * 0.15, h * 0.26, IC_BLACK)
        px(lx - w * 0.06, y + h * 0.48, GLOW_TEAL)
    poly([(cx - 3 * size, y + h + 1), (cx, y + h * 0.62), (cx + 3 * size, y + h + 1)], VOID)   # nose cut-out
    px(cx + w / 2 - 3, y + 1 + max(1, h // 7), GLOW_TEAL)                # power LED: ready to go
    R(cx - w / 2 - max(1, size), y + h * 0.25, cx - w / 2, y + h * 0.75, IC_GREY)   # strap mounts
    R(cx + w / 2, y + h * 0.25, cx + w / 2 + max(1, size), y + h * 0.75, IC_GREY)


SHADE_LIT = {IC_DARK: IC_GREY, SILKSCREEN_WHITE: SILKSCREEN_WHITE, IC_BLACK: IC_DARK, LOGO_RED: SIGNAL_PINK}

# ================================================================= workbench
bench = [(150, 190), (330, 190), (346, 206), (134, 206)]
ell(240, 214, 120, 18, BLACK_TRACE)                                       # light pool under the lamp, on the floor
for lx in (142, 334):                                                     # legs
    R(lx, 206, lx + 4, 246, IC_DARK)
poly(bench, WIRE_BLUE_DEEP)                                               # ESD mat
poly([(134, 206), (346, 206), (346, 211), (134, 211)], IC_DARK)            # bench edge
poly([(170, 192), (300, 192), (306, 202), (164, 202)], WIRE_BLUE)          # lit area under the magnifier
# the quad being built: carbon X, four motors, the stack in the middle
qc = (236, 197)
for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
    mx, my = qc[0] + sx * 22, qc[1] + sy * 5
    line([qc, (mx, my)], IC_BLACK, 3)
    ell(mx, my, 4, 2, SILKSCREEN_SHADE)
    ell(mx, my - 1, 3, 1, SILKSCREEN_WHITE)
    line([(mx - 9, my - 2), (mx + 9, my - 2)], SIGNAL_PINK)              # props
R(qc[0] - 6, qc[1] - 4, qc[0] + 6, qc[1] + 2, BLACK_TRACE)
R(qc[0] - 6, qc[1] - 4, qc[0] + 6, qc[1] - 4, IC_GREY)
px(qc[0] + 4, qc[1] - 2, LOGO_RED)
# soldering station, iron with a hot tip, a multimeter
R(160, 186, 182, 197, IC_GREY)
R(160, 186, 182, 187, SILKSCREEN_SHADE)
text("350", 163, 189, LOGO_RED)
line([(186, 192), (200, 184)], SILKSCREEN_SHADE, 2)
px(201, 183, LOGO_RED)
px(202, 182, SIGNAL_PINK)
R(290, 185, 302, 199, WIRE_YELLOW)
R(292, 187, 300, 191, SIGNAL_TEAL_DEEP)
ell(296, 195, 2, 2, IC_DARK)
# the magnifier lamp: arm from the right wall, ring light
line([(W, 96), (320, 128), (262, 150), (240, 160)], SILKSCREEN_SHADE, 3)     # arm off the right wall
line([(W, 94), (320, 126), (262, 148)], IC_GREY)
line([(240, 160), (237, 168)], SILKSCREEN_SHADE, 2)
ell(236, 171, 15, 4, IC_GREY)                                                # ring light over the quad
ell(236, 170, 13, 3, SILKSCREEN_WHITE)
ell(236, 170, 9, 2, GLOW_TEAL)

# ================================================================= the piles: boards, packs, props, frames
def board(x, y, w, h, green):
    x, y = int(x), int(y)
    R(x, y, x + w, y + h, MASK if green else BLACK_TRACE)
    R(x, y, x + w, y, TRACE_HIGHLIGHT if green else IC_GREY)
    for i in range(rng.randrange(1, 4)):
        cx, cy = x + rng.randrange(2, max(3, w - 4)), y + rng.randrange(2, max(3, h - 3))
        R(cx, cy, cx + rng.randrange(2, 6), cy + rng.randrange(2, 4), IC_DARK)
    for i in range(x + 2, x + w - 1, 3):
        px(i, y + h - 1, ENIG_GOLD)


def pack(x, y, w, h, col):
    R(x, y, x + w, y + h, col)
    R(x, y, x + w, y, SILKSCREEN_WHITE)
    R(x + 1, y + h - 2, x + w - 1, y + h - 1, SHADE_DARK[col])
    line([(x + w, y + 2), (x + w + 4, y + 6)], LOGO_RED)
    line([(x + w, y + 4), (x + w + 4, y + 9)], IC_DARK)


SHADE_DARK = {WIRE_YELLOW: ENIG_GOLD, WIRE_BLUE: WIRE_BLUE_DEEP, LOGO_RED: BURN_RED, GRAFFITI_PURPLE: DUSK_PURPLE}


def pile(x0, x1, ybase, n):
    poly([(x0, ybase), (x0 + (x1 - x0) * 0.2, ybase - 34), (x0 + (x1 - x0) * 0.6, ybase - 46),
          (x1, ybase - 20), (x1, ybase + 4), (x0, ybase + 4)], IC_BLACK)    # the heap's dark mass
    for i in range(n):
        t = rng.random()
        x = x0 + (x1 - x0) * rng.random()
        top = ybase - 40 * math.sin(math.pi * (x - x0) / (x1 - x0)) * 0.9
        y = rng.uniform(top, ybase)
        k = rng.random()
        if k < 0.45:
            board(x, y, rng.randrange(10, 24), rng.randrange(6, 12), rng.random() < 0.5)
        elif k < 0.65:
            pack(x, y, rng.randrange(10, 16), rng.randrange(6, 9), rng.choice(list(SHADE_DARK)))
        elif k < 0.8:                                                      # a broken prop
            line([(x, y), (x + rng.randrange(8, 14), y - rng.randrange(-3, 4))], rng.choice([SIGNAL_PINK, WIRE_YELLOW, GLOW_TEAL]), 2)
        elif k < 0.9:                                                      # a motor
            ell(x, y, 3, 2, SILKSCREEN_SHADE)
            ell(x, y - 1, 2, 1, SILKSCREEN_WHITE)
        else:                                                              # a frame arm
            line([(x, y), (x + rng.randrange(14, 24), y + rng.randrange(-6, 6))], IC_DARK, 3)
    for i in range(6):                                                     # cables tangled over the top
        xa = rng.uniform(x0, x1)
        line(sag(xa, ybase - rng.randrange(10, 30), xa + rng.randrange(-30, 30), ybase - rng.randrange(0, 20),
                 -rng.randrange(4, 12), 10), rng.choice(CABLE))


pile(-10, 128, 262, 46)
pile(352, 492, 262, 46)
# a cardboard box of things to fix
R(40, 210, 88, 246, FR4_EDGE)
R(40, 210, 88, 214, FR4_SHADE)
poly([(40, 210), (52, 200), (78, 200), (88, 210)], FR4_SHADE)
text("TO FIX", 50, 226, IC_DARK)
board(46, 204, 18, 8, True)
pack(66, 203, 12, 7, WIRE_BLUE)

# hanging goggles in front of everything else, near ones bigger
for (cx, top, size, body, ant) in [(70, 18, 1.1, IC_DARK, LOGO_RED), (150, 34, 0.7, SILKSCREEN_WHITE, GLOW_TEAL),
                                   (214, 30, 0.55, IC_DARK, WIRE_YELLOW), (304, 36, 0.6, IC_DARK, WIRE_BLUE),
                                   (354, 22, 0.85, LOGO_RED, IC_DARK), (430, 10, 1.25, IC_DARK, GLOW_TEAL)]:
    line([(cx, 0), (cx, top)], IC_DARK)                                    # hook cord from the ceiling
    goggles(cx, top, size, body, IC_GREY if body == SILKSCREEN_WHITE else DUSK_PURPLE, ant)

out = Path(__file__).resolve().parent / "out"
out.mkdir(exist_ok=True)
im.save(out / "lab-v1-1x.png")
im.resize((W * S, H * S), Image.NEAREST).save(out / "lab-v1.png")
print("wrote", out)
