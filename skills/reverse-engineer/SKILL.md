---
name: reverse-engineer
description: Reverse-engineer the editing style of any reference video (YouTube / Reels / TikTok URL or a local file) and turn it into the first iteration of a new editing skill. Measures pacing (cuts, shot lengths), motion, faces/layout, colour, loudness and speech pace, builds shot-by-shot contact sheets for the agent to study, then scaffolds `.claude/skills/<style>-edit/` with the measured numbers, a style bible and a starter engine, and proves it with a demo render. Use when Kevin says "/reverse-engineer", "learn this editing style", "copy how this video is edited", "make a skill from this video", or hands over a reference edit to match.
---

# /reverse-engineer: learn an editing style, ship skill iteration 1

This is how `fireship-style-edit` was born (2026-09-29: Fireship's "Meta is pivoting again" was
measured shot by shot, then turned into an engine + style bible). This skill makes that repeatable.

**Output:** a study folder (numbers + sheets) and a new skill folder `.claude/skills/<style>-edit/` that
renders a demo in that style. Learn the grammar; never copy the reference's footage, music, logo or show name.

## Step 1. Measure (`scripts/study.py`)

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/study.py" --url "<reference url>" --slug <style> \
    [--start 0 --dur 300] [--prompt "names, products"] [--out studies/<style>]
```

Downloads with yt-dlp (runs `yt-dlp -U` on a YouTube 403), trims to the span you want (default whole
video, max 10 min; 2 to 5 min is plenty for a long-form style, the whole thing for a short), then measures:

| What | How | Why it matters |
|---|---|---|
| cuts, shot length median / mean / p10 / p90, cuts per min, % < 1 s / > 3 s | ffmpeg scene detection (`--threshold 0.30`, lower = more cuts) | the pacing rule |
| **visual events** (things landing: stickers, cards, cutouts) per min + median gap | frame-difference spikes at 10 fps | layered styles (Fireship) change every ~1 s WITHOUT cutting; cuts alone read them as slow |
| longest shots | from the cut list | the "builds" (diagrams, read-alongs) worth copying |
| motion, near-static stretches | frame differencing at 4 fps | "nothing static > X s" |
| face on screen %, face centre, face height | OpenCV face detection | faceless vs talking head vs split / band layout |
| palette, brightness | k-means on sampled frames | colour tokens |
| loudness (LUFS), loudness range, pauses | ebur128 + silencedetect | mix + jump-cut density |
| words, wpm, transcript | Whisper `small.en` | narration pace, script formula |

Writes `report.md` / `report.json` (with measured verdicts) and the sheets:
- `frames/shots_NN.jpg`: ONE frame per shot, numbered, timestamped, with shot length.
- `frames/hook.jpg`: the first 3 s at 10 fps (what stops the scroll).
- `frames/dense_00_open.jpg`: the first 30 s at 2 fps (element changes inside shots).
- `frames/dense_0N_long.jpg`: the longest shots at 2 fps (how builds unfold).

If scene detection misses cuts (fades, whip pans, cuts between near-black cards) or double-counts
(flashes), rerun with `--threshold 0.15` / `0.3` and compare against the sheets. A cut list you didn't
check is a guess. Learned on the first test (Fireship, 2026-10-02): at threshold 0.3 it read 3.65 s per
shot because most changes are elements landing on a held black ground, not hard cuts; the visual-events
metric (a new element every ~1 s) is what captures that style.

## Step 2. LOOK (the part a script can't do)

Read every sheet with the Read tool (they are images). For each recurring element, write down:
what it is (card, sticker, meme, chart, cutout, caption, lower third, zoom, transition), how it
**enters** (pop, slide, whip, bulge), how long it **holds**, **where** it sits, what spoken moment
triggers it, its **text style** (font family look, colour, stroke, size, case), and how often it recurs.
Also: the hook (hook.jpg), the ending, caption track yes/no, layout (full-bleed, split, band, PiP),
transitions per minute. Zoom in on anything unclear: `ffmpeg -ss <t> -i source.mp4 -frames:v 1 x.png`
and Read it at full size. Fill the "Fill in from the sheets" block at the bottom of `report.md`.

## Step 3. Scaffold iteration 1 (`scripts/scaffold_skill.py`)

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/scaffold_skill.py" --study <study folder> \
    --name <style>-edit --title "<Creator / format name>" --base fireship|talking-head|longform|none
```

Pick the base engine closest to the style: **fireship** = faceless B-roll over a VO (16:9, or 9:16 when
the study is vertical); **talking-head** = vertical face-in-band compositor; **longform** = 16:9 talking
head; **none** = write a new engine. It creates `SKILL.md` with the numbers table and the rules that follow
from them, `references/study.md`, the base templates and a starter `render_template.py`.

## Step 4. Write the style bible (fill every TODO in the new SKILL.md)

- `description:` one sentence of trigger criteria (when Kevin should get this skill).
- **Structure**: the section formula with timings from the transcript (hook, setup, beats, payoff, CTA).
- **Devices table**: one row per recurring element from step 2, mapped to an engine function. If the base
  engine lacks a device, write it now (deterministic in t, PIL, cached) in `templates/`.
- **Text + captions**: closest open fonts (copy the TTFs into `templates/fonts/`), colours from the
  palette, stroke, size, position.
- **Don'ts**: what would break the style, phrased from the numbers.
House rules carry over to every new skill: literal visuals (fireship-style-edit section 0), real tweet
cards, no em/en dashes in on-screen text, the 10 s third-party clip rule, masters to `~/Downloads`.

## Step 5. Prove it: demo render

Build a 20 to 40 s demo in the new style using the new skill only (any VO Kevin supplied, or the study's
own audio for a side-by-side). Then compare against the reference:

1. Render, then run `study.py --file renders/demo.mp4 --slug <style>-demo` on your own output.
2. Put the two `report.md` number tables side by side: shot median, cuts/min, static stretches, face %,
   wpm, LUFS. Anything off by more than ~25% is a rule the skill didn't encode yet; fix the skill, not
   just the demo.
3. Tile both hook.jpg sheets next to each other and LOOK.
4. Copy the demo to `~/Downloads/<Style> Demo.mp4` and add a Learnings line to the new SKILL.md.

That is iteration 1. Kevin's notes on the demo drive iteration 2 (edit the SKILL.md rules and engine,
same as the Fireship skill's 10-02 literal-visuals pass).

## Don'ts

- No skill from numbers alone: step 2 (looking at every sheet) is mandatory.
- No reference assets in the new skill (their footage, music bed, logo, fonts-as-branding, show name).
- No "iteration 1" without a demo render and the side-by-side numbers check.
- Don't overwrite an existing skill (`--force` only when Kevin asks to redo it).
