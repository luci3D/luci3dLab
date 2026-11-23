"""Character sprites as text grids (first drafts, to be redrawn in Aseprite).

The guild avatars live in avatars.py. Scale: a human is about 32 px tall.
No outlines: shapes are flat colour,
lit from the top left, with a darker tone on the shaded side.
Each grid character maps to a palette colour name; "." is transparent.
"""

# luci3D, the snake (the player's ally), zig-zagging like the logo, 6 px body. Head faces east.
def _snake(w=54, h=32, t=6):
    g = [["."] * w for _ in range(h)]
    path = [(1, 25), (12, 25), (12, 1), (28, 1), (28, 20), (38, 20), (38, 10)]

    def fill(x0, y0, x1, y1):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                if 0 <= x < w and 0 <= y < h:
                    g[y][x] = "W"
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        fill(x0, y0, x1 + t - 1, y1 + t - 1)
    for x in range(0, 6):  # tapering tail
        g[25][x] = g[30][x] = "."
    for x in range(0, 3):
        g[26][x] = g[29][x] = "."
    for y in range(6, 18):  # head, wider than the body
        for x in range(36, 49):
            if not ((y in (6, 17)) and x in (36, 48)):
                g[y][x] = "W"
    shaded = [[g[y][x] == "W" and (y + 1 >= h or g[y + 1][x] == "." or x + 1 >= w or g[y][x + 1] == ".")
               for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            if shaded[y][x]:
                g[y][x] = "S"
    for (x, y) in [(43, 9), (44, 9), (43, 10), (44, 10)]:
        g[y][x] = "E"
    for (x, y) in [(49, 12), (50, 12), (51, 11), (52, 10), (51, 13), (52, 14)]:
        g[y][x] = "R"
    return "\n".join("".join(r) for r in g)


SNAKE = _snake()
SNAKE_KEYS = {"W": "silkscreen white", "S": "silkscreen shade", "E": "ic black", "R": "logo red"}


def grid(text):
    return [row for row in text.strip("\n").splitlines()]
