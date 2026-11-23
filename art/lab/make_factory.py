#!/usr/bin/env python3
"""The Line: the Lab's manufacturing bay (v2).

An open-frame desktop pick-and-place (drawn after the LumenPnP: black extrusion
frame, gantry, two-nozzle head, up and down cameras with ring lights, a feeder
rail with reels) runs next to a reflow oven, two 3D printers work on the side
bench, and the packing station holds trays of fresh boards and boxes ready to
ship with a small luci3D snake on each. In the corner, a heap of e-waste:
computer parts, wrecked FPV drones, a crashed delivery drone, robot parts.

The room is drawn in one-point perspective from a camera above head height, and
the machines are real 3D blocks (turned to show their sides), projected with
the same camera. 480 x 270, scaled up with hard pixels, palette colours only.
No brand names or logos other than ours.

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

# camera: at the world origin, looking along +Z; floor at Y = -HC; back wall at Z = ZB
VP = (240, 56)
FOC, HC, ZB = 300.0, 4.0, 10.0
BW = (100, 26, 380, VP[1] + FOC * HC / ZB)       # back wall rectangle on screen


# ================================================================= 2D helpers
def R(x0, y0, x1, y1, c):
    d.rectangle([round(min(x0, x1)), round(min(y0, y1)), round(max(x0, x1)), round(max(y0, y1))], fill=c)


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
    return x + (VP[0] - x) * t, y + (VP[1] - y) * t


def sag(x0, y0, x1, y1, dip, n=24):
    return [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n + dip * math.sin(math.pi * i / n)) for i in range(n + 1)]


# ================================================================= 3D: frames, blocks, discs
def proj(X, Y, Z):
    return VP[0] + FOC * X / Z, VP[1] - FOC * Y / Z


class Frame:
    """A local coordinate system standing on the floor: x right, y up from y0, z away from us."""

    def __init__(self, cx, cz, yaw=0.0, y0=0.0):
        self.cx, self.cz, self.yaw, self.y0 = cx, cz, yaw, y0
        self.c, self.s = math.cos(yaw), math.sin(yaw)

    def world(self, lx, ly, lz):
        return (self.cx + lx * self.c - lz * self.s, self.y0 + ly - HC, self.cz + lx * self.s + lz * self.c)

    def vec(self, nx, nz):
        return nx * self.c - nz * self.s, nx * self.s + nz * self.c

    def scr(self, lx, ly, lz):
        return proj(*self.world(lx, ly, lz))

    def child(self, lx, lz, dyaw=0.0, y0=0.0):
        X, _, Z = self.world(lx, 0, lz)
        return Frame(X, Z, self.yaw + dyaw, y0)


PRIMS = []      # (depth, draw function), drawn far to near


def lit_face(nx, nz):
    return -0.6 * nx - 0.8 * nz > 0.3          # light from the front-left


FACES = {
    "top":   ((0, 1, 0), lambda b, u, v: (b[0] + (b[1] - b[0]) * u, b[3], b[4] + (b[5] - b[4]) * v)),
    "front": ((0, 0, -1), lambda b, u, v: (b[0] + (b[1] - b[0]) * u, b[3] - (b[3] - b[2]) * v, b[4])),
    "back":  ((0, 0, 1), lambda b, u, v: (b[1] - (b[1] - b[0]) * u, b[3] - (b[3] - b[2]) * v, b[5])),
    "left":  ((-1, 0, 0), lambda b, u, v: (b[0], b[3] - (b[3] - b[2]) * v, b[5] - (b[5] - b[4]) * u)),
    "right": ((1, 0, 0), lambda b, u, v: (b[1], b[3] - (b[3] - b[2]) * v, b[4] + (b[5] - b[4]) * u)),
}


def lbox(fr, x0, x1, y0, y1, z0, z1, top, front, side, details=(), extra=None, depth_bias=0.0):
    """An axis-aligned block in frame fr. details: (face, u0, v0, u1, v1, colour) painted on faces."""
    b = (x0, x1, y0, y1, z0, z1)
    cz = fr.world((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)[2]

    def draw():
        vis = []
        for name, ((nx, ny, nz), fp) in FACES.items():
            wnx, wnz = fr.vec(nx, nz)
            cxw, cyw, czw = fr.world(*fp(b, 0.5, 0.5))
            if wnx * -cxw + ny * -cyw + wnz * -czw <= 0:
                continue
            vis.append((czw, name, fp, wnx, wnz))
        for czw, name, fp, wnx, wnz in sorted(vis, reverse=True):
            col = top if name == "top" else (front if lit_face(wnx, wnz) else side)
            poly([fr.scr(*fp(b, u, v)) for u, v in ((0, 0), (1, 0), (1, 1), (0, 1))], col)
            for (f, u0, v0, u1, v1, c) in details:
                if f == name:
                    poly([fr.scr(*fp(b, u, v)) for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))], c)
        if extra:
            extra()
    PRIMS.append((cz + depth_bias, draw))


def ldisc(fr, lx, ly, lz, r, axis, col, inner, hub, depth_bias=0.0):
    """A disc (reel, spool) standing upright; axis 'x' faces sideways, 'z' faces us."""
    X, Y, Z = fr.world(lx, ly, lz)
    nx, nz = fr.vec(1, 0) if axis == "x" else fr.vec(0, 1)

    def draw():
        cx, cy = proj(X, Y, Z)
        ry = FOC * r / Z
        rx = ry * max(0.22, abs(nz))
        ell(cx, cy, rx, ry, col)
        ell(cx, cy, rx * 0.62, ry * 0.62, inner)
        ell(cx, cy, max(0.6, rx * 0.22), max(0.8, ry * 0.22), hub)
    PRIMS.append((Z + depth_bias, draw))


def lline(fr, pts, col, w=1, depth_bias=0.0):
    Z = sum(fr.world(*p)[2] for p in pts) / len(pts)
    PRIMS.append((Z + depth_bias, lambda: line([fr.scr(*p) for p in pts], col, w)))


def bench(fr, w, dpt, h=0.9, top=FR4_EDGE):
    """A bench; drawn before whatever stands on it."""
    lbox(fr, -w / 2, w / 2, h - 0.08, h, -dpt / 2, dpt / 2, top, FR4_SHADE, COPPER_SHADOW, depth_bias=0.4)
    for lx in (-w / 2 + 0.04, w / 2 - 0.12):
        for lz in (-dpt / 2 + 0.04, dpt / 2 - 0.12):
            lbox(fr, lx, lx + 0.08, 0, h - 0.08, lz, lz + 0.08, IC_GREY, IC_DARK, IC_BLACK, depth_bias=0.4)


def floor_shadow(fr, x0, x1, z0, z1):
    poly([fr.scr(x0, 0, z0), fr.scr(x1, 0, z0), fr.scr(x1, 0, z1), fr.scr(x0, 0, z1)], BLACK_MASK_DEEP)


# ================================================================= the room
x0, y0, x1, y1 = BW
poly([(0, 0), (W, 0), (x1, y0), (x0, y0)], IC_BLACK)
poly([(x0, y1), (x1, y1), (W, H), (0, H)], BLACK_MASK)
poly([(0, 0), (x0, y0), (x0, y1), (0, H)], VOID)
poly([(W, 0), (x1, y0), (x1, y1), (W, H)], VOID)
R(x0, y0, x1, y1, VOID_MID)
for zf in (9, 8, 7, 6.2, 5.5, 4.9):                                       # floor tiles, true perspective
    line([proj(-6, -HC, zf), proj(6, -HC, zf)], BLACK_TRACE)
for xf in range(-6, 7):
    line([proj(xf, -HC, 4.4), proj(xf, -HC, ZB)], BLACK_TRACE)
for xb in (60, 180, 300, 420):
    a, b = (xb, 0), tv(xb, 0, 0.45)
    line([a, b], IC_DARK, 3)
    line([(a[0] + 2, a[1]), (b[0] + 1, b[1])], IC_GREY)
R(x0, y0, x1, y0 + 1, SIGNAL_PINK)
R(x0, y0 + 2, x1, y0 + 4, GRAFFITI_PURPLE)
R(x0, y0 + 5, x1, y0 + 7, DUSK_PURPLE)

# back wall: reel shelving and the production board
for ys in (40, 64, 88, 112, 136):
    R(104, ys + 14, 152, ys + 15, SILKSCREEN_SHADE)
    for i in range(4):
        cx = 110 + i * 12
        ell(cx, ys + 7, 6, 7, IC_BLACK)
        ell(cx, ys + 7, 5, 6, IC_DARK)
        ell(cx, ys + 7, 2, 2, rng.choice([WIRE_YELLOW, WIRE_BLUE, SILKSCREEN_WHITE, LOGO_RED, GLOW_TEAL]))
R(102, 38, 103, 152, SILKSCREEN_SHADE)
R(153, 38, 154, 152, SILKSCREEN_SHADE)
R(300, 38, 374, 78, IC_GREY)
R(302, 40, 372, 76, SIGNAL_TEAL_DEEP)
text("LINE 01", 305, 43, GLOW_TEAL)
for i, hgt in enumerate((14, 20, 11, 24, 18, 22)):
    R(306 + i * 10, 72 - hgt, 312 + i * 10, 72, GLOW_TEAL if i != 2 else SIGNAL_PINK)

# ceiling: a few runs, three shop lamps
for i in range(6):
    xa = rng.randrange(-20, W + 20)
    xb = xa + rng.choice([-1, 1]) * rng.randrange(60, 160)
    ya, yb = tv(xa, 0, rng.uniform(0, 0.4))[1], tv(xb, 0, rng.uniform(0, 0.4))[1]
    line(sag(xa, max(0, ya), xb, max(0, yb), rng.randrange(6, 18)), rng.choice([IC_DARK, IC_GREY, WIRE_BLUE, LOGO_RED]))
for lx, ly, sz in ((200, 20, 1.0), (380, 14, 1.15), (70, 10, 1.25)):
    line([(lx, 0), (lx, ly)], IC_DARK)
    poly([(lx - 10 * sz, ly + 8 * sz), (lx - 3 * sz, ly), (lx + 3 * sz, ly), (lx + 10 * sz, ly + 8 * sz)], IC_GREY)
    poly([(lx - 10 * sz, ly + 8 * sz), (lx + 10 * sz, ly + 8 * sz), (lx + 8 * sz, ly + 9 * sz),
          (lx - 8 * sz, ly + 9 * sz)], SILKSCREEN_WHITE)

# ================================================================= the pick-and-place bench
BENCH = Frame(-0.55, 7.1, yaw=-0.32)
floor_shadow(BENCH, -1.75, 1.75, -1.15, 1.15)
for (xa, za, xb_, zb_) in ((-1.9, -1.3, 1.9, -1.3), (1.9, -1.3, 1.9, 1.3), (-1.9, -1.3, -1.9, 1.3)):
    p0, p1 = BENCH.scr(xa, 0, za), BENCH.scr(xb_, 0, zb_)                # yellow safety marking
    n = int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / 6)
    for k in range(0, n, 2):
        line([(p0[0] + (p1[0] - p0[0]) * k / n, p0[1] + (p1[1] - p0[1]) * k / n),
              (p0[0] + (p1[0] - p0[0]) * (k + 1) / n, p0[1] + (p1[1] - p0[1]) * (k + 1) / n)], WIRE_YELLOW)
bench(BENCH, 3.3, 2.0)

M = BENCH.child(-0.35, 0.05, y0=0.9)                                    # the machine sits on the bench
MW, MD, MH, E = 1.1, 0.8, 1.0, 0.07
# bed: staging plates full of slots, the board being populated, the up-looking camera
lbox(M, -MW + E, MW - E, 0.02, 0.06, -MD + E, MD - E, IC_BLACK, IC_DARK, IC_BLACK,
     details=[("top", 0.06 + 0.11 * k, 0.1, 0.1 + 0.11 * k, 0.9, IC_DARK) for k in range(8)])
lbox(M, -0.32, 0.32, 0.06, 0.09, -0.2, 0.28, BLACK_TRACE, IC_DARK, IC_BLACK,
     details=[("top", 0.08 + 0.14 * i, 0.12 + 0.18 * j, 0.14 + 0.14 * i, 0.2 + 0.18 * j, ENIG_GOLD if (i + j) % 3 else IC_DARK)
              for i in range(6) for j in range(4)]
     + [("top", 0.0, 0.0, 1.0, 0.06, ENIG_GOLD), ("top", 0.0, 0.94, 1.0, 1.0, ENIG_GOLD),
        ("top", 0.0, 0.0, 0.04, 1.0, ENIG_GOLD), ("top", 0.96, 0.0, 1.0, 1.0, ENIG_GOLD)], depth_bias=-0.01)
lbox(M, -0.78, -0.6, 0.06, 0.16, -0.6, -0.44, IC_DARK, IC_GREY, IC_BLACK,
     details=[("top", 0.15, 0.15, 0.85, 0.85, SILKSCREEN_WHITE), ("top", 0.35, 0.35, 0.65, 0.65, IC_BLACK)])
# frame: black extrusions, base, posts, top
lbox(M, -MW, MW, 0, E, -MD, -MD + E, IC_GREY, IC_DARK, IC_BLACK)
lbox(M, -MW, MW, 0, E, MD - E, MD, IC_GREY, IC_DARK, IC_BLACK)
lbox(M, -MW, -MW + E, 0, E, -MD, MD, IC_GREY, IC_DARK, IC_BLACK)
lbox(M, MW - E, MW, 0, E, -MD, MD, IC_GREY, IC_DARK, IC_BLACK)
for sx in (-MW, MW - E):
    for sz in (-MD, MD - E):
        lbox(M, sx, sx + E, E, MH, sz, sz + E, IC_GREY, IC_DARK, IC_BLACK)
for sx in (-MW, MW - E):                                                # top rails along Y, with linear rails on them
    lbox(M, sx, sx + E, MH - E, MH, -MD, MD, IC_GREY, IC_DARK, IC_BLACK,
         details=[("top", 0.3, 0.02, 0.7, 0.98, SILKSCREEN_SHADE)])
lbox(M, -MW, MW, MH - E, MH, MD - E, MD, IC_GREY, IC_DARK, IC_BLACK)
# gantry, head, nozzles, down camera, cable chain
GZ, HX = 0.02, -0.18
lbox(M, -MW + 0.02, MW - 0.02, MH, MH + 0.08, GZ - 0.05, GZ + 0.05, IC_GREY, IC_DARK, IC_BLACK,
     details=[("front", 0.02, 0.2, 0.98, 0.45, SILKSCREEN_SHADE)])
lbox(M, HX - 0.16, HX + 0.16, MH - 0.3, MH + 0.12, GZ - 0.17, GZ - 0.05, SILKSCREEN_WHITE, SILKSCREEN_SHADE, IC_GREY,
     details=[("front", 0.12, 0.12, 0.42, 0.42, IC_DARK), ("front", 0.58, 0.12, 0.88, 0.42, IC_DARK),
              ("front", 0.46, 0.15, 0.54, 0.25, GLOW_TEAL)], depth_bias=-0.02)
for nx_ in (HX - 0.08, HX + 0.08):
    lbox(M, nx_ - 0.012, nx_ + 0.012, MH - 0.5, MH - 0.3, GZ - 0.12, GZ - 0.1, SILKSCREEN_SHADE, SILKSCREEN_WHITE,
         SILKSCREEN_SHADE, depth_bias=-0.03)
lbox(M, HX + 0.18, HX + 0.3, MH - 0.24, MH - 0.08, GZ - 0.16, GZ - 0.06, IC_DARK, IC_BLACK, IC_BLACK,
     details=[("front", 0.15, 0.6, 0.85, 1.0, GLOW_TEAL)], depth_bias=-0.03)            # down camera + ring light
lbox(M, HX, MW - 0.05, MH + 0.08, MH + 0.13, GZ - 0.02, GZ + 0.04, IC_DARK, IC_BLACK, IC_BLACK,
     details=[("front", 0.05 + 0.09 * k, 0.0, 0.09 + 0.09 * k, 1.0, IC_GREY) for k in range(10)])   # cable chain
# feeder rail across the front, feeders on it, reels hanging off the front
lbox(M, -MW, MW, 0.1, 0.2, -MD - 0.1, -MD, IC_GREY, IC_DARK, IC_BLACK)
for k in range(10):
    fx = -MW + 0.14 + k * 0.2
    lbox(M, fx - 0.06, fx + 0.06, 0.2, 0.27, -MD - 0.1, -MD + 0.12, SILKSCREEN_WHITE, SILKSCREEN_SHADE, IC_GREY,
         details=[("top", 0.3, 0.1, 0.7, 0.3, GLOW_TEAL if k % 4 else SIGNAL_PINK)], depth_bias=-0.05)
    ldisc(M, fx, -0.08, -MD - 0.28, 0.2, "x", IC_BLACK, IC_DARK,
          [WIRE_YELLOW, SILKSCREEN_WHITE, WIRE_BLUE, LOGO_RED][k % 4], depth_bias=-0.06)
# OpenPnP on a monitor at the end of the bench
MON = BENCH.child(1.2, -0.1, y0=0.9)
lbox(MON, -0.05, 0.05, 0, 0.25, 0.05, 0.12, IC_GREY, IC_DARK, IC_BLACK)
lbox(MON, -0.32, 0.32, 0.22, 0.62, -0.03, 0.05, IC_DARK, IC_GREY, IC_BLACK,
     details=[("front", 0.06, 0.08, 0.94, 0.92, SIGNAL_TEAL_DEEP), ("front", 0.48, 0.2, 0.52, 0.8, GLOW_TEAL),
              ("front", 0.25, 0.48, 0.75, 0.52, GLOW_TEAL), ("front", 0.42, 0.4, 0.58, 0.6, BLACK_TRACE)])

# ================================================================= reflow oven on a cart
OVEN = Frame(1.55, 7.6, yaw=-0.18)
floor_shadow(OVEN, -0.55, 0.55, -0.45, 0.45)
bench(OVEN, 1.0, 0.8, h=0.8, top=IC_GREY)
lbox(OVEN, -0.45, 0.45, 0.8, 1.3, -0.34, 0.34, IC_GREY, IC_DARK, IC_BLACK,
     details=[("front", 0.06, 0.18, 0.7, 0.62, VOID_DEEP)]
     + [("front", 0.1 + 0.08 * k, 0.26, 0.13 + 0.08 * k, 0.54, LOGO_RED) for k in range(7)]
     + [("front", 0.76, 0.18, 0.94, 0.34, VOID_DEEP), ("front", 0.79, 0.22, 0.91, 0.3, LOGO_RED),
        ("front", 0.06, 0.72, 0.7, 0.8, SILKSCREEN_SHADE)])

# ================================================================= 3D printers on the side bench
PB = Frame(3.3, 6.9, yaw=0.16)
floor_shadow(PB, -1.45, 1.45, -0.7, 0.7)
bench(PB, 2.8, 1.3)
EP = PB.child(-0.72, 0.0, y0=0.9)                                       # enclosed printer
lbox(EP, -0.48, 0.48, 0, 1.0, -0.46, 0.46, IC_GREY, IC_DARK, IC_BLACK,
     details=[("front", 0.06, 0.06, 0.94, 0.8, VOID_DEEP),
              ("front", 0.08, 0.16, 0.92, 0.19, IC_GREY),                 # gantry
              ("front", 0.42, 0.16, 0.58, 0.3, IC_DARK), ("front", 0.48, 0.3, 0.52, 0.33, LOGO_RED),
              ("front", 0.15, 0.7, 0.85, 0.73, IC_GREY)]                  # bed
     + [("front", 0.3 + 0.01 * (i % 2), 0.68 - 0.035 * i, 0.66 - 0.01 * (i % 2), 0.7 - 0.035 * i,
         GRAFFITI_PURPLE if i % 2 else SMOKE_VIOLET) for i in range(8)]   # the print
     + [("front", 0.08, 0.84, 0.36, 0.94, SIGNAL_TEAL_DEEP), ("front", 0.12, 0.87, 0.3, 0.9, GLOW_TEAL),
        ("left", 0.08, 0.08, 0.92, 0.75, VOID_DEEP), ("right", 0.08, 0.08, 0.92, 0.75, VOID_DEEP)])
lbox(EP, -0.04, 0.04, 1.0, 1.2, 0.05, 0.12, IC_GREY, IC_DARK, IC_BLACK)
ldisc(EP, 0, 1.3, 0.08, 0.2, "z", GRAFFITI_PURPLE, DUSK_PURPLE, IC_GREY, depth_bias=-0.2)
OP = PB.child(0.76, 0.0, y0=0.9)                                        # open-frame printer
lbox(OP, -0.44, 0.44, 0, 0.14, -0.46, 0.46, IC_GREY, IC_DARK, IC_BLACK,
     details=[("front", 0.06, 0.25, 0.3, 0.75, SIGNAL_TEAL_DEEP)])
lbox(OP, -0.34, 0.34, 0.16, 0.19, -0.36, 0.36, ENIG_GOLD, COPPER, COPPER_SHADOW)        # gold PEI bed
lbox(OP, -0.1, 0.14, 0.19, 0.29, -0.08, 0.12, WIRE_YELLOW, GOLD_HIGHLIGHT, ENIG_GOLD, depth_bias=-0.01)
for sx in (-0.44, 0.38):
    lbox(OP, sx, sx + 0.06, 0.14, 1.05, 0.0, 0.07, IC_GREY, IC_DARK, IC_BLACK)
lbox(OP, -0.44, 0.44, 1.0, 1.06, 0.0, 0.07, IC_GREY, IC_DARK, IC_BLACK)
lbox(OP, -0.4, 0.4, 0.5, 0.55, -0.02, 0.03, SILKSCREEN_SHADE, IC_GREY, IC_DARK)          # X gantry
lbox(OP, 0.0, 0.14, 0.36, 0.56, -0.1, -0.02, IC_DARK, IC_BLACK, IC_BLACK,
     details=[("front", 0.3, 0.85, 0.7, 1.0, LOGO_RED)], depth_bias=-0.02)                # hotend
ldisc(OP, 0.0, 1.28, 0.04, 0.2, "z", WIRE_YELLOW, ENIG_GOLD, IC_GREY, depth_bias=-0.2)
lline(OP, [(0.12, 1.2, 0.04), (0.2, 0.9, 0.0), (0.09, 0.56, -0.06)], WIRE_YELLOW, depth_bias=-0.3)

# draw the 3D world, far to near
for _, fn in sorted(PRIMS, key=lambda t: -t[0]):
    fn()
PRIMS.clear()

# ================================================================= packing station (front left)
LOGO = (ROOT / "brand" / "tools" / "make_logo.py").read_text().split('GRID = """')[1].split('"""')[0]
LOGO_ROWS = LOGO.strip("\n").splitlines()


def logo(x, y, c, step):
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


def box2(xa, xb, yb, h, t, top, front, side):
    yt = yb - h
    if xb < VP[0]:
        poly([(xb, yt), (xb, yb), tv(xb, yb, t), tv(xb, yt, t)], side)
    if yt > VP[1]:
        poly([(xa, yt), (xb, yt), tv(xb, yt, t), tv(xa, yt, t)], top)
    R(xa, yt, xb, yb, front)
    return yt


def ship_box(xa, xb, yb, h, t=0.05, label=True):
    yt = box2(xa, xb, yb, h, t, FR4_EDGE, FR4_SHADE, COPPER_SHADOW)
    mx = (xa + xb) / 2
    poly([(mx - 2, yt), (mx + 2, yt), tv(mx + 2, yt, t), tv(mx - 2, yt, t)], COPPER)      # tape
    for step in (2, 3, 4):                                                  # the snake, small, and always on the box
        lw, lh = -(-len(LOGO_ROWS[0]) // step), -(-len(LOGO_ROWS) // step)
        if lw <= (xb - xa) * 0.42 and lh <= h - 6:
            logo(xa + 4, yt + (h - lh) // 2, IC_BLACK, step)
            break
    if label and h >= 20:
        lw = (xb - xa) * 0.34
        R(xb - lw - 3, yb - h * 0.45, xb - 3, yb - 4, SILKSCREEN_WHITE)
        for i in range(3):
            line([(xb - lw - 1, yb - h * 0.45 + 3 + i * 3), (xb - 6 - i * 3, yb - h * 0.45 + 3 + i * 3)], IC_GREY)


poly([(0, 202), (124, 202), (130, 210), (0, 210)], FR4_SHADE)               # packing table
R(0, 210, 130, 214, COPPER_SHADOW)
for lx in (6, 120):
    R(lx, 214, lx + 4, 252, IC_DARK)
R(6, 188, 28, 200, SILKSCREEN_SHADE)                                         # anti-static bags
R(8, 190, 26, 191, SIGNAL_PINK)
R(10, 184, 32, 196, SILKSCREEN_WHITE)
R(12, 186, 30, 187, SIGNAL_PINK)
for k in range(5):                                                           # trays of fresh boards
    ty = 202 - k * 7
    box2(40, 112, ty, 6, 0.05, IC_DARK, IC_BLACK, IC_BLACK)
    for i in range(5):
        pcb(43 + i * 14, ty - 5, 11, 3, leds=False)
R(98, 160, 120, 168, LOGO_RED)                                               # tape gun on top of the trays
R(100, 156, 112, 160, IC_DARK)
ell(118, 158, 4, 4, COPPER)
ship_box(4, 60, 240, 26)                                                     # boxes ready to go
ship_box(4, 66, 270, 32)
ship_box(70, 128, 270, 32)
ship_box(74, 122, 240, 24)
ship_box(132, 172, 268, 24)

# ================================================================= the e-waste heap (front right)
SHADE_LIT = {IC_DARK: IC_GREY, SILKSCREEN_WHITE: SILKSCREEN_WHITE, IC_BLACK: IC_DARK, LOGO_RED: SIGNAL_PINK,
             WIRE_BLUE: GLOW_TEAL}


def drone(cx, cy, r, arms=4, tilt=0.0, flat=0.42, broken=(), dangling=(), noprop=(), body=IC_DARK,
          battery=None, props=(SIGNAL_PINK, IC_GREY), led=None):
    ca, sa = math.cos(tilt), math.sin(tilt)

    def T(x, y):
        return cx + x * ca - y * sa, cy + x * sa + y * ca
    angs = [math.radians({4: 45, 6: 0, 8: 22.5}[arms] + 360 * i / arms) for i in range(arms)]
    aw, mr = max(2, round(r / 9)), max(2, r / 10)

    def carbon(a, b):
        line([a, b], IC_DARK, aw)
        line([(a[0], a[1] - aw / 2), (b[0], b[1] - aw / 2)], IC_GREY)

    def arm(i):
        ex, ey = r * math.cos(angs[i]), r * math.sin(angs[i]) * flat
        if i in broken:
            carbon(T(0, 0), T(ex * 0.45, ey * 0.45))
            px(*T(ex * 0.47, ey * 0.47), IC_GREY)
            return
        if i in dangling:
            carbon(T(0, 0), T(ex * 0.5, ey * 0.5))
            fx, fy = T(ex * 0.5, ey * 0.5)
            carbon((fx, fy), (fx + ex * 0.1, fy + r * 0.5))
            line([(fx + 1, fy), (fx + 3, fy + r * 0.45)], LOGO_RED)
            return
        carbon(T(0, 0), T(ex, ey))
        mx, my = T(ex, ey)
        R(mx - mr, my - mr, mx + mr, my, SILKSCREEN_SHADE)
        ell(mx, my - mr, mr, mr * 0.5, SILKSCREEN_WHITE)
        if i not in noprop:
            pr, pa = r * 0.55, math.radians(25 + 53 * i)
            line([(mx - pr * math.cos(pa), my - mr * 1.2 - pr * math.sin(pa) * flat),
                  (mx + pr * math.cos(pa), my - mr * 1.2 + pr * math.sin(pa) * flat)], props[i % len(props)], 2 if r >= 24 else 1)
    for i in [i for i in range(arms) if math.sin(angs[i]) < 0]:
        arm(i)
    bw, bh = r * 0.3, r * 0.42 * flat + 1
    poly([T(-bw, -bh), T(bw, -bh), T(bw, bh), T(-bw, bh)], body)
    poly([T(-bw, -bh), T(bw, -bh), T(bw, -bh + 1), T(-bw, -bh + 1)], SHADE_LIT.get(body, IC_GREY))
    if battery:
        poly([T(-bw * 0.7, -bh - 2), T(bw * 0.7, -bh - 2), T(bw * 0.7, bh - 2), T(-bw * 0.7, bh - 2)], battery)
    if led:
        px(*T(bw * 0.6, 0), led)
    for i in [i for i in range(arms) if math.sin(angs[i]) >= 0]:
        arm(i)
    return T


def motherboard(x, y):
    R(x, y, x + 34, y + 24, MASK)
    R(x, y, x + 34, y, TRACE_HIGHLIGHT)
    R(x + 5, y + 5, x + 13, y + 13, SILKSCREEN_SHADE)                     # CPU socket
    R(x + 7, y + 7, x + 11, y + 11, IC_GREY)
    for k in range(3):                                                    # RAM slots
        line([(x + 17 + k * 2, y + 3), (x + 17 + k * 2, y + 15)], IC_BLACK)
    for k in range(2):                                                    # PCIe slots
        line([(x + 3, y + 18 + k * 3), (x + 24, y + 18 + k * 3)], IC_BLACK)
    R(x + 28, y - 3, x + 34, y + 7, IC_GREY)                              # I/O shield
    for k in range(4):
        px(x + 4 + k * 3, y + 15, IC_DARK)


def ram(x, y):
    R(x, y, x + 22, y + 5, MASK)
    for k in range(4):
        R(x + 2 + k * 5, y + 1, x + 5 + k * 5, y + 3, IC_BLACK)
    line([(x, y + 5), (x + 22, y + 5)], ENIG_GOLD)


def gpu(x, y):
    R(x, y, x + 32, y + 11, IC_DARK)
    R(x, y, x + 32, y, IC_GREY)
    R(x, y + 10, x + 32, y + 11, LOGO_RED)
    for fx in (x + 9, x + 23):
        ell(fx, y + 5, 4.5, 4.5, IC_BLACK)
        line([(fx - 3, y + 5), (fx + 3, y + 5)], IC_GREY)
        line([(fx, y + 2), (fx, y + 8)], IC_GREY)
    line([(x + 4, y + 12), (x + 24, y + 12)], ENIG_GOLD)


def psu(x, y):
    R(x, y, x + 18, y + 14, IC_GREY)
    R(x, y, x + 18, y + 2, SILKSCREEN_SHADE)
    ell(x + 9, y + 8, 5, 5, IC_DARK)
    line([(x + 5, y + 8), (x + 13, y + 8)], IC_GREY)
    line([(x + 9, y + 4), (x + 9, y + 12)], IC_GREY)
    for k, c in enumerate((WIRE_YELLOW, LOGO_RED, IC_DARK)):
        line(sag(x + 18, y + 4 + k * 3, x + 30, y + 10 + k * 3, 3, 6), c)


def hdd(x, y):
    R(x, y, x + 14, y + 10, SILKSCREEN_SHADE)
    R(x, y, x + 14, y, SILKSCREEN_WHITE)
    ell(x + 6, y + 5, 3.5, 3.5, IC_GREY)
    px(x + 6, y + 5, SILKSCREEN_WHITE)


def robot_arm(x, y):
    line([(x, y), (x + 18, y - 10)], WIRE_YELLOW, 5)
    line([(x + 18, y - 10), (x + 30, y - 4)], WIRE_YELLOW, 4)
    line([(x, y - 2), (x + 18, y - 12)], GOLD_HIGHLIGHT)
    for jx, jy in ((x, y), (x + 18, y - 10)):
        ell(jx, jy, 4, 4, IC_GREY)
        ell(jx, jy, 2, 2, IC_DARK)
    line([(x + 30, y - 4), (x + 35, y - 7)], IC_GREY, 2)
    line([(x + 30, y - 4), (x + 35, y - 1)], IC_GREY, 2)


def robot_head(x, y):
    R(x, y, x + 16, y + 12, IC_GREY)
    R(x, y, x + 16, y + 2, SILKSCREEN_SHADE)
    for ex, c in ((x + 4, GLOW_TEAL), (x + 11, LOGO_RED)):
        ell(ex, y + 6, 3, 3, IC_BLACK)
        px(ex, y + 6, c)
    line([(x + 9, y + 3), (x + 12, y + 9)], IC_BLACK)                     # crack
    line([(x + 8, y), (x + 8, y - 5)], IC_GREY)
    px(x + 8, y - 6, LOGO_RED)


def track(x, y):
    R(x, y, x + 24, y + 7, IC_BLACK)
    for k in range(4):
        ell(x + 4 + k * 5.5, y + 3.5, 2.5, 2.5, IC_GREY)
    for k in range(0, 24, 3):
        px(x + k, y, IC_DARK)


def servo(x, y):
    R(x, y, x + 8, y + 5, WIRE_BLUE)
    R(x, y, x + 8, y, GLOW_TEAL)
    line([(x + 2, y - 1), (x + 7, y - 1)], SILKSCREEN_WHITE)


def delivery_drone(x, y):
    drone(x, y, 26, arms=6, tilt=-0.12, broken=(4,), noprop=(1, 2), body=SILKSCREEN_WHITE, props=(IC_GREY,))
    R(x - 8, y + 6, x + 8, y + 18, FR4_EDGE)                              # its parcel, still strapped on
    R(x - 8, y + 6, x + 8, y + 8, FR4_SHADE)
    R(x - 1, y + 6, x + 1, y + 18, COPPER)
    line([(x - 6, y + 2), (x - 6, y + 6)], IC_GREY)
    line([(x + 6, y + 2), (x + 6, y + 6)], IC_GREY)


poly([(296, 270), (312, 244), (348, 228), (396, 222), (446, 226), (480, 232), (480, 270)], IC_BLACK)  # the heap's mass
hrng = random.Random(61)
for i in range(46):                                                      # base layer: boards and packs
    x, y = hrng.uniform(306, 474), hrng.uniform(232, 266)
    if hrng.random() < 0.65:
        pcb(x, y, hrng.randrange(8, 18), hrng.randrange(4, 8), green=hrng.random() < 0.55, leds=False)
    else:
        R(x, y, x + 10, y + 6, hrng.choice([WIRE_YELLOW, WIRE_BLUE, LOGO_RED]))
        R(x, y, x + 10, y, SILKSCREEN_WHITE)
items = [(motherboard, 312, 244), (gpu, 384, 236), (psu, 430, 240), (hdd, 352, 258), (ram, 404, 258),
         (ram, 346, 238), (robot_head, 456, 226), (track, 364, 250), (servo, 420, 232), (servo, 440, 260),
         (robot_arm, 330, 236), (hdd, 466, 250)]
for fn, x, y in sorted(items, key=lambda t: t[2]):
    fn(x, y)
delivery_drone(404, 224)
drone(352, 228, 20, arms=4, tilt=0.3, broken=(0,), noprop=(2,), props=(WIRE_YELLOW,))          # wrecked FPV quads
drone(456, 246, 16, arms=4, tilt=-0.5, dangling=(1,), noprop=(0, 3), body=LOGO_RED, props=(GLOW_TEAL,))
for i in range(5):                                                       # cable tangles over the top
    xa = hrng.uniform(306, 470)
    line(sag(xa, 246 - hrng.randrange(0, 14), xa + hrng.randrange(-30, 30), 258 - hrng.randrange(0, 12),
             -hrng.randrange(4, 10), 10), hrng.choice([IC_DARK, IC_GREY, LOGO_RED, WIRE_BLUE]))
R(446, 248, 480, 270, IC_DARK)                                           # scrap bin
R(446, 248, 480, 250, IC_GREY)
text("SCRAP", 454, 258, WIRE_YELLOW)

out = Path(__file__).resolve().parent / "out"
out.mkdir(exist_ok=True)
im.save(out / "line-v1-1x.png")
im.resize((W * S, H * S), Image.NEAREST).save(out / "line-v1.png")
print("wrote", out)
