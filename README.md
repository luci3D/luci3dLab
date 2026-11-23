# luci3dLab

Brand, website, shop and game for **luci3D hardware** (working name, it may change).

| Folder | What |
|---|---|
| [`brand/`](brand/) | Palette (`luci3d.gpl`, load it in Aseprite), the snake logo and the scripts that draw it |
| [`art/`](art/) | [`art/world/`](art/world/): the Stack, the first board city (FC + 4-in-1 ESC + cable bridge). [`art/sprites/`](art/sprites/): the five guild avatars and luci3D the snake (drafts) |
| [`zine/`](zine/) | The original hand-drawn maze zine: proof-of-concept levels and inspiration |
| [`docs/`](docs/) | [The story](docs/story.md) and [the workflow](docs/workflow.md) |

## Style and sizes

- **Flat shapes, no outlines.** Shading is one or two darker tones of the same colour; every shadow uses the next darker palette colour (the `SHADE` table in `art/world/make_stack.py`). Inspired by Hyper Light Drifter's look; all designs are our own.
- **Boards are black solder mask with white silkscreen.**
- **Two views:**
  - *City view*: a whole board city in perspective (`art/world/`). No characters: at this scale a person would be a dot.
  - *Street view* (the game): top-down 3/4, a human is about 32 px tall, screen 480×270 (×4 = 1920×1080).
- **Only colours from `brand/palette/luci3d.gpl`.** Scripts look colours up by name, so keep the names when you edit the palette.

## Scripts

Python 3 with Pillow (`pip install pillow`):

```bash
python3 brand/tools/make_logo.py      # snake logo PNGs
python3 art/world/make_stack.py       # the Stack: perspective city view + flat plan
python3 art/sprites/make_avatars.py   # guild avatars + line-up
```
