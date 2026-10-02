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
  figure_row(layer, ["dario-amodei", "daniela-amodei"], 540, 280, lt, 1.4, place, size=480)
  figure_spotlight(layer, "sam-altman", 540, 260, lt, 0.4, place, size=560)
  place(layer, figure_card("sam-altman", w=380), 270, 300, lt, 0.9, frm="left")
  place(layer, figure_round("elon-musk", 520, ring=CORAL), 540, 260, lt, 0.2, scale_pop=True)
  guarded_conveyor(layer, 400 + PACK_DY, lt, topic_marks(["openai", "cursor"]),
                   conveyor_marks, name="topic-lane", speed=180, gap=22)
"""
from __future__ import annotations

import json
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from fonts import AR as _AR, F as _F  # Oswald Bold — never Arial in the slot
_INK = (10, 11, 14)
_CORAL = (255, 122, 24)
_PAPER = (26, 28, 32)
_SILVER = (198, 204, 214)
_NEON = (57, 255, 132)
_RED = (255, 48, 64)

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
            col = _NEON + (255,) if frame == "bezel" else (_SILVER + (255,))
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


def figure_round(slug: str, size: int = 360, ring=_CORAL, ring_w: int | None = None, shadow: bool = True) -> Image.Image | None:
    """Circular portrait badge with a colored ring — the default figure mark.
    Intro/hook: 520–620. Two-up row: 400. Body single: ≥280. Never <240."""
    if ring_w is None:
        ring_w = max(8, round(size * 0.035))
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


def figure_card(slug: str, w: int = 380, name: bool = True, role: bool = True,
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
            d.text((pad + 16, y), txt, font=name_f, fill=_SILVER + (255,))
            y += 44
        if role and meta.get("role"):
            r = meta["role"]
            while d.textlength(r, font=role_f) > w - 32 and len(r) > 4:
                r = r[:-1]
            d.text((pad + 16, y), r, font=role_f, fill=_SILVER + (200,))
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


def figure_row(layer, slugs, cx, cy, lt, t0, place, size=320, gap=24, stagger=0.12,
               exit_at=None, ring=_CORAL, tilt=True, names=False):
    """Centered row of round portraits, staggered entrance, alternating tilt.
    Intro/hook: two faces at size=480. Body: 2–3 at size≥320. Never 3-up on
    the first section. `place` is the compositor's place() so PACK_DY / clamps apply."""
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


def figure_spotlight(layer, slug, cx, cy, lt, t0, place, size=560, exit_at=None, ring=_CORAL):
    """Hero portrait + name plate + role: use when ONE figure is the beat.
    Intro default 560; do not pass size<480."""
    m = figure_round(slug, size, ring=ring)
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
# Kevin 2026-09-15: compact "2B" cards and casino-slot odometers (orange
# cages, overflowing glyphs, Gaussian mush, "COUNTING TOKENS") are trash.
# Hero numbers are a mechanical ticker: full figures, live commas, geared
# reels (ones fly, billions crawl), hairline wells, no overlay on top.

_STEEL = (92, 98, 108)
_GRAPHITE = (36, 38, 46)


def _comma_groups(n: int) -> tuple[int, ...]:
    """10 → (1, 3, 3, 3); 7 → (1, 3, 3); 4 → (1, 3)."""
    groups = []
    left = n
    while left > 3:
        groups.append(3)
        left -= 3
    groups.append(left)
    return tuple(reversed(groups))


def _digit_glyph(ch: str, fsz: int, fill: tuple[int, ...]) -> Image.Image:
    def build():
        font = _F(_AR, fsz)
        d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        tw = int(d0.textlength(ch, font=font)) + 6
        h = int(fsz * 1.22)
        img = Image.new("RGBA", (max(tw, 8), h), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((img.width / 2, img.height / 2), ch, font=font, fill=fill, anchor="mm")
        return img
    return _cached(("odigit", ch, fsz, fill), build)


def _reel(wheel: float, sw: int, sh: int, fsz: int, fill: tuple[int, ...]) -> Image.Image:
    """Vertical 0-9 strip clipped to one cell. wheel is continuous (3.4 → 3 rolling to 4)."""
    d0 = int(math.floor(wheel)) % 10
    frac = wheel - math.floor(wheel)
    d1 = (d0 + 1) % 10
    g0 = _digit_glyph(str(d0), fsz, fill)
    g1 = _digit_glyph(str(d1), fsz, fill)
    strip = Image.new("RGBA", (sw, sh * 2), (0, 0, 0, 0))
    strip.alpha_composite(g0, ((sw - g0.width) // 2, int(sh * 0.5 - g0.height / 2)))
    strip.alpha_composite(g1, ((sw - g1.width) // 2, int(sh * 1.5 - g1.height / 2)))
    y0 = int(frac * sh)
    return strip.crop((0, y0, sw, y0 + sh))


def odometer_card(beat, p, w=1000, h=400, fill=None, fg=(255, 252, 248, 255),
                  accent=(255, 122, 24), label=None, **_kw):
    """Hero number, Apple-style rolling counter (Kevin 2026-09-29 replaced the
    boxed-reel odometer: "find and implement a modern apple inspired odometer").
    See templates/apple_counter.py."""
    from apple_counter import apple_counter
    return apple_counter(beat, p, w=w or 1000, h=max(h, 300), label=label, accent=accent)

def _use_odometer(beat) -> bool:
    v = abs(float(beat.get("value") or 0))
    suf = beat.get("suffix") or ""
    if suf in ("%", "x") or "PM" in suf or "AM" in suf:
        return False
    return v >= 10_000 and float(v).is_integer()


def counter_card(beat, p, w=None, h=380, fill=None, fg=(255, 252, 248, 255), accent=(255, 122, 24),
                 label=None, t=0.0):
    """Every hero number uses the Apple-style rolling counter now (2026-09-29):
    SF Pro digits rolling with motion blur, odometer carry, no leading zeros,
    frosted glass card. Full figures with commas; compact 2B is chips only."""
    from apple_counter import apple_counter
    lab = label if label is not None else (beat.get("label") or "")
    n = len(str(int(abs(float(beat.get("value") or 0)))))
    ww = w or max(420, min(1000, 180 + n * int(h * 0.42)))
    return apple_counter(beat, p, w=ww, h=h, label=lab, accent=accent)

def auto_counters(layer, beats, t, sect_start, place, handled=(), cx=540, cy=160, dur=0.9, hold=1.4,
                  h=380, fill=None, accent=(255, 122, 24)):
    """Draw a counter for every number beat the choreography did not handle.
    `handled` = set of beat['t'] the section already animates by hand. The
    counter enters ON the spoken number (t0 = beat.t), counts for `dur`,
    holds, and flies out `hold` seconds after landing. Big figures get a
    longer count so the odometer can tick through places."""
    for bt in beats:
        if bt["t"] in handled:
            continue
        t0 = bt["t"] - sect_start
        lt = t - sect_start
        this_dur = 1.15 if _use_odometer(bt) else dur
        this_h = max(h, 400) if _use_odometer(bt) else h
        if lt < t0 or lt > t0 + this_dur + hold + 0.25:
            continue
        p = (lt - t0) / this_dur
        place(layer, counter_card(bt, p, h=this_h, fill=fill, accent=accent), cx, cy, lt, t0, dur=0.22,
              frm="up", scale_pop=True, exit_at=t0 + this_dur + hold)


# ─────────────────────────── topic logo lane ───────────────────────────
# Kevin 2026-09-10: the horizontal scroll of associated brand icons is a
# staple. Fetch real marks into assets/logos/, then:
#   guarded_conveyor(layer, 400 + PACK_DY, lt, topic_marks(slugs),
#                    conveyor_marks, name="topic-lane", speed=180, gap=22)

def logo_mark(slug: str, size: int = 120, punch: bool = True,
              root: str = "assets/logos") -> Image.Image | None:
    """Punched, letterboxed mark from assets/logos/<slug>.png."""
    path = os.path.join(root, f"{slug}.png")
    if not os.path.isfile(path):
        return None

    def build():
        im = Image.open(path).convert("RGBA")
        if punch:
            px = list(im.getdata())
            im.putdata([
                (r, g, b, 0) if r > 232 and g > 232 and b > 232 else (r, g, b, a)
                for r, g, b, a in px
            ])
        bbox = im.getbbox()
        if bbox:
            im = im.crop(bbox)
        im.thumbnail((size, size), Image.LANCZOS)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        canvas.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im)
        return canvas
    return _cached(("logomark", path, size, punch), build)


def logo_badge(slug: str, size: int = 120, punch: bool = True,
               fill: tuple[int, ...] | None = None) -> Image.Image | None:
    """Graphite-backed logo tile for the topic conveyor."""
    mark = logo_mark(slug, int(size * 0.72), punch=punch)
    if mark is None:
        return None
    bg = fill or (_PAPER + (255,))

    def build():
        card, pad = _shadow_card((size, size), 22, bg)
        card.alpha_composite(
            mark,
            ((card.width - mark.width) // 2, (card.height - mark.height) // 2 - 2),
        )
        return card
    return _cached(("logobadge", slug, size, punch, bg), build)


def topic_marks(slugs: list[str], size: int = 120, punch: bool = True,
                fill: tuple[int, ...] | None = None) -> list[Image.Image]:
    """5–8 associated logos for guarded_conveyor. Drops missing slugs."""
    out: list[Image.Image] = []
    for slug in slugs:
        badge = logo_badge(slug, size=size, punch=punch, fill=fill)
        if badge is not None:
            out.append(badge)
    return out


# ───────────────────────────── globe (Kevin 2026-09-19 GitNexus "on the planet") ─────────────────────────────
import math as _math  # noqa: E402
import numpy as _np  # noqa: E402
from PIL import ImageFilter as _ImageFilter  # noqa: E402

_CYAN = (56, 200, 248)
_PURPLE = (150, 96, 255)
_NEON = (57, 255, 132)


def globe_card(spin, size=360, col=_CYAN, col2=_PURPLE):
    """Spinning wireframe globe: tilted latitude rings + rotating meridians + rim glow."""
    k = int(spin * 30) % 90

    def build():
        pad = 40
        img = Image.new("RGBA", (size + pad * 2, size + pad * 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cx = cy = size / 2 + pad
        R = size / 2
        # glow + body
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([cx - R - 18, cy - R - 18, cx + R + 18, cy + R + 18], fill=col + (90,))
        glow = glow.filter(_ImageFilter.GaussianBlur(22))
        img.alpha_composite(glow)
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(14, 16, 28, 255), outline=col + (230,), width=4)
        tilt = 0.38
        ang = (k / 90.0) * 2 * _math.pi
        # latitude rings
        for lat in (-60, -30, 0, 30, 60):
            la = _math.radians(lat)
            ry = R * _math.cos(la) * tilt
            rx = R * _math.cos(la)
            yy = cy - R * _math.sin(la)
            box = [cx - rx, yy - ry, cx + rx, yy + ry]
            d.arc(box, 0, 180, fill=col + (150 if lat else 220,), width=2 if lat else 3)
            d.arc(box, 180, 360, fill=col + (70,), width=1)
        # meridians (rotating)
        for i in range(8):
            phi = ang + i * _math.pi / 8
            rx = abs(R * _math.cos(phi))
            front = _math.sin(phi) >= 0
            if rx < 3:
                d.line([(cx, cy - R), (cx, cy + R)], fill=col2 + (200 if front else 60,), width=2)
                continue
            box = [cx - rx, cy - R, cx + rx, cy + R]
            if front:
                d.arc(box, 90, 270, fill=col2 + (200,), width=2) if _math.cos(phi) < 0 else d.arc(box, 270, 90, fill=col2 + (200,), width=2)
            else:
                d.arc(box, 90, 270, fill=col2 + (60,), width=1) if _math.cos(phi) < 0 else d.arc(box, 270, 90, fill=col2 + (60,), width=1)
        # a few "repo" pins that ride the rotation
        rng = _np.random.default_rng(3)
        for j in range(14):
            lat = _math.radians(float(rng.uniform(-55, 65)))
            lon = float(rng.uniform(0, 2 * _math.pi)) + ang
            x3 = _math.cos(lat) * _math.sin(lon)
            z3 = _math.cos(lat) * _math.cos(lon)
            y3 = _math.sin(lat)
            if z3 < 0:
                continue
            px = cx + R * x3
            py = cy - R * (y3 * (1 - tilt) + 0.0) - R * y3 * 0.0
            py = cy - R * y3
            r = 5 + 4 * z3
            d.ellipse([px - r, py - r, px + r, py + r], fill=_NEON + (255,))
        # rim highlight
        d.arc([cx - R + 6, cy - R + 6, cx + R - 6, cy + R - 6], 200, 320, fill=(255, 255, 255, 110), width=3)
        return img
    return _cached(("globe", k, size, col, col2), build)
