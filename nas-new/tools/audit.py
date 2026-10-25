"""Audit gate for dist/. Serves it locally and exits non zero on any finding."""
import functools
import http.server
import re
import sys
import threading
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
PORT = 8765
ORIGIN = f"http://127.0.0.1:{PORT}"
WIDTHS = [320, 360, 375, 390, 414, 480, 768, 1024, 1280, 1600]
PAGES = ["index.html", "in-the-cup.html", "in-the-room.html"]

findings = []
def fail(msg):
    findings.append(msg)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), functools.partial(Quiet, directory=str(DIST)))
threading.Thread(target=srv.serve_forever, daemon=True).start()

LAYOUT_JS = r"""
() => {
  const out = {overflow: [], small: []};
  const vw = document.documentElement.clientWidth;
  if (document.documentElement.scrollWidth > vw) out.overflow.push('document scrollWidth ' + document.documentElement.scrollWidth + ' > ' + vw);
  for (const el of document.querySelectorAll('body *')) {
    if (el.closest('.skip, .hp, .vh, [data-hscroll]')) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    // Content clipped by an in-bounds ancestor (overflow hidden, clip or a
    // scroll box) is not visible past the viewport. The ancestor itself is
    // still measured, so a too-wide container is still caught.
    let clipped = false;
    for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
      const ox = getComputedStyle(a).overflowX;
      if (ox !== 'visible') { const ar = a.getBoundingClientRect(); if (ar.left >= -0.5 && ar.right <= vw + 0.5) { clipped = true; break; } }
    }
    if (clipped) continue;
    if (r.right > vw + 0.5 || r.left < -0.5) out.overflow.push(el.tagName.toLowerCase() + '.' + (el.className || '') + ' spans ' + Math.round(r.left) + '..' + Math.round(r.right));
  }
  for (const el of document.querySelectorAll('a[href], button, input:not([type=hidden]), select, textarea')) {
    if (el.closest('.hp, .vh')) continue;
    if (el.classList.contains('skip')) continue;
    if (el.getClientRects().length === 0) continue;
    if (getComputedStyle(el).visibility === 'hidden' || el.closest('[inert]')) continue;
    let r = el.getBoundingClientRect();
    // A wrapped radio or checkbox is operated through its label, so the label is the target.
    if (el.labels && el.labels.length) { const lr = el.labels[0].getBoundingClientRect(); if (lr.width * lr.height > r.width * r.height) r = lr; }
    const inline = el.tagName === 'A' && getComputedStyle(el).display === 'inline' && el.parentElement && /^(P|LI|SPAN)$/.test(el.parentElement.tagName) && el.parentElement.textContent.trim().length > el.textContent.trim().length;
    if (inline) continue;
    if (r.width < 24 || r.height < 24) out.small.push((el.textContent.trim() || el.outerHTML.slice(0, 60)) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
  }
  return out;
}
"""

STRUCT_JS = r"""
() => {
  const f = [];
  if (document.querySelectorAll('h1').length !== 1) f.push('h1 count ' + document.querySelectorAll('h1').length);
  if (document.querySelectorAll('main').length !== 1) f.push('main count');
  let prev = 0;
  for (const h of document.querySelectorAll('h1,h2,h3,h4,h5,h6')) {
    const l = +h.tagName[1];
    if (prev && l > prev + 1) f.push('heading skip h' + prev + ' to h' + l + ': ' + h.textContent.trim());
    prev = l;
  }
  const ids = {};
  for (const el of document.querySelectorAll('[id]')) { ids[el.id] = (ids[el.id] || 0) + 1; }
  for (const [k, v] of Object.entries(ids)) if (v > 1) f.push('duplicate id ' + k);
  for (const a of document.querySelectorAll('[aria-describedby],[aria-labelledby]')) {
    for (const attr of ['aria-describedby', 'aria-labelledby']) {
      for (const id of (a.getAttribute(attr) || '').split(/\s+/).filter(Boolean)) if (!document.getElementById(id)) f.push(attr + ' points at missing #' + id);
    }
  }
  for (const img of document.querySelectorAll('img')) if (!img.hasAttribute('alt') || (!img.alt.trim() && img.getAttribute('role') !== 'presentation')) f.push('img without alt ' + img.src);
  for (const svg of document.querySelectorAll('svg')) if (!svg.getAttribute('aria-label') && svg.getAttribute('aria-hidden') !== 'true' && !svg.querySelector('title')) f.push('svg without text alternative');
  for (const inp of document.querySelectorAll('input:not([type=hidden]), select, textarea')) {
    if (!inp.labels || inp.labels.length === 0) f.push('field without label #' + inp.id);
    if (inp.closest('.hp') && inp.tabIndex !== -1) f.push('honeypot reachable #' + inp.id);
  }
  if (!document.documentElement.lang) f.push('no lang');
  const t = document.title.length;
  if (t < 20 || t > 95) f.push('title length ' + t);
  const d = (document.querySelector('meta[name=description]') || {}).content || '';
  if (d.length < 60 || d.length > 185) f.push('description length ' + d.length);
  if (!document.querySelector('link[rel=canonical]')) f.push('no canonical');
  for (const img of document.querySelectorAll('img')) if (!img.complete || img.naturalWidth === 0) f.push('image failed to load ' + img.currentSrc);
  return {f, title: t, desc: d.length};
}
"""

CONTRAST_JS = r"""
() => {
  const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; };
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const blend = (top, under) => ({r: top.r * top.a + under.r * (1 - top.a), g: top.g * top.a + under.g * (1 - top.a), b: top.b * top.a + under.b * (1 - top.a), a: 1});
  const bgOf = el => {
    const stack = [];
    for (let n = el; n; n = n.parentElement) { const c = parse(getComputedStyle(n).backgroundColor); if (c && c.a > 0) { stack.push(c); if (c.a === 1) break; } }
    let base = {r: 255, g: 255, b: 255, a: 1};
    for (let i = stack.length - 1; i >= 0; i--) base = blend(stack[i], base);
    return base;
  };
  let min = 99, worst = '', bad = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const node = walker.currentNode; if (!node.textContent.trim()) continue;
    const el = node.parentElement; if (el.closest('.vh, .hp, .skip, script, style')) continue;
    const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const bg = bgOf(el); const fg = blend(parse(cs.color), bg);
    const L1 = lum(fg), L2 = lum(bg); const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const size = parseFloat(cs.fontSize), weight = parseInt(cs.fontWeight);
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    const need = large ? 3 : 4.5;
    if (ratio < min) { min = ratio; worst = node.textContent.trim().slice(0, 40); }
    if (ratio < need) bad.push(node.textContent.trim().slice(0, 40) + ' ' + ratio.toFixed(2));
  }
  return {min, worst, bad};
}
"""

third_party, console_errors = [], []
# The In The Cup seat form is an embedded Typeform (SEAT_FORM_URL in build.py).
ALLOWED_HOSTS = ("https://form.typeform.com/",)

SEEN = "try { sessionStorage.setItem('nitc-intro', 'seen'); } catch (e) {}"
signals = []


cup_posts = []


def on_cup(route):
    cup_posts.append(route.request.post_data or "")
    route.fulfill(status=200, content_type="application/json", body='{"ok":true,"message":"You are on the list."}')


def on_signal(route):
    signals.append(route.request.post_data)
    route.fulfill(status=204, body="")


with sync_playwright() as p:
    browser = p.chromium.launch()

    def nc(intro_seen=True, **kw):
        c = browser.new_context(**kw)
        if intro_seen:
            c.add_init_script(SEEN)
        c.route("**/signal.php", on_signal)
        c.route("**/cup.php", on_cup)
        return c

    for name in PAGES:
        url = f"{ORIGIN}/{name}"
        for w in WIDTHS:
            ctx = nc(viewport={"width": w, "height": 900})
            pg = ctx.new_page()
            pg.on("console", lambda m: m.type == "error" and console_errors.append(m.text))
            pg.on("pageerror", lambda e: console_errors.append(str(e)))
            pg.goto(url, wait_until="networkidle")
            # Scroll through so lazy images and reveals settle.
            pg.evaluate("async () => { for (let y = 0; y < document.body.scrollHeight; y += 400) { window.scrollTo({top: y, behavior: 'instant'}); await new Promise(r => setTimeout(r, 40)); } window.scrollTo({top: 0, behavior: 'instant'}); }")
            pg.wait_for_load_state("networkidle")
            pg.wait_for_timeout(700)
            lay = pg.evaluate(LAYOUT_JS)
            for o in lay["overflow"]:
                fail(f"{name}@{w}: overflow {o}")
            for s in lay["small"]:
                fail(f"{name}@{w}: small target {s}")
            if w in (320, 1280):
                st = pg.evaluate(STRUCT_JS)
                for f in st["f"]:
                    fail(f"{name}@{w}: {f}")
                c = pg.evaluate(CONTRAST_JS)
                for b in c["bad"]:
                    fail(f"{name}@{w}: contrast {b}")
                print(f"{name}@{w}: lowest contrast {c['min']:.2f}:1 ('{c['worst']}'), title {st['title']} chars, description {st['desc']} chars")
            hosts = pg.evaluate("() => performance.getEntriesByType('resource').map(e => e.name)")
            for h in hosts:
                if not h.startswith((ORIGIN, "data:") + ALLOWED_HOSTS):
                    third_party.append(h)
            if w == 1280:
                pg.screenshot(path=str(ROOT / "shots" / f"desktop.png"), full_page=True)
            if w == 390:
                pg.screenshot(path=str(ROOT / "shots" / f"mobile.png"), full_page=True)
            ctx.close()

        if name == "index.html":
            # Mobile behaviour: dock, statement, rail.
            ctx = nc(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
            pg = ctx.new_page(); pg.goto(url, wait_until="networkidle")
            if pg.evaluate("() => document.getElementById('dock').classList.contains('show')"):
                fail(f"{name}: dock visible on load")
            pg.evaluate("() => window.scrollTo({top: document.getElementById('issues').offsetTop, behavior: 'instant'})")
            pg.wait_for_timeout(500)
            d = pg.evaluate("() => { const d = document.getElementById('dock'); const r = d.getBoundingClientRect(); return {show: d.classList.contains('show'), inert: d.hasAttribute('inert'), bottom: Math.round(r.bottom), vh: innerHeight}; }")
            if not d["show"] or d["inert"]:
                fail(f"{name}: dock not shown mid page {d}")
            pg.wait_for_timeout(500)
            d = pg.evaluate("() => { const r = document.getElementById('dock').getBoundingClientRect(); return {bottom: Math.round(r.bottom), vh: innerHeight}; }")
            if d["bottom"] > d["vh"] + 1:
                fail(f"{name}: dock geometry off screen {d}")
            pg.evaluate("() => window.scrollTo({top: document.getElementById('join').offsetTop, behavior: 'instant'})")
            pg.wait_for_timeout(500)
            if pg.evaluate("() => document.getElementById('dock').classList.contains('show')"):
                fail(f"{name}: dock still visible at the final form")
            ctx.close()

            # Interactive pieces: issue previews, rails, numbers, progress.
            for w in (390, 1280):
                ctx = nc(viewport={"width": w, "height": 844}, has_touch=(w == 390))
                pg = ctx.new_page(); pg.goto(url, wait_until="networkidle")
                for i in (1, 2, 3):
                    pg.evaluate(f"() => document.getElementById('issue-{i}-btn').scrollIntoView({{behavior: 'instant', block: 'center'}})")
                    pg.click(f"#issue-{i}-btn")
                    st = pg.evaluate(f"() => ({{exp: document.getElementById('issue-{i}-btn').getAttribute('aria-expanded'), hidden: document.getElementById('issue-{i}-body').hidden, h: document.getElementById('issue-{i}-body').getBoundingClientRect().height}})")
                    if st["exp"] != "true" or st["hidden"] or st["h"] < 40:
                        fail(f"{name}@{w}: issue {i} did not open {st}")
                    pg.click(f"#issue-{i}-btn")
                    if not pg.evaluate(f"() => document.getElementById('issue-{i}-body').hidden"):
                        fail(f"{name}@{w}: issue {i} did not close")
                for rid in ("rule-rail", "shot-rail"):
                    ctl = f'.rail-ctl[data-for="{rid}"]'
                    if pg.evaluate(f"() => document.querySelector('{ctl}').classList.contains('static')"):
                        continue
                    pg.evaluate(f"() => document.querySelector('{ctl}').scrollIntoView({{behavior: 'instant', block: 'center'}})")
                    before = pg.evaluate(f"() => document.getElementById('{rid}').scrollLeft")
                    pg.click(f'{ctl} [data-dir="1"]')
                    pg.wait_for_timeout(900)
                    after = pg.evaluate(f"() => ({{x: document.getElementById('{rid}').scrollLeft, cur: document.querySelector('{ctl} [data-cur]').textContent, prev: document.querySelector('{ctl} [data-dir=\"-1\"]').getAttribute('aria-disabled')}})")
                    if after["x"] <= before or after["cur"] != "02" or after["prev"] != "false":
                        fail(f"{name}@{w}: {rid} next did not advance {after}")
                pg.evaluate("() => document.querySelector('.stats').scrollIntoView({behavior: 'instant'})")
                pg.wait_for_timeout(1800)
                nums = pg.evaluate("() => [...document.querySelectorAll('[data-count]')].map(e => e.textContent === e.getAttribute('data-count'))")
                if not all(nums):
                    fail(f"{name}@{w}: numbers did not settle on their real values")
                pg.evaluate("() => window.scrollTo({top: document.body.scrollHeight, behavior: 'instant'})")
                pg.wait_for_timeout(300)
                prog = pg.evaluate("() => getComputedStyle(document.getElementById('progress')).transform")
                if prog in ("none", "matrix(0, 0, 0, 1, 0, 0)"):
                    fail(f"{name}@{w}: progress line did not move ({prog})")
                ctx.close()

        # Keyboard order: every interactive control reached by Tab, in DOM order.
        ctx = nc(viewport={"width": 1280, "height": 900})
        pg = ctx.new_page(); pg.goto(url, wait_until="networkidle")
        expected = pg.evaluate("() => { const seen = new Set(); return [...document.querySelectorAll('a[href], button, input:not([type=hidden]), textarea, select, [tabindex=\"0\"]')].filter(e => !e.closest('[inert]')).filter(e => e.tabIndex >= 0 && (e.offsetParent !== null || e.getClientRects().length) || e.classList.contains('skip')).filter(e => { if (e.type !== 'radio') return true; if (seen.has(e.name)) return false; seen.add(e.name); return true; }).map(e => e.id || e.textContent.trim() || e.getAttribute('href')); }")
        seen = []
        for _ in range(len(expected) + 5):
            pg.keyboard.press("Tab")
            seen.append(pg.evaluate("() => { const e = document.activeElement; return e.id || e.textContent.trim() || e.getAttribute('href'); }"))
        seen = seen[:len(expected)]
        if seen != expected:
            fail(f"{name}: tab order mismatch\n  expected {expected}\n  got      {seen}")
        # Skip link visible when focused.
        pg.reload(); pg.keyboard.press("Tab")
        top = pg.evaluate("() => document.activeElement.getBoundingClientRect().top")
        if top < 0:
            fail(f"{name}: skip link not visible on focus")

        if name == "index.html":
            # Forms: empty and bad submissions report invalid; only email is required.
            for fid in ["subscribe", "subscribe-2"]:
                pg.reload(wait_until="networkidle")
                required = pg.evaluate(f"() => [...document.querySelectorAll('#{fid} [required]')].map(e => e.name)")
                if required != ["email"]:
                    fail(f"{name}: #{fid} required fields {required}")
                pg.click(f"#{fid} button[type=submit]")
                inv = pg.get_attribute(f"#{fid}-email", "aria-invalid")
                msg = pg.get_attribute(f"#{fid}-msg", "data-state")
                focused = pg.evaluate("() => document.activeElement.id")
                if inv != "true" or msg != "error" or focused != f"{fid}-email":
                    fail(f"{name}: #{fid} empty submit not reported (aria-invalid={inv}, state={msg}, focus={focused})")
                pg.fill(f"#{fid}-email", "not-an-email")
                pg.click(f"#{fid} button[type=submit]")
                if pg.get_attribute(f"#{fid}-email", "aria-invalid") != "true":
                    fail(f"{name}: #{fid} bad email accepted")
                pg.fill(f"#{fid}-email", "reader@example.com")
                pg.click(f"#{fid} button[type=submit]")
                if pg.get_attribute(f"#{fid}-msg", "data-state") != "ok":
                    fail(f"{name}: #{fid} valid email not accepted")
        ctx.close()

        # Reduced motion: nothing hidden behind reveal classes.
        ctx = nc(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
        pg = ctx.new_page(); pg.goto(url, wait_until="networkidle")
        hidden = pg.evaluate("() => [...document.querySelectorAll('[data-reveal]')].filter(e => getComputedStyle(e).opacity !== '1' || e.classList.contains('reveal')).length")
        if hidden:
            fail(f"{name}: {hidden} elements hidden under reduced motion")
        # Print: forms hidden, content visible.
        pg.emulate_media(media="print")
        pr = pg.evaluate("() => ({form: document.querySelector('form.signup') ? getComputedStyle(document.querySelector('form.signup')).display : 'none', h1: getComputedStyle(document.querySelector('h1')).display, reveal: [...document.querySelectorAll('[data-reveal]')].filter(e => getComputedStyle(e).opacity !== '1').length})")
        if pr["form"] != "none" or pr["h1"] == "none" or pr["reveal"]:
            fail(f"{name}: print media wrong {pr}")
        ctx.close()
    # Intro film: shows on a first visit, traps focus, enters on the button, stays gone on reload.
    for w in (390, 1440):
        ctx = nc(intro_seen=False, viewport={"width": w, "height": 844})
        pg = ctx.new_page(); pg.goto(f"{ORIGIN}/index.html", wait_until="load")
        pg.wait_for_timeout(2200)
        st = pg.evaluate("""() => { const i = document.getElementById('intro'); const r = i.getBoundingClientRect(); const v = document.getElementById('intro-film');
            return {on: document.documentElement.classList.contains('intro-on'), w: Math.round(r.width), h: Math.round(r.height), vw: innerWidth, vh: innerHeight,
                    inert: document.getElementById('main').hasAttribute('inert'), focus: document.activeElement.id, src: v.getAttribute('src') || '',
                    logo: document.querySelector('.intro-mark img').complete && document.querySelector('.intro-mark img').naturalWidth > 0}; }""")
        if not (st["on"] and st["w"] == st["vw"] and st["h"] == st["vh"] and st["inert"] and st["focus"] == "intro-enter" and st["logo"]):
            fail(f"intro@{w}: not shown correctly {st}")
        want = "intro-540.mp4" if w < 700 else "intro-720.mp4"
        if not st["src"].endswith(want):
            fail(f"intro@{w}: film source {st['src']} (want {want})")
        pg.keyboard.press("Tab")
        if pg.evaluate("() => document.getElementById('intro').contains(document.activeElement)") is not True:
            fail(f"intro@{w}: focus escaped the intro")
        pg.click("#intro-enter")
        pg.wait_for_timeout(1500)
        st = pg.evaluate("() => ({hidden: document.getElementById('intro').hidden, on: document.documentElement.classList.contains('intro-on'), inert: document.getElementById('main').hasAttribute('inert'), seen: sessionStorage.getItem('nitc-intro'), scroll: getComputedStyle(document.documentElement).overflow})")
        if not st["hidden"] or st["on"] or st["inert"] or st["seen"] != "seen" or st["scroll"] == "hidden":
            fail(f"intro@{w}: did not hand over to the site {st}")
        pg.reload(wait_until="load"); pg.wait_for_timeout(400)
        if not pg.evaluate("() => document.getElementById('intro').hidden"):
            fail(f"intro@{w}: shown again in the same visit")
        # Escape also enters, and the footer replays the film.
        pg.click("#replay"); pg.wait_for_timeout(300)
        if not pg.evaluate("() => document.documentElement.classList.contains('intro-on')"):
            fail(f"intro@{w}: replay did not reopen the film")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(1500)
        if not pg.evaluate("() => document.getElementById('intro').hidden"):
            fail(f"intro@{w}: Escape did not enter")
        ctx.close()
    # Without JavaScript the intro never blocks the page: it is only switched on by script.
    if 'class="intro-on"' in (DIST / "index.html").read_text():
        fail("intro: page ships with the intro forced on")

    # More of this: sends once, then stays marked.
    ctx = nc(viewport={"width": 390, "height": 844}, has_touch=True)
    pg = ctx.new_page(); pg.goto(f"{ORIGIN}/index.html", wait_until="networkidle")
    before = len(signals)
    b = pg.locator('.more[data-signal="alliance-davido"]')
    b.scroll_into_view_if_needed(); b.click(); pg.wait_for_timeout(400); b.click(); pg.wait_for_timeout(400)
    if b.get_attribute("aria-pressed") != "true":
        fail("signal: button not marked after tap")
    sent_now = signals[before:]
    if len(sent_now) != 1 or '"alliance-davido"' not in (sent_now[0] or ""):
        fail(f"signal: expected one request for alliance-davido, got {sent_now}")
    pg.reload(wait_until="networkidle")
    if pg.get_attribute('.more[data-signal="alliance-davido"]', "aria-pressed") != "true":
        fail("signal: not remembered after reload")
    # Map legend lights the right marker.
    pg.locator('.place[data-mk="kenya"]').scroll_into_view_if_needed()
    pg.click('.place[data-mk="kenya"]')
    if not pg.evaluate("() => document.querySelector('.mk-kenya').classList.contains('on') && document.querySelectorAll('.mk.on').length === 1"):
        fail("map: legend did not light the Kenya marker")
    ctx.close()

    # In The Room lightbox: opens, moves, closes, gives focus back.
    for w in (390, 1280):
        ctx = nc(viewport={"width": w, "height": 844}, has_touch=(w == 390))
        pg = ctx.new_page(); pg.goto(f"{ORIGIN}/in-the-room.html", wait_until="networkidle")
        first = pg.locator(".rm-open").first
        first.focus(); pg.keyboard.press("Enter"); pg.wait_for_timeout(500)
        st = pg.evaluate("() => { const d = document.getElementById('lb'); const i = document.getElementById('lb-img'); return {open: d.open, src: i.getAttribute('src'), ok: i.complete && i.naturalWidth > 0, count: d.querySelector('.lb-count').textContent}; }")
        if not st["open"] or not st["ok"] or not st["count"].startswith("01 /"):
            fail(f"lightbox@{w}: did not open {st}")
        pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(300)
        if not pg.evaluate("() => document.querySelector('.lb-count').textContent.startsWith('02 /')"):
            fail(f"lightbox@{w}: arrow key did not move")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
        st = pg.evaluate("() => ({open: document.getElementById('lb').open, back: document.activeElement.classList.contains('rm-open')})")
        if st["open"] or not st["back"]:
            fail(f"lightbox@{w}: close or focus return failed {st}")
        ctx.close()

    # In The Cup seat form: the Typeform embed is present, titled and sized.
    for w in (390, 1280):
        ctx = nc(viewport={"width": w, "height": 844}, has_touch=(w == 390))
        pg = ctx.new_page(); pg.goto(f"{ORIGIN}/in-the-cup.html", wait_until="networkidle")
        pg.locator("#seat .seat-embed").scroll_into_view_if_needed(); pg.wait_for_timeout(300)
        st = pg.evaluate("() => { const f = document.querySelector('#seat .seat-embed iframe'); if (!f) return null; const r = f.getBoundingClientRect(); return {src: f.src, title: f.title, h: Math.round(r.height), w: Math.round(r.width)}; }")
        if not st or not st["src"].startswith(ALLOWED_HOSTS) or not st["title"] or st["h"] < 500 or st["w"] < 280:
            fail(f"cup@{w}: seat embed missing or too small {st}")
        ctx.close()

    browser.close()

# Integrity: every internal reference resolves on disk.
for name in PAGES:
    html = (DIST / name).read_text()
    ids = set(re.findall(r'id="([^"]+)"', html))
    refs = re.findall(r'(?:href|src|poster|data-src-sm|data-src-lg)="([^"]+)"', html) + [u.split()[0] for s in re.findall(r'(?:srcset|imagesrcset)="([^"]+)"', html) for u in s.split(",")]
    for ref in refs:
        ref = ref.strip()
        if ref.startswith("#"):
            if ref[1:] not in ids:
                fail(f"{name}: anchor {ref} has no target")
        elif ref.startswith("http"):
            continue
        elif not (DIST / ref.split("#")[0].split("?")[0]).exists():
            fail(f"{name}: missing file {ref}")
    for m in re.findall(r'content="https://nasinthecut\.com/([^"]+)"', html):
        if not (DIST / m).exists():
            fail(f"{name}: meta points at missing file {m}")

# Icons: every file the manifest names exists and has the size it claims.
import json as _json
from PIL import Image as _Image
man = _json.loads((DIST / "site.webmanifest").read_text())
for ic in man["icons"]:
    f = DIST / ic["src"].lstrip("/")
    if not f.exists():
        fail(f"manifest icon missing {ic['src']}")
    elif ic["sizes"] != "any":
        w, h = _Image.open(f).size
        if f"{w}x{h}" != ic["sizes"]:
            fail(f"manifest icon {ic['src']} is {w}x{h}, claims {ic['sizes']}")
ico = _Image.open(DIST / "favicon.ico")
if not {(16, 16), (32, 32), (48, 48)} <= set(ico.info.get("sizes", set())):
    fail(f"favicon.ico sizes {ico.info.get('sizes')}")

for t in sorted(set(third_party)):
    fail(f"third party request {t}")
for e in sorted(set(console_errors)):
    fail(f"console error {e}")

srv.shutdown()
if findings:
    print(f"\nAUDIT FAILED: {len(findings)} findings")
    for f in findings:
        print("  " + f)
    sys.exit(1)
print(f"\nAUDIT PASSED: {len(PAGES)} page x {len(WIDTHS)} widths, zero findings")
