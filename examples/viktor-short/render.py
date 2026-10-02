#!/usr/bin/env python3
"""VIKTOR short (Kevin 2026-09-26): split animated talking head on the gitnexus-animated compositor.
Story: biggest AI-agency headache = big teams on different AIs -> extra work -> VIKTOR puts everything in one place,
every employee on the same agent -> operator can take massive companies -> comment AGENCY for the tutorial."""
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
    ease_back_out,
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
    logo_mark,
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
        "viktor", "slack", "agent", "memory", "team", "notion", "hubspot", "sync",
        "client", "onboard", "gpt", "claude", "task ✓", "#ops",
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


def whisper_line(text, p, w=960, h=64):
    shown = typewriter(text, p, cursor=True)

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((w / 2, h / 2), shown, font=F(AR, 34), fill=SILVER + (230,), anchor="mm")
        return img
    return cached(("whisper2", shown, w, h), build)



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



# ───────────────────────────── VIKTOR short: sections, anchors, cards, scene ─────────────────────────────
VIK = (120, 92, 255)      # VIKTOR indigo (from the logo)
WHITE = (255, 252, 248)
WHITE_TILE = (255, 252, 248, 255)

BGS = {
    "hook": textured_bg((52, 42, 46), 7, RED),
    "bigbiz": textured_bg((42, 48, 58), 11, CYAN),
    "chaos": textured_bg((52, 46, 44), 13, ORANGE),
    "work": textured_bg((54, 42, 46), 15, RED),
    "viktor": textured_bg((44, 42, 62), 17, VIK),
    "team": textured_bg((42, 48, 60), 19, CYAN),
    "operator": textured_bg((42, 52, 48), 21, NEON),
    "cta": textured_bg((46, 42, 62), 25, VIK),
}

SECT = [
    ("hook", 0.00, 3.40),
    ("bigbiz", 3.40, 6.66),
    ("chaos", 6.66, 13.50),
    ("work", 13.50, 16.20),
    ("viktor", 16.20, 20.40),
    ("team", 20.40, 24.50),
    ("operator", 24.50, 30.55),
    ("cta", 30.55, DUR),
]
SECT_ACCENT = {
    "hook": RED, "bigbiz": CYAN, "chaos": ORANGE, "work": RED, "viktor": VIK, "team": CYAN,
    "operator": NEON, "cta": VIK,
}
KEY_COL = {
    "biggest": RED, "headache": RED, "ai": VIK, "agency": VIK, "career": VIK,
    "big": CYAN, "businesses": CYAN, "recently": CYAN,
    "gpt": NEON, "claude": ORANGE, "won't": RED, "know": RED,
    "extra": RED, "work": RED,
    "tool": VIK, "viktor": VIK, "literally": ORANGE, "everything": VIK, "one": VIK, "place": VIK,
    "every": CYAN, "single": CYAN, "employee": CYAN, "team": CYAN, "same": CYAN, "agent": CYAN,
    "operator": NEON, "massive": NEON, "companies": NEON,
    "full": ORANGE, "tutorial": ORANGE, "youtube": RED, "comment": NEON,
}
KEYWORDS = set(KEY_COL)


def tabs(word, after):
    ons = word_onset(words, word, after=after)
    return ons if ons is not None else after


T_HEADACHE = tabs("headache", 1.0)
T_AGENCY = tabs("agency", 2.2)
T_BIG = tabs("big", 4.8)
T_BUSINESSES = tabs("businesses", 5.0)
T_RECENTLY = tabs("recently", 6.0)
T_ONE = tabs("one", 7.0)
T_GPT = tabs("gpt", 8.4)
T_CLAUDE = tabs("claude", 9.9)
T_ANOTHER = tabs("another", 10.3)
T_WONT = tabs("won't", 11.3)
T_HEADACHE2 = tabs("headache", 14.7)
T_EXTRA = tabs("extra", 15.1)
T_TOOL = tabs("tool", 16.5)
T_VIKTOR = tabs("viktor", 17.0)
T_EVERYTHING = tabs("everything", 18.0)
T_ONEPLACE = tabs("one", 19.3)
T_EVERY = tabs("every", 20.5)
T_EMPLOYEE = tabs("employee", 21.4)
T_ACCESS = tabs("accessing", 23.0)
T_AGENT = tabs("agent", 24.0)
T_OPERATOR = tabs("operator", 26.4)
T_ABLE = tabs("able", 28.3)
T_MASSIVE = tabs("massive", 29.3)
T_TUTORIAL = tabs("tutorial", 31.9)
T_YOUTUBE = tabs("youtube", 32.5)
T_COMMENT = tabs("comment", 33.1)
T_AGENCY_CTA = tabs("agency", 33.3)


def tile(slug, size=150):
    return logo_badge(slug, size, punch=False, fill=WHITE_TILE)


def vik_badge(size=300):
    def build():
        im = Image.open("assets/logos/viktor.png").convert("RGBA").resize((size, size), Image.LANCZOS)
        card = Image.new("RGBA", (size + 60, size + 60), (0, 0, 0, 0))
        sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([30, 44, 30 + size, 44 + size], int(size * 0.22), fill=(0, 0, 0, 120))
        card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(12)))
        card.alpha_composite(im, (30, 30))
        return card
    return cached(("vikbadge", size), build)


def big_word(txt, col, fsz=200):
    """Giant display word sized from the real glyph bbox."""
    def build():
        f = F(AR, fsz)
        d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        x0, y0, x1, y1 = d0.textbbox((0, 0), txt, font=f)
        img = Image.new("RGBA", (x1 - x0 + 40, y1 - y0 + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((20 - x0 + 6, 20 - y0 + 6), txt, font=f, fill=(0, 0, 0, 170))
        d.text((20 - x0, 20 - y0), txt, font=f, fill=col + (255,))
        return img
    return cached(("bigword", txt, col, fsz), build)


def avatar(initial, col, size=110):
    def build():
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse([0, 0, size - 1, size - 1], fill=col + (255,), outline=INK + (255,), width=4)
        d.text((size / 2, size / 2), initial, font=F(AR, int(size * 0.5)), fill=INK + (255,), anchor="mm")
        return im
    return cached(("avatar", initial, col, size), build)


def person_card(label, col, logo=None, note="", w=300, h=340):
    def build():
        card = shadow_card((w, h), 24, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        card.alpha_composite(avatar(label[0], col, 110), (pad + w // 2 - 55, pad + 24))
        d.text((pad + w / 2, pad + 164), label, font=F(AR, 32), fill=WHITE + (255,), anchor="mm")
        if logo is not None:
            card.alpha_composite(logo, (int(pad + w / 2 - logo.width / 2), pad + 196))
        else:
            d.text((pad + w / 2, pad + 250), note, font=F(AR, 28), fill=col + (255,), anchor="mm")
        d.rectangle([pad, pad + 10, pad + 8, pad + h - 10], fill=col + (255,))
        return card
    return cached(("person", label, col, id(logo), note, w, h), build)


def building(col, size=120):
    def build():
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([14, 6, size - 14, size - 4], 10, fill=GRAPHITE + (255,), outline=col + (255,), width=4)
        for rr in range(4):
            for c in range(3):
                x = 28 + c * (size - 56) / 2.4
                y = 20 + rr * 22
                d.rectangle([x, y, x + 13, y + 11], fill=col + (210,))
        return im
    return cached(("bldg", col, size), build)


def terminal(lt, lines, title="AGENT", w=560, h=300, accent=CYAN):
    shown = []
    for t0, txt, col in lines:
        if lt >= t0:
            shown.append((typewriter(txt, clamp01((lt - t0) / 0.35), cursor=False), col))
    key = tuple(shown)

    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad, pad, pad + w, pad + 50], 22, fill=INK + (255,))
        d.rectangle([pad, pad + 28, pad + w, pad + 50], fill=INK + (255,))
        for i, col in enumerate([RED, ORANGE, NEON]):
            d.ellipse([pad + 20 + i * 28, pad + 16, pad + 36 + i * 28, pad + 32], fill=col + (255,))
        d.text((pad + 118, pad + 11), title, font=F(AR, 24), fill=accent + (255,))
        y = pad + 70
        for txt, col in shown:
            d.text((pad + 22, y), txt, font=MONO, fill=col + (255,))
            y += 38
        return card
    return cached(("term", key, title, w, h, accent), build)


def chat_card(lt, msgs, w=620, h=360, title="# team-ops"):
    shown = tuple(i for i, m in enumerate(msgs) if lt >= m[0])

    def build():
        card = shadow_card((w, h), 24, (26, 28, 34, 255))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad, pad, pad + w, pad + 60], 24, fill=INK + (255,))
        d.rectangle([pad, pad + 34, pad + w, pad + 60], fill=INK + (255,))
        sl = logo_mark("slack", 36, punch=False)
        if sl is not None:
            card.alpha_composite(sl, (pad + 18, pad + 12))
        d.text((pad + 66, pad + 30), title, font=F(AR, 28), fill=WHITE + (255,), anchor="lm")
        y = pad + 80
        for i in shown[-3:]:
            _t0, who, col, text, bot = msgs[i]
            if bot:
                vb = logo_mark("viktor", 52, punch=False)
                card.alpha_composite(vb, (pad + 18, y))
            else:
                card.alpha_composite(avatar(who[0], col, 52), (pad + 18, y))
            d.text((pad + 86, y), who, font=F(AR, 24), fill=(VIK if bot else col) + (255,))
            d.text((pad + 86, y + 32), text, font=MONO_S, fill=SILVER + (255,))
            y += 88
        return card
    return cached(("chat", shown, w, h, title), build)


def yt_card(w=460, h=300):
    """Faux YouTube tutorial tile: VIKTOR thumb + play badge + title bar."""
    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        th = h - 70
        d.rounded_rectangle([pad, pad, pad + w, pad + th], 22, fill=(30, 24, 60, 255))
        vb = logo_mark("viktor", int(th * 0.62), punch=False)
        card.alpha_composite(vb, (pad + 30, pad + (th - vb.height) // 2))
        d.text((pad + 60 + vb.width, pad + th / 2 - 36), "FULL", font=F(AR, 52), fill=WHITE + (255,))
        d.text((pad + 60 + vb.width, pad + th / 2 + 18), "TUTORIAL", font=F(AR, 52), fill=ORANGE + (255,))
        yt = logo_mark("youtube", 70, punch=False)
        card.alpha_composite(yt, (pad + w - 90, pad + th - 60))
        d.text((pad + 20, pad + th + 18), "VIKTOR for AI agencies  ·  full walkthrough", font=F(AR, 24), fill=SILVER + (255,))
        return card
    return cached(("yt", w, h), build)


def dashed(layer, x0, y0, x1, y1, col, seg=18, gap=12, width=6):
    d = ImageDraw.Draw(layer)
    L = math.hypot(x1 - x0, y1 - y0)
    k = 0.0
    while k < L:
        a0, a1 = k / L, min(L, k + seg) / L
        d.line([x0 + (x1 - x0) * a0, y0 + (y1 - y0) * a0, x0 + (x1 - x0) * a1, y0 + (y1 - y0) * a1], fill=col + (230,), width=width)
        k += seg + gap


TOPIC = [b for b in (tile(s, 120) for s in ("slack", "notion", "gmail", "hubspot", "gdrive", "salesforce", "zapier", "openai"))
         if b is not None]
AI_MARKS = [b for b in (tile(s, 120) for s in ("openai", "claude-sphinx", "gemini", "slack", "notion")) if b is not None]


def scene(layer, name, lt, t, a):
    gsl = int(30 * math.sin(lt * 0.6))
    r = lambda T: max(0.0, T - 0.08 - a)  # noqa: E731

    if name == "hook":
        # billboard from frame 0: three giant AIs pulling apart + the problem title
        draw_code_rain(layer, lt, n=12, col=RED)
        ticker(layer, "  MY AI AGENCY  ·  BIG BUSINESSES  ·  EVERYONE ON A DIFFERENT AI  ·  ", 700, lt, speed=170, fill=RED + (100,))
        th, tag = r(T_HEADACHE), r(T_AGENCY)
        place(layer, big_text_card("THE BIGGEST HEADACHE", RED, fsz=62, w=960, h=130), 540, 32, lt, -0.4, dur=0.01, scale_pop=True)
        if lt < th - 0.06:
            place(layer, tile("openai", 250), 220, 250, lt, -0.4, dur=0.01, tilt=-8, idle=0)
            place(layer, tile("claude-sphinx", 250), 540, 230, lt, -0.4, dur=0.01, idle=0)
            place(layer, tile("gemini", 250), 860, 250, lt, -0.4, dur=0.01, tilt=8, idle=0)
            for x0, x1 in ((340, 420), (660, 740)):
                dashed(layer, x0, 240 + PACK_DY, x1, 240 + PACK_DY, RED)
        else:
            front_gif(gif_card("headache", max(0, lt - th), w=560, frame="round"), 360, 300, lt, th, **entrance(2))
            light_hit(layer, 360, 300 + PACK_DY, lt, th, RED)
            place(layer, tile("openai", 170), 860, 170, lt, th, dur=0.2, tilt=8, idle=0, frm="right")
            place(layer, tile("claude-sphinx", 170), 860, 360, lt, th + 0.08, dur=0.2, tilt=-6, idle=0, frm="right")
            if lt >= tag:
                place(layer, chip("in my AI agency career", VIK), 800, 510, lt, tag, frm="down")
                light_hit(layer, 800, 510 + PACK_DY, lt, tag, VIK)

    elif name == "bigbiz":
        draw_code_rain(layer, lt, n=12, col=CYAN)
        layer.alpha_composite(ghost_img("BIG BUSINESS", 110), (-60 + gsl, 0))
        ticker(layer, "  WORKING WITH BIG BUSINESSES  ·  UP UNTIL RECENTLY  ·  ", 700, lt, speed=170, fill=CYAN + (100,))
        tb, tbz, trc = r(T_BIG), r(T_BUSINESSES), r(T_RECENTLY)
        place(layer, big_text_card("WORKING WITH BIG BUSINESSES", CYAN, fsz=52, w=960, h=120), 540, 32, lt, -0.35, dur=0.01,
              scale_pop=True)
        place(layer, terminal(lt + 0.4, [(0.0, "$ onboard client --size enterprise", SILVER), (0.6, "! 300+ employees", ORANGE),
                                         (1.2, "! 9 different tools", ORANGE), (1.8, "! 0 shared setup", RED)],
                              title="NEW CLIENT", w=520, h=250, accent=CYAN), 300, 260, lt, -0.3, dur=0.01, frm="left")
        n_b = 0 if lt < tbz else min(6, 1 + int((lt - tbz) / 0.09))
        for k in range(n_b):
            x = 700 + (k % 3) * 130
            y = 200 + (k // 3) * 140
            place(layer, building(CYAN, 124), x, y, lt, tbz + k * 0.09, dur=0.18, scale_pop=True, idle=0)
        if lt >= tb:
            light_hit(layer, 830, 270 + PACK_DY, lt, tb, CYAN)
        place(layer, tile("salesforce", 130), 700, 470, lt, tb + 0.1, frm="up", idle=0)
        place(layer, tile("hubspot", 130), 860, 470, lt, tb + 0.2, frm="up", idle=0)
        if lt >= trc:
            place(layer, stamp_card("UNTIL RECENTLY", CYAN, fsz=58, w=520, h=130), 320, 490, lt, trc, dur=0.2, tilt=-6,
                  scale_pop=True, idle=0)
            light_hit(layer, 320, 490 + PACK_DY, lt, trc, CYAN)

    elif name == "chaos":
        draw_code_rain(layer, lt, n=12, col=ORANGE)
        ticker(layer, "  ONE USES GPT  ·  ONE USES CLAUDE  ·  ONE WON'T EVEN KNOW HOW TO USE AI  ·  ", 700, lt, speed=170,
               fill=ORANGE + (100,))
        tg, tc, tw = r(T_GPT), r(T_CLAUDE), r(T_WONT)
        place(layer, big_text_card("EVERY PERSON, A DIFFERENT AI", ORANGE, fsz=50, w=960, h=120), 540, 32, lt, -0.35, dur=0.01,
              scale_pop=True)
        xs = (190, 540, 890)
        cards = [
            person_card("ALEX", NEON, tile("openai", 96) if lt >= tg else None, "uses..."),
            person_card("SAM", ORANGE, tile("claude-sphinx", 96) if lt >= tc else None, "uses..."),
            person_card("JORDAN", RED, None, "no AI at all" if lt >= tw else "..."),
        ]
        for k, c in enumerate(cards):
            place(layer, c, xs[k], 300, lt, -0.35 + k * 0.08, dur=0.25, frm=("left", "up", "right")[k], idle=0,
                  exit_at=(tw - 0.06) if k == 2 else None)
        if lt >= tg:
            light_hit(layer, xs[0], 300 + PACK_DY, lt, tg, NEON)
            place(layer, chip("GPT", NEON), xs[0], 520, lt, tg, frm="down")
        if lt >= tc:
            light_hit(layer, xs[1], 300 + PACK_DY, lt, tc, ORANGE)
            ix = xs[1] + 8 * math.sin(lt * 2.0)
            place(layer, chip("Claude", ORANGE), xs[1] + 70, 520, lt, tc, frm="down")
            place_claude_invader(layer, ix - 70, 520 + PACK_DY, lt, size=110, look_at=(xs[2], 300 + PACK_DY))
        if lt >= tw:
            front_gif(gif_card("confused", max(0, lt - tw), w=300, frame="round"), xs[2], 310, lt, tw, **entrance(3))
            light_hit(layer, xs[2], 280 + PACK_DY, lt, tw, RED)
            place(layer, strike_chip("knows how to use AI", RED), xs[2] - 60, 520, lt, tw + 0.15, frm="down")
        if lt >= tc + 0.4:
            dashed(layer, xs[0] + 150, 300 + PACK_DY, xs[1] - 150, 300 + PACK_DY, RED)
            dashed(layer, xs[1] + 150, 300 + PACK_DY, xs[2] - 150, 300 + PACK_DY, RED)

    elif name == "work":
        draw_code_rain(layer, lt, n=12, col=RED)
        layer.alpha_composite(ghost_img("EXTRA WORK", 110), (-60 + gsl, 0))
        ticker(layer, "  A LOT OF HEADACHE  ·  EXTRA WORK FOR ME  ·  ", 700, lt, speed=170, fill=RED + (100,))
        th, te = r(T_HEADACHE2), r(T_EXTRA)
        place(layer, big_text_card("HEADACHE + EXTRA WORK", RED, fsz=56, w=960, h=124), 540, 32, lt, -0.35, dur=0.01,
              scale_pop=True)
        front_gif(gif_card("stressed", max(0, lt), w=500, frame="round"), 320, 300, lt, -0.3, dur=0.01, **entrance(5))
        lines = [(0.0, "! sync GPT notes -> Claude", ORANGE), (0.5, "! re-explain client context", ORANGE),
                 (1.0, "! train the non-AI person", RED), (1.5, "! 3 setups, 0 memory", RED)]
        place(layer, terminal(lt, lines, title="MY TODO", w=440, h=260, accent=RED), 800, 260, lt, -0.3, dur=0.01, frm="right")
        if lt >= th:
            light_hit(layer, 800, 260 + PACK_DY, lt, th, RED)
        if lt >= te:
            place(layer, stamp_card("EXTRA WORK", RED, fsz=64, w=440, h=130), 780, 500, lt, te, dur=0.2, tilt=7,
                  scale_pop=True, idle=0)
            light_hit(layer, 780, 500 + PACK_DY, lt, te, RED)

    elif name == "viktor":
        draw_code_rain(layer, lt, n=16, col=VIK)
        layer.alpha_composite(ghost_img("VIKTOR", 130), (-60 + gsl, 0))
        ticker(layer, "  VIKTOR  ·  EVERYTHING IN ONE PLACE  ·  ONE AGENT FOR THE WHOLE TEAM  ·  ", 700, lt, speed=170,
               fill=VIK + (110,))
        tt, tv, tev, top = r(T_TOOL), r(T_VIKTOR), r(T_EVERYTHING), r(T_ONEPLACE)
        if lt < tv:
            place(layer, whisper_line("but with this tool called...", clamp01(lt / 0.8)), 540, 300, lt, -0.3, dur=0.01)
            sil = vik_badge(320).copy()
            sil.putalpha(sil.split()[3].point(lambda v: int(v * 0.25)))
            place(layer, sil, 540, 150, lt, -0.3, dur=0.01, idle=0)
        else:
            cx, cy = 300, 250
            bloom_orb(layer, cx, cy + PACK_DY, 240, VIK, a=80)
            place(layer, vik_badge(380), cx, cy, lt, tv, dur=0.22, scale_pop=True, idle=0)
            light_hit(layer, cx, cy + PACK_DY, lt, tv, VIK)
            light_rays(layer, cx, cy + PACK_DY, lt, VIK)
            place(layer, big_word("VIKTOR", WHITE, 150), 780, 170, lt, tv + 0.06, dur=0.25, frm="right", scale_pop=True, idle=0)
            if lt >= tev:
                # every tool flies into the one hub
                slugs = ["slack", "notion", "gmail", "hubspot", "gdrive", "openai"]
                for k, s in enumerate(slugs):
                    p = clamp01((lt - tev - k * 0.08) / 0.5)
                    if p <= 0:
                        continue
                    ang = -math.pi / 2 + k * (2 * math.pi / len(slugs))
                    sx, sy = 780 + 230 * math.cos(ang), 380 + 120 * math.sin(ang)
                    x = sx + (cx - sx) * ease_back_out(p) * 0.55
                    y = sy + (cy - sy) * ease_back_out(p) * 0.55
                    d = ImageDraw.Draw(layer)
                    d.line([cx, cy + PACK_DY, x, y + PACK_DY], fill=VIK + (160,), width=4)
                    place(layer, tile(s, 110), x, y, lt, tev + k * 0.08, dur=0.15, idle=0)
            if lt >= top:
                place(layer, stamp_card("ONE PLACE", VIK, fsz=70, w=440, h=140), 780, 520, lt, top, dur=0.2, tilt=-6,
                      scale_pop=True, idle=0)
                light_hit(layer, 780, 520 + PACK_DY, lt, top, VIK)

    elif name == "team":
        draw_code_rain(layer, lt, n=12, col=CYAN)
        ticker(layer, "  EVERY SINGLE EMPLOYEE  ·  THE SAME AGENT  ·  RIGHT IN SLACK  ·  ", 700, lt, speed=170, fill=CYAN + (100,))
        te, tem, tac, tag = r(T_EVERY), r(T_EMPLOYEE), r(T_ACCESS), r(T_AGENT)
        place(layer, big_text_card("EVERY EMPLOYEE, SAME AGENT", CYAN, fsz=52, w=960, h=120), 540, 32, lt, -0.35, dur=0.01,
              scale_pop=True)
        cx, cy = 270, 300
        cols = (ORANGE, NEON, PINK, CYAN, SILVER, RED)
        d = ImageDraw.Draw(layer)
        for k in range(6):
            ang = -math.pi / 2 + k * (2 * math.pi / 6)
            x, y = cx + 190 * math.cos(ang), cy + 170 * math.sin(ang)
            if lt >= te + k * 0.1:
                d.line([cx, cy + PACK_DY, x, y + PACK_DY], fill=CYAN + (190,), width=5)
            place(layer, avatar("ABCDEF"[k], cols[k], 96), x, y, lt, -0.3 + k * 0.04, dur=0.2, idle=3)
        place(layer, vik_badge(150), cx, cy, lt, -0.3, dur=0.01, idle=0)
        if lt >= te:
            light_hit(layer, cx, cy + PACK_DY, lt, te, CYAN)
        msgs = [(0.0, "Sarah", PINK, "@Viktor draft the launch posts", False),
                (0.9, "Viktor", VIK, "Done. In Notion + scheduled", True),
                (1.8, "Mike", ORANGE, "@Viktor update the HubSpot deal", False)]
        place(layer, chat_card(lt - tem + 0.3, msgs, w=520, h=330), 780, 280, lt, tem - 0.3, dur=0.25, frm="right")
        if lt >= tag:
            place(layer, stamp_card("SAME AGENT", CYAN, fsz=60, w=440, h=130), 760, 530, lt, tag, dur=0.2, tilt=6,
                  scale_pop=True, idle=0)
            light_hit(layer, 760, 530 + PACK_DY, lt, tag, CYAN)

    elif name == "operator":
        draw_code_rain(layer, lt, n=12, col=NEON)
        layer.alpha_composite(ghost_img("MASSIVE", 120), (-60 + gsl, 0))
        ticker(layer, "  AI AGENCY OPERATOR  ·  NOW ABLE TO WORK WITH MASSIVE COMPANIES  ·  ", 700, lt, speed=170,
               fill=NEON + (100,))
        top, tab, tm = r(T_OPERATOR), r(T_ABLE), r(T_MASSIVE)
        if lt < tm - 0.06:
            place(layer, big_text_card("ME, THE AI AGENCY OPERATOR", NEON, fsz=50, w=960, h=120), 540, 32, lt, -0.35,
                  dur=0.01, scale_pop=True, exit_at=tm - 0.06)
            place(layer, avatar("K", NEON, 220), 250, 270, lt, -0.3, dur=0.01, idle=0, exit_at=tm - 0.06)
            place(layer, chip("1 operator", NEON), 250, 440, lt, top, frm="down", exit_at=tm - 0.06)
            if lt >= top:
                light_hit(layer, 250, 270 + PACK_DY, lt, top, NEON)
            lines = [(0.0, "$ viktor onboard acme-co", SILVER), (0.5, "✓ slack connected", NEON),
                     (1.0, "✓ 14 tools synced", NEON), (1.5, "✓ team live on one agent", NEON)]
            place(layer, terminal(lt - max(0, tab - 1.2), lines, title="VIKTOR", w=540, h=250, accent=NEON), 740, 270, lt,
                  -0.3, dur=0.01, frm="right", exit_at=tm - 0.06)
        else:
            place(layer, big_text_card("MASSIVE COMPANIES", NEON, fsz=64, w=960, h=136), 540, 36, lt, tm, scale_pop=True)
            light_hit(layer, 540, 36 + PACK_DY, lt, tm, NEON)
            light_rays(layer, 540, 36 + PACK_DY, lt, NEON)
            front_gif(gif_card("money", max(0, lt - tm), w=520, frame="round"), 320, 300, lt, tm + 0.05, **entrance(6))
            for k in range(6):
                x = 700 + (k % 3) * 130
                y = 230 + (k // 3) * 150
                place(layer, building(NEON, 130), x, y, lt, tm + 0.1 + k * 0.06, dur=0.18, scale_pop=True, idle=0)
        guarded_conveyor(layer, 500 + PACK_DY, lt, TOPIC, conveyor_marks, name="topic-op", speed=180, gap=22) if lt < tm - 0.06 else None

    else:  # cta
        draw_code_rain(layer, lt, n=12, col=VIK)
        layer.alpha_composite(ghost_img("AGENCY", 130), (-60 + gsl, 0))
        ticker(layer, "  FULL VIKTOR TUTORIAL ON YOUTUBE  ·  COMMENT AGENCY  ·  I'LL SEND IT OUT  ·  ", 700, lt, speed=165,
               fill=VIK + (100,))
        tt, ty, tc = r(T_TUTORIAL), r(T_YOUTUBE), r(T_COMMENT)
        if lt < tc - 0.06:
            place(layer, big_text_card("I FILMED THE FULL TUTORIAL", ORANGE, fsz=52, w=960, h=120), 540, 32, lt, -0.35,
                  dur=0.01, scale_pop=True, exit_at=tc - 0.06)
            place(layer, yt_card(620, 330), 540, 300, lt, tt - 0.2, dur=0.25, scale_pop=True, exit_at=tc - 0.06)
            if lt >= ty:
                place(layer, tile("youtube", 150), 900, 460, lt, ty, dur=0.2, scale_pop=True, idle=0, exit_at=tc - 0.06)
                light_hit(layer, 900, 460 + PACK_DY, lt, ty, RED)
            place(layer, vik_badge(150), 170, 460, lt, -0.3, dur=0.01, idle=0, exit_at=tc - 0.06)
        else:
            place(layer, big_text_card("COMMENT  AGENCY", NEON, fsz=76, w=960, h=160), 540, 50, lt, tc, scale_pop=True)
            light_hit(layer, 540, 50 + PACK_DY, lt, tc, NEON)
            light_rays(layer, 540, 50 + PACK_DY, lt, NEON)
            place(layer, chip("I'll send the tutorial out", ORANGE), 300, 230, lt, tc + 0.25, frm="left")
            place(layer, vik_badge(230), 300, 420, lt, tc + 0.1, frm="left", scale_pop=True, idle=0)
            front_gif(gif_card("letsgo", max(0, lt - tc), w=440, frame="round"), 770, 360, lt, tc + 0.15, **entrance(0))


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
PUNCH_T = [T_HEADACHE, T_VIKTOR, T_MASSIVE]  # one hero punch per act, >=8 s apart
BEATS = number_beats(words)
HANDLED = {b["t"] for b in number_beats(words)}  # no real numbers in this one
CUT_T = [a for _, a, _ in SECT[1:]]
HIT_T = CUT_T + [T_HEADACHE, T_VIKTOR, T_MASSIVE, T_COMMENT]
WHIP_T, HF_T = CUT_T[::2], CUT_T[1::2]
for _b in BEATS:
    print(f"number beat {_b['t']:.2f}s {_b['raw']!r}")
print("punches", [round(p, 2) for p in PUNCH_T])

os.makedirs("frames/out5", exist_ok=True)
PREVIEW = os.environ.get("PREVIEW")
if PREVIEW:
    times = [float(x) for x in PREVIEW.split(",")]
    todo = [int(round(tt * FPS)) for tt in times]
else:
    todo = list(range(N))
    if os.environ.get("RANGE"):
        _a, _b = os.environ["RANGE"].split(":")
        todo = list(range(int(_a), int(_b)))

if todo and not PREVIEW:
    band_cap.set(cv2.CAP_PROP_POS_FRAMES, todo[0])  # RANGE chunks must start the band at their own frame
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
