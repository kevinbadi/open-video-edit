#!/usr/bin/env python3
"""Prep a LANDSCAPE talking-head clip for the long-form engine.

Writes (in the workdir):
  source/talking_head.mp4   1920x1080 @30fps CFR h264 (letterbox/cover if the source is not 16:9)
  audio/narration.wav/.m4a  clip audio (the master timeline)
  audio/words.json          [[word, start, end], ...] (Whisper, --model small.en default)
  source/meta.json          DUR, HEAD_CROP (680x950 1:1 crop around the face for the SPLIT card), face stats
  renders/head_sheet.jpg    the head card at 4 timestamps: EYEBALL IT (cap crown + chin inside, no black)

Usage (from projects/<slug>-longform/):
  python3 .../prep_longform_head.py --clip "/abs/path/clip.mov" --whisper
  python3 .../prep_longform_head.py --clip ... --crop-x 560 --crop-top 100     # override the card crop
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys
import cv2
import numpy as np

CARD_W, CARD_H = 680, 950


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"cmd failed: {' '.join(cmd)}\n{(r.stderr or r.stdout)[-800:]}")
    return r.stdout


def probe(p):
    d = json.loads(sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", p]))
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    num, den = (v.get("r_frame_rate", "30/1").split("/") + ["1"])[:2]
    return {"w": int(v["width"]), "h": int(v["height"]), "fps": float(num) / float(den or 1),
            "dur": float(d["format"]["duration"])}


def face_stats(path, every_s=3.0):
    cc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(path)
    n, fps = int(cap.get(7)), cap.get(5) or 30
    hits = []
    for i in range(0, n, int(fps * every_s)):
        cap.set(1, i)
        ok, fr = cap.read()
        if not ok:
            continue
        fs = cc.detectMultiScale(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY), 1.1, 5, minSize=(120, 120))
        if len(fs):
            x, y, w, h = max(fs, key=lambda f: f[2] * f[3])
            hits.append((round(i / fps, 1), int(x + w / 2), int(y + h / 2), int(h)))
    cap.release()
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", required=True)
    ap.add_argument("--whisper", action="store_true")
    ap.add_argument("--model", default="small.en")
    ap.add_argument("--crop-x", type=int)
    ap.add_argument("--crop-top", type=int)
    a = ap.parse_args()
    for d in ("source", "audio", "renders", "frames"):
        os.makedirs(d, exist_ok=True)
    src = os.path.abspath(a.clip)
    if not os.path.isfile(src):
        sys.exit(f"clip not found: {src}")
    m = probe(src)
    print(f"source {m['w']}x{m['h']} {m['fps']:.2f}fps {m['dur']:.1f}s")
    dest = "source/talking_head.mp4"
    if (m["w"], m["h"]) == (1920, 1080):
        vf = "fps=30"
    else:
        # cover-scale to 1920x1080 (keeps the face; vertical sources lose their top/bottom)
        vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30"
        print(f"! source is not 1920x1080 — cover-cropping ({vf})")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", vf, "-c:v", "libx264", "-preset", "fast", "-crf", "16",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", dest])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", dest, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "audio/narration.wav"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", dest, "-vn", "-c:a", "aac", "-b:a", "192k", "audio/narration.m4a"])
    meta = probe(dest)

    hits = face_stats(dest)
    if hits:
        cx = int(np.median([h[1] for h in hits]))
        cy = int(np.median([h[2] for h in hits]))
        fh = int(np.median([h[3] for h in hits]))
    else:
        print("! no face found — centering the card crop")
        cx, cy, fh = 960, 540, 400
    crop_x = a.crop_x if a.crop_x is not None else max(0, min(1920 - CARD_W, cx - CARD_W // 2))
    # head-anchored: face center sits ~42% down the card, then clamp inside the frame
    crop_top = a.crop_top if a.crop_top is not None else max(0, min(1080 - CARD_H, int(cy - CARD_H * 0.42)))
    head_crop = [crop_x, crop_top, crop_x + CARD_W, crop_top + CARD_H]
    print(f"face cx={cx} cy={cy} h={fh} ({len(hits)} samples) -> HEAD_CROP={head_crop}")

    nwords = 0
    if a.whisper:
        sh(["whisper", "audio/narration.wav", "--model", a.model, "--language", "en", "--word_timestamps", "True",
            "--output_format", "json", "--output_dir", "audio"])
        raw = json.load(open("audio/narration.json"))
        words = [[w["word"].strip(), float(w["start"]), float(w["end"])] for s in raw["segments"] for w in s.get("words", [])]
        json.dump(words, open("audio/words.json", "w"))
        nwords = len(words)
        print(f"whisper -> {nwords} words")
        print(" ".join(w for w, _, _ in words))

    json.dump({"clip": dest, "width": meta["w"], "height": meta["h"], "DUR": round(meta["dur"], 3),
               "HEAD_CROP": head_crop, "face": {"cx": cx, "cy": cy, "h": fh, "samples": hits}, "words": nwords},
              open("source/meta.json", "w"), indent=2)

    # head-card contact sheet (4 timestamps) for eyeballing crown/chin
    cap = cv2.VideoCapture(dest)
    n = int(cap.get(7))
    tiles = []
    for k in (0.1, 0.35, 0.6, 0.9):
        cap.set(1, int(n * k))
        ok, fr = cap.read()
        if ok:
            x0, y0, x1, y1 = head_crop
            tiles.append(cv2.resize(fr[y0:y1, x0:x1], (340, 475)))
    cap.release()
    if tiles:
        cv2.imwrite("renders/head_sheet.jpg", np.hstack(tiles))
        print("✓ renders/head_sheet.jpg (check the card crop)")
    print(f"✓ source/meta.json DUR={meta['dur']:.2f}")


if __name__ == "__main__":
    main()
