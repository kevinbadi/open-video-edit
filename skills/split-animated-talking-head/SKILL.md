---
name: split-animated-talking-head
description: Turn a user-supplied talking-head clip (webcam, phone selfie, or recorded speaker) plus an optional script or source URL into a split-format vertical short — custom-generated animations in the top ~50%, the provided talking-head cropped into a taller rounded band across the bottom, kinetic captions synced to the clip's own voice, real product logos/screenshots whenever a named tool is spoken, real portraits of the notable figures behind any spoken niche (Claude/Anthropic, SpaceX, OpenAI, marketing, business, sales…), Giphy reaction GIFs on punchlines, a hyper-edit layer (keyword punch-ins, hyperframe inserts, whip cuts, shake) No HeyGen. Use when the user provides a talking-head video, webcam recording, selfie clip, or asks for the split animated format using their footage instead of a Megan/Danny/Kevin avatar.
---

# Split Animated Short — user talking head (taller live band)

**HARD RULE (Kevin 2026-09-03): Final video is 1080×1920. Never 720×1280.
Never scale the user's talking-head down to 704×640.** Their clip is already
1080p. Instagram/TikTok/YouTube Shorts display at 1080×1920; a 720p master
gets upscaled and looks like mud. If ffprobe on `renders/final.mp4` is not
`1080x1920`, delete it and start over. Do not publish 720p.

Same flagship format as `split-animated-short`, except the bottom band is the
**clip the user hands you**, not a HeyGen talking-photo. The clip's audio is
the master timeline. Animations are authored per script — zero pixels from any
*reference* reel except its words, if one is given.

Live talking-head footage needs **more band height than the HeyGen 45% lock**
so hats/hair aren't clipped (Kevin 2026-09-01). Default band is **1056×960 at
y=936** on the **1080×1920** canvas (caption baseline rests ON the accent line at
y=BAND_Y-5, letters fully above the head; Kevin 2026-09-18/19). Round all four
corners of the band mask — never `BAND_H+60` (that square-cuts the bottom
flush to the canvas). ~24px of canvas stays under the card.

**PACK LOCK (Kevin 2026-09-03, opensource-100 recut):** animations sit
**just above the captions**, not up against the top of the frame. A top-hugging
pack leaves a vacant band in the middle of the screen. Locked numbers:

```
AH = 770          # animation layer height
LAYER_Y = 90      # composite at (0, 90) → layer covers canvas y=90..860
PACK_DY = 210     # add to every place()/conveyor/orbit/ticker/ghost cy
CAP_Y = 867       # top of the caption zone (pack reference); the word itself is
                  # baseline on the accent line at BAND_Y-5, anchor="ls" (Kevin 2026-09-19)
BAND_Y = 936      # talking-head band (Kevin 2026-09-15: 960 was too low / clipped the bottom)
```

Layer ends ~7px above the captions. Pack numbers from
`clone-projects/opensource-100-animated/render.py` (historical, not bundled). **Never** `LAYER_Y=42` +
`AH=840` with heroes at cy≈180–280 — that was the vacant-middle bug. Never
design at 853 and downscale, and never render the whole video at 720.

**BEST EDIT YET (Kevin 2026-09-26):** `examples/social-agents/render.py`
is now the top reference (it outranks gitnexus). What made it: the user's b-roll used three ways
(banner crop as the reveal on the product name; a live terminal card that starts zoomed on the
command, then pulls back and scrolls with the output; single-line "LIVE FROM THE REPO" crops,
left part of the line only so the text stays readable). Spoken feature lists become a ticking
checklist card with one bespoke visual per item (real reel covers/thumbnails from
brand-content + Downloads, mock inbox / caption / hashtag / SEO-climb cards). GIFs whose burned-in
text matches the spoken line word for word. Stamps only on each section's dramatic beat.
Reuse its Broll / crop_img / strip_card / broll_view(zoom=) helpers whenever b-roll is supplied.

**STATUS QUO (Kevin 2026-09-19, "SOOOOO GOOOOD that should be the new status quo"):**
`examples/gitnexus/render.py` is the current gold reference. Everything
below still applies; what made it land: Luckiest Guy captions resting on the accent
line with a tight glow, the user's own screen recording as the b-roll hook (mystery
"?" over it) and as per-word crop cuts later, a meme beat matched to the spoken line
(Hangover calculation meme on "understand any piece of code") followed by a custom
motion piece on the next word (spinning wireframe `globe_card` on "planet"), terminals
that type the spoken action, a legend card lighting up per component, stamps on the
punch words, a kinetic headline + lower third + counter. Match that energy on every cut.

**LOOK LOCK (Kevin 2026-09-10, china-robots density + github-research-agent wash):**
gold-standard density / titles / GIFs: china-robots (render.py no longer on disk; use social-agents / gitnexus as code refs).
Slot **brightness** lock: `clone-projects/github-research-agent-animated/render.py` (historical, not bundled)
(Kevin 2026-09-10: "background is too dark" on the near-black CHAR wash).
Copy china-robots energy, but use the lifted graphite `textured_bg` — lift
patches, stronger accent glow, `slot_vignette(..., a=22)`. Do **not** ship
Megan paper/sage/coral, and do **not** use near-black CHAR=(14,15,18) as the
slot wash. Locked colors (override after exec of `animation_assets_and_beats.py`).
**Type lock (Kevin 2026-09-15 + 2026-09-19):** overlay / component text is **Oswald Bold**
(`templates/fonts/Oswald-Bold.ttf`, loaded via `templates/fonts.py` as `AR`).
Title cards, chips, huge_word, counters, name plates, ghosts. **Kinetic captions
are Luckiest Guy** (`templates/fonts/LuckiestGuy-Regular.ttf`, `CAP` in fonts.py):
CapCut-style chunky comic caps, white fill (KEY_COL fill on keywords), 7px black
stroke, no drop shadow (Kevin 2026-09-19 "DOG" screenshot). Copy both ttfs.
Never Arial in the slot. Terminals / code rain / tickers stay **Menlo** (`ML`)
— Menlo.ttc must be opened with `index=0` or glyphs double-print. Oswald is
the condensed display face (the big AND over a UI). Copy `fonts.py` +
`fonts/Oswald-Bold.ttf` into every workdir.

```
INK=(10,11,14)  SILVER=(198,204,214)  STEEL=(92,98,108)
GRAPHITE=(36,38,46)  CHAR=(48,50,58)
NEON=(57,255,132)  ORANGE=(255,122,24)  RED=(255,48,64)
CORAL=ORANGE  PAPER=GRAPHITE
AR=Oswald Bold    CAP=Luckiest Guy (captions only)    ML=Menlo (terminals only)
```

Captions: silver body, `KEY_COL` neon/orange/red on keywords, black shadow,
Oswald Bold ~66px (same face as the title cards). Chips: graphite + accent
bar, Oswald. Cards: graphite, Oswald. Slot accent bars like
china-robots (orange/neon/red per section). Hero titles are **~960px wide**.
User B-roll in the slot should fill ~1000×500, not a small inset.

**TOPIC LOGO CONVEYOR (Kevin 2026-09-10 — staple).** The horizontal scroll
of brand icons tied to the video (voice-agents: OpenAI / Cursor / Docker /
Cloudflare / … under the faces) is required on every cut. Not optional
decoration. See `5d` below.

**INTRO BILLBOARD (Kevin 2026-09-14):** the hook / cold-open must read from
across the room. Giant numbers, giant figure circles, giant logos — not a
contact sheet of 150–220px heads under a title. See `5b` size lock. 150px
rounds are banned anywhere.

Do **not** call HeyGen. Do **not** use this skill when the user wants Megan,
Danny, or Kevin generated. That is `split-animated-short`.

Reference compositor + asset library: this skill's `templates/`. Per video,
create `projects/<slug>-animated/` (slug from the clip filename or topic)
and adapt.

Env (only if publishing / staging a feed item): `INSFORGE_*` in
`.env.local (repo or project root)`. Band prep is local: ffmpeg, OpenCV, Whisper.

## Required input

The user **must** provide a talking-head clip. Accept:

- an absolute/relative file path (`~/Desktop/hook.mov`, `source/talking.mp4`)
- a file they dropped into the chat / workspace
- a URL that **is** their talking-head (download with yt-dlp / curl immediately)

Refuse to start until the clip exists on disk. If they also drop a *reference*
reel URL (the thing to recreate visually), that is optional and only supplies
the script — never its pixels.

Vertical 9:16 is ideal. Horizontal/webcam is fine; prep will cover-crop.

## Pipeline

1. **Workdir.** `mkdir -p projects/<slug>-animated/{source,audio,renders,frames}`
   and `cd` there. Copy this skill's `templates/` in (including `apple_counter.py`, `light_fx.py`,
   `fonts.py`, and `fonts/Oswald-Bold.ttf`).

2. **Prep the talking head** (do this first — it is the timeline):

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/prep_talking_head.py" \
  --clip "/ABS/PATH/TO/CLIP" \
  --workdir . \
  --whisper
```

Writes `source/talking_head.mp4` (native resolution, never downscaled),
`audio/narration.wav` + `.m4a`, `renders/talking_band45.mp4` (**1056×960 @
30fps**, rounded later in compose), `source/meta.json` (`DUR`, crop), and
`audio/words.json`.

Inspect band frames at **3 to 4 timestamps** (the recorder re-frames the
head mid-clip). Crop rule for **live** heads: keep the **full hat /
hairline in frame** with a sliver of space above (backward caps sit higher
than Haar's face box). Default `--head-pad` is 0.35. If the crown is clipped,
lower `--crop-top` (and raise `--crop-h` to match the 1056:960 band aspect),
but never below the clip's own black region: prep scans the whole clip for
the first lit row and clamps the crop under it (`content_top`), and refuses
a band with black top rows (`verify_band_top`). A black strip above the
head is a failed prep, not a look. Do not letterbox the band. Do not scale
the band below 1056×960.

3. **Get the script (words to animate).**
   - Default: the talking-head transcript (`audio/words.json`) **is** the script.
   - Extra script given → use it, but **time** beats to the clip's Whisper
     stamps, not to the written script's imagined pacing.
   - Extra URL given (IG/YT/TikTok to *recreate*) → scrape caption / Whisper
     that source for copy only. IG: Apify `apify~instagram-scraper`
     (`directUrls` + `resultsType: "details"`), download `videoUrl` immediately.
     YouTube/TikTok: yt-dlp. Then persona-swap / product-name-fix against the
     caption. The talking-head clip still owns picture + audio.

4. **Guard on-screen text.** Em/en dashes are banned from UGC overlays (AI
   tell). Censor spoken profanity on-screen Nick-thumbnail style (`sh*t`);
   leave the clip's audio uncensored. If the talking head is *not* Kevin and
   the optional source script names Kevin/Kev/Nick/Saraev, strip or swap
   those names in overlay copy.

5. **SOURCE REAL BRAND ART** (do this before choreography). Walk the transcript
   for every named product, tool, model, or company (Claude, Google, GitHub,
   GitNexus, OmniRoute, GPT, Gemini, Llama, …). For each one, fetch a real
   mark into `assets/logos/<slug>.png` and a social/product card into
   `assets/shots/<slug>.png` when it exists:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/fetch_brand_asset.py" \
  --name claude
python3 "${CLAUDE_SKILL_DIR}/scripts/fetch_brand_asset.py" \
  --name gitnexus --github abhigyanpatwari/GitNexus
```

   Priority: **Claude family is locked** (Kevin 2026-09-03). Do not fetch a
   favicon for Claude, Claude Code, Opus, Sonnet, Haiku, Fable, or Anthropic.
   Copy the bundled marks and dance them:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/fetch_brand_asset.py" --name claude
# writes assets/logos/claude.png (sphinx) plus claude-invader.png + claude-sphinx.png
```

   - **Invader** (`templates/claude_marks.py` → `place_claude_invader`): block
     Space-Invader. Idle dance + walk cycle. **Look:** pass `look_at=(x,y)`
     in layer pixels and the pupils slide toward that point (blinks on their
     own). **Grab:** `grab="right"|"left"|"both"`, `grab_at=(x,y)`,
     `grab_t=0..1` (0 rest, ~0.55 reached, 1 holding/lifted). Pass `hold=`
     an RGBA (use `skill_chip("SKILL.md")`) to stick a card to the hand
     once `grab_t > 0.55`. Morph with `morph=0..1` (starburst scatter).
   - **Sphinx** (`place_claude_sphinx`): official Anthropic starburst badge.
     Use as the spinning mark for Opus / Sonnet / Haiku / Anthropic, and as
     a secondary badge next to the invader.
   Call `place_claude(layer, cx, cy, lt, word="claude", look_at=..., grab="right", grab_at=..., grab_t=...)`.
   Copy `templates/claude_marks.py` and `assets/claude-*.png` into the project.

   For every other named product: official SVG/PNG (Wikimedia / simple-icons /
   site favicon) → GitHub avatar + OpenGraph card → Google s2 favicon. Convert
   SVG with `qlmanage -t` on macOS. **A named product must appear as a logo,
   icon, screenshot, or orbiting mark — never as a text-only pill if a mark
   can be fetched.** Punch near-white backgrounds to alpha; keep dark
   full-bleed logos as round badges.

5b. **SOURCE THE FACES** (Kevin 2026-09-05). Whenever the transcript names a
   company, model, or niche that has famous people behind it, put those people
   on screen — viewers who recognize Dario, Sam, Elon, GaryVee, Hormozi lock in
   harder than they do on a logo. Curated niche map lives in
   `scripts/fetch_figure.py` (`--list`): `claude`/`anthropic`/`opus`/… →
   Anthropic founders (Dario + Daniela Amodei, Jack Clark, Jared Kaplan, Chris
   Olah, Tom Brown); `spacex` → Musk, Shotwell, Mueller; `openai`/`chatgpt` →
   Altman, Brockman, Sutskever, Murati…; `marketing` → GaryVee, Hormozi, Godin,
   Neil Patel, Brunson, Kotler, Ogilvy; `business`/`founders`/`money` → Buffett,
   Bezos, Jobs, Musk, Cuban, Hormozi, Naval, Codie, Martell, Thiel; `sales` →
   Cardone, Belfort, Hormozi, Ziglar, Tracy, Robbins; plus `google`, `nvidia`,
   `meta`, `microsoft`, `apple`, `tesla`, `amazon`, `xai`.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/fetch_figure.py" --niche claude --top 4
python3 "${CLAUDE_SKILL_DIR}/scripts/fetch_figure.py" --niche openai --niche marketing
python3 "${CLAUDE_SKILL_DIR}/scripts/fetch_figure.py" --name "Jensen Huang" --wiki Jensen_Huang --x nvidia --role "NVIDIA CEO"
# → assets/figures/<slug>.png (800x800 face-cropped) + <slug>.json {name, role, credit}
```

   Sources: Wikipedia/Commons original → current X avatar (unavatar) →
   Wikidata name-match last (it has returned the wrong "Tom Brown"; eyeball
   any `warn` line). **Always view the fetched portraits** (contact sheet)
   before choreographing; swap with `--name/--x --force` if a crop is a
   stranger or a decade old. Choreography (`templates/media_marks.py`):
   `figure_row(layer, slugs, cx, cy, lt, t0, place, names=True)` for a
   founders lineup (2 faces on the intro, 2–3 later, staggered, alternating tilt),
   `figure_spotlight(layer, slug, cx, cy, lt, t0, place)` when ONE person is
   the beat (hero portrait + name plate + role), `figure_card(slug, w=380)` /
   `figure_round(slug, 360, ring=CORAL)` as marks. **Face lands on the spoken
   word** (`word_onset(words, "anthropic")`), never early. Pair the row with
   the brand mark (Claude → invader + sphinx beside the Amodeis). Names in
   plates are first names for rows, full name + role for spotlights.

   **Figure circle size lock (Kevin 2026-09-14: "make them much larger…
   intro screens should be eye catching with big #s, figures, logos"):**
   the 150–220px rounds that kept shipping (phone-farm, anything-to-explain,
   open-source-trap hook) read as thumbnails, not icons. Floor:
   - **Hook / intro / cold-open:** these ARE the billboard. 1 face →
     `figure_spotlight(..., size=560)` or `figure_round(..., 520–620)`.
     2 faces → `figure_row(..., size=480, gap=12)`. Never 3+ tiny heads on
     the first section — pick the two most iconic. Pair with a 960-wide
     title **or** a `odometer_card` / `counter_card(..., h=440)` **or** a 400–520px logo
     badge; the slot should feel huge, not busy. Conveyor marks stay 110–140
     and sit under the giants, they do not replace them.
   - **Body sections:** single circle ≥280; 2–3-up row ≥320. Spotlight ≥480.
   - **Banned:** `figure_round(..., 150)` / `size=170` / `size=190` anywhere.
     If a 3-up row cannot fit at 320, drop to 2 faces and go bigger.
   Max one lineup per section. Intro faces may be the hero for up to 2.5s;
   later sections treat extra faces as supporting marks, still at the floor
   above — never shrunk to make room for a fourth.

5c. **PULL REACTION GIFs** (Giphy API, Kevin 2026-09-05). Punchlines, flexes,
   shocks and "I'm sorry CapCut" jokes get a real reaction GIF, not a text pill.
   `GIPHY_API_KEY` is in `.env.local (repo or project root)`; the dashboard's favorited
   allow-list (`gifs` table) is available via `--favorites`.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/fetch_giphy.py" --query "mind blown" --list   # look first
python3 "${CLAUDE_SKILL_DIR}/scripts/fetch_giphy.py" --query "mind blown" --slug mind-blown --pick 1
python3 "${CLAUDE_SKILL_DIR}/scripts/fetch_giphy.py" --favorites --query money --slug money-rain --mark-used
# → assets/gifs/<slug>/f0001.png … @30fps (≤4s, 720px wide) + meta.json
```

   Pick by title from `--list` (Kramer / Jon Stewart "mind blown" over a
   12-second anime loop). **Eyeball frame 1** before using: drop GIFs with
   slurs/subtitles, the wrong person, or a joke that misses the line.
   Play with `gif_card(..., w=400, frame="round")` for pairs under a title.
   Rules (china-robots lock): **one GIF per beat, 5–8 per video**, never the
   hero for >2.5s, never covering a 960px title card. Later-section stack is
   **title at cy≈125, pair of ~400px GIFs at cy≈450** (left/right). Hook
   frame 0 is the figure/number/logo billboard — do not cover it with a GIF
   pair unless the hook *is* B-roll. GIF audio is never mixed in. Rating pg-13.

5d. **TOPIC LOGO CONVEYOR — staple (Kevin 2026-09-10).** Every video gets a
   full-width horizontal scroll of the icons *associated with this edit*
   (the stack, products, companies, tools in the story — not random logos).
   Voice-agents showed OpenAI / Cursor / Docker / Cloudflare / … sliding
   under the faces. China-robots used Unitree / Tesla / NVIDIA / Meta /
   Boston Dynamics on "hardware + AI". That lane is the touch Kevin wants
   every time. Conveyor marks stay 110–140px; they are the stream, not the
   intro hero. On the hook, also `place()` 1–2 **giant** logos (360–520px)
   as billboard pieces next to the big figures / number (Kevin 2026-09-14).

   Fetch 5–8 real marks in step 5 (`fetch_brand_asset.py`). Punch white
   pads. Then one lane, one y-band, via `guarded_conveyor`:

```python
from media_marks import topic_marks
marks = topic_marks(["openai", "cursor", "docker", "cloudflare", "vapi"], size=120)
# y is authored cy; helper adds PACK_DY like china-robots
guarded_conveyor(layer, 400 + PACK_DY, max(0, lt - t0), marks,
                 conveyor_marks, name="topic-lane", speed=180, gap=22)
```

   Rules:
   - **At least one topic lane per video.** Cold-open it on the hook when
     the stack is the point, or enter on the spoken product/category beat.
   - 5–8 marks, ~110–130px, graphite badges (dark slot). Full slot width.
   - **One moving stream at a time** (already locked). The lane owns its
     y-band; no second conveyor / orbit on the same band; `lanes.reset()`
     every frame.
   - Marks must match the video. Do not fill with leftover icons from
     another project. Eyeball each PNG (wrong logo / broken SVG → drop).
   - Do not sit the lane on the caption line. Center ≤ `770 - size/2 - 10`
     after PACK_DY (half-sliced icons are a known fail).

6. **AUTHOR THE ANIMATION** (fresh per script): split narration into sections
   at spoken anchors using `audio/words.json` + `source/meta.json` `DUR`.
   **Density + look are locked to the china-robots recut**
   (china-robots (render.py no longer on disk; use social-agents / gitnexus as code refs), Kevin 2026-09-10):
   that is how animated every video in this format should feel. Target
   **6–10 elements on screen at once**, not 2–3 lonely cards.    Prefer
   **motion graphics over copy**: spinning logos, GitHub/product chrome
   (`shot_card`), terminals with ticking lines, skill-file grids, computer
   mockups, scan HUDs, force-directed graphs, brand badges, code
   rain, locks/skulls/bombs when the topic is hacks. Text cards caption a
   graphic, they are not the graphic.
   **Do not default every beat to `orbit_marks`.** The **topic logo conveyor
   is mandatory** (see `5d`). Rotate the *other* motion: zigzag, explode,
   ticker, cascade, loop-arrows, Ken Burns. One orbit per video is plenty.
   Scene content must MATCH what's being said. Set `DUR` from `meta.json`,
   not the template's 62.9s.

   **Cold open (locked, Kevin 2026-09-02):** frame 0 of the *video* must
   already be packed. Scroll-stop on TikTok/Reels shows the first frame.
   Atmosphere (terminal, skill tiles, ghost word, a logo that is legal to
   show) uses `place(..., t0=-0.4, dur=0.01)` so the ease-in has already
   finished. **Never** start the first beat at `t0=0` with `dur=0.3` — that
   leaves frame 0 blank. Skip the white flash on the **hook** section for
   the same reason.

   **Beat `t0` is the spoken word, not the section start.** For every punchline
   (a product name, a number, a claim), look up that word's start in
   `audio/words.json` and set `t0 = word_start - section_start`. Max lead is
   **0.1s**. Never put "300" / "2B" / a named plugin on screen while he is
   still winding up to say it — that spoils the line. Do not preview later
   named products in an earlier section (e.g. don't flash OmniRoute during
   "three core plugins"). Cold-open atmosphere is the exception: generic
   (computer, skills, "installing") can be up before the first named product.

6b. **EVERY SPOKEN NUMBER GETS A COUNTER (Kevin 2026-09-05).** Money, GitHub
   stars, downloads, views, followers, counts, years, percentages, "10 p.m.",
   "3 times a day": if the transcript says a number, a count-up animation
   lands on it. Run the detector while planning beats:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/number_beats.py"   # reads audio/words.json
#  26.40s   100  socials  <- "100 socials"
#  48.46s  $20/mo         <- "20 bucks a month"
#  51.02s  $2B            <- "$2 billion"
```

   `number_beats(words)` (in `hyper_edits.py`) understands digits, spelled
   numbers ("twenty five", "a hundred"), scales ("2 billion", "9.3k"), money
   ("$20", "20 bucks"), "%", "3 times", "10 p.m.", "per month" and a trailing
   label word (stars, downloads, views, socials, agents…). It skips bare
   version digits ("Gemma 4", "LTX 2.5"). Fix Whisper mishears in `words`
   first (see the nano-banana / "2 .5" fixes) so the detector sees the real
   number.

   **Apple counter lock (Kevin 2026-09-29: "find and implement a modern apple
   inspired odometer that'll replace the one we currently have, it's bad").**
   Every hero number, big or small, renders through `templates/apple_counter.py`
   (`counter_card` and `odometer_card` in media_marks both delegate to it, so
   old call sites just work). It is modeled on iOS `contentTransition(.numericText())`
   and keynote stat slides:

   - **SF Pro Display Bold digits** (macOS `/System/Library/Fonts/SFNS.ttf`,
     variable: weight 700, optical size 96) in tabular cells, on a frosted dark
     glass card with a hairline top highlight and a faint accent glow. Label =
     tracked caps in SF Pro Text with an accent dot. No boxes, wells, cages,
     progress bars or orange strips (the old boxed-reel odometer is dead).
   - **Rolling digits:** a place that changes slides up a short hop (0.34 of
     the cell) while the old digit fades out and the new one fades in, both
     edge-faded so nothing pokes above or below the line. A place spinning
     faster than about one digit per frame renders as ONE speed-blurred digit
     (true vertical box blur), never a half-and-half crossfade: that flickers
     as doubled digits.
   - **Odometer carry:** a place rolls only while every place below it is on 9
     and rolling, so the count never shows the next digit early (no
     "2,992,000,000" on the way to 2 billion).
   - **No leading zeros:** a new leading digit and its comma slide + fade in as
     the value reaches them, and the figure re-centers smoothly. Frame 0 of a
     count shows a clean "0", not "0,000,000,000".
   - **Full figures with live commas.** `2,000,000,000` not `2B`. Compact
     "2B" / "1.5M" is a chip or caption only, never the hero count.
   - **Easing:** ≥10k eases in-out so thousands -> millions -> billions
     visibly tick; smaller figures expo-out and settle. One tiny scale breath
     as it lands, never a pulse.
   - **Counts vs years:** a bare 1900-2099 with no label is treated as a year
     (no comma, rolls from value-40). Any counted figure ("2000 person academy",
     "1950 members") passes `"style": "count"` or a label and counts from zero
     with a comma (Kevin 2026-09-29: "2000" started at 1960).
   - **Timing.** Park the card at 0 up to ~0.2s before the number word (or
     from the section start as atmosphere). Count **on** the spoken number,
     land on the unit / scale word ("stars", "billion"). Max lead 0.1s.
   - **The counter is the only big piece while it counts.** Exit GIFs, the
     invader, the conveyor and hyperframe punches off the card; a light_hit
     ring on the landing word is fine.
   - Sizes: hero ≥10k `w=1000, h=400`; smaller heroes `w=440-560, h=300-320`.

   Author the hero beat by hand:

```python
NUM = {b["t"]: b for b in number_beats(words)}
bt = NUM[1.52]   # "two billion"
t0 = trel("two", a)          # spin starts on the number
t_land = trel("billion", a) + 0.15
p = 0.04 if lt < t0 else clamp01((lt - t0) / max(0.12, t_land - t0))
place(layer, odometer_card(bt, p, h=400, label="tokens / day"),
      540, 200, lt, trel("spend", a), dur=0.22, exit_at=t0 + 2.2)
```

   Smaller numbers (100, 646, 20%, $20) use `counter_card` (same Apple
   counter, sized to the figure). Fallback:
   `auto_counters(layer, BEATS, t, a, place, handled=HANDLED)` once per frame
   after the section choreography (`HANDLED` = the `t` values you animated
   yourself). Counter = a big piece (stacking rule applies): exit the
   previous hero before it lands, never park it on a stream lane.

7. **Pacing (locked):** nothing on screen >2.5s *as the hero*; supporting
   orbiting marks / code rain / ghost words stay through the beat. 0.3s
   directional entrances with ±8° tilt + overshoot pop; exits fly up before
   the next beat; per-section Ken Burns zoom; white flash cut at section
   starts **except the first section**; ghost words parallax-drift; something
   always moving (spinning marks, orbiting logos, ticking checks, terminals,
   a lane). **Motion variety, not pulse (Kevin 2026-09-11):** no element
   scale-pulses or bobs in sync; big pieces are still after they land;
   rotate entrances (slam, whip, drop-bounce, tilt-in, typewriter) so no
   two consecutive beats use the same move. If a stretch of >0.4s would only show a ghost word, add
   another graphic.

7b. **HYPER-EDIT LAYER (locked, Kevin 2026-09-05)** — `templates/hyper_edits.py`.
   The motion graphics are the *content*; the hyper-edit is the *cut*. Every
   video gets all of these, deterministic in `t`:
   - **Punch-ins and shake go on the ANIMATION SLOT, never the talking head
     (Kevin 2026-09-05).** Per frame: `layer = punch_zoom(layer,
     punch_scale(t, PUNCH_T, amt=0.045))` then `sx, sy = shake_offset(t,
     HIT_T, amp=14)` and `frame.alpha_composite(layer, (sx, LAYER_Y + sy))`.
     **Punches are RARE (Kevin 2026-09-12: "far too many zoom punch
     effects, annoying to watch").** `PUNCH_T = punch_beats(words,
     PUNCH_WORDS)`: hand-pick ONE hero word per section (the product name,
     the number, the CTA word), >=8 s apart, max 6/min, amt 0.045. Never
     `keyword_onsets(words, KEYWORDS)` for punches; KEYWORDS only colour
     captions. `speed_streaks` rides the same short list. Shake = section
     cuts + at most 3 claims. The band is composited at a fixed
     `(12, BAND_Y)` with no zoom or offset, always.
   - **Hyperframes = 1–2 frame accent inserts on cuts.** `hyperframe(frame, t,
     CUT_T, FPS, region=(0, LAYER_Y, W, AH))` cycles white → ink → invert →
     RGB-split so no two cuts flash the same. Animation slot only; the band
     never flashes. Never on the hook (frame 0 stays packed and clean).
     Never on an odometer while it is counting (Kevin 2026-09-15: the
     constellation overlay sat on top of the digits).
   - **Whip cuts between sections.** Replace the flat white flash with
     `whip_wipe(prev_layer, layer, lt / 0.16, direction=whip_dir(name))` for
     the first 0.16s of a section (outgoing scene pushes out motion-blurred,
     incoming pushes in). Whip **or** hyperframe on a given cut, not both.
   - **Shake on impact.** `HIT_T` = section cuts plus the 3 to 5 biggest
     claims; ≤0.26s, decays; applied to the slot offset (above).
   - **Spring / overshoot entrances.** `spring_preset(t, "snappy"|"bouncy"|
     "heavy")`, `ease_back_out`, `slam_in(img, p)` for hero numbers (1.6× →
     1 with overshoot). Rotate: not every card gets the same pop. Use
     `entrance(k)` for GIFs and cards so consecutive pieces differ, and keep
     `light_hit` / shake / hyperframe for the single dramatic beat of a
     section (Kevin 2026-09-12).
   - **Freeze hit** (`freeze_hit(band, p)`) for a record-scratch beat
     ("so I'm sorry CapCut"): band freezes, zooms 12%, paper tint + ink border
     for ~0.5s, then resumes. Max one per video.
   - **Text fx**: `count_up(300, p, suffix="%")` on stats (expo.out),
     `typewriter(text, p)` in terminals, `highlight_sweep` under the claim,
     `caption_impact(t, onset, key)` scales the caption with a squash bounce.
   Density check: the hyper-edit should make a 60s video feel like it has
   ~40 cuts even though the band is one continuous take.

7c. **No HTML overlay layer (Kevin 2026-10-02: "its actually bad").** The HyperFrames
   `hf_layer` overlay (`render_hf_layer.sh`, `hf_layer_frame`) is removed from the skill.
   Everything in the slot is drawn in the PIL compositor: kinetic titles, lower thirds,
   counters (`apple_counter.py`), terminals. Do not bring back an HTML/GSAP overlay.

7d. **LIGHT FX LAYER (locked, Kevin 2026-09-10).** `templates/light_fx.py`.
    The slot should feel lit, not flat cards on a flat wash. Every video
    gets a cheap light pass on the **animation slot only** (never the band):

    ```python
    from light_fx import (
        scanlines, hud_scan, neon_grid, slot_vignette,
        bloom_orb, rim_pulse, light_hit, light_rays, speed_streaks,
        caption_bloom,
    )
    # atmosphere — every frame, under or just over the graphics
    scanlines(layer, t)
    hud_scan(layer, t, accent)
    neon_grid(layer, t, STEEL)
    bloom_orb(layer, invader_x, invader_y, 200, accent, a=70)
    # hits — same t0 as the spoken word / GIF land / title slam
    light_hit(layer, 540, 300, t, t0, ORANGE)   # ring + sparks + flare
    speed_streaks(layer, t, PUNCH_T, NEON)
    slot_vignette(layer)
    # caption glow (draw on the canvas BEFORE the word)
    caption_bloom(frame, x, y, tw, 66, KEY_COL[wd] if key else SILVER)   # tight halo (word height), a<=40
    ```

    Atmosphere (scanlines + HUD scan + floor grid + a bloom behind the
    invader / hero) is on from frame 0. `light_hit` fires on every keyword
    punch, section cut, GIF land, and title slam. `light_rays` is reserved
    for the CTA / one hero flex — not every section. Copy `light_fx.py`
    into the workdir with the other templates.

8. **Compose** (`templates/split_55_45_compositor.py`, adapted in the workdir):
   - Canvas: **1080 × 1920**. If an old project still has `W, H = 720, 1280`,
     change it before encoding. Coordinates are 1080-space (center **x=540**).
     The template's Megan example still writes 720-era numbers and wraps them
     with `s()` (×1.5). New choreography should use 1080 numbers directly and
     must **not** double-wrap.
   - Animation layer: **1080 × 770**, composited **1:1** at `(0, LAYER_Y)`
     with **LAYER_Y = 90** (canvas 90..860). Apply **PACK_DY = 210** inside
     `place()` (and conveyor / orbit / explode / zigzag / ticker / waveform /
     ghost y) so the pack meets the caption line. Clamp y so assets stay
     inside the 770 slot. After the offset, heroes land around canvas
     y≈500–660; footer chips / receipts kiss y≈850. Cards ~960–990 wide,
     hero numbers ~960×400–520 (`odometer_card` for ≥10k, else `counter_card` h=380–480, intro h≥440),
     intro logos 360–520px, body logos 280–360px, conveyor marks 110–140.
     Author `place(..., cy)` in the old 200–400 hero range and let
     `PACK_DY` drop them — do **not** also author at cy≈500 or they will
     clip the captions. **Side inset:**
     keep every asset fully on-canvas. Left/right edges stay inside
     **x=36..1044** (`SAFE_X`). A ~450px file-tree / terminal parked at
     `cx=165` gets sliced off the left. Side-column pieces: `cx ≥ 270`
     for ~450px cards, `cx ≥ 180` for ~180px icons. Prefer `frm="up"` /
     `"down"` for left-column assets. **Do not** `R(..., 0.78)` shrink, and
     **do not** design at 853 then `resize((540, 640))`.
   - Band: **1056×960 at y=936**, rounded corners r=60 on **all four sides**
     (never `BAND_H+60` — that square-cuts the bottom flush to y=1920).
     ~24px of canvas stays under the card (Kevin 2026-09-15: y=960 sat too
     low and clipped the chin/body). 12px side margins.
     Read `renders/talking_band45.mp4` (already 30fps from prep). Hold the
     last frame if the clip runs short of `DUR`.
   - Kinetic captions **sit on the accent line on top of the band** (Kevin
     2026-09-18: "the text should be sitting on that pink line"; 2026-09-19:
     "the captions need to be above talking head" after a straddled word
     overlapped the cap; then "has to sit on top of that line, it's on it a
     bit"): Luckiest Guy, `anchor="ls"`, `stroke_width=7`, drawn at
     `y = BAND_Y - 8 - 7 - 3` so the STROKE's bottom edge touches the top of
     the accent line (line top is BAND_Y-8). Never center the word on the
     line, never let the stroke overlap it, never float it with a gap. One word, **Oswald Bold** ~66px, pop on word
     onset; KEYWORDS use `KEY_COL` (neon / orange / red) and ~18% bigger;
     body words are silver on the dark slot; black shadow. Caption windows
     disjoint using Whisper word times. Same face as title cards / chips /
     huge_word — never Arial.
   - Band file is `renders/talking_band45.mp4` (prep output). Hard-fail if missing.

9. **Encode + deliver:** frames → ffmpeg + the clip's narration audio
   (`audio/narration.m4a`), crf 16. Review a tiled overview + 2–3 full-res
   frames for collisions / crop. Stage a feed item in
   `brand-content/<persona-or-brand>/carousels/` only if publishing. Publish
   only on Kevin's go.

## Encode

```bash
ffmpeg -y -framerate 30 -i frames/out5/f%05d.jpg -i audio/narration.m4a \
  -c:v libx264 -pix_fmt yuv420p -preset medium -crf 16 -c:a aac -b:a 192k \
  -movflags +faststart -shortest renders/final.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=width,height \
  -of csv=p=0:s=x renders/final.mp4
# must print 1080x1920 — anything else is a failed render
```

Use the clip audio, not a TTS stand-in. Do not mix in trending/copyrighted
sounds (YouTube Content ID).

**Never mux `audio/narration.wav`** (Kevin 2026-09-22, minecraft-astra-jev: "why is
the audio bad?"). That file is the 16 kHz mono downmix prep makes for Whisper. Mux
`audio/narration.m4a` (the untouched 44.1 kHz stereo track) or, better, map the audio
straight from the original clip with `-c:a copy`:

```bash
ffmpeg -y -framerate 30 -i frames/out5/f%05d.jpg -i "<original clip>" \
  -map 0:v:0 -map 1:a:0 -c:v libx264 -pix_fmt yuv420p -crf 16 -c:a copy \
  -movflags +faststart -shortest renders/final.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate,channels -of csv=p=0 renders/final.mp4
# must print 44100,2 (or the source's rate) — 16000,1 means the Whisper scratch track got muxed
```

## Learnings (carried over + talking-head specific)

- **Caption glow is a tight halo (Kevin 2026-09-19: "the glow the captions give off is
  way too large"):** `caption_bloom` radius comes from the word height (th*0.55+10),
  alpha 40, never max(tw, th)/2+36. A wide word must not light up half the band edge.
- **Captions on the pink line (Kevin 2026-09-18, JEV video 3 screenshot):** the
  caption used to sit in the gap between the animation slot and the band
  (`CAP_BOTTOM - fs`, descender padding left a visible gap). Kevin wants the
  letters resting ON the line. First fix centered the word on the line and it
  covered the top of the cap (2026-09-19: "the captions need to be above
  talking head"). Locked: `anchor="ls"` at `y = BAND_Y - 5` (baseline on the
  line, glyphs above the head), drawn after the band. Then 2026-09-19 pm: "has
  to sit on top of that line, it's on it a bit" + the DOG screenshot: caption
  face is now Luckiest Guy with a 7px black stroke, baseline at BAND_Y-18 so the
  stroke bottom rests on the line top; no separate shadow (the stroke is the
  contrast). Title cards / chips stay Oswald. Template + both jev render.py updated; keep `caption_bloom` and the
  black shadow so silver reads on the bright room behind the head.

- **Oswald Bold is the overlay face (Kevin 2026-09-15, screenshot of AND
  over a code UI).** Title cards, chips, huge_word, captions, counters, name
  plates, ghosts: `AR` from `templates/fonts.py` → `fonts/Oswald-Bold.ttf`.
  Arial in the slot is a regression. Terminals / code rain / tickers stay
  Menlo (`ML`, `ImageFont.truetype(..., index=0)`). Copy `fonts.py` + the
  ttf with the other templates. Condensed type can run 8–12px larger than
  the old Arial sizes on the same 960-wide card.
- **Variety over repetition; effects for drama only (Kevin 2026-09-12: "on
  the gifs and stuff, i like animations but a variety. punches and stuff
  like that should apply for dramatic effect").** Rules: (a) no two
  consecutive GIFs / cards enter the same way, rotate with
  `hyper_edits.entrance(k)` (up / tilt-left / drop-pop / tilt-right /
  scale-up / slide / drop-tilt / pop-right) or hand-pick; (b) a GIF appears
  once per video unless it is a deliberate callback on the CTA; (c) impact
  effects (punch, shake, light_hit, hyperframe flash, slam) are reserved for
  the ONE dramatic beat of a section (the reveal, the number, the
  punchline), never on every chip and badge; (d) between beats the slot
  moves through entrances, lanes, terminals typing and GIF motion, not
  through camera hits. If a section has two hits inside 4 s, cut one.
- **Punch-ins were on every keyword (Kevin 2026-09-12: "far too many zoom
  punch effects. it makes it annoying to watch").** 30 keywords in a 37 s
  clip = a zoom every second plus speed streaks on each. Locked:
  `punch_beats()` in hyper_edits (one hero word per section, >=8 s apart,
  <=6/min, amt 0.045); KEYWORDS never drive the zoom again. Energy comes
  from entrances, GIFs, cuts and light hits, not from the slot jumping.
- **No black strip above the head (Kevin 2026-09-12, github-research-agent
  screenshot: "it just doesn't look good").** Kevin's recorder frames the
  head with a BLACK region above it and that boundary moves mid-clip
  (705 -> 772 at 30 s), so a face-box crop that starts above it ships a
  black bar at the top of the band for part of the video. `prep_talking_head.py`
  now scans the whole clip (`content_top`, every 0.5 s, max first-lit row),
  clamps `crop_top` under it, shrinks + upscales the crop when the picture
  below is shorter than 982 px, and `verify_band_top` refuses a band with
  black top rows anywhere. Rule: never fix this by lowering `--crop-top`;
  raise it. Eyeball band frames at 3 to 4 timestamps (not one) before
  compositing.
- **Partial edit / source passthrough (Kevin 2026-09-11, "only the first 15
  seconds needs edit, the rest is handled by broll, captions throughout").**
  When the source clip already carries its own split (screen recording over
  the head) after some point, set `CUT_AT` and animate only `SECT` before
  it; from `CUT_AT` write the SOURCE frame verbatim (`cv2` on
  `source/talking_head.mp4`, native 1080x1920) + `draw_caption()` at the
  same `CAP_Y`, plus one `hyperframe` on the cut.
  Reference: `clone-projects/first15-animated/render.py` (historical, not bundled). Check the source's
  own split line first (brightness-jump scan found y=944) so captions do not
  land on his B-roll's content.
- **2026-09-11 (Kevin, second-brain): "far too much pulsing my friend. i like
  effects but add variety."** Three things were breathing at once: `place()`
  bobbed EVERY element on the same 2.6s sine (the whole slot inhaled
  together), the word-mark cards ran `scale 1.04 yoyo repeat 3`, and the
  CTA card pulsed forever (`1 + 0.05*sin(6t)`). Locked: (a) big pieces
  (>=400px) never idle-move; small pieces drift <=3px with a per-element
  phase + period (3.2 to 5.6s) so nothing syncs; (b) no `yoyo`/`repeat`
  scale pulses, one overshoot settle then still, and each
  card gets a DIFFERENT entrance (whip from left, drop + bounce, letter
  spacing ease); (c) CTA = one slam + one `highlight_sweep`, then still;
  (d) `rim_pulse` only for the first 0.6s after a hit. Energy comes from
  cuts, hits, GIFs and entrances, never from everything wobbling.
- **2026-09-10 (Kevin, agentic-skills): go harder + light the slot.** Sparse
  2–3 card layouts read dead next to china-robots. Lock `templates/light_fx.py`
  on every recut: scanlines, HUD scan, neon floor grid, bloom behind the
  invader, `light_hit` (ring/sparks/flare) on punches and GIF lands, caption
  bloom on keywords. GIFs stay the front layer. Invader > sphinx when both
  exist. Density still china-robots (6–10 live elements).
- **2026-09-10 (Kevin, voice-agents screenshot): the horizontal logo
  conveyor is a staple.** Full-width scroll of icons associated with the
  video (OpenAI / Cursor / Docker / …). Required every cut — `5d` +
  `media_marks.topic_marks` + `guarded_conveyor`. One lane, topic-true
  marks only.
- **2026-09-10 (Kevin, github-research-agent): slot wash was too dark.**
  Lift CHAR to (48,50,58). `textured_bg` adds light patches + a stronger
  accent glow; do not composite `base-8` black sinks. `slot_vignette` at
  `a=22`, not 55. Reference compositor:
  `clone-projects/github-research-agent-animated/render.py` (historical, not bundled).
- **2026-09-10 (Kevin, china-robots): "INCREDIBLE EDIT THATS THE STANDARD."**
  Density, titles, GIFs, neon/orange/red. Compositor:
  china-robots (render.py no longer on disk; use social-agents / gitnexus as code refs). Do not regress to
  paper/sage/coral or a sparse 2–3 card layout. Use the brighter wash above.
- 2026-09-05 upgrade (Kevin): Giphy GIFs (`scripts/fetch_giphy.py` +
  `gif_card`), notable-figure portraits per niche (`scripts/fetch_figure.py` +
  `figure_row` / `figure_spotlight`), hyper-edit layer (`templates/
  hyper_edits.py`: keyword punch-ins, hyperframe inserts, whip cuts, shake,
  springs, freeze hit). All
  verified on the opensource-100 band. Wikidata name search returned the
  wrong Tom Brown → X avatar now outranks Wikidata; tiny Commons originals
  (<400px) are swapped for the X avatar too. Dashboard `DATABASE_URL` carries
  `uselibpqcompat`, which psycopg2 rejects; `_pg_dsn()` strips it.
- Whip + hyperframe on the same cut reads as a glitch storm. One per cut.
- **Density floor (Kevin 2026-09-08, cold-DM edit): "some parts of the animation
  screen were a little bit empty."** Every section must carry, from its first
  frame: at least 3 pieces on screen at all times (a hero/card, a mark or
  figure, a chip or lane), at least one GIF or one notable-figure per
  section, and something moving (lane, spinning mark, invader, count-up).
  Cold-open atmosphere at t0=0 for every section, never a lone chip. More
  memes, more public figures, more motion: if a beat has only a chip and a
  ghost word, add a figure row, a GIF, or a phone/terminal card.
- Numbers (Kevin 2026-09-05 + 2026-09-15): every spoken number is a
  counter, rendered by the Apple counter (templates/apple_counter.py, 2026-09-29):
  full figures, SF Pro rolling digits, odometer carry. Compact "2B" and the old boxed reels (orange cages, overflowing
  digits, "COUNTING TOKENS") are a fail. Run scripts/number_beats.py;
  auto_counters covers what the choreography misses. Bare version digits
  are skipped on purpose. The odometer is the only big piece while it
  counts — no GIF / invader / hyperframe on top of the digits.
- **Talking head locked (Kevin 2026-09-05, HF-hack intro):** the band punch-in
  and shake made the talking head move; Kevin does not want that. He DOES
  want the shake and impact beats, on the animation slot. Band is composited
  at a fixed (12, BAND_Y); the slot layer gets punch_zoom + shake_offset.
- **Band sits higher (Kevin 2026-09-15, ollama-claude-code recut):** y=960
  flushed the card to the bottom of the 9:16 and clipped the chin/body.
  BAND_Y=936, round all four corners, leave ~24px under the card. If the
  hat/crown is clipped, lower `--crop-top`; if the chin is clipped after
  that, the band position is the first lever, not a tighter crop.
- **One carousel per band (Kevin 2026-09-05, voice-agents hook).** Two
  conveyors on the same y, plus loose icons and the invader parked on top,
  read as four carousels stacked. Rules: one moving stream (conveyor /
  zigzag / orbit / ticker) per section at a time; it owns its y band
  (mark height + 6px) and nothing else is placed in that band; a second
  stream may only start after the first has exited. `hyper_edits.lanes`
  enforces it: call `lanes.reset()` at the top of each frame, draw streams
  through `guarded_conveyor(...)` (an overlapping stream is skipped and
  logged), and check `lanes.free(y0, y1)` before parking a card or the
  invader on a stream. No loose "$" icons as fillers: Kevin dislikes them.
  Fill with product marks, chips, or nothing.
- **Stacking rule (Kevin 2026-09-05, Kairos "unbelievable" beat):** a GIF
  card, a hero text card, the previous section's repo/shot card and the
  lower third all overlapped at once. Max **two big pieces**
  (>400px wide: GIF card, hero, shot/repo card, figure spotlight) live at a
  time; when a GIF or hero enters, `exit_at` the previous big card ≤0.1s
  before its `t0`. While a lower third is live (slot y≥600) nothing else
  is authored below cy≈380 (→ py 590). Left/right halves: GIF on one side,
  hero on the other, never both centered. Chips and marks are the only
  things allowed to overlap a card edge.
- GIFs are 720px frame banks (≤4s); a 12s Giphy loop is 360 PNGs — pick the
  short ones from `--list`.

- Frame 0 must be packed. `place(..., t0=-0.4, dur=0.01)` for cold-open
  atmosphere. `t0=0` + 0.3s ease + the hook flash = a blank first frame on
  scroll-stop (NVIDIA SkillSpector, 2026-09-02). Skip the white flash on hook.
  The packed frame is a **billboard** (Kevin 2026-09-14): one or two giant
  figure circles / a huge number / a huge logo, not three 170px heads plus
  chips. If frame 0 looks like a sticker sheet, it failed.
- **Intro figures + numbers + logos must be huge (Kevin 2026-09-14).**
  Hook `figure_round` 520–620 (or `figure_row` size=480 for two). Body floor
  280 / 320. Hero numbers: the Apple counter (`counter_card` / `odometer_card`, full figures) intro h≥400.
  Standalone intro logos 360–520.
  150–220px portrait circles are a regression.
- **Look + density gold standard is china-robots (Kevin 2026-09-10):**
  china-robots (render.py no longer on disk; use social-agents / gitnexus as code refs). Neon/orange/red accents,
  silver captions, 960px titles, full-slot B-roll, 5–8 memes, title-over-GIF
  stack, 6–10 elements live. **Slot wash is brighter** (Kevin 2026-09-10,
  github-research-agent): CHAR=(48,50,58), GRAPHITE=(36,38,46), lift the
  textured_bg instead of crushing it toward black, keep `slot_vignette` light
  (`a=22`). Near-black CHAR=(14,15,18) reads dead. NVIDIA SkillSpector
  (2026-09-02) is the older density floor — match china-robots energy on
  every video. Computer / hack / code talk still gets terminals, grids,
  conveyors, code rain — not a single text pill.
- Left-edge clipping: dense left stacks (file trees, warn icons, globes)
  were getting cut off on SkillSpector. Keep asset edges inside x=36..1044.
  Do not `place(..., 165, ...)` a 450px card. Clamp in `place()` if unsure.
- Whisper also drops or swaps the **opening word**. Play the first 2s of the
  clip before locking captions. "stop wasting" has been heard as "without wasting".
- Pack lock (opensource-100, 2026-09-03): `AH=770`, `LAYER_Y=90`,
  `PACK_DY=210`. Composite at `(0, 90)`, not `(0, 0)` or `(0, 42)`.
  `LAYER_Y=42` + `AH=840` + heroes at cy≈280 hugs the top and leaves a
  vacant band between the graphics and the captions. The pack must sit
  just above y≈867. Verify a frame: ink in the animation slot should end
  within ~80px of the caption line, not 250px above it.
- Cache card renders by state (`CACHE` dict) — ~1,900 frames in ~5 min.
- Live talking-head band is **1056×960 @ y=936** on **1080×1920**. Never
  704×640 on 720×1280 — that downscales a 1080p clip and Instagram wrecks it
  further (Kevin 2026-09-03). Recrop with lower `--crop-top` rather than stretching.
  Do not sit the band at y=960 (Kevin 2026-09-15: too low, bottom clipped).
- Named products get **real logos / GitHub cards**, not text pills. Fetch before
  authoring beats (`scripts/fetch_brand_asset.py`). Claude / Claude Code /
  Opus / Sonnet / Haiku / Fable / Anthropic always use the bundled invader +
  sphinx (`templates/claude_marks.py`) — never a generic favicon.
- Fill the animation slot **edge to edge** (1080×770 at y=90, 1:1). The
  slot is shorter and lower than the old 840@y=42 so content meets the
  captions. Downscaling an 853 canvas into 540×640 leaves a dead band
  between graphics, captions, and the talking head. Downscaling the whole
  video to 720p is forbidden.
- Beat `t0` = spoken-word start minus section start. Punchline graphics (names,
  numbers) appear **on** the word, never 4–6s early. Max lead ~0.1s.
- Prep transcodes the band to 30fps so cv2 reads 1:1 with render frames
  (phone clips are often 24/60fps, HeyGen was 25).
- Face-detect crop can miss side-on / backlit / hatted heads — `--crop-top` is the
  fix, not stretching. Haar face boxes ignore baseball caps; pad extra.
- Hard-fail if `renders/talking_band45.mp4` is missing or shorter than ~1s
  before composing. Do not fall back to HeyGen.
- Conveyor/orbit/zigzag y + PACK_DY must keep the FULL icon inside the 770px
  layer: `conveyor_marks` (and friends) don't clamp like `place()` does, so a
  conveyor authored at cy=560 (py→770 = the layer edge) renders a row of
  half-sliced icons (embracing-fanaticism, Kevin 2026-09-05: "cutoff and looks
  bad"). Keep stream centers ≤ 770 - icon_size/2 - 10 after py(), or add the
  clamp inside the helper.
- Live product b-roll inside a browser-chrome card in the animation slot is a
  PROVEN beat (embracing-fanaticism app section, Kevin 2026-09-05: "really
  good"). Map abs-time windows to source time, seek per frame, keep the
  window under a name_tag + scoreboard chip.
- Read the whole transcript for niche + vibe BEFORE authoring beats, and plan
  notable-figure portraits / GIFs into the choreography wherever the topic
  supports them ("content creator" talk → creator faces, "basketball app" →
  hoopers) — fetch_figure.py --niche + fetch_giphy.py. Placement doesn't have
  to snap to the exact spoken word; it flows from the plan. Named figures
  (MrBeast, Top G) stay mandatory (Kevin 2026-09-05).
- **Lower-thirds vs the topic lane (stop-the-slop, 2026-09-13):** a
  lower third at slot y≈640 lands on top of a `guarded_conveyor` at
  `490 + PACK_DY`. Gate every
  lane with the LT window (`if lt < t_named - 0.05 or lt >= t_after:`) so the
  lane exits before the lower third slides in. Also: `punch_beats()` is now
  used for real (5 punches on a 61 s clip); Whisper base.en heard "slop" as
  "slot" and "GPT" as "GBT" — fix words.json before number_beats/captions.
  Reference: `clone-projects/stop-the-slop-animated/render.py` (historical, not bundled).
- **Letterboxed source = black band bottom (2026-09-18, name-is-jef).** Kevin's
  recorder can export the picture as a 608 px strip (rows 656..1263) inside a
  1080x1920 frame. Prep clamps the crop top under the black but keeps
  `crop_h=982`, so the band ships ~320 black rows at the BOTTOM. Check the band
  sheet for black bottom rows too. Fix: measure lit rows, re-run prep without
  `--whisper` (keeps the fixed words.json) with a cover crop at 1056:960:
  `--crop-top 656 --crop-h 608 --crop-x <face_cx-334> --crop-w 669` (Haar face
  cx on the lit strip). Upscale is fine; letterbox is not.
  Reference: `examples/name-is-jef/render.py` (JEV / TypeSafe:
  pink brand accent, founder portraits scraped from typesafe.ai/team, pricing
  table + Pareto chart shots as b-roll, decision_row / action / yes-no / score
  cards, price wind-down + kinetic "one word at a time" + RL lower third).
- **Parallel RANGE chunks desync the band (2026-09-26, viktor-short).** The gitnexus loop reads
  `band_cap.read()` sequentially from frame 0, so `RANGE=261:522` renders the head from 0:00. Before the
  loop: `if todo and not PREVIEW: band_cap.set(cv2.CAP_PROP_POS_FRAMES, todo[0])`. Verified sync by
  diffing band crops vs `talking_band45.mp4` (diff <1 at the right frame). Reference:
  `examples/viktor-short/render.py` (assembled from gitnexus parts + `viktor_scene.py`).
  Also: small.en Whisper with `initial_prompt` of the product names fixed every mishear base.en made
  ("Claude"/"cloud", VIKTOR, "won't"); run it on shorts too, not just long-form.
