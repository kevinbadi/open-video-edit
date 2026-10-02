---
name: longform-animated-talking-head
description: Edit a LANDSCAPE (16:9, YouTube long-form) talking-head clip Kevin records at his desk into a fast-paced animated hyper-edit — 1920x1080, split layout by default (animation slot left, his head in a ringed card right) with full-bleed and hero-slot layouts as accents, motion-graphic cards, real logos, Giphy reaction GIFs, YouTube thumbnails he drops in, kinetic phrase captions on an accent line, punch/shake on the slot only. No HeyGen. Use when the user hands over a landscape/long-form/YouTube talking-head video (intro, full episode, tutorial) and asks to edit it; vertical shorts stay with split-animated-talking-head.
---

# Long-form animated talking head (landscape 1920x1080)

Built reverse-first on the JEV AI x HyperEdit intro (2026-09-21, Kevin: "ya really good.
solid long form skill start"). Reference cut = **`clone-projects/jev-intro-longform-animated/render.py` (historical, not bundled)**
on top of `templates/longform_engine.py`. Same visual language as the short-form flagship
(Oswald + Luckiest Guy, graphite wash, neon/orange/red + brand accents, real marks, GIFs,
light fx, rare punches) but the canvas, layouts and hook rules are different.

## Locked rules for long-form (Kevin 2026-09-21)

1. **SPLIT is the default layout for talking-to-camera** (Kevin, screenshot of the
   CapCut/Premiere frame: "when i am talking full screen i like this editing layout you did
   the most"). Animation slot 1140x950 left, his head in the ringed 680x950 card right.
   FULL (face full-bleed + side overlays) only for the hook, one dramatic claim, the CTA.
   HERO (full-width slot + head PIP) only when a grid / thumbnails / b-roll IS the content.
2. **No mystery cold open.** Short-form gets the dark wash + "?"; long-form does NOT. Frame 0
   is a bright billboard on the ACTUAL topic (brand badges + wordmark + "the biggest update
   yet" chip beside the untouched face). Never darken the hook. No "?" badges later either.
3. **No bottom strip.** Progress bar / label / timecode / chapter name were "truly pointless".
   Accent line at y=1038, captions rest on it, nothing under it.
4. **Head never moves.** No punch_zoom / shake on the head in any layout. Slot layer only.
5. **Captions are phrase groups** (<=4 words, Luckiest Guy 60px, white, 7px black stroke,
   active word in `KEY_COL`, unspoken words dim STEEL), baseline resting on the accent line.
6. **Consistent palette + type across a series.** Pick brand accents once (`PINK` = Jev,
   `VIOLET` = HyperEdit; `CYAN` / `NEON` / `RED` per section) and reuse them every episode.

## Layouts (engine constants)

```
SPLIT  (default) slot 1140x950 at (40,46) LEFT + head card 680x950 at x=1200 RIGHT (1:1 HEAD_CROP from
       meta, r=44, accent ring). Slot-local px: title cy≈70, left cx≈330, right cx≈850, chips y≈700, lane y≈800.
FULL   head full-bleed 1920x1080 + transparent overlay 1920x1080, bottom gradient under the captions.
       Author overlays on the RIGHT (x 1300..1900) or a top wordmark (cy≈84); the face stays clean.
HERO   slot 1840x950 full width + head PIP 520x292 at (1330,690) with ring. Keep hero pieces out of
       the bottom-right 520x292; lanes may run behind the PIP.
```

Switch layouts on spoken anchors (every ~4–8 s keeps it action packed). Layout change =
0.24 s zoom-dissolve (outgoing view rendered live at the same t, incoming eases 1.035→1.0 scale);
same-layout section cuts whip. **No shake and no hyperframe flash on any section cut** (Kevin
2026-09-30: "I don't like the video shake transition from a different view"). Shake only fires on
`extra_hits` impact beats.

## Pipeline

1. **Workdir + prep** (clip must exist on disk; landscape 1920x1080 expected, others cover-crop):

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/setup_workdir.sh" <slug>        # projects/<slug>-longform/
cd projects/<slug>-longform
python3 "${CLAUDE_SKILL_DIR}/scripts/prep_longform_head.py" --clip "/abs/clip.mov" --whisper
```

   Writes `source/talking_head.mp4` (h264 30fps), `audio/narration.{wav,m4a}`, `audio/words.json`,
   `source/meta.json` (`DUR`, `HEAD_CROP` = 680x950 face-anchored crop for the SPLIT card) and
   `renders/head_sheet.jpg`. **View the sheet**: crown and chin inside the card, face ~42% down;
   override `--crop-x/--crop-top` if he drifts. Fix Whisper mishears in `words.json` first
   ("Jev"/"Jeff", product names) — captions, anchors and number beats all read it.

2. **Read the whole transcript** with timestamps and plan sections at spoken anchors
   (`tabs("word", after)` / `tabs_any([...], after)`). SPLIT by default; one FULL for the hook,
   HERO for the grid moments. "Action packed and fast paced": 6–10 live pieces in the slot,
   a beat on every named product / number / punchline, a GIF on every joke or flex.

3. **Source assets** (before choreography; scripts live in the short skill, call by path):
   - logos: `split-animated-talking-head/scripts/fetch_brand_asset.py` → `assets/logos/`. Proven
     marks (jev, typesafe, hyperedit, obsidian, github, capcut, premiere, youtube, ffmpeg,
     python, openai, gemini, deepseek) sit in `clone-projects/jev-intro-longform-animated/assets/logos` (historical, not bundled)
     — copy them. Claude family = bundled invader/sphinx. Premiere = Wikimedia SVG →
     `qlmanage -t -s 512`. CapCut = s2 favicon (`tool_badge` skips its white punch).
   - GIFs: `fetch_giphy.py --query ... --list`, pick by title, `--id <id> --slug <slug>`; ≤4 s;
     eyeball frame 1. One per beat.
   - thumbnails Kevin drops in → `assets/thumbs/thumb_<i>.png` → `thumb_card(i, w)` (crops the
     YouTube card to the 16:9 image, adds a play badge). Screenshots he pastes live in
     `/var/folders/.../TemporaryItems/NSIRD_screencaptureui_*/` — copy with `find -exec cp`
     (a plain `cp` on those paths fails in the sandbox).
   - figures: `fetch_figure.py` whenever a company / niche with famous faces is spoken.
   Build a contact sheet of everything and view it before authoring.

4. **Author `render.py`** from `templates/render_template.py`: `SECT`, `T_*`, `KEYWORDS`,
   `KEY_COL`, bespoke cards, `scene()`, then `run(SECT, scene, punch_words, extra_hits, ...)`.
   Engine cards: `chip / strike_chip / big_text_card / stamp_card / wordmark / ghost_img /
   ticker / draw_code_rain / sparkle_badge / round_logo / tool_badge + x_mark / terminal_card
   (typed lines) / timeline_card (fake NLE, playhead + agent cursor) / workflow_card (nodes
   light up) / thumb_card / demo_card / whisper_line`; plus `media_marks` (gif_card,
   logo_badge, topic_marks, figure_*, counter/odometer), `hyper_edits` (entrance(k), lanes /
   guarded_conveyor, punch_beats, whip, hyperframe), `light_fx` (light_hit, light_rays,
   bloom_orb, speed_streaks) and `claude_marks` (invader / sphinx).
   Beat `t0` = spoken word (max 0.08 s lead via `r(T)`); cold-open atmosphere with
   `place(..., -0.35, dur=0.01)` so each section's first frame is packed; `exit_at` the
   previous big piece ≤0.06 s before the next hero; rotate `entrance(k)`; punches = ONE hero
   word per section (>=8 s apart); `extra_hits` = the 3–5 biggest claims.

5. **Preview, then render**:

```bash
PREVIEW="0.0,2.2,5.5,12.6,21.5,29.5,44.6,52.2" python3 render.py      # frames/out/f<n>.jpg
bash "${CLAUDE_SKILL_DIR}/scripts/render_parallel.sh" "Readable Name" 4
# → renders/final.mp4 (1920x1080, the clip's audio, crf 16) + ~/Downloads/Readable Name.mp4
```

   Tile the preview frames (3 columns at 960x540) and LOOK for: pieces under the head card /
   PIP, empty halves (add a terminal, lane or badge), a FULL-layout title over the cap, stamps
   over GIFs. Kevin reviews from ~/Downloads; keep the project for re-renders.

## Learnings

- **2026-09-21 v1 → v2 (JEV intro):** dark hook + "?" = wrong for long-form ("it just needs to
  hook the user into the actual topic"); bottom timeline strip = "truly pointless". Both
  removed; slot/head card grew to 950 tall. Approved: layout switching, phrase captions on
  the line, X-marks over CapCut/Premiere on the spoken word, GitHub fork grid on "hundreds",
  thumbnails on "three video updates", Jev slam + rays, fake timeline, workflow nodes, code
  tree, demo card + "INSANE" stamp. Then: SPLIT named the favourite layout for talking.
- HEVC .mov from Kevin's recorder: transcode to h264 30fps first (cv2 reads sequentially,
  seeks only at a RANGE start). 1572 frames render in ~3 min across 4 chunks.
- Long-form Whisper: `small.en` (base mishears more on a long clip).
- 10-minute clips: ~60–90 sections; ~0.15 s/frame/process → 18k frames ≈ 12 min on 4 chunks.
- **2026-09-25 VIKTOR intro** (`examples/viktor-intro-longform/render.py`): Kevin's raw clip had
  logo SLATES baked in (black frame + product logo, no face) at 35.4–37.9 s and 75.5–78.0 s → the head
  card rendered black. Scan every source for dark runs first (`frame[::8,::8].mean() < 40`) and put those
  spans on `"SOLO"` (any non-SPLIT/FULL/HERO name = full-width slot, no head, no PIP); boundaries must
  land on the first real frame. Name-drop reveal + five-fields board went there. Also: `wordmark()`
  clips tall Oswald digits / its `sub` overlaps at big sizes → use a textbbox-sized `big_num()` + a chip;
  Oswald has no ✓ glyph (Menlo does, so terminals are fine); white-bg Wikimedia logos need a white-trim
  crop before `logo_badge(punch=False, fill=WHITE)`.
