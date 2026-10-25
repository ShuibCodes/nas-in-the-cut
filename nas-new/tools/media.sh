#!/usr/bin/env bash
# Rebuild the intro film, poster, soundtrack and chrome logo into src/media/out/.
# Needs ffmpeg and Python 3 with Pillow. Run from the project root:  bash tools/media.sh
# To swap the song, replace src/media/intro-track-source.mp3 and run this again.
set -euo pipefail
cd "$(dirname "$0")/.."
IN=src/media
OUT=src/media/out
mkdir -p "$OUT"

# Film: silent (the song plays separately so the sound button can control it),
# fast start so phones begin playing before the file has fully loaded.
ffmpeg -y -v error -i $IN/intro-source.mp4 -t 24.166 -an -vf "scale=540:-2" \
  -c:v libx264 -profile:v main -preset slow -crf 30 -pix_fmt yuv420p -movflags +faststart $OUT/intro-540.mp4
ffmpeg -y -v error -i $IN/intro-source.mp4 -t 24.166 -an \
  -c:v libx264 -profile:v high -preset slow -crf 31 -pix_fmt yuv420p -movflags +faststart $OUT/intro-720.mp4

# Poster: the first frame, shown while the film loads.
ffmpeg -y -v error -i $IN/intro-source.mp4 -frames:v 1 -q:v 4 $OUT/intro-poster.jpg

# Song: first 30 seconds, half second fade in, two second fade out, 128 kbps.
ffmpeg -y -v error -i $IN/intro-track-source.mp3 -t 30 -af "afade=t=in:d=0.5,afade=t=out:st=28:d=2" \
  -c:a libmp3lame -b:a 128k $OUT/intro-track.mp3

# Chrome logo used on the intro and in the social card.
python3 - <<'PY'
from PIL import Image
im = Image.open("src/img/logo-nitc-chrome-trim.png").convert("RGBA")
for w in (640, 1200):
    r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    r.save(f"src/media/out/logo-nitc-{w}.png", optimize=True)
    r.save(f"src/media/out/logo-nitc-{w}.webp", quality=86, method=6)
PY
ls -la $OUT
