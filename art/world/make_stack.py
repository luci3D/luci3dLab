#!/usr/bin/env python3
"""The Stack, v2: an old flight controller and a 4-in-1 ESC as one city, in perspective.

Two passes:
  1. Plan: the boards drawn flat, top-down (black mask, white silkscreen, copper,
     grime, and the top face of every part). Every part also registers a 3D object.
  2. View: a perspective camera looks down from the south. The plan is projected
     onto the board plane, parts are extruded into blocks, wires sag in 3D, the
     boards are slabs with FR4 edges, and the carbon frame is the floor far below.

Flat shapes, no outlines, light from the north-west, every shadow is the next
darker palette colour. Only colours from brand/palette/luci3d.gpl.

    python3 art/world/make_stack.py
      -> art/world/out/stack-v2.png        the perspective view (1600x900)
      -> art/world/out/stack-v2-plan.png   the flat plan (level-design reference)
"""
import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "brand" / "tools"))
import palette  # noqa: E402
from font3x5 import text_pixels, text_width  # noqa: E402

P = palette.load()
for _k in list(P):
    globals()[_k.upper().replace(" ", "_").replace("-", "_")] = P[_k]

rng = random.Random(7)

# Board colours: black solder mask, copper under it shows as a lighter black.
BM, BM_D, TR, TR_HI = BLACK_MASK, BLACK_MASK_DEEP, BLACK_TRACE, BLACK_TRACE_HIGHLIGHT

# One step darker for each colour: every shadow uses this, so shadows stay in palette.
SHADE = {
    BM: BM_D, BM_D: VOID_DEEP, TR: BM, TR_HI: TR,
    MASK: MASK_DEEP, MASK_DEEP: VOID_DEEP, TRACE: MASK, TRACE_HIGHLIGHT: TRACE,
    GOLD_HIGHLIGHT: ENIG_GOLD, ENIG_GOLD: COPPER, COPPER: COPPER_SHADOW, COPPER_SHADOW: IC_BLACK,
    SILKSCREEN_WHITE: SILKSCREEN_SHADE, SILKSCREEN_SHADE: IC_GREY, IC_GREY: IC_DARK, IC_DARK: IC_BLACK,
    IC_BLACK: VOID_DEEP, FLUX: COPPER_SHADOW, VOID_MID: VOID, VOID: VOID_DEEP, VOID_DEEP: VOID_DEEP,
    FR4_EDGE: FR4_SHADE, FR4_SHADE: COPPER_SHADOW, SIGNAL_TEAL: SIGNAL_TEAL_DEEP, SIGNAL_TEAL_DEEP: BM,
    GLOW_TEAL: SIGNAL_TEAL, GRAFFITI_PURPLE: DUSK_PURPLE, SMOKE_VIOLET: DUSK_PURPLE, DUSK_PURPLE: IC_DARK,
    LOGO_RED: BURN_RED, BURN_RED: IC_BLACK, OXIDE_RED: BURN_RED, WIRE_YELLOW: ENIG_GOLD,
    WIRE_BLUE: WIRE_BLUE_DEEP, WIRE_BLUE_DEEP: VOID, SIGNAL_PINK: GRAFFITI_PURPLE, SKIN: SKIN_SHADE,
    SKIN_SHADE: COPPER_SHADOW,
}
_SHADE_PACKED = {(c[0] << 16) | (c[1] << 8) | c[2]: s for c, s in SHADE.items()}


def shade_arr(arr, m, steps=1):
    for _ in range(steps):
        sub = arr[m].astype(np.int32)
        packed = (sub[:, 0] << 16) | (sub[:, 1] << 8) | sub[:, 2]
        out = np.empty_like(sub)
        out[:] = VOID_DEEP
        for k, v in _SHADE_PACKED.items():
            out[packed == k] = v
        arr[m] = out.astype(np.uint8)


# ================================================================== PASS 1: the plan
FX, FY, FS, FT = 48, 72, 560, 24       # flight controller: x, y, size, board thickness
EX, EY, ES, ET = 832, 40, 640, 26      # 4-in-1 ESC
W, H = EX + ES + 48, 768
YCAB = 372                              # centre line of the cable bridge
HS = 2.2                                # height exaggeration: parts read as buildings
FLOOR = -150                            # the carbon frame, far below the boards
RADIUS = 26

a = np.zeros((H, W, 3), np.uint8)
a[:] = VOID
OBJS = []    # 3D objects for pass 2
HOLES = []   # through-holes: you can see the frame through them


def mask(fn):
    m = Image.new("L", (W, H), 0)
    fn(ImageDraw.Draw(m))
    return np.array(m) > 0


def fill(m, c):
    a[m] = c


def shade(m, steps=1):
    shade_arr(a, m, steps)


def shift(m, dx, dy):
    out = np.zeros_like(m)
    ys, xs = slice(max(dy, 0), H + min(dy, 0)), slice(max(dx, 0), W + min(dx, 0))
    ys0, xs0 = slice(max(-dy, 0), H + min(-dy, 0)), slice(max(-dx, 0), W + min(-dx, 0))
    out[ys, xs] = m[ys0, xs0]
    return out


def rect(x, y, w, h, c):
    x0, y0, x1, y1 = max(int(x), 0), max(int(y), 0), min(int(x + w), W), min(int(y + h), H)
    if x1 > x0 and y1 > y0:
        a[y0:y1, x0:x1] = c


def disc_m(cx, cy, r, ry=None):
    ry = r if ry is None else ry
    return mask(lambda d: d.ellipse([cx - r, cy - ry, cx + r, cy + ry], fill=255))


def poly_m(pts):
    return mask(lambda d: d.polygon([tuple(p) for p in pts], fill=255))


def line_m(pts, w):
    def f(d):
        d.line([tuple(p) for p in pts], fill=255, width=w, joint="curve")
        r = w / 2 - 0.5
        for x, y in (pts[0], pts[-1]):
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    return mask(f)


def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        a[y, x] = c


def text(s, x, y, c, scale=2, wear=0.0):
    for dx, dy in text_pixels(s, scale):
        if wear and rng.random() < wear:
            continue
        put(x + dx, y + dy, c)


def blob_pts(cx, cy, r, n=11, jitter=0.45, ry=None):
    ry = r if ry is None else ry
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        k = 1 - jitter / 2 + rng.random() * jitter
        pts.append((cx + math.cos(t) * r * k, cy + math.sin(t) * ry * k))
    return pts


def blob(cx, cy, r, c=None, ry=None, steps=1):
    m = poly_m(blob_pts(cx, cy, r, ry=ry))
    if c is None:
        shade(m, steps)
    else:
        fill(m, c)
    return m


def chamfer(pts, c=10):
    """Orthogonal polyline -> PCB-style 45-degree corners."""
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        l0, l1 = math.hypot(x1 - x0, y1 - y0), math.hypot(x2 - x1, y2 - y1)
        k = min(c, l0 / 2, l1 / 2)
        if k <= 0:
            out.append((x1, y1))
            continue
        out.append((x1 - (x1 - x0) / l0 * k, y1 - (y1 - y0) / l0 * k))
        out.append((x1 + (x2 - x1) / l1 * k, y1 + (y2 - y1) / l1 * k))
    out.append(pts[-1])
    return out


def path_points(pts, step=1.0):
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        out += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n)]
    out.append(pts[-1])
    return out


def box(x, y, w, d, height, top, side, hi=None, hi_h=2, z0=0.0, flat=False, windows=None, **_):
    """A part: its top face goes into the plan, the block itself is built in pass 2."""
    if not flat:
        rect(x, y, w, d, top)
        if hi:
            rect(x, y, w, hi_h, hi)
    OBJS.append(dict(kind="box", x=x, y=y, w=w, d=d, z0=z0, h=height * HS, top=top, side=side,
                     flat=flat, windows=windows or []))
    return z0 + height * HS


def wire3d(pts, w, c):
    OBJS.append(dict(kind="wire", pts=pts, w=w, c=c))


def smoke(x, y, z=6.0, n=6):
    for i in range(n):
        OBJS.append(dict(kind="puff", x=x + math.sin(i * 1.3) * 6, y=y - i * 2, z=z + 10 + i * 16,
                         r=4 + i * 2.2, c=SMOKE_VIOLET if i % 2 == 0 else DUSK_PURPLE))


# ------------------------------------------------------------------ boards (flat)
for (x, y, s) in [(FX, FY, FS), (EX, EY, ES)]:
    fill(mask(lambda d, x=x, y=y, s=s: d.rounded_rectangle([x, y, x + s - 1, y + s - 1], RADIUS, fill=255)), BM)
FC_AREA = mask(lambda d: d.rounded_rectangle([FX, FY, FX + FS - 1, FY + FS - 1], RADIUS, fill=255))
ESC_AREA = mask(lambda d: d.rounded_rectangle([EX, EY, EX + ES - 1, EY + ES - 1], RADIUS, fill=255))
BOARDS = FC_AREA | ESC_AREA

for _ in range(70):  # flat grime stains on the mask
    m = poly_m(blob_pts(rng.randrange(W), rng.randrange(H), rng.randrange(10, 46), n=9, jitter=0.7))
    shade(m & BOARDS & (a[..., 0] == BM[0]) & (a[..., 1] == BM[1]))


def F(x, y):
    return FX + x, FY + y


def E(x, y):
    return EX + x, EY + y


# ------------------------------------------------------------------ copper: traces and pours
traces = []


def trace(pts, w=8, org=F):
    p = chamfer([org(*q) for q in pts], c=max(8, w))
    traces.append((p, w))
    return p


MCU = (196, 180, 168, 18)
mx, my, ms, mh = MCU
pin_off = [18 + 12 * i for i in range(12)]
CONN_Y = [YCAB - FY - 42 + 12 * i for i in range(8)]

for i in range(6):  # MCU east pins -> ESC connector (motor signals, telemetry, current)
    y0, y1, ax = my + pin_off[6 + i], CONN_Y[2 + i], 430 - 5 * i
    trace([(mx + ms + 20, y0), (ax, y0), (ax, y1), (FS - 40, y1)], 8)
trace([(FS - 40, CONN_Y[0]), (500, CONN_Y[0]), (500, 236), (452, 236)], 14)
trace([(FS - 40, CONN_Y[1]), (520, CONN_Y[1]), (520, 450), (470, 450)], 10)
for i in range(4):
    trace([(mx - 20, my + pin_off[2 + i]), (138 - 10 * i, my + pin_off[2 + i]), (138 - 10 * i, 326)], 6)
trace([(mx + pin_off[0], my - 20), (mx + pin_off[0], 140), (226, 140), (226, 128)], 6)
trace([(mx + pin_off[4], my - 20), (mx + pin_off[4], 140), (270, 140), (270, 128)], 6)
for i in range(4):
    trace([(mx + pin_off[8 + i], my - 20), (mx + pin_off[8 + i], 108 + 12 * i), (392, 108 + 12 * i)], 6)
trace([(452, 126), (476, 126), (476, 176)], 6)
for pin_i, tx_, hy in [(11, 446, 394), (10, 430, 404), (9, 414, 414)]:
    trace([(mx + pin_off[pin_i], my + ms + mh + 20), (mx + pin_off[pin_i], hy), (tx_, hy), (tx_, 416)], 6)
PADS = [("5V", 120), ("GND", 168), ("CAM", 216), ("VTX", 264), ("TX", 312), ("RX", 360)]
trace([(mx + pin_off[7], my + ms + mh + 20), (mx + pin_off[7], 480), (312, 480), (312, 508)], 6)
trace([(mx + pin_off[8], my + ms + mh + 20), (mx + pin_off[8], 466), (360, 466), (360, 508)], 6)
trace([(128, 404), (128, 440), (216, 440), (216, 508)], 6)
trace([(138, 404), (138, 430), (264, 430), (264, 508)], 6)
trace([(120, 508), (120, 470), (60, 470), (60, 420)], 14)
trace([(168, 508), (168, 486)], 10)

ECONN_Y = [YCAB - EY - 42 + 12 * i for i in range(8)]
DRV = [(250, 214), (390, 214), (250, 400), (390, 400)]
for i, (dx_, dy_) in enumerate(DRV):
    trace([(40, ECONN_Y[2 + i]), (150 + 6 * i, ECONN_Y[2 + i]), (150 + 6 * i, dy_ + 18), (dx_, dy_ + 18)], 8, org=E)
trace([(40, ECONN_Y[6]), (120, ECONN_Y[6]), (120, 520), (440, 520)], 8, org=E)
trace([(40, ECONN_Y[7]), (100, ECONN_Y[7]), (100, 560), (300, 560)], 8, org=E)
trace([(40, ECONN_Y[0]), (70, ECONN_Y[0]), (70, 150), (470, 150), (470, 240)], 16, org=E)

copper = np.zeros((H, W), bool)
for p, w in traces:
    copper |= line_m(p, w)
pour = np.zeros((H, W), bool)
for r in [[F(8, 120), F(150, 120), F(150, 300), F(8, 300)], [F(380, 300), F(546, 300), F(546, 470), F(380, 470)],
          [F(90, 8), F(470, 8), F(470, 70), F(90, 70)], [E(60, 60), E(580, 60), E(580, 580), E(60, 580)]]:
    pour |= poly_m(r)
keep = np.array(Image.fromarray((copper * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(13))) > 0
pour &= ~keep & BOARDS
fill(pour, TR)
fill(pour & ~shift(pour, 0, -3), BM_D)
fill(copper, TR_HI)
fill(copper & ~shift(copper, 0, -3), TR)
for y in range(0, H, 28):  # tented stitching vias
    for x in range((y // 28 % 2) * 14, W, 28):
        if pour[y, x] and pour[max(y - 6, 0), x] and pour[min(y + 6, H - 1), x] and \
                pour[y, max(x - 6, 0)] and pour[y, min(x + 6, W - 1)]:
            fill(disc_m(x, y, 4), TR_HI)
            fill(disc_m(x + 1, y + 1, 2), BM_D)


def via(x, y, r=7):
    fill(disc_m(x, y, r), ENIG_GOLD)
    fill(disc_m(x + 1, y + 1, r - 1) & ~disc_m(x - 1, y - 1, r - 1), COPPER)
    fill(disc_m(x, y, r - 3), VOID_DEEP)


for v in [F(452, 236), F(470, 450), F(60, 420), F(168, 486), E(470, 240), E(440, 520), E(300, 560)]:
    via(*v)
for p, w in traces[:6]:  # data packets on the bus
    pts = path_points(p)
    for start in range(rng.randrange(10, 40), len(pts) - 12, 70):
        for (x, y) in pts[start:start + 10]:
            put(int(x), int(y), SIGNAL_PINK)
            put(int(x), int(y) - 1, SIGNAL_PINK)


# ------------------------------------------------------------------ parts kit
def legs(xs, y, dy, n, c=SILKSCREEN_SHADE, tip=ENIG_GOLD, wid=5):
    for x in xs:
        rect(x - wid // 2, y if dy > 0 else y - n, wid, n, c)
        rect(x - wid // 2, y + n - 4 if dy > 0 else y - n, wid, 4, tip)


def legs_h(x, ys, dx, n, c=SILKSCREEN_SHADE, tip=ENIG_GOLD, wid=5):
    for y in ys:
        rect(x if dx > 0 else x - n, y - wid // 2, n, wid, c)
        rect(x + n - 4 if dx > 0 else x - n, y - wid // 2, 4, wid, tip)


def chip0603(x, y, vertical=False, body=COPPER_SHADOW):
    w, d = (14, 28) if vertical else (28, 14)
    box(x, y, w, d, 5, body, SHADE[body])
    if vertical:
        rect(x, y, 14, 7, SILKSCREEN_SHADE)
        rect(x, y + 21, 14, 7, SILKSCREEN_SHADE)
    else:
        rect(x, y, 7, 14, SILKSCREEN_SHADE)
        rect(x + 21, y, 7, 14, SILKSCREEN_SHADE)
    rect(x, y, w, 2, SILKSCREEN_WHITE)


def solder_blob(x, y, r=7, flux=True):
    if flux:
        blob(x + 2, y + 3, r * 2.0, COPPER_SHADOW)
        blob(x + 1, y + 1, r * 1.55, FLUX)
    shade(disc_m(x + 2, y + 3, r))
    fill(disc_m(x, y, r), SILKSCREEN_SHADE)
    fill(disc_m(x - r * 0.25, y - r * 0.3, r * 0.6), SILKSCREEN_WHITE)


def hole(cx, cy, r_hole=15, r_ring=28, r_grom=42):
    fill(disc_m(cx, cy, r_grom), IC_GREY)                           # rubber grommet
    fill(disc_m(cx, cy, r_grom) & ~disc_m(cx + 4, cy + 4, r_grom), SILKSCREEN_SHADE)
    fill(disc_m(cx, cy + 4, r_ring), IC_DARK)
    fill(disc_m(cx, cy, r_ring), ENIG_GOLD)
    fill(disc_m(cx, cy, r_ring) & ~disc_m(cx - 3, cy - 3, r_ring), COPPER)
    for _ in range(3):  # screw scratches
        t0 = rng.uniform(0, 6.28)
        for j in range(16):
            t = t0 + j * 0.05
            put(int(cx + 21 * math.cos(t)), int(cy + 21 * math.sin(t)), COPPER_SHADOW)
    HOLES.append((cx, cy, r_hole))


def scorch(x, y, r):
    blob(x, y, r * 1.4, COPPER_SHADOW)
    blob(x, y, r, None, steps=2)
    blob(x + 2, y + 1, r * 0.5, IC_BLACK)


def silk_box(x, y, w, h, c=SILKSCREEN_WHITE):
    rect(x, y, w, 2, c)
    rect(x, y + h - 2, w, 2, c)
    rect(x, y, 2, h, c)
    rect(x + w - 2, y, 2, h, c)


def dnp(x, y, label):
    """Unpopulated footprint: an empty lot."""
    silk_box(x, y, 40, 22)
    for xx in (x + 5, x + 26):
        rect(xx, y + 5, 9, 12, ENIG_GOLD)
        rect(xx, y + 5, 9, 2, GOLD_HIGHLIGHT)
    text(label, x, y + 26, SILKSCREEN_WHITE, wear=0.2)


def test_point(x, y, label):
    fill(disc_m(x, y, 6), ENIG_GOLD)
    fill(disc_m(x - 1, y - 1, 3), GOLD_HIGHLIGHT)
    text(label, x + 10, y - 5, SILKSCREEN_WHITE, wear=0.2)


def led(x, y, glow, body):
    blob(x + 9, y + 5, 30, SHADE[SHADE[glow]], ry=22)
    blob(x + 9, y + 5, 17, SHADE[glow], ry=13)
    box(x, y, 18, 10, 4, body, SHADE[body])
    rect(x, y, 5, 10, SILKSCREEN_SHADE)
    rect(x + 13, y, 5, 10, SILKSCREEN_SHADE)
    rect(x + 7, y + 3, 4, 3, SILKSCREEN_WHITE)


# ------------------------------------------------------------------ FC parts
for (hx, hy) in [(44, 44), (516, 44), (44, 516), (516, 516)]:
    hole(*F(hx, hy))

X0, Y0 = F(mx, my)
legs([X0 + o for o in pin_off], Y0 - 20, -1, 20)
legs([X0 + o for o in pin_off], Y0 + ms, 1, 20)
legs_h(X0 - 20, [Y0 + o for o in pin_off], -1, 20)
legs_h(X0 + ms, [Y0 + o for o in pin_off], 1, 20)
windows = [(8 + i * 12, 6, GOLD_HIGHLIGHT if rng.random() < 0.5 else IC_GREY) for i in range(13)]
roof = box(X0, Y0, ms, ms, mh, IC_DARK, IC_BLACK, hi=IC_GREY, hi_h=3, windows=windows)
fill(disc_m(X0 + 18, Y0 + 18, 7), IC_BLACK)
text("STM32", X0 + 40, Y0 + 52, IC_GREY, 3)
text("F405", X0 + 46, Y0 + 72, IC_GREY, 3)
box(X0 + 104, Y0 + 104, 40, 28, 10, IC_GREY, IC_DARK, hi=SILKSCREEN_SHADE, z0=roof)  # rooftop unit
for i in range(4):
    rect(X0 + 108 + i * 9, Y0 + 110, 5, 16, IC_DARK)
box(X0 + 20, Y0 + 120, 16, 16, 6, IC_GREY, IC_DARK, z0=roof)                      # vent
blob(X0 + 60, Y0 + 140, 20, None, ry=8)
text("L3D", X0 + 22, Y0 + 92, SIGNAL_PINK, 4)

CX_, CY_ = F(212, 96)  # crystal
box(CX_, CY_, 64, 26, 10, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)
rect(CX_ + 6, CY_ + 8, 52, 4, SILKSCREEN_WHITE)
text("8.000", CX_ + 13, CY_ + 15, IC_GREY, 2)

GX, GY = F(392, 96)  # gyro
for i in range(4):
    rect(GX - 6, GY + 10 + 12 * i, 6, 5, ENIG_GOLD)
    rect(GX + 10 + 12 * i, GY - 6, 5, 6, ENIG_GOLD)
box(GX, GY, 60, 60, 8, IC_DARK, IC_BLACK, hi=IC_GREY)
fill(disc_m(GX + 9, GY + 10, 3), IC_GREY)
text("6000", GX + 14, GY + 26, IC_GREY, 2)
text("U2", GX + 2, GY - 22, SILKSCREEN_WHITE, wear=0.2)

BX, BY = F(456, 176)  # baro
box(BX, BY, 40, 40, 12, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)
fill(disc_m(BX + 28, BY + 12, 3), IC_BLACK)

IX, IY = F(396, 206)  # inductor + buck regulator
box(IX, IY, 56, 52, 16, IC_GREY, IC_DARK, hi=SILKSCREEN_SHADE)
text("4R7", IX + 14, IY + 20, IC_DARK, 2)
box(*F(404, 270), 34, 22, 6, IC_DARK, IC_BLACK, hi=IC_GREY)

OX, OY = F(40, 340)  # OSD: the TV station
legs([OX + 8 + 10 * k for k in range(10)], OY - 14, -1, 14, wid=4)
legs([OX + 8 + 10 * k for k in range(10)], OY + 44, 1, 14, wid=4)
box(OX, OY, 116, 44, 6, IC_DARK, IC_BLACK, hi=IC_GREY)
text("AT7456E", OX + 12, OY + 16, IC_GREY, 2)
text("OSD", OX, OY - 22, SILKSCREEN_WHITE)

LX, LY = F(404, 430)  # flash
legs([LX + 14 + 16 * k for k in range(4)], LY - 14, -1, 14)
legs([LX + 14 + 16 * k for k in range(4)], LY + 40, 1, 12)
box(LX, LY, 72, 40, 6, IC_DARK, IC_BLACK, hi=IC_GREY)
text("25Q128", LX + 6, LY + 14, IC_GREY, 2)

SX, SY = F(8, 140)  # micro SD slot: the warehouse, card sticking out over the edge
box(SX - 40, SY + 30, 60, 96, 3, IC_BLACK, VOID_DEEP, z0=4)
rect(SX - 34, SY + 40, 30, 70, WIRE_BLUE)
rect(SX - 34, SY + 40, 30, 4, GLOW_TEAL)
text("32", SX - 30, SY + 60, SILKSCREEN_WHITE, 2)
box(SX, SY, 130, 150, 12, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE, hi_h=3)
for k in range(4):
    rect(SX + 14, SY + 22 + k * 30, 102, 3, IC_GREY)
rect(SX + 120, SY + 10, 6, 130, SILKSCREEN_WHITE)
text("MICRO SD", SX + 20, SY + 160, SILKSCREEN_WHITE, wear=0.15)

UX, UY = F(-6, 424)  # USB-C, boot button
box(UX, UY, 44, 72, 6, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)
rect(UX + 4, UY + 14, 10, 44, IC_BLACK)
box(*F(76, 450), 34, 30, 8, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)
fill(disc_m(*F(93, 464), 8), IC_BLACK)
text("BOOT", *F(72, 494), SILKSCREEN_WHITE, wear=0.15)

for i in range(5):  # decoupling caps: row houses
    chip0603(*F(150, 190 + i * 30), body=COPPER_SHADOW if i % 2 else IC_DARK)
for i in range(4):
    chip0603(*F(220 + i * 34, 136), vertical=True)
for i in range(4):
    chip0603(*F(214 + i * 34, 418), vertical=True, body=IC_DARK if i % 2 else COPPER_SHADOW)
for (x, y, v) in [(312, 96, True), (346, 96, True), (470, 300, False), (500, 340, True),
                  (60, 300, False), (100, 300, False), (452, 400, True), (180, 370, False)]:
    chip0603(*F(x, y), vertical=v)

led(*F(146, 104), GLOW_TEAL, SIGNAL_TEAL)
led(*F(146, 124), SIGNAL_PINK, DUSK_PURPLE)
text("STAT", *F(110, 108), SILKSCREEN_WHITE, wear=0.2)
dnp(*F(300, 20), "C41")
dnp(*F(160, 26), "R9")
test_point(*F(392, 180), "TP1")
test_point(*F(30, 330), "TP3")

for name, x in PADS:  # edge pads
    px_, py_ = F(x, 524)
    rect(px_ - 16, py_ - 14, 32, 26, ENIG_GOLD)
    rect(px_ - 16, py_ - 14, 32, 3, GOLD_HIGHLIGHT)
    text(name, px_ - text_width(name, 2) // 2, py_ - 32, SILKSCREEN_WHITE, wear=0.12)
for k, (name, x, c) in enumerate([("5V", 120, LOGO_RED), ("GND", 168, IC_DARK), ("CAM", 216, WIRE_YELLOW)]):
    px_, py_ = F(x, 524)
    solder_blob(px_, py_, 9)
    edge = FY + FS
    wire3d([(px_, py_, 6), (px_, edge - 4, 6), (px_ + 6 + k * 4, edge + 30, -20), (px_ + 20 + k * 10, edge + 90, -90),
            (px_ + 40 + k * 16, edge + 170, FLOOR + 5), (px_ + 60 + k * 20, edge + 400, FLOOR + 5)], 9, c)
solder_blob(*F(264, 524), 8)

scorch(*F(250, 44), 20)  # burnt part, magic smoke
box(*F(240, 36), 22, 16, 5, IC_DARK, IC_BLACK)
rect(*F(246, 40), 10, 2, BURN_RED)
smoke(*F(251, 44), z=12)

# bodge wire: luci3D's signature, arcing over the board
bp0, bp2 = F(58, 326), F(176, my + pin_off[9])
pts = []
for i in range(31):
    t = i / 30
    pts.append((bp0[0] + (bp2[0] - bp0[0]) * t + 30 * math.sin(math.pi * t),
                bp0[1] + (bp2[1] - bp0[1]) * t - 80 * math.sin(math.pi * t), 4 + 46 * math.sin(math.pi * t)))
wire3d(pts, 4, COPPER)
solder_blob(*bp0, 5)
solder_blob(*bp2, 5)

text("F4 STACK REV.1 2016", *F(96, 74), SILKSCREEN_WHITE, wear=0.25)
LOGO = (ROOT / "brand" / "tools" / "make_logo.py").read_text().split('GRID = """')[1].split('"""')[0]
lx0, ly0 = F(476, 400)
for yy, row in enumerate(LOGO.strip("\n").splitlines()):
    for xx, ch in enumerate(row):
        if ch in "#r" and rng.random() > 0.08:
            rect(lx0 + xx * 2, ly0 + yy * 2, 2, 2, SILKSCREEN_WHITE if ch == "#" else LOGO_RED)
text("LUCI3D", lx0 - 4, ly0 + 70, SILKSCREEN_WHITE, wear=0.2)

# ------------------------------------------------------------------ ESC parts
for (hx, hy) in [(48, 48), (592, 48), (48, 592), (592, 592)]:
    hole(*E(hx, hy))


def mosfet(x, y, burnt=False):
    rect(x, y - 10, 44, 10, ENIG_GOLD)
    rect(x, y - 10, 44, 2, GOLD_HIGHLIGHT)
    legs([x + 6 + 11 * k for k in range(4)], y + 36, 1, 10)
    box(x, y, 44, 36, 6, IC_GREY if burnt else IC_DARK, IC_BLACK, hi=IC_GREY)
    text("N03", x + 12, y + 14, IC_BLACK if not burnt else IC_DARK, 2)


for qi, (qx, qy) in enumerate([(120, 82), (358, 82), (120, 448), (358, 448)]):
    for r_ in range(2):
        for c_ in range(3):
            mosfet(*E(qx + c_ * 56, qy + r_ * (66 if qi < 2 else -66) + 10), (qi, r_, c_) == (3, 0, 1))
bx, by = E(358 + 56 + 22, 448 + 10 + 18)  # the blown MOSFET
scorch(bx, by, 30)
for (dx, dy) in [(-10, -4), (-4, 0), (2, -2), (8, 3)]:
    rect(bx + dx, by + dy, 6, 2, LOGO_RED)
smoke(bx, by, z=16, n=8)

for (dx_, dy_) in DRV:  # gate drivers
    x, y = E(dx_, dy_)
    for k in range(4):
        rect(x - 5, y + 6 + 8 * k, 5, 4, ENIG_GOLD)
        rect(x + 36, y + 6 + 8 * k, 5, 4, ENIG_GOLD)
    box(x, y, 36, 36, 6, IC_DARK, IC_BLACK, hi=IC_GREY)
    fill(disc_m(x + 6, y + 7, 2), IC_GREY)

# the torn label, one corner peeling up
lab = [E(250, 270), E(330, 256), E(372, 262), E(404, 300), E(398, 352), E(352, 388), E(292, 380),
       E(262, 350), E(276, 328), E(244, 312)]
shade(shift(poly_m(lab), 3, 4))
fill(poly_m(lab), IC_BLACK)
hexpts = [E(326 + 34 * math.cos(math.radians(60 * k + 30)), 322 + 34 * math.sin(math.radians(60 * k + 30)))
          for k in range(6)]
inner = [(x + (x - E(326, 0)[0]) * -0.12, y + (y - E(0, 322)[1]) * -0.12) for (x, y) in hexpts]
fill(poly_m(hexpts) & ~poly_m(inner) & poly_m(lab), IC_GREY)
text("4IN1", *E(310, 314), IC_GREY, 2)
OBJS.append(dict(kind="tri", pts=[(*E(372, 262), 1), (*E(404, 300), 1), (*E(424, 266), 30)],
                 c=SILKSCREEN_SHADE, back=IC_BLACK))

box(*E(410, 500), 64, 26, 8, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)  # shunt
text("R001", *E(424, 510), IC_GREY, 2)
for i in range(6):
    chip0603(*E(140 + i * 36, 300), vertical=True, body=COPPER_SHADOW if i % 2 else IC_DARK)
for i in range(3):
    chip0603(*E(250 + i * 40, 158))
chip0603(*E(160, 560))

# the water tower: big electrolytic lying across the battery pads
CAPX, CAPY = E(500, 236)
blob(CAPX + 30, CAPY + 90, 40, None, ry=96)
OBJS.append(dict(kind="hcyl", cx=CAPX + 30, y0=CAPY, y1=CAPY + 172, r=30))
for (yy, py_) in [(CAPY + 4, 241), (CAPY + 168, 431)]:
    wire3d([(CAPX + 44, yy, 14), (CAPX + 70, yy, 10), (E(612, py_)[0], E(0, py_)[1], 4)], 4, SILKSCREEN_SHADE)

for (py_, c, lab_) in [(206, LOGO_RED, "+"), (396, IC_DARK, "-")]:  # battery pads + leads
    px_, pyy = E(590, py_)
    rect(px_, pyy, 50, 70, ENIG_GOLD)
    rect(px_, pyy, 50, 4, GOLD_HIGHLIGHT)
    solder_blob(px_ + 18, pyy + 35, 16)
    text(lab_, px_ - 22, pyy + 26, SILKSCREEN_WHITE, 4)
    yy = pyy + 35
    lead = []
    for k in range(13):
        t = k / 12
        x_ = px_ + 18 + t * 300
        z_ = 10 if x_ < EX + ES + 6 else max(FLOOR + 8, 10 - ((x_ - EX - ES - 6) / 90) ** 2 * 160)
        lead.append((x_, yy + t * 40, z_))
    wire3d(lead, 24, c)

for gi, (gx0, top, num) in enumerate([(130, True, "4"), (380, True, "2"), (130, False, "3"), (380, False, "1")]):
    for k in range(3):  # motor pads, wires leaving the city
        px_, py_ = E(gx0 + k * 56, 6 if top else ES - 46)
        rect(px_, py_, 40, 40, ENIG_GOLD)
        rect(px_, py_, 40, 4, GOLD_HIGHLIGHT)
        cx_, cy_ = px_ + 20, py_ + 20
        solder_blob(cx_, cy_, 11)
        if (gi, k) == (1, 2):
            blob(cx_ + 14, cy_ + 16, 12, SIGNAL_TEAL_DEEP)
            blob(cx_ + 12, cy_ + 14, 6, SIGNAL_TEAL)
        s = -1 if top else 1
        edge = EY if top else EY + ES
        dx = (k - 1) * 10
        wire3d([(cx_, cy_, 6), (cx_, edge - s * 4, 7), (cx_ + dx, edge + s * 40, -30),
                (cx_ + 2 * dx, edge + s * 90, -100), (cx_ + 3 * dx, edge + s * 140, FLOOR + 6),
                (cx_ + 5 * dx, edge + s * 400, FLOOR + 6)], 12, IC_DARK)
    text(num, *E(gx0 - 34, 60 if top else ES - 100), SILKSCREEN_WHITE, 5)

# ------------------------------------------------------------------ the bridge: 8-wire cable
WIRE_COLORS = [IC_DARK, LOGO_RED, SILKSCREEN_WHITE, WIRE_YELLOW, WIRE_BLUE, TRACE_HIGHLIGHT, COPPER, GRAFFITI_PURPLE]


def connector(x):
    z = box(x, YCAB - 50, 34, 100, 12, SILKSCREEN_WHITE, SILKSCREEN_SHADE)
    for i in range(8):
        rect(x + 13, YCAB - 42 + 12 * i - 3, 8, 6, IC_DARK)
    return z


fcx, ecx = FX + FS - 44, EX + 10
connector(fcx)
connector(ecx)
x_start, x_end = fcx + 30, ecx + 4
plug_top = box(x_start, YCAB - 54, 26, 108, 10, SILKSCREEN_WHITE, SILKSCREEN_SHADE, hi=SILKSCREEN_SHADE, z0=2)
box(x_end - 26, YCAB - 54, 26, 108, 10, SILKSCREEN_WHITE, SILKSCREEN_SHADE, hi=SILKSCREEN_SHADE, z0=2)
zc = plug_top / 2 + 2
mid = (x_start + x_end) / 2
for i, c in enumerate(WIRE_COLORS):
    y = YCAB - 42 + 12 * i
    pts = []
    for k in range(17):
        t = k / 16
        pts.append((x_start + 26 + (x_end - 26 - x_start - 26) * t, y, zc - 34 * math.sin(math.pi * t)))
    wire3d(pts, 10, c)
    if i in (3, 4):  # data pulses
        for t0 in (0.25, 0.7):
            seg = [p for p in pts if abs((p[0] - pts[0][0]) / (pts[-1][0] - pts[0][0]) - t0) < 0.05]
            if len(seg) >= 2:
                wire3d([(p[0], p[1] - 1, p[2] + 4) for p in seg], 4, SIGNAL_PINK if i == 3 else GLOW_TEAL)
box(mid - 14, YCAB - 52, 28, 108, 18 / HS, IC_BLACK, VOID_DEEP, z0=zc - 34 - 10, flat=True)  # heat shrink
box(x_start + 44, YCAB - 50, 6, 104, 14 / HS, SILKSCREEN_WHITE, SILKSCREEN_SHADE, z0=zc - 12, flat=True)

# ------------------------------------------------------------------ grime pass (flat)
for _ in range(40):  # solder balls
    x, y = rng.randrange(W), rng.randrange(H)
    if BOARDS[y, x]:
        shade(disc_m(x + 1, y + 2, 3))
        fill(disc_m(x, y, 3), SILKSCREEN_SHADE)
        put(x - 1, y - 1, SILKSCREEN_WHITE)
for (x, y) in [F(380, 40), E(200, 250), E(470, 560), F(30, 260)]:  # dust bunnies
    for _ in range(5):
        blob(x + rng.randrange(-10, 10), y + rng.randrange(-6, 6), rng.randrange(5, 10), IC_GREY)
    blob(x, y, 6, SILKSCREEN_SHADE)
hair = []
hx, hy = E(150, 380)
for t in range(220):
    hx += math.cos(t * 0.03) * 1.2
    hy += math.sin(t * 0.05 + 1) * 0.8
    hair.append((hx, hy))
hm = line_m(hair, 2)
shade(shift(hm, 2, 3) & ~hm)
fill(hm, IC_GREY)
for _ in range(7):  # scratches through the mask: bare copper on traces
    x, y = rng.randrange(W), rng.randrange(H)
    ang, ln = rng.uniform(-0.5, 0.5), rng.randrange(30, 90)
    for t in range(ln):
        xx, yy = int(x + t * math.cos(ang)), int(y + t * math.sin(ang))
        if 0 <= xx < W and 0 <= yy < H and BOARDS[yy, xx]:
            c = tuple(a[yy, xx])
            if c in (TR_HI, TR):
                a[yy, xx] = COPPER
            elif c in (BM, BM_D):
                a[yy, xx] = TR_HI
blob(EX + 60, YCAB + 70, 22, None)
blob(FX + FS - 80, YCAB + 80, 16, None)

plan = a.copy()
alpha = BOARDS.copy()
for (cx, cy, r) in HOLES:
    alpha &= ~disc_m(cx, cy, r)

# ================================================================== PASS 2: the view
OW, OH = 1600, 900
TH = math.radians(52)                      # camera pitch below the horizon
DIST, FOC = 1500.0, 1500.0
TGT = np.array([744.0, 430.0, 0.0])
CAM = TGT + DIST * np.array([0.0, math.cos(TH), math.sin(TH)])
RV = np.array([1.0, 0.0, 0.0])
UV = np.array([0.0, -math.sin(TH), math.cos(TH)])
FV = np.array([0.0, -math.cos(TH), -math.sin(TH)])
SCX, SCY = OW / 2, OH * 0.5
LIGHT = (0.55, 0.8)                        # shadow offset per unit of height (falls south-east)


def proj(x, y, z):
    d = np.array([x, y, z], float) - CAM
    zc_ = d @ FV
    return (SCX + FOC * (d @ RV) / zc_, SCY - FOC * (d @ UV) / zc_)


def depth(x, y, z):
    return (np.array([x, y, z], float) - CAM) @ FV


scr = Image.new("RGB", (OW, OH), VOID_DEEP)
dr = ImageDraw.Draw(scr)


def poly(pts, c):
    dr.polygon([(round(x), round(y)) for x, y in pts], fill=c)


def screen_mask(polys=(), lines=()):
    m = Image.new("L", (OW, OH), 0)
    d = ImageDraw.Draw(m)
    for pts in polys:
        d.polygon([(round(x), round(y)) for x, y in pts], fill=255)
    for pts, w in lines:
        d.line([(round(x), round(y)) for x, y in pts], fill=255, width=max(1, round(w)), joint="curve")
    return np.array(m) > 0


def shade_screen(m, steps=1):
    arr = np.array(scr)
    shade_arr(arr, m, steps)
    scr.paste(Image.fromarray(arr))


def homography(src, dst):
    A, b = [], []
    for (X, Y), (u, v) in zip(src, dst):
        A.append([X, Y, 1, 0, 0, 0, -u * X, -u * Y])
        b.append(u)
        A.append([0, 0, 0, X, Y, 1, -v * X, -v * Y])
        b.append(v)
    h = np.linalg.solve(np.array(A, float), np.array(b, float))
    return np.append(h, 1.0).reshape(3, 3)


def warp(img, scale, offset, region, z, bbox=None):
    """Project the part of a plan image covering world `region` at height z onto the screen."""
    x0, y0, x1, y1 = region
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    sp = [proj(x, y, z) for x, y in corners]
    tp = [((x + offset[0]) * scale, (y + offset[1]) * scale) for x, y in corners]
    hm = homography(sp, tp)
    if bbox is None:
        bbox = (0, 0, OW, OH)
    bx0, by0, bx1, by1 = bbox
    hm = hm @ np.array([[1, 0, bx0], [0, 1, by0], [0, 0, 1]], float)
    hm /= hm[2, 2]
    return img.transform((bx1 - bx0, by1 - by0), Image.PERSPECTIVE, tuple(hm.flatten()[:8]), Image.NEAREST), sp


# --- the floor: carbon weave, far below
FL_OFF, FL_W, FL_H = (900, 1100), 3400, 2700
flo = np.zeros((FL_H, FL_W, 3), np.uint8)
yy_, xx_ = np.mgrid[0:FL_H, 0:FL_W]
horiz = ((xx_ // 24) + (yy_ // 24)) % 2 == 0
stripe = np.where(horiz, (yy_ // 4) % 2, (xx_ // 4) % 2) == 0
flo[:] = VOID
flo[stripe] = VOID_MID
floor_img = Image.fromarray(flo)
fimg, _ = warp(floor_img, 1, FL_OFF, (-FL_OFF[0], -FL_OFF[1], FL_W - FL_OFF[0], FL_H - FL_OFF[1]), FLOOR)
scr.paste(fimg)
# depth fog: the far frame falls away in flat bands
fog = np.zeros((OH, OW), bool)
fog[: int(OH * 0.24)] = True
shade_screen(fog)
fog[int(OH * 0.11):] = False
shade_screen(fog)


def board_outline(x, y, s, r=RADIUS, n=6):
    pts = []
    for (cx, cy, a0) in [(x + s - r, y + r, -90), (x + s - r, y + s - r, 0), (x + r, y + s - r, 90), (x + r, y + r, 180)]:
        for k in range(n + 1):
            t = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return pts


OUTLINES = [(board_outline(FX, FY, FS), FT), (board_outline(EX, EY, ES), ET)]

# --- shadows on the floor: boards, wires, the bridge, the SD card
fl_polys, fl_lines = [], []
for outline, t in OUTLINES:
    fl_polys.append([proj(x + LIGHT[0] * -FLOOR, y + LIGHT[1] * -FLOOR, FLOOR) for x, y in outline])
for o in OBJS:
    if o["kind"] == "wire":
        sp = [proj(x + LIGHT[0] * (z - FLOOR), y + LIGHT[1] * (z - FLOOR), FLOOR) for x, y, z in o["pts"]]
        fl_lines.append((sp, o["w"] * FOC / depth(*o["pts"][0][:2], FLOOR)))
shade_screen(screen_mask(fl_polys[:2]), 2)
shade_screen(screen_mask((), fl_lines), 1)


# --- wire drawing (used before and after the boards)
def behind_boards(p0, p1):
    """Wire segments that hang below the board level north or east of a board are drawn first."""
    zmax = max(p0[2], p1[2])
    ymax = max(p0[1], p1[1])
    if zmax > -2:
        return False
    for bx_, by_, bs in [(FX, FY, FS), (EX, EY, ES)]:
        if ymax < by_ + 8 or min(p0[0], p1[0]) > bx_ + bs - 8:
            if (bx_ - 60 < p0[0] < bx_ + bs + 500) and ymax < by_ + bs:
                return True
    return False


def draw_wire_run(pts, w, c):
    """A whole run of wire in one stroke: shaded underside, then the lit body."""
    sp = [proj(*p) for p in pts]
    mid_p = pts[len(pts) // 2]
    wp = w * FOC / depth(*mid_p)
    for (dy, ww, cc) in [(wp * 0.18, wp, SHADE.get(c, c)), (-wp * 0.12, wp * 0.68, c)]:
        q = [(x, y + dy) for x, y in sp]
        dr.line(q, fill=cc, width=max(1, round(ww)), joint="curve")
        r = ww / 2
        for (x, y) in (q[0], q[-1]):
            dr.ellipse([x - r, y - r, x + r, y + r], fill=cc)


runs = []  # (wire points run, w, c), split where a wire passes behind a board
for o in OBJS:
    if o["kind"] != "wire":
        continue
    cur, cur_behind = [o["pts"][0]], None
    for p0, p1 in zip(o["pts"], o["pts"][1:]):
        b = behind_boards(p0, p1)
        if cur_behind is not None and b != cur_behind:
            runs.append((cur, o["w"], o["c"], cur_behind))
            cur = [p0]
        cur.append(p1)
        cur_behind = b
    runs.append((cur, o["w"], o["c"], bool(cur_behind)))
for r in sorted([r for r in runs if r[3]], key=lambda r: -depth(*r[0][0])):
    draw_wire_run(*r[:3])


# --- board slabs: FR4 edges with copper layers, then the projected plan on top
def slab_faces(outline, t):
    cxm = sum(p[0] for p in outline) / len(outline)
    cym = sum(p[1] for p in outline) / len(outline)
    faces = []
    for (x0, y0), (x1, y1) in zip(outline, outline[1:] + outline[:1]):
        mxp, myp = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = (y1 - y0), -(x1 - x0)
        if nx * (mxp - cxm) + ny * (myp - cym) < 0:
            nx, ny = -nx, -ny
        if nx * (CAM[0] - mxp) + ny * (CAM[1] - myp) <= 0:
            continue
        side = abs(nx) > abs(ny) * 1.5
        faces.append((depth(mxp, myp, 0), x0, y0, x1, y1, side))
    for _, x0, y0, x1, y1, side in sorted(faces, reverse=True):
        layers = [(0, -2, BM), (-2, -t + 5, FR4_EDGE), (-t + 5, -t, FR4_SHADE)]
        layers += [(-7, -9, COPPER), (-t + 9, -t + 11, COPPER)]
        for (za, zb, c) in layers:
            cc = SHADE.get(c, c) if side else c
            poly([proj(x0, y0, za), proj(x1, y1, za), proj(x1, y1, zb), proj(x0, y0, zb)], cc)


for outline, t in OUTLINES:
    slab_faces(outline, t)

TS = 2
plan_rgba = Image.fromarray(np.dstack([plan, (alpha * 255).astype(np.uint8)]), "RGBA").resize((W * TS, H * TS),
                                                                                             Image.NEAREST)
plan_rgb = Image.fromarray(plan).resize((W * TS, H * TS), Image.NEAREST)
bimg, _ = warp(plan_rgba, TS, (0, 0), (0, 0, W, H), 0)
scr.paste(bimg, (0, 0), bimg)
BOARD_SCREEN = np.array(bimg)[..., 3] > 0

# hole walls: the plated barrel, seen through the hole
for (cx, cy, r) in HOLES:
    n = 20
    t = FT if cx < EX else ET
    for k in range(n):
        ta, tb = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        tm = (ta + tb) / 2
        px_, py_ = cx + r * math.cos(tm), cy + r * math.sin(tm)
        if -math.cos(tm) * (CAM[0] - px_) - math.sin(tm) * (CAM[1] - py_) > 0:
            q = [(cx + r * math.cos(ta), cy + r * math.sin(ta)), (cx + r * math.cos(tb), cy + r * math.sin(tb))]
            poly([proj(*q[0], 0), proj(*q[1], 0), proj(*q[1], -t), proj(*q[0], -t)],
                 COPPER_SHADOW if math.sin(tm) < 0.3 else IC_BLACK)


# --- parts
def footprint_shadow(o):
    x, y, w, d, z0, h = o["x"], o["y"], o["w"], o["d"], o["z0"], o["h"]
    ox, oy = LIGHT[0] * h, LIGHT[1] * h
    pts = [(x, y), (x + w, y), (x + w + ox, y + oy), (x + w + ox, y + d + oy), (x + ox, y + d + oy), (x, y + d)]
    return [proj(px_, py_, z0) for px_, py_ in pts]


def draw_box(o):
    x, y, w, d, z0, h = o["x"], o["y"], o["w"], o["d"], o["z0"], o["h"]
    z1 = z0 + h
    top, side = o["top"], o["side"]
    if CAM[0] < x:
        poly([proj(x, y, z0), proj(x, y + d, z0), proj(x, y + d, z1), proj(x, y, z1)], SHADE.get(top, side))
    if CAM[0] > x + w:
        poly([proj(x + w, y, z0), proj(x + w, y + d, z0), proj(x + w, y + d, z1), proj(x + w, y, z1)],
             SHADE.get(side, side))
    poly([proj(x, y + d, z0), proj(x + w, y + d, z0), proj(x + w, y + d, z1), proj(x, y + d, z1)], side)
    for (xo, ww, c) in o["windows"]:
        za, zb = z0 + h * 0.3, z0 + h * 0.7
        poly([proj(x + xo, y + d, za), proj(x + xo + ww, y + d, za), proj(x + xo + ww, y + d, zb),
              proj(x + xo, y + d, zb)], c)
    quad = [proj(x, y, z1), proj(x + w, y, z1), proj(x + w, y + d, z1), proj(x, y + d, z1)]
    if o["flat"]:
        poly(quad, top)
        return
    bx0 = max(int(min(p[0] for p in quad)) - 1, 0)
    by0 = max(int(min(p[1] for p in quad)) - 1, 0)
    bx1 = min(int(max(p[0] for p in quad)) + 2, OW)
    by1 = min(int(max(p[1] for p in quad)) + 2, OH)
    if bx1 <= bx0 or by1 <= by0:
        return
    img, _ = warp(plan_rgb, TS, (0, 0), (x, y, x + w, y + d), z1, bbox=(bx0, by0, bx1, by1))
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon([(round(px_ - bx0), round(py_ - by0)) for px_, py_ in quad], fill=255)
    scr.paste(img, (bx0, by0), m)


def draw_hcyl(o):
    cx, y0, y1, r = o["cx"], o["y0"], o["y1"], o["r"]
    n = 14
    ladder = [SMOKE_VIOLET, GRAFFITI_PURPLE, DUSK_PURPLE, IC_DARK]
    facets = []
    for k in range(n):
        ta, tb = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        tm = (ta + tb) / 2
        nx, nz = math.cos(tm), math.sin(tm)
        px_, pz = cx + r * nx, r + r * nz
        if nx * (CAM[0] - px_) + nz * (CAM[2] - pz) <= 0:
            continue
        lit = -0.6 * nx + 0.8 * nz
        c = ladder[0 if lit > 0.75 else 1 if lit > 0.2 else 2 if lit > -0.4 else 3]
        if k == 3:
            c = SILKSCREEN_WHITE                     # polarity stripe
        pa = (cx + r * math.cos(ta), r + r * math.sin(ta))
        pb = (cx + r * math.cos(tb), r + r * math.sin(tb))
        facets.append([proj(pa[0], y0, pa[1]), proj(pb[0], y0, pb[1]), proj(pb[0], y1, pb[1]),
                       proj(pa[0], y1, pa[1]), c])
    for f in facets:
        poly(f[:4], f[4])
    end = [proj(cx + r * math.cos(2 * math.pi * k / 20), y1, r + r * math.sin(2 * math.pi * k / 20))
           for k in range(20)]
    poly(end, SILKSCREEN_SHADE)
    end2 = [proj(cx + r * 0.8 * math.cos(2 * math.pi * k / 20) - 2, y1, r + r * 0.8 * math.sin(2 * math.pi * k / 20)
                 + 2) for k in range(20)]
    poly(end2, SILKSCREEN_WHITE)
    for (ax_, az_, bx_, bz_) in [(-r * 0.6, 0, r * 0.6, 0), (0, -r * 0.6, 0, r * 0.6)]:
        dr.line([proj(cx + ax_, y1, r + az_), proj(cx + bx_, y1, r + bz_)], fill=IC_GREY, width=2)


ground = [o for o in OBJS if o["kind"] == "box" and o["z0"] <= 4]
raised = [o for o in OBJS if o["kind"] == "box" and o["z0"] > 4]
sh = screen_mask([footprint_shadow(o) for o in ground] +
                 [[proj(o["cx"] - o["r"] + LIGHT[0] * 0, o["y0"], 0), proj(o["cx"] + o["r"] + LIGHT[0] * 60, o["y0"] + 30, 0),
                   proj(o["cx"] + o["r"] + LIGHT[0] * 60, o["y1"] + 40, 0), proj(o["cx"] - o["r"], o["y1"], 0)]
                  for o in OBJS if o["kind"] == "hcyl"])
shade_screen(sh & BOARD_SCREEN)

items = []
for o in ground:
    items.append((o["y"] + o["d"], 0, lambda o=o: draw_box(o)))
for o in OBJS:
    if o["kind"] == "hcyl":
        items.append((o["y1"], 0, lambda o=o: draw_hcyl(o)))
    if o["kind"] == "tri":
        items.append((max(p[1] for p in o["pts"]), 0,
                      lambda o=o: poly([proj(*p) for p in o["pts"]], o["c"])))
for r in [r for r in runs if not r[3]]:
    items.append((max(p[1] for p in r[0]), 1, lambda r=r: draw_wire_run(*r[:3])))
for _, _, fn in sorted(items, key=lambda t: (t[0], t[1])):
    fn()

# rooftop level: shadows on the roofs, then the rooftop parts
shade_screen(screen_mask([footprint_shadow(o) for o in raised if not o["flat"] or o["w"] > 10]))
for o in sorted(raised, key=lambda o: o["y"] + o["d"]):
    draw_box(o)

# magic smoke rises
for o in sorted([o for o in OBJS if o["kind"] == "puff"], key=lambda o: -depth(o["x"], o["y"], o["z"])):
    cxs, cys = proj(o["x"], o["y"], o["z"])
    rp = o["r"] * FOC / depth(o["x"], o["y"], o["z"])
    poly(blob_pts(cxs, cys, rp, n=9, jitter=0.35), o["c"])

# ------------------------------------------------------------------ export
out = Path(__file__).resolve().parent / "out"
out.mkdir(exist_ok=True)
scr.save(out / "stack-v2.png")
pl = np.zeros_like(plan)
pl[:] = VOID
pl[alpha] = plan[alpha]
Image.fromarray(pl).save(out / "stack-v2-plan.png")
print("wrote", out)
