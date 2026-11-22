#!/usr/bin/env python3
"""FC City, mock-up v0: an old, grimy FPV flight controller seen as a city.

Drawn as code at the brand's base canvas (320x180) using only the colours in
brand/palette/luci3d.gpl. It's a starting point to react to and repaint in
Aseprite, not final art.

    python3 art/city/make_fc_city.py      -> art/city/out/fc-city-v0-{1x,4x}.png

The city: traces are roads, the MCU is downtown, the big capacitor is the water
tower, motor pads are the industrial edge, the OSD chip is the TV station and the
CAM/VTX pads are where analog video comes in and goes out. The snake (micro
luci3D) runs inside the video trace, lighting it up as it goes.
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
MASK_D, MASK, TRACE, TRACE_HI = P["mask deep"], P["mask"], P["trace"], P["trace highlight"]
COP, COP_D, GOLD, GOLD_HI = P["copper"], P["copper shadow"], P["enig gold"], P["gold highlight"]
WHITE, SILK_D, FLUX = P["silkscreen white"], P["silkscreen shade"], P["flux"]
TEAL, TEAL_D = P["signal teal"], P["signal teal deep"]
IC, IC_G = P["ic dark"], P["ic grey"]
RED, RED_O = P["burn red"], P["oxide red"]
VIOLET, DUSK, PURP = P["smoke violet"], P["dusk purple"], P["graffiti purple"]

W, H = 320, 180
rng = random.Random(3)
im = Image.new("RGB", (W, H), MASK)
pix = im.load()


def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        pix[x, y] = c


def get(x, y):
    return pix[x, y] if 0 <= x < W and 0 <= y < H else None


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            put(xx, yy, c)


def disc(cx, cy, r, c, dither=False):
    for yy in range(int(cy - r - 1), int(cy + r + 2)):
        for xx in range(int(cx - r - 1), int(cx + r + 2)):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r and (not dither or (xx + yy) % 2 == 0):
                put(xx, yy, c)


def text(s, x, y, c, scale=1, wear=0.0):
    for dx, dy in text_pixels(s, scale):
        if rng.random() >= wear:
            put(x + dx, y + dy, c)
        else:
            put(x + dx, y + dy, SILK_D if c == WHITE else c)


# ---------------------------------------------------------------- grime field
# Low-res random grid, smoothed: decides where dirt, flux and wear collect.
GW, GH = W // 10 + 2, H // 10 + 2
grid = [[rng.random() for _ in range(GW)] for _ in range(GH)]


def grime(x, y):
    gx, gy = x / 10, y / 10
    x0, y0 = int(gx), int(gy)
    fx, fy = gx - x0, gy - y0
    a = grid[y0][x0] * (1 - fx) + grid[y0][x0 + 1] * fx
    b = grid[y0 + 1][x0] * (1 - fx) + grid[y0 + 1][x0 + 1] * fx
    return a * (1 - fy) + b * fy


for y in range(H):
    for x in range(W):
        g = grime(x, y) + rng.random() * 0.18
        if g > 0.92:
            put(x, y, MASK_D)
        elif g > 0.78 and (x + y) % 2 == 0:
            put(x, y, MASK_D)

# ---------------------------------------------------------------- traces
traces = []  # (points, width)
copper = Image.new("L", (W, H), 0)
cd = ImageDraw.Draw(copper)


def trace(pts, w=3):
    traces.append((pts, w))
    cd.line(pts, fill=255, width=w, joint="curve")
    for p in pts:  # square-ish ends and corners
        r = (w - 1) / 2
        cd.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=255)


# Layout anchors
MCU = (122, 56, 40, 40)          # downtown: x, y, w, h
OSD = (46, 98, 31, 12)           # TV station
GYRO = (186, 30, 14, 14)
CAP = (270, 44, 20)              # water tower: cx, cy, r
PADS_Y = 146                      # 5V GND CAM VTX TX1 RX1 row
PAD_XS = [40, 58, 76, 94, 112, 130]
PAD_NAMES = ["5V", "GND", "CAM", "VTX", "TX1", "RX1"]
MOTOR_YS = [92, 114, 136, 158]


def qfp_pins(x, y, w, h, n, pitch=3):
    """Pin centre coordinates per side for a QFP-like body."""
    off = (w - (n - 1) * pitch) // 2
    return {
        "n": [(x + off + i * pitch, y) for i in range(n)],
        "s": [(x + off + i * pitch, y + h) for i in range(n)],
        "w": [(x, y + off + i * pitch) for i in range(n)],
        "e": [(x + w, y + off + i * pitch) for i in range(n)],
    }


mp = qfp_pins(*MCU, 12)
mx, my, mw, mh = MCU

# Power: battery pads (right, top) -> water tower -> regulator. Wide roads.
trace([(318, 14), (294, 14), (282, 26)], 7)
trace([(240, 70), (240, 90), (226, 104)], 5)
trace([(250, 44), (240, 54), (240, 70)], 5)

# Video path: CAM pad -> OSD in, OSD out -> VTX pad (the snake's road)
osd_s = [(OSD[0] + 2 + 3 * i, OSD[1] + OSD[3] + 3) for i in range(10)]
osd_n = [(OSD[0] + 2 + 3 * i, OSD[1]) for i in range(10)]
cam = (PAD_XS[2], PADS_Y)
vtx = (PAD_XS[3], PADS_Y)
VIDEO_IN = [cam, (cam[0], 132), (osd_s[7][0] + 4, 128), (osd_s[7][0], 124), (osd_s[7][0], osd_s[7][1] + 2)]
trace(VIDEO_IN, 3)
trace([vtx, (vtx[0], 128), (osd_s[9][0] + 8, 120), (osd_s[9][0] + 8, 106), (osd_s[9][0] + 4, 104)], 3)

# OSD <-> MCU (SPI bus, 4 lanes heading north-east into downtown)
for i, k in enumerate([3, 4, 5, 6]):
    sx, sy = osd_n[k]
    ty = mp["w"][3 + i][1]
    y_turn = 90 - 4 * i  # up, 45 degrees, then east into the MCU's west pins
    trace([(sx, sy - 2), (sx, y_turn), (sx + (y_turn - ty), ty), (mx - 3, ty)], 3)

# MCU -> gyro (north-east)
for i in range(3):
    px_, py_ = mp["n"][8 + i]
    gy = GYRO[1] + 3 + 4 * i
    trace([(px_, py_ - 3), (px_, gy + (GYRO[0] - 3 - px_)), (GYRO[0] - 3, gy)], 3)

AVENUES = []
# MCU east -> motor pads (four long avenues, 45-degree jog)
for i, my_ in enumerate(MOTOR_YS):
    ex, ey = mp["e"][4 + 2 * i]
    jog = my_ - ey
    AVENUES.append([(ex + 3, ey), (ex + 20 + 6 * i, ey), (ex + 20 + 6 * i + jog, my_), (296, my_)])
    trace([(ex + 3, ey), (ex + 20 + 6 * i, ey), (ex + 20 + 6 * i + jog, my_), (296, my_)], 3)

# MCU south -> TX1/RX1 pads
for i, k in enumerate([2, 4]):
    sx, sy = mp["s"][k]
    tx = PAD_XS[4 + i]
    trace([(sx, sy + 3), (sx, PADS_Y - 14 - (tx - sx) + 0), (tx, PADS_Y - 14), (tx, PADS_Y)], 3)

# 5V / GND pads up into a regulator block
trace([(PAD_XS[0], PADS_Y), (PAD_XS[0], 128), (30, 118), (30, 70)], 5)

# MCU north-west -> stuff near the mounting hole
for i in range(3):
    px_, py_ = mp["n"][1 + i]
    trace([(px_, py_ - 3), (px_, 40 - 4 * i), (px_ - 24 + 4 * i, 16 + 4 * i)], 3)

# --------------------------------------------------- ground pour (big copper areas)
pour = Image.new("L", (W, H), 0)
pd = ImageDraw.Draw(pour)
pd.rectangle([196, 150, W, H], fill=255)
pd.polygon([(0, 34), (16, 34), (16, 130), (0, 130)], fill=255)
pd.polygon([(176, 0), (240, 0), (240, 22), (210, 22), (204, 28), (176, 28)], fill=255)
keep = copper.copy()
from PIL import ImageFilter  # noqa: E402

keep = keep.filter(ImageFilter.MaxFilter(7))
pp, kp, cp = pour.load(), keep.load(), copper.load()
for y in range(H):
    for x in range(W):
        if pp[x, y] and not kp[x, y]:
            put(x, y, TRACE)

# Render traces: bright top, darker south edge (a little relief)
for y in range(H):
    for x in range(W):
        if cp[x, y]:
            below = cp[x, y + 1] if y + 1 < H else 255
            put(x, y, TRACE_HI if below else TRACE)


def tented(cx, cy):
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            put(cx + dx, cy + dy, TRACE_HI if dx + dy < 0 else MASK if dx + dy > 0 else TRACE_HI)
    put(cx, cy, MASK_D)


def via(cx, cy, big=False):
    r_out, r_in = (3.2, 1.2) if big else (2.2, 0.6)
    for yy in range(cy - 4, cy + 5):
        for xx in range(cx - 4, cx + 5):
            d = math.hypot(xx - cx, yy - cy)
            if d <= r_in:
                put(xx, yy, MASK_D)
            elif d <= r_out:
                lit = (xx - cx) + (yy - cy) < -1
                dark = (xx - cx) + (yy - cy) > 1
                put(xx, yy, GOLD_HI if lit else COP if dark else GOLD)


# Stitching vias on the pours (manholes)
for y in range(5, H, 12):
    for x in range(5 + (y // 12 % 2) * 6, W, 12):
        if pp[x, y] and not kp[x, y] and all(not kp[x + dx, y + dy] for dx in (-3, 3) for dy in (-3, 3)
                                             if 0 <= x + dx < W and 0 <= y + dy < H):
            tented(x, y)
for v in [(30, 70), (226, 104), (282, 26), (138, 26), (126, 28), (114, 32)]:
    via(*v, big=True)

# ---------------------------------------------------------------- components


def shadow(x, y, w, h, d=2):
    rect(x + d, y + d, w, h, MASK_D)


def block(x, y, w, h, top, side, height=2, d=2):
    """Top-down box with a visible south face (buildings). d=0: shadow drawn by the caller."""
    if d:
        shadow(x, y, w, h + height, d)
    rect(x, y, w, h, top)
    rect(x, y + h, w, height, side)


def pin(x, y, dx, dy, n=4):
    for i in range(n):
        put(x + dx * i, y + dy * i, GOLD if i == n - 1 else SILK_D)


# Downtown: the MCU, a skyscraper with lit windows
shadow(mx, my, mw, mh + 4, 3)
for side, (dx, dy) in {"n": (0, -1), "s": (0, 1), "w": (-1, 0), "e": (1, 0)}.items():
    for (px_, py_) in mp[side]:
        off = 4 if side == "s" else 0
        pin(px_ + dx, py_ + dy + off, dx, dy)
block(mx, my, mw, mh, IC, MASK_D, height=4, d=0)
rect(mx + 1, my + 1, mw - 2, 1, IC_G)  # roof edge highlight
for i in range(mw // 3):
    wx = mx + 2 + i * 3
    if wx < mx + mw - 1:
        lit = rng.random() < 0.45
        put(wx, my + mh + 1, GOLD_HI if lit else IC_G)
        put(wx, my + mh + 2, GOLD if lit else IC)
disc(mx + 5, my + 5, 1.6, IC_G)  # pin-1 dimple
text("STM32", mx + 10, my + 14, IC_G)
text("F405", mx + 12, my + 21, IC_G)
text("L3D", mx + 26, my + 31, PURP)  # roof tag
for i in range(3):
    put(mx + 26 + 2 + 4 * i, my + 36, PURP if i != 1 else DUSK)  # drips

# Gyro: small sealed vault
gx, gy, gw, gh = GYRO
for i in range(4):
    for s in range(3):
        put(gx - 1, gy + 3 + 3 * i, GOLD)
        put(gx + 3 + 3 * i, gy - 1, GOLD)
block(gx, gy, gw, gh, IC, MASK_D, height=2)
rect(gx + 1, gy + 1, gw - 2, 1, IC_G)
put(gx + 2, gy + 3, IC_G)
text("U2", gx - 1, gy - 8, WHITE, wear=0.3)

# OSD chip: the TV station (TSSOP with gull-wing legs top and bottom)
ox, oy, ow, oh = OSD
shadow(ox, oy, ow, oh + 3, 2)
for (px_, py_) in osd_n:
    pin(px_, py_ - 1, 0, -1, 3)
for (px_, py_) in osd_s:
    pin(px_, py_, 0, 1, 3)
block(ox, oy, ow, oh, IC, MASK_D, height=3, d=0)
rect(ox + 1, oy + 1, ow - 2, 1, IC_G)
text("AT7456", ox + 3, oy + 4, IC_G)
# antenna mast on the roof: it's the TV station
for i in range(9):
    put(ox + ow - 5, oy - 1 - i, SILK_D)
put(ox + ow - 6, oy - 7, SILK_D)
put(ox + ow - 4, oy - 7, SILK_D)
put(ox + ow - 5, oy - 10, RED)
text("OSD", ox - 14, oy + 3, WHITE, wear=0.25)

# Water tower: big electrolytic, violet sleeve, tagged
cx, cy, r = CAP
disc(cx + 3, cy + 3, r, MASK_D)
disc(cx, cy, r, DUSK)
disc(cx, cy, r - 1, PURP)
for a in range(0, 360, 2):  # polarity band
    if 200 <= a <= 250:
        put(round(cx + (r - 1) * math.cos(math.radians(a))), round(cy + (r - 1) * math.sin(math.radians(a))), WHITE)
        put(round(cx + (r - 2) * math.cos(math.radians(a))), round(cy + (r - 2) * math.sin(math.radians(a))), SILK_D)
disc(cx, cy, r - 4, SILK_D)
disc(cx - 1, cy - 1, r - 6, WHITE)
disc(cx + 1, cy + 1, r - 9, SILK_D)
for i in range(-9, 10):  # K vent
    put(cx + i, cy, IC_G)
    put(cx, cy + i, IC_G)
text("470", cx - 13, cy - 11, IC_G)
text("35V", cx + 3, cy + 6, IC_G)
text("AIK", cx - 13, cy + 3, RED)  # marker tag on the can

# Battery pads with fat old solder
for (py_, lab) in [(10, "+"), (30, "-")]:
    rect(296, py_, 24, 9, GOLD)
    rect(296, py_, 24, 1, GOLD_HI)
    disc(305, py_ + 4, 4, SILK_D)
    disc(304, py_ + 3, 2.5, WHITE)
    text(lab, 289, py_ + 2, WHITE)
text("BAT", 300, 42, WHITE, wear=0.2)

# Regulator, and a burnt one with magic smoke
block(234, 60, 12, 9, IC, MASK_D)
for i in range(3):
    pin(235 + 4 * i, 72, 0, 1, 2)
text("3V3", 248, 62, WHITE, wear=0.3)

bx, by = 258, 120
for yy in range(by - 9, by + 14):
    for xx in range(bx - 10, bx + 18):
        d = math.hypot(xx - (bx + 4), yy - (by + 3))
        if d < 6:
            put(xx, yy, IC if (xx + yy) % 3 else MASK_D)
        elif d < 9 and (xx + yy) % 2 == 0:
            put(xx, yy, COP_D)
        elif d < 11 and (xx * 7 + yy * 3) % 5 == 0:
            put(xx, yy, COP_D)
block(bx, by, 9, 7, IC, MASK_D)
for (xx, yy) in [(bx + 2, by + 2), (bx + 3, by + 3), (bx + 4, by + 3), (bx + 5, by + 4)]:
    put(xx, yy, RED_O)  # crack
smoke = [(0, -2), (1, -3), (1, -4), (0, -5), (-1, -6), (-1, -7), (0, -8), (1, -9), (2, -10), (2, -11),
         (3, -4), (4, -5), (4, -6), (3, -7)]
for i, (dx, dy) in enumerate(smoke):
    put(bx + 4 + dx, by + dy, VIOLET if i % 3 else DUSK)

# Decoupling caps around downtown: row houses
def chip0603(x, y, vertical=False, body=COP_D):
    if vertical:
        shadow(x, y, 3, 7, 1)
        rect(x, y, 3, 7, body)
        rect(x, y, 3, 2, SILK_D)
        rect(x, y + 5, 3, 2, SILK_D)
        put(x, y, WHITE)
    else:
        shadow(x, y, 7, 3, 1)
        rect(x, y, 7, 3, body)
        rect(x, y, 2, 3, SILK_D)
        rect(x + 5, y, 2, 3, SILK_D)
        put(x, y, WHITE)


for i in range(5):
    chip0603(mx - 14, my + 2 + i * 9, vertical=False, body=COP_D if i % 2 else IC)
for i in range(4):
    chip0603(mx + 4 + i * 9, my - 13, vertical=True)
for i in range(4):
    chip0603(mx + 6 + i * 9, my + mh + 12, vertical=False, body=IC if i % 2 else COP_D)
for i in range(3):
    chip0603(206 + i * 9, 34, vertical=True, body=IC)
chip0603(225, 108, body=COP_D)
chip0603(244, 80, vertical=True)
chip0603(20, 84, vertical=True)
chip0603(20, 96, vertical=True, body=IC)

# LEDs: one alive (teal glow), one dead
lx, ly = 210, 132
disc(lx + 3, ly + 1, 5, TEAL_D, dither=True)
rect(lx, ly, 7, 3, TEAL)
put(lx + 3, ly + 1, WHITE)
rect(lx, ly, 2, 3, SILK_D)
rect(lx + 5, ly, 2, 3, SILK_D)
text("STAT", lx - 2, ly + 5, WHITE, wear=0.3)
rect(lx + 22, ly, 7, 3, DUSK)
rect(lx + 22, ly, 2, 3, SILK_D)
rect(lx + 27, ly, 2, 3, SILK_D)

# BOOT button
block(226, 146, 12, 10, SILK_D, IC_G, height=2)
rect(227, 147, 10, 1, WHITE)
disc(232, 151, 2.5, IC)
text("BOOT", 224, 160, WHITE, wear=0.2)

# USB port: the harbour at the south edge
block(150, 166, 30, 14, SILK_D, IC_G, height=0)
rect(150, 166, 30, 1, WHITE)
for i in range(5):
    put(156 + i * 4, 170, IC_G)
rect(146, 168, 4, 6, GOLD)
rect(180, 168, 4, 6, GOLD)
text("USB", 159, 158, WHITE, wear=0.2)

# Mounting hole: the city gate, screw-scratched
hx, hy = 22, 20
for yy in range(hy - 17, hy + 18):
    for xx in range(hx - 17, hx + 18):
        d = math.hypot(xx - hx, yy - hy)
        if 15.5 <= d < 16.5 and (round(math.degrees(math.atan2(yy - hy, xx - hx))) // 12) % 2 == 0:
            put(xx, yy, WHITE)
        elif 7 <= d < 12:
            ang = math.atan2(yy - hy, xx - hx)
            c = GOLD_HI if -2.4 < ang < -1.0 else COP if 0.6 < ang < 2.2 else GOLD
            put(xx, yy, c)
        elif d < 7:
            put(xx, yy, MASK_D if d < 6 else COP_D)
for a0 in (0.3, 2.0, 4.1):  # screw scratches
    for t in range(14):
        a = a0 + t * 0.06
        put(round(hx + 9.5 * math.cos(a)), round(hy + 9.5 * math.sin(a)), COP_D)

# Pad row: 5V GND CAM VTX TX1 RX1
for i, (x, name) in enumerate(zip(PAD_XS, PAD_NAMES)):
    for yy in range(PADS_Y - 5, PADS_Y + 6):
        for xx in range(x - 5, x + 6):
            d = math.hypot(xx - x, yy - PADS_Y)
            if d < 1.5:
                put(xx, yy, MASK_D)
            elif d < 4.8:
                put(xx, yy, GOLD_HI if (xx - x) + (yy - PADS_Y) < -3 else GOLD)
    text(name, x - text_width(name) // 2, PADS_Y - 14 if i % 2 == 0 else PADS_Y + 7, WHITE, wear=0.15)
    if name in ("5V", "GND", "VTX"):  # old solder blobs and flux
        disc(x + 1, PADS_Y + 1, 6, FLUX, dither=True)
        disc(x, PADS_Y, 3.5, SILK_D)
        disc(x - 1, PADS_Y - 1, 2, WHITE)

# Motor pads on the industrial edge
for i, y in enumerate(MOTOR_YS):
    rect(298, y - 4, 22, 9, GOLD)
    rect(298, y - 4, 22, 1, GOLD_HI)
    rect(298, y + 4, 22, 1, COP)
    text(f"M{i + 1}", 285, y - 2, WHITE, wear=0.2)
    if i in (1, 2):
        disc(306, y, 7, FLUX, dither=True)
        disc(306, y, 3.5, SILK_D)
        disc(305, y - 1, 2, WHITE)
    if i == 3:  # cut motor wire still soldered on
        rect(306, y - 2, 14, 4, IC)
        rect(306, y - 2, 14, 1, IC_G)
        for k in range(3):
            put(304 - k, y - 1 + k % 2, COP)
        disc(303, y, 2.5, SILK_D)
# scorch next to M3
for yy in range(126, 146):
    for xx in range(276, 300):
        d = math.hypot(xx - 288, (yy - 136) * 1.4)
        if d < 5 and (xx + yy) % 2 == 0:
            put(xx, yy, MASK_D)
        elif d < 9 and (xx * 3 + yy * 5) % 4 == 0:
            put(xx, yy, COP_D)

# Bodge wire: luci3D's signature repair, MCU pin to the M2 avenue
p0 = (mp["e"][1][0] + 4, mp["e"][1][1])
p2 = (262, 100)
p1 = (205, 70)
pts = []
for t in [i / 200 for i in range(201)]:
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
    pts.append((round(x), round(y)))
for x, y in pts:
    put(x + 1, y + 1, MASK_D)
for x, y in pts:
    put(x, y, COP)
for (x, y) in (p0, p2):
    disc(x + 1, y + 1, 4, FLUX, dither=True)
    disc(x, y, 2, SILK_D)
    put(x - 1, y - 1, WHITE)

# ---------------------------------------------------------------- silkscreen + graffiti
text("F4 FC REV.1  2016", 44, 4, WHITE, wear=0.3)
text("LUCI3D", 44, 11, WHITE, wear=0.2)

# ANALOG IS KING, sprayed big across the south-west
tag = "ANALOG IS KING"
tx, ty = 8, 163
for dx, dy in text_pixels(tag, 2):
    for ox_, oy_ in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
        put(tx + dx + ox_, ty + dy + oy_, MASK_D)
for dx, dy in text_pixels(tag, 2):
    put(tx + dx, ty + dy, VIOLET if dy < 6 else PURP)
for k in range(14):  # drips
    dx = rng.randrange(0, text_width(tag, 2))
    if get(tx + dx, ty + 9) in (VIOLET, PURP):
        for j in range(rng.randrange(2, 6)):
            put(tx + dx, ty + 10 + j, PURP)

# hand-drawn snake tag in white paint near the gate
snake = [(44, 30), (45, 30), (46, 31), (47, 31), (48, 30), (49, 29), (50, 29), (51, 30), (52, 31), (53, 31),
         (54, 30), (55, 29), (56, 29), (57, 30)]
for x, y in snake:
    put(x, y, SILK_D)
put(58, 30, RED)
put(59, 29, RED)

# ---------------------------------------------------------------- dust, scratches, a stray fibre
for _ in range(110):
    x, y = rng.randrange(W), rng.randrange(H)
    if get(x, y) in (MASK, MASK_D, TRACE):
        put(x, y, SILK_D if rng.random() < 0.5 else IC_G)
for _ in range(4):
    x, y = rng.randrange(40, W - 40), rng.randrange(20, H - 20)
    ang = rng.uniform(-0.6, 0.6)
    for t in range(rng.randrange(18, 40)):
        xx, yy = round(x + t * math.cos(ang)), round(y + t * math.sin(ang))
        c = get(xx, yy)
        if c in (TRACE_HI, TRACE):
            put(xx, yy, COP)  # scratched through the mask: bare copper
        elif c in (MASK, MASK_D):
            put(xx, yy, TRACE)
fx, fy = 196.0, 150.0
for t in range(70):
    fx += math.cos(t * 0.15) * 0.9
    fy += math.sin(t * 0.09 + 1) * 0.7
    put(round(fx), round(fy), SILK_D)

# ---------------------------------------------------------------- the snake
# micro luci3D, running inside the M4 trace toward the motors, lighting it up
route = AVENUES[3]
path = []
for a, b in zip(route, route[1:]):
    n = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
    for i in range(n):
        path.append((round(a[0] + (b[0] - a[0]) * i / n), round(a[1] + (b[1] - a[1]) * i / n)))
corner = abs(route[1][0] - route[0][0])
head_i = corner + 13  # body wraps the 45-degree bend
BODY, GLOW, FADE = 34, 26, 22


def on_trace(x, y):
    return 0 <= x < W and 0 <= y < H and cp[x, y]


for i in range(max(0, head_i - BODY - GLOW - FADE), head_i - BODY):
    x, y = path[i]
    bright = i >= head_i - BODY - GLOW
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if on_trace(x + dx, y + dy) and (bright or (x + dx + y + dy) % 2 == 0):
                put(x + dx, y + dy, TEAL if bright else TEAL_D)
body = {}
for i in range(head_i - BODY, head_i):
    x, y = path[i]
    band = (head_i - i) % 7 == 0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if on_trace(x + dx, y + dy):
                body[(x + dx, y + dy)] = SILK_D if (band or dy == 1) else WHITE
hx_, hy_ = path[head_i]
nx, ny = path[min(head_i + 4, len(path) - 1)]
dx, dy = (nx > hx_) - (nx < hx_), (ny > hy_) - (ny < hy_)
for ex in range(-2, 3):
    for ey in range(-2, 3):
        if abs(ex) + abs(ey) <= 3:
            body[(hx_ + ex, hy_ + ey)] = WHITE
body[(hx_ - dy, hy_ + dx)] = MASK_D  # eye
for (x, y) in list(body):  # dark outline so it pops off the board
    for ox_, oy_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if (x + ox_, y + oy_) not in body:
            put(x + ox_, y + oy_, MASK_D)
for (x, y), c in body.items():
    put(x, y, c)
for k, (tx_, ty_) in enumerate([(3 * dx, 3 * dy), (4 * dx, 4 * dy), (5 * dx - dy, 5 * dy - dx), (5 * dx + dy, 5 * dy + dx),
                                 (6 * dx - dy, 6 * dy - dx), (6 * dx + dy, 6 * dy + dx)]):
    put(hx_ + tx_, hy_ + ty_, RED)
for ang in range(0, 360, 20):  # faint halo: it can see the circuit from inside
    rr = 6
    x, y = round(hx_ + rr * math.cos(math.radians(ang))), round(hy_ + rr * math.sin(math.radians(ang)))
    if get(x, y) in (MASK, MASK_D, TRACE):
        put(x, y, TEAL_D)

out = Path(__file__).resolve().parent / "out"
out.mkdir(exist_ok=True)
im.save(out / "fc-city-v0-1x.png")
im.resize((W * 4, H * 4), Image.NEAREST).save(out / "fc-city-v0-4x.png")
print("wrote", out)
