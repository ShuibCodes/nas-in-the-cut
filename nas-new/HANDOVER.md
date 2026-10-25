# Nas In The Cut: handover for a desktop session with Chrome

Written 28 September 2026. Hand this whole file to Claude in a desktop session that has Claude in Chrome connected, together with `nas-in-the-cut-v4.zip`.

## 1. The job in one line

Open Nas's Instagram in Chrome, pick the strongest photos from the six posts below, and swap them into the finished website. Keep everything else as it is.

## 2. Context

- Client: Nasir Hassan, known as Nas. Dubai founder and investor. He built gyms, sold nine figures in real estate, invests in creative businesses and runs Collective 365, a Dubai community that trains twice a week.
- Product: "Nas In The Cut", a free daily business email. Old site: https://www.nasirhassan.com. New domain for this build: https://nasinthecut.com (Hostinger).
- Ray (the user) is rebuilding the site for Nas, with Nas's approval, using Nas's own name, story and photos.
- Preview of the new site (version 4, private to Ray): https://claude.ai/artifact/7x5jHyEVwdH1MWTxiLnJok

## 3. Instagram posts to review (Ray's picks)

1. https://www.instagram.com/p/DdeK7idikOJ/?img_index=1
2. https://www.instagram.com/p/DdeK7idikOJ/?img_index=2
3. https://www.instagram.com/p/DdRszH8Cmxx/?img_index=1
4. https://www.instagram.com/p/DciROGRihvQ/?img_index=1
5. https://www.instagram.com/p/Db3ZNjODV1A/?img_index=1
6. https://www.instagram.com/p/DLIKMaYynzA/
7. Profile for anything else strong: https://www.instagram.com/nasinthecut/

Carousel posts can hold more than one image. Check every slide.

## 4. What each photo slot needs

The site has three photo slots. Each image is cropped to 3:4 on desktop and 4:5 on phones, so the subject needs room around the face.

| Slot | Current file | What works best |
|---|---|---|
| Hero (top of page) | `nas-terrace` | Clean portrait of Nas, face clearly lit, calm background, looking at camera or just off it. Upright. |
| About ("I build. I invest. I write it down.") | `nas-mo-farah` (with Mo Farah, UAE) | The business or credibility side: on site, meeting, speaking, or a well known name. Keep Mo Farah if nothing beats it. |
| Collective 365 | `collective-365` | Group session with energy, Nas visible and leading. |

Deep navy and silver design, so warm, bright daylight photos read best against it. Avoid heavy filters, text overlays, logos or other brands dominating the frame.

## 5. How to get the images

- Open each post in a new Chrome tab. Screenshot or save the full-resolution image of each chosen slide. Instagram serves about 1080 pixels wide, which is enough for this layout.
- Crop out any Instagram interface. Save as JPEG into `src/img/` using the slot file names above, for example `src/img/nas-terrace.jpg`. Keep the old files in a `src/img/previous/` folder in case Ray wants them back.
- Tell Ray which post and slide each chosen image came from, and suggest he still asks Nas for the full-quality originals for launch.

## 6. Rebuild and check (commands run from the project folder)

```
python3 tools/images.py     # makes AVIF, WebP and JPEG at 480, 800 and 1080 wide
python3 tools/og.py         # redraws the social link preview from the hero photo
python3 build.py            # builds dist/, refuses to build on any banned character
python3 tools/audit.py      # must end with: AUDIT PASSED ... zero findings
```

Needs Python 3 with Pillow (AVIF support) and Playwright with Chromium. If a new photo frames the face differently, adjust `object-position` for that slot in `src/styles.css` (search "4:5 crops").

If the photo in a slot changes subject, update its `alt` text and caption in `build.py` (search for the file name).

## 7. Rules for this project

- Ray's standard: `standards/static-site-build-gate.md` in the WEB STUDIO project. One Python builder, hashed assets, no web fonts, no third party requests, audit at ten widths from 320 to 1600.
- No em dashes, en dashes or ellipsis characters anywhere. The builder blocks them.
- No "AI look": no gradients, glows, pills, badges, pulsing dots, emoji, gold, italic accent words or monospace labels. Ray rejected those in version 2.
- Design: deep navy #0B1422, light silver #F1F4F8 and #D6DCE4, muted silver #A9B4C5, hairlines #22314A. Light system type, square photos, slow fades only.
- Mobile first. Body text 18px on phones. Every tap target at least 44px where it matters.
- Plain, step by step explanations to Ray. He is a CEO reading on mobile.

## 8. What is in the zip

- `dist/`: the finished site, ready to upload to Vercel, Netlify or Cloudflare Pages.
- `build.py`: every word of the site. Edit copy here, never in `dist/`.
- `src/styles.css`, `src/app.js`: look and behaviour.
- `src/img/`: source photos. `src/img/out/` holds the generated sizes.
- `tools/images.py`, `tools/og.py`, `tools/audit.py`: image processing, social card, audit gate.
- `claude-design-brand-prompt.md`: paste-ready brief for Claude Design (logo, monogram, favicon set, social assets) in the navy and silver direction.

## 9. Still open before launch

1. Email provider. The form is ready but not connected. When Nas chooses one (Beehiiv or Kit, for example), put its sign-up endpoint in `SUBSCRIBE_ENDPOINT` in `build.py` and rebuild. Until then the form tells people to message @nasinthecut on Instagram.
2. Logo and icons from Claude Design. Drop them into `dist/` under the file names listed in the brand prompt, and replace the interim wordmark in `build.py` (`WORDMARK`).
3. LinkedIn. A Nasir Hassan profile in Dubai real estate (Sterling Boulevard, myrealtordubai.com) was found but not confirmed as him. Add it to `sameAs` in `build.py` only if Ray confirms.
4. Nas signs off on the page before it replaces the live site.

## 10. Finish by

Republishing the preview to the same link if possible, or sending Ray a fresh zip. Tell him in plain words which photos changed and why.


## Update, 28 September 2026 (v4.1)

- Hero photo replaced: Nas in a dark suit and tie, from instagram.com/p/DdRszH8Cmxx slide 1 (Barcelona). Caption now "Nasir Hassan, Barcelona". Hero crop on phones moved to 50% 25% so the face stays in frame.
- Collective 365 photo replaced: group run on the green track, Nas in the middle, from instagram.com/p/Db3ZNjODV1A slide 6.
- About photo unchanged (Mo Farah). The Barcelona meeting photo was square and lost a person in the 3:4 crop.
- Social preview (og.jpg) redrawn from the new hero.
- Old photos kept in src/img/previous/.
- Audit: AUDIT PASSED, 1 page x 10 widths, zero findings.
- Before launch: ask Nas for the full-quality originals of both photos.


## Version 5, 28 September 2026

What changed
- Logo is now just NAS: the 2b wordmark, redrawn in silver with the node in muted silver #A9B4C5 so it sits inside the navy and silver palette (the master files use cyan). Header, footer and an About signature all use it.
- New favicon and app icon: the N with the silver node, on navy. New social preview (og.jpg) with the NAS logo, the headline and the Barcelona portrait.
- Brand files are in brand/: logo SVGs (silver for dark grounds, navy for light), favicon.svg, icon-512.png, apple-touch-icon-180.png, og-1200x630.jpg.
- Copy: earned motivation in Nas's own words. The "zero motivational quotes" line is gone. One line of his story in About ("I came to the UK as a kid, from a country at war").
- Interactive: live Dubai clock with a countdown to the 7:00 issue, reading progress line under the header, numbers band that counts up once, tap-to-read issue previews, swipeable "Six rules I run on" deck, Collective 365 photo swipe with 4 real photos, arrow buttons and keyboard arrows on both rails.
- Collective 365 photos: the run (Db3ZNjODV1A slide 6), the huddle (Db3ZNjODV1A slide 5), the call (Db3ZNjODV1A slide 7, the previous section photo), the street (DciROGRihvQ slide 4).
- The audit now also tests the issue previews, both rails, the counters and the progress line. AUDIT PASSED, zero findings.

Nas must approve before launch
- The six rules are his Instagram captions, lightly tidied. Rule 5 comes from the newsletter copy.
- The three issue previews are drafted in his voice. Replace them with his real opening paragraphs.
- The story line about coming to the UK.

## Version 6, 29 September 2026

New on the site
- Intro film on first visit (once per visit): Nas's reel, silent, under a deep blue shade with the chrome NAS IN THE CUT logo and the line "How the money actually gets made." A Sound button plays the intro track (browsers only allow sound after a tap, so the film starts silent). Enter, a tap anywhere, Escape, or the end of the film opens the site with a wipe. "Play the film" in the footer replays it. Add ?intro to the address to force it, ?nointro to skip it.
- Film: media/intro-540.mp4 (phones, 2.0 MB) and media/intro-720.mp4 (desktop, 2.8 MB), no audio track. Track: media/intro-track.mp3, the first 30 seconds of the supplied song with a fade. Ray chose to use this commercial recording; the licence is Nas's responsibility. To swap it, replace media/intro-track.mp3 with any MP3 of the same name.
- Numbers: $9+ figures in Dubai real estate, 95 countries, 6 African countries with offices, 365 Collective.
- Strategic alliances: Davido (Spiro partnership through Narrativ Africa), Sir Mo Farah, the President of FC Barcelona, plus "Some of the most important relationships stay private. That is the point."
- Africa: offices in Cote d'Ivoire, Gabon, Benin, Rwanda, Uganda and Kenya, a dotted world map with office markers and a 95 countries counter. Countries are not lit up yet: needs Nas's list of 95.
- Rules: seven now, adding "Only those who can see the invisible can do the impossible."
- In The Room: a second page, in-the-room.html (also /in-the-room), 14 photos with one-line stories and a full screen viewer.
- More of this: a quiet button under alliances, issues, rules, Collective 365 and every In The Room photo. Taps go to signal.php, counted in data/signals.json (blocked from the public). Private tally: https://nasinthecut.com/stats.php?key=bpQhnueWrTbWfm7cxqci9nC4
- Link preview now uses the chrome logo.

Checks
- AUDIT PASSED, 2 pages x 10 widths, zero findings. The audit now also tests the intro (shows, traps focus, enters, stays gone, replays, Escape), the signal (one request, remembered), the map legend and the viewer.
- PHP tested: valid taps 204, bad id 400, GET 405, wrong stats key 404.
- Phone over 4G with a slow processor: page visible in about 1.3 s.

Nas to approve
- Rules, issue previews, story line, "biggest training community", the alliances wording and the In The Room captions.

## Version 7, 12 October 2026: In The Cup

- New page in-the-cup.html (also /in-the-cup) and a homepage section, with "In The Cup" in the header on every screen size.
- Concept: once a month everyone in Nas's world meets for coffee somewhere special, with a couple of special guests and open questions for them and for Nas. Every month one reader is picked for a one to one coffee with Nas, in person or online. House rules: come as you are, no pitching, phones face down, bring one real question.
- Save your seat form: name, email, in person or online, optional question, and a tick box for the one to one. Requests go to cup.php and are stored privately in data/cup-requests.json (same email updates its request, 20 a day per connection, bots caught by a hidden field). Read them, and download a spreadsheet, on stats.php with the same key. To get an email for each new request, put an address in NOTIFY_EMAIL at the top of cup.php.
- Share image for the page: img/og-cup.jpg (latte with the logo, "In The Cup.").
- In The Room gains two frames: lunch with Davido, and Kokko in Barcelona.
- Left out on purpose: the two photos in the black StepCorrect T-shirt, because the print reads as a swear word close up.
- AUDIT PASSED, 3 pages x 10 widths, zero findings, including the seat form (required fields, choice required, request sent, success shown). PHP tested: valid 200, update, bad email or choice 400, honeypot, no-JavaScript fallback redirect, daily limit, spreadsheet export guarded against formula injection, names escaped on the private page.
