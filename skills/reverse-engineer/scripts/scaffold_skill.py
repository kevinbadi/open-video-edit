#!/usr/bin/env python3
"""scaffold_skill.py: turn a style study into the FIRST ITERATION of a new editing skill
(step 3 of /reverse-engineer).

    python3 scaffold_skill.py --study studies/<slug> --name <style>-edit \
        --title "Fireship Code Report" --base fireship [--skills-dir .claude/skills]

Creates <skills-dir>/<name>/ with:
  SKILL.md                      frontmatter + the measured numbers table + the rules derived from them +
                                TODO blocks for what only eyes can learn (devices, text styles, layout)
  references/study.md           the full report (copied) + where the study folder lives
  templates/                    the base engine to build on:
      --base fireship           fireship_engine.py + fonts + marks (16:9 or 9:16 faceless B-roll engine)
      --base talking-head       split-animated-talking-head templates (vertical talking-head compositor)
      --base longform           longform-animated-talking-head templates (16:9 talking-head compositor)
      --base none               empty templates/ (write a new engine)
  templates/render_template.py  a starter render script wired to the base engine

It never overwrites an existing skill unless --force. The agent then fills the TODOs from the sheets
and proves the skill with a demo render (SKILL.md steps 4 and 5).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.abspath(os.path.join(HERE, "..", ".."))       # .../.claude/skills (sibling skills)

BASES = {
    "fireship": ("fireship-style-edit/templates", ["fireship_engine.py", "fonts", "assets"]),
    "talking-head": ("split-animated-talking-head/templates", None),
    "longform": ("longform-animated-talking-head/templates", None),
    "none": (None, None),
}

STARTERS = {
    "fireship": '''#!/usr/bin/env python3
"""First-iteration render for {name}. Built on fireship_engine (faceless B-roll engine).
Set FIRESHIP_CANVAS=9:16 BEFORE the import for a vertical style."""
import os
{canvas}from fireship_engine import *  # noqa: F401,F403

WORDS = words_onsets("audio/words.json") if os.path.exists("audio/words.json") else []
DUR = {dur}


def A(word, after=0.0):
    return at(WORDS, word, after)


SHOTS = []          # Shot(t0, t1, bg=..., layers=[Layer(...)]), cut every ~{median} s (measured)

if __name__ == "__main__":
    render(SHOTS, duration=DUR, out_dir=os.environ.get("OUT", "frames/out"))
''',
    "talking-head": '''#!/usr/bin/env python3
"""First-iteration render for {name}. Start from templates/split_55_45_compositor.py (copy it in as the
compositor) and re-tune its constants to the measured layout in SKILL.md."""
''',
    "longform": '''#!/usr/bin/env python3
"""First-iteration render for {name}. Start from templates/render_template.py of the longform skill
(copied here) and re-tune its layout constants to the measured layout in SKILL.md."""
''',
    "none": '''#!/usr/bin/env python3
"""First-iteration render for {name}: write the engine this style needs (PIL compositor, frames ->
ffmpeg). Measured pacing: cut every ~{median} s."""
''',
}


def rules_from(R: dict) -> list[str]:
    s, v, a, src = R["shots"], R["visual"], R.get("audio", {}), R["source"]
    out = [f"Hard cut every **~{s['shot_len_median']} s median** (p10 {s['shot_len_p10']} s, p90 {s['shot_len_p90']} s); "
           f"{s['under_1s_pct']}% of shots are under 1 s, {s['over_3s_pct']}% over 3 s."]
    if v.get("event_gap_median"):
        out.append(f"Something new lands every **~{v['event_gap_median']} s** ({v['events_per_min']} visual events/min): stickers, cards, "
                   "cutouts, zooms between and inside shots. Pace the layers to this, not only the cuts.")
    if v.get("longest_static_s", 0) <= 2:
        out.append("Nothing sits still: no near-static stretch longer than 2 s (something enters or moves at least that often).")
    else:
        out.append(f"Holds exist: the longest near-static stretch is {v['longest_static_s']} s; anything longer is off-style.")
    fp = v.get("face_on_screen_pct", 0)
    if fp < 15:
        out.append("Faceless: the narrator is never on screen; every second is B-roll.")
    elif fp > 60:
        out.append(f"Talking head on screen {fp}% of the time; face centred at x={v.get('face_center_x')}, y={v.get('face_center_y')}, "
                   f"face height {v.get('face_height_frac')} of the frame.")
    else:
        out.append(f"Talking head and B-roll alternate (face on screen {fp}% of the time).")
    if a.get("wpm"):
        out.append(f"Narration pace ~{a['wpm']} wpm with {a['pauses_over_0_35s']} pauses > 0.35 s in {src['duration']:.0f} s.")
    if a.get("loudness_range_lu") is not None:
        out.append(f"Mix: master to {a['loudness_lufs']} LUFS with LRA ~{a['loudness_range_lu']} LU.")
    ar = "9:16 vertical" if (src["height"] or 0) > (src["width"] or 1) else "16:9"
    out.append(f"Canvas {ar} ({src['width']}x{src['height']}), {src['fps']} fps source.")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--study", required=True)
    ap.add_argument("--name", required=True, help="new skill name, kebab-case, e.g. mrbeast-style-edit")
    ap.add_argument("--title", required=True, help="what was studied, e.g. 'MrBeast Shorts'")
    ap.add_argument("--base", choices=list(BASES), default="none")
    ap.add_argument("--skills-dir", default=SKILLS)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    R = json.load(open(os.path.join(a.study, "report.json")))
    dst = os.path.join(a.skills_dir, a.name)
    if os.path.exists(dst) and not a.force:
        sys.exit(f"{dst} exists (pass --force to overwrite)")
    os.makedirs(os.path.join(dst, "templates"), exist_ok=True)
    os.makedirs(os.path.join(dst, "references"), exist_ok=True)

    base_dir, items = BASES[a.base]
    if base_dir:
        src = os.path.join(a.skills_dir, base_dir)
        if not os.path.isdir(src):
            src = os.path.join(SKILLS, base_dir)
        for it in (items or os.listdir(src)):
            p = os.path.join(src, it)
            if not os.path.exists(p) or it == "__pycache__":
                continue
            q = os.path.join(dst, "templates", it)
            (shutil.copytree(p, q, dirs_exist_ok=True) if os.path.isdir(p) else shutil.copy2(p, q))

    s = R["shots"]
    vertical = (R["source"]["height"] or 0) > (R["source"]["width"] or 1)
    starter = STARTERS[a.base].format(name=a.name, dur=round(R["source"]["duration"], 2), median=s["shot_len_median"],
                                      canvas='os.environ.setdefault("FIRESHIP_CANVAS", "9:16")\n' if vertical else "")
    open(os.path.join(dst, "templates", "render_template.py"), "w").write(starter)
    shutil.copy2(os.path.join(a.study, "report.md"), os.path.join(dst, "references", "study.md"))

    today = dt.date.today().isoformat()
    src_ref = R.get("url") or R.get("file")
    rules = "\n".join(f"- {r}" for r in rules_from(R))
    table = "\n".join(f"| {k} | {v} |" for k, v in [
        ("cut every (median)", f"{s['shot_len_median']} s"), ("cuts / min", s["cuts_per_min"]),
        ("shots < 1 s / > 3 s", f"{s['under_1s_pct']}% / {s['over_3s_pct']}%"),
        ("something new lands every", f"{R['visual'].get('event_gap_median')} s ({R['visual'].get('events_per_min')}/min)"),
        ("face on screen", f"{R['visual'].get('face_on_screen_pct')}%"),
        ("longest near-static", f"{R['visual'].get('longest_static_s')} s"),
        ("wpm", R.get("audio", {}).get("wpm")),
        ("loudness / LRA", f"{R.get('audio', {}).get('loudness_lufs')} LUFS / {R.get('audio', {}).get('loudness_range_lu')} LU")])
    pal = " ".join(f"`{p['hex']}`" for p in R["visual"].get("palette", [])[:6])
    md = f"""---
name: {a.name}
description: Edit a video in the {a.title} style, reverse-engineered on {today} from {src_ref}. TODO (step 4) - one sentence on what the style looks like (layout, pacing, signature devices) and when to use it, written as trigger criteria.
---

# {a.title} style (iteration 1)

Reverse-engineered {today} by `/reverse-engineer` from {src_ref}.
Study (report + every sheet): `{os.path.abspath(a.study)}` (copy of the report in `references/study.md`).
**Learn the grammar; never copy their assets** (their footage, music, logo, show name).

## 1. The numbers (measured, hit these)

| metric | measured |
|---|---|
{table}

Palette (dominant colours): {pal}

Rules that follow directly from the numbers:
{rules}

## 2. Structure

TODO (step 4): read `audio/transcript.txt` + the shot sheets and write the section formula with timings
(hook, setup, body beats, payoff, CTA / outro) the way fireship-style-edit section 2 does.

## 3. Visual devices (engine function -> when)

TODO (step 4): one row per recurring device seen on the sheets: what it is, how it enters, how long it
holds, where it sits, which spoken moment triggers it, and the engine function that draws it
(existing in templates/ or written now).

| Device | Engine | Use it when the VO... |
|---|---|---|
| | | |

## 4. On-screen text + captions

TODO (step 4): fonts (closest open font in templates/fonts), colours, stroke, size, position, caption
track yes/no and chunking.

## 5. Pipeline

1. Words: Whisper `small.en` + names -> `audio/words.json`. Every beat keys off spoken words.
2. Shot list: `time | exact words | what is literally on screen | source`, one shot per ~{s['shot_len_median']} s.
3. Assets: real footage of what is named (`fireship-style-edit/scripts/fetch_footage.py`), logos, memes.
4. `render.py` from `templates/render_template.py`; preview one frame per shot; render in parallel chunks.
5. Copy the master to `~/Downloads/<Readable Name>.mp4`.

## 6. Don'ts

TODO (step 4): what would break the style (from the numbers: no shot longer than
{s['shot_len_p90']} s unless something builds, ...).

## 7. Learnings

- {today}: iteration 1 scaffolded from the study. Next: demo render (reverse-engineer step 5), then refine on Kevin's notes.
"""
    open(os.path.join(dst, "SKILL.md"), "w").write(md)
    print(f"ok {dst}")
    print("next: fill the TODOs in SKILL.md from the sheets, then build the demo render (reverse-engineer steps 4-5)")


if __name__ == "__main__":
    main()
