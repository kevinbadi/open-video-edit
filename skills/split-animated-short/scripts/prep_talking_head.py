#!/usr/bin/env python3
"""Prep a user-supplied talking-head clip for the 55/45 split compositor.

Copies the clip at native resolution (never downscale), extracts narration
audio, face-detects a head-anchored band crop (1056x960 @ 30fps on a
1080x1920 canvas), and writes source/meta.json. Optional --whisper emits
audio/words.json in the [[word, start, end], ...] shape the renderer expects.

Usage (from projects/<slug>-animated/):
  python3 /path/to/prep_talking_head.py --clip /path/to/talking-head.mp4
  python3 /path/to/prep_talking_head.py --clip ./source/raw.mov --whisper
  python3 /path/to/prep_talking_head.py --clip ./in.mp4 --crop-top 180 --crop-h 900
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

import cv2
import numpy as np


# 1080x1920 delivery. Never 720x1280. Band is 1056x960 (12px side margins)
# so a 1080p talking-head crop is ~1:1, not scaled down to 704x640
# (Kevin 2026-09-03 — Instagram upscales 720p and it looks like mud).
BAND_W, BAND_H, BAND_FPS = 1056, 960, 30
BAND_ASPECT = BAND_W / BAND_H  # ~1.10


def sh(cmd: list[str] | str, **kw) -> str:
    r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, **kw)
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "")[-800:]
        sys.exit(f"cmd failed ({r.returncode}): {cmd if isinstance(cmd, str) else ' '.join(cmd)}\n{err}")
    return r.stdout


def probe(path: str) -> dict:
    raw = sh([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", path,
    ])
    data = json.loads(raw)
    vs = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if not vs:
        sys.exit(f"no video stream in {path}")
    dur = float(data.get("format", {}).get("duration") or vs.get("duration") or 0)
    fps_s = vs.get("r_frame_rate") or vs.get("avg_frame_rate") or "30/1"
    num, den = (fps_s.split("/") + ["1"])[:2]
    fps = float(num) / float(den) if float(den) else 30.0
    return {
        "width": int(vs.get("width") or 0),
        "height": int(vs.get("height") or 0),
        "duration": dur,
        "fps": fps,
        "pix_fmt": vs.get("pix_fmt"),
        "codec": vs.get("codec_name") or "",
    }


def content_top(clip: str, step_s: float = 0.5, thresh: float = 10.0) -> int:
    """Highest row where the picture actually starts, across the WHOLE clip.

    Kevin's recorder frames the head with a black region above it and that
    boundary moves mid-clip (github-research-agent: 705 -> 772 at 30 s). A
    crop that starts above the boundary ships a black strip at the top of
    the band (Kevin 2026-09-12: "it just doesn't look good"). Returns the
    MAX first-non-black row over samples every `step_s` seconds; frames that
    are fully black are ignored."""
    cap = cv2.VideoCapture(clip)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    top = 0
    step = max(1, int(round(fps * step_s)))
    for i in range(0, n, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, fr = cap.read()
        if not ok:
            continue
        rows = fr.mean(axis=(1, 2))
        lit = rows > thresh
        if not lit.any():
            continue
        first = int(lit.argmax())
        if first > top:
            top = first
    cap.release()
    return top


def verify_band_top(path: str, rows: int = 12, thresh: float = 10.0) -> None:
    """Refuse a band whose top rows are black anywhere in the clip."""
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    bad = []
    for i in range(0, n, max(1, int(fps))):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, fr = cap.read()
        if not ok:
            continue
        if fr[:rows].mean() < thresh and fr.mean() > thresh:
            bad.append(round(i / fps, 1))
    cap.release()
    if bad:
        sys.exit(
            f"band has a black strip at the top at t={bad[:6]}s — the crop starts above the "
            f"picture. Lower --crop-top is wrong here; RAISE it (content_top) or re-run prep."
        )


def detect_crop(clip: str, src_w: int, src_h: int, head_pad: float) -> tuple[int, int, int, int]:
    """Head-anchored 1056:960 crop in source pixels. Haar face detect on ~8 frames;
    fallback is a top-weighted cover crop (sliver of headroom, no letterbox)."""
    crop_h = int(round(src_w / BAND_ASPECT))
    if crop_h > src_h:
        crop_h = src_h
        crop_w = min(src_w, int(round(crop_h * BAND_ASPECT)))
    else:
        crop_w = src_w
    crop_x = max(0, (src_w - crop_w) // 2)
    crop_top = max(0, int(src_h * 0.08))

    cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
    cc = cv2.CascadeClassifier(cascade_path) if os.path.exists(cascade_path) else None
    if cc is None or cc.empty():
        print("! no haar cascade — using top-weighted cover crop")
        if crop_top + crop_h > src_h:
            crop_top = max(0, src_h - crop_h)
        return crop_w, crop_h, crop_x, crop_top

    cap = cv2.VideoCapture(clip)
    nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    samples = 8
    idxs = [int(i * nframes / (samples + 1)) for i in range(1, samples + 1)] if nframes > samples else list(range(nframes))
    tops, faces_cx = [], []
    min_face = max(80, min(src_w, src_h) // 8)
    for i in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, fr = cap.read()
        if not ok:
            continue
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        fs = cc.detectMultiScale(g, 1.1, 5, minSize=(min_face, min_face))
        if len(fs):
            x, y, w2, h2 = max(fs, key=lambda f: int(f[2]) * int(f[3]))
            tops.append(int(y - head_pad * h2))
            faces_cx.append(int(x + w2 / 2))
    cap.release()

    if tops:
        crop_top = max(0, min(tops))
        if faces_cx and crop_w < src_w:
            cx = int(sum(faces_cx) / len(faces_cx))
            crop_x = max(0, min(src_w - crop_w, cx - crop_w // 2))
        print(f"face-detect: {len(tops)} hits, crop_top={crop_top}")
    else:
        print("! no faces detected — top-weighted cover crop")

    # Never start the crop inside the black region above the head (whole-clip scan).
    ctop = content_top(clip)
    if ctop > 0:
        floor_top = ctop + 4
        if floor_top > crop_top:
            print(f"content-top clamp: crop_top {crop_top} -> {floor_top} (black above the head until row {ctop})")
            crop_top = floor_top
        if crop_top + crop_h > src_h:
            # Not enough picture below the black region for a full-size crop:
            # shrink the crop (slight upscale) instead of shipping a black strip.
            crop_h = src_h - crop_top
            crop_w = min(src_w, int(round(crop_h * BAND_ASPECT)))
            cx = int(sum(faces_cx) / len(faces_cx)) if faces_cx else src_w // 2
            crop_x = max(0, min(src_w - crop_w, cx - crop_w // 2))
            print(f"content-top shrink: crop {crop_w}x{crop_h} (upscaled to {BAND_W}x{BAND_H})")

    if crop_top + crop_h > src_h:
        crop_top = max(0, src_h - crop_h)
    return crop_w, crop_h, crop_x, crop_top


def whisper_words(wav: str, out_json: str) -> int:
    sh([
        "whisper", wav, "--model", "base", "--language", "en",
        "--word_timestamps", "True", "--output_format", "json",
        "--output_dir", os.path.dirname(out_json) or ".",
    ])
    stem = os.path.splitext(os.path.basename(wav))[0]
    src = os.path.join(os.path.dirname(out_json) or ".", f"{stem}.json")
    raw = json.load(open(src))
    words = []
    for seg in raw.get("segments") or []:
        for w in seg.get("words") or []:
            t = (w.get("word") or w.get("text") or "").strip()
            if not t:
                continue
            words.append([t, float(w.get("start") or 0), float(w.get("end") or 0)])
    json.dump(words, open(out_json, "w"))
    return len(words)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", required=True, help="path to the user talking-head video")
    ap.add_argument("--workdir", default=".", help="projects/<slug>-animated/")
    ap.add_argument("--whisper", action="store_true", help="run Whisper base → audio/words.json")
    ap.add_argument("--crop-top", type=int, default=None, help="override crop Y in source pixels")
    ap.add_argument("--crop-h", type=int, default=None, help="override crop height in source pixels")
    ap.add_argument("--crop-x", type=int, default=None)
    ap.add_argument("--crop-w", type=int, default=None)
    ap.add_argument("--head-pad", type=float, default=0.35, help="fraction of face height above hairline (higher keeps hats)")
    args = ap.parse_args()

    wd = os.path.abspath(args.workdir)
    clip_in = os.path.abspath(args.clip)
    if not os.path.isfile(clip_in):
        sys.exit(f"clip not found: {clip_in}")
    os.chdir(wd)
    os.makedirs("source", exist_ok=True)
    os.makedirs("audio", exist_ok=True)
    os.makedirs("renders", exist_ok=True)
    os.makedirs("frames", exist_ok=True)

    dest = os.path.abspath("source/talking_head.mp4")
    src_meta = probe(clip_in)
    if os.path.abspath(clip_in) != dest:
        # Keep native resolution. Never scale the user's file.
        codec = (src_meta.get("codec") or "").lower()
        if clip_in.lower().endswith(".mp4") and codec in ("h264", "avc1"):
            sh(["ffmpeg", "-y", "-loglevel", "error", "-i", clip_in, "-c", "copy", dest])
        else:
            sh(["ffmpeg", "-y", "-loglevel", "error", "-i", clip_in,
                "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", dest])
    meta = probe(dest)
    print(f"clip {meta['width']}x{meta['height']} {meta['fps']:.2f}fps {meta['duration']:.2f}s")
    if src_meta["width"] >= 1080 and (
        meta["width"] < src_meta["width"] or meta["height"] < src_meta["height"]
    ):
        sys.exit(
            f"refusing a downscaled source: {src_meta['width']}x{src_meta['height']} "
            f"→ {meta['width']}x{meta['height']}"
        )

    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", dest, "-vn",
        "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "audio/narration.wav"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", dest, "-vn",
        "-c:a", "aac", "-b:a", "192k", "audio/narration.m4a"])

    if args.crop_w and args.crop_h and args.crop_top is not None:
        crop_w, crop_h, crop_x, crop_top = args.crop_w, args.crop_h, args.crop_x or 0, args.crop_top
    else:
        crop_w, crop_h, crop_x, crop_top = detect_crop(dest, meta["width"], meta["height"], args.head_pad)
        if args.crop_top is not None:
            crop_top = args.crop_top
        if args.crop_h is not None:
            crop_h = args.crop_h
        if args.crop_x is not None:
            crop_x = args.crop_x
        if args.crop_w is not None:
            crop_w = args.crop_w

    print(f"band crop: {crop_w}x{crop_h}+{crop_x}+{crop_top} → {BAND_W}x{BAND_H}@{BAND_FPS}")
    if crop_w == BAND_W and crop_h == BAND_H:
        vf = f"crop={crop_w}:{crop_h}:{crop_x}:{crop_top},fps={BAND_FPS}"
    else:
        vf = (
            f"crop={crop_w}:{crop_h}:{crop_x}:{crop_top},"
            f"scale={BAND_W}:{BAND_H}:flags=lanczos,fps={BAND_FPS}"
        )
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", dest, "-vf", vf,
        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-an",
        "renders/talking_band45.mp4"])
    band = probe("renders/talking_band45.mp4")
    verify_band_top("renders/talking_band45.mp4")
    if band["width"] < BAND_W or band["height"] < BAND_H:
        sys.exit(
            f"band is {band['width']}x{band['height']} — refusing anything below "
            f"{BAND_W}x{BAND_H} (never ship 720p talking-head)"
        )

    nwords = 0
    if args.whisper:
        nwords = whisper_words("audio/narration.wav", "audio/words.json")
        print(f"whisper → {nwords} words")

    out = {
        "clip": dest,
        "width": meta["width"],
        "height": meta["height"],
        "src_fps": meta["fps"],
        "DUR": round(meta["duration"], 3),
        "crop": {"w": crop_w, "h": crop_h, "x": crop_x, "y": crop_top},
        "band": {"w": BAND_W, "h": BAND_H, "fps": BAND_FPS, "path": "renders/talking_band45.mp4"},
        "words": nwords,
    }
    json.dump(out, open("source/meta.json", "w"), indent=2)
    print(f"✓ wrote source/meta.json  DUR={out['DUR']}s")


if __name__ == "__main__":
    main()
