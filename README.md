# luci3dLab

Brand, website, shop and game for **luci3D hardware** (working name, it may change).

| Folder | What |
|---|---|
| [`brand/`](brand/) | Palette (`luci3d.gpl`, load it in Aseprite), the snake logo and the scripts that draw it |
| [`art/`](art/) | [`art/world/`](art/world/): the Stack (FC + 4-in-1 ESC + cable bridge). [`art/sprites/`](art/sprites/): characters |
| [`zine/`](zine/) | The original hand-drawn maze zine: proof-of-concept levels and inspiration |
| [`docs/`](docs/) | [The story](docs/story.md) and [the workflow](docs/workflow.md) |

## Style and sizes

- **Top-down, 3/4 view.** Tops of objects plus their south face. Light from the top left.
- **Flat shapes, no outlines.** Shading is one or two darker tones of the same colour; every shadow uses the next darker palette colour (the `SHADE` table in `art/world/make_stack.py`). Inspired by Hyper Light Drifter's look; all designs are our own.
- **A human is about 32 px tall.** The game screen is 480×270 (×4 = 1920×1080).
- **Only colours from `brand/palette/luci3d.gpl`.** Scripts look colours up by name, so keep the names when you edit the palette.

## Scripts

Python 3 with Pillow (`pip install pillow`):

```bash
python3 brand/tools/make_logo.py      # snake logo PNGs
python3 art/world/make_stack.py       # the Stack: world map + one game screen
```
