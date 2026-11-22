#!/usr/bin/env python3
"""The Stack, mock-up v1: an old flight controller and a 4-in-1 ESC as one city.

Top-down (3/4 view), a human is about 32 px tall. Flat shapes, no outlines,
light from the top left, shadows are the next darker palette colour. Only
colours from brand/palette/luci3d.gpl.

    python3 art/world/make_stack.py
      -> art/world/out/stack-v1-world.png   the whole map, 1 px = 1 game pixel
      -> art/world/out/stack-v1-screen*.png one 480x270 game screen around the bridge

The FC (left) and the ESC (right) float over the quad's carbon frame. The
8-wire cable between them is the bridge.
"""
import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "brand" / "tools"))
sys.path.insert(0, str(ROOT / "art" / "sprites"))
import palette  # noqa: E402
import sprites  # noqa: E402
from font3x5 import text_pixels, text_width  # noqa: E402

P = palette.load()
for _k in list(P):
    globals()[_k.upper().replace(" ", "_").replace("-", "_")] = P[_k]
# names now available: MASK, MASK_DEEP, TRACE, TRACE_HIGHLIGHT, COPPER, ENIG_GOLD, ...

rng = random.Random(7)

# One step darker for each colour: used for every shadow, so shadows stay in palette.
SHADE = {
    MASK: MASK_DEEP, MASK_DEEP: VOID_DEEP, TRACE: MASK, TRACE_HIGHLIGHT: TRACE,
    GOLD_HIGHLIGHT: ENIG_GOLD, ENIG_GOLD: COPPER, COPPER: COPPER_SHADOW, COPPER_SHADOW: IC_BLACK,
    SILKSCREEN_WHITE: SILKSCREEN_SHADE, SILKSCREEN_SHADE: IC_GREY, IC_GREY: IC_DARK, IC_DARK: IC_BLACK,
    IC_BLACK: VOID_DEEP, FLUX: COPPER_SHADOW, VOID_MID: VOID, VOID: VOID_DEEP, VOID_DEEP: VOID_DEEP,
    FR4_EDGE: FR4_SHADE, FR4_SHADE: COPPER_SHADOW, SIGNAL_TEAL: SIGNAL_TEAL_DEEP, SIGNAL_TEAL_DEEP: MASK,
    GLOW_TEAL: SIGNAL_TEAL, GRAFFITI_PURPLE: DUSK_PURPLE, SMOKE_VIOLET: DUSK_PURPLE, DUSK_PURPLE: IC_DARK,
    LOGO_RED: BURN_RED, BURN_RED: IC_BLACK, OXIDE_RED: BURN_RED, WIRE_YELLOW: ENIG_GOLD,
    WIRE_BLUE: WIRE_BLUE_DEEP, WIRE_BLUE_DEEP: VOID, SIGNAL_PINK: GRAFFITI_PURPLE, SKIN: SKIN_SHADE,
    SKIN_SHADE: COPPER_SHADOW,
}
_SHADE_PACKED = {(a[0] << 16) | (a[1] << 8) | a[2]: b for a, b in SHADE.items()}

# ------------------------------------------------------------------ world layout
FX, FY, FS, FT = 48, 72, 560, 16       # flight controller: x, y, size, board thickness
EX, EY, ES, ET = 832, 40, 640, 18      # 4-in-1 ESC
W, H = EX + ES + 48, 768
YCAB = 372                              # centre line of the cable bridge
SCREEN = (408, YCAB - 135, 480, 270)    # the game-screen crop

a = np.zeros((H, W, 3), np.uint8)


# ------------------------------------------------------------------ drawing kit
def mask(fn):
    m = Image.new("L", (W, H), 0)
    fn(ImageDraw.Draw(m))
    return np.array(m) > 0


def fill(m, c):
    a[m] = c


def shade(m, steps=1):
    for _ in range(steps):
        sub = a[m].astype(np.int32)
        packed = (sub[:, 0] << 16) | (sub[:, 1] << 8) | sub[:, 2]
        out = np.empty_like(sub)
        out[:] = MASK_DEEP
        for k, v in _SHADE_PACKED.items():
            out[packed == k] = v
        a[m] = out.astype(np.uint8)


def shift(m, dx, dy):
    out = np.zeros_like(m)
    ys, xs = slice(max(dy, 0), H + min(dy, 0)), slice(max(dx, 0), W + min(dx, 0))
    ys0, xs0 = slice(max(-dy, 0), H + min(-dy, 0)), slice(max(-dx, 0), W + min(-dx, 0))
    out[ys, xs] = m[ys0, xs0]
    return out


def rect_m(x, y, w, h):
    return mask(lambda d: d.rectangle([x, y, x + w - 1, y + h - 1], fill=255))


def rect(x, y, w, h, c):
    x0, y0, x1, y1 = max(int(x), 0), max(int(y), 0), min(int(x + w), W), min(int(y + h), H)
    if x1 > x0 and y1 > y0:
        a[y0:y1, x0:x1] = c


def shade_rect(x, y, w, h, steps=1):
    x0, y0, x1, y1 = max(int(x), 0), max(int(y), 0), min(int(x + w), W), min(int(y + h), H)
    if x1 > x0 and y1 > y0:
        m = np.zeros((H, W), bool)
        m[y0:y1, x0:x1] = True
        shade(m, steps)


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


def box(x, y, w, h, height, top, side, sh=(4, 4), hi=None, hi_h=2):
    """A 3/4-view block: flat shadow, south face, top face, optional lit top edge."""
    if sh:
        shade_rect(x + sh[0], y + sh[1], w, h + height)
    rect(x, y + h, w, height, side)
    rect(x, y, w, h, top)
    if hi:
        rect(x, y, w, hi_h, hi)


# ------------------------------------------------------------------ the floor: carbon frame
for ty in range(0, H, 16):
    for tx in range(0, W, 16):
        horiz = ((tx // 16) + (ty // 16)) % 2 == 0
        for k in range(0, 16, 4):
            if horiz:
                rect(tx, ty + k, 16, 2, VOID_MID)
                rect(tx, ty + k + 2, 16, 2, VOID)
            else:
                rect(tx + k, ty, 2, 16, VOID_MID)
                rect(tx + k + 2, ty, 2, 16, VOID)
# frame grime and screw holes far below
for _ in range(14):
    blob(rng.randrange(W), rng.randrange(H), rng.randrange(20, 70), steps=1)


# ------------------------------------------------------------------ boards
def board(x, y, s, t, radius=26):
    shade(mask(lambda d: d.rounded_rectangle([x + 22, y + 30, x + s + 22, y + s + t + 30], radius, fill=255)), 2)
    for k in range(t, 0, -1):
        c = FR4_SHADE if k > t - 4 else COPPER if k in (5, 6, t - 6) else FR4_EDGE
        fill(mask(lambda d, k=k: d.rounded_rectangle([x, y + k, x + s - 1, y + s - 1 + k], radius, fill=255)), c)
    fill(mask(lambda d: d.rounded_rectangle([x, y, x + s - 1, y + s - 1], radius, fill=255)), MASK)


board(FX, FY, FS, FT)
board(EX, EY, ES, ET)
FC_AREA = mask(lambda d: d.rounded_rectangle([FX, FY, FX + FS - 1, FY + FS - 1], 26, fill=255))
ESC_AREA = mask(lambda d: d.rounded_rectangle([EX, EY, EX + ES - 1, EY + ES - 1], 26, fill=255))
BOARDS = FC_AREA | ESC_AREA

# Mask texture: flat darker stains (grime), no dithering.
for _ in range(70):
    m = poly_m(blob_pts(rng.randrange(W), rng.randrange(H), rng.randrange(10, 46), n=9, jitter=0.7))
    shade(m & BOARDS & (a[..., 0] == MASK[0]) & (a[..., 1] == MASK[1]))


def F(x, y):
    return FX + x, FY + y


def E(x, y):
    return EX + x, EY + y


# ------------------------------------------------------------------ copper: traces and pours
traces = []  # (abs points, width)


def trace(pts, w=8, org=F):
    p = chamfer([org(*q) for q in pts], c=max(8, w))
    traces.append((p, w))
    return p


# --- FC routing (local coords)
MCU = (196, 180, 168, 18)       # x, y, size, height
mx, my, ms, mh = MCU
pin_off = [18 + 12 * i for i in range(12)]
CONN_Y = [YCAB - FY - 42 + 12 * i for i in range(8)]   # FC connector pin rows (local)

bus = []
for i in range(6):  # MCU east pins -> connector pins 2..7 (motor signals, telemetry, current)
    y0 = my + pin_off[6 + i]
    y1 = CONN_Y[2 + i]
    ax = 430 - 5 * i
    bus.append(trace([(mx + ms + 20, y0), (ax, y0), (ax, y1), (FS - 40, y1)], 8))
vbat = trace([(FS - 40, CONN_Y[0]), (500, CONN_Y[0]), (500, 236), (452, 236)], 14)
trace([(FS - 40, CONN_Y[1]), (520, CONN_Y[1]), (520, 450), (470, 450)], 10)  # GND run
for i in range(4):  # MCU west -> OSD top pins
    y0 = my + pin_off[2 + i]
    xo = 138 - 10 * i
    trace([(mx - 20, y0), (xo, y0), (xo, 326)], 6)
trace([(mx + pin_off[0], my - 20), (mx + pin_off[0], 140), (226, 140), (226, 128)], 6)  # crystal
trace([(mx + pin_off[4], my - 20), (mx + pin_off[4], 140), (270, 140), (270, 128)], 6)
for i in range(4):  # MCU north -> gyro west side
    x0 = mx + pin_off[8 + i]
    gy = 108 + 12 * i
    trace([(x0, my - 20), (x0, gy), (392, gy)], 6)
trace([(452, 126), (476, 126), (476, 176)], 6)  # gyro -> baro
for k, (pin_i, tx_, hy) in enumerate([(11, 446, 394), (10, 430, 404), (9, 414, 414)]):
    x0 = mx + pin_off[pin_i]
    trace([(x0, my + ms + mh + 20), (x0, hy), (tx_, hy), (tx_, 416)], 6)  # MCU -> flash
PADS = [("5V", 120), ("GND", 168), ("CAM", 216), ("VTX", 264), ("TX", 312), ("RX", 360)]
trace([(mx + pin_off[7], my + ms + mh + 20), (mx + pin_off[7], 480), (312, 480), (312, 508)], 6)
trace([(mx + pin_off[8], my + ms + mh + 20), (mx + pin_off[8], 466), (360, 466), (360, 508)], 6)
trace([(128, 404), (128, 440), (216, 440), (216, 508)], 6)   # OSD -> CAM
trace([(138, 404), (138, 430), (264, 430), (264, 508)], 6)   # OSD -> VTX
trace([(120, 508), (120, 470), (60, 470), (60, 420)], 14)    # 5V
trace([(168, 508), (168, 486)], 10)

# --- ESC routing
ECONN_Y = [YCAB - EY - 42 + 12 * i for i in range(8)]
DRV = [(250, 214), (390, 214), (250, 400), (390, 400)]  # gate drivers (local, 36x36)
for i, (dx_, dy_) in enumerate(DRV):
    y0 = ECONN_Y[2 + i]
    trace([(40, y0), (150 + 6 * i, y0), (150 + 6 * i, dy_ + 18), (dx_, dy_ + 18)], 8, org=E)
trace([(40, ECONN_Y[6]), (120, ECONN_Y[6]), (120, 520), (440, 520)], 8, org=E)   # current sense
trace([(40, ECONN_Y[7]), (100, ECONN_Y[7]), (100, 560), (300, 560)], 8, org=E)   # telemetry
trace([(40, ECONN_Y[0]), (70, ECONN_Y[0]), (70, 150), (470, 150), (470, 240)], 16, org=E)  # VBAT to cap

copper = np.zeros((H, W), bool)
for p, w in traces:
    copper |= line_m(p, w)

# Pours: big copper areas under the mask, kept clear of traces
pour_regions = [
    [F(8, 120), F(150, 120), F(150, 300), F(8, 300)],
    [F(380, 300), F(546, 300), F(546, 470), F(380, 470)],
    [F(90, 8), F(470, 8), F(470, 70), F(90, 70)],
    [E(60, 60), E(580, 60), E(580, 580), E(60, 580)],
]
pour = np.zeros((H, W), bool)
for r in pour_regions:
    pour |= poly_m(r)
keep = Image.fromarray((copper * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(13))
pour &= ~(np.array(keep) > 0) & BOARDS
fill(pour, TRACE)
fill(pour & ~shift(pour, 0, -3), MASK)  # south edge of each pour reads as a little step
fill(copper, TRACE_HIGHLIGHT)
fill(copper & ~shift(copper, 0, -3), TRACE)  # south curb on each trace

# tented stitching vias on the pours (manhole covers)
for y in range(0, H, 28):
    for x in range((y // 28 % 2) * 14, W, 28):
        if pour[y, x] and pour[max(y - 6, 0), x] and pour[min(y + 6, H - 1), x] and \
                pour[y, max(x - 6, 0)] and pour[y, min(x + 6, W - 1)]:
            fill(disc_m(x, y, 4), TRACE_HIGHLIGHT)
            fill(disc_m(x + 1, y + 1, 2), MASK_DEEP)


def via(x, y, r=7):
    shade(disc_m(x + 2, y + 2, r))
    fill(disc_m(x, y, r), ENIG_GOLD)
    fill(disc_m(x + 1, y + 1, r - 1) & ~disc_m(x - 1, y - 1, r - 1), COPPER)
    fill(disc_m(x, y, r - 3), VOID)


for v in [F(452, 236), F(470, 450), F(60, 420), F(168, 486), E(470, 240), E(440, 520), E(300, 560)]:
    via(*v)

# data packets running on the bus (animated on the website later)
for p, w in traces[:6]:
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
    if vertical:
        box(x, y, 14, 28, 5, body, SHADE[body], sh=(3, 3))
        rect(x, y, 14, 7, SILKSCREEN_SHADE)
        rect(x, y + 21, 14, 7, SILKSCREEN_SHADE)
        rect(x, y, 14, 2, SILKSCREEN_WHITE)
    else:
        box(x, y, 28, 14, 5, body, SHADE[body], sh=(3, 3))
        rect(x, y, 7, 14, SILKSCREEN_SHADE)
        rect(x + 21, y, 7, 14, SILKSCREEN_SHADE)
        rect(x, y, 28, 2, SILKSCREEN_WHITE)
        rect(x + 7, y, 14, 2, SHADE[SHADE[body]] if body != IC_BLACK else IC_DARK)


def solder_blob(x, y, r=7, flux=True):
    if flux:
        blob(x + 2, y + 3, r * 2.0, COPPER_SHADOW)
        blob(x + 1, y + 1, r * 1.55, FLUX)
    shade(disc_m(x + 2, y + 3, r))
    fill(disc_m(x, y, r), SILKSCREEN_SHADE)
    fill(disc_m(x - r * 0.25, y - r * 0.3, r * 0.6), SILKSCREEN_WHITE)


def hole(cx, cy, r_hole=15, r_ring=28, r_grom=42):
    shade(disc_m(cx + 6, cy + 8, r_grom))
    fill(disc_m(cx, cy, r_grom), IC_GREY)                          # rubber grommet
    fill(disc_m(cx, cy, r_grom) & ~disc_m(cx + 4, cy + 4, r_grom), SILKSCREEN_SHADE)
    fill(disc_m(cx, cy + 4, r_ring), IC_DARK)                       # grommet inner wall
    fill(disc_m(cx, cy, r_ring), ENIG_GOLD)
    fill(disc_m(cx, cy, r_ring) & ~disc_m(cx - 3, cy - 3, r_ring), COPPER)
    fill(disc_m(cx, cy, r_hole), VOID_DEEP)                         # through to the frame
    fill(disc_m(cx, cy - 3, r_hole) & ~disc_m(cx, cy + 3, r_hole), COPPER_SHADOW)
    for k in range(3):  # screw scratches
        t0 = rng.uniform(0, 6.28)
        for j in range(16):
            t = t0 + j * 0.05
            put(int(cx + 21 * math.cos(t)), int(cy + 21 * math.sin(t)), COPPER_SHADOW)


def smoke(x, y, n=5):
    for i in range(n):
        r = 3 + i * 1.6
        blob(x + math.sin(i * 1.3) * 6, y - i * 9, r, SMOKE_VIOLET if i % 2 == 0 else DUSK_PURPLE, ry=r * 0.8)


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
    rect(x + 5, y + 5, 9, 12, ENIG_GOLD)
    rect(x + 26, y + 5, 9, 12, ENIG_GOLD)
    rect(x + 5, y + 5, 9, 2, GOLD_HIGHLIGHT)
    rect(x + 26, y + 5, 9, 2, GOLD_HIGHLIGHT)
    text(label, x, y + 26, SILKSCREEN_WHITE, wear=0.2)


def test_point(x, y, label):
    fill(disc_m(x, y, 6), ENIG_GOLD)
    fill(disc_m(x - 1, y - 1, 3), GOLD_HIGHLIGHT)
    text(label, x + 10, y - 5, SILKSCREEN_WHITE, wear=0.2)


def led(x, y, glow, body):
    blob(x + 9, y + 5, 26, SHADE[SHADE[glow]] if SHADE[glow] in SHADE else glow, ry=18)
    blob(x + 9, y + 5, 15, SHADE[glow], ry=11)
    box(x, y, 18, 10, 4, body, SHADE[body], sh=(2, 2))
    rect(x, y, 5, 10, SILKSCREEN_SHADE)
    rect(x + 13, y, 5, 10, SILKSCREEN_SHADE)
    rect(x + 7, y + 3, 4, 3, SILKSCREEN_WHITE)


def wire(pts, w, c, ground_shadow=(8, 18)):
    """Insulated wire. Casts a shadow on whatever is below."""
    m = line_m(pts, w)
    shade(shift(m, *ground_shadow) & ~m, 1)
    fill(m, c)
    fill(m & ~shift(m, 0, -3), SHADE[c])
    return m


# ------------------------------------------------------------------ FC parts
for (hx, hy) in [(44, 44), (516, 44), (44, 516), (516, 516)]:
    hole(*F(hx, hy))

# downtown: the MCU, with a rooftop
X0, Y0 = F(mx, my)
shade_rect(X0 + 8, Y0 + 10, ms, ms + mh)
for side in "nswe":
    if side == "n":
        legs([X0 + o for o in pin_off], Y0 - 20, -1, 20)
    if side == "s":
        legs([X0 + o for o in pin_off], Y0 + ms + mh, 1, 20)
    if side == "w":
        legs_h(X0 - 20, [Y0 + o for o in pin_off], -1, 20)
    if side == "e":
        legs_h(X0 + ms, [Y0 + o for o in pin_off], 1, 20)
box(X0, Y0, ms, ms, mh, IC_DARK, IC_BLACK, sh=None, hi=IC_GREY, hi_h=3)
for i in range(13):  # lit windows on the south face
    wx = X0 + 8 + i * 12
    lit = rng.random() < 0.5
    rect(wx, Y0 + ms + 5, 6, 8, GOLD_HIGHLIGHT if lit else IC_DARK)
fill(disc_m(X0 + 18, Y0 + 18, 7), IC_BLACK)                       # pin-1 dimple
text("STM32", X0 + 40, Y0 + 52, IC_GREY, 3)
text("F405", X0 + 46, Y0 + 72, IC_GREY, 3)
box(X0 + 104, Y0 + 104, 40, 28, 10, IC_GREY, IC_DARK, sh=(5, 5), hi=SILKSCREEN_SHADE)  # rooftop unit
for i in range(4):
    rect(X0 + 108 + i * 9, Y0 + 110, 5, 16, IC_DARK)
box(X0 + 20, Y0 + 120, 16, 16, 6, IC_GREY, IC_DARK, sh=(4, 4))      # vent
rect(X0 + 132, Y0 + 30, 3, 40, SILKSCREEN_SHADE)                    # antenna mast
rect(X0 + 126, Y0 + 30, 15, 3, SILKSCREEN_SHADE)
fill(disc_m(X0 + 133, Y0 + 28, 3), LOGO_RED)
blob(X0 + 60, Y0 + 140, 20, None, ry=8)                             # roof water stain
text("L3D", X0 + 22, Y0 + 96, SIGNAL_PINK, 4)                       # tag on the roof

# crystal: a little tanker
CX_, CY_ = F(212, 96)
box(CX_, CY_, 64, 26, 10, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)
rect(CX_ + 6, CY_ + 8, 52, 4, SILKSCREEN_WHITE)
text("8.000", CX_ + 13, CY_ + 15, IC_GREY, 2)

# gyro
GX, GY = F(392, 96)
for i in range(4):
    rect(GX - 6, GY + 10 + 12 * i, 6, 5, ENIG_GOLD)
    rect(GX + 10 + 12 * i, GY - 6, 5, 6, ENIG_GOLD)
box(GX, GY, 60, 60, 8, IC_DARK, IC_BLACK, hi=IC_GREY)
fill(disc_m(GX + 9, GY + 10, 3), IC_GREY)
text("6000", GX + 14, GY + 26, IC_GREY, 2)
text("U2", GX + 2, GY - 22, SILKSCREEN_WHITE, wear=0.2)

# baro: a metal can with a vent hole
BX, BY = F(456, 176)
box(BX, BY, 40, 40, 12, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)
fill(disc_m(BX + 28, BY + 12, 3), IC_BLACK)

# inductor + buck regulator
IX, IY = F(396, 206)
box(IX, IY, 56, 52, 16, IC_GREY, IC_DARK, hi=SILKSCREEN_SHADE)
text("4R7", IX + 14, IY + 20, IC_DARK, 2)
legs([F(0, 0)[0] + 410, F(0, 0)[0] + 438], F(0, 270)[1] + 12, 1, 8)
box(*F(404, 270), 34, 22, 6, IC_DARK, IC_BLACK, hi=IC_GREY)

# OSD: the TV station
OX, OY = F(40, 340)
legs([OX + 8 + 10 * k for k in range(10)], OY - 14, -1, 14, wid=4)
legs([OX + 8 + 10 * k for k in range(10)], OY + 44 + 6, 1, 14, wid=4)
box(OX, OY, 116, 44, 6, IC_DARK, IC_BLACK, hi=IC_GREY)
text("AT7456E", OX + 12, OY + 16, IC_GREY, 2)
rect(OX + 92, OY - 46, 4, 46, SILKSCREEN_SHADE)                    # broadcast mast
for k in range(3):
    rect(OX + 84 + k * 2, OY - 40 + k * 12, 20 - k * 4, 3, SILKSCREEN_SHADE)
fill(disc_m(OX + 94, OY - 48, 4), LOGO_RED)
text("OSD", OX, OY - 22, SILKSCREEN_WHITE)

# flash
LX, LY = F(404, 430)
legs([LX + 14 + 16 * k for k in range(4)], LY - 14, -1, 14)
legs([LX + 14 + 16 * k for k in range(4)], LY + 40 + 6, 1, 12)
box(LX, LY, 72, 40, 6, IC_DARK, IC_BLACK, hi=IC_GREY)
text("25Q128", LX + 6, LY + 14, IC_GREY, 2)

# micro SD slot: the warehouse, with a card sticking out over the edge
SX, SY = F(8, 140)
box(SX - 40, SY + 30, 60, 96, 6, IC_BLACK, VOID_DEEP, sh=(14, 22))  # card over the void
rect(SX - 34, SY + 40, 30, 70, WIRE_BLUE)
rect(SX - 34, SY + 40, 30, 4, GLOW_TEAL)
text("32", SX - 30, SY + 60, SILKSCREEN_WHITE, 2)
box(SX, SY, 130, 150, 12, SILKSCREEN_SHADE, IC_GREY, sh=(6, 6), hi=SILKSCREEN_WHITE, hi_h=3)
for k in range(4):
    rect(SX + 14, SY + 22 + k * 30, 102, 3, IC_GREY)
rect(SX + 120, SY + 10, 6, 130, SILKSCREEN_WHITE)
text("MICRO SD", SX + 20, SY + 160, SILKSCREEN_WHITE, wear=0.15)

# USB-C on the bottom-left edge, boot button
UX, UY = F(-6, 424)
box(UX, UY, 44, 72, 6, SILKSCREEN_SHADE, IC_GREY, sh=(8, 10), hi=SILKSCREEN_WHITE)
rect(UX + 4, UY + 14, 10, 44, IC_BLACK)
box(*F(76, 450), 34, 30, 8, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)
fill(disc_m(*F(93, 464), 8), IC_BLACK)
text("BOOT", *F(72, 494), SILKSCREEN_WHITE, wear=0.15)

# decoupling caps: row houses around downtown
for i in range(5):
    chip0603(*F(150, 190 + i * 30), body=COPPER_SHADOW if i % 2 else IC_DARK)
for i in range(4):
    chip0603(*F(220 + i * 34, 136), vertical=True)
for i in range(4):
    chip0603(*F(214 + i * 34, 418), vertical=True, body=IC_DARK if i % 2 else COPPER_SHADOW)
for (x, y, v) in [(312, 96, True), (346, 96, True), (470, 300, False), (500, 340, True),
                  (60, 300, False), (100, 300, False), (452, 400, True), (180, 370, False)]:
    chip0603(*F(x, y), vertical=v)

# LEDs with light pools
led(*F(146, 104), GLOW_TEAL, SIGNAL_TEAL)
led(*F(146, 124), SIGNAL_PINK, DUSK_PURPLE)
text("STAT", *F(110, 108), SILKSCREEN_WHITE, wear=0.2)

# empty lots and test points
dnp(*F(300, 20), "C41")
dnp(*F(160, 26), "R9")
test_point(*F(392, 180), "TP1")
test_point(*F(30, 330), "TP3")

# edge pads with wires
for name, x in PADS:
    px_, py_ = F(x, 524)
    rect(px_ - 16, py_ - 14, 32, 26, ENIG_GOLD)
    rect(px_ - 16, py_ - 14, 32, 3, GOLD_HIGHLIGHT)
    text(name, px_ - text_width(name, 2) // 2, py_ - 32, SILKSCREEN_WHITE, wear=0.12)
for name, x, c in [("5V", 120, LOGO_RED), ("GND", 168, IC_DARK), ("CAM", 216, WIRE_YELLOW)]:
    px_, py_ = F(x, 524)
    wire([(px_, py_), (px_, py_ + 40), (px_ + 30, H + 20)], 9, c, ground_shadow=(10, 22))
    solder_blob(px_, py_, 9)
solder_blob(*F(264, 524), 8)

# burnt part: something died here, magic smoke still leaving
scorch(*F(250, 44), 20)
box(*F(240, 36), 22, 16, 5, IC_DARK, IC_BLACK)
rect(*F(246, 40), 10, 2, BURN_RED)
smoke(*F(251, 28))

# bodge wire: luci3D's signature, OSD pin to an MCU pin, over everything
bp0, bp2 = F(58, 326), F(176, my + pin_off[9])
bp1 = (bp0[0] + 20, bp2[1] - 160)
pts = [((1 - t) ** 2 * bp0[0] + 2 * (1 - t) * t * bp1[0] + t * t * bp2[0],
        (1 - t) ** 2 * bp0[1] + 2 * (1 - t) * t * bp1[1] + t * t * bp2[1]) for t in [i / 60 for i in range(61)]]
wire(pts, 4, COPPER, ground_shadow=(5, 9))
solder_blob(*bp0, 5)
solder_blob(*bp2, 5)

# silkscreen
text("F4 STACK REV.1 2016", *F(96, 74), SILKSCREEN_WHITE, wear=0.25)
LOGO = (ROOT / "brand" / "tools" / "make_logo.py").read_text().split('GRID = """')[1].split('"""')[0]
lx0, ly0 = F(476, 400 - 0)
for yy, row in enumerate(LOGO.strip("\n").splitlines()):
    for xx, ch in enumerate(row):
        if ch in "#r" and rng.random() > 0.08:
            rect(lx0 + xx * 2, ly0 + yy * 2 - 0, 2, 2, SILKSCREEN_WHITE if ch == "#" else LOGO_RED)
text("LUCI3D", lx0 - 4, ly0 + 70, SILKSCREEN_WHITE, wear=0.2)

# ------------------------------------------------------------------ ESC parts
for (hx, hy) in [(48, 48), (592, 48), (48, 592), (592, 592)]:
    hole(*E(hx, hy))


def mosfet(x, y, burnt=False):
    rect(x, y - 10, 44, 10, ENIG_GOLD)                # drain tab
    rect(x, y - 10, 44, 2, GOLD_HIGHLIGHT)
    legs([x + 6 + 11 * k for k in range(4)], y + 36 + 6, 1, 10)
    box(x, y, 44, 36, 6, IC_BLACK if not burnt else IC_DARK, VOID_DEEP, hi=IC_DARK)
    text("N03", x + 12, y + 14, IC_DARK if not burnt else IC_GREY, 2)


QUADS = [(120, 82), (358, 82), (120, 448), (358, 448)]
for qi, (qx, qy) in enumerate(QUADS):
    for r_ in range(2):
        for c_ in range(3):
            burnt = (qi, r_, c_) == (3, 0, 1)
            x, y = E(qx + c_ * 56, qy + r_ * (66 if qi < 2 else -66) + 10)
            mosfet(x, y, burnt)
# a blown MOSFET in quadrant 1
bx, by = E(358 + 56 + 22, 448 + 10 + 18)
scorch(bx, by, 30)
for (dx, dy) in [(-10, -4), (-4, 0), (2, -2), (8, 3)]:
    rect(bx + dx, by + dy, 6, 2, LOGO_RED)
smoke(bx, by - 14, 6)

for (dx_, dy_) in DRV:  # gate drivers / ESC MCUs
    x, y = E(dx_, dy_)
    for k in range(4):
        rect(x - 5, y + 6 + 8 * k, 5, 4, ENIG_GOLD)
        rect(x + 36, y + 6 + 8 * k, 5, 4, ENIG_GOLD)
    box(x, y, 36, 36, 6, IC_DARK, IC_BLACK, hi=IC_GREY)
    fill(disc_m(x + 6, y + 7, 2), IC_GREY)

# the torn label: what's left of the sticker, one corner peeling
lab = [E(250, 270), E(330, 256), E(372, 262), E(404, 300), E(398, 352), E(352, 388), E(292, 380),
       E(262, 350), E(276, 328), E(244, 312)]
shade(shift(poly_m(lab), 4, 6))
fill(poly_m(lab), IC_BLACK)
hexpts = [E(326 + 34 * math.cos(math.radians(60 * k + 30)), 322 + 34 * math.sin(math.radians(60 * k + 30)))
          for k in range(6)]
hexm = poly_m(hexpts) & ~poly_m([(x + (x - E(326, 0)[0]) * -0.12, y + (y - E(0, 322)[1]) * -0.12)
                                  for (x, y) in hexpts])
fill(hexm & poly_m(lab), IC_GREY)
text("4IN1", *E(310, 314), IC_GREY, 2)
flap = [E(372, 262), E(404, 300), E(420, 270)]
shade(shift(poly_m(flap), 5, 7))
fill(poly_m(flap), SILKSCREEN_SHADE)
fill(poly_m([E(372, 262), E(404, 300), E(392, 276)]), SILKSCREEN_WHITE)

# current-sense shunt and a row of caps
box(*E(410, 500), 64, 26, 8, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)
text("R001", *E(424, 510), IC_GREY, 2)
for i in range(6):
    chip0603(*E(140 + i * 36, 300), vertical=True, body=COPPER_SHADOW if i % 2 else IC_DARK)
for i in range(3):
    chip0603(*E(250 + i * 40, 158))
chip0603(*E(160, 560))

# the water tower: big electrolytic lying across the battery pads
CAPX, CAPY = E(500, 236)
shade(mask(lambda d: d.rounded_rectangle([CAPX + 10, CAPY + 14, CAPX + 70, CAPY + 186], 26, fill=255)))
fill(mask(lambda d: d.rounded_rectangle([CAPX, CAPY, CAPX + 60, CAPY + 172], 26, fill=255)), GRAFFITI_PURPLE)
fill(mask(lambda d: d.rounded_rectangle([CAPX, CAPY, CAPX + 60, CAPY + 172], 26, fill=255))
     & ~mask(lambda d: d.rounded_rectangle([CAPX - 6, CAPY - 4, CAPX + 50, CAPY + 168], 26, fill=255)), DUSK_PURPLE)
rect(CAPX + 8, CAPY + 20, 8, 132, SMOKE_VIOLET)                    # highlight
rect(CAPX + 30, CAPY + 10, 10, 152, SILKSCREEN_WHITE)               # polarity stripe
for k in range(7):
    rect(CAPX + 32, CAPY + 22 + k * 20, 6, 3, DUSK_PURPLE)
fill(disc_m(CAPX + 30, CAPY + 172, 26, 8) & mask(
    lambda d: d.rounded_rectangle([CAPX, CAPY, CAPX + 60, CAPY + 172], 26, fill=255)), SILKSCREEN_SHADE)
text("AIK", CAPX + 12, CAPY + 70, LOGO_RED, 3)                       # marker tag

# battery pads + big leads off the east edge
for (py_, c, lab_) in [(206, LOGO_RED, "+"), (396, IC_DARK, "-")]:
    px_, pyy = E(590, py_)
    rect(px_, pyy, 50, 70, ENIG_GOLD)
    rect(px_, pyy, 50, 4, GOLD_HIGHLIGHT)
    wire([(px_ + 22, pyy + 35), (W + 40, pyy + 35 + (20 if c == IC_DARK else -10))], 24, c, ground_shadow=(10, 26))
    solder_blob(px_ + 18, pyy + 35, 16)
    text(lab_, px_ - 22, pyy + 26, SILKSCREEN_WHITE, 4)

# motor pads: top and bottom edges, wires leaving the map
for gi, (gx0, top, num) in enumerate([(130, True, "4"), (380, True, "2"), (130, False, "3"), (380, False, "1")]):
    for k in range(3):
        px_, py_ = E(gx0 + k * 56, 6 if top else ES - 46)
        rect(px_, py_, 40, 40, ENIG_GOLD)
        rect(px_, py_, 40, 4, GOLD_HIGHLIGHT)
        cx_, cy_ = px_ + 20, py_ + 20
        end = (cx_ + (k - 1) * 14, -40 if top else H + 40)
        wire([(cx_, cy_), end], 12, IC_DARK, ground_shadow=(10, 24))
        solder_blob(cx_, cy_, 11)
        if (gi, k) == (1, 2):
            blob(cx_ + 14, cy_ + 16, 12, SIGNAL_TEAL_DEEP)                  # corrosion
            blob(cx_ + 12, cy_ + 14, 6, SIGNAL_TEAL)
    nx_, ny_ = E(gx0 - 34, 60 if top else ES - 100)
    text(num, nx_, ny_, SILKSCREEN_WHITE, 5)

# ------------------------------------------------------------------ the bridge: 8-wire cable
WIRE_COLORS = [IC_DARK, LOGO_RED, SILKSCREEN_WHITE, WIRE_YELLOW, WIRE_BLUE, TRACE_HIGHLIGHT, COPPER, GRAFFITI_PURPLE]


def connector(x, y, facing):
    """JST-style receptacle (cream) at the board edge, pins toward 'facing'."""
    box(x, y, 34, 100, 12, SILKSCREEN_WHITE, SILKSCREEN_SHADE, hi=None)
    for i in range(8):
        yy = YCAB - 42 + 12 * i
        rect(x + (24 if facing > 0 else 2), yy - 3, 8, 6, IC_DARK)


fcx = FX + FS - 44
connector(fcx, YCAB - 50, +1)
ecx = EX + 10
connector(ecx, YCAB - 50, -1)
x_start, x_end = fcx + 30, ecx + 4
# plugs
box(x_start, YCAB - 54, 26, 108, 10, SILKSCREEN_WHITE, SILKSCREEN_SHADE, sh=(10, 22))
box(x_end - 26, YCAB - 54, 26, 108, 10, SILKSCREEN_WHITE, SILKSCREEN_SHADE, sh=(10, 22))
cable = np.zeros((H, W), bool)
wires_m = []
for i, c in enumerate(WIRE_COLORS):
    y = YCAB - 42 + 12 * i
    sag = 6
    pts = [(x_start + 26, y), ((x_start + x_end) / 2, y + sag), (x_end - 26, y)]
    m = line_m(pts, 10)
    wires_m.append((m, c))
    cable |= m
solid = np.array(Image.fromarray((cable * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
shade(shift(solid, 14, 34) & ~cable)
for m, c in wires_m:
    fill(m, c)
    fill(m & ~shift(m, 0, -3), SHADE[c])
box(x_start, YCAB - 54, 26, 108, 10, SILKSCREEN_WHITE, SILKSCREEN_SHADE, sh=None)
box(x_end - 26, YCAB - 54, 26, 108, 10, SILKSCREEN_WHITE, SILKSCREEN_SHADE, sh=None)
# heat-shrink band and a zip tie
mid = (x_start + x_end) // 2
box(mid - 14, YCAB - 52, 28, 108, 6, IC_BLACK, VOID_DEEP, sh=None, hi=IC_DARK)
box(x_start + 40, YCAB - 50, 6, 104, 4, SILKSCREEN_WHITE, SILKSCREEN_SHADE, sh=None)
rect(x_start + 38, YCAB + 50, 10, 10, SILKSCREEN_WHITE)
# data pulses on the signal wires
for i in (3, 4):
    y = YCAB - 42 + 12 * i
    for x0 in (x_start + 70, x_start + 150):
        rect(x0, y - 2 + 3, 12, 3, SIGNAL_PINK if i == 3 else GLOW_TEAL)

# ------------------------------------------------------------------ grime pass
for _ in range(40):  # solder balls
    x, y = rng.randrange(W), rng.randrange(H)
    if BOARDS[y, x]:
        shade(disc_m(x + 1, y + 2, 3))
        fill(disc_m(x, y, 3), SILKSCREEN_SHADE)
        put(x - 1, y - 1, SILKSCREEN_WHITE)
for (x, y) in [F(380, 40), E(200, 250), E(470, 560), F(30, 260)]:  # dust bunnies
    for k in range(5):
        blob(x + rng.randrange(-10, 10), y + rng.randrange(-6, 6), rng.randrange(5, 10), IC_GREY)
    blob(x, y, 6, SILKSCREEN_SHADE)
hair = []
hx, hy = E(150, 380)
for t in range(220):  # a hair across the ESC
    hx += math.cos(t * 0.03) * 1.2
    hy += math.sin(t * 0.05 + 1) * 0.8
    hair.append((hx, hy))
wire(hair, 2, IC_BLACK, ground_shadow=(2, 3))
for _ in range(7):  # scratches through the mask: bare copper on traces
    x, y = rng.randrange(W), rng.randrange(H)
    ang, ln = rng.uniform(-0.5, 0.5), rng.randrange(30, 90)
    for t in range(ln):
        xx, yy = int(x + t * math.cos(ang)), int(y + t * math.sin(ang))
        if 0 <= xx < W and 0 <= yy < H and BOARDS[yy, xx]:
            c = tuple(a[yy, xx])
            a[yy, xx] = COPPER if c in (TRACE_HIGHLIGHT, TRACE) else TRACE if c in (MASK, MASK_DEEP) else a[yy, xx]
            if 0 <= yy + 1 < H and c in (TRACE_HIGHLIGHT, TRACE, MASK, MASK_DEEP):
                a[yy + 1, xx] = SHADE.get(tuple(a[yy + 1, xx]), a[yy + 1, xx])
# flux and fingerprints near the connectors (somebody's been working here)
blob(EX + 60, YCAB + 70, 22, None)
blob(FX + FS - 80, YCAB + 80, 16, None)


# ------------------------------------------------------------------ characters
def stamp(grid_text, keys, x, y, foot_shadow=None, flat_shadow=None):
    g = sprites.grid(grid_text)
    if foot_shadow:
        w_, h_ = foot_shadow
        shade(disc_m(x + len(g[0]) / 2 + 1, y + len(g) - 1, w_, h_))
    if flat_shadow:
        m = np.zeros((H, W), bool)
        for yy, row in enumerate(g):
            for xx, ch in enumerate(row):
                if ch != "." and 0 <= y + yy + flat_shadow[1] < H and 0 <= x + xx + flat_shadow[0] < W:
                    m[y + yy + flat_shadow[1], x + xx + flat_shadow[0]] = True
        shade(m)
    for yy, row in enumerate(g):
        for xx, ch in enumerate(row):
            if ch != ".":
                put(x + xx, y + yy, P[keys[ch]])


# the pilot, standing on the bridge (32 px tall)
stamp(sprites.PILOT, sprites.PILOT_KEYS, mid - 40, YCAB - 30, foot_shadow=(9, 4))
# micro luci3D on the data bus, heading for the bridge
stamp(sprites.SNAKE, sprites.SNAKE_KEYS, FX + 424, YCAB + 50, flat_shadow=(3, 4))

# ------------------------------------------------------------------ export
out = Path(__file__).resolve().parent / "out"
out.mkdir(exist_ok=True)
img = Image.fromarray(a)
img.save(out / "stack-v1-world.png")
sx, sy, sw, sh_ = SCREEN
scr = img.crop((sx, sy, sx + sw, sy + sh_))
scr.save(out / "stack-v1-screen-1x.png")
scr.resize((sw * 2, sh_ * 2), Image.NEAREST).save(out / "stack-v1-screen-2x.png")
print("wrote", out, img.size)
