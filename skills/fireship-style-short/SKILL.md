---
name: fireship-style-short
description: Vertical (9:16, 1080x1920) short-form version of the Fireship "Code Report" editor for Shorts / Reels / TikTok, 30 to 60 s over a voiceover or any audio overlay. Faceless, 100% B-roll that LITERALLY shows each line (real news/event footage as full-width bands over a blurred fill, Wikipedia/doc highlighter cards, real tweet cards, built-up diagrams, meme cut-ins, slapped-on stickers), hard cut every ~1.5 s, word-chunk captions in the safe zone. Use when Kevin asks for a Fireship-style short, a vertical / shorts version of a Fireship edit, or a faceless news short. Long-form 16:9 goes to fireship-style-edit; his own face goes to split-animated-talking-head.
---

# Fireship-style SHORT (vertical faceless news short)

The long-form skill (`fireship-style-edit`) is the source of truth for the grammar: **read its section 0
(LITERAL VISUALS) and section 3 (devices) first.** This skill only changes what a phone needs. Both
skills share one engine: `fireship-style-edit/templates/fireship_engine.py`, which switches to 1080x1920
when `FIRESHIP_CANVAS=9:16` is set before import. `templates/short_kit.py` sets that and adds the
vertical helpers, so a short's `render.py` starts with `from short_kit import *`.

Reference build: `examples/weird-hack-short/render.py` (the 60 s vertical cut of "The most
interesting hack in history just got weirder", built from the same footage as the long-form edit).

## 1. What changes for vertical

| | Long-form (16:9) | Short (9:16) |
|---|---|---|
| Canvas | 1920x1080 | **1080x1920** |
| Length | 5 min | **30 to 60 s** (one story, one payoff) |
| Cut rate | ~2.2 s median | **~1.5 s median**, nothing static > 1.2 s, diagram builds ≤ 8 s |
| Captions | none | **word-chunk captions ON** (most views start muted): Luckiest Guy, white + black stroke, keywords yellow, the spoken word pops. `CAPTIONS=0` for a pure Fireship look |
| 16:9 footage | full-bleed | **`footage_band()`**: full-width band over a blurred, darkened fill of the same footage. Keeps news lower thirds and faces. `footage_fill(fx=…)` only when the subject is centred |
| Memes | full-bleed | **`gif_band()`**: same band treatment, so burned-in captions stay readable |
| Cards | 1200-1500 wide | **`card(...)` / `fit_w()`** shrink every tweet / headline / doc / bench card to 960 wide |
| Diagram | wide, left→right | **tall, top→bottom** inside `(60, 260, 1020, 1300)`; blocks ≥ 420 wide so labels stay readable |
| Hook | kinetic words on black | **frame 0 must be a picture**: footage band + the first words as a big sticker. A black opener loses the swipe |
| Ending | title card + outro | **payoff or loop line** as the last shot; a "comment X" sticker if there is a CTA |

## 2. Safe zones (platform UI covers these)

- **Top 200 px**: status bar, search, "Shorts" header. Stickers start at y ≥ 220.
- **Bottom 460 px (y > 1460)**: title, channel, audio ticker. Captions sit ON the 1360 line (baseline),
  nothing else goes below 1300.
- **Right rail** (x > 960, y > 900): like / comment / share buttons. Keep stickers left of it down there.
- The band's centre is `BAND_Y = 760`: stack a sticker ABOVE the band (y 220–420) and one BELOW it
  (y 1080–1210, slot STICKER_BELOW = 1150). Never on top of the faces / lower third inside the band.

## 3. Pipeline

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/setup_short.sh" <slug>        # projects/<slug>-short/ with engine + kit
cd projects/<slug>-short
# audio: the VO / overlay, trimmed to the short (30-60 s)
ffmpeg -t 60 -i "<audio>" -ar 48000 audio/voice.wav
# words: Whisper small.en + initial_prompt (names) -> audio/words.json   (same as long-form)
# footage: the long-form skill's fetch_footage.py (search -> download -> 1 fps sheet -> --cut [--crop])
python3 ../../.claude/skills/fireship-style-edit/scripts/fetch_footage.py --search "<person> <event>"
```

1. **Shot list** (`time | exact VO words | what is literally on screen | source`), ~1 shot per 1.5 s.
2. **Assets**, literal-first: footage of the named people/events, real docs (`wikipedia_extract` +
   `wiki_doc`), real tweet cards (X mark + avatar), logos, memes (check burned-in caption position).
3. **`render.py`** from `templates/render_short_template.py`: `Shot(...)` list exactly like long-form,
   but backgrounds come from `footage_band` / `gif_band` / `image_band`, cards go through `card()`, and
   `render(SHOTS, DUR, post=make_captions(WORDS, KEYWORDS))`.
4. **Preview** one frame per shot (`PREVIEW=...`), tile at 270x480, LOOK: captions clear of stickers,
   nothing in the safe zones, faces/lower thirds in the band uncovered.
5. **Render** in 4 parallel `RANGE` chunks, `short_mux('frames/out', 'audio/voice.wav', 'renders/final.mp4')`,
   copy to `~/Downloads/<Readable Name> (Short).mp4`.

## 4. Clip + audio policy (Kevin 2026-10-02)

Any clip and any audio may be used in our edits (news footage, event footage, memes, a creator's
audio overlay). Kevin's rule: **no single third-party clip on screen for more than 10 s in a row.** Cut
away (sticker shot, diagram, meme) before 10 s and come back if needed. Don't add copyright caveats to
deliveries. The continuous music bed is still owned / royalty-free, because it runs the whole video.

## 5. Don'ts

- No black or empty first frame. No static frame > 1.2 s.
- No sticker or card inside the safe zones, none over a face or a news lower third.
- No long-form-sized cards dropped in unscaled (they spill off a 1080-wide frame).
- No caption track fighting a sticker at the same height: stickers above the band or at 1080–1280,
  captions on 1360.
- Everything in the long-form Don'ts still applies (literal visuals, real tweet cards, no em/en dashes in
  sticker text, no Fireship branding).
