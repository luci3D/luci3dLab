"""luci3D, the snake: the player's pet companion and guide (first draft).

Small (about half a guild avatar's height) and black. The logo is white only
because it sits on dark backgrounds; in the game the snake is black, so it
gets a grey highlight along its back and a purple rim light on its shadow
side to stand out on black boards. Teal eye: it sees the circuit from the
inside. Red tongue, like the logo.

The guild avatars live in avatars.py. Grid characters map to palette colour
names; "." is transparent.
"""


def _snake(w=23, h=14, t=3):
    g = [["."] * w for _ in range(h)]
    path = [(1, 10), (5, 10), (5, 1), (11, 1), (11, 8), (15, 8), (15, 4)]  # the logo's zig-zag

    def fill(x0, y0, x1, y1):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                if 0 <= x < w and 0 <= y < h:
                    g[y][x] = "B"
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        fill(x0, y0, x1 + t - 1, y1 + t - 1)
    g[10][0] = g[12][0] = "."             # tail tip
    g[10][1] = g[12][1] = "."
    for y in range(2, 8):                 # head, a little wider than the body
        for x in range(15, 21):
            if not (y in (2, 7) and x in (15, 20)):
                g[y][x] = "B"
    solid = [[c == "B" for c in row] for row in g]

    def body(x, y):
        return 0 <= x < w and 0 <= y < h and solid[y][x]
    for y in range(h):
        for x in range(w):
            if not solid[y][x]:
                continue
            if not body(x, y - 1) or not body(x - 1, y) and not body(x, y + 1):
                g[y][x] = "h"             # lit edge (top / left)
            elif not body(x, y + 1) or not body(x + 1, y):
                g[y][x] = "r"             # rim light (bottom / right)
            else:
                g[y][x] = "B"
    g[2][16] = g[2][17] = "s"             # specular glints
    g[1][6] = "s"
    g[4][18] = "E"
    for (x, y) in [(21, 5), (22, 5), (22, 4), (22, 6)]:
        g[y][x] = "R"
    return "\n".join("".join(r) for r in g)


SNAKE = _snake()
SNAKE_KEYS = {"B": "ic dark", "h": "ic grey", "r": "dusk purple", "s": "silkscreen shade",
              "E": "glow teal", "R": "logo red"}


def grid(text):
    return [row for row in text.strip("\n").splitlines()]
