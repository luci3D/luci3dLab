"""Detailed e-waste for the lab scenes: computer parts, robot parts, a crashed delivery drone.

Bound to a scene's own 2D drawing helpers, so every scene draws them the same way:

    parts = Parts(R, line, ell, px, sag, drone, P)
    parts.scatter([(parts.gpu, 380, 236), (parts.robot_head, 450, 226), ...])

Flat shapes, palette colours only. Coordinates are screen pixels at 480 x 270.
"""


class Parts:
    def __init__(self, R, line, ell, px, sag, drone, P):
        self.R, self.line, self.ell, self.px, self.sag, self.drone = R, line, ell, px, sag, drone
        self.c = {k.upper().replace(" ", "_"): v for k, v in P.items()}

    def scatter(self, items):
        """Draw (part, x, y) items back to front."""
        for fn, x, y in sorted(items, key=lambda t: t[2]):
            fn(x, y)

    def motherboard(self, x, y):
        R, line, px, c = self.R, self.line, self.px, self.c
        R(x, y, x + 34, y + 24, c["MASK"])
        R(x, y, x + 34, y, c["TRACE_HIGHLIGHT"])
        R(x + 5, y + 5, x + 13, y + 13, c["SILKSCREEN_SHADE"])           # CPU socket
        R(x + 7, y + 7, x + 11, y + 11, c["IC_GREY"])
        for k in range(3):                                               # RAM slots
            line([(x + 17 + k * 2, y + 3), (x + 17 + k * 2, y + 15)], c["IC_BLACK"])
        for k in range(2):                                               # PCIe slots
            line([(x + 3, y + 18 + k * 3), (x + 24, y + 18 + k * 3)], c["IC_BLACK"])
        R(x + 28, y - 3, x + 34, y + 7, c["IC_GREY"])                     # I/O shield
        for k in range(4):
            px(x + 4 + k * 3, y + 15, c["IC_DARK"])

    def ram(self, x, y):
        R, line, c = self.R, self.line, self.c
        R(x, y, x + 22, y + 5, c["MASK"])
        for k in range(4):
            R(x + 2 + k * 5, y + 1, x + 5 + k * 5, y + 3, c["IC_BLACK"])
        line([(x, y + 5), (x + 22, y + 5)], c["ENIG_GOLD"])

    def gpu(self, x, y):
        R, line, ell, c = self.R, self.line, self.ell, self.c
        R(x, y, x + 32, y + 11, c["IC_DARK"])
        R(x, y, x + 32, y, c["IC_GREY"])
        R(x, y + 10, x + 32, y + 11, c["LOGO_RED"])
        for fx in (x + 9, x + 23):
            ell(fx, y + 5, 4.5, 4.5, c["IC_BLACK"])
            line([(fx - 3, y + 5), (fx + 3, y + 5)], c["IC_GREY"])
            line([(fx, y + 2), (fx, y + 8)], c["IC_GREY"])
        line([(x + 4, y + 12), (x + 24, y + 12)], c["ENIG_GOLD"])

    def psu(self, x, y):
        R, line, ell, sag, c = self.R, self.line, self.ell, self.sag, self.c
        R(x, y, x + 18, y + 14, c["IC_GREY"])
        R(x, y, x + 18, y + 2, c["SILKSCREEN_SHADE"])
        ell(x + 9, y + 8, 5, 5, c["IC_DARK"])
        line([(x + 5, y + 8), (x + 13, y + 8)], c["IC_GREY"])
        line([(x + 9, y + 4), (x + 9, y + 12)], c["IC_GREY"])
        for k, col in enumerate((c["WIRE_YELLOW"], c["LOGO_RED"], c["IC_DARK"])):
            line(sag(x + 18, y + 4 + k * 3, x + 30, y + 10 + k * 3, 3, 6), col)

    def hdd(self, x, y):
        R, ell, px, c = self.R, self.ell, self.px, self.c
        R(x, y, x + 14, y + 10, c["SILKSCREEN_SHADE"])
        R(x, y, x + 14, y, c["SILKSCREEN_WHITE"])
        ell(x + 6, y + 5, 3.5, 3.5, c["IC_GREY"])
        px(x + 6, y + 5, c["SILKSCREEN_WHITE"])

    def robot_arm(self, x, y):
        line, ell, c = self.line, self.ell, self.c
        line([(x, y), (x + 18, y - 10)], c["WIRE_YELLOW"], 5)
        line([(x + 18, y - 10), (x + 30, y - 4)], c["WIRE_YELLOW"], 4)
        line([(x, y - 2), (x + 18, y - 12)], c["GOLD_HIGHLIGHT"])
        for jx, jy in ((x, y), (x + 18, y - 10)):
            ell(jx, jy, 4, 4, c["IC_GREY"])
            ell(jx, jy, 2, 2, c["IC_DARK"])
        line([(x + 30, y - 4), (x + 35, y - 7)], c["IC_GREY"], 2)
        line([(x + 30, y - 4), (x + 35, y - 1)], c["IC_GREY"], 2)

    def robot_head(self, x, y):
        R, line, ell, px, c = self.R, self.line, self.ell, self.px, self.c
        R(x, y, x + 16, y + 12, c["IC_GREY"])
        R(x, y, x + 16, y + 2, c["SILKSCREEN_SHADE"])
        for ex, col in ((x + 4, c["GLOW_TEAL"]), (x + 11, c["LOGO_RED"])):
            ell(ex, y + 6, 3, 3, c["IC_BLACK"])
            px(ex, y + 6, col)
        line([(x + 9, y + 3), (x + 12, y + 9)], c["IC_BLACK"])           # crack
        line([(x + 8, y), (x + 8, y - 5)], c["IC_GREY"])
        px(x + 8, y - 6, c["LOGO_RED"])

    def track(self, x, y):
        R, ell, px, c = self.R, self.ell, self.px, self.c
        R(x, y, x + 24, y + 7, c["IC_BLACK"])
        for k in range(4):
            ell(x + 4 + k * 5.5, y + 3.5, 2.5, 2.5, c["IC_GREY"])
        for k in range(0, 24, 3):
            px(x + k, y, c["IC_DARK"])

    def servo(self, x, y):
        R, line, c = self.R, self.line, self.c
        R(x, y, x + 8, y + 5, c["WIRE_BLUE"])
        R(x, y, x + 8, y, c["GLOW_TEAL"])
        line([(x + 2, y - 1), (x + 7, y - 1)], c["SILKSCREEN_WHITE"])

    def delivery_drone(self, x, y):
        R, line, c = self.R, self.line, self.c
        self.drone(x, y, 26, arms=6, tilt=-0.12, broken=(4,), noprop=(1, 2), body=c["SILKSCREEN_WHITE"],
                   props=(c["IC_GREY"],), led=None)
        R(x - 8, y + 6, x + 8, y + 18, c["FR4_EDGE"])                     # its parcel, still strapped on
        R(x - 8, y + 6, x + 8, y + 8, c["FR4_SHADE"])
        R(x - 1, y + 6, x + 1, y + 18, c["COPPER"])
        line([(x - 6, y + 2), (x - 6, y + 6)], c["IC_GREY"])
        line([(x + 6, y + 2), (x + 6, y + 6)], c["IC_GREY"])
