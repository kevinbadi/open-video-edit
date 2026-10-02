# OPEN VIDEO EDIT

**The world's best AI video editing harness.**

Hand Claude Code a raw talking-head clip and get back a finished, fully animated short: motion graphics,
kinetic captions, real logos, real faces, reaction GIFs, live b-roll cards, rolling counters and a
hyper-edit cut, all timed to the word you said. No timeline, no templates you drag around, no paid
generation. Every frame is drawn in Python and rendered locally.

Built and battle-tested on the [@KevBuildsApps](https://youtube.com/@KevBuildsApps) / Creator OS
channels, where it edits real videos every day.

---

## What's inside

| Skill | What it makes |
| --- | --- |
| [`split-animated-talking-head`](skills/split-animated-talking-head/SKILL.md) | **The flagship.** A 1080×1920 vertical short: your talking head in a rounded band at the bottom, a dense animated slot on top, Luckiest Guy captions resting on the accent line. |
| [`longform-animated-talking-head`](skills/longform-animated-talking-head/SKILL.md) | The same hyper-edit for 16:9 YouTube long-form: split view (animation slot + head card), zoom dissolves, chapter beats. |
| [`split-animated-short`](skills/split-animated-short/SKILL.md) | The 55/45 split format from a script or a source reel, for an AI avatar (HeyGen) instead of your own footage. |
| [`fireship-style-edit`](skills/fireship-style-edit/SKILL.md) | Faceless "Code Report" style tech news over a voiceover: 2.2s cuts, footage that literally shows what each line says, tweet/headline stacks, highlighted docs, built-up diagrams, memes. |
| [`fireship-style-short`](skills/fireship-style-short/SKILL.md) | The same Fireship grammar for Shorts / Reels / TikTok: 1080×1920, ~1.5s cuts, news footage as bands over a blurred fill, stickers in the safe slots, word-chunk captions. Shares the long-form engine. |
| [`reverse-engineer`](skills/reverse-engineer/SKILL.md) | **Learn any editing style.** Point it at a reference video: it measures cuts, shot lengths, things landing per minute, motion, faces/layout, palette, loudness and words per minute, builds contact sheets of every shot for the agent to study, then scaffolds iteration 1 of a new `<style>-edit` skill (numbers, rules, base engine) and proves it with a demo render. |

Each skill is a `SKILL.md` playbook (the rules, sizes, timings and every lesson learned the hard way)
plus the Python that does the work:

- **`scripts/`**
  - `prep_talking_head.py`: face-aware band crop that never ships a black bar, clean audio, and Whisper word timestamps (`small.en`, primed with your product names).
  - `fetch_brand_asset.py`: real logos from Wikimedia, simple-icons, GitHub or a site favicon.
  - `fetch_figure.py`: face-cropped portraits of the people behind a niche (Anthropic founders, OpenAI, Meta, GaryVee, Hormozi...).
  - `fetch_giphy.py`: Giphy search, downloaded as frame banks.
  - `number_beats.py`: finds every spoken number so it gets a counter.
  - `fetch_footage.py` (fireship): yt-dlp search → download (auto-updates on a YouTube 403) → 1 fps contact sheet → frame-accurate cut, with `--crop` for news picture-in-picture panels.
- **`templates/`**
  - `hyper_edits.py`: punch-ins, shake, whip cuts, 1–2 frame flash inserts, spring entrances, typewriter text, and a one-moving-stream-per-band lane guard.
  - `light_fx.py`: scanlines, HUD scan, neon floor grid, bloom, light hits, light rays and caption glow.
  - `apple_counter.py`: an iOS-style rolling odometer (SF Pro digits, carry, motion blur, live commas, year mode).
  - `media_marks.py`: GIF cards, logo badges, figure rows and spotlights, topic logo conveyors, a spinning globe.
  - `claude_marks.py`: the dancing Claude invader (look-at, grab, hold) and the starburst mark.
  - `split_55_45_compositor.py` / `longform_engine.py` / `fireship_engine.py`: the compositors.
- **`fonts/`**: Oswald Bold (overlays), Luckiest Guy (captions), Anton, Bangers, Space Mono, Inter, Press Start 2P.

### `examples/`

Real `render.py` files from shipped edits. These are the best way to learn the style:

| Example | Why it's here |
| --- | --- |
| `social-agents` | Rated "the best edit yet": b-roll banner reveal, zoomed live terminal, a ticking skill checklist with a visual per item. |
| `gitnexus` | The "new status quo": captions on the line, a meme on the spoken line, a custom motion piece on the next word. |
| `claude-hunger-games` | A fully custom world: ember-lit arena, 100 tributes spawning in waves, strategy trading cards, a 5-way clash with a scorecard, cannon, elimination countdown, crowned victor. |
| `claude-ads-api` | Invader shooting logos, hub-and-spoke API diagram, CEO columns, a step-by-step ad-builder pipeline with a panel per step. |
| `jev-app-store` | A screen recording mapped onto the script so the live card shows exactly what's being said, with real app icons cropped out of the footage. |
| `name-is-jef` | A product explainer with founder portraits, pricing and chart shots, decision cards. |
| `viktor-short` | Parallel chunked rendering, with the band kept in sync. |
| `viktor-intro-longform` | A 16:9 long-form cut. |
| `prompt-injection-fireship` | 60s Fireship-style cold open: 27 cuts, real event footage, a Wikipedia highlighter, an 8s diagram build, memes placed around their burned-in captions. |
| `weird-hack-fireship` | 60s long-form cut built from real BBC / CNBC / Bloomberg coverage: literal visuals on every line, two attack-chain diagrams. |
| `weird-hack-short` | The same story as a 60s vertical short through `fireship-style-short`. |

They reference their own `assets/` and `source/` folders, which are not included. Read them, copy the
patterns, don't run them as-is.

---

## How an edit runs

```
clip.mov
  └─ prep_talking_head.py ──► band (1056×960 @30fps) + audio + words.json (word timestamps)
       └─ fetch logos / faces / GIFs for everything the transcript names
            └─ render.py: sections cut at spoken anchors, every beat t0 = the word's start time
                 └─ PIL draws each frame: slot (graphics + light fx + hyper-edit) + band + caption
                      └─ ffmpeg: 1080×1920 H.264, the ORIGINAL clip's audio, crf 16
```

The talking-head audio is the master timeline. Graphics land **on** the word (max 0.1s early), never
while you're still winding up to say it. Final renders split into parallel chunks
(`RANGE=0:200 python3 render.py`), and a 30s short renders in a few minutes.

---

## Install

You need [Claude Code](https://claude.com/claude-code), Python 3.9+, and ffmpeg.

```bash
git clone https://github.com/kevinbadi/open-video-edit.git
cd open-video-edit
pip install -r requirements.txt          # pillow, opencv-python, numpy, openai-whisper, yt-dlp
brew install ffmpeg                      # or apt install ffmpeg

./install.sh                             # copies the skills into ~/.claude/skills
./install.sh /path/to/your/project       # or into that project's .claude/skills
```

Optional keys go in `.env.local` at your project root (see `.env.example`):

- `GIPHY_API_KEY`: reaction GIFs (free at developers.giphy.com).
- `HEYGEN_API_KEY`: only for `split-animated-short` avatar renders.

## Use it

In Claude Code, from the folder where you want your projects:

```
edit this talking head: ~/Downloads/my-clip.mov
here's b-roll of what I'm talking about: ~/Downloads/screen-recording.mp4
```

Claude loads `split-animated-talking-head`, preps the band, plans the beats against your transcript,
sources the logos, faces and GIFs, writes `projects/<slug>-animated/render.py`, checks preview frames
for collisions, renders, and hands you a 1080×1920 MP4.

Long-form: *"edit this landscape talking head"*. Faceless: *"make a Fireship-style video about X"*.

---

## Platform notes

- Built on macOS. It uses SF Pro (counter digits) and Menlo (terminals) when present, and falls back to
  the bundled fonts elsewhere.
- No HTML overlay layer: every pixel is drawn in Python.
- Logos, portraits and GIFs are fetched at edit time and are not redistributed here. Product names, logos
  and the Claude marks are trademarks of their owners.

## License

MIT for the code. Fonts are under their own open licenses (SIL OFL / Apache 2.0).
