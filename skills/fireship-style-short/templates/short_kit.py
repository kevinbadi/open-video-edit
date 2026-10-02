#!/usr/bin/env python3
"""short_kit.py: the vertical (9:16, 1080x1920) layer on top of fireship_engine.

    from short_kit import *          # sets FIRESHIP_CANVAS=9:16, then imports the engine

Same devices as the long-form Fireship skill, re-laid-out for a phone:
  - footage_band(): 16:9 news/event footage as a full-width band with a blurred, darkened fill of
    the same footage behind it (keeps lower thirds + faces), or footage_fill() for a centre crop.
  - gif_band(): a meme the same way (burned-in captions stay readable).
  - fit_w(): shrink any long-form card (tweet, headline, doc, diagram) to the safe width.
  - Captions: word-chunk captions in the lower safe zone, keywords in yellow (on by default for
    shorts: most views start muted). CAPTIONS=0 env turns them off for a pure Fireship look.
  - SAFE zones: top 200 px (status bar / search), bottom 460 px (title, buttons) and the right
    rail x > 960 in the bottom half (like / comment / share). Nothing important goes there.
"""
import glob
import os
import sys

os.environ["FIRESHIP_CANVAS"] = "9:16"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fireship_engine import *  # noqa: E402,F401,F403
import fireship_engine as _fe  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

assert (W, H) == (1080, 1920), "short_kit must be imported before anything else imports fireship_engine"

SAFE_TOP = 200
SAFE_BOTTOM = 1460          # captions sit on this line; below it is platform UI
SAFE_W = 960                # max card width
CX = W / 2
BAND_Y = 760                # centre of the footage band (upper-middle: eyes land here)
STICKER_ABOVE, STICKER_BELOW = 330, 1150   # sticker slots that never touch the band's faces or the captions


def _blur_fill(fr, darken=0.45):
    bg = fit_cover(fr.convert("RGB"), W, H, zoom=1.15).filter(ImageFilter.GaussianBlur(28))
    return Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), darken)


def band_frame(fr, cy=BAND_Y, zoom=1.0, fx=0.5, fy=0.5, aspect=16 / 9):
    """Compose one vertical frame: blurred fill + the source as a full-width band centred at cy."""
    canvas = _blur_fill(fr)
    bh = int(W / aspect)
    band = fit_cover(fr.convert("RGB"), W, bh, zoom=zoom, fx=fx, fy=fy)
    canvas.paste(band, (0, int(cy - bh / 2)))
    d = ImageDraw.Draw(canvas)
    d.line([(0, int(cy - bh / 2)), (W, int(cy - bh / 2))], fill=(0, 0, 0), width=4)
    d.line([(0, int(cy + bh / 2)), (W, int(cy + bh / 2))], fill=(0, 0, 0), width=4)
    return canvas


def footage_band(path, src_start=0.0, cy=BAND_Y, zoom=1.0, fx=0.5, fy=0.5, push=0.03):
    """16:9 footage as a band over its own blurred fill, with a slow push-in."""
    return lambda lt, t: band_frame(footage(path).frame(src_start + lt), cy=cy, zoom=zoom + push * lt, fx=fx, fy=fy)


def footage_fill(path, src_start=0.0, fx=0.5, zoom=1.0, push=0.03):
    """Full-bleed centre crop (use when the subject is centred; fx picks the column)."""
    return lambda lt, t: fit_cover(footage(path).frame(src_start + lt).convert("RGB"), zoom=zoom + push * lt, fx=fx)


def image_band(path, cy=BAND_Y, push=0.03):
    src = Image.open(path).convert("RGB")
    aspect = src.width / src.height
    return lambda lt, t: band_frame(src, cy=cy, zoom=1.0 + push * lt, aspect=max(1.0, aspect))


def gif_band(slug, cy=BAND_Y, root="assets/gifs"):
    fs = sorted(glob.glob(f"{root}/{slug}/f*.png"))
    first = Image.open(fs[0])
    aspect = max(0.75, first.width / first.height)
    return lambda lt, t: band_frame(Image.open(fs[int(lt * 30) % len(fs)]), cy=cy, aspect=aspect)


def fit_w(img, maxw=SAFE_W):
    """Shrink a long-form card (tweet / headline / doc / bench) to the vertical safe width."""
    if img is None or img.width <= maxw:
        return img
    s = maxw / img.width
    return img.resize((maxw, max(1, int(img.height * s))), Image.LANCZOS)


def card(fn, maxw=SAFE_W):
    """Layer img factory: card(lambda lt: tweet_card(...)) -> callable that returns a safe-width card."""
    return lambda lt: fit_w(fn(lt) if callable(fn) else fn, maxw)


# ───────────────────────────── captions (on by default) ─────────────────────────────
CAP_ON = os.environ.get("CAPTIONS", "1") != "0"
CAP_SIZE = 92
CAP_YELLOW = (255, 214, 0)


def caption_chunks(words, max_words=3, max_gap=0.35):
    """Group Whisper words into 1-3 word chunks that break on pauses and punctuation."""
    chunks, cur = [], []
    for w, a, b in words:
        if cur and (len(cur) >= max_words or a - cur[-1][2] > max_gap or cur[-1][0][-1:] in ".,?!"):
            chunks.append(cur)
            cur = []
        cur.append((w, a, b))
    if cur:
        chunks.append(cur)
    return [(" ".join(x[0] for x in c), c[0][1], c[-1][2], c) for c in chunks]


def make_captions(words, keywords=(), y=SAFE_BOTTOM - 100):
    """post= hook for render(): draws the live chunk; the word being spoken pops, keywords in yellow."""
    chunks = caption_chunks(words)
    keys = {k.lower() for k in keywords}

    def post(canvas, t):
        if not CAP_ON:
            return
        live = next((c for c in chunks if c[1] - 0.05 <= t <= c[2] + 0.12), None)
        if live is None:
            return
        d = ImageDraw.Draw(canvas)
        toks = live[3]
        gap = 26
        size = CAP_SIZE
        while True:
            f = font("display", size)
            fpop = font("display", int(size * 1.1))
            # slots are reserved at the POPPED size so the live word never grows into its neighbour
            widths = [d.textlength(w.upper(), font=fpop) for w, _a, _b in toks]
            total = sum(widths) + gap * (len(toks) - 1)
            if total <= W - 110 or size <= 48:
                break
            size -= 4
        x = CX - total / 2
        for (w, a, b), wd in zip(toks, widths):
            clean = w.strip(".,!?\"'").lower()
            col = CAP_YELLOW if clean in keys else (255, 255, 255)
            live_word = a <= t <= b
            fw = fpop if live_word else f
            # each word owns its slot; the spoken word pops in place (centred), never into its neighbour
            d.text((x + wd / 2, y), w.upper(), font=fw, fill=col, anchor="ms", stroke_width=9, stroke_fill=(0, 0, 0))
            x += wd + gap
    return post


def short_mux(out_dir, voice, out, music=None):
    """Same loudness/48 kHz mux as long-form."""
    mux(out_dir, voice, music, out)
