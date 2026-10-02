#!/usr/bin/env python3
"""Apple-style rolling counter (Kevin 2026-09-29: "find and implement a modern
apple inspired odometer that'll replace the one we currently have, it's bad").

Modeled on iOS `contentTransition(.numericText())` + keynote stat slides:
  * big SF Pro Display Bold digits, tabular cells, no boxes / wells / cages
  * each place rolls vertically: outgoing digit slides up + fades, incoming
    slides up from below + fades in, with vertical motion blur scaled to speed
  * places are geared like a real odometer: ones spin, higher places only tick
    over when the place below wraps 9 -> 0
  * no leading zeros: a new leading digit (and its comma) slides in as the
    number grows, and the whole figure re-centers smoothly (width eases)
  * frosted dark glass card, hairline highlight, accent dot + tracked label

Drop-in for counter_card / odometer_card (media_marks delegates here):
    apple_counter(beat, p, w=1000, h=400, label="GITHUB STARS", accent=ORANGE)
`beat` = {"value", "prefix", "suffix", "style"}; p = 0..1 progress (already on
the spoken word). Deterministic in p, no Date / randomness.
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

_SF = "/System/Library/Fonts/SFNS.ttf"
_HERE = os.path.dirname(os.path.abspath(__file__))
_FALLBACK = os.path.join(_HERE, "fonts", "Oswald-Bold.ttf")
_FONTS: dict = {}


def _font(size: int, weight: int = 700, opsz: int = 96) -> ImageFont.FreeTypeFont:
    key = (size, weight, opsz)
    if key in _FONTS:
        return _FONTS[key]
    try:
        f = ImageFont.truetype(_SF, size)
        # axes: Width, Optical Size, GRAD, Weight
        f.set_variation_by_axes([100, opsz, 400, weight])
    except Exception:
        f = ImageFont.truetype(_FALLBACK, size)
    _FONTS[key] = f
    return f


def _ease_out_expo(p: float) -> float:
    return 1.0 if p >= 1 else 1 - 2 ** (-10 * p)


def _ease_in_out_cubic(p: float) -> float:
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


def _raw(target: float, p: float) -> float:
    p = max(0.0, min(1.0, p))
    # Big figures: ease-in-out so thousands -> millions visibly tick (not a jump);
    # small figures: expo-out snap, settles like iOS.
    e = _ease_in_out_cubic(p) if abs(target) >= 10_000 else _ease_out_expo(p)
    return abs(target) * e


def _card(w: int, h: int, accent) -> Image.Image:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    # soft drop shadow
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([14, 22, w - 14, h - 4], 44, fill=(0, 0, 0, 110))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    body = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    for y in range(h):  # vertical glass gradient
        t = y / max(1, h - 1)
        c = (int(34 - 16 * t), int(35 - 16 * t), int(42 - 18 * t), 238)
        bd.line([(0, y), (w, y)], fill=c)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([6, 6, w - 7, h - 7], 40, fill=255)
    body.putalpha(mask)
    img.alpha_composite(body)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([6, 6, w - 7, h - 7], 40, outline=(255, 255, 255, 30), width=2)
    d.line([(52, 8), (w - 52, 8)], fill=(255, 255, 255, 60), width=1)  # hairline top highlight
    # faint accent bloom behind the digits
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([w * 0.2, h * 0.15, w * 0.8, h * 0.75], fill=tuple(accent) + (34,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
    return img


def _digit_tile(ch: str, font, cell_w: int, cell_h: int, fill=(255, 255, 255)) -> Image.Image:
    key = ("dt", ch, font.size, cell_w, cell_h, fill)
    if key in _FONTS:
        return _FONTS[key]
    im = Image.new("RGBA", (cell_w, cell_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((cell_w / 2, cell_h * 0.52), ch, font=font, fill=fill + (255,), anchor="mm")
    # subtle top-to-bottom tone (Apple keynote numerals)
    shade = Image.new("L", (cell_w, cell_h), 0)
    sd = ImageDraw.Draw(shade)
    for y in range(cell_h):
        sd.line([(0, y), (cell_w, y)], fill=int(40 * y / cell_h))
    dark = Image.new("RGBA", (cell_w, cell_h), (0, 0, 0, 255))
    dark.putalpha(Image.composite(shade, Image.new("L", im.size, 0), im.split()[3]))
    im.alpha_composite(dark)
    _FONTS[key] = im
    return im


def _column(cur: int, nxt: int, frac: float, font, cell_w: int, cell_h: int, blur: float,
            hide_cur: bool = False) -> Image.Image:
    """One digit place mid-roll: `cur` leaving upward, `nxt` arriving from below.
    hide_cur: the outgoing digit is a leading zero, so only the arrival shows."""
    col = Image.new("RGBA", (cell_w, cell_h), (0, 0, 0, 0))
    ease = frac * frac * (3 - 2 * frac)  # smoothstep so each tick settles
    travel = int(cell_h * 0.34)  # short hop: digits blur through each other, iOS numericText
    if ease < 1 and not hide_cur:
        a = _digit_tile(str(cur), font, cell_w, cell_h)
        a = a.copy()
        a.putalpha(a.split()[3].point(lambda v, k=(1 - ease) ** 1.6: int(v * k)))
        col.alpha_composite(a, (0, -int(travel * ease)))
    if ease > 0:
        b = _digit_tile(str(nxt), font, cell_w, cell_h).copy()
        b.putalpha(b.split()[3].point(lambda v, k=ease ** 1.6: int(v * k)))
        col.alpha_composite(b, (0, int(travel * (1 - ease))))
    # soft vertical edge fade: rolling digits dissolve at the line, never poke out
    key = ("fade", cell_w, cell_h)
    fade = _FONTS.get(key)
    if fade is None:
        fade = Image.new("L", (cell_w, cell_h), 0)
        fd = ImageDraw.Draw(fade)
        edge = cell_h * 0.26
        for y in range(cell_h):
            t = min(1.0, y / edge, (cell_h - 1 - y) / edge)
            fd.line([(0, y), (cell_w, y)], fill=int(255 * max(0.0, t) ** 1.4))
        _FONTS[key] = fade
    col.putalpha(Image.composite(col.split()[3], Image.new("L", col.size, 0), fade))
    if blur > 0.6:
        col = _vblur(col, int(min(cell_h * 0.18, blur * 1.4)))
    return col


def _vblur(im: Image.Image, length: int) -> Image.Image:
    """True vertical motion blur: box filter along y on premultiplied RGBA."""
    if length < 2:
        return im
    import numpy as np
    a = np.asarray(im, dtype=np.float32)
    alpha = a[..., 3:4] / 255.0
    pre = np.concatenate([a[..., :3] * alpha, alpha], axis=2)
    pad = length // 2
    padded = np.pad(pre, ((pad, length - pad), (0, 0), (0, 0)))
    cs = np.cumsum(padded, axis=0)
    out = (cs[length:] - cs[:-length])[: a.shape[0]] / length
    al = np.clip(out[..., 3:4], 1e-6, 1.0)
    rgb = np.clip(out[..., :3] / al, 0, 255)
    res = np.concatenate([rgb, np.clip(out[..., 3:4] * 255, 0, 255)], axis=2).astype(np.uint8)
    return Image.fromarray(res, "RGBA")


def apple_counter(beat, p, w=1000, h=400, label=None, accent=(255, 122, 24), fill=None, fg=None,
                  **_ignored) -> Image.Image:
    target = float(beat.get("value") or 0)
    prefix = beat.get("prefix", "") or ""
    suffix = beat.get("suffix", "") or ""
    lab = label if label is not None else (beat.get("label") or "")
    decimals = 0 if float(target).is_integer() else 1
    commas = beat.get("style") != "year" and abs(target) >= 1000

    r = _raw(target, p)
    r_prev = _raw(target, p - 0.034)  # ~1 frame back at a ~1 s count, for motion blur
    scale = 10 ** decimals
    R, Rp = r * scale, r_prev * scale
    n = max(1, len(str(int(abs(target) * scale))))

    lab_h = int(h * 0.2) if lab else 0
    card = _card(w, h, accent)
    num_h = h - lab_h - 20
    # digit size from width AND height so figures always fit their cells
    sep_w_ratio = 0.32
    extra = (len(prefix) + len(suffix)) * 0.62
    groups = (n - 1) // 3 if commas else 0
    size_by_w = int((w - 110) / (n * 0.62 + groups * sep_w_ratio + extra + (0.28 if decimals else 0)) / 1.0)
    fsz = max(28, min(int(num_h * 0.78), size_by_w))
    font = _font(fsz, 700, 96)
    final_w = (n * 0.62 + groups * sep_w_ratio) * fsz + sum(font.getlength(c) for c in prefix + suffix)
    if final_w > w - 90:
        fsz = int(fsz * (w - 90) / final_w)
        font = _font(fsz, 700, 96)
    cell_w = int(fsz * 0.62)
    cell_h = int(fsz * 1.18)
    sep_w = int(fsz * sep_w_ratio)

    # Places, ones first. Geared: place i rolls only while the place below wraps.
    # Real odometer carry: place i rolls only while EVERY place below it is on 9
    # and rolling, and it rolls exactly as far as the ones wheel has (so a place
    # never shows its next digit early: no "2,992,000,000" on the way to 2B).
    places = []
    iv = int(math.floor(R))
    carry = R - math.floor(R)  # ones-wheel fraction
    for i in range(n):
        cur = (iv // (10 ** i)) % 10
        frac = carry if i == 0 else (carry if all((iv // (10 ** k)) % 10 == 9 for k in range(i)) else 0.0)
        spd = abs(R - Rp) / (10 ** i)
        if i == 0 or iv >= 10 ** i:
            present, hide = 1.0, False
        elif frac > 0:
            present, hide = frac, True  # new leading digit arriving: slide + fade in, no ghost zero
        else:
            present, hide = 0.0, True
        if spd >= 0.9 and not hide:
            # Spinning faster than ~a digit per frame: a clean speed-blurred digit,
            # never a half-and-half crossfade (that flickers as doubled digits).
            places.append((cur, (cur + 1) % 10, 0.0, min(18.0, 6 + spd * 2.0), present, hide))
            continue
        places.append((cur, (cur + 1) % 10, frac, min(12.0, spd * 6.0), present, hide))

    # Layout right-to-left; width eases with the presence of leading places.
    items = []  # (kind, payload, width, alpha)
    gw = lambda ch: int(font.getlength(ch)) + int(fsz * 0.04)  # noqa: E731  measured glyph width
    for s in reversed(suffix):
        items.append(("ch", s, gw(s), 1.0))
    for i, (cur, nxt, frac, blur, present, hide) in enumerate(places):
        if decimals and i == decimals:
            items.append(("ch", ".", int(fsz * 0.3), 1.0))
        if commas and i > 0 and (i - decimals) % 3 == 0 and i - decimals > 0:
            items.append(("ch", ",", sep_w, present))
        items.append(("dg", (cur, nxt, frac, blur, hide), cell_w, present))
    for s in reversed(prefix):
        items.append(("ch", s, gw(s), 1.0))
    total = sum(wd * al for _, _, wd, al in items)
    x = (w + total) / 2
    y0 = int(20 + (num_h - cell_h) / 2)
    for kind, payload, wd, al in items:
        if al <= 0.01:
            continue
        x -= wd * al
        if kind == "dg":
            cur, nxt, frac, blur, hide = payload
            col = _column(cur, nxt, frac, font, cell_w, cell_h, blur, hide_cur=hide)
            if al < 1:
                col.putalpha(col.split()[3].point(lambda v, k=al: int(v * k)))
                dy = int(cell_h * 0.35 * (1 - al))
            else:
                dy = 0
            card.alpha_composite(col, (int(x), y0 + dy))
        else:
            ch = payload
            t = Image.new("RGBA", (max(1, wd), cell_h), (0, 0, 0, 0))
            ImageDraw.Draw(t).text((wd / 2, cell_h * 0.52), ch, font=font,
                                   fill=(235, 236, 240, int(255 * al)), anchor="mm")
            card.alpha_composite(t, (int(x), y0))
    if lab:
        d = ImageDraw.Draw(card)
        lf = _font(max(18, int(lab_h * 0.42)), 600, 17)
        text = " ".join(str(lab).upper())  # tracked caps
        tw = d.textlength(text, font=lf)
        cy = h - lab_h / 2 - 12
        dot = int(lab_h * 0.16)
        x0 = (w - tw - dot * 3) / 2
        d.ellipse([x0, cy - dot / 2, x0 + dot, cy + dot / 2], fill=tuple(accent) + (255,))
        d.text((x0 + dot * 2.2, cy), text, font=lf, fill=(160, 162, 172, 255), anchor="lm")
    # settle: a tiny scale "breath" as it lands (once, not a pulse)
    if 0.96 < p < 1.0:
        s = 1 + 0.025 * math.sin((p - 0.96) / 0.04 * math.pi)
        card = card.resize((int(w * s), int(h * s)), Image.BICUBIC)
    return card
