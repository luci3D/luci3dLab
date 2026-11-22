# luci3dLab

Brand, website, shop and game for **luci3D hardware** (working name, it may change).

| Folder | What |
|---|---|
| [`brand/`](brand/) | Palette (`luci3d.gpl`, load it in Aseprite), the snake logo and the scripts that draw it |
| [`art/`](art/) | Scenes and tiles. Start with [`art/city/`](art/city/), the flight-controller city |
| [`zine/`](zine/) | The original hand-drawn maze zine: proof-of-concept levels and inspiration |
| [`docs/`](docs/) | [The story](docs/story.md) and [the workflow](docs/workflow.md) |

## Fixed sizes

- **Base canvas 320×180.** Scales by whole numbers to every target: ×4 = 1280×720 (YouTube thumbnail), ×6 = 1920×1080 (video), ×8 = 2560×1440 (channel banner).
- **16 px tiles** for the game. A room is 20×10 tiles plus a 20 px status bar.
- **Only colours from `brand/palette/luci3d.gpl`.** Scripts look colours up by name, so keep the names when you edit the palette.

## Scripts

Python 3 with Pillow (`pip install pillow`):

```bash
python3 brand/tools/make_logo.py      # snake logo PNGs
python3 art/city/make_fc_city.py      # FC city mock-up
```
