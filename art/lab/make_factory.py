#!/usr/bin/env python3
"""The Line: the Lab's manufacturing bay.

A pick-and-place machine feeds a reflow oven, two 3D printers run on the side
bench, and the packing station holds trays of fresh boards and a stack of boxes
ready to ship, each with the luci3D snake printed on it. Still some clutter and
an e-waste heap in the corner, but the machines are the stars.

Same room and style as make_lab.py: one-point perspective at 480 x 270, scaled
up with hard pixels, flat shapes, palette colours only.

    python3 art/lab/make_factory.py   -> art/lab/out/line-v1.png (1440 x 810), line-v1-1x.png
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "brand" / "tools"))
import palette  # noqa: E402
from font3x5 import text_pixels  # noqa: E402

P = palette.load()
globals().update({k.upper().replace(" ", "_"): v for k, v in P.items()})

W, H, S = 480, 270, 3
rng = random.Random(8)
im = Image.new("RGB", (W, H), VOID_DEEP)
d = ImageDraw.Draw(im)
VP = (240, 112)
BW = (100, 30, 380, 172)


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


def tv(x, y, t):
    """The point t of the way from (x, y) toward the vanishing point."""
    return x + (VP[0] - x) * t, y + (VP[1] - y) * t


def sag(x0, y0, x1, y1, dip, n=24):
    return [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n + dip * math.sin(math.pi * i / n)) for i in range(n + 1)]


def box3(x0, x1, yb, h, t, top, front, side):
    """A block standing on the floor: front face x0..x1, from yb up h, depth t toward the VP."""
    yt = yb - h
    if x1 < VP[0]:
        poly([(x1, yt), (x1, yb), tv(x1, yb, t), tv(x1, yt, t)], side)
    if x0 > VP[0]:
        poly([(x0, yt), (x0, yb), tv(x0, yb, t), tv(x0, yt, t)], side)
    if yt > VP[1]:
        poly([(x0, yt), (x1, yt), tv(x1, yt, t), tv(x0, yt, t)], top)
    R(x0, yt, x1, yb, front)
    return yt


LOGO = (ROOT / "brand" / "tools" / "make_logo.py").read_text().split('GRID = """')[1].split('"""')[0]
LOGO_ROWS = LOGO.strip("\n").splitlines()


def logo(x, y, c, step=1):
    """The snake, at full size (step 1) or half size (step 2), as printed ink."""
    for yy in range(0, len(LOGO_ROWS), step):
        for xx in range(0, len(LOGO_ROWS[0]), step):
            cell = [LOGO_ROWS[j][i] for j in range(yy, min(yy + step, len(LOGO_ROWS)))
                    for i in range(xx, min(xx + step, len(LOGO_ROWS[0])))]
            if "#" in cell:
                px(x + xx // step, y + yy // step, c)
            elif "r" in cell:
                px(x + xx // step, y + yy // step, LOGO_RED)


def pcb(x, y, w, h, green=False, leds=True):
    x, y = int(x), int(y)
    R(x, y, x + w, y + h, MASK if green else BLACK_TRACE)
    R(x, y, x + w, y, TRACE_HIGHLIGHT if green else IC_GREY)
    for i in range(rng.randrange(1, 3)):
        cx, cy = x + rng.randrange(1, max(2, w - 3)), y + rng.randrange(1, max(2, h - 1))
        R(cx, cy, cx + min(3, w // 3), cy + 1, IC_DARK)
    for i in range(x + 1, x + w, 3):
        px(i, y + h, ENIG_GOLD)
    if leds:
        px(x + w - 2, y + 1, rng.choice([GLOW_TEAL, LOGO_RED]))


# ================================================================= the room (same bay as the Lab)
x0, y0, x1, y1 = BW
poly([(0, 0), (W, 0), (x1, y0), (x0, y0)], IC_BLACK)
poly([(x0, y1), (x1, y1), (W, H), (0, H)], BLACK_MASK)
poly([(0, 0), (x0, y0), (x0, y1), (0, H)], VOID)
poly([(W, 0), (x1, y0), (x1, y1), (W, H)], VOID)
R(x0, y0, x1, y1, VOID_MID)
for k in range(1, 9):
    t = (k / 9) ** 1.7
    yy = y1 + (H - y1) * t
    line([(x0 - x0 * t, yy), (x1 + (W - x1) * t, yy)], BLACK_TRACE)
for xb in range(0, W + 1, 60):
    line([(xb, H), tv(xb, H, 0.58)], BLACK_TRACE)
for xb in (60, 180, 300, 420):
    a, b = (xb, 0), tv(xb, 0, 0.73)
    line([a, b], IC_DARK, 3)
    line([(a[0] + 2, a[1]), (b[0] + 1, b[1])], IC_GREY)
R(x0, y0, x1, y0 + 1, SIGNAL_PINK)
R(x0, y0 + 2, x1, y0 + 4, GRAFFITI_PURPLE)
R(x0, y0 + 5, x1, y0 + 7, DUSK_PURPLE)

# light pools from the shop lamps
for cx, cy, rx in ((210, 196, 110), (400, 222, 70), (80, 236, 80)):
    ell(cx, cy, rx, rx * 0.2, BLACK_TRACE)

# ================================================================= back wall: reels, the production board
for k, ys in enumerate((48, 72, 96, 120, 144)):                          # reel shelving
    R(104, ys + 14, 152, ys + 15, SILKSCREEN_SHADE)
    for i in range(4):
        cx = 110 + i * 12
        ell(cx, ys + 7, 6, 7, IC_BLACK)
        ell(cx, ys + 7, 5, 6, IC_DARK)
        ell(cx, ys + 7, 2, 2, rng.choice([WIRE_YELLOW, WIRE_BLUE, SILKSCREEN_WHITE, LOGO_RED, GLOW_TEAL]))
R(102, 46, 103, 162, SILKSCREEN_SHADE)
R(153, 46, 154, 162, SILKSCREEN_SHADE)
R(300, 44, 374, 84, IC_GREY)                                             # production dashboard
R(302, 46, 372, 82, SIGNAL_TEAL_DEEP)
text("LINE 01", 305, 49, GLOW_TEAL)
for i, hgt in enumerate((14, 20, 11, 24, 18, 22)):
    R(306 + i * 10, 78 - hgt, 312 + i * 10, 78, GLOW_TEAL if i != 2 else SIGNAL_PINK)

# ================================================================= ceiling: a few runs, shop lamps
for i in range(7):
    xa = rng.randrange(-20, W + 20)
    xb = xa + rng.choice([-1, 1]) * rng.randrange(60, 160)
    ya, yb = tv(xa, 0, rng.uniform(0, 0.45))[1], tv(xb, 0, rng.uniform(0, 0.45))[1]
    line(sag(xa, max(0, ya), xb, max(0, yb), rng.randrange(8, 30)), rng.choice([IC_DARK, IC_GREY, WIRE_BLUE, LOGO_RED]))
for lx, ly, sz in ((210, 44, 1.0), (400, 30, 1.2), (80, 26, 1.3)):        # shop lamps
    line([(lx, 0), (lx, ly)], IC_DARK)
    poly([(lx - 10 * sz, ly + 8 * sz), (lx - 3 * sz, ly), (lx + 3 * sz, ly), (lx + 10 * sz, ly + 8 * sz)], IC_GREY)
    poly([(lx - 10 * sz, ly + 8 * sz), (lx + 10 * sz, ly + 8 * sz), (lx + 8 * sz, ly + 9 * sz), (lx - 8 * sz, ly + 9 * sz)],
         SILKSCREEN_WHITE)

# ================================================================= floor marking around the line
for xx in range(126, 384, 8):
    line([(xx, 186), (xx + 4, 186)], WIRE_YELLOW)

# ================================================================= pick-and-place machine
R(118, 148, 142, 152, IC_GREY)                                            # inlet conveyor, a panel going in
pcb(122, 145, 18, 3)
for i in range(4):                                                         # reel trolley
    ell(130, 158 + i * 6, 9, 3, IC_BLACK)
    ell(130, 157 + i * 6, 8, 2, IC_DARK)
    px(130, 157 + i * 6, rng.choice([WIRE_YELLOW, SILKSCREEN_WHITE, WIRE_BLUE]))
R(122, 178, 138, 182, IC_DARK)
top = box3(144, 292, 184, 64, 0.11, SILKSCREEN_WHITE, SILKSCREEN_SHADE, IC_GREY)
R(144, 178, 292, 184, IC_DARK)                                             # kick plate
R(150, top + 6, 286, top + 36, VOID_DEEP)                                  # the window
R(150, top + 6, 286, top + 7, IC_DARK)
line([(152, top + 11), (284, top + 11)], IC_GREY, 2)                       # gantry rail
R(198, top + 9, 214, top + 22, IC_DARK)                                    # placement head
R(198, top + 9, 214, top + 10, IC_GREY)
for i in range(4):
    line([(201 + i * 4, top + 22), (201 + i * 4, top + 26)], COPPER)       # nozzles
px(212, top + 13, GLOW_TEAL)
R(160, top + 29, 278, top + 30, IC_GREY)                                   # conveyor rails
pcb(174, top + 26, 54, 3)                                                  # the board being populated
R(150, top + 40, 286, top + 56, IC_GREY)                                   # feeder bank
for xx in range(152, 286, 5):
    R(xx, top + 42, xx + 3, top + 55, IC_DARK)
    px(xx + 1, top + 44, rng.choice([GLOW_TEAL, GLOW_TEAL, SIGNAL_PINK]))
text("PNP-01", 153, top + 58, IC_GREY)
R(148, top - 22, 149, top, IC_GREY)                                        # stack light
for i, c in enumerate((BURN_RED, COPPER_SHADOW, GLOW_TEAL)):
    R(146, top - 22 + i * 5, 151, top - 18 + i * 5, c)
R(296, top - 16, 314, top - 4, IC_GREY)                                    # screen on an arm
R(297, top - 15, 313, top - 5, SIGNAL_TEAL_DEEP)
line([(299, top - 12), (311, top - 12)], GLOW_TEAL)
line([(299, top - 9), (307, top - 9)], GLOW_TEAL)
line([(305, top - 4), (300, top + 6)], IC_GREY)

# ================================================================= reflow oven
otop = box3(296, 376, 184, 34, 0.1, IC_GREY, IC_DARK, IC_BLACK)
R(300, otop + 8, 372, otop + 16, VOID_DEEP)                                # heater window
for xx in range(302, 372, 6):
    line([(xx, otop + 9), (xx + 3, otop + 15)], LOGO_RED)
    px(xx + 1, otop + 11, WIRE_YELLOW)
R(300, otop + 20, 316, otop + 26, VOID_DEEP)
text("245", 301, otop + 21, LOGO_RED)
R(376, otop + 10, 392, otop + 13, IC_GREY)                                 # outlet conveyor, boards coming out
pcb(378, otop + 7, 12, 3)
R(292, otop + 12, 296, otop + 14, IC_GREY)

# ================================================================= 3D printers on the side bench
poly([(326, 200), (476, 200), (480, 208), (322, 208)], FR4_SHADE)          # bench top
R(322, 208, 480, 212, COPPER_SHADOW)
for lx in (328, 470):
    R(lx, 212, lx + 4, 254, IC_DARK)
# enclosed printer
ptop = box3(334, 392, 202, 58, 0.08, IC_GREY, IC_DARK, IC_BLACK)
R(338, ptop + 4, 388, ptop + 46, VOID_DEEP)                                # glass door
line([(339, ptop + 10), (387, ptop + 10)], IC_GREY)                        # gantry
R(356, ptop + 8, 366, ptop + 16, IC_DARK)                                  # hotend
px(361, ptop + 17, LOGO_RED)
px(364, ptop + 10, GLOW_TEAL)
R(342, ptop + 38, 384, ptop + 40, IC_GREY)                                 # bed
for i in range(7):                                                         # the print, layer by layer
    R(352 + i % 2, ptop + 37 - i * 2, 370 - i % 2, ptop + 37 - i * 2, GRAFFITI_PURPLE if i % 2 else SMOKE_VIOLET)
R(338, ptop + 48, 352, ptop + 54, SIGNAL_TEAL_DEEP)                        # screen
line([(340, ptop + 50), (349, ptop + 50)], GLOW_TEAL)
ell(372, ptop - 8, 10, 10, GRAFFITI_PURPLE)                                # spool on top
ell(372, ptop - 8, 6, 6, DUSK_PURPLE)
ell(372, ptop - 8, 2, 2, IC_GREY)
line([(372, ptop + 2), (372, ptop)], GRAFFITI_PURPLE)
# open-frame printer
R(404, 150, 407, 200, IC_DARK)
R(452, 150, 455, 200, IC_DARK)
R(404, 148, 455, 151, IC_DARK)
R(404, 148, 455, 148, IC_GREY)
line([(407, 176), (452, 176)], IC_GREY, 2)                                 # X gantry
R(422, 172, 432, 182, IC_DARK)                                             # hotend
px(427, 183, LOGO_RED)
R(410, 190, 450, 192, ENIG_GOLD)                                           # gold PEI bed
R(410, 193, 450, 194, COPPER)
for i in range(4):
    R(420, 189 - i, 434, 189 - i, WIRE_YELLOW if i % 2 else GOLD_HIGHLIGHT)   # a TPU mount coming up
R(400, 194, 459, 202, IC_DARK)                                             # base
R(402, 196, 412, 200, SIGNAL_TEAL_DEEP)
ell(430, 136, 10, 10, WIRE_YELLOW)                                         # spool
ell(430, 136, 6, 6, ENIG_GOLD)
ell(430, 136, 2, 2, IC_GREY)
R(429, 146, 431, 148, IC_GREY)
line(sag(436, 140, 428, 172, 6, 10), WIRE_YELLOW)                          # filament to the hotend

# ================================================================= packing station: fresh boards and boxes
poly([(0, 196), (150, 196), (156, 204), (0, 204)], FR4_SHADE)              # packing table
R(0, 204, 156, 208, COPPER_SHADOW)
for lx in (8, 146):
    R(lx, 208, lx + 4, 250, IC_DARK)
R(10, 182, 32, 194, SILKSCREEN_SHADE)                                      # anti-static bags
R(12, 184, 30, 185, SIGNAL_PINK)
R(14, 178, 36, 190, SILKSCREEN_WHITE)
R(16, 180, 34, 181, SIGNAL_PINK)
R(40, 186, 62, 194, LOGO_RED)                                              # tape gun
R(42, 182, 54, 186, IC_DARK)
ell(60, 184, 5, 5, COPPER)
for k in range(5):                                                         # ESD trays of fresh boards
    ty = 196 - k * 7
    box3(70, 148, ty, 6, 0.05, IC_DARK, IC_BLACK, IC_BLACK)
    for i in range(5):
        pcb(73 + i * 15, ty - 5, 12, 3, leds=False)


def ship_box(xa, xb, yb, h, t=0.05, label=True):
    yt = box3(xa, xb, yb, h, t, FR4_EDGE, FR4_SHADE, COPPER_SHADOW)
    if yt > VP[1]:                                                         # packing tape across the top
        mx = (xa + xb) / 2
        poly([(mx - 2, yt), (mx + 2, yt), tv(mx + 2, yt, t), tv(mx - 2, yt, t)], COPPER)
    logo(xa + 4, yt + 4, IC_BLACK, 2)                                      # a small printed snake
    if label:
        lw = (xb - xa) * 0.34
        R(xb - lw - 3, yb - h * 0.45, xb - 3, yb - 4, SILKSCREEN_WHITE)
        for i in range(3):
            line([(xb - lw - 1, yb - h * 0.45 + 3 + i * 3), (xb - 6 - i * 3, yb - h * 0.45 + 3 + i * 3)], IC_GREY)


# boxes ready to ship, kept low so the trays stay in view
ship_box(150, 182, 196, 14, label=False)                                   # one packed on the table
ship_box(4, 60, 236, 26)
ship_box(4, 66, 270, 34)
ship_box(70, 128, 270, 32)
ship_box(74, 120, 238, 22)
ship_box(132, 174, 268, 24)
ship_box(178, 206, 262, 16, label=False)

# a bit of everyday clutter on the floor
crng = random.Random(55)
for i in range(4):                                                         # power and data runs across the floor
    xa = crng.uniform(160, 300)
    line(sag(xa, 186, xa + crng.uniform(-80, 80), 250 + crng.uniform(0, 18), -crng.uniform(2, 8), 16),
         crng.choice([IC_DARK, IC_GREY, WIRE_BLUE]), 2)
ell(226, 236, 10, 3, IC_BLACK)                                             # a reel on the floor
ell(226, 235, 9, 2, IC_DARK)
px(226, 235, WIRE_YELLOW)
for (x, y) in ((198, 212), (262, 222), (300, 206)):                        # loose boards
    pcb(x, y, crng.randrange(8, 14), 4, green=crng.random() < 0.5, leds=False)
line([(318, 250), (330, 216)], IC_DARK, 3)                                 # a frame arm leaning on the bench
line([(317, 250), (329, 216)], IC_GREY)
R(214, 248, 248, 262, IC_DARK)                                             # a crate of empty trays
R(214, 248, 248, 249, IC_GREY)

# ================================================================= the corner heap (still some e-waste)
SHADE_DARK = {WIRE_YELLOW: ENIG_GOLD, WIRE_BLUE: WIRE_BLUE_DEEP, LOGO_RED: BURN_RED}
poly([(392, 270), (420, 236), (452, 226), (486, 240), (486, 270)], IC_BLACK)
for i in range(30):
    x = rng.uniform(398, 480)
    y = rng.uniform(232, 266)
    k = rng.random()
    if k < 0.55:
        pcb(x, y, rng.randrange(8, 18), rng.randrange(4, 8), green=rng.random() < 0.6, leds=False)
    elif k < 0.8:
        col = rng.choice(list(SHADE_DARK))
        R(x, y, x + 10, y + 6, col)
        R(x, y, x + 10, y, SILKSCREEN_WHITE)
    else:
        line([(x, y), (x + rng.randrange(8, 16), y + rng.randrange(-4, 4))], rng.choice([SIGNAL_PINK, WIRE_YELLOW]), 2)
R(440, 240, 476, 270, IC_DARK)                                             # scrap bin
R(440, 240, 476, 242, IC_GREY)
text("SCRAP", 448, 252, WIRE_YELLOW)

out = Path(__file__).resolve().parent / "out"
out.mkdir(exist_ok=True)
im.save(out / "line-v1-1x.png")
im.resize((W * S, H * S), Image.NEAREST).save(out / "line-v1.png")
print("wrote", out)
