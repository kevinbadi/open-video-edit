#!/usr/bin/env python3
"""study.py: measure the editing style of a reference video (step 1 of /reverse-engineer).

    python3 study.py --url "https://www.youtube.com/watch?v=..." --slug fireship-meta [--start 0 --dur 300]
    python3 study.py --file ~/Downloads/ref.mp4 --slug ref-reel
    # -> <out>/  (default ./studies/<slug>/)
    #    source.mp4            the analysed span
    #    report.md / .json     every measured number (cuts, pacing, motion, faces, colour, audio, speech)
    #    cuts/cuts.txt         cut timestamps
    #    frames/shots_NN.jpg   one frame per shot (mid-shot), numbered + timestamped, 30 per sheet
    #    frames/dense_NN.jpg   2 fps sheets of the opening + the longest shots (in-shot element changes)
    #    frames/hook.jpg       the first 3 s at 10 fps (what stops the scroll)
    #    audio/words.json      Whisper word timestamps (if there is speech)

Measures what a script can measure. What a script can't (sticker styles, card types, transitions,
caption look, joke rhythm) the agent reads off the sheets: that is step 2 of SKILL.md.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


def sh(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip()[-800:])
    return r


def probe(path):
    r = sh(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
            "-of", "json", path])
    j = json.loads(r.stdout)
    v = next((s for s in j["streams"] if s.get("codec_type") == "video"), {})
    num, den = (v.get("r_frame_rate", "30/1").split("/") + ["1"])[:2]
    has_audio = any(s.get("codec_type") == "audio" for s in j["streams"])
    return {"width": v.get("width"), "height": v.get("height"), "fps": round(float(num) / float(den or 1), 3),
            "duration": float(j["format"]["duration"]), "has_audio": has_audio}


# ───────────────────────────── 0. source ─────────────────────────────
def fetch(url: str, dst: str) -> None:
    cmd = ["yt-dlp", "-q", "--no-warnings", "-f", "bv*[height<=1080]+ba/b[height<=1080]", "--merge-output-format", "mp4",
           "-o", dst, url]
    r = sh(cmd, check=False)
    if r.returncode != 0 and any(k in r.stderr + r.stdout for k in ("403", "Forbidden", "reloaded", "not available")):
        print("yt-dlp refused (stale client) -> yt-dlp -U and retry", flush=True)
        sh(["yt-dlp", "-U"], check=False)
        r = sh(cmd, check=False)
    if r.returncode != 0:
        sys.exit("download failed: " + (r.stderr or r.stdout)[-500:])


def trim(src: str, dst: str, start: float, dur: float | None) -> None:
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-i", src]
    if dur:
        cmd += ["-t", str(dur)]
    sh(cmd + ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", dst])


# ───────────────────────────── 1. cuts + pacing ─────────────────────────────
def detect_cuts(path: str, threshold: float) -> list[float]:
    r = sh(["ffmpeg", "-hide_banner", "-i", path, "-vf", f"select='gt(scene,{threshold})',showinfo", "-an", "-f", "null", "-"],
           check=False)
    ts = [float(m.group(1)) for m in re.finditer(r"pts_time:([0-9.]+)", r.stderr)]
    out = []
    for t in ts:                      # merge flicker: cuts closer than 0.25 s are one cut
        if not out or t - out[-1] > 0.25:
            out.append(round(t, 3))
    return out


def shot_stats(cuts: list[float], dur: float) -> dict:
    edges = [0.0] + cuts + [dur]
    shots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1) if edges[i + 1] - edges[i] > 0.04]
    lens = [b - a for a, b in shots]
    srt = sorted(lens)
    pct = lambda p: srt[min(len(srt) - 1, int(p * (len(srt) - 1)))] if srt else 0
    longest = sorted(range(len(shots)), key=lambda i: -lens[i])[:5]
    return {
        "shots": len(shots), "cuts_per_min": round(len(cuts) / dur * 60, 1),
        "shot_len_median": round(statistics.median(lens), 2) if lens else 0,
        "shot_len_mean": round(statistics.mean(lens), 2) if lens else 0,
        "shot_len_p10": round(pct(0.1), 2), "shot_len_p90": round(pct(0.9), 2),
        "under_1s_pct": round(100 * sum(1 for x in lens if x < 1.0) / max(1, len(lens)), 1),
        "over_3s_pct": round(100 * sum(1 for x in lens if x > 3.0) / max(1, len(lens)), 1),
        "longest_shots": [{"start": round(shots[i][0], 2), "len": round(lens[i], 2)} for i in longest],
        "_shots": shots,
    }


# ───────────────────────────── 2. sheets for the agent to LOOK at ─────────────────────────────
FONT = "/System/Library/Fonts/Menlo.ttc"


def _label():
    return (f"drawtext=fontfile={FONT}:text='%{{pts\\:hms}}':x=6:y=6:fontsize=18:fontcolor=yellow:box=1:boxcolor=black"
            if os.path.exists(FONT) else "null")


def shot_sheets(path: str, shots, out_dir: str, per_sheet: int = 30, portrait: bool = False) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    tw, th = (180, 320) if portrait else (320, 180)
    cols = 10 if portrait else 6
    sheets = []
    tmp = os.path.join(out_dir, "_shots")
    os.makedirs(tmp, exist_ok=True)
    for i, (a, b) in enumerate(shots):
        t = a + (b - a) / 2
        sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1",
            "-vf", f"scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:-1:-1,"
                   f"drawtext=fontfile={FONT}:text='{i} @{a:.1f}s ({b - a:.1f})':x=4:y=4:fontsize=14:fontcolor=yellow:box=1:boxcolor=black"
            if os.path.exists(FONT) else f"scale={tw}:{th}", os.path.join(tmp, f"s{i:04d}.png")])
    for k in range(0, len(shots), per_sheet):
        n = min(per_sheet, len(shots) - k)
        rows = math.ceil(n / cols)
        out = os.path.join(out_dir, f"shots_{k // per_sheet:02d}.jpg")
        sh(["ffmpeg", "-v", "error", "-y", "-start_number", str(k), "-i", os.path.join(tmp, "s%04d.png"),
            "-frames:v", "1", "-vf", f"tile={cols}x{rows}", out])
        sheets.append(out)
    shutil.rmtree(tmp, ignore_errors=True)
    return sheets


def dense_sheet(path: str, t0: float, dur: float, fps: float, out: str, portrait: bool = False) -> str:
    tw, th = (180, 320) if portrait else (320, 180)
    n = max(1, int(dur * fps))
    cols = 10 if portrait else 8
    rows = math.ceil(n / cols)
    sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", path, "-vf",
        f"fps={fps},scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:-1:-1,setpts=PTS+{t0}/TB,{_label()},"
        f"tile={cols}x{rows}", "-frames:v", "1", out])
    return out


# ───────────────────────────── 3. motion, faces, colour ─────────────────────────────
def visual_stats(path: str, dur: float, sample_fps: float = 4.0) -> dict:
    if cv2 is None:
        return {}
    cap = cv2.VideoCapture(path)
    face = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    prev, diffs, faces, face_boxes, lum, pix = None, [], 0, [], [], []
    n = int(dur * sample_fps)
    for i in range(n):
        cap.set(cv2.CAP_PROP_POS_MSEC, i / sample_fps * 1000)
        ok, fr = cap.read()
        if not ok:
            break
        small = cv2.resize(fr, (160, int(160 * fr.shape[0] / fr.shape[1])))
        g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        if prev is not None:
            diffs.append(float(np.mean(np.abs(g.astype(int) - prev.astype(int)))))
        prev = g
        lum.append(float(g.mean()))
        if i % 2 == 0:
            pix.append(cv2.cvtColor(small, cv2.COLOR_BGR2RGB).reshape(-1, 3)[::7])
            gb = cv2.cvtColor(cv2.resize(fr, (480, int(480 * fr.shape[0] / fr.shape[1]))), cv2.COLOR_BGR2GRAY)
            fs = face.detectMultiScale(gb, 1.15, 5, minSize=(30, 30))
            if len(fs):
                faces += 1
                x, y, w, h = max(fs, key=lambda b: b[2] * b[3])
                face_boxes.append((x / gb.shape[1], y / gb.shape[0], w / gb.shape[1], h / gb.shape[0]))
    cap.release()
    checked = max(1, math.ceil(n / 2))
    # static stretches: consecutive samples with almost no change
    static_runs, run = [], 0
    for d in diffs:
        if d < 1.2:
            run += 1
        else:
            if run:
                static_runs.append(run / sample_fps)
            run = 0
    if run:
        static_runs.append(run / sample_fps)
    out = {
        "motion_mean_diff": round(statistics.mean(diffs), 2) if diffs else 0,
        "static_over_1_5s": sum(1 for r in static_runs if r >= 1.5),
        "longest_static_s": round(max(static_runs), 2) if static_runs else 0,
        "brightness_mean": round(statistics.mean(lum), 1) if lum else 0,
        "face_on_screen_pct": round(100 * faces / checked, 1),
    }
    if face_boxes:
        fb = np.array(face_boxes)
        out["face_center_x"] = round(float(np.median(fb[:, 0] + fb[:, 2] / 2)), 2)
        out["face_center_y"] = round(float(np.median(fb[:, 1] + fb[:, 3] / 2)), 2)
        out["face_height_frac"] = round(float(np.median(fb[:, 3])), 3)
    if pix:
        out["palette"] = palette(np.concatenate(pix).astype(np.float32))
    return out


def visual_events(path: str, dur: float, fps: float = 10.0) -> dict:
    """Things LANDING, not just hard cuts: frame-difference spikes at 10 fps (a sticker popping on,
    a card sliding in, a cutout appearing) on a persistent background. Scene detection only sees
    full-frame changes, so layered styles (Fireship: elements piling onto a black ground) read as
    'slow' on cuts alone. A spike = diff > max(1.5, 3x the clip's median diff), >= 0.3 s apart."""
    if cv2 is None:
        return {}
    cap = cv2.VideoCapture(path)
    prev, diffs = None, []
    for i in range(int(dur * fps)):
        cap.set(cv2.CAP_PROP_POS_MSEC, i / fps * 1000)
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(cv2.resize(fr, (192, int(192 * fr.shape[0] / fr.shape[1]))), cv2.COLOR_BGR2GRAY).astype(int)
        diffs.append(float(np.mean(np.abs(g - prev))) if prev is not None else 0.0)
        prev = g
    cap.release()
    if len(diffs) < 3:
        return {}
    med = statistics.median(d for d in diffs if d > 0) if any(diffs) else 0
    thr = max(1.5, 3 * med)
    events, last = [], -1.0
    for i in range(1, len(diffs) - 1):
        if diffs[i] > thr and diffs[i] >= diffs[i - 1] and diffs[i] >= diffs[i + 1] and i / fps - last >= 0.3:
            events.append(round(i / fps, 2))
            last = i / fps
    gaps = [b - a for a, b in zip([0.0] + events, events + [dur])]
    return {"visual_events": len(events), "events_per_min": round(len(events) / dur * 60, 1),
            "event_gap_median": round(statistics.median(gaps), 2) if gaps else 0, "_events": events}


def palette(px: np.ndarray, k: int = 8, iters: int = 12) -> list[dict]:
    rng = np.random.default_rng(0)
    cent = px[rng.choice(len(px), k, replace=False)]
    for _ in range(iters):
        lab = np.argmin(((px[:, None, :] - cent[None]) ** 2).sum(-1), axis=1)
        cent = np.array([px[lab == j].mean(0) if np.any(lab == j) else cent[j] for j in range(k)])
    counts = np.bincount(lab, minlength=k)
    order = np.argsort(-counts)
    return [{"hex": "#%02x%02x%02x" % tuple(int(c) for c in cent[j]), "share": round(100 * counts[j] / len(px), 1)}
            for j in order]


# ───────────────────────────── 4. audio + speech ─────────────────────────────
def audio_stats(path: str, out_dir: str, whisper_model: str, prompt: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    r = sh(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], check=False)
    I = re.findall(r"^\s+I:\s+(-?[0-9.]+) LUFS", r.stderr, re.M)
    LRA = re.findall(r"^\s+LRA:\s+([0-9.]+) LU", r.stderr, re.M)
    r = sh(["ffmpeg", "-i", path, "-af", "silencedetect=noise=-38dB:d=0.35", "-f", "null", "-"], check=False)
    pauses = [float(x) for x in re.findall(r"silence_duration: ([0-9.]+)", r.stderr)]
    out = {"loudness_lufs": float(I[-1]) if I else None, "loudness_range_lu": float(LRA[-1]) if LRA else None,
           "pauses_over_0_35s": len(pauses), "longest_pause_s": round(max(pauses), 2) if pauses else 0}
    wav = os.path.join(out_dir, "speech16k.wav")
    sh(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "1", "-ar", "16000", wav])
    if shutil.which("whisper"):
        cmd = ["whisper", wav, "--model", whisper_model, "--language", "en", "--word_timestamps", "True",
               "--output_format", "json", "--output_dir", out_dir]
        if prompt:
            cmd += ["--initial_prompt", prompt]
        sh(cmd, check=False)
        jp = os.path.join(out_dir, "speech16k.json")
        if os.path.exists(jp):
            raw = json.load(open(jp))
            words = [[w["word"].strip(), round(w["start"], 2), round(w["end"], 2)]
                     for s in raw.get("segments", []) for w in s.get("words", [])]
            json.dump(words, open(os.path.join(out_dir, "words.json"), "w"))
            open(os.path.join(out_dir, "transcript.txt"), "w").write(" ".join(w for w, _a, _b in words))
            if words:
                span = max(1e-6, words[-1][2] - words[0][1])
                out["words"] = len(words)
                out["wpm"] = round(len(words) / span * 60, 1)
                out["speech_coverage_pct"] = round(100 * sum(b - a for _w, a, b in words) / span, 1)
    return out


# ───────────────────────────── report ─────────────────────────────
def verdicts(R: dict) -> list[str]:
    v, s, vis, au = [], R["shots"], R["visual"], R["audio"]
    v.append(f"Pacing: a cut every {s['shot_len_median']} s median ({s['cuts_per_min']} cuts/min); "
             + ("hyper-fast" if s["shot_len_median"] < 1.2 else "fast" if s["shot_len_median"] < 2.5 else "moderate" if s["shot_len_median"] < 5 else "slow") + ".")
    if vis.get("event_gap_median"):
        layered = vis["event_gap_median"] < 0.6 * s["shot_len_median"]
        v.append(f"Something new lands every {vis['event_gap_median']} s median ({vis['events_per_min']} visual events/min)"
                 + (": LAYERED style, elements pile onto a held background between cuts." if layered else "."))
    fp = vis.get("face_on_screen_pct", 0)
    if fp < 15:
        v.append(f"Faceless: a face is on screen only {fp}% of the time (B-roll driven).")
    elif fp > 60:
        pos = vis.get("face_center_y", 0.5)
        v.append(f"Talking head: a face is on screen {fp}% of the time, centred at y={pos} of frame "
                 + ("(head in the lower half: split / band format)" if pos > 0.55 else "(head upper/middle)") + ".")
    else:
        v.append(f"Mixed: a face is on screen {fp}% of the time (talking head cut with B-roll).")
    if vis.get("longest_static_s", 0) > 2:
        v.append(f"Holds: the longest near-static stretch is {vis['longest_static_s']} s.")
    else:
        v.append("Always moving: no near-static stretch longer than 2 s.")
    if au.get("wpm"):
        v.append(f"Speech: {au['wpm']} wpm, {au['pauses_over_0_35s']} pauses > 0.35 s "
                 + ("(jump-cut every breath)" if au["pauses_over_0_35s"] < R["source"]["duration"] / 15 else "(natural pauses kept)") + ".")
    if au.get("loudness_range_lu") is not None:
        v.append(f"Mix: {au['loudness_lufs']} LUFS, LRA {au['loudness_range_lu']} LU "
                 + ("(heavily compressed, bed under VO)" if au["loudness_range_lu"] < 6 else "(dynamic)") + ".")
    return v


def write_report(R: dict, path_md: str) -> None:
    s, vis, au, src = R["shots"], R["visual"], R["audio"], R["source"]
    L = [f"# Style study: {R['slug']}", "", f"Source: {R.get('url') or R.get('file')}  ",
         f"Analysed: {src['start']} s + {src['duration']:.1f} s at {src['width']}x{src['height']}, {src['fps']} fps", "",
         "## Verdicts (measured)", ""] + [f"- {x}" for x in R["verdicts"]] + ["",
         "## Numbers", "", "| metric | value |", "|---|---|"]
    for k, val in [("shots", s["shots"]), ("cuts / min", s["cuts_per_min"]), ("shot length median", s["shot_len_median"]),
                   ("shot length mean", s["shot_len_mean"]), ("shot length p10 / p90", f"{s['shot_len_p10']} / {s['shot_len_p90']}"),
                   ("shots < 1 s", f"{s['under_1s_pct']}%"), ("shots > 3 s", f"{s['over_3s_pct']}%"),
                   ("visual events / min (things landing)", vis.get("events_per_min")),
                   ("something new lands every (median)", f"{vis.get('event_gap_median')} s"),
                   ("motion (mean frame diff)", vis.get("motion_mean_diff")), ("near-static stretches >= 1.5 s", vis.get("static_over_1_5s")),
                   ("longest near-static", vis.get("longest_static_s")), ("face on screen", f"{vis.get('face_on_screen_pct')}%"),
                   ("face centre (x, y) / height", f"{vis.get('face_center_x')}, {vis.get('face_center_y')} / {vis.get('face_height_frac')}"),
                   ("brightness mean", vis.get("brightness_mean")), ("loudness", f"{au.get('loudness_lufs')} LUFS, LRA {au.get('loudness_range_lu')} LU"),
                   ("pauses > 0.35 s", au.get("pauses_over_0_35s")), ("words / wpm", f"{au.get('words')} / {au.get('wpm')}")]:
        L.append(f"| {k} | {val} |")
    L += ["", "Longest shots (usually the builds worth studying): " +
          ", ".join(f"{x['start']}s ({x['len']}s)" for x in s["longest_shots"]), "",
          "Palette: " + " ".join(f"`{p['hex']}` {p['share']}%" for p in vis.get("palette", [])), "",
          "## Sheets to LOOK at (step 2)", ""] + [f"- `{p}`" for p in R["sheets"]] + ["",
          "## Fill in from the sheets (step 2)", "",
          "- Devices (what kind of element appears, how it enters, how long it holds, where it sits):",
          "- On-screen text styles (fonts, colours, stroke, size, position, caption track yes/no):",
          "- Transitions (hard cut / whip / glitch / zoom / flash), and how often:",
          "- Layout (full-bleed, split, band, picture-in-picture, safe zones):",
          "- Hook (first 3 s, see hook.jpg) and ending:",
          "- Sound (music bed, SFX on hits, risers):", ""]
    open(path_md, "w").write("\n".join(L))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--file")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--out", help="study folder (default ./studies/<slug>)")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--dur", type=float, default=None, help="analyse only this many seconds (default: all, max 600)")
    ap.add_argument("--threshold", type=float, default=0.22, help="scene-cut sensitivity (lower = more cuts)")
    ap.add_argument("--whisper-model", default="small.en")
    ap.add_argument("--prompt", default="", help="names to bias Whisper spelling")
    a = ap.parse_args()
    if not (a.url or a.file):
        sys.exit("--url or --file is required")
    out = a.out or os.path.join("studies", a.slug)
    for d in ("frames", "cuts", "audio"):
        os.makedirs(os.path.join(out, d), exist_ok=True)
    raw = os.path.join(out, "raw.mp4")
    if a.url:
        if not os.path.exists(raw):
            print("downloading...", flush=True)
            fetch(a.url, raw)
    else:
        raw = os.path.expanduser(a.file)
    full = probe(raw)
    dur = min(a.dur or full["duration"] - a.start, 600.0, full["duration"] - a.start)
    src = os.path.join(out, "source.mp4")
    trim(raw, src, a.start, dur)
    info = probe(src)
    info["start"] = a.start
    portrait = (info["height"] or 0) > (info["width"] or 1)
    print(f"source {info['width']}x{info['height']} {info['fps']} fps, {info['duration']:.1f}s", flush=True)

    print("cuts...", flush=True)
    cuts = detect_cuts(src, a.threshold)
    open(os.path.join(out, "cuts", "cuts.txt"), "w").write("\n".join(f"{c:.3f}" for c in cuts))
    S = shot_stats(cuts, info["duration"])
    shots = S.pop("_shots")

    print(f"{len(shots)} shots -> sheets...", flush=True)
    sheets = shot_sheets(src, shots, os.path.join(out, "frames"), portrait=portrait)
    sheets.append(dense_sheet(src, 0.0, min(3.0, info["duration"]), 10, os.path.join(out, "frames", "hook.jpg"), portrait))
    sheets.append(dense_sheet(src, 0.0, min(30.0, info["duration"]), 2, os.path.join(out, "frames", "dense_00_open.jpg"), portrait))
    for i, ls in enumerate(S["longest_shots"][:3]):
        sheets.append(dense_sheet(src, ls["start"], min(ls["len"], 20.0), 2,
                                  os.path.join(out, "frames", f"dense_{i + 1:02d}_long.jpg"), portrait))

    print("motion / faces / palette...", flush=True)
    V = visual_stats(src, info["duration"])
    EV = visual_events(src, info["duration"])
    open(os.path.join(out, "cuts", "events.txt"), "w").write("\n".join(f"{e:.2f}" for e in EV.pop("_events", [])))
    V.update(EV)
    A = {}
    if info["has_audio"]:
        print("audio / speech...", flush=True)
        A = audio_stats(src, os.path.join(out, "audio"), a.whisper_model, a.prompt)

    R = {"slug": a.slug, "url": a.url, "file": a.file, "source": info, "shots": S, "visual": V, "audio": A,
         "sheets": [os.path.relpath(p, out) for p in sheets]}
    R["verdicts"] = verdicts(R)
    json.dump(R, open(os.path.join(out, "report.json"), "w"), indent=2)
    write_report(R, os.path.join(out, "report.md"))
    print("\n".join(R["verdicts"]))
    print(f"ok {out}/report.md  ({len(sheets)} sheets)")


if __name__ == "__main__":
    main()
