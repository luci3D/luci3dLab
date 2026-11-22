"""Read brand/palette/luci3d.gpl into {name: (r, g, b)} for the art scripts."""
from pathlib import Path

GPL = Path(__file__).resolve().parent.parent / "palette" / "luci3d.gpl"


def load(path=GPL):
    pal = {}
    for line in Path(path).read_text().splitlines():
        parts = line.split("\t")
        nums = parts[0].split()
        if len(nums) == 3 and all(n.isdigit() for n in nums):
            name = parts[1].strip() if len(parts) > 1 else f"c{len(pal)}"
            pal[name] = tuple(int(n) for n in nums)
    return pal
