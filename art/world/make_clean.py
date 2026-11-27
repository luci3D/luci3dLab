#!/usr/bin/env python3
"""The Clean Stack: a 4-in-1 ESC, a flight controller and our (future) all-in-one DVR,
in mint condition. The website's first impression.

Left to right: ESC  ==8-wire bridge==  FC  ==3-wire bridge==  DVR.
The FC and ESC are generic, laid out after the TBS Lucid F4 FC and 4in1 ESC drawings
(no TBS branding). Everything works: LEDs lit, data running, wires bundled tidy.
Black boards, white silkscreen. Scale: about 12 px per mm.

    python3 art/world/make_clean.py
      -> art/world/out/clean-v1.png        perspective view
      -> art/world/out/clean-v1-plan.png   flat plan
"""
import math
from pathlib import Path

from PIL import Image

from citykit import City, rounded_outline, spline, C, SHADE

g = globals()
g.update(C)
BLACKW = IC_DARK                         # "black" wire insulation (reads on the dark floor)

YC = 330                                 # centre line through the three boards
EX, EY, EW, EH = 40, YC - 204, 528, 408  # ESC (44 x 34 mm)
FX, FY, FW, FH = EX + EW + 180, YC - 174, 372, 348   # FC (31 x 29 mm)
DX, DY, DS = FX + FW + 180, YC - 162, 324            # DVR (27 x 27 mm, 20 x 20 mounting)
W, H = DX + DS + 40, 680

city = City(W, H, seed=11, floor=-120)
c = city


def E(x, y):
    return EX + x, EY + y


def F(x, y):
    return FX + x, FY + y


def D(x, y):
    return DX + x, DY + y


# ================================================================= boards
c.board(rounded_outline(EX, EY, EW, EH, 22), 24)
c.board(rounded_outline(FX, FY, FW, FH, 40, notches=[("n", 102, 12), ("n", 270, 12), ("s", 102, 12), ("s", 270, 12),
                                                    ("w", 100, 12), ("w", 248, 12), ("e", 100, 12), ("e", 248, 12)]), 20)
c.board(rounded_outline(DX, DY, DS, DS, 34), 18)

# ================================================================= copper
# --- ESC: motor pads top/bottom, FC connector on the east side, battery on the west
PADX = [99, 165, 231, 297, 363, 429]
ECON_Y = [162 + 12 * k for k in range(8)]           # local y of the 8 connector pins (east side)
DRV = (232, 172)                                     # ESC MCU (local), 64 x 64
for k in range(6):
    c.trace([E(PADX[k], 40), E(PADX[k], 52)], 30)    # pad -> MOSFET drain, wide
    c.trace([E(PADX[k], 368), E(PADX[k], 356)], 30)
for k, y in enumerate(ECON_Y[2:6]):                  # motor signals into the MCU
    c.trace([E(440, y), E(330 + 6 * k, y), E(330 + 6 * k, DRV[1] + 14 + 12 * k), E(DRV[0] + 64, DRV[1] + 14 + 12 * k)], 8)
c.trace([E(440, ECON_Y[6]), E(380, ECON_Y[6]), E(380, 270), E(176, 270), E(176, 250)], 8)     # current sensor
c.trace([E(440, ECON_Y[7]), E(396, ECON_Y[7]), E(396, 284), E(120, 284)], 8)                  # telemetry
c.trace([E(440, ECON_Y[0]), E(410, ECON_Y[0]), E(410, 126), E(120, 126), E(120, 150)], 16)    # VBAT out
for k in range(6):                                   # gate drive, MCU -> MOSFET rows
    x = PADX[k]
    c.trace([E(DRV[0] + 8 + 9 * k, DRV[1]), E(DRV[0] + 8 + 9 * k, 140), E(x, 140), E(x, 108)], 5)

# --- FC
MCU = (130, 130, 112)                                # local x, y, size (LQFP-64)
mx, my, ms = MCU
FCON_Y = [132 + 12 * k for k in range(8)]            # ESC connector pins (west side)
pin = [12 + (ms - 24) * i / 15 for i in range(16)]
for k in range(8):                                   # ESC port -> MCU west pins
    y0 = FCON_Y[k]
    yt = my + pin[4 + k]
    c.trace([F(64, y0), F(84 + 3 * k, y0), F(84 + 3 * k, yt), F(mx - 16, yt)], 6 if k else 12)
for i in range(6):                                   # MCU east -> HD port
    c.trace([F(mx + ms + 16, my + pin[2 + i]), F(292, my + pin[2 + i]), F(292, 110 + 12 * i), F(308, 110 + 12 * i)], 6)
for i in range(2):                                   # USB D+/D- (a pair)
    c.trace([F(180 + 10 * i, 70), F(180 + 10 * i, my - 16)], 5)
for i in range(3):                                   # MCU -> IMU
    c.trace([F(mx + pin[11 + i], my - 16), F(mx + pin[11 + i], 100 + 6 * i), F(262, 100 + 6 * i)], 5)
for i, (px, py) in enumerate([(344, 200), (344, 222), (344, 244)]):   # DVR tap pads
    c.trace([F(px, py), F(296 - 8 * i, py), F(296 - 8 * i, my + pin[10 + i]), F(mx + ms + 16, my + pin[10 + i])], 6)
c.trace([F(64, FCON_Y[0]), F(76, FCON_Y[0]), F(76, 300), F(120, 300)], 12)        # VBAT to the regulators
for i in range(4):                                   # receiver pads
    c.trace([F(150 + 22 * i, 330), F(150 + 22 * i, 312), F(mx + pin[4 + i * 2], 312), F(mx + pin[4 + i * 2], my + ms + 16)], 5)

# --- DVR
RV = (116, 112, 92)                                  # RV1103
TP = (56, 124, 50)                                   # TP9950
J2_Y = [194, 206, 218]                               # J2 pins (west side)
c.trace([D(48, J2_Y[0]), D(64, J2_Y[0]), D(64, TP[1] + TP[2] + 6)], 8)            # video in -> decoder
c.trace([D(48, J2_Y[1]), D(76, J2_Y[1]), D(76, 236), D(84, 236)], 14)            # 5 V -> buck
for i in range(6):                                   # MIPI: decoder -> RV1103 (3 pairs)
    y = TP[1] + 8 + 7 * i
    c.trace([D(TP[0] + TP[2], y), D(RV[0], y)], 4)
for i in range(6):                                   # RV1103 -> SD card
    y = RV[1] + 14 + 12 * i
    c.trace([D(RV[0] + RV[2], y), D(222, y)], 5)
for i in range(4):                                   # RV1103 -> NAND
    x = RV[0] + 14 + 14 * i
    c.trace([D(x, RV[1] + RV[2]), D(x, 214)], 5)
c.trace([D(RV[0] + RV[2] - 10, RV[1] + RV[2]), D(RV[0] + RV[2] - 10, 216), D(212, 216), D(212, 222)], 5)   # IMU
c.trace([D(140, 270), D(104, 270), D(104, 220), D(RV[0] + 6, 220), D(RV[0] + 6, RV[1] + RV[2])], 5)        # mic

cu = c.copper(pour_regions=[
    [E(60, 56), E(500, 56), E(500, 352), E(60, 352)],
    [F(14, 20), F(358, 20), F(358, 328), F(14, 328)],
    [D(14, 14), D(310, 14), D(310, 310), D(14, 310)],
])
c.packets(range(4, 10), SIGNAL_PINK, every=60)                     # ESC commands
c.packets([i for i, (p, w) in enumerate(c.traces) if w == 6][:14], SIGNAL_PINK, every=55)
mipi = [i for i, (p, w) in enumerate(c.traces) if w == 4]
c.packets(mipi, GLOW_TEAL, every=24, length=8)                     # video flowing into the recorder
for v in [E(120, 150), E(176, 250), E(120, 284), F(120, 300), D(84, 236)]:
    c.via(*v)

# ================================================================= ESC parts
for (hx, hy) in [(30, 118), (30, 290), (498, 118), (498, 290)]:
    c.hole(*E(hx, hy), r_hole=12, r_ring=21, thickness=24)
for k, x in enumerate(PADX):
    c.pad(*E(x - 22, 4), 44, 36)
    c.pad(*E(x - 22, 368), 44, 36)
    c.rect(*E(x - 24, 52 - 8), 48, 8, ENIG_GOLD)                   # MOSFET tabs
    c.box(*E(x - 26, 52), 52, 50, 6, IC_DARK, IC_BLACK, hi=IC_GREY)
    c.rect(*E(x - 24, 356), 48, 8, ENIG_GOLD)
    c.box(*E(x - 26, 304), 52, 50, 6, IC_DARK, IC_BLACK, hi=IC_GREY)
for k in range(10):                                                # gate resistor rows
    c.chip(*E(110 + 30 * k, 112), 20, 10, IC_DARK if k % 2 else COPPER_SHADOW, 3)
    c.chip(*E(110 + 30 * k, 290), 20, 10, IC_DARK if k % 2 else COPPER_SHADOW, 3)
c.qfn(*E(*DRV), 64, 64, 5, "F421")
c.qfn(*E(318, 150), 30, 30, 4)
c.qfn(*E(318, 222), 30, 30, 4)
c.box(*E(70, 128), 56, 36, 6, IC_DARK, IC_BLACK, hi=IC_GREY)     # regulator
c.rect(*E(78, 164), 40, 8, ENIG_GOLD)
c.box(*E(140, 132), 30, 24, 7, COPPER_SHADOW, IC_BLACK)           # tantalum
c.rect(*E(140, 132), 30, 4, IC_GREY)
c.box(*E(226, 248), 26, 14, 4, IC_DARK, IC_BLACK)
c.box(*E(130, 248), 86, 28, 6, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)   # current shunt
for i in range(3):
    c.chip(*E(352 + 24 * i, 196), 12, 22, COPPER_SHADOW, 3)
c.jst(*E(440, 150), 48, 108, 8, "v", 10)                           # FC port
c.text_c("FC", *E(464, 128), SILKSCREEN_WHITE, 2)
# battery pads, capacitor, tidy leads (west)
for py, lab in [(150, "+"), (222, "-")]:
    c.pad(*E(2, py), 52, 46)
    c.solder(*E(28, py + 23), 14)
c.text("+", *E(60, 160), SILKSCREEN_WHITE, 3)
c.text("-", *E(60, 236), SILKSCREEN_WHITE, 3)
c.text_c("4IN1 ESC  3-6S", *E(330, 268), SILKSCREEN_WHITE, 2)
YB = EY + 209                                                      # the leads meet here
for py, col, off in [(173, LOGO_RED, -13), (245, BLACKW, 13)]:      # battery leads, side by side, off the board
    y0 = EY + py
    c.wire(spline([(EX + 28, y0, 8), (EX - 14, y0, 8), (EX - 50, YB + off, 7), (EX - 165, YB + off, 7),
                   (EX - 205, YB + off + 30, -50), (EX - 235, YB + off + 120, c.FLOOR + 12),
                   (EX - 265, H + 300, c.FLOOR + 12)]), 22, col)
CAP_R, CAP_Z = 26, 17                                               # the cap lies on top of the leads
c.radial_cap(EX - 150, EX - 30, YB, CAP_R, "e", [E(30, 173), E(30, 245)], z=CAP_Z, key_bias=100)
# motor wires: three per motor, gathered into a sleeved bundle that runs off toward its arm
for grp in range(2):
    for top in (True, False):
        s_ = -1 if top else 1
        edge = EY if top else EY + EH
        gx = EX + (PADX[3 * grp] + PADX[3 * grp + 2]) / 2
        dx = (-0.55 if grp == 0 else 0.55)                          # arms point to the corners
        for i in range(3):
            px, py = EX + PADX[3 * grp + i], (EY + 22) if top else (EY + 386)
            bx = gx + (i - 1) * 11
            ctrl = [(px, py, 6), (px, edge + s_ * 30, 4), (px, edge + s_ * 80, -40),
                    (px + (bx - px) * 0.7, edge + s_ * 150, c.FLOOR + 8), (bx, edge + s_ * 210, c.FLOOR + 6),
                    (bx + dx * 400, edge + s_ * 700, c.FLOOR + 6)]
            c.wire([(px, py, 6)] + spline(ctrl[1:]), 10, BLACKW)
            c.solder(px, py, 9)
        sleeve = spline([(gx, edge + s_ * 222 + 3, c.FLOOR + 9), (gx + dx * 120, edge + s_ * 360, c.FLOOR + 9),
                         (gx + dx * 404, edge + s_ * 705, c.FLOOR + 9)], 8)
        c.wire(sleeve, 40, IC_BLACK)

# ================================================================= FC parts
for (hx, hy) in [(66, 54), (306, 54), (66, 294), (306, 294)]:
    c.hole(*F(hx, hy), r_hole=18, r_ring=28, r_grom=38, thickness=20)
c.qfp(*F(mx, my), ms, 16, 8, label=[("AT32", 2), ("F435", 2)])
c.box(*F(132, -12), 108, 78, 8, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE, hi_h=3)    # USB-C
c.rect(*F(146, -12), 80, 6, IC_BLACK)
c.rect(*F(150, 8), 72, 4, SILKSCREEN_WHITE)
c.jst(*F(16, 114), 48, 120, 8, "v", 10)                           # ESC port
c.jst(*F(308, 96), 48, 90, 6, "v", 10)                            # HD port
c.box(*F(262, 92), 30, 34, 3, IC_DARK, IC_BLACK, hi=IC_GREY)      # IMU
c.fill(c.disc_m(*F(268, 98), 2), IC_GREY)
c.box(*F(266, 138), 26, 26, 4, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)   # baro
c.fill(c.disc_m(*F(284, 146), 2), IC_BLACK)
for x in (118, 210):                                               # 5 V and 9 V regulators
    c.box(*F(x, 262), 44, 44, 9, IC_GREY, IC_DARK, hi=SILKSCREEN_SHADE)
    c.text_c("2R2", *F(x + 22, 280), IC_DARK, 2)
c.box(*F(170, 266), 30, 20, 4, IC_DARK, IC_BLACK, hi=IC_GREY)
for i in range(4):                                                  # receiver pads
    c.fill(c.disc_m(*F(150 + 22 * i, 332), 7), ENIG_GOLD)
    c.fill(c.disc_m(*F(149 + 22 * i, 331), 3), GOLD_HIGHLIGHT)
c.box(*F(74, 238), 26, 18, 6, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)   # boot button
c.fill(c.disc_m(*F(87, 247), 5), IC_BLACK)
c.led(*F(224, 324), GLOW_TEAL, SIGNAL_TEAL, 18)                     # status LEDs
c.led(*F(248, 324), SIGNAL_PINK, GRAFFITI_PURPLE, 18)
for i in range(6):                                                  # decoupling caps around the MCU
    c.chip(*F(mx + 6 + 18 * i, my - 30), 12, 8, IC_DARK if i % 2 else COPPER_SHADOW, 3)
for i in range(4):
    c.chip(*F(96, my + 20 + 22 * i), 12, 8, COPPER_SHADOW, 3)
for i in range(3):
    c.chip(*F(254, my + 66 + 16 * i), 12, 8, IC_DARK, 3)
for i, (px, py) in enumerate([(344, 200), (344, 222), (344, 244)]):  # DVR tap pads
    c.fill(c.disc_m(*F(px, py), 8), ENIG_GOLD)
    c.text(["VID", "5V", "G"][i], *F(312 - [12, 4, 0][i], py - 5), SILKSCREEN_WHITE, 2)

# ================================================================= DVR parts (ours)
for (hx, hy) in [(42, 42), (282, 42), (42, 282), (282, 282)]:
    c.hole(*D(hx, hy), r_hole=18, r_ring=27, r_grom=36, thickness=18)
c.qfn(*D(RV[0], RV[1]), RV[2], RV[2], 6, "", n=6)
c.text_c("RV1103", *D(RV[0] + RV[2] / 2, RV[1] + 36), IC_GREY, 2)
c.qfn(*D(TP[0], TP[1]), TP[2], TP[2], 4, "", n=4)
c.text_c("9950", *D(TP[0] + TP[2] / 2, TP[1] + 20), IC_GREY, 2)
c.box(*D(120, 214), 64, 42, 4, IC_DARK, IC_BLACK, hi=IC_GREY)      # NAND
c.text_c("NAND", *D(152, 230), IC_GREY, 2)
c.box(*D(196, 222), 32, 28, 3, IC_DARK, IC_BLACK, hi=IC_GREY)      # IMU
c.fill(c.disc_m(*D(202, 228), 2), IC_GREY)
c.box(*D(120, 268), 40, 30, 5, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)   # MEMS mic
c.fill(c.disc_m(*D(148, 278), 3), IC_BLACK)
c.box(*D(84, 214), 34, 34, 8, IC_GREY, IC_DARK, hi=SILKSCREEN_SHADE)            # buck inductor
c.box(*D(306, 118), 34, 84, 2, IC_BLACK, VOID_DEEP, z0=4)           # micro SD card, out over the edge
c.rect(*D(310, 126), 26, 60, WIRE_BLUE)
c.box(*D(222, 100), 90, 112, 7, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE, hi_h=3)  # SD slot
for k in range(4):
    c.rect(*D(232, 120 + 22 * k), 70, 3, IC_GREY)
c.jst(*D(12, 176), 36, 60, 3, "v", 10)                              # J2: video, 5 V, GND
c.box(*D(90, 84), 24, 20, 5, SILKSCREEN_SHADE, IC_GREY, hi=SILKSCREEN_WHITE)    # button
c.fill(c.disc_m(*D(102, 94), 4), IC_BLACK)
c.led(*D(176, 262), LOGO_RED, BURN_RED, 24)                         # REC
c.text("REC", *D(200, 262), SILKSCREEN_WHITE, 2)

for i in range(4):
    c.chip(*D(124 + 18 * i, 94), 12, 8, IC_DARK if i % 2 else COPPER_SHADOW, 3)
c.logo(*D(84, 14), 1)
c.text("OPEN-DVR", *D(118, 18), SILKSCREEN_WHITE, 3)
c.text("LUCI3D  REV A", *D(118, 40), SILKSCREEN_WHITE, 2)

# ================================================================= the bridges
# FC <-> ESC: 8 wires, one red (VBAT), seven black
fc_plug = (FX - 18, FX + 16)
esc_plug = (EX + 488, EX + EW + 18)
c.box(fc_plug[0], FY + 110, fc_plug[1] - fc_plug[0], 128, 9, SILKSCREEN_WHITE, SILKSCREEN_SHADE,
      hi=SILKSCREEN_SHADE, z0=2)
c.box(esc_plug[0], EY + 146, esc_plug[1] - esc_plug[0], 128, 9, SILKSCREEN_WHITE, SILKSCREEN_SHADE,
      hi=SILKSCREEN_SHADE, z0=2)
zc = 12
for k in range(8):
    y = FY + FCON_Y[k]
    pts = [(esc_plug[1] + (fc_plug[0] - esc_plug[1]) * t / 16, y, zc - 28 * math.sin(math.pi * t / 16))
           for t in range(17)]
    c.wire(pts, 9, LOGO_RED if k == 0 else BLACKW)
    if k in (3, 5):
        seg = pts[4:7] if k == 3 else pts[10:13]
        c.wire([(x, y - 1, z + 4) for x, y, z in seg], 3, SIGNAL_PINK)
# FC -> DVR: 3 wires soldered to the FC's tap pads, plugged into J2
d_plug = (DX - 16, DX + 14)
c.box(d_plug[0], DY + 182, d_plug[1] - d_plug[0], 48, 9, SILKSCREEN_WHITE, SILKSCREEN_SHADE, hi=SILKSCREEN_SHADE, z0=2)
for k, (py, col) in enumerate([(200, BLACKW), (222, LOGO_RED), (244, BLACKW)]):
    x0, y0 = F(344, py)
    x1, y1 = d_plug[0], DY + J2_Y[k]
    pts = []
    for t in range(17):
        u = t / 16
        pts.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * (3 * u * u - 2 * u ** 3), 6 - 30 * math.sin(math.pi * u)))
    c.wire(pts, 9, col)
    c.solder(x0, y0, 7)
    if k == 0:
        c.wire([(x, y - 1, z + 4) for x, y, z in pts[6:9]], 3, GLOW_TEAL)

# ================================================================= render
out = Path(__file__).resolve().parent / "out"
out.mkdir(exist_ok=True)
c.plan_image().save(out / "clean-v1-plan.png")
img = c.render(out_size=(1800, 760), target=((EX - 160 + DX + DS) / 2, H / 2 + 20, 0), pitch=62, dist=1500, focal=1400,
               screen_cy=0.44)   # framed from the cap on the leads to the DVR
img.save(out / "clean-v1.png")
# close-up of our board alone: rendered small, scaled up with hard pixels
dvr = c.render(out_size=(560, 420), target=(DX + DS / 2 + 6, DY + DS / 2 + 14, 0), pitch=60, dist=900,
               focal=1110, screen_cy=0.5, fog=False)
dvr.resize((560 * 2, 420 * 2), Image.NEAREST).save(out / "clean-v1-dvr.png")
print("wrote", out, (W, H))
