#!/usr/bin/env python3
"""Split animated talking-head: GitNexus, understand any codebase (Kevin, 2026-09-19).

1080x1920. Live band 1056x960 at y=936. Animation slot AH=770 at LAYER_Y=90,
PACK_DY=210, captions at y=867. The user's Subway Surfers screen recording
(source/subway.mov, 1920x1080) is the b-roll: full-slot browser card on the
hook + the "real time" beat, cropped HUD panels (probabilities, JEV tag,
score, keys) as live cards, the 50-games grid on "alive". Journey: b-roll
hook with a mystery "?" that flips to the JEV mark -> why viral (LLM faces)
-> tool calling terminal -> real time (not sped up stamp) -> the task card
-> RL + probabilities HUD -> 50 alive -> traditional LLM dies (game over)
-> CTA comment SEND. Max two big pieces. No em/en dashes on screen.
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
    word_onset,
)
from media_marks import (  # noqa: E402
    auto_counters,
    figure_row,
    figure_spotlight,
    gif_card,
    hf_layer_frame,
    logo_badge,
    name_plate,
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
from claude_marks import place_claude_invader, skill_chip  # noqa: E402

INK = (10, 11, 14)
SILVER = (198, 204, 214)
STEEL = (92, 98, 108)
GRAPHITE = (36, 38, 46)
CHAR = (48, 50, 58)
NEON = (57, 255, 132)
ORANGE = (255, 122, 24)
RED = (255, 48, 64)
PINK = (236, 72, 153)
PURPLE = (150, 96, 255)    # GitNexus brand purple
CYAN = (56, 200, 248)
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
    "hook": textured_bg((42, 44, 58), 7, PURPLE),
    "name": textured_bg((46, 42, 60), 11, PURPLE),
    "fork": textured_bg((50, 46, 50), 13, ORANGE),
    "add": textured_bg((42, 48, 58), 15, CYAN),
    "learn": textured_bg((44, 50, 54), 17, NEON),
    "clients": textured_bg((50, 46, 54), 19, ORANGE),
    "click": textured_bg((42, 46, 58), 21, CYAN),
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
    ("hook", 0.00, 6.50),
    ("name", 6.50, 8.58),
    ("fork", 8.58, 11.76),
    ("add", 11.76, 17.20),
    ("learn", 17.20, 24.94),
    ("clients", 24.94, 31.52),
    ("click", 31.52, 39.46),
    ("cta", 39.46, DUR),
]
KEYWORDS = {
    "visual", "learner", "one", "tool", "understand", "any", "code", "planet",
    "git", "nexus", "works",
    "forked", "project", "no", "idea",
    "add", "design", "knowledge", "graph", "screen",
    "learn", "every", "single", "component", "codebase", "knowing", "powerful",
    "clients", "non", "-technical", "everything",
    "click", "interactive", "automations", "live", "skills", "agents",
    "tutorial", "comment",
}
SECT_ACCENT = {
    "hook": PURPLE, "name": PURPLE, "fork": ORANGE, "add": CYAN, "learn": NEON,
    "clients": ORANGE, "click": CYAN, "cta": NEON,
}
KEY_COL = {
    "visual": PURPLE, "learner": PURPLE, "one": NEON, "tool": NEON, "understand": NEON, "any": ORANGE, "code": ORANGE, "planet": ORANGE,
    "git": PURPLE, "nexus": PURPLE, "works": NEON,
    "forked": ORANGE, "project": ORANGE, "no": RED, "idea": RED,
    "add": CYAN, "design": CYAN, "knowledge": CYAN, "graph": CYAN, "screen": NEON,
    "learn": NEON, "every": NEON, "single": NEON, "component": NEON, "codebase": ORANGE, "knowing": RED, "powerful": NEON,
    "clients": ORANGE, "non": RED, "-technical": RED, "everything": NEON,
    "click": CYAN, "interactive": CYAN, "automations": NEON, "live": NEON, "skills": PURPLE, "agents": ORANGE,
    "tutorial": ORANGE, "comment": NEON,
}


def tabs(word, after):
    """Absolute onset of the first `word` at/after `after`."""
    ons = word_onset(words, word, after=after)
    return ons if ons is not None else after


# ───────────────────────────── b-roll (the user's Subway Surfers recording) ─────────────────────────────

class Broll:
    """Sequential-friendly reader for source/subway.mov (1920x1080 @30)."""

    def __init__(self, path):
        self.cap = cv2.VideoCapture(path)
        self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.idx = -10
        self.cache = {}

    def frame(self, src_t):
        i = max(0, min(self.n - 1, int(src_t * 30)))
        if i in self.cache:
            return self.cache[i]
        if i != self.idx + 1:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, fr = self.cap.read()
        self.idx = i
        if not ok:
            return None
        img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
        self.cache = {i: img}
        return img


BROLL = Broll("source/broll.mov")
CROPS = {
    "graph": (10, 220, 1565, 1005),     # the knowledge-graph canvas
    "full": (0, 40, 1920, 1040),        # whole GitNexus UI
    "legend": (1590, 520, 1920, 1030),  # NODE TYPES list
    "brain": (1590, 225, 1920, 500),    # "Marketing OS · system brain" blurb
    "chips": (10, 50, 1090, 140),       # node-type filter chips
}
SRC_HOOK = 0.0
SRC_GRAPH = 23.5
SRC_LEGEND = 12.0
SRC_CLICK = 4.0
SRC_AUTOS = 6.5
SRC_SKILLS = 10.0
SRC_AGENTS = 20.0
SRC_CTA = 25.0


def broll_card(kind, src_t, w, h, label=None, accent=NEON, live=True, dim=0):
    """Cropped live frame from the recording in a graphite browser-style card."""
    fr = BROLL.frame(src_t)
    if fr is None:
        return None
    x0, y0, x1, y1 = CROPS[kind]
    im = fr.crop((x0, y0, x1, y1))
    scale = max(w / im.width, h / im.height)
    im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    cx0 = (im.width - w) // 2
    im = im.crop((cx0, 0, cx0 + w, h)).convert("RGBA")
    if dim:
        im = Image.blend(im, Image.new("RGBA", im.size, (10, 11, 14, 255)), dim / 255)
    top = 44 if kind == "game" else 0
    card = shadow_card((w + 20, h + top + (56 if label else 20)), 22, GRAPHITE + (255,))
    pad = 32
    if kind == "game":
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad, pad, pad + w + 20, pad + top + 30], 22, fill=INK + (255,))
        for i, col in enumerate([RED, ORANGE, NEON]):
            d.ellipse([pad + 22 + i * 30, pad + 14, pad + 38 + i * 30, pad + 30], fill=col + (255,))
        d.text((pad + 130, pad + 10), "gitnexus  ·  Marketing OS  ·  system brain", font=MONO_S, fill=STEEL + (255,))
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], 16, fill=255)
    im.putalpha(mask)
    card.alpha_composite(im, (pad + 10, pad + top + 10))
    d = ImageDraw.Draw(card)
    d.rectangle([pad, pad + top, pad + 8, pad + top + h + 20], fill=accent + (255,))
    if live:
        d.rounded_rectangle([pad + w - 96, pad + top + 20, pad + w + 4, pad + top + 58], 12, fill=INK + (220,))
        d.ellipse([pad + w - 84, pad + top + 31, pad + w - 68, pad + top + 47], fill=RED + (255,))
        d.text((pad + w - 58, pad + top + 27), "LIVE", font=F(AR, 22), fill=SILVER + (255,))
    if label:
        d.text((pad + 24, pad + top + h + 22), label, font=F(AR, 24), fill=SILVER + (255,))
    return card


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


def strike_chip(txt, accent=RED):
    """Chip with the word crossed out in red (no thinking / no decision making)."""
    def build():
        base = chip(txt, accent)
        img = base.copy()
        d = ImageDraw.Draw(img)
        d.line([(18, img.height // 2 + 4), (img.width - 12, img.height // 2 - 6)], fill=accent + (255,), width=7)
        return img
    return cached(("strikechip", txt, accent), build)


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


def stamp_card(txt, col=RED, fsz=72, w=620, h=150):
    """Rubber-stamp: thick outline, hollow, tilted by place()."""
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([6, 6, w - 6, h - 6], 22, outline=col + (255,), width=12)
        d.rounded_rectangle([22, 22, w - 22, h - 22], 14, outline=col + (150,), width=3)
        d.text((w / 2, h / 2 - 4), txt, font=F(AR, fsz), fill=col + (255,), anchor="mm")
        return img
    return cached(("stamp", txt, col, fsz, w, h), build)


def draw_code_rain(layer, lt, n=18, col=NEON):
    glyphs = [
        "jev", "typesafe", "left", "mid", "right", "jump", "slide", "198ms",
        "p=0.97", "system-1", "typed", "decision", "no tokens", "row 170",
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
        im = im.crop((x0, 0, x0 + w, h))
        card = shadow_card((w + 20, h + (60 if label else 20)), 22, GRAPHITE + (255,))
        pad = 32
        card.alpha_composite(im, (pad + 10, pad + 10))
        d = ImageDraw.Draw(card)
        d.rectangle([pad, pad, pad + 8, pad + h + 20], fill=accent + (255,))
        if label:
            d.text((pad + 24, pad + h + 22), label, font=F(AR, 24), fill=SILVER + (255,))
        return card

    return cached(("pshot", slug, w, h, label, accent), build)


def mystery_badge(lt, size=260):
    """Hook: glitching silver '?' round badge, sits over the HUD corner of the b-roll."""
    k = int(lt * 30)

    def build():
        rng = np.random.default_rng(k)
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse([0, 0, size - 1, size - 1], fill=(18, 19, 24, 245), outline=SILVER + (160,), width=4)
        fq = F(AR, int(size * 0.66))
        cx, cy = size / 2, size / 2 - 6
        jitter = 0 if (k % 9) else int(rng.integers(-10, 10))
        d.text((cx - 5 + jitter, cy), "?", font=fq, fill=RED + (150,), anchor="mm")
        d.text((cx + 5 - jitter, cy), "?", font=fq, fill=NEON + (150,), anchor="mm")
        d.text((cx, cy), "?", font=fq, fill=SILVER + (255,), anchor="mm")
        if k % 7 == 0:
            y = int(rng.integers(30, size - 30))
            d.rectangle([12, y, size - 12, y + 5], fill=PINK + (150,))
        return img

    return cached(("mysteryb", k % 63, size), build)


def whisper_line(text, p, w=960, h=64):
    shown = typewriter(text, p, cursor=True)

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((w / 2, h / 2), shown, font=F(AR, 34), fill=STEEL + (255,), anchor="mm")
        return img
    return cached(("whisper", shown, w, h), build)


def stat_chip(big, small, accent=NEON, w=440, h=150):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w, h], 24, fill=GRAPHITE + (255,), outline=accent + (160,), width=3)
        d.text((w / 2, 58), big, font=F(AR, 76), fill=accent + (255,), anchor="mm")
        d.text((w / 2, 120), small, font=F(AR, 24), fill=SILVER + (255,), anchor="mm")
        return img
    return cached(("statchip", big, small, accent, w, h), build)


def tool_terminal(lt, w=600, h=330):
    """Tool-calling terminal: the decision comes out typed, no reasoning tokens."""
    lines = [
        (0.00, "> frame #172  ·  row 170 in 0.3s", STEEL),
        (0.30, "> jev.act(frame)", SILVER),
        (0.75, "  -> A · LEFT      p=0.97", ORANGE),
        (1.15, "  198 ms  ·  0 reasoning tokens", NEON),
        (1.90, "> jev.act(frame)  ->  W · JUMP", SILVER),
        (2.55, "> jev.act(frame)  ->  S · SLIDE", SILVER),
    ]
    shown = []
    for t0, txt, col in lines:
        if lt >= t0:
            shown.append((typewriter(txt, clamp01((lt - t0) / 0.35), cursor=False), col))
    k = tuple(shown)

    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad + 14, pad + 12, pad + w - 14, pad + 56], 12, fill=INK + (255,))
        d.text((pad + 30, pad + 20), "TOOL CALLING", font=F(AR, 24), fill=ORANGE + (255,))
        d.text((pad + w - 190, pad + 22), "no thinking", font=MONO_S, fill=STEEL + (255,))
        y = pad + 76
        for txt, col in shown:
            d.text((pad + 24, y), txt, font=MONO, fill=col + (255,))
            y += 38
        if not shown:
            d.text((pad + 24, y), "waiting for frame...", font=MONO, fill=STEEL + (255,))
        return card
    return cached(("toolterm", k, w, h), build)


def task_card(p, w=960, h=290):
    """The agent's one instruction, typed in on the spoken words."""
    text = "make this player last as long as humanly possible"
    shown = typewriter(text, p, cursor=True)
    done = p >= 1

    def build():
        card = shadow_card((w, h), 24, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad + 16, pad + 14, pad + w - 16, pad + 62], 14, fill=INK + (255,))
        d.text((pad + 34, pad + 24), "TASK", font=F(AR, 24), fill=ORANGE + (255,))
        d.text((pad + w - 220, pad + 26), "assigned to  JEV", font=MONO_S, fill=STEEL + (255,))
        f2 = F(AR, 44)
        x, y = pad + 34, pad + 86
        maxw = w - 68
        line = ""
        for wd in shown.split():
            test = (line + " " + wd).strip()
            if d.textlength(test, font=f2) > maxw:
                d.text((x, y), line, font=f2, fill=SILVER + (255,))
                y += 54
                line = wd
            else:
                line = test
        d.text((x, y), line, font=f2, fill=SILVER + (255,))
        if done:
            d.rounded_rectangle([pad + 34, pad + h - 66, pad + 250, pad + h - 22], 12, fill=NEON + (255,))
            d.text((pad + 142, pad + h - 44), "ACCEPTED", font=F(AR, 26), fill=INK + (255,), anchor="mm")
        return card
    return cached(("task", shown, done, w, h), build)


def latency_card(p, w=600, h=300):
    """Per-decision latency: a traditional LLM vs JEV. Bars fill on p."""
    q = clamp01(p)
    gpt = int(2400 * (1 - (1 - q) ** 3))
    jev = 198

    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + 24, pad + 14), "LATENCY PER DECISION", font=F(AR, 26), fill=SILVER + (255,))
        rows = [("GPT / ASTRA", gpt, RED, gpt / 2400), ("JEV", jev, NEON, jev / 2400)]
        y = pad + 66
        for lab, v, col, frac in rows:
            d.text((pad + 24, y), lab, font=F(AR, 28), fill=col + (255,))
            d.text((pad + w - 24, y), f"{v:,} ms", font=F(AR, 40), fill=col + (255,), anchor="ra")
            d.rounded_rectangle([pad + 24, y + 52, pad + w - 24, y + 76], 10, fill=CHAR + (255,))
            fw = int((w - 48) * max(0.02, frac))
            d.rounded_rectangle([pad + 24, y + 52, pad + 24 + fw, y + 76], 10, fill=col + (255,))
            y += 108
        d.text((pad + 24, pad + h - 42), "the character is already dead by the time GPT answers", font=MONO_S, fill=STEEL + (255,))
        return card
    return cached(("latency", gpt // 40, w, h), build)


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


def rl_card(p, w=520, h=300):
    """Reinforcement-learning loop card: spinning loop arrows + attempt counter."""
    ang = (p * 720) % 360
    att = int(1 + 9999 * (1 - (1 - clamp01(p)) ** 3))

    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + 24, pad + 16), "REINFORCEMENT", font=F(AR, 34), fill=PINK + (255,))
        d.text((pad + 24, pad + 52), "LEARNING", font=F(AR, 34), fill=PINK + (255,))
        la = loop_arrows(ang)
        la = la.resize((150, 150), Image.LANCZOS)
        card.alpha_composite(la, (pad + w - 190, pad + 20))
        d.text((pad + 24, pad + 120), "attempt", font=MONO_S, fill=STEEL + (255,))
        d.text((pad + 24, pad + 146), f"{att:,}", font=F(AR, 64), fill=SILVER + (255,))
        d.rounded_rectangle([pad + 24, pad + 236, pad + w - 24, pad + 256], 8, fill=CHAR + (255,))
        d.rounded_rectangle([pad + 24, pad + 236, pad + 24 + int((w - 48) * clamp01(p)), pad + 256], 8, fill=PINK + (255,))
        return card
    return cached(("rlcard", int(ang / 6), att // 37, w, h), build)


def jev_hero(size=480):
    """Giant JEV mark: pink round TypeSafe logo."""
    def build():
        return logo_badge("jev", size, fill=INK + (255,), punch=False)
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


def pointer_chip(txt, accent=ORANGE):
    """Chip with a big chevron pointing right (the HUD is on the right hand side)."""
    def build():
        base = chip(txt, accent)
        img = Image.new("RGBA", (base.width + 70, base.height), (0, 0, 0, 0))
        img.alpha_composite(base, (0, 0))
        d = ImageDraw.Draw(img)
        x = base.width + 14
        d.polygon([(x, 8), (x + 44, base.height // 2), (x, base.height - 8)], fill=accent + (255,))
        return img
    return cached(("pointer", txt, accent), build)


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



# ───────────────────────────── video-3 cards ─────────────────────────────

def mystery_card(lt, w=960, h=380):
    """Cold open: dark card, glitching '?', whisper line. Reveal on 'Jev'."""
    k = int(lt * 30)

    def build():
        rng = np.random.default_rng(k)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w, h], 30, fill=(18, 19, 24, 255), outline=STEEL + (120,), width=2)
        fq = F(AR, 260)
        cx, cy = w / 2, h / 2 - 8
        jitter = 0 if (k % 9) else int(rng.integers(-14, 14))
        d.text((cx - 6 + jitter, cy), "?", font=fq, fill=RED + (150,), anchor="mm")
        d.text((cx + 6 - jitter, cy), "?", font=fq, fill=NEON + (150,), anchor="mm")
        d.text((cx, cy), "?", font=fq, fill=SILVER + (255,), anchor="mm")
        if k % 7 == 0:
            y = int(rng.integers(30, h - 30))
            d.rectangle([20, y, w - 20, y + 6], fill=PINK + (140,))
        d.text((cx, h - 42), "everyone is losing their mind over this...", font=F(AR, 30), fill=STEEL + (255,), anchor="mm")
        return img

    return cached(("mystery", k % 63), build)


ORCH_NODES = ["openai", "claude", "gemini", "deepseek", "github", "nvidia"]


def orchestra_card(spin, w=660, h=430, lit=True):
    """JEV in the middle, model / tool nodes around it, a beam sweeps node to node."""
    k = int(spin * 30)
    node_k = int(spin * 2.2) % len(ORCH_NODES)
    travel = (spin * 2.2) % 1.0

    def build():
        card = shadow_card((w, h), 24, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + 24, pad + 14), "ORCHESTRATOR", font=F(AR, 24), fill=PINK + (255,))
        d.text((pad + w - 210, pad + 18), "directs the flow", font=MONO_S, fill=STEEL + (255,))
        cx, cy = pad + w / 2, pad + h / 2 + 18
        rx, ry = w / 2 - 90, h / 2 - 80
        pts = []
        for i in range(len(ORCH_NODES)):
            ang = -math.pi / 2 + i * 2 * math.pi / len(ORCH_NODES)
            pts.append((cx + rx * math.cos(ang), cy + ry * math.sin(ang)))
        for i, (x, y) in enumerate(pts):
            on = lit and i == node_k
            d.line([(cx, cy), (x, y)], fill=(PINK if on else STEEL) + (255 if on else 90,), width=6 if on else 3)
            if on:
                tx, ty = cx + (x - cx) * travel, cy + (y - cy) * travel
                d.ellipse([tx - 10, ty - 10, tx + 10, ty + 10], fill=NEON + (255,))
        for i, (x, y) in enumerate(pts):
            b = logo_badge(ORCH_NODES[i], 92, fill=(CHAR if (lit and i == node_k) else GRAPHITE) + (255,),
                           punch=(ORCH_NODES[i] != "claude"))
            if b is not None:
                card.alpha_composite(b, (int(x - b.width / 2), int(y - b.height / 2)))
        jb = logo_badge("jev", 150, fill=INK + (255,), punch=False)
        if jb is not None:
            card.alpha_composite(jb, (int(cx - jb.width / 2), int(cy - jb.height / 2)))
        return card
    return cached(("orch", node_k, int(travel * 12), lit, w, h), build)


def chat_card(text_full, p, w=960, h=260, who="you"):
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
        f2 = F(AR, 40)
        x, y = pad + 34, pad + 90
        maxw = w - 68
        line = ""
        for wd in shown.split():
            test = (line + " " + wd).strip()
            if d.textlength(test, font=f2) > maxw:
                d.text((x, y), line, font=f2, fill=SILVER + (255,))
                y += 50
                line = wd
            else:
                line = test
        d.text((x, y), line + (" |" if cursor else ""), font=f2, fill=SILVER + (255,))
        return card
    return cached(("chat", text_full, n, cursor, w, h, who), build)


def tool_chip(fn, done=False, accent=NEON, w=460, h=96):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w, h], 20, fill=INK + (255,), outline=accent + (200,), width=3)
        d.text((24, 18), "tool call", font=MONO_S, fill=STEEL + (255,))
        d.text((24, 44), fn, font=F(ML, 30), fill=accent + (255,))
        if done:
            d.text((w - 34, h / 2), "✓", font=F(AR, 44), fill=NEON + (255,), anchor="mm")
        return img
    return cached(("toolchip", fn, done, accent, w, h), build)


def race_card(kind, p_tok, p_time, lt, w=500, h=340):
    """THINKING AGENT (red, burns tokens + seconds) vs JEV (pink, instant tool call)."""
    thinking = kind == "thinking"
    tokens = int(12480 * (1 - (1 - clamp01(p_tok)) ** 2)) if thinking else 0
    secs = 9.4 * clamp01(p_time) if thinking else 0.198
    dots = "." * (1 + int(lt * 4) % 4)
    step = int(clamp01(p_time) * 5)

    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        acc = RED if thinking else PINK
        d.rounded_rectangle([pad + 14, pad + 12, pad + w - 14, pad + 56], 12, fill=INK + (255,))
        d.text((pad + 30, pad + 20), "THINKING AGENT" if thinking else "JEV", font=F(AR, 24), fill=acc + (255,))
        d.text((pad + 24, pad + 76), "tokens burned", font=MONO_S, fill=STEEL + (255,))
        d.text((pad + 24, pad + 98), f"{tokens:,}", font=F(AR, 60), fill=(RED if thinking else NEON) + (255,))
        d.text((pad + w - 24, pad + 76), "time", font=MONO_S, fill=STEEL + (255,), anchor="ra")
        d.text((pad + w - 24, pad + 98), (f"{secs:.1f} s" if thinking else "198 ms"), font=F(AR, 60),
               fill=(RED if thinking else NEON) + (255,), anchor="ra")
        y = pad + 190
        if thinking:
            lines = ["reasoning" + dots, "hmm, should I use a tool?" + dots, "let me reconsider" + dots,
                     "ok maybe get_weather" + dots, "actually wait" + dots]
            d.text((pad + 24, y), lines[min(step, 4)], font=MONO, fill=SILVER + (255,))
            d.text((pad + 24, y + 34), "tool call: not yet", font=MONO, fill=STEEL + (255,))
        else:
            d.text((pad + 24, y), 'get_weather("miami")  ->  called', font=MONO, fill=NEON + (255,))
            d.text((pad + 24, y + 34), "0 reasoning tokens  ·  typed decision", font=MONO, fill=STEEL + (255,))
        d.rounded_rectangle([pad + 24, pad + h - 44, pad + w - 24, pad + h - 24], 8, fill=CHAR + (255,))
        fw = int((w - 48) * (clamp01(p_time) if thinking else 1.0))
        d.rounded_rectangle([pad + 24, pad + h - 44, pad + 24 + fw, pad + h - 24], 8, fill=acc + (255,))
        return card
    return cached(("race", kind, tokens // 60, round(secs, 1), dots if thinking else "", step, w, h), build)


def layer_stack_card(p, w=760, h=400):
    """Existing models as a row of tiles; the JEV layer slides down on top."""
    q = clamp01(p)
    drop = int((1 - (1 - q) ** 3) * 150)

    def build():
        card = shadow_card((w, h), 24, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + 24, pad + h - 50), "your AI models that already exist", font=F(AR, 24), fill=SILVER + (255,))
        slugs = ["openai", "claude", "gemini", "deepseek", "xai"]
        step = (w - 60) // len(slugs)
        y0 = pad + h - 200
        d.rounded_rectangle([pad + 20, y0 - 16, pad + w - 20, y0 + 130], 18, fill=CHAR + (255,))
        for i, s in enumerate(slugs):
            b = logo_badge(s, 110, fill=GRAPHITE + (255,), punch=(s != "claude"))
            if b is not None:
                card.alpha_composite(b, (pad + 30 + i * step + (step - b.width) // 2, y0))
        # JEV layer bar
        ly = pad - 120 + drop
        d.rounded_rectangle([pad + 20, ly, pad + w - 20, ly + 96], 18, fill=PINK + (255,), outline=SILVER + (90,), width=2)
        d.text((pad + w / 2, ly + 48), "JEV LAYER", font=F(AR, 52), fill=INK + (255,), anchor="mm")
        d.text((pad + 34, ly + 14), "decisions", font=MONO_S, fill=INK + (200,))
        d.text((pad + w - 34, ly + 14), "routing", font=MONO_S, fill=INK + (200,), anchor="ra")
        return card
    return cached(("layerstack", drop, w, h), build)


def one_card(w=440, h=440):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w, h], 30, fill=GRAPHITE + (255,), outline=NEON + (170,), width=4)
        d.text((w / 2, h / 2 - 30), "1", font=F(AR, 300), fill=NEON + (255,), anchor="mm")
        d.text((w / 2, h - 50), "CORE REASON", font=F(AR, 34), fill=SILVER + (255,), anchor="mm")
        return img
    return cached(("onecard", w, h), build)



# ───────────────────────────── GitNexus cards ─────────────────────────────

def mystery_badge2(lt, size=240):
    return mystery_badge(lt, size)


def whisper_line(text, p, w=960, h=64):
    shown = typewriter(text, p, cursor=True)

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((w / 2, h / 2), shown, font=F(AR, 34), fill=SILVER + (230,), anchor="mm")
        return img
    return cached(("whisper2", shown, w, h), build)


def gn_hero(size=420):
    def build():
        return logo_badge("gitnexus", size, fill=INK + (255,), punch=False)
    return cached(("gnhero", size), build)


def gn_wordmark(w=960, h=150):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w, h], 30, fill=PURPLE + (255,), outline=SILVER + (80,), width=2)
        d.text((w / 2 - 40, h / 2 - 8), "GITNEXUS", font=F(AR, 100), fill=INK + (255,), anchor="mm")
        d.text((w - 150, h / 2), "open source", font=F(AR, 26), fill=INK + (220,), anchor="mm")
        return img
    return cached(("gnword", w, h), build)


def terminal_gn(lt, w=620, h=330, mode="fork"):
    if mode == "fork":
        lines = [
            (0.00, "$ git clone github.com/someone/project", SILVER),
            (0.55, "  Cloning into 'project'...  done.", STEEL),
            (0.95, "$ ls src/", SILVER),
            (1.30, "  412 files   ·   38,904 lines", ORANGE),
            (1.80, "$ cat README.md", SILVER),
            (2.20, "  (empty)", RED),
        ]
        title = "FRESH FORK"
    else:
        lines = [
            (0.00, "$ npx gitnexus analyze .", SILVER),
            (0.45, "  parsing 412 files...", STEEL),
            (0.85, "  286 nodes  ·  691 edges", CYAN),
            (1.25, "  building knowledge graph...", STEEL),
            (1.70, "  done in 3.2 s  ->  open the graph", NEON),
        ]
        title = "GITNEXUS"
    shown = []
    for t0, txt, col in lines:
        if lt >= t0:
            shown.append((typewriter(txt, clamp01((lt - t0) / 0.35), cursor=False), col))
    k = tuple(shown)

    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad + 14, pad + 12, pad + w - 14, pad + 56], 12, fill=INK + (255,))
        for i, col in enumerate([RED, ORANGE, NEON]):
            d.ellipse([pad + 30 + i * 24, pad + 26, pad + 44 + i * 24, pad + 40], fill=col + (255,))
        d.text((pad + 120, pad + 20), title, font=F(AR, 24), fill=(PURPLE if mode != "fork" else ORANGE) + (255,))
        y = pad + 76
        for txt, col in shown:
            d.text((pad + 24, y), txt, font=MONO, fill=col + (255,))
            y += 38
        if not shown:
            d.text((pad + 24, y), "_", font=MONO, fill=STEEL + (255,))
        return card
    return cached(("termgn", mode, k, w, h), build)


def repo_card(w=760, h=300):
    return product_shot("gitnexus", w=w, h=h, label="github.com/abhigyanpatwari/GitNexus  ·  47k stars", accent=PURPLE)


NODE_TYPES = [("Schedulers", SILVER), ("Automations", NEON), ("Skills", PURPLE), ("API routes", ORANGE),
              ("Webhooks", PINK), ("Dashboard pages", CYAN), ("DB tables", (180, 255, 90)), ("Personas", ORANGE)]


def node_types_card(n_on, w=460, h=400):
    """Legend-style list of node types lighting up one by one."""
    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + 24, pad + 14), "NODE TYPES", font=F(AR, 24), fill=SILVER + (255,))
        y = pad + 58
        for i, (lab, col) in enumerate(NODE_TYPES):
            on = i < n_on
            d.ellipse([pad + 26, y + 6, pad + 46, y + 26], fill=(col if on else CHAR) + (255,))
            d.text((pad + 62, y), lab, font=F(AR, 28), fill=(SILVER if on else STEEL) + (255,))
            y += 40
        return card
    return cached(("nodetypes", n_on, w, h), build)


def client_card(p, w=520, h=300):
    """A non-technical client asking; the graph answers."""
    q = "how does my system actually work?"
    shown = typewriter(q, clamp01(p), cursor=True)

    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad + 16, pad + 14, pad + w - 16, pad + 62], 14, fill=INK + (255,))
        d.text((pad + 34, pad + 24), "CLIENT", font=F(AR, 24), fill=ORANGE + (255,))
        d.text((pad + w - 200, pad + 26), "non-technical", font=MONO_S, fill=STEEL + (255,))
        f2 = F(AR, 34)
        x, y = pad + 34, pad + 88
        line = ""
        for wd in shown.split():
            test = (line + " " + wd).strip()
            if d.textlength(test, font=f2) > w - 68:
                d.text((x, y), line, font=f2, fill=SILVER + (255,)); y += 44; line = wd
            else:
                line = test
        d.text((x, y), line, font=f2, fill=SILVER + (255,))
        d.text((pad + 34, pad + h - 60), "answer: click around the graph", font=MONO_S, fill=NEON + (255,))
        return card
    return cached(("client", shown, w, h), build)


def globe_card(spin, size=360, col=CYAN, col2=PURPLE):
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
        glow = glow.filter(ImageFilter.GaussianBlur(22))
        img.alpha_composite(glow)
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(14, 16, 28, 255), outline=col + (230,), width=4)
        tilt = 0.38
        ang = (k / 90.0) * 2 * math.pi
        # latitude rings
        for lat in (-60, -30, 0, 30, 60):
            la = math.radians(lat)
            ry = R * math.cos(la) * tilt
            rx = R * math.cos(la)
            yy = cy - R * math.sin(la)
            box = [cx - rx, yy - ry, cx + rx, yy + ry]
            d.arc(box, 0, 180, fill=col + (150 if lat else 220,), width=2 if lat else 3)
            d.arc(box, 180, 360, fill=col + (70,), width=1)
        # meridians (rotating)
        for i in range(8):
            phi = ang + i * math.pi / 8
            rx = abs(R * math.cos(phi))
            front = math.sin(phi) >= 0
            if rx < 3:
                d.line([(cx, cy - R), (cx, cy + R)], fill=col2 + (200 if front else 60,), width=2)
                continue
            box = [cx - rx, cy - R, cx + rx, cy + R]
            if front:
                d.arc(box, 90, 270, fill=col2 + (200,), width=2) if math.cos(phi) < 0 else d.arc(box, 270, 90, fill=col2 + (200,), width=2)
            else:
                d.arc(box, 90, 270, fill=col2 + (60,), width=1) if math.cos(phi) < 0 else d.arc(box, 270, 90, fill=col2 + (60,), width=1)
        # a few "repo" pins that ride the rotation
        rng = np.random.default_rng(3)
        for j in range(14):
            lat = math.radians(float(rng.uniform(-55, 65)))
            lon = float(rng.uniform(0, 2 * math.pi)) + ang
            x3 = math.cos(lat) * math.sin(lon)
            z3 = math.cos(lat) * math.cos(lon)
            y3 = math.sin(lat)
            if z3 < 0:
                continue
            px = cx + R * x3
            py = cy - R * (y3 * (1 - tilt) + 0.0) - R * y3 * 0.0
            py = cy - R * y3
            r = 5 + 4 * z3
            d.ellipse([px - r, py - r, px + r, py + r], fill=NEON + (255,))
        # rim highlight
        d.arc([cx - R + 6, cy - R + 6, cx + R - 6, cy + R - 6], 200, 320, fill=(255, 255, 255, 110), width=3)
        return img
    return cached(("globe", k, size, col, col2), build)


HOLD = skill_chip("NEXUS")
TOPIC_CODE = ["gitnexus", "github", "openai", "anthropic", "gemini", "deepseek", "nvidia", "xai"]

T_VISUAL = tabs("visual", 0.1)          # 0.30
T_TOOL = tabs("tool", 1.5)              # 1.86
T_UNDERSTAND = tabs("understand", 3.0)  # 3.26
T_ANY = tabs("any", 3.6)                # 3.84
T_CODE = tabs("code", 4.5)              # 4.80
T_PLANET = tabs("planet", 5.2)          # 5.48
T_GIT = tabs("Git", 6.5)                # 6.80
T_NEXUS = tabs("Nexus", 6.9)            # 7.08
T_WORKS = tabs("works", 7.9)            # 8.14
T_FORKED = tabs("forked", 9.0)          # 9.32
T_NOIDEA = tabs("no", 10.4)             # 10.60
T_WORKS2 = tabs("works", 11.2)          # 11.50
T_ADD = tabs("add", 12.0)               # 12.16
T_GIT2 = tabs("Git", 12.3)              # 12.40
T_DESIGN = tabs("design", 13.6)         # 13.78
T_KNOW = tabs("knowledge", 14.4)        # 14.62
T_GRAPH = tabs("graph", 14.8)           # 14.98
T_SCREEN = tabs("screen", 16.3)         # 16.58
T_LEARN = tabs("learn", 17.5)           # 17.72
T_EVERY = tabs("every", 18.3)           # 18.50
T_COMPONENT = tabs("component", 19.2)   # 19.36
T_CODEBASE = tabs("code", 20.4)         # 20.54
T_KNOWING = tabs("knowing", 21.6)       # 21.84
T_POWERFUL = tabs("powerful", 24.2)     # 24.48
T_BUILD = tabs("build", 25.2)           # 25.38
T_CLIENTS = tabs("clients", 26.3)       # 26.56
T_NONTECH = tabs("non", 27.0)           # 27.16
T_UNDERSTAND2 = tabs("understand", 28.6)  # 28.84
T_EVERYTHING = tabs("everything", 29.3)   # 29.42
T_CLICK = tabs("click", 31.3)           # 31.52
T_INTERACTIVE = tabs("interactive", 32.2)  # 32.34
T_AUTOS = tabs("automations", 34.6)     # 34.88
T_LIVE = tabs("live", 35.4)             # 35.54
T_SKILLS = tabs("skills", 35.8)         # 35.98
T_AGENTS = tabs("agents", 36.9)         # 37.04
T_BLAH = tabs("blah", 37.8)             # 37.92
T_HELPS = tabs("helps", 38.6)           # 38.74
T_GIT3 = tabs("Git", 39.8)              # 39.94
T_TUTORIAL = tabs("tutorial", 41.2)     # 41.38
T_COMMENT = tabs("comment", 41.9)       # 42.08
T_NEXUS2 = tabs("NEXUS", 42.3)          # 42.44


def scene(layer, name, lt, t, a):
    gsl = int(30 * math.sin(lt * 0.6))
    r = lambda T: max(0.0, T - 0.08 - a)  # noqa: E731

    if name == "hook":
        # the hook IS the b-roll: the live knowledge graph from frame 0, a "?" until "tool"
        draw_code_rain(layer, lt, n=12, col=PURPLE)
        ticker(layer, "  VISUAL LEARNERS  ·  ONE TOOL  ·  ANY CODEBASE ON THE PLANET  ·  ", 700, lt, speed=170, fill=PURPLE + (100,))
        t_tool, t_und, t_any, t_code, t_planet = r(T_TOOL), r(T_UNDERSTAND), r(T_ANY), r(T_CODE), r(T_PLANET)
        if lt < t_und - 0.06:
            place(layer, broll_card("graph", SRC_HOOK + t, 1000, 520, accent=PURPLE), 540, 250, lt, -0.4, dur=0.01,
                  exit_at=t_und - 0.06)
        if lt < t_tool:
            place(layer, mystery_badge(lt, 240), 880, 120, lt, -0.4, dur=0.01, idle=0)
            place(layer, whisper_line("one tool to understand any codebase...", clamp01(lt / 1.4)), 540, 545, lt, -0.4, dur=0.01)
        elif lt < t_und - 0.06:
            place(layer, chip("the one tool I use", NEON), 260, 545, lt, t_tool, frm="left", exit_at=t_und - 0.06)
            light_hit(layer, 880, 120 + PACK_DY, lt, t_tool, PURPLE)
        else:
            # "understand any piece of code on the planet": the Hangover calculation meme, then a globe (Kevin 2026-09-19)
            place(layer, big_text_card("UNDERSTAND ANY PIECE OF CODE", NEON, fsz=46, w=960, h=110),
                  540, 32, lt, t_und, scale_pop=True)
            light_hit(layer, 540, 32 + PACK_DY, lt, t_und, NEON)
            front_gif(gif_card("thinking", max(0, lt - t_und), w=640, frame="round", label="me reading the codebase"),
                      340, 320, lt, t_und, **entrance(2))
            if lt >= t_code and lt < t_planet - 0.06:
                place(layer, stamp_card("ANY CODE", ORANGE, fsz=70, w=460, h=140), 820, 200, lt, t_code, dur=0.2,
                      tilt=-10, scale_pop=True, idle=0, exit_at=t_planet - 0.06)
                light_hit(layer, 820, 200 + PACK_DY, lt, t_code, ORANGE)
            if lt >= t_planet:
                place(layer, globe_card(lt - t_planet, size=340), 820, 300, lt, t_planet, dur=0.25, scale_pop=True, idle=0)
                light_hit(layer, 820, 300 + PACK_DY, lt, t_planet, CYAN)
                place(layer, chip("on the planet", ORANGE), 820, 520, lt, t_planet + 0.15, frm="down")

    elif name == "name":
        draw_code_rain(layer, lt, n=14, col=PURPLE)
        layer.alpha_composite(ghost_img("GITNEXUS", 110), (-60 + gsl, 0))
        ticker(layer, "  GITNEXUS  ·  OPEN SOURCE  ·  ZERO-SERVER CODE INTELLIGENCE ENGINE  ·  47K STARS  ·  ", 700, lt, speed=170, fill=PURPLE + (110,))
        t_git, t_nex, t_works = r(T_GIT), r(T_NEXUS), r(T_WORKS)
        # HF lower third (slot y>=632) is live 6.7..8.6: everything stays above cy≈330
        place(layer, gn_wordmark(960, 130), 540, -25, lt, -0.35, dur=0.01, scale_pop=True)
        place(layer, gn_hero(340), 290, 250, lt, -0.3, dur=0.01, idle=0)
        light_hit(layer, 290, 250 + PACK_DY, lt, t_nex, PURPLE)
        light_rays(layer, 290, 250 + PACK_DY, lt, PURPLE)
        place(layer, repo_card(w=440, h=190), 800, 245, lt, t_nex + 0.05, frm="right", scale_pop=True)

    elif name == "fork":
        draw_code_rain(layer, lt, n=12, col=ORANGE)
        ticker(layer, "  FRESH FORK  ·  412 FILES  ·  NO README  ·  NO IDEA HOW IT WORKS  ·  ", 700, lt, speed=170, fill=ORANGE + (100,))
        t_fork, t_no, t_w2 = r(T_FORKED), r(T_NOIDEA), r(T_WORKS2)
        place(layer, big_text_card("LET'S SAY I FORKED A PROJECT", ORANGE, fsz=46, w=960, h=110),
              540, 32, lt, -0.35, dur=0.01, scale_pop=True)
        place(layer, terminal_gn(lt - max(0.0, t_fork - 0.3), w=600, h=330, mode="fork"), 340, 300, lt, -0.3, dur=0.01, frm="left")
        if lt >= t_fork:
            light_hit(layer, 340, 300 + PACK_DY, lt, t_fork, ORANGE)
        place(layer, logo_badge("github", 200, fill=GRAPHITE + (255,)), 850, 220, lt, -0.3, dur=0.01, idle=0,
              exit_at=t_no - 0.06)
        if lt >= t_no:
            front_gif(gif_card("confused", max(0, lt - t_no), w=380, frame="round", label="no idea how it works"),
                      840, 300, lt, t_no, **entrance(3))
            light_hit(layer, 840, 300 + PACK_DY, lt, t_no, RED)

    elif name == "add":
        draw_code_rain(layer, lt, n=12, col=CYAN)
        ticker(layer, "  ADD GITNEXUS  ·  IT DESIGNS A KNOWLEDGE GRAPH  ·  286 NODES  ·  691 EDGES  ·  ", 700, lt, speed=170, fill=CYAN + (100,))
        t_add, t_git, t_des, t_know, t_graph, t_screen = r(T_ADD), r(T_GIT2), r(T_DESIGN), r(T_KNOW), r(T_GRAPH), r(T_SCREEN)
        # HF kinetic "KNOWLEDGE GRAPH" owns the slot top 14.5..17.1
        if lt < t_know - 0.06:
            place(layer, big_text_card("I ADD GITNEXUS TO IT", CYAN, fsz=50, w=960, h=116),
                  540, 32, lt, -0.35, dur=0.01, scale_pop=True, exit_at=t_know - 0.06)
            place(layer, terminal_gn(lt - t_add, w=620, h=300, mode="add"), 350, 300, lt, t_add, dur=0.25, frm="left",
                  exit_at=t_know - 0.06)
            light_hit(layer, 350, 300 + PACK_DY, lt, t_git, CYAN)
            place(layer, gn_hero(300), 840, 300, lt, t_git, idle=0, exit_at=t_know - 0.06, **entrance(4))
            if lt >= t_des:
                place(layer, chip("it designs...", CYAN), 840, 480, lt, t_des, frm="down", exit_at=t_know - 0.06)
        else:
            place(layer, broll_card("graph", SRC_GRAPH + (lt - t_know), 1000, 500, accent=CYAN, label="the knowledge graph of my Marketing OS"),
                  540, 330, lt, t_know, dur=0.22, scale_pop=True)
            light_hit(layer, 540, 330 + PACK_DY, lt, t_know, CYAN)
            if lt >= t_screen:
                place(layer, chip("the one on your screen", NEON), 860, 130, lt, t_screen, frm="right")

    elif name == "learn":
        draw_code_rain(layer, lt, n=12, col=NEON)
        layer.alpha_composite(ghost_img("LEARN", 120), (-60 + gsl, 0))
        ticker(layer, "  EVERY SINGLE COMPONENT  ·  WITHOUT KNOWING HOW TO CODE  ·  ", 700, lt, speed=170, fill=NEON + (100,))
        t_learn, t_every, t_comp, t_cb, t_knowing, t_pow = (r(T_LEARN), r(T_EVERY), r(T_COMPONENT), r(T_CODEBASE),
                                                             r(T_KNOWING), r(T_POWERFUL))
        # HF "nodes" counter sits top-right 19.3..21.2 (slot x>=690, y<=134)
        if lt < t_pow - 0.06:
            place(layer, big_text_card("EVERY SINGLE COMPONENT", NEON, fsz=48, w=640, h=110),
                  360, 32, lt, -0.35, dur=0.01, scale_pop=True, exit_at=t_pow - 0.06)
            n_on = 0 if lt < t_every else min(len(NODE_TYPES), 1 + int((lt - t_every) / 0.22))
            place(layer, node_types_card(n_on, w=440, h=400), 280, 300, lt, -0.3, dur=0.01, exit_at=t_pow - 0.06)
            light_hit(layer, 280, 300 + PACK_DY, lt, t_comp, NEON)
            place(layer, broll_card("graph", SRC_LEGEND + lt, 480, 270, accent=NEON), 790, 280, lt, t_learn,
                  exit_at=t_pow - 0.06, **entrance(2))
            if lt >= t_knowing:
                place(layer, strike_chip("knowing how to code", RED), 760, 530, lt, t_knowing, frm="down", exit_at=t_pow - 0.06)
                light_hit(layer, 760, 530 + PACK_DY, lt, t_knowing, RED)
        else:
            place(layer, stamp_card("SO POWERFUL", NEON, fsz=80, w=700, h=160), 540, 60, lt, t_pow, dur=0.2, tilt=-6,
                  scale_pop=True, idle=0)
            light_hit(layer, 540, 60 + PACK_DY, lt, t_pow, NEON)
            light_rays(layer, 540, 60 + PACK_DY, lt, NEON)
            front_gif(gif_card("knowledge", max(0, lt - t_pow), w=460, frame="round"), 320, 360, lt, t_pow, **entrance(1))
            place(layer, gn_hero(280), 820, 360, lt, t_pow + 0.1, idle=0, **entrance(3))

    elif name == "clients":
        draw_code_rain(layer, lt, n=12, col=ORANGE)
        ticker(layer, "  CLIENT PROJECTS  ·  NON-TECHNICAL  ·  THEY NEED TO SEE HOW IT WORKS  ·  ", 700, lt, speed=170, fill=ORANGE + (100,))
        t_build, t_cl, t_nt, t_und, t_evt = r(T_BUILD), r(T_CLIENTS), r(T_NONTECH), r(T_UNDERSTAND2), r(T_EVERYTHING)
        if lt < t_cl - 0.06:
            place(layer, big_text_card("WHEN I BUILD FOR CLIENTS", ORANGE, fsz=48, w=960, h=110),
                  540, 32, lt, -0.35, dur=0.01, scale_pop=True, exit_at=t_cl - 0.06)
            place(layer, broll_card("full", SRC_CTA + lt, 620, 340, accent=ORANGE), 380, 300, lt, -0.3, dur=0.01,
                  exit_at=t_cl - 0.06)
            place(layer, gn_hero(240), 860, 300, lt, -0.3, dur=0.01, idle=0, exit_at=t_cl - 0.06)
        else:
            place(layer, big_text_card("NON-TECHNICAL CLIENTS", ORANGE, fsz=54, w=960, h=120),
                  540, 34, lt, t_cl, scale_pop=True)
            light_hit(layer, 540, 34 + PACK_DY, lt, t_cl, ORANGE)
            place(layer, client_card((lt - t_cl) / 1.6, w=520, h=300), 300, 300, lt, t_cl, dur=0.25, frm="left")
            if lt < t_und - 0.06:
                place(layer, broll_card("brain", SRC_LEGEND + lt, 400, 300, live=False, accent=ORANGE), 820, 300, lt, t_nt,
                      exit_at=t_und - 0.06, **entrance(6))
            else:
                front_gif(gif_card("magnify", max(0, lt - t_und), w=400, frame="round"), 820, 300, lt, t_und, **entrance(7))
                light_hit(layer, 820, 300 + PACK_DY, lt, t_und, ORANGE)
            if lt >= t_evt:
                place(layer, chip("how everything works", NEON), 820, 500, lt, t_evt, frm="down")

    elif name == "click":
        draw_code_rain(layer, lt, n=10, col=CYAN)
        ticker(layer, "  CLICK AROUND  ·  AUTOMATIONS LIVE  ·  SKILLS  ·  AGENTS  ·  INTERACTIVE  ·  ", 700, lt, speed=170, fill=CYAN + (100,))
        t_click, t_int, t_aut, t_live, t_sk, t_ag, t_blah, t_helps = (r(T_CLICK), r(T_INTERACTIVE), r(T_AUTOS), r(T_LIVE),
                                                                       r(T_SKILLS), r(T_AGENTS), r(T_BLAH), r(T_HELPS))
        # b-roll windows cut on the spoken word: full graph -> automations filter -> skills -> personas
        if lt < t_aut:
            src, lab = SRC_CLICK + lt, "click around the live graph"
        elif lt < t_sk:
            src, lab = SRC_AUTOS + (lt - t_aut), "filter: automations that are live"
        elif lt < t_ag:
            src, lab = SRC_SKILLS + (lt - t_sk), "filter: skills"
        else:
            src, lab = SRC_AGENTS + (lt - t_ag), "filter: agents and personas"
        if lt < t_aut - 0.06:
            place(layer, big_text_card("CLICK AROUND, INTERACTIVE", CYAN, fsz=46, w=960, h=110),
                  540, 32, lt, -0.35, dur=0.01, scale_pop=True, exit_at=t_aut - 0.06)
        else:
            place(layer, big_text_card("WHAT IS LIVE, RIGHT NOW", NEON, fsz=48, w=960, h=110),
                  540, 32, lt, t_aut, scale_pop=True)
            light_hit(layer, 540, 32 + PACK_DY, lt, t_aut, NEON)
        place(layer, broll_card("graph", src, 1000, 480, accent=CYAN, label=lab), 540, 330, lt, -0.3, dur=0.01)
        if lt >= t_aut:
            place(layer, chip("automations", NEON), 200, 140, lt, t_aut, frm="left", idle=0)
        if lt >= t_sk:
            place(layer, chip("skills", PURPLE), 400, 140, lt, t_sk, frm="down", idle=0)
            light_hit(layer, 400, 140 + PACK_DY, lt, t_sk, PURPLE)
        if lt >= t_ag:
            place(layer, chip("agents", ORANGE), 570, 140, lt, t_ag, frm="right", idle=0)
        if lt >= t_blah:
            place(layer, chip("blah blah blah", STEEL), 790, 140, lt, t_blah, frm="right", idle=0)
        if lt >= t_helps:
            place(layer, stamp_card("HELPS A LOT", NEON, fsz=64, w=460, h=130), 300, 300, lt, t_helps, dur=0.2, tilt=8,
                  scale_pop=True, idle=0)
            light_hit(layer, 300, 300 + PACK_DY, lt, t_helps, NEON)

    else:  # cta
        draw_code_rain(layer, lt, n=10, col=NEON)
        layer.alpha_composite(ghost_img("NEXUS", 120), (-60 + gsl, 0))
        ticker(layer, "  COMMENT NEXUS  ·  GITNEXUS PROJECT + MY TUTORIAL  ·  I'LL SHOOT IT OVER  ·  ", 700, lt, speed=165, fill=NEON + (90,))
        t_git, t_tut, t_com, t_nex = r(T_GIT3), r(T_TUTORIAL), r(T_COMMENT), r(T_NEXUS2)
        if lt < t_com - 0.06:
            place(layer, big_text_card("WANT THE PROJECT + TUTORIAL", PURPLE, fsz=46, w=960, h=110),
                  540, 32, lt, -0.35, dur=0.01, scale_pop=True, exit_at=t_com - 0.06)
            place(layer, gn_hero(340), 300, 300, lt, -0.3, dur=0.01, idle=0, exit_at=t_com - 0.06)
            place(layer, repo_card(w=440, h=230), 790, 290, lt, t_git, frm="right", exit_at=t_com - 0.06)
            if lt >= t_tut:
                place(layer, chip("plus my tutorial", ORANGE), 790, 480, lt, t_tut, frm="down", exit_at=t_com - 0.06)
        else:
            place(layer, big_text_card("COMMENT  NEXUS", NEON, fsz=64, w=960, h=140),
                  540, 40, lt, t_com, scale_pop=True)
            light_hit(layer, 540, 40 + PACK_DY, lt, t_com, NEON)
            light_rays(layer, 540, 40 + PACK_DY, lt, NEON)
            place(layer, chip("I'll shoot that over", ORANGE), 220, 210, lt, t_com + 0.3, frm="left")
            place(layer, broll_card("graph", SRC_CTA + lt, 360, 180, live=False, accent=NEON, dim=40), 620, 270, lt, t_com + 0.15,
                  frm="down")
            place(layer, gn_hero(260), 300, 470, lt, t_com + 0.1, frm="left", scale_pop=True, idle=0)
            ix = 640 + 10 * math.sin(lt * 1.8)
            iy = 480 + PACK_DY + 6 * math.sin(lt * 2.1)
            bloom_orb(layer, ix, iy, 100, NEON, a=55)
            place_claude_invader(
                layer, ix, iy, lt, size=220,
                look_at=(540, 40 + PACK_DY),
                grab="right", grab_at=(ix - 80, iy - 30), grab_t=min(1.0, max(0.0, (lt - t_nex) / 0.5)),
                hold=HOLD if lt > t_nex + 0.3 else None,
            )
            front_gif(gif_card("lets-go", max(0, lt - t_com), w=280, frame="round"),
                      900, 470, lt, t_com + 0.2, frm="right", tilt=4)


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
PUNCH_T = punch_beats(words, ["nexus", "graph", "powerful", "live", "comment"])
BEATS = number_beats(words)
HANDLED = {1.58}  # "one tool" is not a counter beat
CUT_T = [a for _, a, _ in SECT[1:]]
HIT_T = CUT_T + [T_NEXUS, T_KNOW, T_POWERFUL, T_AUTOS, T_COMMENT]
WHIP_T, HF_T = CUT_T[::2], CUT_T[1::2]
for _b in BEATS:
    print(f"number beat {_b['t']:.2f}s {_b['raw']!r}")
print("punches", [round(p, 2) for p in PUNCH_T])

os.makedirs("frames/out5", exist_ok=True)
PREVIEW = os.environ.get("PREVIEW")
if PREVIEW:
    times = [0.00, 2.40, 3.60, 4.40, 5.00, 5.70, 6.30]
    todo = [int(round(tt * FPS)) for tt in times]
else:
    todo = list(range(N))
    if os.environ.get("RANGE"):
        _a, _b = os.environ["RANGE"].split(":")
        todo = list(range(int(_a), int(_b)))

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
        col = (KEY_COL.get(wd, ORANGE) + (255,)) if key else (255, 255, 255, 255)
        shcol = (0, 0, 0, 190)
        ons = next((aa for ww, aa, bb2 in words if ww.strip().rstrip(".,!?").lower() == wd and aa <= t <= bb2 + 0.1), t)
        fs = int(66 * caption_impact(t, ons, key))
        cf = F(CAP, fs)  # Luckiest Guy caps (Kevin 2026-09-19)
        tw = d.textlength(wd, font=cf)
        x = (W - tw) / 2
        y = BAND_Y - 8 - 7 - 3  # stroke bottom rests on top of the accent line
        if key:
            caption_bloom(frame, x, y - fs, tw, fs, KEY_COL.get(wd, NEON))
        d.text((x, y), wd, font=cf, fill=col, anchor="ls", stroke_width=7, stroke_fill=(0, 0, 0, 255))

    frame.convert("RGB").save(f"frames/out5/f{n:05d}.jpg", quality=95)
    if PREVIEW:
        print(f"preview {n}/{N} t={t:.2f} {name}", flush=True)
    elif n % 60 == 0:
        print(f"{n}/{N}", flush=True)

band_cap.release()
print("frames done", len(todo), flush=True)
