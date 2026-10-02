#!/usr/bin/env python3
"""Split animated talking-head: Social SDK killed Hootsuite and Sprout.

1080x1920. Hook is the Claude invader locking onto Hootsuite and Sprout
and shooting both logos, then a full-figure $1,000,000,000 odometer.
"""
import json
import math
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = open("animation_assets_and_beats.py").read()
ASSETS = SRC.split('os.makedirs("frames/out2"')[0]
exec(compile(ASSETS, "animation_assets", "exec"), globals())

from hyper_edits import (  # noqa: E402
    caption_impact,
    clamp01,
    ease_in_cubic,
    entrance,
    guarded_conveyor,
    hyperframe,
    lanes,
    number_beats,
    punch_beats,
    punch_scale,
    punch_zoom,
    shake_offset,
    typewriter,
    whip_dir,
    whip_wipe,
)
from media_marks import (  # noqa: E402
    auto_counters,
    counter_card,
    gif_card,
    logo_badge,
    odometer_card,
    topic_marks,
)
from light_fx import (  # noqa: E402
    bloom_orb,
    caption_bloom,
    hud_scan,
    light_hit,
    light_rays,
    neon_grid,
    scanlines,
    slot_vignette,
    speed_streaks,
)
from claude_marks import place_claude_invader, place_claude_sphinx  # noqa: E402

INK = (10, 11, 14)
SILVER = (198, 204, 214)
STEEL = (92, 98, 108)
GRAPHITE = (36, 38, 46)
CHAR = (48, 50, 58)
NEON = (57, 255, 132)
ORANGE = (255, 122, 24)
RED = (255, 48, 64)
CORAL = ORANGE
PAPER = GRAPHITE
WHITE = (255, 252, 248)
MONO = F(ML, 22)
MONO_S = F(ML, 18)

AH = 770
LAYER_Y = 90
PACK_DY = 210
BAND_Y = 936
SAFE_X = (36, 1044)
BAND_W, BAND_H = 1056, 960
if (W, H) != (1080, 1920):
    raise SystemExit(f"must be 1080x1920, got {W}x{H}")

meta = json.load(open("source/meta.json"))
DUR = float(meta["DUR"])
words = json.load(open("audio/words.json"))
N = int(round(DUR * FPS))

SECT = [
    ("hook", 0.00, 6.32),
    ("kid", 6.32, 11.94),
    ("agent", 11.94, 19.82),
    ("build", 19.82, 23.70),
    ("cta", 23.70, DUR + 0.05),
]
KEYWORDS = {
    "claude", "killed", "hootsuite", "sprout", "social", "billion",
    "15", "open", "source", "sdk", "agent", "unlimited", "accounts",
    "schedule", "competitor", "free", "comment",
}
SECT_ACCENT = {
    "hook": ORANGE, "kid": NEON, "agent": (80, 170, 255), "build": RED, "cta": NEON,
}
KEY_COL = {
    "claude": ORANGE, "killed": RED, "hootsuite": RED, "sprout": NEON,
    "social": NEON, "billion": ORANGE, "15": ORANGE, "open": NEON, "source": NEON,
    "sdk": NEON, "agent": (80, 170, 255), "unlimited": NEON, "accounts": ORANGE,
    "schedule": ORANGE, "competitor": RED, "free": NEON, "comment": NEON,
}


def textured_bg(base, seed, glow=ORANGE):
    rng = np.random.default_rng(seed)
    arr = np.tile(np.array(base, np.float32), (H + 160, W + 160, 1))
    arr += rng.normal(0, 2.4, (H + 160, W + 160, 1))
    arr += rng.normal(0, 6.0, (H + 160, 1, 1)) * 0.22
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    sh = Image.new("L", (W + 160, H + 160), 0)
    d = ImageDraw.Draw(sh)
    for cx, cy, rx, ry in [(180, 220, 460, 300), (720, 980, 480, 340), (540, 80, 360, 220)]:
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=48)
    sh = sh.filter(ImageFilter.GaussianBlur(90))
    lift = Image.new("RGB", (W + 160, H + 160), tuple(min(255, c + 18) for c in base))
    base_img = Image.composite(lift, img, sh)
    glow_l = Image.new("L", (W + 160, H + 160), 0)
    gd = ImageDraw.Draw(glow_l)
    gd.ellipse([W // 2 - 500, 0, W // 2 + 660, 820], fill=70)
    glow_l = glow_l.filter(ImageFilter.GaussianBlur(140))
    glow_rgb = Image.new("RGB", (W + 160, H + 160), glow)
    return Image.composite(glow_rgb, base_img, glow_l)


BGS = {
    "hook": textured_bg((48, 36, 32), 7, ORANGE),
    "kid": textured_bg((36, 48, 42), 11, NEON),
    "agent": textured_bg((32, 40, 52), 13, (80, 170, 255)),
    "build": textured_bg((48, 34, 38), 17, RED),
    "cta": textured_bg((36, 48, 44), 19, NEON),
}


def trel(word, after=0.0):
    for w, a, b in words:
        if a >= after - 0.01 and w.strip().rstrip(".,!?").lower() == word:
            return a
    return after


T_KILLED = trel("killed")
T_HOOT = trel("hootsuite")
T_SPROUT = trel("sprout")
T_BILLION = trel("billion")
T_A = trel("a", 5.0)
T_15 = trel("15")
T_OPEN = trel("open")
T_SDK = trel("social", 9.0)
T_AGENT = trel("agent")
T_UNLIM = trel("unlimited")
T_ACCOUNTS = trel("accounts")
T_SCHED = trel("schedule")
T_BUILD = trel("build")
T_SPROUT2 = trel("sprout", 20)
T_HOOT2 = trel("hootsuite", 20)
T_COMMENT = trel("comment")
T_SOCIAL_CTA = trel("social", 24)


def place(frame, img, cx, cy, lt, t0, dur=0.3, frm="up", tilt=0.0, idle=5, scale_pop=False, exit_at=None):
    if img is None:
        return
    p = ease((lt - t0) / dur) if dur else 1.0
    if p <= 0:
        return
    alpha = p
    if exit_at is not None:
        q = (lt - exit_at) / 0.22
        if q >= 1:
            return
        if q > 0:
            alpha = min(alpha, 1 - q)
            p2 = ease(q)
        else:
            p2 = 0
    else:
        p2 = 0
    off = 90 * (1 - p)
    dx, dy = {"up": (0, off), "down": (0, -off), "left": (off, 0), "right": (-off, 0)}.get(frm, (0, off))
    if idle and img.width < 400 and img.height < 400:
        ph = (cx * 0.37 + cy * 0.61) % 6.28
        per = 3.2 + ((cx + cy) % 7) * 0.35
        dy += min(3.0, idle) * math.sin(ph + (lt * 2 * math.pi) / per)
    dy -= 120 * p2
    im = img
    if scale_pop:
        pop = outp((lt - t0) / max(0.05, dur))
        im = im.resize((max(1, int(im.width * pop)), max(1, int(im.height * pop))), Image.BICUBIC)
    if tilt:
        im = im.rotate(tilt, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    x = int(cx - im.width / 2 + dx)
    y = int(cy + PACK_DY - im.height / 2 + dy)
    max_w = SAFE_X[1] - SAFE_X[0]
    if im.width <= max_w:
        x = max(SAFE_X[0], min(SAFE_X[1] - im.width, x))
    else:
        x = max(0, min(W - im.width, x))
    y = max(0, min(AH - min(im.height, AH), y))
    frame.alpha_composite(im, (x, y))


GIF_Q = []


def front_gif(*args, **kwargs):
    GIF_Q.append((args, kwargs))


def flush_gifs(layer):
    while GIF_Q:
        args, kwargs = GIF_Q.pop(0)
        place(layer, *args, **kwargs)


def os_chip(txt, accent=ORANGE, fsz=28):
    def build():
        fnt = F(AR, fsz)
        tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(txt, font=fnt))
        w, h = tw + 48, fsz + 28
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 14, fill=GRAPHITE + (255,))
        d.rectangle([0, 0, 8, h], fill=accent + (255,))
        d.text((28, h / 2), txt, font=fnt, fill=SILVER + (255,), anchor="lm")
        return img
    return cached(("oschip", txt, accent, fsz), build)


def title_card(txt, accent=ORANGE, fsz=72, w=960, h=150):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 28, fill=GRAPHITE + (255,))
        d.rectangle([0, 0, 14, h], fill=accent + (255,))
        d.text((w / 2 + 6, h / 2 - 2), txt, font=F(AR, fsz), fill=WHITE + (255,), anchor="mm")
        return img
    return cached(("title", txt, accent, fsz, w, h), build)


def reticle(size=240, accent=RED, locked=False):
    def build():
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        c = size // 2
        col = (accent if locked else STEEL) + (230,)
        d.ellipse([8, 8, size - 9, size - 9], outline=col, width=4)
        d.ellipse([c - 8, c - 8, c + 8, c + 8], outline=col, width=3)
        arm = 28
        d.line([(c, 0), (c, arm)], fill=col, width=4)
        d.line([(c, size - arm), (c, size)], fill=col, width=4)
        d.line([(0, c), (arm, c)], fill=col, width=4)
        d.line([(size - arm, c), (size, c)], fill=col, width=4)
        return img
    return cached(("ret", size, accent, locked), build)


def brand_target(slug, size=230):
    badge = logo_badge(slug, size=size, punch=True, fill=WHITE + (255,))
    return badge


def dead_stamp(w=220):
    def build():
        img = Image.new("RGBA", (w, 78), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, 77], 12, outline=RED + (255,), width=6)
        d.text((w / 2, 39), "DEAD", font=F(AR, 48), fill=RED + (255,), anchor="mm")
        return img
    return cached(("dead", w), build)


def terminal_card(lines, w=700, h=280, title="agent"):
    key = tuple(lines)

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 22, fill=INK + (255,))
        d.rectangle([0, 0, 10, h], fill=NEON + (255,))
        d.text((28, 16), title, font=F(AR, 22), fill=STEEL + (255,))
        y = 58
        for line in lines:
            d.text((28, y), line, font=MONO, fill=NEON + (255,))
            y += 36
        return img
    return cached(("term", key, w, h, title), build)


def ghost_word(text, size=120, alpha=50):
    def build():
        fnt = F(AR, size)
        tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        tw = int(tmp.textlength(text, font=fnt))
        img = Image.new("RGBA", (tw + 20, size + 20), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((10, 4), text, font=fnt, fill=SILVER + (alpha,))
        return img
    return cached(("ghost", text, size, alpha), build)


def laser(layer, x0, y0, x1, y1, p, accent=ORANGE):
    p = clamp01(p)
    bx = x0 + (x1 - x0) * p
    by = y0 + (y1 - y0) * p
    d = ImageDraw.Draw(layer)
    d.line([(x0, y0), (bx, by)], fill=accent + (90,), width=22)
    d.line([(x0, y0), (bx, by)], fill=(255, 244, 220, 255), width=8)
    r = 18
    d.ellipse([bx - r, by - r, bx + r, by + r], fill=WHITE + (255,))
    d.ellipse([x0 - 10, y0 - 10, x0 + 10, y0 + 10], fill=accent + (255,))


def shatter(layer, img, cx, cy, age):
    if img is None:
        return
    cols = rows = 3
    tw, th = max(1, img.width // cols), max(1, img.height // rows)
    for r in range(rows):
        for c in range(cols):
            piece = img.crop((c * tw, r * th, img.width if c == cols - 1 else (c + 1) * tw,
                              img.height if r == rows - 1 else (r + 1) * th))
            ang = math.atan2(r - 1, c - 1) + (0.4 if (r + c) % 2 else -0.2)
            dist = age * 340
            alpha = max(0, 1 - age / 0.85)
            if alpha <= 0:
                continue
            pc = piece.copy()
            pc.putalpha(pc.split()[3].point(lambda v, a=alpha: int(v * a)))
            rot = age * (180 if c > 1 else -160)
            pc = pc.rotate(rot, expand=True, resample=Image.BICUBIC)
            x = int(cx - img.width / 2 + c * tw + math.cos(ang) * dist - pc.width / 2)
            y = int(cy - img.height / 2 + r * th + math.sin(ang) * dist - 40 * age - pc.height / 2)
            if 0 <= x < W and 0 <= y < AH:
                layer.alpha_composite(pc, (x, y))