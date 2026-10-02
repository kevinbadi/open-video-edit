#!/usr/bin/env python3
"""Fireship-style ("Code Report") faceless B-roll engine, 1920x1080.

Reverse-engineered 2026-09-29 from Fireship's "Meta is pivoting again" (Code Report,
5:40, study in clone-projects/fireship-style-study/). The narrator never appears: every
second is B-roll (event footage, docs with orange highlighter, tweets, headline cards,
cutouts, memes, sticker text, built-up diagrams), hard-cut roughly every 2.2 s with a
new element landing every ~1-1.5 s, over a continuous music bed.

Author a video as a list of Shot(...) objects (see render_template.py) and call render().
Every device below is deterministic in t, so frames can be rendered in parallel chunks.
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
W, H = 1920, 1080
FPS = 30

# ───────────────────────────── palette (measured off the study frames) ─────────────────────────────
BLACK = (14, 14, 16)          # doc/diagram ground is near-black, not pure
PANEL = (22, 22, 26)
WHITE = (255, 255, 255)
INK = (18, 18, 20)
HIGHLIGHT = (247, 164, 88)    # the orange text highlighter
RED = (230, 36, 52)           # "MUSE" / "BUT" / price box / X marks
ORANGE = (255, 140, 36)       # "$449" price outline fill
YELLOW = (255, 214, 0)        # starburst text
PINK = (255, 150, 190)        # "PINKY PWOMISE" plate
GREEN = (46, 204, 113)        # diagram "PASSWORDS" block, pointer arrows
CYAN = (38, 190, 222)         # diagram "SENTINEL" block
CREAM = (250, 244, 222)       # diagram "WEB" block
PURPLE = (126, 87, 214)       # diagram outer box stroke + caption
DIAG_ORANGE = (255, 126, 54)  # diagram dashed box + labels
TWEET_BG = (0, 0, 0)
TWEET_MUTED = (113, 118, 123)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    files = {
        "display": "LuckiestGuy-Regular.ttf",   # kinetic opener / comic stickers
        "block": "Anton-Regular.ttf",           # "MUSE" red block text, stamps
        "comic": "Bangers-Regular.ttf",         # FREE! / price stickers
        "pixel": "PressStart2P-Regular.ttf",    # year labels, name plates, diagram labels
        "mono": "SpaceMono-Bold.ttf",
        "ui": "Inter.ttf",                      # docs, tweets
        "oswald": "Oswald-Bold.ttf",
    }
    if name == "serif":
        for p in ("/System/Library/Fonts/Supplemental/Georgia Bold.ttf", "/System/Library/Fonts/Supplemental/Georgia.ttf"):
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
        name = "oswald"
    return ImageFont.truetype(os.path.join(FONT_DIR, files[name]), size)


_CACHE: dict = {}


def cached(key, fn):
    if key not in _CACHE:
        _CACHE[key] = fn()
    return _CACHE[key]


def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def ease_out(p: float) -> float:
    p = clamp01(p)
    return 1 - (1 - p) ** 3


def ease_back(p: float, s: float = 1.9) -> float:
    p = clamp01(p) - 1
    return p * p * ((s + 1) * p + s) + 1


def text_size(txt: str, f: ImageFont.FreeTypeFont) -> tuple[int, int, int, int]:
    return ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), txt, font=f)


def outlined_text(txt: str, f, fill, stroke=INK, sw=8, shadow=True, pad=24) -> Image.Image:
    x0, y0, x1, y1 = text_size(txt, f)
    im = Image.new("RGBA", (x1 - x0 + pad * 2 + sw * 2, y1 - y0 + pad * 2 + sw * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = pad + sw - x0, pad + sw - y0
    if shadow:
        d.text((ox + 6, oy + 8), txt, font=f, fill=(0, 0, 0, 150), stroke_width=sw, stroke_fill=(0, 0, 0, 150))
    d.text((ox, oy), txt, font=f, fill=fill + (255,) if len(fill) == 3 else fill, stroke_width=sw,
           stroke_fill=stroke + (255,) if len(stroke) == 3 else stroke)
    return im


# ───────────────────────────── stickers (text slapped on footage) ─────────────────────────────
def sticker(txt: str, style: str = "red_block", size: int = 160) -> Image.Image:
    """Sticker text styles observed in the study:
    red_block   "MUSE"            Anton, red fill, white stroke
    starburst   "FREE!"           Bangers yellow w/ red stroke inside a red/yellow starburst
    comic       "*GULP*"          Luckiest Guy white, thick black stroke
    pink_plate  "PINKY PWOMISE"   black text on a pink plate
    price_box   "$1,300"          white text on a red box
    price_pop   "$449"            orange text, dark stroke
    stamp       "DISCONTINUED"    red rubber stamp, outlined box, rough edge
    name_plate  "ALEXANDR WANG"   pixel font, black on light plate, black border
    quote       '"ONE MORE THING..."'  white Anton caps, black stroke
    year        "2018"            white pixel font, black stroke
    red_caps    "BUT"             red Luckiest Guy, black stroke
    """
    def build():
        if style == "red_block":
            return outlined_text(txt, font("block", size), RED, stroke=WHITE, sw=max(4, size // 22))
        if style == "red_caps":
            return outlined_text(txt, font("display", size), RED, stroke=INK, sw=max(5, size // 16))
        if style == "comic":
            return outlined_text(txt, font("display", size), WHITE, stroke=INK, sw=max(8, size // 9))
        if style == "quote":
            return outlined_text(txt, font("block", size), WHITE, stroke=INK, sw=max(6, size // 12))
        if style == "year":
            return outlined_text(txt, font("pixel", size), WHITE, stroke=INK, sw=max(6, size // 10))
        if style == "price_pop":
            return outlined_text(txt, font("comic", size), ORANGE, stroke=(40, 20, 10), sw=max(6, size // 12))
        f = font({"starburst": "comic", "pink_plate": "block", "price_box": "comic", "stamp": "block",
                  "name_plate": "pixel"}[style], size)
        x0, y0, x1, y1 = text_size(txt, f)
        tw, th = x1 - x0, y1 - y0
        if style == "price_box":
            im = Image.new("RGBA", (tw + 70, th + 60), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, im.width - 1, im.height - 1], fill=RED + (255,))
            d.text((35 - x0, 30 - y0), txt, font=f, fill=WHITE + (255,))
            return im
        if style == "pink_plate":
            im = Image.new("RGBA", (tw + 60, th + 44), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, im.width - 1, im.height - 1], fill=PINK + (255,))
            d.text((30 - x0, 22 - y0), txt, font=f, fill=INK + (255,))
            return im
        if style == "name_plate":
            im = Image.new("RGBA", (tw + 60, th + 50), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, im.width - 1, im.height - 1], fill=(242, 238, 226, 255), outline=INK + (255,), width=5)
            d.text((30 - x0, 25 - y0), txt, font=f, fill=INK + (255,))
            return im
        if style == "stamp":
            im = Image.new("RGBA", (tw + 90, th + 70), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rectangle([6, 6, im.width - 7, im.height - 7], outline=RED + (255,), width=10)
            d.text((45 - x0, 35 - y0), txt, font=f, fill=RED + (255,))
            rng = np.random.default_rng(len(txt))
            a = np.array(im)
            mask = rng.random(a.shape[:2]) < 0.08
            a[mask, 3] = (a[mask, 3] * 0.2).astype(np.uint8)
            return Image.fromarray(a)
        if style == "starburst":
            R = int(max(tw, th) * 0.95)
            im = Image.new("RGBA", (R * 2 + 20, R * 2 + 20), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            cx = cy = R + 10
            pts = []
            for k in range(28):
                r = R if k % 2 == 0 else R * 0.72
                a = k * math.pi / 14 - math.pi / 2
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            d.polygon(pts, fill=RED + (255,))
            inner = [(cx + (x - cx) * 0.86, cy + (y - cy) * 0.86) for x, y in pts]
            d.polygon(inner, fill=YELLOW + (255,))
            inner2 = [(cx + (x - cx) * 0.8, cy + (y - cy) * 0.8) for x, y in pts]
            d.polygon(inner2, fill=RED + (255,))
            d.text((cx, cy), txt, font=f, fill=YELLOW + (255,), anchor="mm", stroke_width=max(4, size // 18),
                   stroke_fill=(150, 0, 0, 255))
            return im
        raise ValueError(style)
    return cached(("sticker", txt, style, size), build)


# ───────────────────────────── cards (docs, tweets, headlines) ─────────────────────────────
def doc_card(lines: list[str], highlight: list[tuple[int, int, int]] | None = None, p: float = 1.0,
             width: int = 1440, size: int = 46, bullet: bool = False) -> Image.Image:
    """White doc snippet on the black ground; `highlight` = [(line, char_from, char_to)] swept
    left-to-right by p (0..1) in the orange highlighter, the study's signature read-along device."""
    f = font("ui", size)
    lh = int(size * 1.5)
    pad = 44
    im = Image.new("RGBA", (width, pad * 2 + lh * len(lines)), WHITE + (255,))
    d = ImageDraw.Draw(im)
    x0 = pad + (40 if bullet else 0)
    if bullet:
        d.ellipse([pad + 6, pad + lh // 2 - 6, pad + 18, pad + lh // 2 + 6], fill=INK)
    spans = highlight or []
    total = sum(max(0, b - a) for _l, a, b in spans) or 1
    budget = p * total
    for li, a, b in spans:
        if budget <= 0:
            break
        take = min(b - a, int(round(budget)))
        budget -= b - a
        pre = d.textlength(lines[li][:a], font=f)
        seg = d.textlength(lines[li][a:a + take], font=f)
        y = pad + li * lh
        d.rectangle([x0 + pre - 2, y + 4, x0 + pre + seg + 2, y + lh - 4], fill=HIGHLIGHT)
    for i, ln in enumerate(lines):
        d.text((x0, pad + i * lh + (lh - size) // 2 - 2), ln, font=f, fill=INK)
    return im


def phrase_spans(lines: list[str], phrase: str) -> list[tuple[int, int, int]]:
    """Highlight spans for a phrase that may wrap across lines (whole words, never mid-word)."""
    words = phrase.split()
    flat = []  # (line, start, end, word)
    for li, ln in enumerate(lines):
        for m in re.finditer(r"\S+", ln):
            flat.append((li, m.start(), m.end(), m.group()))
    norm = lambda w: re.sub(r"[^\w$%']", "", w.lower())
    for i in range(len(flat) - len(words) + 1):
        if all(norm(flat[i + k][3]) == norm(words[k]) for k in range(len(words))):
            spans = {}
            for li, a, b, _w in flat[i:i + len(words)]:
                s0, e0 = spans.get(li, (a, b))
                spans[li] = (min(s0, a), max(e0, b))
            return [(li, a, b) for li, (a, b) in sorted(spans.items())]
    raise ValueError(f"phrase not found: {phrase!r}")


def highlight_image(img: Image.Image, boxes: list[tuple[int, int, int, int]], p: float) -> Image.Image:
    """Orange highlighter swept over a REAL screenshot (Playwright capture of the article/docs).
    boxes are text-line rects in image px; they fill in order as p goes 0..1 (multiply blend)."""
    out = img.convert("RGBA").copy()
    total = sum(b[2] - b[0] for b in boxes) or 1
    budget = p * total
    over = Image.new("RGBA", out.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    for x0, y0, x1, y1 in boxes:
        if budget <= 0:
            break
        w = min(x1 - x0, budget)
        budget -= x1 - x0
        d.rectangle([x0, y0, x0 + w, y1], fill=HIGHLIGHT + (255,))
    base = np.asarray(out).astype(np.float32)
    hl = np.asarray(over).astype(np.float32)
    a = hl[..., 3:4] / 255.0
    base[..., :3] = base[..., :3] * (1 - a) + (base[..., :3] * hl[..., :3] / 255.0) * a
    return Image.fromarray(base.clip(0, 255).astype(np.uint8))


def tweet_card(name: str, handle: str, text: str, avatar: Image.Image | None = None, verified: bool = True,
               meta: str = "", width: int = 1150) -> Image.Image:
    def build():
        f_name, f_h, f_t = font("ui", 38), font("ui", 32), font("ui", 42)
        words, lines, cur = text.split(), [], ""
        dd = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        for w in words:
            t = (cur + " " + w).strip()
            if dd.textlength(t, font=f_t) > width - 80:
                lines.append(cur)
                cur = w
            else:
                cur = t
        lines.append(cur)
        h = 140 + len(lines) * 56 + (60 if meta else 24)
        im = Image.new("RGBA", (width, h), TWEET_BG + (255,))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, width - 1, h - 1], 18, outline=(47, 51, 54, 255), width=2)
        if avatar is not None:
            av = avatar.convert("RGBA").resize((80, 80))
            m = Image.new("L", (80, 80), 0)
            ImageDraw.Draw(m).ellipse([0, 0, 79, 79], fill=255)
            im.paste(av, (36, 30), m)
        else:
            d.ellipse([36, 30, 116, 110], fill=(60, 64, 70, 255))
        d.text((136, 32), name, font=f_name, fill=WHITE)
        nx = 136 + d.textlength(name, font=f_name) + 10
        if verified:
            d.ellipse([nx, 40, nx + 32, 72], fill=(29, 155, 240, 255))
            d.line([nx + 9, 56, nx + 15, 63, nx + 25, 49], fill=WHITE, width=4)
        d.text((136, 78), handle, font=f_h, fill=TWEET_MUTED)
        for i, ln in enumerate(lines):
            d.text((36, 136 + i * 56), ln, font=f_t, fill=(231, 233, 234))
        if meta:
            d.text((36, h - 54), meta, font=f_h, fill=TWEET_MUTED)
        return im
    return cached(("tweet", name, handle, text, id(avatar), verified, meta, width), build)


def headline_card(outlet: str, title: str, dek: str = "", width: int = 1000, dark: bool = False) -> Image.Image:
    """News headline card (Wired/Verge/Reuters look): serif title, small caps outlet line."""
    def build():
        f_o, f_t, f_d = font("mono", 20), font("serif", 52), font("ui", 26)
        dd = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        tl, cur = [], ""
        for w in title.split():
            t = (cur + " " + w).strip()
            if dd.textlength(t, font=f_t) > width - 90:
                tl.append(cur)
                cur = w
            else:
                cur = t
        tl.append(cur)
        h = 90 + len(tl) * 62 + (70 if dek else 30)
        bg, fg = ((20, 20, 22), WHITE) if dark else (WHITE, INK)
        im = Image.new("RGBA", (width, h), bg + (255,))
        d = ImageDraw.Draw(im)
        d.rectangle([40, 34, 40 + d.textlength(outlet.upper(), font=f_o) + 20, 64], fill=fg)
        d.text((50, 36), outlet.upper(), font=f_o, fill=bg)
        for i, ln in enumerate(tl):
            d.text((40, 84 + i * 62), ln, font=f_t, fill=fg)
        if dek:
            d.text((40, 90 + len(tl) * 62), dek, font=f_d, fill=(110, 110, 116) if not dark else (170, 170, 176))
        return im
    return cached(("headline", outlet, title, dek, width, dark), build)


# ───────────────────────────── arrows, cutouts, collage ─────────────────────────────
def curved_arrow(canvas: Image.Image, a: tuple[float, float], b: tuple[float, float], p: float,
                 col=WHITE, width: int = 12, bend: float = 0.35) -> None:
    """Hand-drawn style curved pointer, drawn progressively (p 0..1), white with black outline."""
    p = ease_out(p)
    if p <= 0:
        return
    (x0, y0), (x1, y1) = a, b
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0)
    cx, cy = mx + nx * bend, my + ny * bend
    pts = []
    n = max(2, int(40 * p))
    for i in range(n + 1):
        t = p * i / n
        pts.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1))
    d = ImageDraw.Draw(canvas)
    d.line(pts, fill=INK + (255,), width=width + 8, joint="curve")
    d.line(pts, fill=col + (255,), width=width, joint="curve")
    if p > 0.95:
        ex, ey = pts[-1]
        px, py = pts[-3]
        ang = math.atan2(ey - py, ex - px)
        L = width * 3.2
        head = [(ex, ey), (ex - L * math.cos(ang - 0.5), ey - L * math.sin(ang - 0.5)),
                (ex - L * math.cos(ang + 0.5), ey - L * math.sin(ang + 0.5))]
        d.polygon(head, fill=col + (255,), outline=INK + (255,))


def cutout(path: str, height: int) -> Image.Image | None:
    """A background-removed person/object PNG (use `npx hyperframes remove-background` or rembg
    to make them). Cutouts walk over docs/tweets in the study (Zuck over a tweet, mascot into a doc)."""
    if not os.path.exists(path):
        return None
    def build():
        im = Image.open(path).convert("RGBA")
        bb = im.getbbox()
        if bb:
            im = im.crop(bb)
        s = height / im.height
        return im.resize((max(1, int(im.width * s)), height), Image.LANCZOS)
    return cached(("cutout", path, height), build)


def collage_strip(images: list[Image.Image], width: int = 900, height: int = 640) -> Image.Image:
    """Stacked horizontal crops of several faces (the "everyone reacting" strip at 16.5 s)."""
    def build():
        n = len(images)
        band = height // n
        out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        for i, im in enumerate(images):
            im = im.convert("RGBA")
            s = max(width / im.width, band / im.height)
            r = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
            ox, oy = (r.width - width) // 2, (r.height - band) // 2
            out.paste(r.crop((ox, oy, ox + width, oy + band)), (0 + (i % 2) * 18, i * band))
        return out
    return cached(("collage", tuple(id(i) for i in images), width, height), build)


# ───────────────────────────── diagram builder (the 31 s "how it works" shot) ─────────────────────────────
@dataclass
class DiagramItem:
    t: float                      # appears at this section-local time
    kind: str                     # frame | dashed | label | block | arrow | red_arrow | image
    box: tuple = ()               # (x0, y0, x1, y1) or ((x0,y0),(x1,y1)) for arrows
    text: str = ""
    color: tuple = WHITE
    image: Image.Image | None = None


def draw_diagram(items: list[DiagramItem], lt: float, title: str = "") -> Image.Image:
    """Dark-ground systems diagram that BUILDS in sync with narration: purple outer frame with a
    tiny pixel caption, orange dashed sub-box, orange pixel labels, solid colored blocks
    (green / cyan / cream) with pixel text, white arrows, red arrows for the attack path."""
    im = Image.new("RGBA", (W, H), BLACK + (255,))
    d = ImageDraw.Draw(im)
    fl = font("pixel", 18)
    if title:
        d.text((W // 2, 60), title.upper(), font=font("pixel", 16), fill=PURPLE, anchor="mm")
    for it in items:
        p = clamp01((lt - it.t) / 0.25)
        if p <= 0:
            continue
        a = int(255 * p)
        if it.kind == "frame":
            x0, y0, x1, y1 = it.box
            d.rounded_rectangle(it.box, 16, outline=PURPLE + (a,), width=6)
        elif it.kind == "dashed":
            x0, y0, x1, y1 = it.box
            dash = 18
            for x in range(int(x0), int(x1), dash * 2):
                d.line([x, y0, min(x + dash, x1), y0], fill=DIAG_ORANGE + (a,), width=5)
                d.line([x, y1, min(x + dash, x1), y1], fill=DIAG_ORANGE + (a,), width=5)
            for y in range(int(y0), int(y1), dash * 2):
                d.line([x0, y, x0, min(y + dash, y1)], fill=DIAG_ORANGE + (a,), width=5)
                d.line([x1, y, x1, min(y + dash, y1)], fill=DIAG_ORANGE + (a,), width=5)
            if it.text:
                d.text((x0 + 24, y0 + 22), it.text.upper(), font=fl, fill=DIAG_ORANGE + (a,))
        elif it.kind == "label":
            d.text(it.box[:2], it.text.upper(), font=fl, fill=(it.color if it.color != WHITE else DIAG_ORANGE) + (a,))
        elif it.kind == "block":
            x0, y0, x1, y1 = it.box
            s = 0.85 + 0.15 * ease_back(p)
            cx, cy, w2, h2 = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 * s, (y1 - y0) / 2 * s
            d.rounded_rectangle([cx - w2, cy - h2, cx + w2, cy + h2], 10, fill=it.color + (a,))
            txtc = INK if sum(it.color) > 380 else WHITE
            d.text((cx, cy), it.text.upper(), font=fl, fill=txtc + (a,), anchor="mm")
        elif it.kind in ("arrow", "red_arrow"):
            (x0, y0), (x1, y1) = it.box
            col = RED if it.kind == "red_arrow" else WHITE
            q = ease_out(p)
            ex, ey = x0 + (x1 - x0) * q, y0 + (y1 - y0) * q
            d.line([x0, y0, ex, ey], fill=col + (a,), width=5)
            if q > 0.9:
                ang = math.atan2(y1 - y0, x1 - x0)
                d.polygon([(ex, ey), (ex - 18 * math.cos(ang - 0.45), ey - 18 * math.sin(ang - 0.45)),
                           (ex - 18 * math.cos(ang + 0.45), ey - 18 * math.sin(ang + 0.45))], fill=col + (a,))
            if it.text:
                d.text(((x0 + x1) / 2 + 12, (y0 + y1) / 2 - 10), it.text.upper(), font=font("pixel", 14), fill=col + (a,))
        elif it.kind == "image" and it.image is not None:
            x, y = it.box[:2]
            s = 0.6 + 0.4 * ease_back(p)
            img = it.image.resize((max(1, int(it.image.width * s)), max(1, int(it.image.height * s))), Image.BICUBIC)
            im.alpha_composite(img, (int(x - img.width / 2), int(y - img.height / 2)))
    return im


# ───────────────────────────── transitions + camera ─────────────────────────────
def glitch(frame: Image.Image, k: int, seed: int = 0) -> Image.Image:
    """The 1-3 frame datamosh/slice glitch used on some cuts: horizontal bands displaced,
    RGB channels split, a few bands swapped to black."""
    a = np.asarray(frame.convert("RGB")).copy()
    rng = np.random.default_rng(seed * 97 + k)
    out = a.copy()
    y = 0
    while y < H:
        h = int(rng.integers(8, 70))
        dx = int(rng.integers(-220, 220)) if rng.random() < 0.55 else 0
        out[y:y + h] = np.roll(a[y:y + h], dx, axis=1)
        if rng.random() < 0.12:
            out[y:y + h] = (out[y:y + h] * 0.15).astype(np.uint8)
        y += h
    shift = int(rng.integers(10, 26))
    out[..., 0] = np.roll(out[..., 0], shift, axis=1)
    out[..., 2] = np.roll(out[..., 2], -shift, axis=1)
    return Image.fromarray(out)


def bulge_pop(img: Image.Image, p: float) -> Image.Image:
    """Fisheye/barrel pop-in (the article bursting in at 1.5 s): strong bulge + scale-up that
    relaxes to flat by p=1. Returns an RGBA of the same size as img."""
    import cv2
    p = clamp01(p)
    if p >= 1:
        return img
    a = np.asarray(img.convert("RGBA"))
    h, w = a.shape[:2]
    k = 0.55 * (1 - ease_out(p))
    yy, xx = np.indices((h, w), dtype=np.float32)
    nx, ny = (xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)
    r2 = nx * nx + ny * ny
    f = 1 + k * r2
    scale = 0.55 + 0.45 * ease_back(p)
    mx = (nx / f / scale) * (w / 2) + w / 2
    my = (ny / f / scale) * (h / 2) + h / 2
    out = cv2.remap(a, mx, my, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return Image.fromarray(out)


def fit_cover(img: Image.Image, w: int = W, h: int = H, zoom: float = 1.0, fx: float = 0.5, fy: float = 0.5) -> Image.Image:
    s = max(w / img.width, h / img.height) * zoom
    r = img.resize((int(img.width * s) + 1, int(img.height * s) + 1), Image.BICUBIC)
    ox, oy = int((r.width - w) * fx), int((r.height - h) * fy)
    return r.crop((ox, oy, ox + w, oy + h))


class Footage:
    """Sequential-friendly video reader (full-bleed B-roll: keynote footage, screen recordings)."""
    _open: dict = {}

    def __init__(self, path: str):
        import cv2
        self.path = path
        self.cap = cv2.VideoCapture(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.idx = -10
        self.last = None

    def frame(self, t: float) -> Image.Image:
        import cv2
        n = max(0, int(t * self.fps))
        if n != self.idx + 1:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ok, fr = self.cap.read()
        if ok:
            self.last = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
        self.idx = n
        return self.last if self.last is not None else Image.new("RGB", (W, H), BLACK)


def footage(path: str) -> Footage:
    if path not in Footage._open:
        Footage._open[path] = Footage(path)
    return Footage._open[path]


# ───────────────────────────── title card + kinetic opener ─────────────────────────────
def title_card(show: str, date_str: str, lt: float, accent=RED) -> Image.Image:
    """Show-title card (the study's "THE CODE REPORT" + red date): boxed stacked title on black
    with a scale-in, light-leak sweep, the date underneath. Use YOUR show name, never Fireship's."""
    im = Image.new("RGBA", (W, H), BLACK + (255,))
    words = show.upper().split()
    top, rest = (words[0], " ".join(words[1:])) if len(words) > 1 else ("", show.upper())
    f_big, f_small = font("oswald", 210), font("oswald", 84)
    d = ImageDraw.Draw(im)
    lines = rest.split() if len(rest.split()) <= 2 else [rest]
    bw = max(d.textlength(l, font=f_big) for l in lines) + 90
    bh = 225 * len(lines) + 70
    p = ease_back(clamp01(lt / 0.35))
    card = Image.new("RGBA", (int(bw), int(bh)), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rectangle([0, 0, bw - 1, bh - 1], outline=WHITE + (255,), width=18)
    for i, l in enumerate(lines):
        cd.text((bw / 2, 45 + i * 225 + 110), l, font=f_big, fill=WHITE, anchor="mm")
    s = 0.7 + 0.3 * p
    card = card.resize((max(1, int(card.width * s)), max(1, int(card.height * s))), Image.BICUBIC)
    im.alpha_composite(card, (W // 2 - card.width // 2, H // 2 - card.height // 2 + 20))
    if top:
        d.text((W // 2 - card.width // 2 + 10, H // 2 - card.height // 2 - 76), top, font=f_small, fill=WHITE)
    if lt > 0.25:
        d.text((W // 2, H // 2 + card.height // 2 + 90), date_str.upper(), font=font("oswald", 58), fill=accent)
    # light sweep
    x = int(-400 + (lt / 1.2) * (W + 800))
    sweep = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sweep).polygon([(x, 0), (x + 180, 0), (x - 120, H), (x - 300, H)], fill=60)
    im = Image.composite(Image.new("RGBA", (W, H), (255, 255, 255, 255)), im, sweep.filter(ImageFilter.GaussianBlur(40)))
    return im


def kinetic_words(words: list[tuple[str, float]], lt: float) -> Image.Image:
    """Cold-open word-by-word text on black ("EARLIER THIS ..."), each word landing on its
    spoken onset (section-local seconds), newest word in white, rounded heavy caps."""
    im = Image.new("RGBA", (W, H), BLACK + (255,))
    shown = [w for w, t in words if lt >= t]
    if not shown:
        return im
    line = " ".join(shown[-3:]).upper()
    f = font("display", 110)
    d = ImageDraw.Draw(im)
    d.text((W // 2, H // 2), line, font=f, fill=WHITE, anchor="mm")
    return im


# ───────────────────────────── timeline model ─────────────────────────────
@dataclass
class Layer:
    """An element on top of a shot: draw(canvas, lt) with lt = shot-local seconds.
    t0/t1 bound it; `pop` scales it in with overshoot like every sticker in the study."""
    t0: float
    t1: float
    img: Callable[[float], Image.Image | None] | Image.Image | None = None
    xy: tuple[float, float] = (W / 2, H / 2)
    tilt: float = 0.0
    anim: str = "pop"           # pop | slide_left | slide_right | slide_up | none | bulge
    draw: Callable[[Image.Image, float], None] | None = None


@dataclass
class Shot:
    t0: float
    t1: float
    bg: Callable[[float, float], Image.Image] | None = None   # (lt, abs_t) -> RGB/RGBA frame
    layers: list[Layer] = field(default_factory=list)
    glitch_in: bool = False     # 2-frame glitch on this cut (use on ~1 in 5 cuts, never all)
    note: str = ""


def _place(canvas: Image.Image, L: Layer, lt: float) -> None:
    if lt < L.t0 or lt >= L.t1:
        return
    if L.draw is not None:
        L.draw(canvas, lt - L.t0)
        return
    im = L.img(lt - L.t0) if callable(L.img) else L.img
    if im is None:
        return
    p = clamp01((lt - L.t0) / 0.22)
    x, y = L.xy
    if L.anim == "bulge":
        im = bulge_pop(im, clamp01((lt - L.t0) / 0.4))
    elif L.anim == "pop":
        s = 0.35 + 0.65 * ease_back(p)
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    elif L.anim.startswith("slide"):
        q = 1 - ease_out(p)
        dx, dy = {"slide_left": (-1, 0), "slide_right": (1, 0), "slide_up": (0, 1)}[L.anim]
        x += dx * q * 900
        y += dy * q * 700
    if L.tilt:
        im = im.rotate(L.tilt, expand=True, resample=Image.BICUBIC)
    canvas.alpha_composite(im.convert("RGBA"), (int(x - im.width / 2), int(y - im.height / 2)))


def black_bg(lt: float, t: float) -> Image.Image:
    return Image.new("RGBA", (W, H), BLACK + (255,))


def image_bg(path_or_img, zoom_per_s: float = 0.015, fx: float = 0.5, fy: float = 0.5):
    """Still full-bleed with a slow push-in (screenshots/photos never sit dead still)."""
    src = Image.open(path_or_img).convert("RGB") if isinstance(path_or_img, str) else path_or_img
    return lambda lt, t: fit_cover(src, zoom=1.0 + zoom_per_s * lt, fx=fx, fy=fy)


def video_bg(path: str, src_start: float = 0.0, zoom: float = 1.0):
    return lambda lt, t: fit_cover(footage(path).frame(src_start + lt), zoom=zoom)


def render(shots: list[Shot], duration: float, out_dir: str = "frames/out", fps: int = FPS) -> None:
    """Render frames (RANGE="a:b" env for parallel chunks, PREVIEW="1.0,5.2" for spot checks)."""
    os.makedirs(out_dir, exist_ok=True)
    n = int(duration * fps)
    todo = list(range(n))
    if os.environ.get("PREVIEW"):
        todo = [int(float(x) * fps) for x in os.environ["PREVIEW"].split(",")]
    elif os.environ.get("RANGE"):
        a, b = os.environ["RANGE"].split(":")
        todo = list(range(int(a), min(n, int(b))))
    shots = sorted(shots, key=lambda s: s.t0)
    for fi in todo:
        t = fi / fps
        sh = next((s for s in shots if s.t0 <= t < s.t1), shots[-1])
        lt = t - sh.t0
        bg = sh.bg(lt, t) if sh.bg else black_bg(lt, t)
        canvas = bg.convert("RGBA") if bg.size == (W, H) else fit_cover(bg.convert("RGBA"))
        for L in sh.layers:
            _place(canvas, L, lt)
        frame = canvas.convert("RGB")
        if sh.glitch_in and lt < 2.5 / fps:
            frame = glitch(frame, int(lt * fps), seed=int(sh.t0 * 10))
        frame.save(f"{out_dir}/f{fi:05d}.jpg", quality=92)
        if os.environ.get("PREVIEW"):
            print(f"preview {fi} t={t:.2f} {sh.note}", flush=True)
        elif fi % 60 == 0:
            print(f"{fi}/{n}", flush=True)


def mux(out_dir: str, voice: str, music: str | None, out: str, fps: int = FPS, bed_db: float = -17.0) -> None:
    """Encode + mix: VO on top, continuous music bed ducked under it (study: bed sits ~2-3 dB
    under speech in the gaps, LRA ~3 LU = heavily compressed), loudness-normalised for YouTube."""
    inputs = ["-framerate", str(fps), "-i", f"{out_dir}/f%05d.jpg", "-i", voice]
    if music:
        inputs += ["-stream_loop", "-1", "-i", music]
        af = (f"[2:a]volume={bed_db}dB[bed];[bed][1:a]sidechaincompress=threshold=0.05:ratio=6:attack=15:release=250[duck];"
              "[1:a]acompressor=threshold=-20dB:ratio=3:attack=5:release=80[vo];"
              "[vo][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:LRA=4:TP=-1.5[a]")
        amap = ["-filter_complex", af, "-map", "0:v", "-map", "[a]"]
    else:
        amap = ["-map", "0:v", "-map", "1:a", "-af", "acompressor=threshold=-20dB:ratio=3,loudnorm=I=-14:LRA=4:TP=-1.5"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, *amap, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", out], check=True)


def words_onsets(words_json: str) -> list[tuple[str, float, float]]:
    return [(w.strip(), float(a), float(b)) for w, a, b in json.load(open(words_json))]


def at(words: list[tuple[str, float, float]], word: str, after: float = 0.0) -> float:
    """Absolute onset of the first `word` at/after `after` (beats land ON the spoken word)."""
    wl = word.lower()
    for w, a, _b in words:
        if a >= after and w.lower().strip(".,!?\"'") == wl:
            return a
    return after
