#!/usr/bin/env python3
"""fetch_footage.py: real event footage for Fireship-style B-roll, via yt-dlp (no browser).

The literal-visuals rule: when the VO says "the Prime Minister of Australia stood up at the UN",
the shot is footage of that person at that podium. This finds it, downloads it, shows you a
timestamped contact sheet so you pick the exact moment, and cuts an accurate H.264 clip.

  # 1. find candidates (duration | id | title); prefer short uploads (< 10 min)
  python3 fetch_footage.py --search "Anthony Albanese UN General Assembly speech" --n 8

  # 2. download one whole video (<= 1080p). On a YouTube 403 / "page needs to be reloaded"
  #    it runs `yt-dlp -U` once and retries (a stale yt-dlp is the usual cause).
  python3 fetch_footage.py --id dQw4w9WgXcQ --slug albanese-un

  # 3. contact sheet, 1 frame per second (never pick moments off a 5 s sheet)
  python3 fetch_footage.py --slug albanese-un --sheet --from 30 --to 66
  #    -> frames/footage_albanese-un_30-66.jpg (timestamps burned in)

  # 4. cut the moment (video only, frame-accurate, 1920x1080 H.264)
  python3 fetch_footage.py --slug albanese-un --cut 41.5 3.0
  #    -> assets/footage/albanese-un_41.5.mp4   use with video_bg(path, 0.0)
  #    News uploads often show the event as a picture-in-picture panel (sidebar, QR code, logo bug):
  #    grab one full-res frame, measure the panel, and crop it out so the event is full-bleed:
  python3 fetch_footage.py --slug albanese-un --cut 50 4 --crop 85,41,1357,824

Run from the edit's workdir. Footage you didn't shoot is for internal tests unless you have
the rights; Content ID will flag published re-uploads.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

DL_DIR = "assets/footage/src"
CUT_DIR = "assets/footage"
SHEET_DIR = "frames"
FMT = "bv*[height<=1080]+ba/b[height<=1080]"
STALE = ("403", "Forbidden", "page needs to be reloaded", "Requested format is not available", "Sign in to confirm")


def sh(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip()[-800:])
    return r


def search(q: str, n: int) -> None:
    r = sh(["yt-dlp", "--no-warnings", "--flat-playlist", "--print", "%(duration)s|%(id)s|%(title)s", f"ytsearch{n}:{q}"])
    rows = []
    for ln in r.stdout.strip().splitlines():
        d, vid, title = (ln.split("|", 2) + ["", ""])[:3]
        try:
            d = float(d)
        except ValueError:
            d = -1
        rows.append((d, vid, title))
    for d, vid, title in sorted(rows, key=lambda x: (x[0] < 0, x[0])):
        mm = f"{int(d // 60)}:{int(d % 60):02d}" if d >= 0 else "?"
        print(f"{mm:>7}  {vid}  {title}")


def src_path(slug: str) -> str:
    return os.path.join(DL_DIR, f"{slug}.mp4")


def download(vid: str, slug: str, allow_long: bool) -> None:
    os.makedirs(DL_DIR, exist_ok=True)
    url = vid if vid.startswith("http") else f"https://www.youtube.com/watch?v={vid}"
    if not allow_long:
        d = sh(["yt-dlp", "--no-warnings", "--print", "%(duration)s", url], check=False).stdout.strip()
        try:
            if float(d) > 1200:
                sys.exit(f"{vid} is {float(d) / 60:.0f} min; pick a shorter upload or pass --allow-long")
        except ValueError:
            pass
    cmd = ["yt-dlp", "-q", "--no-warnings", "-f", FMT, "--merge-output-format", "mp4", "-o", src_path(slug), url]
    r = sh(cmd, check=False)
    if r.returncode != 0 and any(k in (r.stderr + r.stdout) for k in STALE):
        print("yt-dlp refused (stale client); updating with yt-dlp -U and retrying...", flush=True)
        print(sh(["yt-dlp", "-U"], check=False).stdout.strip().splitlines()[-1:] or "")
        for f in os.listdir(DL_DIR):
            if f.startswith(slug) and f.endswith(".part"):
                os.remove(os.path.join(DL_DIR, f))
        r = sh(cmd, check=False)
    if r.returncode != 0 or not os.path.exists(src_path(slug)):
        sys.exit("download failed: " + (r.stderr or r.stdout).strip()[-600:])
    dur = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src_path(slug)]).stdout.strip()
    print(f"ok {src_path(slug)}  ({float(dur):.1f}s)")


def sheet(slug: str, t0: float, t1: float, every: float) -> None:
    os.makedirs(SHEET_DIR, exist_ok=True)
    n = max(1, int((t1 - t0) / every))
    cols = 8 if n > 16 else 6
    rows = (n + cols - 1) // cols
    out = os.path.join(SHEET_DIR, f"footage_{slug}_{int(t0)}-{int(t1)}.jpg")
    font = "/System/Library/Fonts/Menlo.ttc"
    draw = (f"drawtext=fontfile={font}:text='%{{eif\\:t+{t0}\\:d}}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black"
            if os.path.exists(font) else "null")
    sh(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-t", str(t1 - t0), "-i", src_path(slug),
        "-vf", f"fps={1 / every},scale=320:-2,{draw},tile={cols}x{rows}", "-frames:v", "1", out])
    print(f"ok {out}  ({n} frames, every {every}s)")


def frame(slug: str, t: float) -> None:
    """One full-res still (for measuring a picture-in-picture panel before --crop)."""
    os.makedirs(SHEET_DIR, exist_ok=True)
    out = os.path.join(SHEET_DIR, f"footage_{slug}_{t:g}.png")
    sh(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", src_path(slug), "-frames:v", "1", out])
    print(f"ok {out}")


def cut(slug: str, start: float, dur: float, crop: str | None = None) -> None:
    os.makedirs(CUT_DIR, exist_ok=True)
    out = os.path.join(CUT_DIR, f"{slug}_{start:g}.mp4")
    pre = ""
    if crop:
        x, y, w, h = [int(v) for v in crop.split(",")]
        pre = f"crop={w}:{h}:{x}:{y},"
    sh(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-i", src_path(slug), "-t", str(dur), "-an",
        "-vf", pre + "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", out])
    print(f"ok {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--search")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--id", help="YouTube id or full URL to download")
    ap.add_argument("--slug")
    ap.add_argument("--allow-long", action="store_true")
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=None)
    ap.add_argument("--every", type=float, default=1.0)
    ap.add_argument("--cut", nargs=2, type=float, metavar=("START", "DUR"))
    ap.add_argument("--crop", help="x,y,w,h in source px: keep only this panel (news picture-in-picture)")
    ap.add_argument("--frame", type=float, help="write one full-res still at this time (to measure --crop)")
    a = ap.parse_args()
    if a.search:
        search(a.search, a.n)
        return
    if not a.slug:
        sys.exit("--slug is required for --id / --sheet / --cut")
    if a.id:
        download(a.id, a.slug, a.allow_long)
    if a.sheet:
        t1 = a.t1
        if t1 is None:
            t1 = float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src_path(a.slug)]).stdout)
        sheet(a.slug, a.t0, t1, a.every)
    if a.frame is not None:
        frame(a.slug, a.frame)
    if a.cut:
        cut(a.slug, a.cut[0], a.cut[1], a.crop)


if __name__ == "__main__":
    main()
