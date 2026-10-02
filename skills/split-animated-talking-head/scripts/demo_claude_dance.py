#!/usr/bin/env python3
"""Black-screen demo: Claude invader looks, grabs a SKILL.md card, dances.

Run:
  python3 scripts/demo_claude_dance.py
Writes projects/claude-dance-demo/renders/claude-dance.mp4
and copies to ~/Downloads/claude-dance.mp4
"""
from __future__ import annotations

import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.abspath(os.path.join(HERE, "..", "templates"))
sys.path.insert(0, TEMPLATES)

from claude_marks import (  # noqa: E402
    dance_path,
    ease,
    ensure_claude_marks,
    place_claude_invader,
    place_claude_sphinx,
    skill_chip,
)

from fonts import AR, F  # noqa: E402

W, H, FPS = 1080, 1920, 30
DUR = 12.0
N = int(DUR * FPS)


def main() -> None:
    root = os.path.join(os.environ.get("PROJECTS_DIR", os.path.join(os.getcwd(), "projects")), "claude-dance-demo")
    frames = os.path.join(root, "frames")
    renders = os.path.join(root, "renders")
    os.makedirs(frames, exist_ok=True)
    os.makedirs(renders, exist_ok=True)
    os.makedirs(os.path.join(root, "assets", "logos"), exist_ok=True)
    os.chdir(root)
    ensure_claude_marks("assets/logos")

    font = F(AR, 42)
    small = F(AR, 28)
    chip = skill_chip("SKILL.md", 220, 92)
    card_home = (820.0, 620.0)

    for n in range(N):
        t = n / FPS
        frame = Image.new("RGBA", (W, H), (8, 8, 10, 255))
        d = ImageDraw.Draw(frame)

        # Beat sheet
        # 0-2.8  idle dance, eyes follow the sphinx
        # 2.8-5.2 look at the card, reach, pick it up
        # 5.2-8.4 hold it, walk, glance at camera then back at the card
        # 8.4-10  morph burst (still holding)
        # 10-12   drop, wave, look at sphinx
        if t < 2.8:
            caption = "eyes follow"
            cx, cy = dance_path(t, W, H, margin=280)
            sph_xy = (W * 0.22 + 80 * math.sin(t * 1.4), 280 + 40 * math.cos(t * 1.7))
            look_at = sph_xy
            grab, grab_at, grab_t, hold = None, None, 0.0, None
            morph = 0.0
            card_xy = card_home
        elif t < 5.2:
            caption = "look + grab"
            u = (t - 2.8) / 2.4
            cx, cy = 420.0, 980.0
            sph_xy = (200.0, 260.0)
            card_xy = card_home
            look_at = card_xy
            grab, grab_at = "right", card_xy
            grab_t = ease((u - 0.15) / 0.7)
            hold = chip if grab_t > 0.55 else None
            morph = 0.0
        elif t < 8.4:
            caption = "carry"
            u = t - 5.2
            cx, cy = dance_path(t * 0.85, W, H, margin=300)
            cy = min(cy, 1200)
            sph_xy = (180.0, 240.0)
            grab, grab_t, hold = "right", 1.0, chip
            # glance at camera (center-up) then back at the held card
            glance = 0.5 + 0.5 * math.sin(u * 2.2)
            grab_at = (cx + 90, cy - 70)
            look_at = (W / 2, 400) if glance > 0.55 else grab_at
            morph = 0.0
            card_xy = None
        elif t < 10.0:
            caption = "morph"
            cx, cy = 540.0, 980.0
            sph_xy = (200.0, 260.0)
            morph = ease((t - 8.4) / 0.45) if t < 9.2 else 1.0 - ease((t - 9.2) / 0.5)
            grab, grab_at, grab_t, hold = "right", (cx + 80, cy - 80), 1.0, chip
            look_at = sph_xy
            card_xy = None
        else:
            caption = "drop + wave"
            u = (t - 10.0) / 2.0
            cx, cy = 540.0, 1020.0
            sph_xy = (W * 0.78, 300.0)
            # card falls
            fall = ease(min(1.0, u / 0.5))
            card_xy = (cx + 90, cy - 70 + fall * 420)
            grab, grab_at, grab_t, hold = "right", None, 0.0, None
            look_at = sph_xy if u > 0.35 else card_xy
            morph = 0.0

        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([cx - 180, cy + 110, cx + 180, cy + 180], fill=(206, 105, 87, 38))
        frame = Image.alpha_composite(frame, glow.filter(ImageFilter.GaussianBlur(22)))

        if card_xy is not None and hold is None:
            frame.alpha_composite(chip, (int(card_xy[0] - chip.width / 2), int(card_xy[1] - chip.height / 2)))

        place_claude_sphinx(frame, sph_xy[0], sph_xy[1], t, size=150)
        place_claude_invader(
            frame, cx, cy, t, size=360, morph=morph,
            look_at=look_at, grab=grab, grab_at=grab_at, grab_t=grab_t, hold=hold,
        )

        d.text((W / 2, 88), "CLAUDE", font=font, fill=(252, 250, 246, 230), anchor="mt")
        d.text((W / 2, 140), caption, font=small, fill=(160, 150, 140, 210), anchor="mt")

        frame.convert("RGB").save(os.path.join(frames, f"f{n:05d}.jpg"), quality=95)
        if n % 30 == 0:
            print(f"{n}/{N} {caption}")

    out = os.path.join(renders, "claude-dance.mp4")
    subprocess.check_call([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", os.path.join(frames, "f%05d.jpg"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "16",
        "-movflags", "+faststart", out,
    ])
    probe = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", out,
    ], text=True).strip()
    print("wrote", out, probe)
    dest = os.path.expanduser("~/Downloads/claude-dance.mp4")
    shutil.copy2(out, dest)
    print("copied", dest)
    if probe != "1080x1920":
        sys.exit(f"expected 1080x1920, got {probe}")


if __name__ == "__main__":
    main()
