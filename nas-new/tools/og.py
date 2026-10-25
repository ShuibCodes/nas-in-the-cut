"""Render the 1200x630 social card and the touch icons with headless Chromium."""
import base64
import io
import sys
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(ROOT))
from build import NAS_PATHS, FAVICON  # noqa: E402  one source for the mark

photo = base64.b64encode((SRC / "img" / "out" / "nas-terrace-1080.jpg").read_bytes()).decode()
chrome = base64.b64encode((SRC / "media" / "out" / "logo-nitc-1200.png").read_bytes()).decode()
LOGO = f'<img src="data:image/png;base64,{chrome}" style="width:430px;height:auto;align-self:flex-start;display:block;margin-left:-6px" alt="">'

OG = f"""<!doctype html><html><head><style>
html,body{{margin:0;width:1200px;height:630px;background:#0b1422;color:#f1f4f8;font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;overflow:hidden}}
.wrap{{display:grid;grid-template-columns:1fr 430px;height:630px}}
.txt{{padding:62px 64px 58px;display:flex;flex-direction:column;justify-content:space-between;border-right:1px solid #34455f}}
h1{{font-size:78px;line-height:1.02;letter-spacing:-.035em;margin:0;font-weight:300}}
.rule{{height:1px;background:#22314a;margin:0 0 22px}}
.foot{{display:flex;justify-content:space-between;align-items:baseline;font-size:21px;color:#a9b4c5;letter-spacing:.01em}}
.foot b{{font-weight:400;color:#f1f4f8}}
.img{{background:url(data:image/jpeg;base64,{photo}) 72% 22%/cover}}
</style></head><body><div class="wrap"><div class="txt">
{LOGO}
<h1>How the money<br>actually gets made.</h1>
<div><div class="rule"></div><div class="foot"><span><b>@nasinthecut</b>&nbsp;&nbsp;The daily email from Nasir Hassan</span><span>Dubai</span></div></div>
</div><div class="img"></div></div></body></html>"""

latte = base64.b64encode((SRC / "img" / "out" / "g-cup-latte-1280.jpg").read_bytes()).decode()
OG_CUP = f"""<!doctype html><html><head><style>
html,body{{margin:0;width:1200px;height:630px;background:#0b1422;color:#f1f4f8;font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;overflow:hidden}}
.wrap{{display:grid;grid-template-columns:1fr 560px;height:630px}}
.txt{{padding:62px 64px 58px;display:flex;flex-direction:column;justify-content:space-between;border-right:1px solid #34455f}}
.k{{font-size:22px;color:#a9b4c5;letter-spacing:.02em;margin:0 0 18px}}
h1{{font-size:96px;line-height:1;letter-spacing:-.035em;margin:0;font-weight:300}}
.sub{{font-size:28px;line-height:1.35;color:#d6dce4;margin:24px 0 0;font-weight:300}}
.rule{{height:1px;background:#22314a;margin:0 0 22px}}
.foot{{display:flex;justify-content:space-between;align-items:baseline;font-size:21px;color:#a9b4c5}}
.foot b{{font-weight:400;color:#f1f4f8}}
.img{{background:url(data:image/jpeg;base64,{latte}) 52% 55%/cover}}
</style></head><body><div class="wrap"><div class="txt">
{LOGO.replace('width:430px','width:300px')}
<div><p class="k">Once a month</p><h1>In The Cup.</h1><p class="sub">Coffee with Nas. Special guests,<br>real questions, real connections.</p></div>
<div><div class="rule"></div><div class="foot"><span><b>@nasinthecut</b>&nbsp;&nbsp;In person or online</span><span>Pull up a chair</span></div></div>
</div><div class="img"></div></div></body></html>"""

ICON = f"""<!doctype html><html><body style="margin:0;width:512px;height:512px">
{FAVICON.replace('<svg ', '<svg width="512" height="512" ')}</body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
    pg.set_content(OG)
    png = pg.screenshot(type="png")
    Image.open(io.BytesIO(png)).convert("RGB").save(SRC / "img" / "og.jpg", quality=88, optimize=True, progressive=True)
    pg.set_content(OG_CUP)
    Image.open(io.BytesIO(pg.screenshot(type="png"))).convert("RGB").save(SRC / "img" / "og-cup.jpg", quality=88, optimize=True, progressive=True)
    pg.set_viewport_size({"width": 512, "height": 512})
    pg.set_content(ICON)
    icon = Image.open(io.BytesIO(pg.screenshot(type="png"))).convert("RGB")
    icon.resize((180, 180), Image.LANCZOS).save(SRC / "apple-touch-icon.png", optimize=True)
    for size in (16, 32, 192, 512):
        icon.resize((size, size), Image.LANCZOS).save(SRC / f"icon-{size}.png", optimize=True)
    icon.save(SRC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    # Maskable: Android crops to a circle, so the mark sits inside the central 80% safe zone.
    mask = Image.new("RGB", (512, 512), (11, 20, 34))
    mask.paste(icon.resize((410, 410), Image.LANCZOS), (51, 51))
    mask.save(SRC / "icon-maskable-512.png", optimize=True)
    b.close()
print("og.jpg and the full icon set written")
