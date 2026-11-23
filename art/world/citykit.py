"""citykit: draw a board city flat, then view it in perspective.

A scene script makes a City, draws its boards and parts in plan (top-down,
in world pixels), and calls render(). The kit works in two passes:

  1. Plan: boards, copper, silkscreen, pads and the top face of every part go
     into a flat image; every part also registers a 3D object.
  2. View: a perspective camera looks down from the south. The plan is projected
     onto the board plane, parts are extruded into blocks, wires hang in 3D, the
     boards are slabs with FR4 edges, and the carbon frame is the floor below.

Flat shapes, no outlines, light from the north-west. Every shadow is the next
darker palette colour (SHADE), so the result only uses brand palette colours.
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
C = {k.upper().replace(" ", "_"): v for k, v in P.items()}   # C["ENIG_GOLD"] etc.
globals().update(C)

BM, BM_D, TR, TR_HI = BLACK_MASK, BLACK_MASK_DEEP, BLACK_TRACE, BLACK_TRACE_HIGHLIGHT

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
WIRE_SHINE = {IC_DARK: IC_GREY, LOGO_RED: SIGNAL_PINK}       # a thin lit line along some wires
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


def spline(ctrl, per=12):
    """Smooth 3D path through control points (Catmull-Rom), for tidy wires."""
    pts = [ctrl[0]] + list(ctrl) + [ctrl[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = (np.array(q, float) for q in pts[i - 1:i + 3])
        for k in range(per):
            t = k / per
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                                    + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(ctrl[-1]))
    return out


def rounded_outline(x, y, w, h, r, n=6, notches=()):
    """Rounded rectangle outline (clockwise). notches: (edge, pos, radius) semicircle bites,
    edge in 'nsew', pos measured along the edge from the board's top-left."""
    pts = []
    corners = [(x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)]
    edges = {"e": [], "s": [], "w": [], "n": []}
    for e, pos, rad in notches:
        edges[e].append((pos, rad))

    def bite(cx, cy, rad, a0, a1):
        return [(cx + rad * math.cos(math.radians(a)), cy + rad * math.sin(math.radians(a)))
                for a in np.linspace(a0, a1, 7)]
    for i, (cx, cy, a0) in enumerate(corners):
        for k in range(n + 1):
            t = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
        if i == 0:      # east edge, going down
            for pos, rad in sorted(edges["e"]):
                pts += bite(x + w, y + pos, rad, -90, -270)
        elif i == 1:    # south edge, going left
            for pos, rad in sorted(edges["s"], reverse=True):
                pts += bite(x + pos, y + h, rad, 0, -180)
        elif i == 2:    # west edge, going up
            for pos, rad in sorted(edges["w"], reverse=True):
                pts += bite(x, y + pos, rad, 90, -90)
        else:           # north edge, going right
            for pos, rad in sorted(edges["n"]):
                pts += bite(x + pos, y, rad, 180, 0)
    return pts


class City:
    def __init__(self, w, h, seed=7, height_scale=2.2, floor=-150):
        self.W, self.H = w, h
        self.HS = height_scale
        self.FLOOR = floor
        self.rng = random.Random(seed)
        self.a = np.zeros((h, w, 3), np.uint8)
        self.a[:] = VOID
        self.objs = []
        self.holes = []
        self.boards = []       # (outline, thickness)
        self.board_area = np.zeros((h, w), bool)
        self.traces = []

    # ---------------------------------------------------------------- plan drawing
    def mask(self, fn):
        m = Image.new("L", (self.W, self.H), 0)
        fn(ImageDraw.Draw(m))
        return np.array(m) > 0

    def fill(self, m, c):
        self.a[m] = c

    def shade(self, m, steps=1):
        shade_arr(self.a, m, steps)

    def shift(self, m, dx, dy):
        H, W = self.H, self.W
        out = np.zeros_like(m)
        ys, xs = slice(max(dy, 0), H + min(dy, 0)), slice(max(dx, 0), W + min(dx, 0))
        ys0, xs0 = slice(max(-dy, 0), H + min(-dy, 0)), slice(max(-dx, 0), W + min(-dx, 0))
        out[ys, xs] = m[ys0, xs0]
        return out

    def rect(self, x, y, w, h, c):
        x0, y0 = max(int(x), 0), max(int(y), 0)
        x1, y1 = min(int(x + w), self.W), min(int(y + h), self.H)
        if x1 > x0 and y1 > y0:
            self.a[y0:y1, x0:x1] = c

    def disc_m(self, cx, cy, r, ry=None):
        ry = r if ry is None else ry
        return self.mask(lambda d: d.ellipse([cx - r, cy - ry, cx + r, cy + ry], fill=255))

    def poly_m(self, pts):
        return self.mask(lambda d: d.polygon([tuple(p) for p in pts], fill=255))

    def line_m(self, pts, w):
        def f(d):
            d.line([tuple(p) for p in pts], fill=255, width=w, joint="curve")
            r = w / 2 - 0.5
            for x, y in (pts[0], pts[-1]):
                d.ellipse([x - r, y - r, x + r, y + r], fill=255)
        return self.mask(f)

    def put(self, x, y, c):
        if 0 <= x < self.W and 0 <= y < self.H:
            self.a[y, x] = c

    def text(self, s, x, y, c, scale=2):
        for dx, dy in text_pixels(s, scale):
            self.put(int(x + dx), int(y + dy), c)

    def text_c(self, s, cx, y, c, scale=2):
        self.text(s, cx - text_width(s, scale) // 2, y, c, scale)

    def blob_pts(self, cx, cy, r, n=11, jitter=0.45, ry=None):
        ry = r if ry is None else ry
        pts = []
        for i in range(n):
            t = 2 * math.pi * i / n + self.rng.uniform(-0.2, 0.2)
            k = 1 - jitter / 2 + self.rng.random() * jitter
            pts.append((cx + math.cos(t) * r * k, cy + math.sin(t) * ry * k))
        return pts

    def glow(self, cx, cy, r, c):
        """A soft light pool: two flat rings of the colour's shades."""
        self.fill(self.disc_m(cx, cy, r, r * 0.75), SHADE[SHADE[c]])
        self.fill(self.disc_m(cx, cy, r * 0.58, r * 0.45), SHADE[c])

    # ---------------------------------------------------------------- boards and copper
    def board(self, outline, thickness):
        m = self.poly_m(outline)
        self.fill(m, BM)
        self.board_area |= m
        self.boards.append((outline, thickness))

    def trace(self, pts, w=8):
        p = chamfer(pts, c=max(8, w))
        self.traces.append((p, w))
        return p

    def copper(self, pour_regions=(), via_grid=28, clearance=13):
        cu = np.zeros((self.H, self.W), bool)
        for p, w in self.traces:
            cu |= self.line_m(p, w)
        pour = np.zeros_like(cu)
        for r in pour_regions:
            pour |= self.poly_m(r)
        keep = np.array(Image.fromarray((cu * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(clearance))) > 0
        pour &= ~keep & self.board_area
        self.fill(pour, TR)
        self.fill(pour & ~self.shift(pour, 0, -3), BM_D)
        self.fill(cu, TR_HI)
        self.fill(cu & ~self.shift(cu, 0, -3), TR)
        if via_grid:
            for y in range(0, self.H, via_grid):
                for x in range((y // via_grid % 2) * (via_grid // 2), self.W, via_grid):
                    ok = all(pour[min(max(y + dy, 0), self.H - 1), min(max(x + dx, 0), self.W - 1)]
                             for dx, dy in ((0, 0), (0, -6), (0, 6), (-6, 0), (6, 0)))
                    if ok:
                        self.fill(self.disc_m(x, y, 4), TR_HI)
                        self.fill(self.disc_m(x + 1, y + 1, 2), BM_D)
        return cu

    def packets(self, trace_ids, color=SIGNAL_PINK, every=70, length=10):
        for i in trace_ids:
            p, w = self.traces[i]
            pts = path_points(p)
            for start in range(self.rng.randrange(8, 30), len(pts) - length - 2, every):
                for (x, y) in pts[start:start + length]:
                    self.put(int(x), int(y), color)
                    self.put(int(x), int(y) - 1, color)

    def via(self, x, y, r=7):
        self.fill(self.disc_m(x, y, r), ENIG_GOLD)
        self.fill(self.disc_m(x + 1, y + 1, r - 1) & ~self.disc_m(x - 1, y - 1, r - 1), COPPER)
        self.fill(self.disc_m(x, y, r - 3), VOID_DEEP)

    # ---------------------------------------------------------------- parts
    def box(self, x, y, w, d, height, top, side, hi=None, hi_h=2, z0=0.0, flat=False, windows=None):
        if not flat:
            self.rect(x, y, w, d, top)
            if hi:
                self.rect(x, y, w, hi_h, hi)
        self.objs.append(dict(kind="box", x=x, y=y, w=w, d=d, z0=z0, h=height * self.HS, top=top, side=side,
                              flat=flat, windows=windows or []))
        return z0 + height * self.HS

    def wire(self, pts, w, c):
        self.objs.append(dict(kind="wire", pts=pts, w=w, c=c))

    def hcyl(self, cx, y0, y1, r, stripe=True):
        self.objs.append(dict(kind="hcyl", cx=cx, y0=y0, y1=y1, r=r, stripe=stripe))

    def legs(self, xs, y, dy, n, wid=5):
        for x in xs:
            self.rect(x - wid // 2, y if dy > 0 else y - n, wid, n, SILKSCREEN_SHADE)
            self.rect(x - wid // 2, y + n - 4 if dy > 0 else y - n, wid, 4, ENIG_GOLD)

    def legs_h(self, x, ys, dx, n, wid=5):
        for y in ys:
            self.rect(x if dx > 0 else x - n, y - wid // 2, n, wid, SILKSCREEN_SHADE)
            self.rect(x + n - 4 if dx > 0 else x - n, y - wid // 2, 4, wid, ENIG_GOLD)

    def qfp(self, x, y, s, n, height, label=(), pitch=None, leg=16, top=IC_DARK, side=IC_BLACK):
        pitch = pitch or (s - 24) / (n - 1)
        offs = [12 + pitch * i for i in range(n)]
        self.legs([x + o for o in offs], y - leg, -1, leg)
        self.legs([x + o for o in offs], y + s, 1, leg)
        self.legs_h(x - leg, [y + o for o in offs], -1, leg)
        self.legs_h(x + s, [y + o for o in offs], 1, leg)
        z = self.box(x, y, s, s, height, top, side, hi=IC_GREY, hi_h=3)
        self.fill(self.disc_m(x + 12, y + 12, 5), IC_BLACK)
        for i, (t, sc) in enumerate(label):
            self.text_c(t, x + s / 2, y + s / 2 - 12 + i * 18, IC_GREY, sc)
        return z

    def qfn(self, x, y, w, d, height, label="", top=IC_DARK, n=4):
        for k in range(n):
            f = (k + 1) / (n + 1)
            self.rect(x - 5, y + d * f - 2, 5, 4, ENIG_GOLD)
            self.rect(x + w, y + d * f - 2, 5, 4, ENIG_GOLD)
            self.rect(x + w * f - 2, y - 5, 4, 5, ENIG_GOLD)
            self.rect(x + w * f - 2, y + d, 4, 5, ENIG_GOLD)
        z = self.box(x, y, w, d, height, top, SHADE[top], hi=IC_GREY if top == IC_DARK else None)
        self.fill(self.disc_m(x + 6, y + 6, 2), IC_GREY)
        if label:
            self.text_c(label, x + w / 2, y + d / 2 - 5, IC_GREY, 2)
        return z

    def chip(self, x, y, w=24, d=12, body=COPPER_SHADOW, height=4):
        """A small passive (0603/0402): metal ends, body in the middle."""
        vertical = d > w
        self.box(x, y, w, d, height, body, SHADE[body])
        e = max(4, (d if vertical else w) // 4)
        if vertical:
            self.rect(x, y, w, e, SILKSCREEN_SHADE)
            self.rect(x, y + d - e, w, e, SILKSCREEN_SHADE)
        else:
            self.rect(x, y, e, d, SILKSCREEN_SHADE)
            self.rect(x + w - e, y, e, d, SILKSCREEN_SHADE)
        self.rect(x, y, w, 2, SILKSCREEN_WHITE)

    def solder(self, x, y, r=6):
        """A clean, shiny joint (no flux)."""
        self.fill(self.disc_m(x, y, r), SILKSCREEN_SHADE)
        self.fill(self.disc_m(x - r * 0.25, y - r * 0.3, r * 0.6), SILKSCREEN_WHITE)

    def pad(self, x, y, w, d):
        self.rect(x, y, w, d, ENIG_GOLD)
        self.rect(x, y, w, 3, GOLD_HIGHLIGHT)
        self.rect(x, y + d - 2, w, 2, COPPER)

    def hole(self, cx, cy, r_hole, r_ring, r_grom=None, thickness=20):
        if r_grom:
            self.fill(self.disc_m(cx, cy, r_grom), IC_GREY)
            self.fill(self.disc_m(cx, cy, r_grom) & ~self.disc_m(cx + 4, cy + 4, r_grom), SILKSCREEN_SHADE)
            self.fill(self.disc_m(cx, cy + 4, r_ring), IC_DARK)
        self.fill(self.disc_m(cx, cy, r_ring), ENIG_GOLD)
        self.fill(self.disc_m(cx, cy, r_ring) & ~self.disc_m(cx - 3, cy - 3, r_ring), COPPER)
        self.holes.append((cx, cy, r_hole, thickness))

    def led(self, x, y, light, body, glow=34):
        self.glow(x + 9, y + 5, glow, light)
        self.box(x, y, 18, 10, 4, body, SHADE[body])
        self.rect(x, y, 5, 10, SILKSCREEN_SHADE)
        self.rect(x + 13, y, 5, 10, SILKSCREEN_SHADE)
        self.rect(x + 6, y + 3, 6, 4, SILKSCREEN_WHITE)

    def silk_box(self, x, y, w, h, c=SILKSCREEN_WHITE):
        self.rect(x, y, w, 2, c)
        self.rect(x, y + h - 2, w, 2, c)
        self.rect(x, y, 2, h, c)
        self.rect(x + w - 2, y, 2, h, c)

    def jst(self, x, y, w, d, pins, axis="v", height=10):
        """JST-SH style receptacle, cream plastic, pins along the long side."""
        z = self.box(x, y, w, d, height, SILKSCREEN_WHITE, SILKSCREEN_SHADE)
        for i in range(pins):
            if axis == "v":
                py = y + 12 + (d - 24) * i / max(pins - 1, 1)
                self.rect(x + w / 2 - 4, py - 3, 8, 6, IC_DARK)
            else:
                px = x + 12 + (w - 24) * i / max(pins - 1, 1)
                self.rect(px - 3, y + d / 2 - 4, 6, 8, IC_DARK)
        return z

    def logo(self, x, y, scale=2, color=SILKSCREEN_WHITE):
        grid = (ROOT / "brand" / "tools" / "make_logo.py").read_text().split('GRID = """')[1].split('"""')[0]
        for yy, row in enumerate(grid.strip("\n").splitlines()):
            for xx, ch in enumerate(row):
                if ch in "#r":
                    self.rect(x + xx * scale, y + yy * scale, scale, scale, color if ch == "#" else LOGO_RED)

    # ================================================================ pass 2: the view
    def render(self, out_size=(1600, 900), target=None, pitch=52, dist=1500.0, focal=1500.0, screen_cy=0.5,
               light=(0.55, 0.8), fog=True, plan_scale=2):
        W, H = self.W, self.H
        OW, OH = out_size
        TH = math.radians(pitch)
        tgt = np.array(target if target is not None else (W / 2, H / 2 + 40, 0.0), float)
        cam = tgt + dist * np.array([0.0, math.cos(TH), math.sin(TH)])
        RV, UV = np.array([1.0, 0, 0]), np.array([0.0, -math.sin(TH), math.cos(TH)])
        FV = np.array([0.0, -math.cos(TH), -math.sin(TH)])
        SCX, SCY = OW / 2, OH * screen_cy
        FLOOR = self.FLOOR

        def proj(x, y, z):
            d = np.array([x, y, z], float) - cam
            zc = d @ FV
            return (SCX + focal * (d @ RV) / zc, SCY - focal * (d @ UV) / zc)

        def depth(x, y, z):
            return (np.array([x, y, z], float) - cam) @ FV

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
            x0, y0, x1, y1 = region
            corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            sp = [proj(x, y, z) for x, y in corners]
            tp = [((x + offset[0]) * scale, (y + offset[1]) * scale) for x, y in corners]
            hm = homography(sp, tp)
            bx0, by0, bx1, by1 = bbox or (0, 0, OW, OH)
            hm = hm @ np.array([[1, 0, bx0], [0, 1, by0], [0, 0, 1]], float)
            hm /= hm[2, 2]
            return img.transform((bx1 - bx0, by1 - by0), Image.PERSPECTIVE, tuple(hm.flatten()[:8]), Image.NEAREST)

        # --- floor: carbon weave far below, with depth fog
        off, fw, fh = (1100, 1300), W + 2200, H + 2600
        yy_, xx_ = np.mgrid[0:fh, 0:fw]
        horiz = ((xx_ // 24) + (yy_ // 24)) % 2 == 0
        stripe = np.where(horiz, (yy_ // 4) % 2, (xx_ // 4) % 2) == 0
        flo = np.zeros((fh, fw, 3), np.uint8)
        flo[:] = VOID
        flo[stripe] = VOID_MID
        scr.paste(warp(Image.fromarray(flo), 1, off, (-off[0], -off[1], fw - off[0], fh - off[1]), FLOOR))
        if fog:
            m = np.zeros((OH, OW), bool)
            m[: int(OH * 0.24)] = True
            shade_screen(m)
            m[int(OH * 0.11):] = False
            shade_screen(m)

        # --- shadows on the floor
        polys = [[proj(x + light[0] * -FLOOR, y + light[1] * -FLOOR, FLOOR) for x, y in o] for o, t in self.boards]
        lines = []
        for o in self.objs:
            if o["kind"] == "wire":
                sp = [proj(x + light[0] * (z - FLOOR), y + light[1] * (z - FLOOR), FLOOR) for x, y, z in o["pts"]]
                lines.append((sp, o["w"] * focal / depth(*o["pts"][0][:2], FLOOR)))
        shade_screen(screen_mask(polys), 2)
        shade_screen(screen_mask((), lines), 1)

        # --- wires: runs behind the boards first
        bboxes = [(min(p[0] for p in o), min(p[1] for p in o), max(p[0] for p in o), max(p[1] for p in o))
                  for o, t in self.boards]

        def behind(p0, p1):
            if max(p0[2], p1[2]) > -2:
                return False
            ymax, xmin, xmax = max(p0[1], p1[1]), min(p0[0], p1[0]), max(p0[0], p1[0])
            for bx0, by0, bx1, by1 in bboxes:
                if ymax < by0 + 8 and xmax > bx0 - 60 and xmin < bx1 + 60:
                    return True        # hanging north of a board
                if max(p0[2], p1[2]) > -40:
                    continue           # a shallow sag (a bridge) stays in front
                if xmin > bx1 - 8 and by0 - 40 < ymax < by1 + 40 and cam[0] < bx1:
                    return True        # hanging east of a board, camera to the west
                if xmax < bx0 + 8 and by0 - 40 < ymax < by1 + 40 and cam[0] > bx0:
                    return True        # hanging west of a board, camera to the east
            return False

        def draw_run(pts, w, c):
            sp = [proj(*p) for p in pts]
            wp = w * focal / depth(*pts[len(pts) // 2])
            strokes = [(wp * 0.18, wp, SHADE.get(c, c)), (-wp * 0.12, wp * 0.68, c)]
            if c in WIRE_SHINE and wp >= 6:
                strokes.append((-wp * 0.28, max(1, wp * 0.16), WIRE_SHINE[c]))
            for dy, ww, cc in strokes:
                q = [(x, y + dy) for x, y in sp]
                dr.line(q, fill=cc, width=max(1, round(ww)), joint="curve")
                r = ww / 2
                for (x, y) in (q[0], q[-1]):
                    dr.ellipse([x - r, y - r, x + r, y + r], fill=cc)

        runs = []
        for o in self.objs:
            if o["kind"] != "wire":
                continue
            cur, state = [o["pts"][0]], None
            for p0, p1 in zip(o["pts"], o["pts"][1:]):
                b = behind(p0, p1)
                if state is not None and b != state:
                    runs.append((cur, o["w"], o["c"], state))
                    cur = [p0]
                cur.append(p1)
                state = b
            runs.append((cur, o["w"], o["c"], bool(state)))
        for r in sorted([r for r in runs if r[3]], key=lambda r: -depth(*r[0][0])):
            draw_run(*r[:3])

        # --- board slabs, then the plan on top
        for outline, t in self.boards:
            cxm = sum(p[0] for p in outline) / len(outline)
            cym = sum(p[1] for p in outline) / len(outline)
            faces = []
            for (x0, y0), (x1, y1) in zip(outline, outline[1:] + outline[:1]):
                mx, my = (x0 + x1) / 2, (y0 + y1) / 2
                nx, ny = (y1 - y0), -(x1 - x0)
                if nx * (mx - cxm) + ny * (my - cym) < 0:
                    nx, ny = -nx, -ny
                if nx * (cam[0] - mx) + ny * (cam[1] - my) <= 0:
                    continue
                faces.append((depth(mx, my, 0), x0, y0, x1, y1, abs(nx) > abs(ny) * 1.5))
            for _, x0, y0, x1, y1, side in sorted(faces, reverse=True):
                for za, zb, c in [(0, -2, BM), (-2, -t + 5, FR4_EDGE), (-t + 5, -t, FR4_SHADE),
                                  (-7, -9, COPPER), (-t + 9, -t + 11, COPPER)]:
                    poly([proj(x0, y0, za), proj(x1, y1, za), proj(x1, y1, zb), proj(x0, y0, zb)],
                         SHADE.get(c, c) if side else c)
        alpha = self.board_area.copy()
        for cx, cy, r, t in self.holes:
            alpha &= ~self.disc_m(cx, cy, r)
        plan = self.a.copy()
        TS = plan_scale
        plan_rgba = Image.fromarray(np.dstack([plan, (alpha * 255).astype(np.uint8)]), "RGBA").resize(
            (W * TS, H * TS), Image.NEAREST)
        plan_rgb = Image.fromarray(plan).resize((W * TS, H * TS), Image.NEAREST)
        bimg = warp(plan_rgba, TS, (0, 0), (0, 0, W, H), 0)
        scr.paste(bimg, (0, 0), bimg)
        board_screen = np.array(bimg)[..., 3] > 0
        for cx, cy, r, t in self.holes:     # plated barrels seen through the holes
            n = 20
            for k in range(n):
                ta, tb = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
                tm = (ta + tb) / 2
                px, py = cx + r * math.cos(tm), cy + r * math.sin(tm)
                if -math.cos(tm) * (cam[0] - px) - math.sin(tm) * (cam[1] - py) > 0:
                    q0 = (cx + r * math.cos(ta), cy + r * math.sin(ta))
                    q1 = (cx + r * math.cos(tb), cy + r * math.sin(tb))
                    poly([proj(*q0, 0), proj(*q1, 0), proj(*q1, -t), proj(*q0, -t)],
                         COPPER_SHADOW if math.sin(tm) < 0.3 else IC_BLACK)

        # --- parts
        def footprint_shadow(o):
            x, y, w, d, z0, h = o["x"], o["y"], o["w"], o["d"], o["z0"], o["h"]
            ox, oy = light[0] * h, light[1] * h
            pts = [(x, y), (x + w, y), (x + w + ox, y + oy), (x + w + ox, y + d + oy), (x + ox, y + d + oy), (x, y + d)]
            return [proj(px, py, z0) for px, py in pts]

        def draw_box(o):
            x, y, w, d, z0, h = o["x"], o["y"], o["w"], o["d"], o["z0"], o["h"]
            z1 = z0 + h
            top, side = o["top"], o["side"]
            if cam[0] < x:
                poly([proj(x, y, z0), proj(x, y + d, z0), proj(x, y + d, z1), proj(x, y, z1)], SHADE.get(top, side))
            if cam[0] > x + w:
                poly([proj(x + w, y, z0), proj(x + w, y + d, z0), proj(x + w, y + d, z1), proj(x + w, y, z1)],
                     SHADE.get(side, side))
            poly([proj(x, y + d, z0), proj(x + w, y + d, z0), proj(x + w, y + d, z1), proj(x, y + d, z1)], side)
            for xo, ww, c in o["windows"]:
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
            img = warp(plan_rgb, TS, (0, 0), (x, y, x + w, y + d), z1, bbox=(bx0, by0, bx1, by1))
            m = Image.new("L", img.size, 0)
            ImageDraw.Draw(m).polygon([(round(px - bx0), round(py - by0)) for px, py in quad], fill=255)
            scr.paste(img, (bx0, by0), m)

        def draw_hcyl(o):
            cx, y0, y1, r = o["cx"], o["y0"], o["y1"], o["r"]
            ladder = [SMOKE_VIOLET, GRAFFITI_PURPLE, DUSK_PURPLE, IC_DARK]
            n = 14
            for k in range(n):
                ta, tb = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
                tm = (ta + tb) / 2
                nx, nz = math.cos(tm), math.sin(tm)
                if nx * (cam[0] - (cx + r * nx)) + nz * (cam[2] - (r + r * nz)) <= 0:
                    continue
                lit = -0.6 * nx + 0.8 * nz
                c = ladder[0 if lit > 0.75 else 1 if lit > 0.2 else 2 if lit > -0.4 else 3]
                if o["stripe"] and k == 3:
                    c = SILKSCREEN_WHITE
                pa = (cx + r * math.cos(ta), r + r * math.sin(ta))
                pb = (cx + r * math.cos(tb), r + r * math.sin(tb))
                poly([proj(pa[0], y0, pa[1]), proj(pb[0], y0, pb[1]), proj(pb[0], y1, pb[1]), proj(pa[0], y1, pa[1])], c)
            poly([proj(cx + r * math.cos(2 * math.pi * k / 20), y1, r + r * math.sin(2 * math.pi * k / 20))
                  for k in range(20)], SILKSCREEN_SHADE)
            poly([proj(cx + r * 0.8 * math.cos(2 * math.pi * k / 20) - 2, y1, r + r * 0.8 * math.sin(2 * math.pi * k / 20) + 2)
                  for k in range(20)], SILKSCREEN_WHITE)
            for ax, az, bx, bz in [(-r * 0.6, 0, r * 0.6, 0), (0, -r * 0.6, 0, r * 0.6)]:
                dr.line([proj(cx + ax, y1, r + az), proj(cx + bx, y1, r + bz)], fill=IC_GREY, width=2)

        ground = [o for o in self.objs if o["kind"] == "box" and o["z0"] <= 4]
        raised = [o for o in self.objs if o["kind"] == "box" and o["z0"] > 4]
        cyl_sh = [[proj(o["cx"] - o["r"], o["y0"], 0), proj(o["cx"] + o["r"] + light[0] * 60, o["y0"] + 30, 0),
                   proj(o["cx"] + o["r"] + light[0] * 60, o["y1"] + 40, 0), proj(o["cx"] - o["r"], o["y1"], 0)]
                  for o in self.objs if o["kind"] == "hcyl"]
        shade_screen(screen_mask([footprint_shadow(o) for o in ground] + cyl_sh) & board_screen)
        items = [(o["y"] + o["d"], 0, lambda o=o: draw_box(o)) for o in ground]
        items += [(o["y1"], 0, lambda o=o: draw_hcyl(o)) for o in self.objs if o["kind"] == "hcyl"]
        items += [(max(p[1] for p in r[0]), 1, lambda r=r: draw_run(*r[:3])) for r in runs if not r[3]]
        for _, _, fn in sorted(items, key=lambda t: (t[0], t[1])):
            fn()
        if raised:
            shade_screen(screen_mask([footprint_shadow(o) for o in raised if not o["flat"] or o["w"] > 10]))
            for o in sorted(raised, key=lambda o: o["y"] + o["d"]):
                draw_box(o)
        self.screen = scr
        return scr

    def plan_image(self):
        alpha = self.board_area.copy()
        for cx, cy, r, t in self.holes:
            alpha &= ~self.disc_m(cx, cy, r)
        pl = np.zeros_like(self.a)
        pl[:] = VOID
        pl[alpha] = self.a[alpha]
        return Image.fromarray(pl)
