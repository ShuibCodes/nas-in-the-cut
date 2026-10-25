"""Produce responsive AVIF and JPEG renditions from the source photos.

Two sets:
  frames:  cropped to 3:4 for the layout slots, at 480, 800 and 1080 wide
  gallery: native shape for In The Room, at 640 and 1280 wide
Output goes to src/img/out/. build.py reads the result.
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "img"
OUT = SRC / "out"
OUT.mkdir(parents=True, exist_ok=True)

# name: horizontal focus (0 left, 1 right) used when a wider photo is cut to 3:4
FRAMES = {
    "nas-terrace": .5, "nas-mo-farah": .5, "collective-365": .5, "collective-365-b": .5,
    "collective-365-c": .5, "collective-365-d": .5, "davido-spiro": .5, "bcn-handshake": .42,
    "davido-backstage": .5, "bcn-training-ground": .42, "nas-sea-terrace": .5,
    "bcn-laugh": .45, "bcn-dinner": .35,
    "cup-latte": .5, "cup-kokko": .5, "cup-lounge": .55, "cup-lobby": .5, "davido-lunch": .5,
}
GALLERY = ["bcn-handshake", "bcn-laugh", "bcn-boardroom", "bcn-dinner", "bcn-training-ground",
           "davido-spiro", "davido-backstage", "nas-mo-farah", "nas-terrace", "nas-sea-terrace",
           "collective-365", "collective-365-c", "collective-365-b", "collective-365-d",
           "davido-lunch", "cup-lounge", "cup-kokko", "cup-lobby", "cup-latte", "cup-latte-close"]


def save(r, stem, q=(52, 74, 78)):
    r.save(OUT / f"{stem}.avif", quality=q[0], speed=4)
    r.save(OUT / f"{stem}.jpg", quality=q[2], optimize=True, progressive=True)


for name, fx in FRAMES.items():
    if not (SRC / f"{name}.jpg").exists():
        continue
    im = ImageOps.exif_transpose(Image.open(SRC / f"{name}.jpg")).convert("RGB")
    w, h = im.size
    if h < w * 4 / 3:  # too wide: cut the sides around the focus point
        cw = round(h * 3 / 4)
        left = min(max(0, round(w * fx - cw / 2)), w - cw)
        im = im.crop((left, 0, left + cw, h))
    else:  # too tall: cut top and bottom evenly
        ch = round(w * 4 / 3)
        top = (h - ch) // 2
        im = im.crop((0, top, w, top + ch))
    for width in (480, 800, 1080):
        if width <= im.width:
            save(im.resize((width, round(width * 4 / 3)), Image.LANCZOS), f"{name}-{width}")

for name in GALLERY:
    if not (SRC / f"{name}.jpg").exists():
        continue
    im = ImageOps.exif_transpose(Image.open(SRC / f"{name}.jpg")).convert("RGB")
    for width in (640, 1280):
        if width <= im.width:
            save(im.resize((width, round(width * im.height / im.width)), Image.LANCZOS), f"g-{name}-{width}")

total = sum(f.stat().st_size for f in OUT.iterdir())
print(f"{len(list(OUT.iterdir()))} files, {total/1024/1024:.1f} MB")
