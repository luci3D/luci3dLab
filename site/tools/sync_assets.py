#!/usr/bin/env python3
"""Copy the art the website uses from the repo into site/img, and build the favicon.

Run after re-rendering any art:
    python3 site/tools/sync_assets.py
"""
import shutil
import sys
from pathlib import Path

from PIL import Image

SITE = Path(__file__).resolve().parents[1]
ROOT = SITE.parent
sys.path.insert(0, str(ROOT / "brand" / "tools"))
import palette  # noqa: E402

IMG = SITE / "img"
IMG.mkdir(exist_ok=True)
COPIES = {
    "art/world/out/clean-v1.png": "clean.png",
    "art/world/out/clean-v1-plan.png": "clean-plan.png",
    "art/world/out/stack-v2.png": "stack.png",
    "brand/logo/luci3d-snake-1x.png": "logo-1x.png",
    "brand/logo/luci3d-snake-8x.png": "logo-8x.png",
    **{f"zine/maze-0{i}.png": f"maze-0{i}.png" for i in range(1, 6)},
}
for src, dst in COPIES.items():
    shutil.copyfile(ROOT / src, IMG / dst)

# favicon: the snake on black mask, padded square, scaled with hard pixels
P = palette.load()
logo = Image.open(ROOT / "brand/logo/luci3d-snake-1x.png").convert("RGBA")
side = max(logo.size) + 3
icon = Image.new("RGBA", (side, side), P["black mask"] + (255,))
icon.paste(logo, ((side - logo.width) // 2, (side - logo.height) // 2), logo)
icon.resize((side * 6, side * 6), Image.NEAREST).save(IMG / "favicon.png")
print("synced", sorted(p.name for p in IMG.iterdir()))
