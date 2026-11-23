#!/usr/bin/env python3
"""Render the guild avatars: one PNG per guild plus a line-up on a black board.

    python3 art/sprites/make_avatars.py
      -> art/sprites/out/avatar-<guild>.png      1x, transparent (for Aseprite / the game)
      -> art/sprites/out/guild-lineup.png        all guilds + luci3D, scaled up to look at
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "brand" / "tools"))
sys.path.insert(0, str(HERE))
import palette  # noqa: E402
import avatars  # noqa: E402
import sprites  # noqa: E402
from font3x5 import text_pixels, text_width  # noqa: E402

P = palette.load()
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

for row in avatars.BASE:
    assert len(row) == avatars.W, row


def sprite_image(grid, keys):
    im = Image.new("RGBA", (len(grid[0]), len(grid)), (0, 0, 0, 0))
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch != ".":
                im.putpixel((x, y), P[keys[ch]] + (255,))
    return im


imgs = {}
for name in avatars.ORDER:
    g = avatars.build(name)
    imgs[name] = sprite_image(g, avatars.GUILDS[name]["keys"])
    imgs[name].save(OUT / f"avatar-{name}.png")
snake = sprite_image(sprites.grid(sprites.SNAKE), sprites.SNAKE_KEYS)

# line-up on a strip of black board
SLOT, PAD = 40, 14
LW = PAD * 2 + SLOT * len(imgs) + snake.width + 10
LH = 52
strip = Image.new("RGB", (LW, LH), P["black mask"])
d = ImageDraw.Draw(strip)
d.rectangle([0, 40, LW, 44], fill=P["black trace highlight"])   # a trace to stand on
d.rectangle([0, 44, LW, 45], fill=P["black trace"])
for x in range(6, LW, 28):
    d.rectangle([x, 10, x + 1, 11], fill=P["black trace"])          # tented vias
shadow = P["black mask deep"]
x = PAD
for name, im in imgs.items():
    fx = x + (SLOT - im.width) // 2
    fy = 44 - im.height + 1
    d.ellipse([fx + 3, 41, fx + im.width - 3, 46], fill=shadow)
    if name == "whitespace":                                     # the drone's own shadow
        d.ellipse([fx + 16, 45, fx + 22, 47], fill=shadow)
    strip.paste(im, (fx, fy), im)
    x += SLOT
sx, sy = x + 4, 44 - snake.height + 2
d.polygon([(sx + 3, sy + 30), (sx + 52, sy + 30), (sx + 52, sy + 33), (sx + 3, sy + 33)], fill=shadow)
strip.paste(snake, (sx, sy), snake)

S = 6
big = strip.resize((LW * S, LH * S), Image.NEAREST)
canvas = Image.new("RGB", (big.width, big.height + 60), P["void"])
canvas.paste(big, (0, 0))
labels = [avatars.GUILDS[n]["title"] for n in avatars.ORDER] + ["LUCI3D"]
centers = [PAD + SLOT * i + SLOT // 2 for i in range(len(imgs))] + [sx + snake.width // 2]
for lab, cx in zip(labels, centers):
    tw = text_width(lab, 3)
    for dx, dy in text_pixels(lab, 3):
        canvas.putpixel((cx * S - tw // 2 + dx, big.height + 22 + dy), P["silkscreen white"])
canvas.save(OUT / "guild-lineup.png")
print("wrote", OUT)
