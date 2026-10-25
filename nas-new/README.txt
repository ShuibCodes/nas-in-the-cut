NAS IN THE CUT  |  nasinthecut.com
Developer handover, A to Z
Version 7 (In The Cup), handed over 13 October 2026
Owner of the build: Ray (r.miah9124@gmail.com). Client: Nasir Hassan ("Nas"), Dubai.

Read this file top to bottom once. Every section is short. Section Q is the list
of work that is still open, in priority order. Everything else explains how the
site works so you can finish that list without breaking anything.


==============================================================================
CONTENTS
==============================================================================
 A. What the site is
 B. What is in this zip (and the second zip)
 C. Stack and design decisions (read before changing anything)
 D. Folder map
 E. Set up a machine
 F. Build, step by step
 G. The build gate (why the build can refuse)
 H. The audit (the quality gate)
 I. Editing content
 J. Frontend behaviour, feature by feature
 K. Backend: what exists today
 L. Data files and their exact shape
 M. The private stats page
 N. Hosting: Hostinger, .htaccess, deploy and update
 O. Security, privacy and the Content Security Policy
 P. Testing the backend locally
 Q. WHAT IS LEFT TO COMPLETE (the backend to-do list)
 R. Content still waiting on Nas
 S. House rules for this project
 T. Quick reference


==============================================================================
A. WHAT THE SITE IS
==============================================================================
Nas In The Cut is a free daily business email by Nasir Hassan, a Dubai founder
and investor. The site has one job: get people onto that email list. It also
shows who Nas is and runs a monthly coffee meetup called In The Cup.

Three pages:
  index.html          Home. Intro film, sign-up, issues, rules, numbers,
                      alliances, Africa map, Collective 365, In The Cup teaser.
  in-the-room.html    Photo gallery with one-line stories and a full screen viewer.
                      Short link: /in-the-room
  in-the-cup.html     In The Cup: the monthly coffee. "Save your seat" form.
                      Short link: /in-the-cup

Live domain: https://nasinthecut.com (bare domain, https, www redirects to it).
Hosting: Hostinger shared hosting (LiteSpeed, Apache compatible, PHP available).
Instagram: https://www.instagram.com/nasinthecut/


==============================================================================
B. WHAT IS IN THIS ZIP (AND THE SECOND ZIP)
==============================================================================
nasinthecut-v7-source.zip   (this one)
  Everything needed to rebuild the site from scratch: the builder, styles,
  scripts, PHP, original photos, original film and song, and all the tools.
  Generated files (resized photos, encoded film, dist/) are left out to keep it
  small. Section F rebuilds them in about two minutes.

nasinthecut-v7-hostinger.zip   (sent separately)
  The finished, built website exactly as it is on the server. Use it as the
  reference for "what correct output looks like", or to restore the live site.


==============================================================================
C. STACK AND DESIGN DECISIONS (READ BEFORE CHANGING ANYTHING)
==============================================================================
1. Static site from ONE Python file. build.py holds every word on the site and
   writes plain HTML into dist/. There is no framework, no npm build, no CMS.
   Edit copy in build.py, never in dist/.
2. Vanilla JavaScript (src/app.js), one CSS file (src/styles.css). System fonts
   only. No web fonts, no analytics, no third party requests of any kind. The
   audit fails the build if a page calls another domain.
3. CSS and JS file names carry a content hash (styles.4d0e5da72b.css), so they
   can be cached for a year and every update is picked up at once.
4. Strict Content Security Policy: no inline scripts and no inline styles.
   That is why map marker positions are generated into the CSS, and the intro
   check runs from its own small file. Keep it that way (see section O).
5. Backend is three small PHP files that write JSON files into a private data/
   folder. No database. That is deliberate for a launch on shared hosting, and
   fine for thousands of rows. Section Q says when to move to a database.
6. Mobile first. Tested at 10 widths from 320 to 1600 pixels.


==============================================================================
D. FOLDER MAP
==============================================================================
README.txt                 This file.
HANDOVER.md                Version history v4 to v7 with the reasons for each change.
requirements.txt           Python packages.
build.py                   THE BUILDER. All copy, all page structure, the build gate.
claude-design-brand-prompt.md   Old brief used for the logo work. Reference only.

src/
  styles.css               All styles. Palette tokens at the top.
  app.js                   All page behaviour (section J).
  intro-gate.js            Tiny script in <head>: decides before paint whether
                           the intro film shows. Adds class "intro-on" or "ready"
                           to <html>.
  htaccess.txt             Becomes dist/.htaccess (section N).
  php/signal.php           "More of this" tap counter.
  php/cup.php              In The Cup seat requests.
  php/stats.php            Private page: tallies, seat requests, CSV download.
  favicon.ico, icon-*.png, apple-touch-icon.png   Made by tools/og.py.
  img/*.jpg                ORIGINAL photos (inputs). Do not edit by hand.
  img/logo-nitc-chrome.png, logo-nitc-chrome-trim.png   Chrome NAS IN THE CUT logo.
  img/world-dots.svg       Dotted world map, made by tools/map.
  img/og.jpg, og-cup.jpg   Social share images, made by tools/og.py.
  img/previous/            Older photos kept in case Nas wants them back.
  img/out/                 GENERATED by tools/images.py (not in this zip).
  media/intro-source.mp4   Original reel (24 s, 720x1280).
  media/intro-track-source.mp3   Original song file (see licence note, section Q).
  media/out/               GENERATED by tools/media.sh (not in this zip).

tools/
  images.py                Photos to AVIF + JPEG at several widths.
  media.sh                 Film, poster, 30 s song cut, chrome logo sizes (ffmpeg).
  og.py                    Social cards (og.jpg, og-cup.jpg) and the icon set.
  audit.py                 Headless Chromium audit of every page at 10 widths.
  markers.json             Map marker positions in percent. Read by build.py.
  map/gen.mjs              Redraws world-dots.svg and markers.json (Node).

backend-starter/           NEW, not yet wired in. Ready-to-finish code for section Q.
  subscribe.php            Email sign-up relay for Beehiiv or Kit.
  nitc-config.sample.php   Private settings file template (API keys, stats key).

brand/                     Logo SVGs, icons and an OG image for reuse elsewhere.

dist/                      GENERATED website. Upload this. Rebuilt on every build.


==============================================================================
E. SET UP A MACHINE
==============================================================================
Tested with: Python 3.11, Pillow 12.2, Playwright 1.56, ffmpeg 6.1, Node 22,
PHP 8.4. Mac or Linux. Windows works through WSL.

  1. Python 3.10 or newer.
  2. pip install -r requirements.txt
  3. python3 -m playwright install chromium
  4. ffmpeg (Mac: brew install ffmpeg. Ubuntu: apt install ffmpeg)
  5. PHP 8.x, only for testing the backend locally (Mac: brew install php)
  6. Node 18+, only if you redraw the world map.

Check AVIF works:  python3 -c "from PIL import features; print(features.check('avif'))"
It must print True. If not, upgrade Pillow.


==============================================================================
F. BUILD, STEP BY STEP
==============================================================================
Run everything from the project root (the folder with build.py). Order matters
the first time, because each step uses the output of the one before.

  1. python3 tools/images.py      photos  -> src/img/out/        (about 1 min)
  2. bash tools/media.sh          film, song, logo -> src/media/out/
  3. python3 tools/og.py          share images and icons (needs 1 and 2)
  4. python3 build.py             writes dist/
  5. python3 tools/audit.py       must end with:
                                  AUDIT PASSED: 3 page x 10 widths, zero findings

After the first time, a copy change only needs steps 4 and 5.
New or swapped photo: steps 1, 4, 5 (and 3 if it is the hero or the latte).
New song: drop it in as src/media/intro-track-source.mp3, then steps 2, 4, 5.

Optional, map only:  cd tools/map && npm install && node gen.mjs
Then add the new key to OFFICES in build.py.

Note: build.py quietly skips any photo whose resized files are missing. If a
photo is missing from the page, you skipped step 1.


==============================================================================
G. THE BUILD GATE (WHY THE BUILD CAN REFUSE)
==============================================================================
build.py checks every output file before writing anything. It prints
"BUILD REFUSED" and the reason if it finds:
  - em dash, en dash, ellipsis character, non-breaking space, zero width space
  - TODO, FIXME, XXX, PLACEHOLDER, [CONFIRM, lorem ipsum
This is a client rule, not a style choice. Use commas, colons or full stops.
Straight apostrophes in visible text are turned into curly ones automatically.


==============================================================================
H. THE AUDIT (THE QUALITY GATE)
==============================================================================
tools/audit.py serves dist/ locally, opens each page in headless Chromium at
320, 360, 375, 390, 414, 768, 1024, 1280, 1440 and 1600 pixels and checks:
  layout overflow, tap targets (24 px minimum), heading structure, alt text,
  form labels, colour contrast, third party requests, console errors, keyboard
  tab order, the intro film (shows, traps focus, enters, replays, Escape),
  "More of this" (one request, remembered), the map legend, the photo viewer,
  the In The Cup form (cup.php is mocked), the mobile dock, the sign-up forms,
  reduced motion, print styles, and that every link and file exists.
Nothing ships unless it ends with zero findings. If you add a feature, add a
check for it in audit.py.

Known limit: the Chromium used by Playwright cannot play H.264, so the film
itself is not played during the audit. Check the film on a real phone.


==============================================================================
I. EDITING CONTENT
==============================================================================
All in build.py. Search for these names:
  TITLE, DESCRIPTION, OG_DESC   page title and share text (home)
  HERO_LEDE                     the opening paragraph
  ISSUES                        the three issue previews
  RULES                         the seven rules
  STATS                         $9+ figures, 95 countries, 6 African countries, 365
  ALLIANCES                     Davido, Sir Mo Farah, FC Barcelona
  OFFICES                       the six African offices on the map
  SHOTS                         Collective 365 photo rail
  ROOM, ROOM_TITLE, ROOM_DESC   In The Room photos and stories
  CUP_TITLE, CUP_DESC, CUP_STEPS, CUP_RULES, CUP_SHOTS, body_cup()   In The Cup
  PERSON                        structured data for Google (sameAs links)
  SUBSCRIBE_ENDPOINT            where sign-ups go (section Q1)

Adding a photo: put the JPEG in src/img/ with a short lowercase name, add the
name to FRAMES (3:4 crops) and/or GALLERY (native shape) in tools/images.py,
then add it to SHOTS, ROOM or CUP_SHOTS in build.py with alt text and caption.

Palette (src/styles.css, top): navy #0B1422, deep #07101C, raised #111D30,
hairline #22314A, strong hairline #34455F, silver #D6DCE4, bright silver
#F1F4F8, muted silver #A9B4C5. No gradients, glows or gold.


==============================================================================
J. FRONTEND BEHAVIOUR, FEATURE BY FEATURE (src/app.js)
==============================================================================
Sign-up forms (form.signup)
  Email checked in the browser. If SUBSCRIBE_ENDPOINT is empty (today), the
  form says sign-ups open at launch and points people to Instagram. When it is
  set, the form POSTs JSON {"email": "...", "source": "<form id>"} and expects
  any 2xx status for success. Hidden "website" field catches bots.

Intro film (first visit in a browser session)
  src/intro-gate.js runs in <head>. If sessionStorage "nitc-intro" is not
  "seen", <html> gets class "intro-on" and the film overlay shows, otherwise
  "ready". The film is silent; a Sound button plays media/intro-track.mp3
  (browsers only allow sound after a tap). Enter, any tap, Escape or the end of
  the film enters the site. "Play the film" in the footer replays it.
  Add ?intro to any URL to force it, ?nointro to skip it.
  Phones get intro-540.mp4, wider screens intro-720.mp4.

"More of this" buttons
  Quiet button under issues, rules, alliances, Collective 365, In The Cup and
  every In The Room photo. One tap per item per browser (localStorage
  "nitc-signals"), sent with navigator.sendBeacon to signal.php as
  {"id": "issue-1"}. Ids: issue-N, rule-N, alliance-davido, alliance-mo-farah,
  alliance-barcelona, collective-365, in-the-cup, room-<photo name>.

In The Cup form (#cup-form)
  Checks fields, POSTs FormData to cup.php with Accept: application/json and
  shows the message from the reply. Without JavaScript it posts normally and
  cup.php redirects back to in-the-cup.html?seat=saved#seat.

Also: Dubai clock with countdown to 07:00 (UTC+4), header that hides on
scroll, mobile dock, reading progress line, issue accordions, swipe rails with
arrows and keyboard, numbers that count up once, map legend toggles, and the
In The Room viewer (<dialog>, swipe, arrows, Escape).


==============================================================================
K. BACKEND: WHAT EXISTS TODAY
==============================================================================
All three files sit in the site root next to index.html and write to data/.
data/ is blocked from the web by data/.htaccess ("Require all denied").
Every write uses an exclusive file lock (flock), so two visitors at once are safe.

1. signal.php    POST only. Body JSON {"id": "..."}
   - id must match ^[a-z0-9-]{2,48}$  else 400
   - adds 1 to that id in data/signals.json, replies 204
   - GET replies 405. Maximum 500 different ids (then 429).
   - Stores nothing about the visitor.

2. cup.php       POST only. Form fields:
     name        required, up to 80 characters
     email       required, valid, up to 120, stored lowercase
     mode        required, "in-person" or "online"
     question    optional, up to 400
     one_to_one  "yes" if ticked
     website     honeypot: if filled, replies success and stores nothing
   Rules:
   - Same email again replaces the earlier request (no duplicates).
   - Max 20 requests a day from one connection (cafe wifi safe). The IP is
     never stored, only a sha256 fingerprint of it.
   - Max 5000 requests in the file (then 503).
   Replies, when the request says Accept: application/json:
     200 {"ok":true,"message":"..."}   400 bad fields   405 not POST
     429 daily limit   500 cannot write   503 list full
   Otherwise: 303 redirect to in-the-cup.html?seat=saved#seat (or seat=error).
   Optional NOTIFY_EMAIL constant at the top: sends a plain email for each new
   request with PHP mail(). Empty today, so off.

3. stats.php     GET, private. See section M.

backend-starter/subscribe.php   Written and tested locally, NOT yet deployed.
   See Q1.


==============================================================================
L. DATA FILES AND THEIR EXACT SHAPE
==============================================================================
Both are created on the first write. Both live in public_html/data/ on the
server and are NOT in any zip. Never delete the data folder when updating.

data/signals.json
  {"issue-1": 14, "rule-3": 6, "room-davido-lunch": 2}

data/cup-requests.json   (array, pretty printed, UTF-8)
  [
    {
      "at": "2026-10-12T09:41:07+00:00",   UTC, ISO 8601
      "name": "Sara Khan",
      "email": "sara@example.com",
      "mode": "in-person",                  or "online"
      "one_to_one": true,
      "question": "How did you fund the first gym?",
      "who": "3f1c...e9"                    sha256 of IP, for the daily limit only
    }
  ]

data/subscribe-rate.json  (only once subscribe.php is live)
  {"<sha256 of IP>": [unix times in the last hour]}


==============================================================================
M. THE PRIVATE STATS PAGE
==============================================================================
  https://nasinthecut.com/stats.php?key=<STATS_KEY>
  https://nasinthecut.com/stats.php?key=<STATS_KEY>&csv=1   (spreadsheet download)

The key is the constant STATS_KEY at the top of src/php/stats.php. A wrong key
gets a plain 404 (timing-safe compare). The page shows "More of this" tallies
with readable names, and every In The Cup request, newest first. All output is
HTML-escaped. The CSV puts an apostrophe in front of any cell starting with
= + - @ so Excel cannot run it as a formula.

This is a launch-day solution. A key in a URL ends up in browser history.
Replacing it is task Q3.


==============================================================================
N. HOSTING: HOSTINGER, .HTACCESS, DEPLOY AND UPDATE
==============================================================================
What .htaccess does (source: src/htaccess.txt)
  - http and www both 301 to https://nasinthecut.com
  - /in-the-room and /in-the-cup 301 to the .html pages
  - Correct types for avif, webp, svg, webmanifest, mp4, mp3
  - Compression for text files
  - Caching: HTML never cached, hashed CSS/JS one year, media one month
  - Security headers: CSP, HSTS, nosniff, DENY framing, referrer policy,
    permissions policy
  - No directory listings. UPLOAD.txt, _headers, signals.json and
    cup-requests.json can never be served.
  _headers in dist/ is the same idea for Netlify or Cloudflare. Hostinger
  ignores it and it is left out of the upload zip.

First deploy
  1. hPanel > Websites > Manage (nasinthecut.com) > File Manager > public_html
  2. Delete everything in public_html.
  3. Zip the CONTENTS of dist/ (files at the zip root, not a dist folder).
     Leave out _headers and anything in data/ except data/.htaccess.
  4. Upload, right click, Extract into public_html itself.
  5. Check index.html, the three PHP files and the folders assets, img, media,
     data sit directly in public_html. Delete the zip.
  6. Security > SSL: free certificate active.
  7. Make sure data/ is writable by PHP (755 on the folder is normal on
     Hostinger). Tap a "More of this" button, then open stats.php to confirm.

Every later update
  Same as above, BUT in step 2 delete everything EXCEPT the data folder.
  It holds every tap and every seat request. Download a copy of data/ first.

Check after deploy
  curl -I http://www.nasinthecut.com            -> 301 to https://nasinthecut.com/
  curl -I https://nasinthecut.com/data/cup-requests.json   -> 403
  curl -I https://nasinthecut.com/in-the-cup    -> 301 to /in-the-cup.html
  Open the site on a phone: film plays, Sound works, Enter works.


==============================================================================
O. SECURITY, PRIVACY AND THE CONTENT SECURITY POLICY
==============================================================================
Current CSP:
  default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self';
  connect-src 'self' https:; form-action 'self' https:;
  frame-src https://form.typeform.com; base-uri 'self'; frame-ancestors 'none'

  frame-src is the one exception to "no third party requests": the In The Cup
  "Save your seat" section embeds a Typeform (SEAT_FORM_URL in build.py).

What it means for you:
  - No inline <script> or style="" attributes. Put code in app.js, styles in
    styles.css. The audit will catch console CSP errors.
  - fetch() to the site itself or any https address is allowed, so the
    sign-up relay (same site) works with no change.
  - If you add an embedded provider form, a captcha or analytics, you must add
    its domain to the CSP in src/htaccess.txt AND to HEADERS in build.py.
    Prefer not to: the relay approach in Q1 needs no CSP change.

Personal data held today: names, emails, optional questions (cup-requests.json).
No cookies. localStorage/sessionStorage only hold "seen the intro" and "tapped
More of this", nothing personal.


==============================================================================
P. TESTING THE BACKEND LOCALLY
==============================================================================
  python3 build.py
  cd dist && php -S 127.0.0.1:8080
  (PHP's built-in server ignores .htaccess, so data/ is NOT protected locally.)

  # signal: expect 204, 400, 405
  curl -i -X POST -d '{"id":"issue-1"}' http://127.0.0.1:8080/signal.php
  curl -i -X POST -d '{"id":"BAD ID"}'  http://127.0.0.1:8080/signal.php
  curl -i http://127.0.0.1:8080/signal.php

  # cup: expect 200 JSON, then 400
  curl -i -H 'Accept: application/json' -d 'name=Test&email=t@example.com&mode=online' http://127.0.0.1:8080/cup.php
  curl -i -H 'Accept: application/json' -d 'name=Test&email=bad&mode=online'          http://127.0.0.1:8080/cup.php

  # stats: wrong key 404, right key 200
  curl -i "http://127.0.0.1:8080/stats.php?key=wrong"

To test .htaccess for real, use Apache or LiteSpeed (a Docker httpd image with
mod_rewrite, mod_headers, mod_expires enabled works), or a Hostinger staging
subdomain.


==============================================================================
Q. WHAT IS LEFT TO COMPLETE (THE BACKEND TO-DO LIST)
==============================================================================
In order. Q1 to Q4 are needed before a public launch. Each item says what
"done" means.

Q1. CONNECT THE EMAIL SIGN-UP  (most important, blocks launch)
    Nas has to choose the provider: Beehiiv or Kit (ConvertKit). Both work.
    a. Create the publication or form. Get the API key and the publication id
       (Beehiiv) or form id (Kit).
    b. Copy backend-starter/nitc-config.sample.php to nitc-config.php, fill it
       in, upload it ONE LEVEL ABOVE public_html (on Hostinger:
       /home/<user>/domains/nasinthecut.com/nitc-config.php). Never commit it.
    c. Copy backend-starter/subscribe.php to src/php/subscribe.php and add
       "subscribe.php": (SRC / "php" / "subscribe.php").read_text(),
       to the files dict in build.py main(), next to cup.php.
    d. In build.py set  SUBSCRIBE_ENDPOINT = "subscribe.php"
    e. Check both API calls in subscribe.php against the provider's current
       docs (endpoints and field names change). Make sure the provider sends
       the welcome email with issue #1, and that double opt-in is on.
    f. Build, audit, deploy. Sign up with a real address from a phone.
    Done when: a sign-up on the live site appears in the provider within a
    minute and the welcome email arrives. Bad emails get the error message.
    Already in the starter: validation, 10 per hour per connection limit,
    secret kept server side, JSON 200/4xx/5xx replies the page understands.

Q2. IN THE CUP NOTIFICATIONS
    cup.php can email Nas's team per request via PHP mail(), but mail() from
    shared hosting often lands in spam.
    Do: send through SMTP (Hostinger email account, or the provider's API,
    or a transactional service such as Postmark or Resend) using PHPMailer or
    a plain HTTPS call. Read the address from nitc-config.php
    ('notify_email'), not from a constant in the file.
    Also send the person a confirmation email ("You are on the list").
    Done when: a test request emails the team and the requester, and neither
    lands in spam (set SPF, DKIM and DMARC for nasinthecut.com in Hostinger DNS).

Q3. PROPER ADMIN ACCESS FOR stats.php
    Today: a secret key in the URL.
    Minimum: move STATS_KEY into nitc-config.php ('stats_key'), rotate it
    (the current key has been shared in chat and in docs, so treat it as
    known), and give it to Ray and Nas only.
    Better: a login page with password_hash()/password_verify(), a session
    cookie (HttpOnly, Secure, SameSite=Strict), session_regenerate_id() on
    login, a lockout after 5 wrong tries, and a CSRF token on any action.
    Or protect /stats.php with Hostinger's "Password protect directories"
    (basic auth) by moving it into an /admin/ folder.
    Done when: no data is reachable without logging in, and the old key 404s.

Q4. PRIVACY AND CONSENT (GDPR / UAE PDPL)
    - Write a privacy page (privacy.html): who holds the data (Nas's company),
      what is collected (email; for In The Cup name, email, mode, question),
      why, how long, how to be deleted. Link it from both forms and the footer.
    - Add a line under each form linking it. The current form copy is
      "Used only for In The Cup invites. Never sold or shared." Keep it true.
    - Deletion: add a way to remove a person from cup-requests.json (a delete
      button on the admin page, or a script) and from the email provider.
    - Retention: clear In The Cup requests older than, say, 12 months.
    Done when: the privacy page is live and a delete request can be handled
    in under five minutes.

Q5. BACKUPS OF data/
    Hostinger backs up the account, but restoring one file is slow.
    Do: a daily cron job (hPanel > Advanced > Cron Jobs) that copies
    public_html/data/*.json to a dated folder above public_html and keeps 30
    days, or emails the CSV weekly. Example command:
      mkdir -p ~/backups && tar czf ~/backups/data-$(date +\%F).tgz -C ~/domains/nasinthecut.com/public_html data && find ~/backups -name 'data-*' -mtime +30 -delete
    Done when: yesterday's backup exists and has been restored once as a test.

Q6. THE IN THE CUP WORKFLOW (invites and the monthly one to one)
    Today requests are only collected. Nas's team needs to:
    a. Pick a date and venue each month.
    b. Invite: export the CSV from stats.php and send the invite through the
       email provider (tag or segment "in-the-cup", split in-person / online).
       Better: when a seat request comes in, also add the person to the
       provider with a tag "in-the-cup" and "in-person" or "online"
       (same API as Q1), so invites are one click.
    c. Pick the one to one reader: random draw among one_to_one = true.
       A small "Draw" button on the admin page that picks one at random,
       records the month and the winner, and excludes past winners.
    d. Optional: capacity per month, "seat confirmed" status, waitlist.
       At this point move from JSON files to a database (Hostinger has MySQL;
       SQLite also works). Suggested table:
         cup_requests(id, created_at, name, email UNIQUE, mode, one_to_one,
                      question, status, month, ip_hash)
    Done when: Nas's team can run a month end to end without touching files.

Q7. STRONGER ABUSE PROTECTION
    Current: honeypot fields, per-connection daily or hourly limits, size caps,
    strict validation. Good enough for launch.
    If spam appears: add Cloudflare Turnstile to the two forms (needs the
    Turnstile domain added to the CSP, script-src and frame-src), or put the
    domain behind Cloudflare with a rate limit rule on /cup.php,
    /subscribe.php and /signal.php.

Q8. MONITORING
    Turn on an uptime check (UptimeRobot or Hostinger's own) for the home page
    and for a POST to signal.php. Make sure PHP errors go to the log, not the
    screen (display_errors off is the Hostinger default; keep it).

Q9. LIGHT UP THE 95 COUNTRIES ON THE MAP  (needs Nas's list)
    The map shows Dubai and the six African offices. "95 countries" is a
    counter only. With the list: add each country's longitude and latitude to
    "places" in tools/map/gen.mjs (or switch to shading whole countries with
    world-atlas countries-50m.json), rerun, add a softer marker style for
    "travelled" versus "office" in styles.css, update the alt text in
    build.py. Keep the SVG under about 60 KB.

Q10. MUSIC LICENCE FOR THE INTRO
    media/intro-track.mp3 is the first 30 seconds of a commercial recording
    supplied by Ray. The licence is Nas's responsibility and is not cleared in
    this build. To swap: replace src/media/intro-track-source.mp3 with a
    licensed track, run bash tools/media.sh, build, deploy. Same file name,
    no code change.


==============================================================================
R. CONTENT STILL WAITING ON NAS
==============================================================================
Not code, but nothing should go public until Nas signs these off:
  - The seven rules, the three issue previews (replace with his real opening
    paragraphs), the story line about coming to the UK as a kid.
  - "Biggest training community", the alliances wording, In The Room captions,
    the In The Cup concept and house rules.
  - Full quality originals of the Instagram photos (current ones are about
    1080 pixels from Instagram).
  - CEO Forum Africa video: wanted, not yet supplied.
  - LinkedIn: a Nasir Hassan profile (Sterling Boulevard, Dubai real estate)
    matches his Instagram bio. Add the URL to PERSON["sameAs"] in build.py once
    Nas confirms it is his.
  - Not "Dr". He is Nasir Hassan or Nas.
  - Left out on purpose: two photos in the black StepCorrect T-shirt.


==============================================================================
S. HOUSE RULES FOR THIS PROJECT
==============================================================================
  1. Every word lives in build.py. Never hand-edit dist/.
  2. No em dashes, en dashes or ellipses. The gate enforces it.
  3. No third party requests on page load. No web fonts, no trackers.
  4. No inline scripts or styles (CSP).
  5. Audit must pass with zero findings before any upload.
  6. Look: navy and silver, system type, square photos, slow fades. No
     gradients, glows, gold, emoji, pill badges or pulsing dots.
  7. Never delete public_html/data on the server.
  8. Secrets (API keys, admin passwords) live in nitc-config.php above
     public_html. Never in build.py, never in the zip, never in git.
  9. Explain changes to Ray in plain steps. He reads on his phone.


==============================================================================
T. QUICK REFERENCE
==============================================================================
Full rebuild     python3 tools/images.py && bash tools/media.sh && python3 tools/og.py && python3 build.py && python3 tools/audit.py
Copy change      python3 build.py && python3 tools/audit.py
Local preview    cd dist && php -S 127.0.0.1:8080   then open http://127.0.0.1:8080
Force intro      add ?intro to the URL      Skip intro   ?nointro
Private page     /stats.php?key=<STATS_KEY>  (CSV: add &csv=1)
Data             public_html/data/signals.json, cup-requests.json
Config (to add)  /home/<user>/domains/nasinthecut.com/nitc-config.php

End of handover.
