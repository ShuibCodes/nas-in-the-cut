"""Nas In The Cut: single source of truth for every word on the site.

Assembles flat HTML into dist/. Generated files are never edited by hand.
Hard gates run over everything before a single file is written.
"""
import gzip
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
BASE = "https://www.nasirhassan.com"
IG = "https://www.instagram.com/nasinthecut/"

# The email provider's POST endpoint. Empty means the form tells visitors to
# message him on Instagram instead. /api/subscribe is the Next.js Kit relay.
SUBSCRIBE_ENDPOINT = "/api/subscribe"

# Typeform shown in the In The Cup "Save your seat" section. Its host must stay
# in frame-src in HEADERS and src/htaccess.txt, and in ALLOWED_HOSTS in tools/audit.py.
SEAT_FORM_URL = "https://form.typeform.com/to/zGgTtYQH"

TITLE = "Nas In The Cut | The daily email on how the money actually gets made"
DESCRIPTION = ("A free daily email from Nasir Hassan in Dubai: how the deals really get done, from Dubai "
               "real estate to the companies he builds across Africa. Three minutes a day.")
OG_DESC = "The free daily email on how the money actually gets made. Issue #1 goes out to early readers."

# ---------------------------------------------------------------- content

HERO_LEDE = ("I build companies, I've raised millions, sold nine figures in Dubai real estate and founded "
             "the biggest training community in the city. This is how it actually works.")

ISSUES = [
    ("Routine", "3 min", "What I get done before 99% of people wake up",
     "Two hours, three decisions, no phone until the work is done.",
     ["The phone stays in another room until the first block is finished. Not on silent. In another room.",
      "Hour one goes to the single decision that moves money this week. Hour two goes to training, because a clear head closes better deals than a busy one.",
      "By the time most people open their inbox, my day is already decided. That is the whole trick, and it is the one most people skip."]),
    ("Gyms", "3 min", "How I'd open a gym on $50k, not $500k",
     "The equipment is the last thing you pay for. Here is what comes first.",
     ["Every first-time gym owner falls in love with the kit. The kit is the easy part.",
      "What comes first is the community: fifty people who would train with you in a car park. Then the lease terms. Then the coaches. Then, last, the equipment.",
      "Get the order right and you open with members already paying. Get it wrong and you open with a showroom."]),
    ("Real estate", "4 min", "The 'safe' property deal that nearly got me",
     "Everyone called it low risk. Here is what they missed.",
     ["On paper it was the easiest deal of the year. Good area, good developer, good numbers.",
      "Everyone in the room called it low risk. Nobody in the room had read the payment schedule properly. I nearly signed anyway.",
      "This issue is the checklist I use now, line by line, before any deal gets my signature."]),
]

RULES = [
    ("Everything comes to you at the right time. Be patient.", "On the long game"),
    ("Timing is everything. Execution is the key.", "On closing"),
    ("The best opportunities start as simple conversations with people you genuinely like.", "On deals"),
    ("People post the work. The biggest moves happen behind the simplest pictures.", "On noise"),
    ("Motivation is a Tuesday morning feeling. Systems are what still work on Thursday.", "On discipline"),
    ("Only those who can see the invisible can do the impossible.", "On vision"),
    ("Tomorrow we go again.", "On everything"),
]

# (big figure, counts up?, unit, label)
STATS = [
    ("$9+", False, "figures", "in Dubai real estate"),
    ("95", True, "countries", "travelled, and counting"),
    ("6", True, "African countries", "with offices"),
    ("365", True, "Collective", "the training community I founded"),
]

ALLIANCES = [
    ("davido-spiro", "Nasir Hassan with Davido at the Davido and Spiro partnership", "Davido",
     "The Davido and Spiro partnership, connected through Narrativ Africa.", "alliance-davido"),
    ("nas-mo-farah", "Nasir Hassan with Sir Mo Farah in a sunlit courtyard in the UAE", "Sir Mo Farah",
     "Four-time Olympic champion. Time together in the UAE.", "alliance-mo-farah"),
    ("bcn-handshake", "Nasir Hassan greeting the President of FC Barcelona", "The President of FC Barcelona",
     "Meetings in Barcelona, at the club and at the table.", "alliance-barcelona"),
]

OFFICES = [  # (marker key, label)
    ("cote-divoire", "Côte d'Ivoire"), ("gabon", "Gabon"), ("benin", "Benin"),
    ("rwanda", "Rwanda"), ("uganda", "Uganda"), ("kenya", "Kenya"),
]

LANDS = [
    ("The deal", "One real deal, broken down",
     "What it cost, what it made and the one call that decided it, always with the numbers attached. "
     "Plus what I'm watching this week in Dubai property, Africa and the companies I build."),
    ("The fail", "The fails, in full",
     "Everyone posts the exit. Nobody posts the spreadsheet from the year before. I post the spreadsheet."),
    ("The system", "The habits that hold",
     "What still works when the motivation is gone: how I plan the week, protect the mornings and make decisions fast."),
]

SHOTS = [
    ("collective-365", "Nasir Hassan leading a Collective 365 group run in Dubai", "The run"),
    ("collective-365-c", "Nasir Hassan in a circle huddle with Collective 365 members in Dubai", "The huddle"),
    ("collective-365-b", "Nasir Hassan with his arm raised, leading a Collective 365 session in Dubai", "The call"),
    ("collective-365-d", "A Collective 365 group running together through a Dubai street", "The street"),
]
SHOTS = [g for g in SHOTS if (SRC / "img" / "out" / f"{g[0]}-800.jpg").exists()]

# In The Room: (image, alt, place, story)
ROOM = [
    ("bcn-laugh", "Nasir Hassan sharing a laugh with the President of FC Barcelona", "Barcelona",
     "The part of the meeting you only get by being yourself."),
    ("davido-spiro", "Nasir Hassan with Davido", "Davido x Spiro",
     "Marking the Davido and Spiro partnership, connected through Narrativ Africa."),
    ("bcn-handshake", "Nasir Hassan greeting the President of FC Barcelona", "Barcelona",
     "With the President of FC Barcelona."),
    ("davido-backstage", "Nasir Hassan backstage with Davido in Dubai", "Dubai",
     "Backstage, the night Davido shut it down."),
    ("bcn-boardroom", "Nasir Hassan at a boardroom table in Barcelona", "Barcelona", "Around the table."),
    ("davido-lunch", "Nasir Hassan shaking hands with Davido across a lunch table", "Davido", "Lunch, and a handshake that meant something."),
    ("nas-mo-farah", "Nasir Hassan with Sir Mo Farah in the UAE", "UAE", "With Sir Mo Farah."),
    ("bcn-dinner", "Nasir Hassan at dinner with the President of FC Barcelona", "Barcelona",
     "Dinner with the President of FC Barcelona."),
    ("nas-terrace", "Nasir Hassan in a dark suit and tie in Barcelona", "Barcelona", "Between meetings."),
    ("bcn-training-ground", "Nasir Hassan at a desk overlooking football training pitches", "Barcelona",
     "Looking out over the training pitches."),
    ("collective-365", "Nasir Hassan leading a Collective 365 group run in Dubai", "Collective 365", "The run."),
    ("nas-sea-terrace", "Nasir Hassan seated on a terrace overlooking the sea in Dubai", "Dubai", "Home base."),
    ("cup-kokko", "Nasir Hassan having coffee outside Kokko cafe in Barcelona", "Barcelona", "The coffee spot comes first. Always."),
    ("collective-365-c", "Nasir Hassan in a circle huddle with Collective 365 members", "Collective 365", "The huddle."),
    ("collective-365-b", "Nasir Hassan leading a Collective 365 session", "Collective 365", "The call."),
    ("collective-365-d", "A Collective 365 group running through a Dubai street", "Collective 365", "Through the city."),
]
ROOM = [r for r in ROOM if (SRC / "img" / "out" / f"g-{r[0]}-640.jpg").exists()]

# In The Cup: the monthly coffee
CUP_TITLE = "In The Cup | Coffee with Nas, once a month"
CUP_DESC = ("Once a month, everyone in Nasir Hassan's world sits down for coffee: special guests, real questions, "
            "and one reader gets a one to one coffee with Nas.")
CUP_STEPS = [
    ("A new spot", "Somewhere special, every month. I'm a big fan of a great coffee spot. The location goes to readers first."),
    ("Special guests", "I bring a couple of people doing big things to the table. You hear from them and ask them your questions directly."),
    ("Your questions", "Bring your questions for me too, whether it's business, property, or building from the ground up."),
]
CUP_RULES = [
    ("Come as you are.", "No titles at the table."),
    ("No pitching.", "Connections first. Business follows."),
    ("Phones face down.", "Be in the room you're in."),
    ("Bring one real question.", "That's the price of the coffee."),
]
CUP_SHOTS = [
    ("cup-kokko", "Nasir Hassan having coffee outside Kokko cafe in Barcelona", "Barcelona"),
    ("cup-lounge", "Nasir Hassan in conversation with two guests around a low table in a hotel lounge", "Around the table"),
    ("cup-lobby", "Nasir Hassan standing in a bright mint coloured lobby", "Between meetings"),
]

MARKERS = json.loads((ROOT / "tools" / "markers.json").read_text())

# ---------------------------------------------------------------- helpers

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def picture(name, alt, sizes, eager=False):
    widths = [w for w in (480, 800, 1080) if (SRC / "img" / "out" / f"{name}-{w}.jpg").exists()]
    def srcset(ext):
        return ", ".join(f"img/{name}-{w}.{ext} {w}w" for w in widths)
    load = 'fetchpriority="high" loading="eager"' if eager else 'loading="lazy"'
    return (
        f'<picture>'
        f'<source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
        f'<img src="img/{name}-800.jpg" srcset="{srcset("jpg")}" sizes="{sizes}" '
        f'width="1080" height="1440" alt="{esc(alt)}" {load} decoding="async">'
        f'</picture>'
    )


def g_large(name):
    """Largest gallery rendition that exists for this photo."""
    return 1280 if (SRC / "img" / "out" / f"g-{name}-1280.jpg").exists() else 640


def gpicture(name, alt, sizes):
    """Gallery image at its natural shape."""
    from PIL import Image
    w, h = Image.open(SRC / "img" / "out" / f"g-{name}-640.jpg").size
    big = g_large(name)
    def srcset(ext):
        return f"img/g-{name}-640.{ext} 640w" + (f", img/g-{name}-1280.{ext} 1280w" if big == 1280 else "")
    return (
        f'<picture>'
        f'<source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
        f'<img src="img/g-{name}-640.jpg" srcset="{srcset("jpg")}" sizes="{sizes}" '
        f'width="{w}" height="{h}" alt="{esc(alt)}" loading="lazy" decoding="async">'
        f'</picture>'
    )


# The NAS wordmark (option 2b), redrawn in the site's silver. The node, cyan
# in the master files, takes the muted silver so it sits inside the palette.
NAS_PATHS = (
    '<g transform="translate(-13 -16)">'
    '<path fill-rule="evenodd" d="M13,16 L120.5,16 L271,264 L271,16 L336,16 L336,320 L229,320 L79,74 L79,320 L13,320 Z"/>'
    '<path fill-rule="evenodd" d="M532.5,16 L627.5,16 L761.3,320 L689.3,320 L664.2,263 L495.8,263 L470.7,320 L398.7,320 Z M580,71.7 L520.9,206 L639.1,206 Z"/>'
    '<path d="M808,76 A60,60 0 0 1 868,16 L1061,16 A54,54 0 0 1 1115,70 L1115,96 Q1115,104 1107,104 L1057,104 Q1049,104 1049,96 L1049,88 Q1049,72 1033,72 L896,72 Q880,72 880,88 L880,121 Q880,137 896,137 L1060,137 A60,60 0 0 1 1120,197 L1120,266 A54,54 0 0 1 1066,320 L862,320 A54,54 0 0 1 808,266 L808,239 Q808,231 816,231 L868,231 Q876,231 876,239 L876,248 Q876,264 892,264 L1033,264 Q1049,264 1049,248 L1049,209 Q1049,193 1033,193 L868,193 A60,60 0 0 1 808,133 Z"/>'
    '</g>'
)


def logo(cls="wm"):
    return (f'<svg class="{cls}" viewBox="0 0 1227 304" aria-hidden="true" focusable="false">'
            f'<g fill="currentColor">{NAS_PATHS}</g><circle class="node" cx="1195" cy="272" r="32"/></svg>')


WORDMARK = logo()

ARROW_L = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'
ARROW_R = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'
PLUS = '<svg class="pm" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5 12h14M12 5v14" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'
CLOSE = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'
SPEAKER = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 9.5h3.5L12 6v12l-4.5-3.5H4z" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>'
           '<path class="wave" d="M15.5 9.2a4 4 0 0 1 0 5.6M18 7a7 7 0 0 1 0 10" fill="none" stroke="currentColor" stroke-width="1.4"/>'
           '<path class="mute" d="M16 9.5l5 5M21 9.5l-5 5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>')


def signup(form_id, describe_id, button="Send me issue #1"):
    return f'''<form class="signup" id="{form_id}" action="#{form_id}" method="post" novalidate data-endpoint="{SUBSCRIBE_ENDPOINT}">
  <div class="row">
    <label class="vh" for="{form_id}-email">Email address</label>
    <input id="{form_id}-email" type="email" name="email" autocomplete="email" inputmode="email" enterkeyhint="send" required placeholder="Your email address" aria-describedby="{describe_id} {form_id}-msg">
    <button class="btn" type="submit">{button}</button>
  </div>
  <div class="hp" aria-hidden="true"><label for="{form_id}-web">Leave this empty</label><input id="{form_id}-web" type="text" name="website" tabindex="-1" autocomplete="off"></div>
  <p class="msg" id="{form_id}-msg" role="status" aria-live="polite"></p>
</form>'''


def terms(tid):
    return f'<p class="terms" id="{tid}">Free. One email a day. Unsubscribe in one click.</p>'


def more(signal, what):
    """The quiet 'More of this' signal. Counted privately, never shown."""
    return (f'<button class="more" type="button" data-signal="{signal}" aria-pressed="false">'
            f'<span class="more-a">More of this<span class="vh">: {esc(what)}</span></span>'
            f'<span class="more-b" aria-hidden="true">Noted. More coming.</span></button>')


def rail(rid, label, count):
    """Prev and next controls plus a live counter for a horizontal rail."""
    return f'''<div class="rail-ctl" data-for="{rid}">
  <p class="count" aria-live="polite"><span class="vh">{label} </span><span data-cur>01</span><span class="of"><span aria-hidden="true"> / {count:02d}</span><span class="vh"> of {count}</span></span></p>
  <div class="rail-line" aria-hidden="true"><span></span></div>
  <div class="arrows">
    <button class="arrow" type="button" data-dir="-1" aria-controls="{rid}" aria-disabled="true"><span class="vh">Previous</span>{ARROW_L}</button>
    <button class="arrow" type="button" data-dir="1" aria-controls="{rid}"><span class="vh">Next</span>{ARROW_R}</button>
  </div>
</div>'''


def header(kind):
    home = kind == "home"
    h = "" if home else "./"
    brand = "#top" if home else "./"
    cur = lambda k: ' aria-current="page"' if kind == k else ''
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-head" id="site-head">
  <div class="wrap">
    <a class="brand" href="{brand}"><span class="vh">Nas In The Cut, home</span>{WORDMARK}</a>
    <nav class="head-nav" aria-label="Main">
      <a class="hide-md" href="{h}#alliances">Alliances</a>
      <a class="hide-md" href="{h}#africa">Africa</a>
      <a class="hide-sm" href="in-the-room.html"{cur("room")}>In The Room</a>
      <a class="cup-link" href="in-the-cup.html"{cur("cup")}>In The Cup</a>
      <a class="sub-link" href="{h}#subscribe">Subscribe</a>
    </nav>
  </div>
  <div class="progress" aria-hidden="true"><span id="progress"></span></div>
</header>'''


def footer(kind):
    home = kind == "home"
    h = "" if home else "./"
    film = ('<button class="text-btn" type="button" id="replay">Play the film</button>' if home else '')
    return f'''<footer class="site-foot">
  <div class="wrap">
    <div class="top">
      <a class="brand" href="{'#top' if home else './'}"><span class="vh">Nas In The Cut, home</span>{WORDMARK}</a>
      <nav aria-label="Footer">
        <a href="{h}#subscribe">Subscribe</a>
        <a href="in-the-cup.html">In The Cup</a>
        <a href="in-the-room.html">In The Room</a>
        <a href="{IG}" rel="me noopener" target="_blank">Instagram<span class="vh"> (opens in a new tab)</span></a>
        {film}
      </nav>
    </div>
    <p class="privacy">Your email is used for one thing: sending you this newsletter and, if you ask, In The Cup invites. It isn't sold, shared or added to anything else, and every email has a one-click unsubscribe.</p>
    <p class="legal">&copy; 2026 Nas In The Cut. Real business. No filter.</p>
  </div>
</footer>'''


def intro():
    return f'''<div class="intro" id="intro" role="dialog" aria-modal="true" aria-label="Nas In The Cut, intro film">
  <div class="intro-blur" aria-hidden="true"></div>
  <video class="intro-film" id="intro-film" muted playsinline preload="none" poster="media/intro-poster.jpg"
    data-src-sm="media/intro-540.mp4" data-src-lg="media/intro-720.mp4" aria-hidden="true"></video>
  <div class="intro-shade" aria-hidden="true"></div>
  <audio id="intro-audio" preload="auto" src="media/intro-track.mp3"></audio>
  <div class="intro-mark">
    <picture><source type="image/webp" srcset="media/logo-nitc-640.webp 640w, media/logo-nitc-1200.webp 1200w" sizes="(min-width: 900px) 720px, 84vw">
    <img src="media/logo-nitc-640.png" srcset="media/logo-nitc-640.png 640w, media/logo-nitc-1200.png 1200w" sizes="(min-width: 900px) 720px, 84vw" width="1200" height="220" alt="Nas In The Cut"></picture>
    <p class="intro-line">How the money actually gets made.</p>
  </div>
  <button class="intro-sound" id="intro-sound" type="button" aria-pressed="false">{SPEAKER}<span class="lbl">Sound on</span></button>
  <button class="intro-enter" id="intro-enter" type="button">Enter {ARROW_R}</button>
  <div class="intro-time" aria-hidden="true"><span id="intro-time"></span></div>
</div>'''


def body_home():
    issues = "\n".join(f'''<li class="issue">
  <h3 class="issue-h"><button class="issue-btn" type="button" aria-expanded="false" aria-controls="issue-{i}-body" id="issue-{i}-btn">
    <span class="n" aria-hidden="true">{i:02d}</span>
    <span class="t"><span class="title">{esc(title)}</span><span class="teaser">{esc(teaser)}</span><span class="m">{esc(tag)} &middot; {esc(mins)}</span></span>
    {PLUS}
  </button></h3>
  <div class="issue-body" id="issue-{i}-body" role="region" aria-labelledby="issue-{i}-btn" hidden>
    <div class="issue-in">{"".join(f"<p>{esc(p)}</p>" for p in paras)}<p class="more-note">The full issue goes to subscribers.</p>{more(f"issue-{i}", title)}</div>
  </div>
</li>''' for i, (tag, mins, title, teaser, paras) in enumerate(ISSUES, 1))

    rules = "\n".join(f'''<li class="rule">
  <span class="rule-n" aria-hidden="true">{i:02d}</span>
  <blockquote><p>{esc(q)}</p></blockquote>
  <div class="rule-foot"><p class="rule-tag">{esc(tag)}</p>{more(f"rule-{i}", q)}</div>
</li>''' for i, (q, tag) in enumerate(RULES, 1))

    stats = "\n".join(f'''<li class="stat" data-reveal>
  <span class="vh">{esc(num)} {esc(unit)}, {esc(label)}</span>
  <span class="big" aria-hidden="true"><span{' data-count="' + num + '"' if count else ''}>{esc(num)}</span></span>
  <span class="unit" aria-hidden="true">{esc(unit)}</span>
  <span class="lab" aria-hidden="true">{esc(label)}</span>
</li>''' for num, count, unit, label in STATS)

    alliances = "\n".join(f'''<li class="ally">
  <figure>
    <div class="frame">{picture(img, alt, "(min-width: 1100px) 340px, (min-width: 700px) 44vw, 80vw")}</div>
    <figcaption><h3>{esc(name)}</h3><p>{esc(line)}</p></figcaption>
  </figure>
  {more(sig, name)}
</li>''' for img, alt, name, line, sig in ALLIANCES)

    markers = "\n".join(f'<span class="mk mk-{k}" data-mk="{k}" aria-hidden="true"></span>' for k in MARKERS)
    offices = "\n".join(f'<li><button class="place" type="button" data-mk="{k}" aria-pressed="false">{esc(label)}</button></li>'
                        for k, label in [("dubai", "Dubai")] + OFFICES)

    lands = "\n".join(f'''<div class="def" data-reveal>
  <dt>{esc(label)}</dt>
  <dd><h3>{esc(t)}</h3><p>{esc(d)}</p></dd>
</div>''' for label, t, d in LANDS)

    shots = "\n".join(f'''<li class="shot">
  <figure>
    <div class="frame">{picture(name, alt, "(min-width: 900px) 380px, 80vw")}</div>
    <figcaption>{esc(cap)}</figcaption>
  </figure>
</li>''' for name, alt, cap in SHOTS)

    teaser = [r for r in ROOM if r[0] in ("bcn-laugh", "davido-backstage", "bcn-dinner")]
    teaser_html = "\n".join(f'''<li><a class="tease" href="in-the-room.html"><span class="frame">{picture(img, alt, "(min-width: 900px) 300px, 30vw")}</span><span class="vh">{esc(place)}: {esc(story)}</span></a></li>'''
                            for img, alt, place, story in teaser if (SRC / "img" / "out" / f"{img}-800.jpg").exists())

    return f'''{intro()}
{header("home")}

<main id="main">
  <section class="hero" id="top" aria-labelledby="h-hero">
    <div class="wrap grid">
      <div class="hero-copy">
        <p class="kicker a1"><span class="clock" id="clock">Every morning at 7:00, Dubai time</span></p>
        <h1 id="h-hero" class="h1"><span class="ln"><span>How the money</span></span> <span class="ln"><span>actually gets</span></span> <span class="ln"><span>made.</span></span></h1>
        <p class="lede a3">{esc(HERO_LEDE)}</p>
        <div class="a4">
          {signup("subscribe", "terms-a")}
          {terms("terms-a")}
        </div>
      </div>
      <figure class="hero-photo a5">
        <div class="frame">{picture("nas-terrace", "Nasir Hassan in a dark suit and tie on a city street in Barcelona", "(min-width: 900px) 440px, 92vw", eager=True)}</div>
        <figcaption>Nasir Hassan, Barcelona</figcaption>
      </figure>
    </div>
  </section>

  <section class="stats" aria-labelledby="h-stats">
    <div class="wrap">
      <h2 id="h-stats" class="vh">In numbers</h2>
      <ul class="stat-grid">
{stats}
      </ul>
    </div>
  </section>

  <section class="alliances" id="alliances" aria-labelledby="h-alliances">
    <div class="wrap cols">
      <p class="side">Strategic alliances</p>
      <div>
        <h2 id="h-alliances" class="big-line" data-reveal>I do my best work in rooms with the most senior people. By being myself.</h2>
      </div>
    </div>
    <div class="wrap">
      <ul class="rail ally-rail" id="ally-rail" data-hscroll tabindex="0" aria-label="Alliances, scrolls sideways">
{alliances}
      </ul>
      {rail("ally-rail", "Alliance", len(ALLIANCES))}
      <p class="private" data-reveal>Some of the most important relationships stay private. That is the point.</p>
    </div>
  </section>

  <section class="africa" id="africa" aria-labelledby="h-africa">
    <div class="wrap cols">
      <p class="side">Africa</p>
      <div class="africa-copy" data-reveal>
        <h2 id="h-africa">Offices in six African countries.</h2>
        <p>Côte d'Ivoire, Gabon, Benin, Rwanda, Uganda and Kenya, run from Dubai. I build companies alongside the business leaders and governments shaping the continent.</p>
      </div>
    </div>
    <div class="wrap">
      <figure class="map" data-reveal>
        <div class="map-head">
          <p class="map-big"><span data-count="95">95</span></p>
          <p class="map-cap">countries travelled.<br>Offices in six.</p>
        </div>
        <div class="map-art"><div class="map-in">
          <img src="img/world-dots.svg" width="1000" height="470" alt="World map marking Dubai and offices in Côte d'Ivoire, Gabon, Benin, Rwanda, Uganda and Kenya" loading="lazy" decoding="async">
{markers}
        </div></div>
        <figcaption>
          <ul class="places" aria-label="Offices and base">
{offices}
          </ul>
        </figcaption>
      </figure>
    </div>
  </section>

  <section class="statement" aria-label="Why I write">
    <div class="wrap cols">
      <p class="side">Why I write</p>
      <div>
        <p class="big-line" data-reveal>Most of the journey happens quietly.</p>
        <p class="body-copy" data-reveal>The early mornings, the deals that nearly broke me, the sacrifices nobody posts. Then one day you look around and it has all been worth it. This is where I write that part down, every morning, for the people who are still in the quiet part.</p>
      </div>
    </div>
  </section>

  <section id="issues" aria-labelledby="h-issues">
    <div class="wrap cols">
      <p class="side">Already written</p>
      <div>
        <h2 id="h-issues" data-reveal>The first three issues</h2>
        <p class="sub" data-reveal>Open any issue to read how it starts.</p>
        <ol class="contents" data-reveal>
{issues}
        </ol>
        <p class="fine">Three minutes each. Written before 7am, sent as is.</p>
      </div>
    </div>
  </section>

  <section class="rules" id="rules" aria-labelledby="h-rules">
    <div class="wrap cols">
      <p class="side">The rules</p>
      <div class="rules-head">
        <h2 id="h-rules" data-reveal>Seven rules I run on.</h2>
        <p class="sub" data-reveal>Swipe through. Tap the ones you want more of.</p>
      </div>
    </div>
    <div class="wrap">
      <ol class="rail rule-rail" id="rule-rail" data-hscroll tabindex="0" aria-label="Seven rules, scrolls sideways">
{rules}
      </ol>
      {rail("rule-rail", "Rule", len(RULES))}
    </div>
  </section>

  <section class="about" id="about" aria-labelledby="h-about">
    <div class="wrap cols">
      <p class="side">Who's writing</p>
      <div class="about-grid">
        <figure class="photo" data-reveal>
          <div class="frame">{picture("nas-sea-terrace" if (SRC / "img" / "out" / "nas-sea-terrace-800.jpg").exists() else "nas-mo-farah", "Nasir Hassan seated on a terrace overlooking the sea in Dubai", "(min-width: 900px) 340px, 92vw")}</div>
          <figcaption>Dubai</figcaption>
        </figure>
        <div class="about-copy" data-reveal>
          <h2 id="h-about">I build. I invest. I write it down.</h2>
          <p class="first">I came to the UK as a kid, from a country at war. Everything since has been built one early morning at a time.</p>
          <p>I build companies across Africa and the Gulf, I've raised millions, sold nine figures in real estate, and I back creative businesses from Dubai.</p>
          <p>Some of it worked. Some of it cost me money I'd rather not name in a headline. This newsletter is the part I never used to share: the actual decisions, the actual numbers, the morning after.</p>
          <p class="sign" aria-hidden="true">{logo("sig")}</p>
        </div>
      </div>
    </div>
  </section>

  <section id="what-lands" aria-labelledby="h-lands">
    <div class="wrap cols">
      <p class="side">In every issue</p>
      <div>
        <h2 id="h-lands" data-reveal>Three minutes. One decision.</h2>
        <dl class="defs">
{lands}
        </dl>
      </div>
    </div>
  </section>

  <section class="collective" id="collective-365" aria-labelledby="h-collective">
    <div class="wrap cols">
      <p class="side">Collective 365</p>
      <div class="c-copy" data-reveal>
        <h2 id="h-collective">Founders in the room next to fighters.</h2>
        <p>I founded Collective 365, and it has become the biggest training community in Dubai. Twice a week we train together before the day starts. No titles and no pitching. You show up, you do the work, and tomorrow we go again.</p>
        <a class="text-link" href="{IG}" rel="me noopener" target="_blank">See Collective 365 on Instagram<span class="vh"> (opens in a new tab)</span></a>
      </div>
    </div>
    <div class="wrap">
      <ul class="rail shot-rail" id="shot-rail" data-hscroll tabindex="0" aria-label="Collective 365 photos, scrolls sideways">
{shots}
      </ul>
      {rail("shot-rail", "Photo", len(SHOTS))}
      <div class="c-more">{more("collective-365", "Collective 365")}</div>
    </div>
  </section>

  <section class="cup-tease" id="in-the-cup" aria-labelledby="h-cup">
    <div class="wrap cols">
      <p class="side">In The Cup</p>
      <div class="cup-tease-grid">
        <div class="cup-tease-copy" data-reveal>
          <h2 id="h-cup">Coffee with Nas. Once a month.</h2>
          <p>Everyone in my world, one table, somewhere special. A couple of special guests, real questions, real connections. And every month, one reader gets a coffee with me, one to one.</p>
          <a class="btn" href="in-the-cup.html">Pull up a chair {ARROW_R}</a>
        </div>
        <figure class="cup-tease-art" data-reveal>
          <div class="wide">{gpicture("cup-latte", "A cappuccino with NAS IN THE CUT drawn in the foam", "(min-width: 900px) 520px, 92vw")}</div>
        </figure>
      </div>
    </div>
  </section>

  <section class="room-tease" aria-labelledby="h-tease">
    <div class="wrap cols">
      <p class="side">In The Room</p>
      <div data-reveal>
        <h2 id="h-tease">The people, the places, the moments.</h2>
        <ul class="tease-grid">
{teaser_html}
        </ul>
        <a class="btn btn-ghost" href="in-the-room.html">Enter In The Room {ARROW_R}</a>
      </div>
    </div>
  </section>

  <section class="final" id="join" aria-labelledby="h-final">
    <div class="wrap">
      <p class="kicker" data-reveal><span id="clock-2">The next issue lands at 7:00, Dubai time</span></p>
      <h2 id="h-final" data-reveal>Read one. Then decide.</h2>
      <p class="final-sub" data-reveal>If it's not worth three minutes, unsubscribe. I won't be offended.</p>
      {signup("subscribe-2", "terms-b")}
      {terms("terms-b")}
    </div>
  </section>
</main>

{footer("home")}

<div class="dock" id="dock" aria-hidden="true" inert>
  <a class="btn dock-btn" href="#join">Get issue #1, free</a>
</div>'''


def body_room():
    items = "\n".join(f'''<li class="rm">
  <figure>
    <button class="rm-open" type="button" data-i="{i}" aria-label="Open full screen: {esc(place)}, {esc(story)}">{gpicture(img, alt, "(min-width: 1100px) 520px, (min-width: 700px) 46vw, 100vw")}</button>
    <figcaption><span class="rm-place">{esc(place)}</span> <span class="rm-story">{esc(story)}</span></figcaption>
  </figure>
  {more("room-" + img, place + ", " + story)}
</li>''' for i, (img, alt, place, story) in enumerate(ROOM))
    data = json.dumps([{"src": f"img/g-{img}-{g_large(img)}.jpg", "alt": alt, "cap": f"{place}. {story}"} for img, alt, place, story in ROOM],
                      separators=(",", ":"))
    return f'''{header("room")}

<main id="main">
  <section class="room-hero" id="top" aria-labelledby="h-room">
    <div class="wrap">
      <p class="kicker a1">{len(ROOM)} frames</p>
      <h1 id="h-room" class="h1"><span class="ln"><span>In The Room.</span></span></h1>
      <p class="lede a3">The people, the places and the moments behind the work. Tap any frame to see it full screen.</p>
    </div>
  </section>

  <section class="room" aria-label="Frames">
    <div class="wrap">
      <ul class="rm-grid">
{items}
      </ul>
    </div>
  </section>

  <section class="final" id="join" aria-labelledby="h-final">
    <div class="wrap">
      <h2 id="h-final" data-reveal>The rest goes in the email.</h2>
      <p class="final-sub" data-reveal>One real deal and the numbers behind it, every morning at 7:00, Dubai time.</p>
      <a class="btn" href="./#subscribe">Get issue #1, free</a>
    </div>
  </section>
</main>

{footer("room")}

<dialog class="lb" id="lb" aria-label="Full screen photo">
  <figure class="lb-fig" id="lb-fig"><figcaption id="lb-cap"></figcaption></figure>
  <button class="lb-btn lb-prev" type="button" data-dir="-1"><span class="vh">Previous photo</span>{ARROW_L}</button>
  <button class="lb-btn lb-next" type="button" data-dir="1"><span class="vh">Next photo</span>{ARROW_R}</button>
  <button class="lb-btn lb-close" type="button"><span class="vh">Close</span>{CLOSE}</button>
  <p class="lb-count" aria-live="polite"></p>
</dialog>
<script type="application/json" id="room-data">{data}</script>'''


def cup_form():
    return '''<form class="cup-form" id="cup-form" action="cup.php" method="post" novalidate>
  <div class="field">
    <label for="cup-name">Your name</label>
    <input id="cup-name" name="name" type="text" autocomplete="name" required maxlength="80" aria-describedby="cup-msg">
  </div>
  <div class="field">
    <label for="cup-email">Email</label>
    <input id="cup-email" name="email" type="email" autocomplete="email" inputmode="email" required maxlength="120" aria-describedby="cup-msg">
  </div>
  <fieldset class="field mode" id="cup-mode">
    <legend>How you'll join</legend>
    <div class="choices">
      <label class="choice"><input type="radio" name="mode" value="in-person" id="cup-mode-in" required> <span>In person</span></label>
      <label class="choice"><input type="radio" name="mode" value="online" id="cup-mode-online"> <span>Online</span></label>
    </div>
  </fieldset>
  <div class="field">
    <label for="cup-question">Your question for Nas <span class="opt">(optional)</span></label>
    <textarea id="cup-question" name="question" rows="3" maxlength="400"></textarea>
  </div>
  <label class="tick" for="cup-121"><input type="checkbox" id="cup-121" name="one_to_one" value="yes"> <span>Put me forward for a one to one coffee with Nas</span></label>
  <div class="hp" aria-hidden="true"><label for="cup-web">Leave this empty</label><input id="cup-web" type="text" name="website" tabindex="-1" autocomplete="off"></div>
  <button class="btn" type="submit">Pull up a chair</button>
  <p class="msg" id="cup-msg" role="status" aria-live="polite"></p>
  <p class="terms">Used only for In The Cup invites. Never sold or shared.</p>
</form>'''


def body_cup():
    steps = "\n".join(f'<li class="step" data-reveal><span class="n" aria-hidden="true">{i:02d}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></li>'
                      for i, (t, d) in enumerate(CUP_STEPS, 1))
    rules = "\n".join(f'<li><span class="r">{esc(r)}</span> <span class="w">{esc(w)}</span></li>' for r, w in CUP_RULES)
    shots = "\n".join(f'<li class="shot"><figure><div class="frame">{picture(img, alt, "(min-width: 900px) 340px, 78vw")}</div><figcaption>{esc(cap)}</figcaption></figure></li>'
                      for img, alt, cap in CUP_SHOTS)
    return f'''{header("cup")}

<main id="main">
  <section class="cup-hero" id="top" aria-labelledby="h-cup-page">
    <div class="wrap cup-hero-grid">
      <div class="cup-hero-copy">
        <p class="kicker a1">Once a month</p>
        <h1 id="h-cup-page" class="h1"><span class="ln"><span>In The Cup.</span></span></h1>
        <p class="lede a3">Once a month, everyone in my world sits down for coffee. One special spot, a couple of special guests, and real conversations with people building real things.</p>
        <div class="a4"><a class="btn" href="#seat">Pull up a chair</a></div>
      </div>
      <figure class="cup-hero-art a5">
        <div class="wide">{gpicture("cup-latte-close", "A cappuccino with NAS IN THE CUT drawn in the foam", "(min-width: 900px) 560px, 100vw")}</div>
      </figure>
    </div>
  </section>

  <section class="cup-why" aria-labelledby="h-why">
    <div class="wrap cols">
      <p class="side">The table</p>
      <div>
        <h2 id="h-why" class="big-line" data-reveal>A space for everyone in my world to meet.</h2>
        <p class="body-copy" data-reveal>In The Cup is where the people around me meet each other. Founders, investors, readers and the Collective 365 crew. You network, you build real connections with each other, and you leave knowing people worth knowing.</p>
      </div>
    </div>
  </section>

  <section class="cup-steps" aria-labelledby="h-steps">
    <div class="wrap cols">
      <p class="side">Every month</p>
      <div>
        <h2 id="h-steps" data-reveal>How it works.</h2>
        <ol class="steps">
{steps}
        </ol>
      </div>
    </div>
  </section>

  <section class="one2one" aria-labelledby="h-121">
    <div class="wrap cols">
      <p class="side">Coffee with Nas</p>
      <div class="one2one-grid">
        <div class="one2one-copy" data-reveal>
          <h2 id="h-121">One reader. One coffee. Every month.</h2>
          <p>Every month I sit down with one reader, one to one. Face to face if you can make it in person, online if you're anywhere else in the world.</p>
          <p>Your coffee, your questions. Business, property, building from the ground up, or the thing you haven't told anyone yet.</p>
        </div>
        <div class="rules-box" data-reveal>
          <h3>House rules</h3>
          <ol class="cup-rules">
{rules}
          </ol>
        </div>
      </div>
    </div>
  </section>

  <section class="cup-photos" aria-label="Coffee and conversations">
    <div class="wrap">
      <ul class="rail shot-rail" id="cup-rail" data-hscroll tabindex="0" aria-label="Photos, scrolls sideways">
{shots}
      </ul>
      {rail("cup-rail", "Photo", len(CUP_SHOTS))}
    </div>
  </section>

  <section class="seat" id="seat" aria-labelledby="h-seat">
    <div class="wrap cols">
      <p class="side">Pull up a chair</p>
      <div>
        <h2 id="h-seat" data-reveal>Save your seat.</h2>
        <p class="sub" data-reveal>Tell me who you are and how you'll join. Table details reach you before anyone else.</p>
        <div class="seat-embed"><iframe src="{SEAT_FORM_URL}#utm_source=in-the-cup" title="Save your seat with Nas" loading="lazy" allow="clipboard-write"></iframe></div>
        <div class="seat-more">{more("in-the-cup", "In The Cup")}</div>
      </div>
    </div>
  </section>

  <section class="final" id="join" aria-labelledby="h-final">
    <div class="wrap">
      <h2 id="h-final" data-reveal>Invites go out in the email first.</h2>
      <p class="final-sub" data-reveal>The daily email gets the date and the spot before anyone else. Three minutes a day, every morning at 7:00, Dubai time.</p>
      <a class="btn" href="./#subscribe">Get issue #1, free</a>
    </div>
  </section>
</main>

{footer("cup")}'''


PERSON = {
    "@type": "Person", "@id": f"{BASE}/#nas", "name": "Nasir Hassan",
    "alternateName": ["Nas", "Nas In The Cut"], "url": f"{BASE}/",
    "image": f"{BASE}/img/nas-terrace-800.jpg",
    "description": ("Founder and investor based in Dubai. Builds companies with offices in six African countries, "
                    "has sold nine figures in Dubai real estate and founded Collective 365, the biggest training community in Dubai."),
    "homeLocation": {"@type": "Place", "name": "Dubai, United Arab Emirates"},
    "knowsAbout": ["Dubai real estate", "Building companies in Africa", "Strategic partnerships", "Founder habits"],
    "sameAs": [IG],
}


def jsonld(kind):
    graph = [
        {"@type": "WebSite", "@id": f"{BASE}/#website", "url": f"{BASE}/", "name": "Nas In The Cut",
         "description": OG_DESC, "inLanguage": "en", "publisher": {"@id": f"{BASE}/#nas"}},
        PERSON,
    ]
    if kind == "home":
        graph.append({"@type": "WebPage", "@id": f"{BASE}/#page", "url": f"{BASE}/", "name": TITLE,
                      "description": DESCRIPTION, "isPartOf": {"@id": f"{BASE}/#website"}, "about": {"@id": f"{BASE}/#nas"},
                      "primaryImageOfPage": {"@type": "ImageObject", "url": f"{BASE}/img/og.jpg", "width": 1200, "height": 630}})
    elif kind == "cup":
        graph.append({"@type": "WebPage", "@id": f"{BASE}/in-the-cup.html#page", "url": f"{BASE}/in-the-cup.html",
                      "name": CUP_TITLE, "description": CUP_DESC, "isPartOf": {"@id": f"{BASE}/#website"},
                      "about": {"@id": f"{BASE}/#nas"},
                      "primaryImageOfPage": {"@type": "ImageObject", "url": f"{BASE}/img/og-cup.jpg", "width": 1200, "height": 630}})
    else:
        graph.append({"@type": "ImageGallery", "@id": f"{BASE}/in-the-room.html#page", "url": f"{BASE}/in-the-room.html",
                      "name": ROOM_TITLE, "description": ROOM_DESC, "isPartOf": {"@id": f"{BASE}/#website"},
                      "about": {"@id": f"{BASE}/#nas"}})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, separators=(",", ":"))


ROOM_TITLE = "In The Room | Nas In The Cut, photos and stories from Nasir Hassan"
ROOM_DESC = ("Photos and short stories from Nasir Hassan: Barcelona, Davido, Sir Mo Farah, Collective 365 "
             "and the rooms behind the work.")


def page(kind, css_file, js_file, gate_file):
    home = kind == "home"
    meta = {
        "home": (TITLE, DESCRIPTION, f"{BASE}/", "Nas In The Cut", OG_DESC, "og.jpg",
                 "Nas In The Cut: how the money actually gets made"),
        "room": (ROOM_TITLE, ROOM_DESC, f"{BASE}/in-the-room.html", "In The Room | Nas In The Cut", ROOM_DESC, "og.jpg",
                 "Nas In The Cut: how the money actually gets made"),
        "cup": (CUP_TITLE, CUP_DESC, f"{BASE}/in-the-cup.html", "In The Cup | Coffee with Nas", CUP_DESC, "og-cup.jpg",
                "In The Cup: coffee with Nas, once a month"),
    }
    title, desc, url, og_title, og_desc, og_img, og_alt = meta[kind]
    body = {"home": body_home, "room": body_room, "cup": body_cup}[kind]()
    preload = ('<link rel="preload" as="image" type="image/avif" imagesrcset="img/nas-terrace-480.avif 480w, '
               'img/nas-terrace-800.avif 800w, img/nas-terrace-1080.avif 1080w" imagesizes="(min-width: 900px) 440px, 92vw">'
               if home else "")
    gate = f'<script src="{gate_file}"></script>' if home else ""
    return f'''<!doctype html>
<html lang="en"{'' if home else ' class="ready"'}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0b1422">
<meta name="author" content="Nasir Hassan">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Nas In The Cut">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(og_title)}">
<meta property="og:description" content="{esc(og_desc)}">
<meta property="og:image" content="{BASE}/img/{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(og_alt)}">
<meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(og_title)}">
<meta name="twitter:description" content="{esc(og_desc)}">
<meta name="twitter:image" content="{BASE}/img/{og_img}">
<link rel="icon" href="favicon.ico" sizes="48x48">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="icon-32.png" type="image/png" sizes="32x32">
<link rel="icon" href="icon-16.png" type="image/png" sizes="16x16">
<link rel="apple-touch-icon" href="apple-touch-icon.png" sizes="180x180">
<meta name="apple-mobile-web-app-title" content="NAS">
<meta name="application-name" content="NAS">
<meta name="color-scheme" content="dark">
<meta name="format-detection" content="telephone=no">
<link rel="manifest" href="site.webmanifest">
{preload}
<link rel="stylesheet" href="{css_file}">
{gate}
<script type="application/ld+json">{jsonld(kind)}</script>
</head>
<body class="is-{kind}">
{body}
<script src="{js_file}" defer></script>
</body>
</html>
'''

# ---------------------------------------------------------------- extras

ROBOTS = f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n"
SITEMAP = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{BASE}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>
  <url><loc>{BASE}/in-the-cup.html</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>{BASE}/in-the-room.html</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>
</urlset>
'''
LLMS = f"""# Nas In The Cut

> A free daily email from Nasir Hassan (Nas), a founder and investor based in Dubai.
> Each issue takes three minutes: one real deal with the numbers, one real mistake, and the habits that hold up.

## About the author
- Nasir Hassan, known as Nas, based in Dubai, United Arab Emirates.
- Builds companies, with offices in Cote d'Ivoire, Gabon, Benin, Rwanda, Uganda and Kenya.
- Has raised millions and sold nine figures in Dubai real estate.
- Built gym businesses from the ground up and invests in creative businesses.
- Has travelled to 95 countries.
- Athlete. Founded Collective 365, the biggest training community in Dubai, which trains together twice a week.
- Instagram: {IG}

## In The Cup
- Once a month, readers, founders, investors and the Collective 365 crew meet for coffee somewhere special.
- Special guests join the table and take questions. Readers bring questions for Nas too.
- Every month one reader is picked for a one to one coffee with Nas, in person or online.

## What the newsletter covers
- Real deals broken down: cost, return and the decision that mattered.
- Failures in full, with the numbers.
- Habits and systems for founders.

## Links
- Home and sign-up: {BASE}/
- In The Cup, the monthly coffee: {BASE}/in-the-cup.html
- Photos and stories: {BASE}/in-the-room.html
"""
MANIFEST = json.dumps({
    "name": "Nas In The Cut", "short_name": "NAS", "start_url": "/", "scope": "/", "display": "standalone",
    "background_color": "#0b1422", "theme_color": "#0b1422",
    "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
              {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
              {"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"}],
}, indent=2)
N_PATH = "M13,16 L120.5,16 L271,264 L271,16 L336,16 L336,320 L229,320 L79,74 L79,320 L13,320 Z"
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="Nas In The Cut">'
           '<rect width="512" height="512" fill="#0b1422"/>'
           f'<g transform="translate(74 131) scale(.82) translate(-13 -16)"><path d="{N_PATH}" fill="#f1f4f8"/></g>'
           '<circle cx="411" cy="354" r="26" fill="#a9b4c5"/></svg>')
HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self' https:; form-action 'self' https:; frame-src https://form.typeform.com; base-uri 'self'; frame-ancestors 'none'
/assets/*
  Cache-Control: public, max-age=31536000, immutable
/img/*
  Cache-Control: public, max-age=31536000, immutable
"""

# ---------------------------------------------------------------- gates

BANNED_CHARS = {"—": "em dash", "–": "en dash", "…": "ellipsis",
                " ": "non breaking space", "​": "zero width space"}
BANNED_MARKERS = ["[CONFIRM", "lorem ipsum", "TODO", "FIXME", "XXX", "PLACEHOLDER"]


def gate(files):
    problems = []
    for name, text in files.items():
        for ch, label in BANNED_CHARS.items():
            if ch in text:
                problems.append(f"{name}: contains {label}")
        # Uppercase markers match case-sensitively so the HTML placeholder
        # attribute and ::placeholder selector do not trip the gate.
        for m in BANNED_MARKERS:
            hit = (m.lower() in text.lower()) if m.islower() else (m in text)
            if hit:
                problems.append(f"{name}: unresolved marker {m}")
    return problems


def smart_quotes(html):
    """Typographic apostrophes and quotes in visible text only (never in tags, scripts or styles)."""
    out, pos = [], 0
    for m in re.finditer(r"<script\b.*?</script>|<style\b.*?</style>|<[^>]+>", html, re.S):
        text = html[pos:m.start()]
        text = re.sub(r"(\w)'(\w)", "\\1\u2019\\2", text)
        text = re.sub(r"(^|[\s(])'(?=\w)", "\\1\u2018", text)
        text = text.replace("'", "\u2019")
        out.append(text); out.append(m.group(0)); pos = m.end()
    out.append(html[pos:])
    return "".join(out)


def hashed(name, text):
    h = hashlib.sha256(text.encode()).hexdigest()[:10]
    stem, ext = name.rsplit(".", 1)
    return f"assets/{stem}.{h}.{ext}"


def marker_css():
    """Office marker positions as CSS classes, so the page needs no inline styles."""
    return "\n".join(f".mk-{k} {{ left: {x}%; top: {y}%; }}" for k, (x, y) in MARKERS.items()) + "\n"


def main():
    css = (SRC / "styles.css").read_text() + "\n/* Generated: office markers */\n" + marker_css()
    js = (SRC / "app.js").read_text()
    gate_js = (SRC / "intro-gate.js").read_text()
    css_file, js_file, gate_file = hashed("styles.css", css), hashed("app.js", js), hashed("intro.js", gate_js)
    home = smart_quotes(page("home", css_file, js_file, gate_file))
    room = smart_quotes(page("room", css_file, js_file, gate_file))
    cup = smart_quotes(page("cup", css_file, js_file, gate_file))

    files = {"index.html": home, "in-the-room.html": room, "in-the-cup.html": cup, css_file: css, js_file: js, gate_file: gate_js,
             "robots.txt": ROBOTS, "sitemap.xml": SITEMAP, "llms.txt": LLMS, "site.webmanifest": MANIFEST,
             "favicon.svg": FAVICON, "_headers": HEADERS,
             ".htaccess": (SRC / "htaccess.txt").read_text(),
             "signal.php": (SRC / "php" / "signal.php").read_text(),
             "stats.php": (SRC / "php" / "stats.php").read_text(),
             "cup.php": (SRC / "php" / "cup.php").read_text(),
             "data/.htaccess": "Require all denied\n"}
    problems = gate(files)
    if problems:
        print("BUILD REFUSED")
        for p in problems:
            print("  " + p)
        sys.exit(1)

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    (DIST / "data").mkdir()
    for name, text in files.items():
        (DIST / name).write_text(text)
    shutil.copytree(SRC / "img" / "out", DIST / "img")
    shutil.copy(SRC / "img" / "world-dots.svg", DIST / "img" / "world-dots.svg")
    shutil.copytree(SRC / "media" / "out", DIST / "media")
    for extra in ["og.jpg", "og-cup.jpg"]:
        if (SRC / "img" / extra).exists():
            shutil.copy(SRC / "img" / extra, DIST / "img" / extra)
    for extra in ["favicon.ico", "apple-touch-icon.png", "icon-16.png", "icon-32.png", "icon-192.png", "icon-512.png", "icon-maskable-512.png"]:
        if (SRC / extra).exists():
            shutil.copy(SRC / extra, DIST / extra)

    gz = sum(len(gzip.compress(files[n].encode(), 9)) for n in ["index.html", css_file, js_file, gate_file])
    print(f"built {len(files)} text files; home + css + js = {gz/1024:.1f} KB gzipped")


if __name__ == "__main__":
    main()
