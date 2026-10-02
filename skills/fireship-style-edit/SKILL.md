---
name: fireship-style-edit
description: Edit or build a FACELESS, Fireship "Code Report"-style tech news video (16:9, 1920x1080) — narrator never on screen, 100% B-roll (event footage, real article/doc screenshots with an orange highlighter sweep, tweet + headline card stacks, background-removed cutouts, meme cut-ins, slapped-on sticker text, built-up systems diagrams, glitch cuts) hard-cut every ~2 s over a continuous music bed at ~210 wpm deadpan narration. Use when Kevin asks for "Fireship style", a Code Report / news-roundup / "everything you missed" video, a faceless tech explainer, or a voiceover-driven B-roll edit. His own talking-head footage goes to longform-animated-talking-head / split-animated-talking-head instead.
---

# Fireship-style edit (faceless "Code Report" format)

Learned 2026-09-29 by reverse-engineering Fireship's *"Meta is pivoting again… everything you missed
from Connect 2026"* (5:40, 1080p, 23.976 fps). Full study (transcript with word times, cut list,
per-shot contact sheets, dense in-shot frame sheets, audio measurements):
`clone-projects/fireship-style-study/` (historical, not bundled) (`frames/sheet_*.jpg`, `frames/zoom_*.jpg`, `audio/`, `cuts/`).
**Learn the grammar; never copy their assets.** No Fireship footage, music, logo or the name
"Code Report" in our videos. Our show title is our own (default "The Kev Report").

Engine: `templates/fireship_engine.py`. Template + device demo: `templates/render_template.py`.
Real-page capture with in-page highlighter: `scripts/capture_page.mjs`.
Demo of every device: `~/Downloads/Fireship Style Demo Reel.mp4` (built from `clone-projects/fireship-demo/` (historical, not bundled)).

## 1. The numbers (measured, hit these)

| Metric | Fireship | Rule for us |
|---|---|---|
| Hard cuts | 107 in 340 s | a new shot every **~2.2 s median** (mean 3.2) |
| Element changes | new sticker / card / arrow every ~1–1.5 s inside shots | **nothing static > 1.5 s** |
| Longest shots | 31 s diagram build, 17 s doc highlight, 14 s phone-mock story | long shots are only allowed if they **build** (diagram grows, highlighter reads along, cards stack) |
| Narration | 1,207 words / 340 s = **213 wpm**, only 19 pauses > 0.35 s | jump-cut every breath out; VO is continuous |
| Narrator on screen | **never** | faceless, always |
| Burned-in captions | **none** | no subtitle track on screen (text appears only as stickers/cards) |
| Audio | continuous music bed ~2–3 dB under VO in gaps; loudness range **3.2 LU** | ducked bed + compressed VO, `mux()` normalises to −14 LUFS for YouTube |
| Aspect / fps | 16:9, 23.976 | 1920×1080, 30 fps (our stack) |

## 2. Script formula (Code Report structure, with timings from the study)

1. **Cold open, 0–65 s (~19%)**: first line is a deadpan absurd personal joke ("while I was finishing my
   certification to become a Metaverse real estate agent…"), then the news in one run-on sentence,
   the "and because [company] already knows what we're all thinking…" turn, then the promise:
   "In today's video we'll break down X, look at how it actually works under the hood, and find out
   if it's the future of Y or just [callback joke]."
2. **Date + title card, ~65 s**: "It is September 25th, 2026, and you're watching **[Show name]**." Title card on that line.
3. **History / context, 65–137 s**: "Now, this isn't [company]'s first attempt…" with an archival year label ("2018"), a stamp ("DISCONTINUED"), a punchline.
4. **How it works (the technical core), 137–198 s**: one long **diagram build** in sync with the narration, then the catch ("But ironically…", "and that's where he's still kind of lying").
5. **Rapid-fire product news, 198–277 s**: specs + price stickers ("$1,300", "$449"), famous-people B-roll with dry asides, one "one more thing".
6. **Sponsor, 277–332 s (~16%)**: segue from the last topic ("But if you'd rather not wait until December for… you can build… today with **[Sponsor]**"), a mini story told through the product's screen recordings.
7. **Outro, 8 s**: "This has been [Show name], thanks for watching, and I will see you in the next one." Title card + "link below" sticker.

**Voice rules**: deadpan, never hype words; a joke every ~10–15 s, usually as a hard-left turn at the
end of a factual sentence ("…send flowers to your wife's boyfriend"); callbacks to the cold-open
joke at the end of the intro; specific numbers and names always; pop-culture comparisons; mild
irreverence, but punch at companies and the powerful, not at groups of people. Keep sentences
long and rolling. The VO carries all the information; visuals carry the jokes.

## 3. Visual devices (engine function → when)

| Device | Engine | Use it when the VO… |
|---|---|---|
| Kinetic cold-open words on black | `kinetic_words()` | first 1–2 s, before the first image |
| Article/doc bursts in with a fisheye | `Layer(anim="bulge")` | introduces a source |
| **Orange highlighter read-along** | `doc_card(... phrase_spans())` or real page: `capture_page.mjs --highlight` → `highlight_image(img, boxes, p)` | quotes or paraphrases a doc: sweep p 0→1 across the spoken words |
| Full-bleed footage + slow push | `video_bg()` / `image_bg()` | describes an event, product, person |
| Logo slide-in + red block name | `Layer(img=logo, anim="slide_left")` + `sticker(name, "red_block")` | names a product the first time |
| Tweet stack (tilted, overlapping) | `tweet_card()` ×2–3, tilts ±2–4° | "people online are saying…" |
| Headline card stack | `headline_card()` light + dark, stacked, offset | "reports say…", controversies |
| Cutout walking over a card | `cutout()` (make with `npx hyperframes remove-background` or rembg) | a person reacts to / owns the thing on screen |
| Reaction-face collage strip | `collage_strip()` | "everyone's reaction" |
| Meme cut-in (full frame, 0.5–1.5 s) | Giphy via `split-animated-talking-head/scripts/fetch_giphy.py`, `bg=` frames | every punchline |
| Sticker text slapped on | `sticker(txt, style)`: `red_block` `starburst` `comic` `pink_plate` `price_box` `price_pop` `stamp` `name_plate` `quote` `year` `red_caps` | prices, names, years, one-word reactions ("BUT", "*GULP*", "FREE!") |
| Hand-drawn curved pointer | `curved_arrow()` | points at the exact UI element or line being named |
| Systems diagram that builds | `draw_diagram([DiagramItem...])`: purple frame + pixel caption, orange dashed box + labels, green/cyan/cream blocks, white arrows, **red arrows for the attack/fail path**, dropped-in icons | "the way it works is…" (one per video, 20–40 s) |
| Glitch cut | `Shot(glitch_in=True)` | ~1 in 5 cuts, on topic changes and punchline reveals, never every cut |
| Show title card | `title_card("The Kev Report", date)` | the date line + the outro |

Composition rules seen in every frame:
- Cards sit on the **near-black ground** `(14,14,16)`, centered or offset, never framed in a UI chrome.
- Overlaps are deliberate: second card overlaps the first by ~15–25%, opposite tilt.
- Stickers are **big** (100–220 px text) and tilted −12…+10°; they pop in with overshoot and then hold still.
- Brand marks are real (fetch with `split-animated-talking-head/scripts/fetch_brand_asset.py`).
- Every beat lands **on the spoken word**: `at(WORDS, "word", after)`, max lead 0.1 s.

## 4. Pipeline

```bash
WD=projects/<slug>-fireship && mkdir -p $WD/{audio,assets/{shots,logos,cutouts,gifs},frames} && cd $WD
cp "<skill>/templates/render_template.py" render.py
```

1. **Script** (section 2 formula, ~210 wpm → a 5 min video ≈ 1,050 words). Kevin records the VO, or
   ElevenLabs (voice id from `.env.local`), saved as `audio/voice.wav`. Jump-cut silences > 0.3 s
   (`ffmpeg silenceremove` or the HyperFrames CLI) before transcribing.
2. **Words**: Whisper `small.en` with `initial_prompt` = the product/people names → `audio/words.json`
   (`[[word, start, end]]`). Fix mishears first; every beat keys off it.
3. **Shot list**: walk the transcript, one Shot per ~2 s, one device per clause. Write it as a
   table (time | VO words | device | asset) before coding. Budget: ~1 meme per 15 s, 1 diagram, 3–6 doc
   highlights, 4–8 tweet/headline stacks, stickers everywhere.
4. **Assets** (before choreography): real pages via
   `node <skill>/scripts/capture_page.mjs --url … --selector … --highlight "exact phrase" --boxes x.json`
   (capture a clean base AND a boxes file so the highlight SWEEPS on the words); logos; Giphy memes;
   cutouts; event footage clips. Build a contact sheet and look at it.
5. **Author `render.py`**: `SHOTS = [Shot(t0, t1, bg=…, layers=[Layer(t0, t1, img=…, xy, tilt, anim)])]`
   with times from `at(WORDS, …)`.
6. **Preview**: `PREVIEW="1.0,5.2,…" python3 render.py` → tile the frames and LOOK (dead frames,
   stacked text collisions, a sticker covering the thing it points at).
7. **Render + mux**:
   ```bash
   N=$((DUR*30)); for i in 0 1 2 3; do RANGE="$((i*N/4)):$(((i+1)*N/4))" python3 render.py & done; wait
   python3 -c "from fireship_engine import mux; mux('frames/out','audio/voice.wav','assets/music_bed.mp3','renders/final.mp4')"
   cp renders/final.mp4 ~/Downloads/"<Readable Name>.mp4"
   ```
   Music bed: royalty-free/owned only (no trending or copyrighted tracks: YouTube Content ID).

## 5. Don'ts
- No face cam, no captions track, no bottom progress bar.
- No static frame > 1.5 s, no shot > 3 s unless something is building.
- No generic stock "AI brain" imagery: every visual is the actual thing being discussed.
- No Fireship assets, music, logo, fonts-as-branding or the "Code Report" name.
- Em/en dashes stay out of on-screen sticker text (house rule).
