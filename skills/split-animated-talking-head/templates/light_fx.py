#!/usr/bin/env python3
"""Light FX layer for the split-animated slot (Kevin 2026-09-10).

HUD scanlines, neon floor grid, bloom orbs, impact rings, spark bursts,
lens flares, god rays, speed streaks. Deterministic in t. Cheap PIL.

The motion graphics are the content; this is the *light pass* on the
1080x770 animation slot. Never light the talking-head band.

Wire-up (after graphics + GIFs, before punch_zoom / whip):

    from light_fx import (
        scanlines, hud_scan, neon_grid, slot_vignette,
        bloom_orb, rim_pulse, impact_ring, spark_burst,
        flare, light_rays, speed_streaks, light_hit, caption_bloom,
    )
    scanlines(layer, t)
    hud_scan(layer, t, NEON)
    neon_grid(layer, t, STEEL)
    bloom_orb(layer, cx, cy, 180, ORANGE, a=70)
    light_hit(layer, cx, cy, t, t0, ORANGE)   # ring + sparks + flare
    speed_streaks(layer, t, PUNCH_T, NEON)
    slot_vignette(layer)

Hits land on the spoken word (same t0 as the graphic). Atmosphere
(scanlines / grid / hud_scan) runs every frame from frame 0.
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter

_CACHE: dict = {}


def _clamp01(p: float) -> float:
    return 0.0 if p < 0 else 1.0 if p > 1 else p


def _cached(key, fn):
    if key not in _CACHE:
        _CACHE[key] = fn()
    return _CACHE[key]


def scanlines(layer: Image.Image, t: float, alpha: int = 22, period: int = 4) -> None:
    """CRT / HUD scanlines that crawl 1px per frame."""
    w, h = layer.size
    sheet = _cached(("scan", w, h, period, alpha), lambda: _scan_sheet(w, h, period, alpha))
    off = int(t * 30) % period
    layer.alpha_composite(sheet, (0, -off))


def _scan_sheet(w: int, h: int, period: int, alpha: int) -> Image.Image:
    im = Image.new("RGBA", (w, h + period), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(0, h + period, period):
        d.line([0, y, w, y], fill=(255, 255, 255, alpha))
    return im


def hud_scan(layer: Image.Image, t: float, color=(57, 255, 132), speed: float = 380.0,
             thick: int = 3) -> None:
    """Single bright scan bar sweeping the slot top→bottom, looping."""
    w, h = layer.size
    y = int((t * speed) % (h + 80)) - 40
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, y, w, y + thick], fill=color + (150,))
    d.rectangle([0, y - 10, w, y], fill=color + (40,))
    d.rectangle([0, y + thick, w, y + thick + 14], fill=color + (28,))
    layer.alpha_composite(ov)


def neon_grid(layer: Image.Image, t: float, color=(92, 98, 108), y0: int = 520,
              rows: int = 7, cols: int = 9) -> None:
    """Perspective floor grid near the caption line. Scrolls toward camera."""
    w, h = layer.size
    d = ImageDraw.Draw(layer)
    vanish_x = w // 2
    vanish_y = 90
    scroll = (t * 0.35) % 1.0
    for i in range(rows):
        p = _clamp01((i + scroll) / rows)
        y = int(y0 + (h - 8 - y0) * (p ** 1.6))
        a = int(28 + 70 * p)
        d.line([20, y, w - 20, y], fill=color + (a,), width=1)
    for j in range(cols + 1):
        u = j / cols
        x1 = int(40 + (w - 80) * u)
        d.line([vanish_x, vanish_y, x1, h - 4], fill=color + (36,), width=1)


def slot_vignette(layer: Image.Image, a: int = 22) -> None:
    w, h = layer.size
    vig = _cached(("vig", w, h, a), lambda: _vignette(w, h, a))
    layer.alpha_composite(vig)


def _vignette(w: int, h: int, a: int) -> Image.Image:
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([-w * 0.15, -h * 0.2, w * 1.15, h * 1.25], fill=255)
    m = ImageOps_invert_blur(m)
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ov.putalpha(m.point(lambda v: int(v * a / 255)))
    return ov


def ImageOps_invert_blur(m: Image.Image) -> Image.Image:
    inv = m.point(lambda v: 255 - v)
    return inv.filter(ImageFilter.GaussianBlur(28))


def bloom_orb(layer: Image.Image, cx: float, cy: float, r: int, color,
              a: int = 70) -> None:
    """Soft colored glow behind a hero / invader / GIF."""
    r = max(24, int(r))
    orb = _cached(("orb", r, color, a), lambda: _orb(r, color, a))
    layer.alpha_composite(orb, (int(cx - orb.width / 2), int(cy - orb.height / 2)))


def _orb(r: int, color, a: int) -> Image.Image:
    s = r * 2 + 40
    im = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(im)
    d.ellipse([20, 20, s - 20, s - 20], fill=a)
    im = im.filter(ImageFilter.GaussianBlur(r // 2 + 8))
    rgb = Image.new("RGB", (s, s), color)
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    out.paste(rgb, (0, 0))
    out.putalpha(im)
    return out


def rim_pulse(layer: Image.Image, cx: float, cy: float, r: float, t: float,
              color, hz: float = 1.4) -> None:
    """Breathing neon ring."""
    p = 0.55 + 0.45 * math.sin(t * hz * math.tau)
    rr = r * (0.92 + 0.10 * p)
    a = int(80 + 90 * p)
    d = ImageDraw.Draw(layer)
    box = [cx - rr, cy - rr, cx + rr, cy + rr]
    d.ellipse(box, outline=color + (a,), width=3)


def impact_ring(layer: Image.Image, cx: float, cy: float, t: float, t0: float,
                color, life: float = 0.42, r0: float = 30, r1: float = 280) -> None:
    """Expanding shockwave on a punch / GIF land / title slam."""
    p = _clamp01((t - t0) / life)
    if p <= 0 or p >= 1:
        return
    r = r0 + (r1 - r0) * (1 - (1 - p) ** 2)
    a = int(200 * (1 - p))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color + (a,), width=max(2, int(8 * (1 - p))))
    r2 = r * 0.72
    d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=color + (a // 3,), width=2)


def spark_burst(layer: Image.Image, cx: float, cy: float, t: float, t0: float,
                color, n: int = 14, life: float = 0.38, rad: float = 220) -> None:
    p = _clamp01((t - t0) / life)
    if p <= 0 or p >= 1:
        return
    d = ImageDraw.Draw(layer)
    a = int(230 * (1 - p))
    e = 1 - (1 - p) ** 2
    for i in range(n):
        ang = (i / n) * math.tau + t0 * 3.1
        rr = rad * e
        x = cx + math.cos(ang) * rr
        y = cy + math.sin(ang) * rr
        s = max(2, int(7 * (1 - p)))
        d.ellipse([x - s, y - s, x + s, y + s], fill=color + (a,))
        d.line([cx + math.cos(ang) * rr * 0.35, cy + math.sin(ang) * rr * 0.35, x, y],
               fill=color + (a // 2,), width=1)


def flare(layer: Image.Image, cx: float, cy: float, t: float, t0: float,
          color, life: float = 0.28) -> None:
    """Cross flare + two ghost orbs. Short hit."""
    p = _clamp01((t - t0) / life)
    if p <= 0 or p >= 1:
        return
    a = int(180 * (1 - p) ** 1.4)
    span = 90 + 70 * (1 - p)
    d = ImageDraw.Draw(layer)
    d.line([cx - span, cy, cx + span, cy], fill=color + (a,), width=3)
    d.line([cx, cy - span * 0.45, cx, cy + span * 0.45], fill=color + (a,), width=2)
    for k, sc in ((0.55, 0.18), (1.15, 0.10)):
        ox = cx + span * k * 0.35
        oy = cy + 8
        rr = span * sc
        d.ellipse([ox - rr, oy - rr, ox + rr, oy + rr], fill=color + (a // 3,))


def light_rays(layer: Image.Image, cx: float, cy: float, t: float, color,
               n: int = 7, a: int = 28) -> None:
    """Rotating god-rays behind a CTA / invader."""
    w, h = layer.size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rot = t * 18
    reach = max(w, h)
    for i in range(n):
        ang = math.radians(rot + i * (360 / n))
        half = math.radians(7)
        pts = [
            (cx, cy),
            (cx + math.cos(ang - half) * reach, cy + math.sin(ang - half) * reach),
            (cx + math.cos(ang + half) * reach, cy + math.sin(ang + half) * reach),
        ]
        d.polygon(pts, fill=color + (a,))
    layer.alpha_composite(ov.filter(ImageFilter.GaussianBlur(6)))


def speed_streaks(layer: Image.Image, t: float, hits, color=(57, 255, 132),
                  life: float = 0.16) -> None:
    """Diagonal speed lines on punch-ins."""
    age = None
    for h in hits:
        d = t - h
        if 0 <= d < life and (age is None or d < age):
            age = d
    if age is None:
        return
    p = age / life
    a = int(90 * (1 - p))
    w, hgt = layer.size
    d = ImageDraw.Draw(layer)
    for i in range(9):
        y = 40 + i * (hgt - 80) / 8 + 18 * math.sin(i + t * 9)
        x0 = -40 + i * 30
        d.line([x0, y, x0 + 160 * (1 - p), y - 18], fill=color + (a,), width=2)


def light_hit(layer: Image.Image, cx: float, cy: float, t: float, t0: float,
              color) -> None:
    """One-call punch: shockwave + sparks + flare."""
    impact_ring(layer, cx, cy, t, t0, color)
    spark_burst(layer, cx, cy, t, t0, color)
    flare(layer, cx, cy, t, t0, color)


def caption_bloom(frame: Image.Image, x: float, y: float, tw: float, th: float,
                  color, a: int = 70) -> None:
    """Soft glow under a kinetic caption word (draw BEFORE the text).
    Kevin 2026-09-19: "the glow the captions give off is way too large" -> a tight
    halo hugging the word (radius from the word HEIGHT, not its width), a=40."""
    r = int(th * 0.55 + 10)
    bloom_orb(frame, x + tw / 2, y + th / 2, r, color, a=min(a, 40))
