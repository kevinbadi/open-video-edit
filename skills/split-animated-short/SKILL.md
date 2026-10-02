---
name: split-animated-short
description: Turn a video script OR a source video URL (IG reel / YouTube / TikTok) into a 55/45 split-format vertical short — custom-generated animations in the top 55%, the AI persona (Megan/Danny) talking in a rounded band across the bottom 45%, narration + kinetic captions synced to the persona's voice. Zero source pixels used. Trigger when Kevin drops a script or a short-form video link and wants the split animated version for a persona.
---

# Split Animated Short (55/45 — LOCKED FORMAT, Kevin 2026-07-12)

Kevin's flagship original-content format: "video script / video download →
video clone + custom animation recreate." Every frame is generated — the
animations are authored per script, the persona narrates, nothing is copied
from the source video except its words.

Reference implementation (first approved video):
`clone-projects/Danc08PA0kz-animated/` — `render5.py` (the 55/45 build) +
`render2.py` (asset library + beat engine). Copies live in `templates/`.
Per video, create `projects/<slug>-animated/` and adapt.

## Persona constants (vertical looks)

Fill in your own HeyGen looks (HeyGen dashboard → Avatars / Voices, or `GET /v2/avatars`):

| persona | talking_photo_id (vertical) | voice_id |
|---|---|---|
| persona-a | `<TALKING_PHOTO_ID>` | `<VOICE_ID>` |
| persona-b | `<TALKING_PHOTO_ID>` | `<VOICE_ID>` |

**Your own avatar** (char_type `avatar`, not a talking_photo): submit with
`{"type":"avatar","avatar_id":"<AVATAR_ID>","avatar_style":"normal"}` and its
`voice_id`. Some avatar renders come back LETTERBOXED (content ~y648-1296 of the
1080x1920 frame, light bars above/below). Band crop that fills 704x578
head-anchored with no bars: `crop=731:600:90:665,scale=704:578,fps=30`. The
persona guard still applies: an avatar speaks first-person and never names the
creator it was cloned from. Sections can auto-align to the avatar's narration
with a two-pointer aligner over the Whisper words (no hand-timed SECT).

Env: `HEYGEN_API_KEY`, `APIFY_TOKEN`, `INSFORGE_*` (`.env.local`).
Cost: HeyGen ≈ 1 quota/second of narration; everything else is local.

## Pipeline

1. **Get the script.**
   - Script given → use it directly.
   - URL given → IG reels: Apify `apify~instagram-scraper` (`directUrls` +
     `resultsType: "details"`) — yt-dlp CANNOT fetch IG even with cookies;
     the returned CDN `videoUrl` is short-lived, download immediately. The
     item's `caption` is GROUND TRUTH for fixing Whisper mishearings.
     YouTube/TikTok: yt-dlp. Then Whisper (base, word timestamps).
2. **Correct + guard the script.** Fix product names against the caption
   (whisper renders "Claude"→"Clod", "submit"→"admit", etc.). Persona-swap
   any identity (Kevin/Kev → persona; also strip other creators' names).
   HARD GUARD before HeyGen: refuse if /\b(kev(in)?|nick|saraev)\b/i.
3. **HeyGen narration** — ONE job, persona's VERTICAL look, 1080x1920,
   `{"type": "talking_photo", "talking_photo_id": ...}`. ENERGY SETTINGS
   (Kevin 07-13, tuned over two runs): voice `"speed": 1.10` + `"emotion":
   "Excited"` → ~3.25 words/sec — LOCKED DEFAULT (1.15 was "slightly too
   fast"). Write the script punchy AND WITH PERSONALITY — named frameworks
   and attitude, not plain advice ("the throw shit at the wall framework",
   "stalk your analytics like it's your ex's new girlfriend", "never let
   the algorithm catch you lacking"). On-screen text censors profanity
   Nick-thumbnail style (sh*t) via a caption CENSOR map; spoken audio
   stays uncensored. Original-concept videos: pick tips that ARE Creator
   OS features (post-everywhere / winners analytics / week scheduling) so
   the CTA is the natural payoff. The video
   doubles as the band footage; the audio is the master timeline. Whisper
   the narration → `words.json` (all sync flows from HER timing — no
   speed-matching, this is original content).
4. **AUTHOR THE ANIMATION** (the creative step — done fresh per script):
   split the narration into sections at spoken anchors ("first…", "next…",
   CTA), then pack **6–10 elements on screen at once** (NVIDIA SkillSpector
   recut, Kevin 2026-09-02 — that density is locked for every split video).
   Prefer motion graphics over lonely text pills: terminals, product logos,
   skill grids, screenshots, orbiting marks, HUDs. **Claude family is locked
   (Kevin 2026-09-03):** copy `split-animated-talking-head/templates/claude_marks.py`
   and `assets/claude-invader.png` + `claude-sphinx.png`. Whenever the
   narration says Claude, Claude Code, Opus, Sonnet, Haiku, Fable, or
   Anthropic, call `place_claude(...)` — dancing block invader + spinning
   Sphinx badge. Eyes `look_at=(x,y)`, arms `grab="right"` / `grab_at` /
   `grab_t` to pick things up. Never a favicon. Keep asset edges inside
   x=36..1044 so left-column pieces aren't sliced off. Asset library:
   `templates/animation_assets_and_beats.py`. Scene content must MATCH
   what's being narrated at that moment.
5. **Pacing rules (Kevin: "users don't have attention spans")**: nothing
   on screen >2.5s; 0.3s directional entrances with ±8° tilt + overshoot
   pop; exits fly up before the next beat; per-section Ken Burns zoom;
   white flash cut at section starts (ANIMATION REGION ONLY — persona
   stays stable); ghost words parallax-drift; something always moving
   (spinning arrows, ticking checks, pulsing CTA, bouncing arrow that
   points DOWN at the persona on the comment CTA).
6. **Compose 55/45** (`templates/split_55_45_compositor.py`):
   - Animation layer renders TRANSPARENT in the 720x853 design space, then
     uniform-scales 0.823x into the top 702px (no distortion, 64px side
     pads on top of the 60px in-layer safe zones; keep content ≥90px from
     the layer top for platform UI).
   - Persona band: 704x578 at y=702, rounded TOP corners r=40, 8px side
     margins (background shows through). CROP RULE: start a SLIVER above
     the top of her head (y≈420 in the 1080x1920 HeyGen video for Megan's
     look) — no headroom, so her movement plays against the band edge.
     Pre-transcode the band to 30fps (HeyGen outputs 25fps; cv2 must read
     1:1 with render frames).
   - Kinetic captions at y≈636 in the gap: one word, Arial Bold ~44px,
     pop on word onset, KEYWORDS (product words, numbers, hook words)
     render CORAL and ~18% bigger; dark ink on light scenes, white on
     sage; caption windows DISJOINT BY CONSTRUCTION (whisper word times
     overlap).
7. **Encode + deliver**: frames → ffmpeg + narration audio (crf 19).
   Review a tiled overview + 2-3 full-res frames for collisions. Feed
   item in `brand-content/<persona>/carousels/` (remote Insforge URL
   slide). Publish to the persona's socials only on Kevin's go.

## Learnings baked in
- Animation density: 6–10 live elements, SkillSpector recut energy, on
  every video. Left/right edges stay inside x=24..696 (left stacks clip).
- Whisper mishears product names — always cross-check the source caption.
- HeyGen speaks ~25-30% slower than typical creators; irrelevant here
  (her audio IS the timeline) but relevant if ever matching source pacing.
- Cache card renders by state (CACHE dict) — 1,900 frames in ~5 min.
- Ratio history: 2/3-1/3 → 3/5-2/5 → **55/45 LOCKED** (Kevin) with the
  tight head crop.

## 2026-09-05 upgrade (shared with split-animated-talking-head)

The persona variant uses the same new layers. Copies of the scripts and
templates live in this skill's `scripts/` and `templates/`; the rules are in
`split-animated-talking-head/SKILL.md` steps 5b (notable-figure portraits per
niche, `fetch_figure.py` + `figure_row` / `figure_spotlight`), 5c (Giphy
reaction GIFs, `fetch_giphy.py` + `gif_card`), 7b (hyper-edit layer:
keyword punch-ins on the persona band, hyperframe inserts, whip cuts, shake,
springs, freeze hit — `hyper_edits.py`). Follow them on every video. No HTML
overlay layer: the HyperFrames `hf_layer` was removed (Kevin 2026-10-02).
