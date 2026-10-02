#!/usr/bin/env python3
"""Split animated talking-head: JEV, TypeSafe AI's non-LLM "System One" model.

1080x1920. Live band 1056x960 at y=936. Animation slot AH=770 at LAYER_Y=90,
PACK_DY=210, captions at y=867. Journey: mystery cold open -> 200x faster /
cheaper counters -> Claude Fable pricing -> JEV reveal (TypeSafe mark + Diogo
Almeida) -> one word at a time -> out the window -> three ways (action /
yes-no / score) -> not an LLM -> video games -> Subway Surfers -> RL loop -> CTA.
Max two big pieces. No em/en dashes on screen.
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
    count_up,
    ease_back_out,
    guarded_conveyor,
    hyperframe,
    lanes,
    number_beats,
    punch_scale,
    punch_zoom,
    shake_offset,
    typewriter,
    whip_dir,
    whip_wipe,
    word_onset,
)
from media_marks import (  # noqa: E402
    auto_counters,
    counter_card,
    figure_row,
    figure_spotlight,
    gif_card,
    hf_layer_frame,
    logo_badge,
    logo_mark,
    topic_marks,
)
from light_fx import (  # noqa: E402
    bloom_orb,
    caption_bloom,
    hud_scan,
    light_hit,
    light_rays,
    neon_grid,
    rim_pulse,
    scanlines,
    slot_vignette,
    speed_streaks,
)
from claude_marks import place_claude_invader, place_claude_sphinx, skill_chip  # noqa: E402

INK = (10, 11, 14)
SILVER = (198, 204, 214)
STEEL = (92, 98, 108)
GRAPHITE = (36, 38, 46)
CHAR = (48, 50, 58)
NEON = (57, 255, 132)
ORANGE = (255, 122, 24)
RED = (255, 48, 64)
PINK = (236, 72, 153)      # TypeSafe / JEV brand pink
CORAL = ORANGE
PAPER = GRAPHITE
MONO = F(ML, 22)
MONO_S = F(ML, 18)


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
    "hook": textured_bg((40, 42, 52), 7, ORANGE),
    "reveal": textured_bg((54, 44, 54), 11, PINK),
    "onebyone": textured_bg((48, 48, 56), 13, STEEL),
    "toss": textured_bg((54, 44, 46), 15, RED),
    "threeways": textured_bg((42, 50, 54), 17, NEON),
    "shock": textured_bg((54, 44, 54), 19, PINK),
    "games": textured_bg((44, 48, 58), 21, ORANGE),
    "subway": textured_bg((44, 50, 56), 23, NEON),
    "cta": textured_bg((42, 52, 48), 25, NEON),
}

AH = 770
LAYER_Y = 90
PACK_DY = 210
CAP_Y = 867
BAND_Y = 936
CAP_BOTTOM = BAND_Y - 12
SAFE_X = (36, 1044)
BAND_W, BAND_H = 1056, 960
if (W, H) != (1080, 1920):
    raise SystemExit(f"must be 1080x1920, got {W}x{H}")

meta = json.load(open("source/meta.json"))
DUR = float(meta["DUR"])
words = json.load(open("audio/words.json"))
N = int(DUR * FPS)

SECT = [
    ("hook", 0.00, 9.50),
    ("reveal", 9.50, 16.60),
    ("onebyone", 16.60, 26.30),
    ("toss", 26.30, 30.80),
    ("threeways", 30.80, 42.30),
    ("shock", 42.30, 50.20),
    ("games", 50.20, 57.30),
    ("subway", 57.30, 70.40),
    ("cta", 70.40, DUR),
]
KEYWORDS = {
    "new", "model", "released", "200", "faster", "cheaper", "claude", "fable", "5.1",
    "jev", "wild", "anything", "explain",
    "one", "word", "time", "agent", "response",
    "threw", "window", "designed",
    "three", "ways", "action", "choice", "yes", "no", "score", "data",
    "shocking", "beautiful", "large", "language",
    "examples", "crazy", "video", "games",
    "subway", "surfers", "questions", "complete", "click", "reinforcement", "learning", "perfects",
    "access", "release", "comment",
}
SECT_ACCENT = {
    "hook": ORANGE, "reveal": PINK, "onebyone": ORANGE, "toss": RED,
    "threeways": NEON, "shock": PINK, "games": ORANGE, "subway": NEON, "cta": NEON,
}
KEY_COL = {
    "new": ORANGE, "model": ORANGE, "released": RED, "200": NEON, "faster": NEON, "cheaper": NEON,
    "claude": ORANGE, "fable": ORANGE, "5.1": ORANGE,
    "jev": PINK, "wild": RED, "anything": RED, "explain": NEON,
    "one": ORANGE, "word": ORANGE, "time": ORANGE, "agent": NEON, "response": ORANGE,
    "threw": RED, "window": RED, "designed": NEON,
    "three": NEON, "ways": NEON, "action": ORANGE, "choice": ORANGE, "yes": NEON, "no": RED,
    "score": ORANGE, "data": ORANGE,
    "shocking": RED, "beautiful": PINK, "large": RED, "language": RED,
    "examples": ORANGE, "crazy": RED, "video": ORANGE, "games": ORANGE,
    "subway": NEON, "surfers": NEON, "questions": ORANGE, "complete": ORANGE, "click": ORANGE,
    "reinforcement": NEON, "learning": NEON, "perfects": NEON,
    "access": ORANGE, "release": ORANGE, "comment": NEON,
}


def trel(word, sect_a, after=None, lead=0.08):
    ons = word_onset(words, word, after=after if after is not None else sect_a)
    if ons is None:
        return 0.05
    return max(0.0, (ons - lead) - sect_a)


def tabs(word, after):
    """Absolute onset of the first `word` at/after `after`."""
    ons = word_onset(words, word, after=after)
    return ons if ons is not None else after


# ───────────────────────────── cards ─────────────────────────────

def chip(txt, accent=None):
    accent = accent or NEON

    def build():
        f2 = F(AR, 24)
        tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(txt, font=f2))
        img = Image.new("RGBA", (tw + 48, 58), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, tw + 47, 57], 16, fill=GRAPHITE + (255,))
        d.rectangle([0, 0, 8, 57], fill=accent + (255,))
        d.text((24, 14), txt, font=f2, fill=SILVER + (255,))
        return img

    return cached(("chipA", txt, accent), build)


def ghost_img(text, size):
    def build():
        img = Image.new("RGBA", (W + 400, size + 60), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((200, 10), text, font=F(AR, size), fill=SILVER + (44,))
        return img

    return cached(("ghA", text, size), build)


def big_text_card(txt, fill=ORANGE, fg=None, fsz=52, w=960, h=130):
    if fg is None:
        fg = INK + (255,) if fill in (NEON, ORANGE, RED, PINK) else SILVER + (255,)

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w, h], 26, fill=fill + (255,), outline=SILVER + (70,), width=2)
        f2 = F(AR, fsz)
        parts = txt.split()
        gap = 16
        widths = [d.textlength(p, font=f2) for p in parts]
        total = sum(widths) + gap * max(0, len(parts) - 1)
        x = (w - total) / 2
        y = (h - fsz) / 2 - 6
        for part, pw in zip(parts, widths):
            d.text((x, y), part, font=f2, fill=fg)
            x += pw + gap
        return img

    return cached(("btcA", txt, fill, fsz, w, h), build)


def draw_code_rain(layer, lt, n=18, col=NEON):
    glyphs = [
        "jev", "typesafe", "action", "yes/no", "score", "rlcd", "70ms",
        "$0.042", "system-1", "typed", "decision", "p=0.94",
    ]
    d = ImageDraw.Draw(layer)
    for i in range(n):
        x = 16 + (i * 58) % 980
        y = int((lt * 120 + i * 47) % 620) - 40
        d.text((x, y), glyphs[i % len(glyphs)], font=MONO_S, fill=col + (70,))


def ticker(layer, text, y, lt, speed=140, fill=SILVER + (80,)):
    d = ImageDraw.Draw(layer)
    tw = int(d.textlength(text, font=MONO))
    span = tw + 90
    x = layer.size[0] - int((lt * speed) % (span + layer.size[0]))
    d.text((x, y), text, font=MONO, fill=fill)


def product_shot(slug, w=520, h=360, label=None, accent=ORANGE):
    def build():
        path = f"assets/shots/{slug}.png"
        if not os.path.isfile(path):
            path = f"assets/shots/{slug}.jpg"
        if not os.path.isfile(path):
            return None
        im = Image.open(path).convert("RGBA")
        scale = max(w / im.width, h / im.height)
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
        x0 = (im.width - w) // 2
        y0 = 0
        im = im.crop((x0, y0, x0 + w, y0 + h))
        card = shadow_card((w + 20, h + (60 if label else 20)), 22, GRAPHITE + (255,))
        # shadow_card pads by blur*2 = 32
        pad = 32
        card.alpha_composite(im, (pad + 10, pad + 10))
        d = ImageDraw.Draw(card)
        d.rectangle([pad, pad, pad + 8, pad + h + 20], fill=accent + (255,))
        if label:
            d.text((pad + 24, pad + h + 22), label, font=F(AR, 24), fill=SILVER + (255,))
        return card

    return cached(("pshot", slug, w, h, label, accent), build)


def mystery_card(lt, w=960, h=380):
    """Cold open: dark card, glitching '?', whisper line. Reveal on 'new'."""
    k = int(lt * 30)

    def build():
        rng = np.random.default_rng(k)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w, h], 30, fill=(18, 19, 24, 255), outline=STEEL + (120,), width=2)
        fq = F(AR, 260)
        cx, cy = w / 2, h / 2 - 8
        jitter = 0 if (k % 9) else int(rng.integers(-14, 14))
        # rgb split glitch
        d.text((cx - 6 + jitter, cy), "?", font=fq, fill=RED + (150,), anchor="mm")
        d.text((cx + 6 - jitter, cy), "?", font=fq, fill=NEON + (150,), anchor="mm")
        d.text((cx, cy), "?", font=fq, fill=SILVER + (255,), anchor="mm")
        if k % 7 == 0:
            y = int(rng.integers(30, h - 30))
            d.rectangle([20, y, w - 20, y + 6], fill=PINK + (140,))
        d.text((cx, h - 42), "a new model just dropped", font=F(AR, 30), fill=STEEL + (255,), anchor="mm")
        return img

    return cached(("mystery", k % 63), build)


def stat_chip(big, small, accent=NEON, w=440, h=150):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w, h], 24, fill=GRAPHITE + (255,), outline=accent + (160,), width=3)
        d.text((w / 2, 58), big, font=F(AR, 76), fill=accent + (255,), anchor="mm")
        d.text((w / 2, 120), small, font=F(AR, 24), fill=SILVER + (255,), anchor="mm")
        return img
    return cached(("statchip", big, small, accent, w, h), build)


def chat_card(text_full, p, w=960, h=300, who="agent"):
    """LLM chat bubble typing word by word."""
    parts = text_full.split()
    n = int(clamp01(p) * (len(parts) + 1))
    shown = " ".join(parts[:n])
    cursor = (int(p * 30) % 2 == 0)

    def build():
        card = shadow_card((w, h), 24, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad + 16, pad + 14, pad + w - 16, pad + 62], 14, fill=INK + (255,))
        d.text((pad + 34, pad + 24), who, font=F(AR, 24), fill=ORANGE + (255,))
        d.ellipse([pad + w - 60, pad + 28, pad + w - 40, pad + 48], fill=NEON + (255,))
        # wrap
        f2 = F(AR, 34)
        x, y = pad + 34, pad + 86
        maxw = w - 68
        line = ""
        for wd in shown.split():
            test = (line + " " + wd).strip()
            if d.textlength(test, font=f2) > maxw:
                d.text((x, y), line, font=f2, fill=SILVER + (255,))
                y += 44
                line = wd
            else:
                line = test
        d.text((x, y), line + (" |" if cursor else ""), font=f2, fill=SILVER + (255,))
        d.text((pad + w - 250, pad + h - 44), "one token at a time", font=MONO_S, fill=STEEL + (255,))
        return card
    return cached(("chat", text_full, n, cursor, w, h, who), build)


def decision_row(step=-1, w=980, h=150, compact=False):
    """ACTION / YES · NO / SCORE tiles. step lights 0..2, 3 = all lit."""
    def build():
        labels = ["ACTION", "YES / NO", "SCORE"]
        subs = ["pick a choice", "binary answer", "rate the data"]
        cols = [ORANGE, NEON, PINK]
        n = 3
        gap = 18
        tw = (w - gap * 2) // n
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for i, (lab, sub) in enumerate(zip(labels, subs)):
            x = i * (tw + gap)
            on = (step == 3) or (i <= step)
            active = (i == step) or step == 3
            fill = (cols[i] if active else (CHAR if on else GRAPHITE)) + (255,)
            fg = INK + (255,) if active else SILVER + (255,)
            d.rounded_rectangle([x, 0, x + tw, h - 1], 22, fill=fill, outline=cols[i] + (140,), width=2)
            if compact:
                d.text((x + tw / 2, h / 2), lab, font=F(AR, 34), fill=fg, anchor="mm")
            else:
                d.text((x + tw / 2, 46), lab, font=F(AR, 40), fill=fg, anchor="mm")
                d.text((x + tw / 2, 106), sub, font=F(AR, 22), fill=fg, anchor="mm")
            d.text((x + 18, 10), f"{i + 1}", font=F(AR, 22), fill=fg)
        return img
    return cached(("drow", step, w, h, compact), build)


def action_card(p, w=680, h=300):
    """A list of allowed actions; a cursor sweeps then locks on one."""
    opts = ["jump", "roll", "swipe left", "swipe right"]
    k = int(clamp01(p) * 9)
    sel = (k % 4) if k < 8 else 0
    locked = k >= 8

    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + 24, pad + 16), "allowed_actions[]", font=MONO, fill=STEEL + (255,))
        y = pad + 60
        for i, o in enumerate(opts):
            on = i == sel
            fill = (ORANGE if (on and locked) else (CHAR if on else GRAPHITE)) + (255,)
            fg = INK + (255,) if (on and locked) else SILVER + (255,)
            d.rounded_rectangle([pad + 20, y, pad + w - 20, y + 48], 12, fill=fill)
            d.text((pad + 40, y + 10), ("> " if on else "  ") + o, font=F(AR, 28), fill=fg)
            if on and locked:
                d.text((pad + w - 150, y + 10), "p=0.94", font=MONO, fill=INK + (255,))
            y += 56
        return card
    return cached(("actcard", sel, locked, w, h), build)


def yesno_card(p, w=680, h=300):
    k = int(clamp01(p) * 8)
    yes_lit = k >= 3

    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + 24, pad + 16), "is this frame safe to jump?", font=F(AR, 28), fill=SILVER + (255,))
        bw = (w - 80) // 2
        for i, (lab, col) in enumerate([("YES", NEON), ("NO", RED)]):
            x = pad + 24 + i * (bw + 32)
            lit = (i == 0 and yes_lit) or (i == 1 and not yes_lit and k >= 1 and k < 3)
            fill = col + (255,) if lit else CHAR + (255,)
            fg = INK + (255,) if lit else SILVER + (255,)
            d.rounded_rectangle([x, pad + 70, x + bw, pad + 200], 22, fill=fill, outline=col + (160,), width=3)
            d.text((x + bw / 2, pad + 135), lab, font=F(AR, 72), fill=fg, anchor="mm")
        if yes_lit:
            d.text((pad + 24, pad + 220), "confidence 0.97   latency 70 ms", font=MONO, fill=NEON + (255,))
        return card
    return cached(("yncard", yes_lit, k, w, h), build)


def score_card(p, w=680, h=300):
    v = int(94 * (1 - (1 - clamp01(p)) ** 3))

    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + 24, pad + 16), "score(data)", font=MONO, fill=STEEL + (255,))
        d.text((pad + 24, pad + 50), f"{v}", font=F(AR, 120), fill=PINK + (255,))
        d.text((pad + 190, pad + 118), "/ 100", font=F(AR, 40), fill=SILVER + (255,))
        # bar
        d.rounded_rectangle([pad + 24, pad + 210, pad + w - 24, pad + 240], 12, fill=CHAR + (255,))
        d.rounded_rectangle([pad + 24, pad + 210, pad + 24 + int((w - 48) * v / 100), pad + 240], 12, fill=PINK + (255,))
        d.text((pad + w - 250, pad + 60), "typed output", font=MONO_S, fill=STEEL + (255,))
        d.text((pad + w - 250, pad + 86), "no text, no tokens", font=MONO_S, fill=STEEL + (255,))
        return card
    return cached(("scorecard", v, w, h), build)


def strike_row(p, w=980, h=190):
    """LLM logos with a red strike sweeping across."""
    k = int(clamp01(p) * 12)

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        slugs = ["openai", "gemini", "claude", "deepseek", "xai"]
        n = len(slugs)
        step = w // n
        for i, s in enumerate(slugs):
            b = logo_badge(s, 150, fill=GRAPHITE + (255,), punch=(s not in ("claude",)))
            if b is None:
                continue
            img.alpha_composite(b, (i * step + (step - b.width) // 2, (h - b.height) // 2))
        d = ImageDraw.Draw(img)
        x1 = int(w * k / 12)
        if x1 > 0:
            d.line([(0, h - 30), (x1, 30)], fill=RED + (255,), width=16)
        return img
    return cached(("strike", k, w, h), build)


def hud_card(lt, w=500, h=380):
    """Three questions HUD typed in as Kevin says them (abs times)."""
    lines = [
        (63.6, "Q1  complete the game?", "-> ACTION"),
        (65.7, "Q2  what do I click?", "-> CHOICE"),
        (66.9, "Q3  how good was that?", "-> SCORE 0.93"),
    ]
    shown = []
    for t0, q, a in lines:
        if lt >= t0:
            pq = clamp01((lt - t0) / 0.5)
            shown.append((typewriter(q, pq, cursor=False), a if pq >= 1 else ""))
    k = tuple((a, b) for a, b in shown)

    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad + 14, pad + 12, pad + w - 14, pad + 56], 12, fill=INK + (255,))
        d.text((pad + 30, pad + 20), "JEV loop", font=F(AR, 24), fill=NEON + (255,))
        d.text((pad + w - 170, pad + 22), "3 questions", font=MONO_S, fill=STEEL + (255,))
        y = pad + 80
        for q, a in shown:
            d.text((pad + 24, y), q, font=MONO, fill=SILVER + (255,))
            if a:
                d.text((pad + 24, y + 30), a, font=MONO, fill=ORANGE + (255,))
            y += 84
        if not shown:
            d.text((pad + 24, y), "watching frame...", font=MONO, fill=STEEL + (255,))
        return card
    return cached(("hud", k, w, h), build)


def rl_card(p, w=520, h=300):
    """Reinforcement-learning loop card: spinning loop arrows + attempt counter."""
    ang = (p * 720) % 360
    att = int(1 + 9999 * (1 - (1 - clamp01(p)) ** 3))

    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + 24, pad + 16), "REINFORCEMENT", font=F(AR, 34), fill=NEON + (255,))
        d.text((pad + 24, pad + 52), "LEARNING", font=F(AR, 34), fill=NEON + (255,))
        la = loop_arrows(ang)
        la = la.resize((150, 150), Image.LANCZOS)
        card.alpha_composite(la, (pad + w - 190, pad + 20))
        d.text((pad + 24, pad + 120), "attempt", font=MONO_S, fill=STEEL + (255,))
        d.text((pad + 24, pad + 146), f"{att:,}", font=F(AR, 64), fill=SILVER + (255,))
        d.rounded_rectangle([pad + 24, pad + 236, pad + w - 24, pad + 256], 8, fill=CHAR + (255,))
        d.rounded_rectangle([pad + 24, pad + 236, pad + 24 + int((w - 48) * clamp01(p)), pad + 256], 8, fill=NEON + (255,))
        return card
    return cached(("rlcard", int(ang / 6), att // 37, w, h), build)


def jev_hero(size=480, t=0.0):
    """Giant JEV mark: pink round TypeSafe logo + JEV wordmark ring."""
    def build():
        b = logo_badge("jev", size, fill=INK + (255,), punch=False)
        return b
    return cached(("jevhero", size), build)


def jev_wordmark(w=960, h=150):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w, h], 30, fill=PINK + (255,), outline=SILVER + (80,), width=2)
        d.text((w / 2 - 10, h / 2 - 8), "JEV", font=F(AR, 110), fill=INK + (255,), anchor="mm")
        d.text((w - 210, h / 2), "by TypeSafe AI", font=F(AR, 26), fill=INK + (220,), anchor="mm")
        return img
    return cached(("jevword", w, h), build)


def place(frame, img, cx, cy, lt, t0, dur=0.3, frm="up", tilt=0.0, idle=5, scale_pop=False, exit_at=None):
    if img is None:
        return
    p = ease((lt - t0) / dur)
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
        pop = outp((lt - t0) / dur)
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


HOLD = skill_chip("JEV")
TOPIC_AI = ["openai", "anthropic", "gemini", "deepseek", "xai", "nvidia", "github"]
TOPIC_JEV = ["jev", "typesafe", "dcvc", "openai", "anthropic", "subway-surfers", "gemini"]

# absolute beat times (words.json, max 0.1s lead)
T_NEW = tabs("new", 1.5)          # 1.94
T_200A = tabs("200", 3.0)         # 3.86
T_200B = tabs("200", 5.0)         # 6.04
T_CLAUDE = tabs("Claude", 7.0)    # 8.0
T_JEV = tabs("Jev", 9.0)          # 9.8
T_WILD = tabs("wild", 11.0)       # 12.3
T_EXPLAIN = tabs("explain", 15.0)  # 15.5
T_AI2 = tabs("AI", 16.5)          # 16.9
T_BUILDS = tabs("builds", 18.0)   # 18.5
T_WORD1 = tabs("word", 19.5)      # 20.1
T_AGENT = tabs("agent", 22.0)     # 22.5
T_RESP2 = tabs("response", 24.0)  # 24.7
T_JEV2 = tabs("Jev", 26.0)        # 26.4
T_THREW = tabs("threw", 27.0)     # 27.5
T_WINDOW = tabs("window", 28.0)   # 28.2
T_DESIGN = tabs("designed", 29.5)  # 30.2
T_THREE1 = tabs("three", 32.0)    # 32.7
T_ACTION = tabs("action", 35.0)   # 35.5
T_YES = tabs("yes", 37.0)         # 37.8
T_SCORE = tabs("score", 39.5)     # 39.9
T_DATA = tabs("data", 41.0)       # 41.2
T_JEV3 = tabs("Jev", 42.5)        # 43.0
T_SHOCK = tabs("shocking", 43.0)  # 43.9
T_BEAUT = tabs("beautiful", 44.0)  # 44.7
T_THREE2 = tabs("three", 46.5)    # 47.2
T_LARGE = tabs("large", 48.5)     # 49.1
T_EXAMPLES = tabs("examples", 50.0)  # 50.5
T_JEV4 = tabs("Jev", 52.0)        # 52.3
T_CRAZY = tabs("crazy", 53.0)     # 53.7
T_VIDEO = tabs("video", 56.0)     # 56.6
T_GAMES = tabs("games", 56.5)     # 57.0
T_SUBWAY = tabs("subway", 58.0)   # 58.8
T_THREE3 = tabs("three", 60.5)    # 61.2
T_RL = tabs("reinforcement", 68.0)  # 68.4
T_PERF = tabs("perfects", 69.0)   # 69.7
T_JEV5 = tabs("Jev", 71.0)        # 71.4
T_COMMENT = tabs("comment", 73.0)  # 73.4


def scene(layer, name, lt, t, a):
    gsl = int(30 * math.sin(lt * 0.6))
    r = lambda T: max(0.0, T - 0.08 - a)  # noqa: E731  relative beat with 0.08 lead

    if name == "hook":
        draw_code_rain(layer, lt, n=16, col=ORANGE)
        layer.alpha_composite(ghost_img("NEW MODEL", 84), (-120 + gsl, 0))
        ticker(layer, "  NEW AI MODEL  ·  200X FASTER  ·  200X CHEAPER  ·  NOT AN LLM  ·  ",
               600, lt, speed=170, fill=ORANGE + (90,))
        t_new, t_a, t_b, t_cl = r(T_NEW), r(T_200A), r(T_200B), r(T_CLAUDE)
        # topic lane: the AI stack, cold-open, exits before the pricing shot
        if lt < t_cl - 0.05:
            guarded_conveyor(layer, 440 + PACK_DY, max(0, lt + 0.3),
                             topic_marks(TOPIC_AI, size=100), conveyor_marks,
                             name="topic-lane", speed=190, gap=22)
        if lt < t_new:
            # mystery cold open: packed from frame 0
            place(layer, mystery_card(lt), 540, 240, lt, -0.4, dur=0.01)
            place(layer, chip("I can't believe I'm saying this", STEEL), 540, 30, lt, -0.4, dur=0.01)
        elif lt < t_a - 0.06:
            place(layer, big_text_card("NEW AI MODEL JUST DROPPED", ORANGE, fsz=48, w=960, h=110),
                  540, 36, lt, t_new, scale_pop=True)
            place(layer, mystery_card(lt), 540, 260, lt, -0.4, dur=0.01, exit_at=t_a - 0.06)
            light_hit(layer, 540, 36 + PACK_DY, lt, t_new, ORANGE)
        elif lt < t_b - 0.06:
            place(layer, big_text_card("NEW AI MODEL JUST DROPPED", ORANGE, fsz=48, w=960, h=110),
                  540, 36, lt, t_new, scale_pop=True)
            bt = NUM.get(3.86)
            if bt:
                place(layer, counter_card(bt, (lt - t_a) / 0.6, h=380, label="times FASTER", fill=GRAPHITE, accent=NEON),
                      540, 250, lt, t_a, dur=0.2, scale_pop=True, exit_at=t_b - 0.06)
            light_hit(layer, 540, 250 + PACK_DY, lt, t_a, NEON)
        elif lt < t_cl - 0.06:
            place(layer, big_text_card("200X FASTER  ·  200X CHEAPER", NEON, fsz=46, w=960, h=110),
                  540, 36, lt, t_b, scale_pop=True)
            bt = NUM.get(6.04)
            if bt:
                place(layer, counter_card(bt, (lt - t_b) / 0.6, h=380, label="times CHEAPER", fill=GRAPHITE, accent=ORANGE),
                      540, 250, lt, t_b, dur=0.2, scale_pop=True, exit_at=t_cl - 0.06)
            light_hit(layer, 540, 250 + PACK_DY, lt, t_b, ORANGE)
        else:
            place(layer, big_text_card("CHEAPER THAN CLAUDE FABLE 5.1", ORANGE, fsz=44, w=960, h=104),
                  540, 32, lt, t_cl, scale_pop=True)
            place(layer, product_shot("pricing", w=760, h=380, label="price per million tokens  ·  Jev $0.042 vs Fable $10", accent=PINK),
                  400, 300, lt, t_cl, dur=0.25, frm="left")
            light_hit(layer, 400, 300 + PACK_DY, lt, t_cl, ORANGE)
            ix = 930 + 8 * math.sin(lt * 2.0)
            iy = 300 + PACK_DY + 6 * math.sin(lt * 2.4)
            bloom_orb(layer, ix, iy, 110, ORANGE, a=60)
            rim_pulse(layer, ix, iy, 130, lt, ORANGE)
            place_claude_invader(layer, ix, iy, lt, size=200, look_at=(400, 300 + PACK_DY))
            place_claude_sphinx(layer, 930, 90 + PACK_DY, lt, size=120)

    elif name == "reveal":
        draw_code_rain(layer, lt, n=14, col=PINK)
        layer.alpha_composite(ghost_img("JEV", 120), (-60 + gsl, 0))
        ticker(layer, "  JEV  ·  TYPESAFE AI  ·  SYSTEM ONE MODEL  ·  $40M SEED  ·  DIOGO ALMEIDA  ·  ",
               600, lt, speed=170, fill=PINK + (100,))
        t_jev, t_wild, t_exp = r(T_JEV), r(T_WILD), r(T_EXPLAIN)
        if lt < t_wild - 0.06:
            # billboard: giant JEV mark + Diogo spotlight + wordmark
            place(layer, jev_wordmark(960, 140), 540, 30, lt, -0.35, dur=0.01, scale_pop=True)
            place(layer, jev_hero(440), 290, 290, lt, -0.3, dur=0.01, scale_pop=True, frm="left")
            figure_spotlight(layer, "diogo-almeida", 800, 270, lt, t_jev + 0.05, place, size=440, ring=PINK,
                             exit_at=t_wild - 0.06)
            light_rays(layer, 290, 290 + PACK_DY, lt, PINK)
            light_hit(layer, 540, 30 + PACK_DY, lt, t_jev, PINK)
        elif lt < t_exp - 0.06:
            place(layer, big_text_card("ABSOLUTELY WILD", RED, fsz=56, w=960, h=130),
                  540, 36, lt, t_wild, scale_pop=True)
            place(layer, jev_hero(300), 240, 330, lt, -0.3, dur=0.01, exit_at=t_exp - 0.06)
            front_gif(gif_card("mind-blown", max(0, lt - t_wild), w=460, frame="round"),
                      760, 330, lt, t_wild, frm="right", tilt=4, exit_at=t_exp - 0.06)
            light_hit(layer, 760, 330 + PACK_DY, lt, t_wild, RED)
            place(layer, chip("not like anything we've seen", RED), 540, 500, lt, t_wild + 0.9, frm="down",
                  exit_at=t_exp - 0.06)
        else:
            place(layer, big_text_card("HOW JEV ACTUALLY WORKS", PINK, fsz=48, w=960, h=110),
                  540, 32, lt, t_exp, scale_pop=True)
            place(layer, chip("explaining it right now", NEON), 300, 200, lt, t_exp + 0.1, frm="left")
            place(layer, jev_hero(260), 820, 330, lt, t_exp, frm="right", scale_pop=True)
            place(layer, decision_row(-1, w=640, h=120, compact=True), 380, 340, lt, t_exp + 0.15, frm="up")
            light_hit(layer, 540, 32 + PACK_DY, lt, t_exp, PINK)

    elif name == "onebyone":
        draw_code_rain(layer, lt, n=12, col=ORANGE)
        ticker(layer, "  EVERY LLM  ·  ONE TOKEN AT A TIME  ·  AUTOREGRESSIVE  ·  SLOW  ·  ",
               600, lt, speed=165, fill=ORANGE + (90,))
        t_ai, t_b, t_w, t_ag, t_r2 = r(T_AI2), r(T_BUILDS), r(T_WORD1), r(T_AGENT), r(T_RESP2)
        # HF overlay carries the kinetic "ONE WORD AT A TIME" headline at slot top (y 30..130)
        if lt < t_b - 0.06:
            place(layer, big_text_card("EVERY AI UNTIL NOW", ORANGE, fsz=46, w=960, h=104),
                  540, 32, lt, -0.35, dur=0.01, scale_pop=True, exit_at=t_b - 0.06)
            figure_row(layer, ["sam-altman", "dario-amodei"], 540, 230, lt, t_ai, place, size=340, gap=40,
                       ring=ORANGE, names=True, exit_at=t_b - 0.06)
            light_hit(layer, 540, 230 + PACK_DY, lt, t_ai, ORANGE)
        else:
            msg1 = "The best way to grow on Instagram is to post consistently and reply to every comment"
            msg2 = "Sure! Here are three ideas for your next reel. First, hook them in the first second"
            if lt < t_r2 - 0.05:
                p = (lt - t_b) / 5.2
                place(layer, chat_card(msg1, p, w=960, h=290), 540, 280, lt, t_b, dur=0.22, scale_pop=True)
            else:
                p = (lt - t_r2) / 1.6
                place(layer, chat_card(msg2, p, w=960, h=290, who="agent #2"), 540, 280, lt, t_r2, dur=0.22, frm="down")
            light_hit(layer, 540, 280 + PACK_DY, lt, t_w, ORANGE)
            # LLM marks under the card
            for i, s in enumerate(["openai", "gemini", "claude", "deepseek"]):
                place(layer, logo_badge(s, 120, fill=GRAPHITE + (255,), punch=(s != "claude")), 300 + i * 160, 480, lt,
                      t_b + 0.1 + i * 0.08, frm="up", tilt=(-4, 3, -3, 4)[i])
            if lt >= t_ag:
                place(layer, chip("your agent, word by word", ORANGE), 860, 470, lt, t_ag, frm="right")

    elif name == "toss":
        draw_code_rain(layer, lt, n=12, col=RED)
        layer.alpha_composite(ghost_img("OUT", 110), (-80 + gsl, 0))
        ticker(layer, "  JEV THREW IT OUT THE WINDOW  ·  NO TOKENS  ·  NO TEXT  ·  ",
               600, lt, speed=170, fill=RED + (100,))
        t_j, t_th, t_win, t_des = r(T_JEV2), r(T_THREW), r(T_WINDOW), r(T_DESIGN)
        if lt < t_win - 0.06:
            place(layer, big_text_card("JEV THREW THAT OUT", RED, fsz=50, w=960, h=120),
                  540, 34, lt, -0.35, dur=0.01, scale_pop=True, exit_at=t_win - 0.06)
        else:
            place(layer, big_text_card("OUT THE WINDOW", RED, fsz=60, w=960, h=130),
                  540, 36, lt, t_win, scale_pop=True)
            light_hit(layer, 540, 36 + PACK_DY, lt, t_win, RED)
        place(layer, jev_hero(340), 270, 320, lt, -0.3, dur=0.01, frm="left", scale_pop=True)
        front_gif(gif_card("toss-it", max(0, lt - t_th), w=440, frame="round"),
                  790, 320, lt, t_th, frm="right", tilt=-5)
        light_hit(layer, 790, 320 + PACK_DY, lt, t_th, RED)
        if lt >= t_des:
            place(layer, chip("designed completely differently", NEON), 540, 500, lt, t_des, frm="down")

    elif name == "threeways":
        draw_code_rain(layer, lt, n=12, col=NEON)
        ticker(layer, "  ACTION  ·  YES / NO  ·  SCORE  ·  TYPED DECISIONS  ·  70 MS  ·  ",
               600, lt, speed=170, fill=NEON + (90,))
        t_3, t_act, t_yes, t_sc, t_data = r(T_THREE1), r(T_ACTION), r(T_YES), r(T_SCORE), r(T_DATA)
        step = -1
        if lt >= t_act:
            step = 0
        if lt >= t_yes:
            step = 1
        if lt >= t_sc:
            step = 2
        if lt < t_3 - 0.05:
            place(layer, big_text_card("JEV CAN ONLY RESPOND", NEON, fsz=48, w=960, h=110),
                  540, 32, lt, -0.35, dur=0.01, scale_pop=True, exit_at=t_3 - 0.05)
            place(layer, jev_hero(300), 300, 300, lt, -0.3, dur=0.01, exit_at=t_3 - 0.05)
            place(layer, chip("in one of ...", STEEL), 760, 300, lt, 0.3, frm="right", exit_at=t_3 - 0.05)
        elif lt < t_act - 0.06:
            bt = NUM.get(32.68)
            if bt:
                place(layer, counter_card(bt, (lt - t_3) / 0.5, h=440, label="WAYS TO RESPOND", fill=GRAPHITE, accent=NEON),
                      540, 250, lt, t_3, dur=0.2, scale_pop=True, exit_at=t_act - 0.06)
            light_hit(layer, 540, 250 + PACK_DY, lt, t_3, NEON)
        else:
            place(layer, decision_row(step, w=980, h=150), 540, 40, lt, t_act, dur=0.25, scale_pop=True)
            light_hit(layer, 540, 40 + PACK_DY, lt, t_act, ORANGE)
            light_hit(layer, 540, 40 + PACK_DY, lt, t_yes, NEON)
            light_hit(layer, 540, 40 + PACK_DY, lt, t_sc, PINK)
            if step == 0:
                place(layer, action_card((lt - t_act) / 1.9), 420, 330, lt, t_act, dur=0.25, frm="left",
                      exit_at=t_yes - 0.06)
            elif step == 1:
                place(layer, yesno_card((lt - t_yes) / 1.4), 420, 330, lt, t_yes, dur=0.25, frm="down",
                      exit_at=t_sc - 0.06)
            else:
                place(layer, score_card((lt - t_sc) / 1.3), 420, 330, lt, t_sc, dur=0.25, frm="right")
                if lt >= t_data:
                    place(layer, chip("on data you fed it", PINK), 420, 500, lt, t_data, frm="down")
            place(layer, jev_hero(230), 900, 330, lt, t_act + 0.1, frm="right")

    elif name == "shock":
        draw_code_rain(layer, lt, n=12, col=PINK)
        layer.alpha_composite(ghost_img("NOT AN LLM", 78), (-100 + gsl, 0))
        ticker(layer, "  SO SHOCKING  ·  SO BEAUTIFUL  ·  NOT A LARGE LANGUAGE MODEL  ·  ",
               600, lt, speed=170, fill=PINK + (100,))
        t_j, t_sh, t_be, t_3, t_lg = r(T_JEV3), r(T_SHOCK), r(T_BEAUT), r(T_THREE2), r(T_LARGE)
        if lt < t_sh - 0.06:
            place(layer, big_text_card("WHAT MAKES JEV", PINK, fsz=48, w=960, h=110),
                  540, 32, lt, -0.35, dur=0.01, scale_pop=True, exit_at=t_sh - 0.06)
            place(layer, jev_hero(320), 540, 300, lt, -0.3, dur=0.01, scale_pop=True, exit_at=t_sh - 0.06)
        elif lt < t_lg - 0.06:
            place(layer, big_text_card("SO SHOCKING  ·  SO BEAUTIFUL", RED, fsz=44, w=960, h=104),
                  540, 32, lt, t_sh, scale_pop=True, exit_at=t_lg - 0.06)
            light_hit(layer, 540, 32 + PACK_DY, lt, t_sh, RED)
            if lt < t_be - 0.06:
                front_gif(gif_card("shocked", max(0, lt - t_sh), w=400, frame="round"),
                          540, 320, lt, t_sh, frm="down", tilt=-4, exit_at=t_be - 0.06)
            else:
                place(layer, product_shot("chart", w=700, h=330, label="accuracy vs cost per workflow  ·  Jev is the star", accent=PINK),
                      400, 300, lt, t_be, dur=0.25, frm="left", exit_at=t_lg - 0.06)
                light_hit(layer, 400, 300 + PACK_DY, lt, t_be, PINK)
                place(layer, jev_hero(220), 920, 240, lt, t_be + 0.1, frm="right", exit_at=t_lg - 0.06)
                if lt >= t_3:
                    place(layer, decision_row(3, w=980, h=96, compact=True), 540, 510, lt, t_3, dur=0.22, frm="up",
                          exit_at=t_lg - 0.06)
        else:
            place(layer, big_text_card("NOT AN LLM", RED, fsz=76, w=960, h=150), 540, 46, lt, t_lg, scale_pop=True)
            light_hit(layer, 540, 46 + PACK_DY, lt, t_lg, RED)
            place(layer, strike_row((lt - t_lg - 0.15) / 0.6, w=980, h=190), 540, 330, lt, t_lg + 0.05, dur=0.22, frm="up")
            place(layer, chip("no tokens  ·  no text  ·  typed decisions", PINK), 540, 480, lt, t_lg + 0.5, frm="down")

    elif name == "games":
        draw_code_rain(layer, lt, n=12, col=ORANGE)
        layer.alpha_composite(ghost_img("PLAY", 110), (-60 + gsl, 0))
        ticker(layer, "  JEV IN THE WILD  ·  PLAYS ENTIRE VIDEO GAMES  ·  REAL TIME LOOPS  ·  ",
               600, lt, speed=170, fill=ORANGE + (90,))
        t_ex, t_j, t_cr, t_vid, t_g = r(T_EXAMPLES), r(T_JEV4), r(T_CRAZY), r(T_VIDEO), r(T_GAMES)
        if lt < t_vid - 0.06:
            guarded_conveyor(layer, 495 + PACK_DY, max(0, lt + 0.3),
                             topic_marks(TOPIC_JEV, size=100, punch=False), conveyor_marks,
                             name="topic-lane", speed=180, gap=22)
            place(layer, big_text_card("BEST EXAMPLES RIGHT NOW", ORANGE, fsz=46, w=960, h=104),
                  540, 32, lt, -0.35, dur=0.01, scale_pop=True, exit_at=t_vid - 0.06)
            place(layer, jev_hero(280), 280, 270, lt, -0.3, dur=0.01, exit_at=t_vid - 0.06)
            place(layer, chip("people using JEV today", NEON), 280, 395, lt, 0.2, exit_at=t_vid - 0.06)
            if lt >= t_cr:
                front_gif(gif_card("incredibles", max(0, lt - t_cr), w=460, frame="round"),
                          770, 290, lt, t_cr, frm="right", tilt=4, exit_at=t_vid - 0.06)
                light_hit(layer, 770, 290 + PACK_DY, lt, t_cr, ORANGE)
            else:
                place(layer, stat_chip("70 ms", "per decision", accent=NEON, w=420, h=150), 770, 240, lt, 0.3,
                      frm="right", exit_at=t_cr - 0.06)
                place(layer, stat_chip("$0", "per output token", accent=ORANGE, w=420, h=150), 770, 400, lt, 0.5,
                      frm="right", exit_at=t_cr - 0.06)
        else:
            place(layer, big_text_card("PLAYS ENTIRE VIDEO GAMES", ORANGE, fsz=48, w=960, h=110),
                  540, 32, lt, t_g, scale_pop=True)
            light_hit(layer, 540, 32 + PACK_DY, lt, t_g, ORANGE)
            front_gif(gif_card("controller", max(0, lt - t_vid), w=600, frame="bezel", label="jev.play(game)"),
                      540, 330, lt, t_vid, frm="up", tilt=0)
            light_hit(layer, 540, 330 + PACK_DY, lt, t_vid, ORANGE)

    elif name == "subway":
        draw_code_rain(layer, lt, n=10, col=NEON)
        ticker(layer, "  SUBWAY SURFERS  ·  3 QUESTIONS  ·  REINFORCEMENT LEARNING  ·  UNTIL PERFECT  ·  ",
               600, lt, speed=170, fill=NEON + (90,))
        t_sub, t_3, t_rl, t_pf = r(T_SUBWAY), r(T_THREE3), r(T_RL), r(T_PERF)
        if lt < t_3 - 0.06:
            place(layer, big_text_card("JEV PLAYING SUBWAY SURFERS", NEON, fsz=46, w=960, h=104),
                  540, 20, lt, -0.35, dur=0.01, scale_pop=True, exit_at=t_3 - 0.06)
            front_gif(gif_card("subway-surfers", max(0, lt - t_sub), w=980, frame="round"),
                      540, 330, lt, t_sub, dur=0.25, frm="up", exit_at=t_3 - 0.06)
            light_hit(layer, 540, 330 + PACK_DY, lt, t_sub, NEON)
            if lt < t_sub:
                place(layer, jev_hero(300), 540, 320, lt, -0.3, dur=0.01, exit_at=t_sub - 0.04)
        elif lt < t_rl - 0.06:
            place(layer, big_text_card("JUST 3 QUESTIONS, EVERY FRAME", NEON, fsz=44, w=960, h=104),
                  540, 20, lt, t_3, scale_pop=True, exit_at=t_rl - 0.06)
            light_hit(layer, 540, 20 + PACK_DY, lt, t_3, NEON)
            front_gif(gif_card("subway-run", max(0, lt - t_3), w=520, frame="round"),
                      300, 300, lt, t_3, frm="left", tilt=-3, exit_at=t_rl - 0.06)
            place(layer, hud_card(t, w=500, h=380), 800, 300, lt, t_3 + 0.1, frm="right", exit_at=t_rl - 0.06)
        else:
            # HF lower third (slot y>=640) is live: keep PIL pieces above cy≈330
            front_gif(gif_card("subway-run", max(0, lt - t_3), w=460, frame="round", speed=1.6),
                      280, 220, lt, -0.3, dur=0.01, frm="left", tilt=-3)
            place(layer, rl_card((lt - t_rl) / 1.5, w=540, h=300), 790, 220, lt, t_rl, dur=0.25, frm="right",
                  scale_pop=True)
            light_hit(layer, 790, 220 + PACK_DY, lt, t_rl, NEON)
            if lt >= t_pf:
                place(layer, chip("until it perfects it", NEON), 790, 400, lt, t_pf, frm="down")

    else:  # cta
        draw_code_rain(layer, lt, n=10, col=NEON)
        layer.alpha_composite(ghost_img("JEV", 120), (-60 + gsl, 0))
        ticker(layer, "  COMMENT JEV  ·  FULL RELEASE ANNOUNCEMENTS  ·  I'LL SEND IT OVER  ·  ",
               600, lt, speed=165, fill=NEON + (90,))
        t_j, t_com = r(T_JEV5), r(T_COMMENT)
        if lt < t_com - 0.06:
            place(layer, big_text_card("FULL JEV RELEASE NOTES", PINK, fsz=48, w=960, h=110),
                  540, 32, lt, -0.35, dur=0.01, scale_pop=True, exit_at=t_com - 0.06)
            place(layer, jev_hero(340), 300, 310, lt, -0.3, dur=0.01, exit_at=t_com - 0.06)
            place(layer, product_shot("typesafe-og", w=440, h=230, label="typesafe.ai", accent=PINK), 790, 300, lt, 0.15,
                  frm="right", exit_at=t_com - 0.06)
        else:
            place(layer, big_text_card("COMMENT  JEV", NEON, fsz=64, w=960, h=140),
                  540, 40, lt, t_com, scale_pop=True)
            light_hit(layer, 540, 40 + PACK_DY, lt, t_com, NEON)
            light_rays(layer, 540, 40 + PACK_DY, lt, NEON)
            place(layer, chip("I'll send it over", ORANGE), 260, 200, lt, t_com + 0.3, frm="left")
            place(layer, jev_hero(260), 300, 400, lt, t_com + 0.1, frm="left", scale_pop=True)
            ix = 640 + 10 * math.sin(lt * 1.8)
            iy = 400 + PACK_DY + 6 * math.sin(lt * 2.1)
            bloom_orb(layer, ix, iy, 100, NEON, a=55)
            place_claude_invader(
                layer, ix, iy, lt, size=220,
                look_at=(540, 40 + PACK_DY),
                grab="right", grab_at=(ix - 80, iy - 30), grab_t=min(1.0, max(0.0, (lt - t_com) / 0.5)),
                hold=HOLD if lt > t_com + 0.3 else None,
            )
            front_gif(gif_card("mind-blown", max(0, lt - t_com), w=280, frame="round"),
                      900, 380, lt, t_com + 0.2, frm="right", tilt=4)


if not os.path.isfile("renders/talking_band45.mp4"):
    raise SystemExit("missing renders/talking_band45.mp4")

band_cap = cv2.VideoCapture("renders/talking_band45.mp4")
band_mask = Image.new("L", (BAND_W, BAND_H), 0)
ImageDraw.Draw(band_mask).rounded_rectangle([0, 0, BAND_W - 1, BAND_H - 1], 60, fill=255)
_band_cache = {}


def band_at(n):
    if n in _band_cache:
        return _band_cache[n]
    band_cap.set(cv2.CAP_PROP_POS_FRAMES, n)
    ok, fr = band_cap.read()
    if not ok:
        return None
    img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    img.putalpha(band_mask)
    if len(_band_cache) < 8:
        _band_cache[n] = img
    return img


# one hero punch per section, >=8s apart (Kevin 2026-09-12: punches are rare)
PUNCH_T = [T_JEV, T_WINDOW, T_SHOCK, T_GAMES, T_RL]
BEATS = number_beats(words)
NUM = {round(b["t"], 2): b for b in BEATS}
HANDLED = {3.86, 6.04, 32.68, 47.22, 61.22}
CUT_T = [a for _, a, _ in SECT[1:]]
HIT_T = CUT_T + [T_200A, T_JEV, T_WINDOW, T_SHOCK, T_LARGE, T_COMMENT]
WHIP_T, HF_T = CUT_T[::2], CUT_T[1::2]
for _b in BEATS:
    print(f"number beat {_b['t']:.2f}s {_b['raw']!r}")
print("punches", [round(p, 2) for p in PUNCH_T])

os.makedirs("frames/out5", exist_ok=True)
PREVIEW = os.environ.get("PREVIEW")
if PREVIEW:
    times = [0.00, 1.20, 2.40, 4.40, 6.60, 8.60,
             10.30, 11.50, 13.00, 15.90,
             17.40, 19.40, 21.40, 23.20, 25.20,
             26.90, 28.60, 30.40,
             31.40, 33.20, 36.20, 38.60, 40.80,
             42.90, 44.30, 46.00, 48.00, 49.60,
             51.20, 54.40, 57.10,
             58.00, 59.60, 62.00, 66.40, 69.00, 70.00,
             71.60, 73.90]
    todo = [int(round(tt * FPS)) for tt in times]
else:
    todo = list(range(N))

last_band = None
prev_layer = None
prev_name = None

for i, n in enumerate(todo):
    t = n / FPS
    name, a, b = next(s for s in SECT if s[1] <= t < s[2] or s is SECT[-1])
    lt, sd = t - a, max(0.01, b - a)
    z = 1.0 + 0.05 * (lt / sd)
    bg = BGS[name]
    bw, bh = int((W + 160) / z), int((H + 160) / z)
    ox, oy = (bg.width - bw) // 2, (bg.height - bh) // 2
    frame = bg.crop((ox, oy, ox + bw, oy + bh)).resize((W, H), Image.BICUBIC).convert("RGBA")
    layer = Image.new("RGBA", (W, AH), (0, 0, 0, 0))
    lanes.reset()
    GIF_Q.clear()

    scanlines(layer, t)
    hud_scan(layer, t, SECT_ACCENT[name])
    neon_grid(layer, t, STEEL)
    scene(layer, name, lt, t, a)
    auto_counters(layer, BEATS, t, a, place, handled=HANDLED)
    flush_gifs(layer)
    slot_vignette(layer, a=22)
    speed_streaks(layer, t, PUNCH_T, NEON)
    hf = hf_layer_frame(n)
    if hf is not None:
        layer.alpha_composite(hf)

    if name != prev_name:
        prev_layer = None if name == "hook" else prev_layer
        prev_name = name
    if lt < 0.16 and a in WHIP_T and prev_layer is not None:
        layer = whip_wipe(prev_layer, layer, lt / 0.16, direction=whip_dir(name))
    else:
        prev_layer = layer.copy()

    layer = punch_zoom(layer, punch_scale(t, PUNCH_T, amt=0.045))
    sx, sy = shake_offset(t, HIT_T, amp=14)
    frame.alpha_composite(layer, (sx, LAYER_Y + sy))
    acc = SECT_ACCENT[name]
    hd = ImageDraw.Draw(frame)
    hd.rectangle([48, BAND_Y - 8, W - 48, BAND_Y - 4], fill=acc + (200,))
    hd.rectangle([48, LAYER_Y + 2, W - 48, LAYER_Y + 4], fill=SILVER + (70,))
    hyperframe(frame, t, HF_T, FPS, region=(0, LAYER_Y, W, AH))

    if PREVIEW:
        bf = band_at(n)
    else:
        ok, fr = band_cap.read()
        if ok:
            bf = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGBA")
            bf.putalpha(band_mask)
        else:
            bf = None
    if bf is not None:
        last_band = bf
    if last_band is not None:
        frame.alpha_composite(last_band, (12, BAND_Y))

    wd = word_at(t)
    if wd:
        d = ImageDraw.Draw(frame)
        key = wd in KEYWORDS
        col = (KEY_COL.get(wd, ORANGE) + (255,)) if key else (SILVER + (255,))
        shcol = (0, 0, 0, 190)
        ons = next((aa for ww, aa, bb2 in words if ww.strip().rstrip(".,!?").lower() == wd and aa <= t <= bb2 + 0.1), t)
        fs = int(66 * caption_impact(t, ons, key))
        cf = F(AR, fs)
        tw = d.textlength(wd, font=cf)
        x = (W - tw) / 2
        y = CAP_BOTTOM - fs
        if key:
            caption_bloom(frame, x, y, tw, fs, KEY_COL.get(wd, NEON))
        d.text((x + 2, y + 4), wd, font=cf, fill=shcol)
        d.text((x, y), wd, font=cf, fill=col)

    frame.convert("RGB").save(f"frames/out5/f{n:05d}.jpg", quality=95)
    if PREVIEW:
        print(f"preview {n}/{N} t={t:.2f} {name}", flush=True)
    elif n % 60 == 0:
        print(f"{n}/{N}", flush=True)

band_cap.release()
print("frames done", len(todo), flush=True)
