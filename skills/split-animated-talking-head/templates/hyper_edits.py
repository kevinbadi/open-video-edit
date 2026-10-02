#!/usr/bin/env python3
"""Hyper-edit toolkit for the split-animated compositor (Kevin 2026-09-05).

"Hyper-edit" = the Nick-style rapid-fire editing layer on top of the motion
graphics: punch-ins on the talking head at keyword onsets, single-frame accent
inserts (hyperframes) on cuts, whip transitions between sections, camera
shake on impact beats, spring/overshoot easing (Remotion-style presets),
RGB-split + zoom-blur glitches, count-ups and typewriter text.

Everything is deterministic in t (no random state per frame) so preview
frames match the full render. Pure PIL + numpy.

Wire-up (compositor loop):

    from hyper_edits import *
    PUNCH_T = keyword_onsets(words, KEYWORDS)          # [t, t, ...]
    CUT_T   = [a for _, a, _ in SECT[1:]]              # section cuts

    # animation slot: punch-in on keywords + shake on hits (Kevin 2026-09-05)
    layer = punch_zoom(layer, punch_scale(t, PUNCH_T, amt=0.06))
    sx, sy = shake_offset(t, HIT_T, amp=14)
    frame.alpha_composite(layer, (sx, LAYER_Y + sy))
    # talking-head band: LOCKED STILL. Never punch_zoom / shake_offset the band.
    frame.alpha_composite(band, (12, BAND_Y))

    # single-frame accent on section cuts (1-2 frames, never on the hook)
    hyperframe(frame, t, CUT_T, FPS, kind="auto", region=(0, LAYER_Y, W, AH))

    # whip between sections instead of the flat white flash
    if lt < 0.16 and prev_layer is not None:
        layer = whip_wipe(prev_layer, layer, lt / 0.16, direction=whip_dir(name))

    # caption impact
    fs = int(66 * caption_impact(t, onset, key))
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

# ─────────────────────────── easing / springs ───────────────────────────

def clamp01(p: float) -> float:
    return 0.0 if p < 0 else 1.0 if p > 1 else p


def ease_out_cubic(p):
    p = clamp01(p)
    return 1 - (1 - p) ** 3


def ease_in_cubic(p):
    """Slow start so a 10-figure count actually ticks through thousands / millions
    before the billions land. expo.out jumps to ~2B instantly and looks dead."""
    p = clamp01(p)
    return p * p * p


def ease_out_expo(p):
    p = clamp01(p)
    return 1.0 if p >= 1 else 1 - 2 ** (-10 * p)


def ease_in_out_quad(p):
    p = clamp01(p)
    return 2 * p * p if p < 0.5 else 1 - (-2 * p + 2) ** 2 / 2


def ease_back_out(p, s: float = 1.70158):
    """Overshoot pop (GSAP back.out)."""
    p = clamp01(p) - 1
    return 1 + (s + 1) * p ** 3 + s * p * p


def spring(t: float, damping: float = 10.0, stiffness: float = 100.0, mass: float = 1.0) -> float:
    """Remotion-style spring 0→1 over time t (seconds). Presets below.
    smooth={damping:200} snappy={damping:20,stiffness:200} bouncy={damping:8}
    heavy={damping:15,stiffness:80,mass:2}."""
    if t <= 0:
        return 0.0
    w0 = math.sqrt(stiffness / mass)
    zeta = damping / (2 * math.sqrt(stiffness * mass))
    if zeta < 1:
        wd = w0 * math.sqrt(1 - zeta * zeta)
        x = 1 - math.exp(-zeta * w0 * t) * (math.cos(wd * t) + (zeta * w0 / wd) * math.sin(wd * t))
    elif zeta == 1:
        x = 1 - math.exp(-w0 * t) * (1 + w0 * t)
    else:
        s1 = -w0 * (zeta - math.sqrt(zeta * zeta - 1))
        s2 = -w0 * (zeta + math.sqrt(zeta * zeta - 1))
        x = 1 - (s2 * math.exp(s1 * t) - s1 * math.exp(s2 * t)) / (s2 - s1)
    return x


SPRINGS = {
    "smooth": dict(damping=200),
    "snappy": dict(damping=20, stiffness=200),
    "bouncy": dict(damping=8),
    "heavy": dict(damping=15, stiffness=80, mass=2),
}


def spring_preset(t: float, name: str = "snappy") -> float:
    return spring(t, **SPRINGS[name])


# ───────────────────────────── word timing ─────────────────────────────

def keyword_onsets(words, keywords, min_gap: float = 0.35) -> list[float]:
    """Start times of KEYWORD words, de-duplicated so punches don't stack.
    For CAPTION colouring only. Do NOT feed this to punch_scale (Kevin
    2026-09-12: "far too many zoom punch effects"); use punch_beats()."""
    out: list[float] = []
    for w, a, _b in words:
        k = (w or "").strip().rstrip(".,!?").lower()
        if k in keywords and (not out or a - out[-1] >= min_gap):
            out.append(float(a))
    return out


def punch_beats(words, punch_words, min_gap: float = 8.0, max_per_min: float = 6.0) -> list[float]:
    """The FEW moments that earn a slot punch-in: the spoken onsets of
    `punch_words` (one hero word per section, hand-picked), thinned to at
    least `min_gap` seconds apart and capped at `max_per_min`. A 40 s video
    gets ~4 punches, not 30. Pair with shake only on section cuts."""
    onsets = keyword_onsets(words, set(punch_words), min_gap=min_gap)
    if not words:
        return onsets
    dur = max(b for _w, _a, b in words) or 1.0
    cap = max(1, int(dur / 60.0 * max_per_min + 0.999))
    return onsets[:cap]


def word_onset(words, word: str, after: float = 0.0) -> float | None:
    """First start time of `word` at/after `after` — for beat t0 lookups."""
    word = word.lower()
    for w, a, _b in words:
        if a >= after and (w or "").strip().rstrip(".,!?").lower() == word:
            return float(a)
    return None


# ───────────────────────────── punch-ins ─────────────────────────────

def punch_scale(t: float, hits, amt: float = 0.045, attack: float = 0.04, decay: float = 0.32) -> float:
    """Scale factor for the band: snaps to 1+amt at each hit, eases back."""
    s = 1.0
    for h in hits:
        d = t - h
        if d < 0 or d > attack + decay:
            continue
        if d < attack:
            s = max(s, 1 + amt * (d / attack))
        else:
            s = max(s, 1 + amt * (1 - ease_out_cubic((d - attack) / decay)))
    return s


def punch_zoom(img: Image.Image, scale: float, anchor=(0.5, 0.42)) -> Image.Image:
    """Zoom into img by `scale` around anchor (fraction), keeping the size.
    Alpha (rounded band mask) is preserved because we crop-then-resize."""
    if scale <= 1.001:
        return img
    w, h = img.size
    cw, ch = int(w / scale), int(h / scale)
    ax, ay = anchor
    x0 = int(min(max(0, ax * w - cw * ax), w - cw))
    y0 = int(min(max(0, ay * h - ch * ay), h - ch))
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.BICUBIC)


def ladder_scale(t: float, steps, hold: float = 0.0) -> float:
    """Multi-state zoom ladder: steps=[(t0, scale), ...]; hard jumps between
    poses (HyperFrames pose-ladder idea) — use for 'stacking' lists."""
    s = 1.0
    for t0, sc in steps:
        if t >= t0:
            s = sc
    return s


# ───────────────────────────── shake / hits ─────────────────────────────

def _hash01(i: int) -> float:
    x = math.sin(i * 12.9898 + 78.233) * 43758.5453
    return x - math.floor(x)


def shake_offset(t: float, hits, amp: float = 12.0, dur: float = 0.26, fps: int = 30) -> tuple[int, int]:
    """Deterministic decaying jitter after each hit (camera shake)."""
    for h in hits:
        d = t - h
        if 0 <= d < dur:
            k = 1 - d / dur
            fi = int(t * fps)
            dx = (_hash01(fi * 2) * 2 - 1) * amp * k
            dy = (_hash01(fi * 2 + 1) * 2 - 1) * amp * k * 0.6
            return int(dx), int(dy)
    return 0, 0


# ─────────────────────────── hyperframe inserts ───────────────────────────

def hyperframe_kind(t: float, cuts, fps: int = 30, frames: int = 2, kinds=("white", "ink", "invert", "rgb")) -> str | None:
    """Which single-frame accent (if any) to draw at time t. Cycles kinds per
    cut so the video doesn't flash the same way twice in a row."""
    for i, c in enumerate(cuts):
        fi = int(round((t - c) * fps))
        if 0 <= fi < frames:
            return kinds[i % len(kinds)]
    return None


def hyperframe(frame: Image.Image, t: float, cuts, fps: int = 30, kind: str = "auto",
               region=None, frames: int = 2, strength: float = 1.0) -> None:
    """Draw a 1-2 frame accent insert in place. region=(x, y, w, h) limits it
    to the animation slot so the talking head stays stable."""
    k = hyperframe_kind(t, cuts, fps, frames) if kind == "auto" else (kind if hyperframe_kind(t, cuts, fps, frames) else None)
    if not k:
        return
    x, y, w, h = region or (0, 0, frame.width, frame.height)
    sub = frame.crop((x, y, x + w, y + h))
    if k == "white":
        ov = Image.new("RGBA", (w, h), (255, 253, 248, int(230 * strength)))
        sub = Image.alpha_composite(sub, ov)
    elif k == "ink":
        ov = Image.new("RGBA", (w, h), (24, 22, 20, int(215 * strength)))
        sub = Image.alpha_composite(sub, ov)
    elif k == "invert":
        rgb = ImageOps.invert(sub.convert("RGB"))
        sub = Image.blend(sub, rgb.convert("RGBA"), strength)
    elif k == "rgb":
        sub = rgb_split(sub, int(22 * strength))
    frame.paste(sub, (x, y))


# ───────────────────────────── glitch fx ─────────────────────────────

def rgb_split(img: Image.Image, amt: int = 14) -> Image.Image:
    if amt <= 0:
        return img
    r, g, b, a = img.convert("RGBA").split()
    r = ImageChops.offset(r, amt, 0)
    b = ImageChops.offset(b, -amt, 0)
    return Image.merge("RGBA", (r, g, b, a))


def zoom_blur(img: Image.Image, amt: float = 0.06, steps: int = 6) -> Image.Image:
    """Radial-ish zoom blur by stacking scaled copies (impact / whip feel)."""
    if amt <= 0:
        return img
    w, h = img.size
    out = img.convert("RGBA")
    acc = np.array(out).astype(np.float32)
    for i in range(1, steps + 1):
        s = 1 + amt * i / steps
        cw, ch = int(w / s), int(h / s)
        x0, y0 = (w - cw) // 2, (h - ch) // 2
        layer = out.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.BILINEAR)
        acc += np.array(layer).astype(np.float32)
    acc /= steps + 1
    return Image.fromarray(np.clip(acc, 0, 255).astype(np.uint8), "RGBA")


def motion_blur_h(img: Image.Image, px: int) -> Image.Image:
    if px <= 1:
        return img
    return img.filter(ImageFilter.BoxBlur((px, 0)))


# ───────────────────────────── transitions ─────────────────────────────

def whip_dir(name: str) -> str:
    """Alternate whip direction per section name so consecutive cuts differ."""
    return "left" if (sum(map(ord, name)) % 2 == 0) else "right"


def whip_wipe(prev: Image.Image, new: Image.Image, p: float, direction: str = "left", blur: int = 40) -> Image.Image:
    """Whip-pan push: previous layer flies out, new layer flies in, both
    motion-blurred at peak velocity. p in 0..1 over ~0.16s."""
    p = clamp01(p)
    w, h = new.size
    e = ease_in_out_quad(p)
    vel = math.sin(p * math.pi)  # 0 → 1 → 0
    off = int(w * e)
    sign = -1 if direction == "left" else 1
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pb = motion_blur_h(prev, int(blur * vel))
    nb = motion_blur_h(new, int(blur * vel))
    out.alpha_composite(pb, (sign * off, 0))
    out.alpha_composite(nb, (sign * (off - w), 0))
    return out


def slam_in(img: Image.Image, p: float) -> Image.Image:
    """Scale from 1.6→1 with overshoot + alpha ramp: use for hero numbers."""
    p = clamp01(p)
    s = 1.6 - 0.6 * ease_back_out(p, 1.2)
    im = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BICUBIC)
    if p < 1:
        im = im.copy()
        im.putalpha(im.split()[3].point(lambda v: int(v * ease_out_expo(p * 2))))
    return im


def freeze_hit(band: Image.Image, p: float, zoom: float = 1.12, tint=(255, 253, 248)) -> Image.Image:
    """Freeze-frame hit dressing: quick zoom + paper tint + ink border, for a
    'record scratch' beat (beat-freeze-cut / freeze-frame-dressing blocks)."""
    p = clamp01(p)
    im = punch_zoom(band, 1 + (zoom - 1) * ease_out_expo(p))
    ov = Image.new("RGBA", im.size, tint + (int(70 * (1 - p)),))
    im = Image.alpha_composite(im, ov)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, im.width - 7, im.height - 7], 54, outline=(30, 28, 26, int(255 * (1 - p * 0.5))), width=10)
    return im


# ───────────────────────────── text fx ─────────────────────────────

def typewriter(text: str, p: float, cursor: bool = True, t: float = 0.0) -> str:
    n = int(len(text) * clamp01(p))
    s = text[:n]
    if cursor and p < 1 and int(t * 6) % 2 == 0:
        s += "▍"
    return s


def count_up(target: float, p: float, prefix: str = "", suffix: str = "", decimals: int = 0, ease=ease_out_expo) -> str:
    v = target * ease(p)
    return f"{prefix}{v:,.{decimals}f}{suffix}"


def caption_impact(t: float, onset: float, key: bool) -> float:
    """Caption scale multiplier: keywords slam bigger with a squash bounce."""
    d = t - onset
    if d < 0:
        return 1.0
    if key:
        return 1 + 0.22 * max(0.0, 1 - d / 0.14) + 0.06 * math.exp(-d * 9) * math.sin(d * 40)
    return 1 + 0.10 * max(0.0, 1 - d / 0.10)


def highlight_sweep(img: Image.Image, p: float, color=(217, 111, 78, 120), pad: int = 6) -> Image.Image:
    """Highlighter pen sweeping left→right behind text/an image."""
    p = clamp01(p)
    w, h = img.size
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.rounded_rectangle([0, pad, int((w + pad * 2) * p), h + pad], 10, fill=color)
    out.alpha_composite(img, (pad, pad))
    return out


# ───────────────────────────── lane guard ─────────────────────────────
# Kevin 2026-09-05 (voice-agents hook): two conveyors + free icons + the
# invader stacked on one y band = "four carousels overlaid". A carousel is
# ONE carousel. Every moving stream (conveyor / zigzag / orbit / ticker)
# claims a horizontal lane per frame; a second stream that overlaps an
# already-claimed lane is skipped and reported once, and place() callers can
# ask `lanes.free(y0, y1)` before parking a card on top of a stream.

class Lanes:
    def __init__(self):
        self.claims = []          # [(name, y0, y1)] for the current frame
        self.reported = set()

    def reset(self):
        self.claims = []

    def claim(self, name, y0, y1):
        """True if the band [y0, y1] is free (and claims it). False = skip draw."""
        for n, a, b in self.claims:
            if y0 < b and y1 > a:
                key = (n, name)
                if key not in self.reported:
                    self.reported.add(key)
                    print(f"[lanes] '{name}' skipped: overlaps '{n}' ({a}-{b} vs {y0}-{y1}) — one stream per band")
                return False
        self.claims.append((name, y0, y1))
        return True

    def free(self, y0, y1):
        return all(not (y0 < b and y1 > a) for _, a, b in self.claims)


lanes = Lanes()


def guarded_conveyor(layer, y, lt, imgs, conveyor_fn, name="conveyor", pad=6, **kw):
    """Topic-logo staple (Kevin 2026-09-10): one horizontal scroll of the
    marks associated with this video. Draw only if the band is free.
    y is authored cy + PACK_DY (china-robots). Returns True if drawn."""
    if not imgs:
        return False
    h = max(im.height for im in imgs) + pad * 2
    if not lanes.claim(name, y - h // 2, y + h // 2):
        return False
    conveyor_fn(layer, y, lt, imgs, **kw)
    return True


# ───────────────────────────── number beats ─────────────────────────────
# Kevin 2026-09-05: every number the transcript says (money, stars, downloads,
# views, followers, counts, years, percentages, "10 p.m.", "3x") gets an
# on-screen counter animation. number_beats() finds them in words.json;
# media_marks.counter_card() / odometer_card() draws the count-up;
# auto_counters() places any beat the choreography did not handle itself.
# Kevin 2026-09-15: compact "2B" and casino-slot counters are banned.
# Hero numbers (>=10k) are full-figure odometers with live commas.

import re as _re

_UNITS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
          "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
          "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
_SCALES = {"hundred": 100, "thousand": 1_000, "k": 1_000, "grand": 1_000, "million": 1_000_000, "m": 1_000_000,
           "billion": 1_000_000_000, "b": 1_000_000_000, "trillion": 1_000_000_000_000}
_MONEY_AFTER = {"bucks", "dollars", "dollar", "usd", "cash"}
_PCT_AFTER = {"percent", "%"}
_TIMES_AFTER = {"times", "x"}
_TIME_AFTER = {"pm", "am", "p.m.", "a.m.", "p", "a", "o'clock", "oclock"}
_PER_AFTER = {"a", "per"}
_PER_UNITS = {"month": "/mo", "year": "/yr", "day": "/day", "week": "/wk", "hour": "/hr", "minute": "/min"}
LABEL_WORDS = {"stars", "star", "downloads", "download", "views", "view", "followers", "follower", "subs", "subscribers",
               "likes", "comments", "shares", "socials", "accounts", "agents", "messages", "clients", "users", "customers",
               "sales", "orders", "posts", "videos", "clips", "hours", "minutes", "seconds", "days", "weeks", "months",
               "years", "people", "creators", "apps", "tools", "models", "plugins", "skills", "files", "lines", "words",
               "frames", "steps", "platforms", "channels", "leads", "calls", "emails", "dms", "installs", "forks",
               "commits", "repos", "gb", "mb", "tb", "fps", "hz", "km", "miles", "pounds", "kg", "calories", "kcal", "macros",
               "grams", "reps", "sets", "pieces", "slides", "pages", "episodes", "seasons", "levels", "tiers", "plans"}
_SKIP_SPELLED_SOLO = {"one", "two", "a", "an"}

def _clean(w):
    return (w or "").strip().lower().strip("\"'()[]")

def _parse_digit_token(tok):
    """'$100,000' → (100000, '$', ''); '2.5k' → (2500, '', ''); '3x' → (3, '', 'x'); '92%' → (92, '', '%')."""
    m = _re.match(r"^([$€£]?)(\d[\d,]*(?:\.\d+)?)([kKmMbB]|x|X|%)?[.,!?;:]*$", tok)
    if not m:
        return None
    prefix, num, suf = m.group(1), m.group(2).replace(",", ""), (m.group(3) or "")
    try:
        val = float(num)
    except ValueError:
        return None
    if suf.lower() in ("k", "m", "b"):
        val *= _SCALES[suf.lower()]; suf = "\x00k" if suf.lower() == "k" else ""
    elif suf.lower() == "x":
        suf = "x"
    return val, prefix, suf

def number_beats(words, min_solo=3):
    """Scan [[word, start, end], ...] → list of dicts sorted by time:
    {t, end, value, prefix, suffix, label, raw, words:[i..j]}.
    Handles digits, spelled numbers ('twenty five', 'a hundred'), scales
    ('2 billion', '2.5k'), money ('$20', '20 bucks'), '% / percent', '3 times',
    '10 p.m.', 'per month' and a trailing label word (stars, downloads, ...)."""
    toks = [(_clean(w), float(a), float(b)) for w, a, b in words]
    out = []
    i = 0
    n = len(toks)
    while i < n:
        w, a, b = toks[i]
        val = None; prefix = ""; suffix = ""; raw = [w]; j = i
        d = _parse_digit_token(w)
        style = ""
        if d:
            val, prefix, suffix = d
            if suffix == "\x00k":
                suffix = ""; style = "k"
        elif w in ("half", "quarter") and i + 2 < n and toks[i + 1][0] in ("a", "an") and toks[i + 2][0].rstrip(".,!?") in ("hundred", "thousand", "million", "billion", "trillion"):
            # "half a million" → 0.5 × scale (scale loop below multiplies)
            val = 0.5 if w == "half" else 0.25
            raw.append(toks[i + 1][0]); j = i + 1
        elif w.rstrip(".,!?") in _UNITS or w.rstrip(".,!?") in _TENS or (w in ("a", "an") and i + 1 < n and toks[i + 1][0].rstrip(".,!?") in ("hundred", "thousand", "million", "billion", "trillion")):
            ww = w.rstrip(".,!?")
            val = 1.0 if ww in ("a", "an") else float(_UNITS.get(ww, _TENS.get(ww, 0)))
            # 'twenty five'
            if ww in _TENS and i + 1 < n and toks[i + 1][0].rstrip(".,!?") in _UNITS and _UNITS[toks[i + 1][0].rstrip(".,!?")] < 10:
                j = i + 1; val += _UNITS[toks[j][0].rstrip(".,!?")]; raw.append(toks[j][0])
        if val is None:
            i += 1
            continue
        spelled = d is None
        # Whisper splits thousands: "100" ",000" → 100000
        while not spelled and j + 1 < n and _re.match(r"^,\d{3}[.,!?]*$", toks[j + 1][0]):
            val = val * 1000 + int(toks[j + 1][0].strip(",.!?")); raw.append(toks[j + 1][0]); j += 1
        # Whisper splits decimals: "2" ".5" → 2.5
        if not spelled and j + 1 < n and _re.match(r"^\.\d+[.,!?]*$", toks[j + 1][0]):
            frac = toks[j + 1][0].rstrip(".,!?")
            val = float(f"{int(val)}{frac}"); raw.append(toks[j + 1][0]); j += 1
        # scales after: '2 billion', 'a hundred', 'hundred thousand'
        k = j + 1
        while k < n and toks[k][0].rstrip(".,!?") in ("hundred", "thousand", "million", "billion", "trillion", "k", "grand"):
            sc = _SCALES[toks[k][0].rstrip(".,!?")]
            val = val * sc if sc >= 1000 or val < 100 else val + sc
            raw.append(toks[k][0]); j = k; k += 1
        # money / percent / times / time-of-day / per-unit after
        if k < n:
            nxt = toks[k][0].rstrip(".,!?;")
            nxt2 = toks[k + 1][0].rstrip(".,!?;") if k + 1 < n else ""
            if nxt in _MONEY_AFTER:
                prefix = "$"; raw.append(toks[k][0]); j = k; k += 1
            elif nxt in _PCT_AFTER:
                suffix = "%"; raw.append(toks[k][0]); j = k; k += 1
            elif nxt in _TIMES_AFTER:
                suffix = "x"; raw.append(toks[k][0]); j = k; k += 1
            elif nxt in ("p", "a") and nxt2.strip(".") == "m":
                suffix = " PM" if nxt == "p" else " AM"; raw += [toks[k][0], toks[k + 1][0]]; j = k + 1; k += 2
            elif nxt.replace(".", "") in ("pm", "am"):
                suffix = " " + nxt.replace(".", "").upper(); raw.append(toks[k][0]); j = k; k += 1
            if k < n and toks[k][0].rstrip(".,!?") in _PER_AFTER and k + 1 < n and toks[k + 1][0].rstrip(".,!?") in _PER_UNITS:
                suffix += _PER_UNITS[toks[k + 1][0].rstrip(".,!?")]; raw += [toks[k][0], toks[k + 1][0]]; j = k + 1; k += 2
            elif k < n and toks[k][0].rstrip(".,!?") in _PER_UNITS and val >= 1000:
                suffix += _PER_UNITS[toks[k][0].rstrip(".,!?")]; raw.append(toks[k][0]); j = k; k += 1
        label = ""
        if k < n and toks[k][0].rstrip(".,!?") in LABEL_WORDS:
            label = toks[k][0].rstrip(".,!?"); raw.append(label); j = k
        # skip weak spelled solos ('one of the', 'a lot') unless they carry a unit / label / scale
        if spelled and val < min_solo and not (prefix or suffix or label or len(raw) > 1):
            i += 1
            continue
        if spelled and w in _SKIP_SPELLED_SOLO and not (prefix or suffix or label or len(raw) > 1):
            i += 1
            continue
        # bare small digits are usually versions / list markers ("Gemma 4", "LTX 2.5", "1,") — not counters
        if not spelled and val < 10 and not (prefix or suffix or label or any(r.rstrip(".,!?") in _SCALES or r in _MONEY_AFTER for r in raw[1:])):
            i += 1
            continue
        out.append({"t": a, "end": toks[j][2], "value": val, "prefix": prefix, "suffix": suffix, "label": label,
                    "raw": " ".join(raw), "spelled": spelled, "style": style})
        i = j + 1
    return out


def n_figures(v) -> int:
    """How many digit windows a hero odometer needs. 2e9 → 10; floor 4, cap 12."""
    n = len(str(int(abs(float(v)))))
    return max(4, min(12, n))


def fmt_number(v, prefix="", suffix="", compact=True, style=""):
    """Hero counters pass compact=False (2,000,000,000 not 2B). compact is
    chips / captions only — Kevin 2026-09-15 called the compact '2B' card trash."""
    av = abs(v)
    if style == "k" and 1000 <= av < 1_000_000:
        s = f"{v / 1e3:.1f}".rstrip("0").rstrip(".") + "k"
        return f"{prefix}{s}{suffix}"
    if compact and av >= 1_000_000_000:
        s = f"{v / 1e9:.1f}".rstrip("0").rstrip(".") + "B"
    elif compact and av >= 1_000_000:
        s = f"{v / 1e6:.1f}".rstrip("0").rstrip(".") + "M"
    elif compact and av >= 10_000 and not (1900 <= av <= 2099):
        s = f"{v / 1e3:.1f}".rstrip("0").rstrip(".") + "k"
    elif 1900 <= av <= 2099 and float(v).is_integer() and style != "count":
        s = f"{int(v)}"  # a year: no comma (style="count" for "2,000 members")
    elif float(v).is_integer():
        s = f"{int(v):,}"
    else:
        s = f"{v:,.2f}".rstrip("0").rstrip(".")
    return f"{prefix}{s}{suffix}"


def _counter_ease(beat, ease=None):
    if ease is not None:
        return ease
    v = abs(float(beat.get("value") or 0))
    # Large figures need ease-in so 0 → thousands → millions actually ticks.
    # expo.out on 2 billion lands on ~2B in the first frames (Kevin 2026-09-15).
    if v >= 10_000:
        return ease_in_cubic
    return ease_out_expo


def counter_value_raw(beat, p, ease=None):
    """Unrounded eased value for odometer reels (fractional wheels)."""
    ease = _counter_ease(beat, ease)
    v = beat["value"]
    # Years roll from value-40, but only real years: a counted label ("2000
    # person academy", "1950 members") is a count from zero (Kevin 2026-09-29:
    # the 2000 counter showed 1960 before he said it).
    is_year = beat.get("style") == "year" or (
        beat.get("style") != "count" and not str(beat.get("label", "")).strip()
    )
    if is_year and 1900 <= v <= 2099 and beat.get("suffix", "") == "" and beat.get("prefix", "") == "":
        start = v - 40
    else:
        start = 0
    return start + (v - start) * ease(p)


def counter_value(beat, p, ease=None):
    """Value shown at progress p (0..1). Years roll from value-40 so '2026'
    doesn't start at zero. Large figures ease-in so the places tick."""
    cur = counter_value_raw(beat, p, ease=ease)
    v = beat["value"]
    if float(v).is_integer():
        return float(round(cur))
    return round(cur, 1)


# ---------------------------------------------------------------- variety
_ENTRANCES = [
    dict(frm="up"),
    dict(frm="left", tilt=-5),
    dict(frm="down", scale_pop=True),
    dict(frm="right", tilt=5),
    dict(frm="up", scale_pop=True),
    dict(frm="left"),
    dict(frm="down", tilt=-4),
    dict(frm="right", scale_pop=True),
]


def entrance(i: int) -> dict:
    """Rotating place() kwargs so consecutive GIFs / cards never enter the
    same way (Kevin 2026-09-12: "i like animations but a variety"). Use
    `place(layer, img, cx, cy, lt, t0, **entrance(k))` with a per-section
    counter k, or hash on the beat time: entrance(int(t0 * 10))."""
    return dict(_ENTRANCES[i % len(_ENTRANCES)])
