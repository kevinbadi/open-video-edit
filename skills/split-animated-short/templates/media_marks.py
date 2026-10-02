#!/usr/bin/env python3
"""Media marks for the split-animated renderer: Giphy GIF cards, notable-figure
portraits, logos and counters. Pure PIL; drop next to
render.py and `from media_marks import *`.

Assets are produced by the skill scripts:
  scripts/fetch_giphy.py   → assets/gifs/<slug>/f0000.png + meta.json
  scripts/fetch_figure.py  → assets/figures/<slug>.png + .json

Choreography (layer pixels, 1080x770 slot; cy goes through the compositor's
place()/py() like every other asset):

  place(layer, gif_card("mind-blown", lt - 2.1, w=520), 540, 300, lt, 2.1, exit_at=4.4)
  figure_row(layer, ["dario-amodei", "daniela-amodei", "jack-clark"], 540, 260, lt, 1.4, place)
  place(layer, figure_card("sam-altman", w=300), 270, 300, lt, 0.9, frm="left")
  place(layer, figure_round("elon-musk", 260, ring=CORAL), 810, 240, lt, 1.2, scale_pop=True)
"""
from __future__ import annotations

import json
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

_AR = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
_MENLO = "/System/Library/Fonts/Menlo.ttc"
_F = lambda p, s: ImageFont.truetype(p, s)  # noqa: E731
_INK = (30, 28, 26)
_CORAL = (217, 111, 78)
_PAPER = (250, 249, 246)

_CACHE: dict = {}


def _cached(key, fn):
    if key not in _CACHE:
        _CACHE[key] = fn()
    return _CACHE[key]


def _shadow_card(size, radius, fill, blur=16, alpha=70):
    w, h = size
    pad = blur * 2
    card = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + w, pad + h + 10], radius, fill=(20, 18, 16, alpha))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(blur // 2)))
    ImageDraw.Draw(card).rounded_rectangle([pad, pad, pad + w, pad + h], radius, fill=fill)
    return card, pad


# ─────────────────────────────── GIFs ───────────────────────────────

def gif_meta(slug: str, root: str = "assets/gifs") -> dict | None:
    p = os.path.join(root, slug, "meta.json")
    if not os.path.isfile(p):
        return None
    return _cached(("gifmeta", p), lambda: json.load(open(p)))


def gif_frame(slug: str, t: float, w: int | None = None, loop: bool = True,
              root: str = "assets/gifs", speed: float = 1.0) -> Image.Image | None:
    """Raw GIF frame at local time t (seconds since the GIF started)."""
    meta = gif_meta(slug, root)
    if not meta:
        return None
    n = meta["frames"]
    idx = int(max(0.0, t * speed) * meta["fps"])
    idx = idx % n if loop else min(idx, n - 1)
    path = os.path.join(root, slug, f"f{idx + 1:04d}.png")
    if not os.path.isfile(path):
        path = os.path.join(root, slug, f"f{idx:04d}.png")

    def build():
        im = Image.open(path).convert("RGBA")
        if w and im.width != w:
            im = im.resize((w, max(1, int(im.height * w / im.width))), Image.LANCZOS)
        return im
    return _cached(("gif", path, w), build)


def gif_card(slug: str, t: float, w: int = 520, radius: int = 28, label: str | None = None,
             loop: bool = True, frame: str = "card", speed: float = 1.0) -> Image.Image | None:
    """GIF in a rounded, shadowed card (frame="card"), a bare rounded clip
    (frame="round"), or a phone-ish dark bezel (frame="bezel"). Label = small
    chip under the GIF ("giphy" style caption or a one-word punch)."""
    fr = gif_frame(slug, t, w=w, loop=loop, speed=speed)
    if fr is None:
        return None
    key = ("gifcard", slug, int(t * (gif_meta(slug)["fps"]) * speed) % max(1, gif_meta(slug)["frames"]), w, radius, label, frame)

    def build():
        iw, ih = fr.size
        mask = Image.new("L", (iw, ih), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, iw - 1, ih - 1], radius, fill=255)
        clip = fr.copy()
        clip.putalpha(mask)
        if frame == "round":
            return clip
        bez = 14 if frame == "bezel" else 10
        lab_h = 54 if label else 0
        fill = (24, 22, 20, 255) if frame == "bezel" else (_PAPER + (255,))
        card, pad = _shadow_card((iw + bez * 2, ih + bez * 2 + lab_h), radius + 8, fill)
        card.alpha_composite(clip, (pad + bez, pad + bez))
        if label:
            d = ImageDraw.Draw(card)
            f = _F(_AR, 26)
            tw = d.textlength(label, font=f)
            col = (159, 227, 180, 255) if frame == "bezel" else (_INK + (255,))
            d.text((pad + bez + (iw - tw) / 2, pad + bez + ih + 12), label, font=f, fill=col)
        return card
    return _cached(key, build)


# ───────────────────────────── figures ─────────────────────────────

def figure_meta(slug: str, root: str = "assets/figures") -> dict:
    p = os.path.join(root, f"{slug}.json")
    if not os.path.isfile(p):
        return {"name": slug.replace("-", " ").title(), "role": ""}
    return _cached(("figmeta", p), lambda: json.load(open(p)))


def _figure_img(slug: str, size: int, root: str = "assets/figures") -> Image.Image | None:
    p = os.path.join(root, f"{slug}.png")
    if not os.path.isfile(p):
        return None
    return _cached(("figimg", p, size), lambda: Image.open(p).convert("RGBA").resize((size, size), Image.LANCZOS))


def figure_round(slug: str, size: int = 240, ring=_CORAL, ring_w: int = 8, shadow: bool = True) -> Image.Image | None:
    """Circular portrait badge with a colored ring — the default figure mark."""
    im = _figure_img(slug, size - ring_w * 2)
    if im is None:
        return None

    def build():
        pad = 24 if shadow else 0
        out = Image.new("RGBA", (size + pad * 2, size + pad * 2), (0, 0, 0, 0))
        if shadow:
            sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).ellipse([pad, pad + 10, pad + size, pad + size + 10], fill=(20, 18, 16, 80))
            out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(10)))
        d = ImageDraw.Draw(out)
        d.ellipse([pad, pad, pad + size, pad + size], fill=ring + (255,))
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).ellipse([0, 0, im.width - 1, im.height - 1], fill=255)
        face = im.copy()
        face.putalpha(m)
        out.alpha_composite(face, (pad + ring_w, pad + ring_w))
        return out
    return _cached(("figround", slug, size, ring, ring_w, shadow), build)


def figure_card(slug: str, w: int = 300, name: bool = True, role: bool = True,
                accent=_CORAL, radius: int = 26) -> Image.Image | None:
    """Portrait card: photo on top, bold name + dim role line beneath."""
    meta = figure_meta(slug)
    im = _figure_img(slug, w - 24)
    if im is None:
        return None

    def build():
        name_f = _F(_AR, 30)
        role_f = _F(_AR, 21)
        h = (w - 24) + 12 + (44 if name else 0) + (30 if role and meta.get("role") else 0) + 14
        card, pad = _shadow_card((w, h), radius, _PAPER + (255,))
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius - 8, fill=255)
        photo = im.copy()
        photo.putalpha(m)
        card.alpha_composite(photo, (pad + 12, pad + 12))
        d = ImageDraw.Draw(card)
        d.rectangle([pad + 12, pad + 12, pad + 12 + 10, pad + 12 + im.height], fill=accent + (255,))
        y = pad + 12 + im.height + 12
        if name:
            txt = meta.get("name", slug)
            while d.textlength(txt, font=name_f) > w - 32 and len(txt) > 4:
                txt = txt[:-1]
            d.text((pad + 16, y), txt, font=name_f, fill=_INK + (255,))
            y += 44
        if role and meta.get("role"):
            r = meta["role"]
            while d.textlength(r, font=role_f) > w - 32 and len(r) > 4:
                r = r[:-1]
            d.text((pad + 16, y), r, font=role_f, fill=(120, 116, 110, 255))
        return card
    return _cached(("figcard", slug, w, name, role, accent, radius), build)


def name_plate(text: str, sub: str = "", w: int | None = None, fill=_INK, fg=(255, 252, 248, 255)) -> Image.Image:
    """Lower-third style name plate (bold name, small role), for a figure spotlight."""
    def build():
        f1, f2 = _F(_AR, 40), _F(_AR, 24)
        d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        tw = max(d0.textlength(text, font=f1), d0.textlength(sub, font=f2) if sub else 0)
        ww = w or int(tw + 56)
        hh = 64 + (34 if sub else 0)
        img = Image.new("RGBA", (ww, hh), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, ww, hh], 18, fill=fill + (255,))
        d.rectangle([0, 0, 12, hh], fill=_CORAL + (255,))
        d.text((28, 12), text, font=f1, fill=fg)
        if sub:
            d.text((28, 60), sub, font=f2, fill=fg[:3] + (200,))
        return img
    return _cached(("nameplate", text, sub, w, fill, fg), build)


def figure_row(layer, slugs, cx, cy, lt, t0, place, size=220, gap=36, stagger=0.12,
               exit_at=None, ring=_CORAL, tilt=True, names=False):
    """Centered row of round portraits, staggered entrance, alternating tilt.
    `place` is the compositor's place() so PACK_DY / clamps apply."""
    marks = [(s, figure_round(s, size, ring=ring)) for s in slugs]
    marks = [(s, m) for s, m in marks if m is not None]
    if not marks:
        return
    step = size + gap
    x0 = cx - step * (len(marks) - 1) / 2
    for i, (s, m) in enumerate(marks):
        x = int(x0 + i * step)
        place(layer, m, x, cy, lt, t0 + i * stagger, frm=("left", "up", "right")[i % 3],
              tilt=((-6, 4, -4, 6)[i % 4] if tilt else 0), scale_pop=True, exit_at=exit_at)
        if names:
            meta = figure_meta(s)
            first = meta.get("name", s).split(" ")[0]
            place(layer, name_plate(first, fill=_INK), x, cy + size // 2 + 46, lt, t0 + i * stagger + 0.08,
                  frm="down", exit_at=exit_at)


def figure_spotlight(layer, slug, cx, cy, lt, t0, place, size=420, exit_at=None, ring=_CORAL):
    """Hero portrait + name plate + role: use when ONE figure is the beat."""
    m = figure_round(slug, size, ring=ring, ring_w=12)
    if m is None:
        return
    meta = figure_meta(slug)
    place(layer, m, cx, cy, lt, t0, scale_pop=True, exit_at=exit_at)
    place(layer, name_plate(meta.get("name", slug), meta.get("role", "")), cx, cy + size // 2 + 70, lt, t0 + 0.12,
          frm="down", exit_at=exit_at)


def figures_on_disk(niche: str | None = None, root: str = "assets/figures") -> list[str]:
    """Slugs fetched for a niche (in fetch order = fame order), or all."""
    if not os.path.isdir(root):
        return []
    out = []
    for f in sorted(os.listdir(root)):
        if f.endswith(".json"):
            m = json.load(open(os.path.join(root, f)))
            if niche is None or m.get("niche") == niche:
                out.append((os.path.getmtime(os.path.join(root, f)), m["slug"]))
    return [s for _, s in sorted(out)]


# ─────────────────────────── number counters ───────────────────────────

def counter_card(beat, p, w=None, h=300, fill=None, fg=(255, 252, 248, 255), accent=(217, 111, 78),
                 label=None, t=0.0):
    """Animated count-up hero for a transcript number. `beat` from
    hyper_edits.number_beats(); p = (lt - t0) / 0.9 clamped. Digits count
    expo.out, the card squash-pops when the number lands, an accent bar
    sweeps underneath. Cached per displayed value so it is cheap."""
    from hyper_edits import counter_value, fmt_number, clamp01, ease_back_out
    p = clamp01(p)
    v = counter_value(beat, p)
    txt = fmt_number(v, beat.get("prefix", ""), beat.get("suffix", ""), style=beat.get("style", ""))
    lab = label if label is not None else beat.get("label", "")
    fill = fill or _INK
    key = ("counter", txt, lab, w, h, fill, accent, int(p * 60))

    def build():
        f1 = _F(_AR, int(h * 0.5))
        f2 = _F(_AR, max(24, int(h * 0.12)))
        d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        # width fits the WIDEST string the count-up will show (e.g. "1,999" is wider than "2026")
        tw = max(d0.textlength(fmt_number(counter_value(beat, q), beat.get("prefix", ""), beat.get("suffix", ""), style=beat.get("style", "")), font=f1)
                 for q in (0.1, 0.3, 0.5, 0.7, 0.85, 0.95, 1.0))
        ww = w or int(max(tw + 120, 420))
        img = Image.new("RGBA", (ww, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, ww, h], 36, fill=fill + (255,))
        # landed pop: brief squash when p crosses ~0.97
        tw_now = d.textlength(txt, font=f1)
        d.text(((ww - tw_now) / 2, int(h * 0.09)), txt, font=f1, fill=fg)
        if lab:
            tw2 = d.textlength(lab, font=f2)
            d.text(((ww - tw2) / 2, int(h * 0.66)), lab, font=f2, fill=fg[:3] + (225,))
        # accent sweep
        d.rounded_rectangle([40, h - 26, 40 + int((ww - 80) * p), h - 12], 8, fill=accent + (255,))
        return img
    im = _cached(key, build)
    # squash-pop at the landing (not cached: cheap resize)
    if 0.94 < p < 1.0:
        s = 1 + 0.06 * (1 - abs((p - 0.97) / 0.03))
        im = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
    return im


def auto_counters(layer, beats, t, sect_start, place, handled=(), cx=540, cy=160, dur=0.9, hold=1.4,
                  h=300, fill=None, accent=(217, 111, 78)):
    """Draw a counter for every number beat the choreography did not handle.
    `handled` = set of beat['t'] the section already animates by hand. The
    counter enters ON the spoken number (t0 = beat.t), counts for `dur`,
    holds, and flies out `hold` seconds after landing."""
    for bt in beats:
        if bt["t"] in handled:
            continue
        t0 = bt["t"] - sect_start
        lt = t - sect_start
        if lt < t0 or lt > t0 + dur + hold + 0.25:
            continue
        p = (lt - t0) / dur
        place(layer, counter_card(bt, p, h=h, fill=fill, accent=accent), cx, cy, lt, t0, dur=0.22,
              frm="up", scale_pop=True, exit_at=t0 + dur + hold)
