#!/usr/bin/env python3
"""Split animated talking-head: Claude Hunger Games (Kevin's /hunger-games skill).

1080x1920. Brainstorm hook -> custom gold crest + Effie GIF on the name -> /hunger-games terminal
(real plan: 100 tributes, 5 days, 471 sub-agent calls) -> Apple counter 100 -> arena grid spawning
in waves of 10 -> strategy trading cards (real card names from strategies.json) -> 5-way clash with
Gamemaker rubric (real weights) + cannon -> 100/40/16/8/4/1 elimination -> crowned victor -> CTA.
Embers rise through every section.
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
    highlight_sweep,
    punch_scale,
    punch_zoom,
    shake_offset,
    typewriter,
    whip_dir,
    whip_wipe,
)
from media_marks import gif_card, logo_badge, logo_mark, topic_marks  # noqa: E402
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
BLUE = (80, 170, 255)
CYAN = (56, 200, 248)
CORAL = ORANGE
PAPER = GRAPHITE
WHITE = (255, 252, 248)
TERM_BG = (27, 28, 32)
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


def trel(word, after=0.0):
    for w, a, b in words:
        if a >= after - 0.01 and w.strip().rstrip(".,!?").lower() == word:
            return a
    return after


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


# ───────────────────────────── cards ─────────────────────────────

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


def title_card(txt, accent=ORANGE, fsz=72, w=960, h=150, strike=0.0):
    k = int(strike * 20)

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 28, fill=GRAPHITE + (255,))
        d.rectangle([0, 0, 14, h], fill=accent + (255,))
        fnt = F(AR, fsz)
        d.text((w / 2 + 6, h / 2 - 2), txt, font=fnt, fill=WHITE + (255,), anchor="mm")
        if k:
            tw = d.textlength(txt, font=fnt)
            x0 = w / 2 + 6 - tw / 2 - 16
            x1 = x0 + (tw + 32) * (k / 20)
            d.line([(x0, h / 2 + 6), (x1, h / 2 - 6)], fill=RED + (255,), width=14)
        return img
    return cached(("title", txt, accent, fsz, w, h, k), build)


def stamp(txt, col=RED, fsz=64, pad=34):
    def build():
        fnt = F(AR, fsz)
        tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(txt, font=fnt))
        w, h = tw + pad * 2, fsz + 44
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 16, fill=INK + (200,), outline=col + (255,), width=8)
        d.rounded_rectangle([12, 12, w - 13, h - 13], 10, outline=col + (150,), width=2)
        d.text((w / 2, h / 2 - 2), txt, font=fnt, fill=col + (255,), anchor="mm")
        return img
    return cached(("stamp", txt, col, fsz), build)


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
            pc = pc.rotate(age * (180 if c > 1 else -160), expand=True, resample=Image.BICUBIC)
            x = int(cx - img.width / 2 + c * tw + math.cos(ang) * dist - pc.width / 2)
            y = int(cy - img.height / 2 + r * th + math.sin(ang) * dist - 40 * age - pc.height / 2)
            if -pc.width < x < W and -pc.height < y < AH:
                layer.alpha_composite(pc, (x, y))


def img_card(path, w, radius=22, ring=None):
    def build():
        im = Image.open(path).convert("RGBA")
        h = int(im.height * w / im.width)
        im = im.resize((w, h), Image.LANCZOS)
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=255)
        im.putalpha(mask)
        card = shadow_card((w + 12, h + 12), radius + 6, (ring or GRAPHITE) + (255,))
        card.alpha_composite(im, (32 + 6, 32 + 6))
        return card
    return cached(("imgcard", path, w, ring), build)


from media_marks import counter_card  # noqa: E402
from claude_marks import load_invader_sprite, skill_chip  # noqa: E402

GOLD = (255, 196, 64)
EMBER = (255, 104, 28)
BLOOD = (220, 30, 46)

T_BRAIN = trel("brainstorming")
T_CLAUDE1 = trel("claude")
T_BUILT = trel("built")
T_SKILL = trel("skill")
T_CALLED = trel("called")
T_CLAUDE2 = trel("claude", 3.3)
T_HUNGER = trel("hunger")
T_GAMES = trel("games")
T_IDEAS = trel("ideas")
T_FUN = trel("fun")
T_SO2 = trel("so", 6.6)
T_GIVE = trel("give")
T_IDEA = trel("idea", 7.9)
T_CREATE = trel("create")
T_A = trel("a", 9.3)
T_HUNDRED = trel("hundred")
T_CHARS = trel("characters")
T_ATTR = trel("attributes")
T_CENTERED = trel("centered")
T_AND = trel("and", 13.7)
T_BATTLE = trel("battle")
T_DEATH = trel("death")
T_UNTIL = trel("until")
T_EXACT = trel("exact")
T_WINNER = trel("winner")
T_ANSWER = trel("answer")
T_IF = trel("if", 22.5)
T_HUNGER2 = trel("hunger", 23.0)
T_COMMENT = trel("comment")
T_GAMES3 = trel("games", 24.6)

SECT = [
    ("hook", 0.00, T_CALLED),
    ("title", T_CALLED, T_SO2),
    ("idea", T_SO2, T_A),
    ("spawn", T_A, T_AND),
    ("battle", T_AND, T_UNTIL),
    ("days", T_UNTIL, T_WINNER - 0.06),
    ("victor", T_WINNER - 0.06, T_IF),
    ("cta", T_IF, DUR + 0.05),
]
KEYWORDS = {
    "brainstorming", "claude", "skill", "hunger", "games", "ideas", "fun", "idea", "create", "hundred",
    "characters", "attributes", "battle", "death", "exact", "winner", "answer", "comment", "agents",
}
KEY_COL = {
    "brainstorming": CYAN, "claude": ORANGE, "skill": NEON, "hunger": GOLD, "games": GOLD, "ideas": CYAN,
    "fun": NEON, "idea": CYAN, "create": NEON, "hundred": GOLD, "characters": ORANGE, "attributes": CYAN,
    "battle": RED, "death": RED, "exact": GOLD, "winner": GOLD, "answer": NEON, "comment": NEON, "agents": ORANGE,
}
SECT_ACCENT = {
    "hook": CYAN, "title": GOLD, "idea": CYAN, "spawn": GOLD, "battle": RED,
    "days": EMBER, "victor": GOLD, "cta": GOLD,
}

BGS = {
    "hook": textured_bg((34, 40, 52), 7, CYAN),
    "title": textured_bg((52, 40, 28), 11, GOLD),
    "idea": textured_bg((34, 40, 52), 13, CYAN),
    "spawn": textured_bg((50, 40, 30), 17, GOLD),
    "battle": textured_bg((54, 30, 32), 23, RED),
    "days": textured_bg((52, 34, 28), 29, EMBER),
    "victor": textured_bg((56, 44, 26), 31, GOLD),
    "cta": textured_bg((52, 40, 28), 19, GOLD),
}


# ───────────────────────────── arena fx ─────────────────────────────

def embers(layer, t, n=46, col=EMBER, hot=GOLD, a=1.0):
    """Rising ember particles, deterministic in t (the arena is always on fire)."""
    d = ImageDraw.Draw(layer)
    for i in range(n):
        h1 = ((i * 7919) % 1000) / 1000
        h2 = ((i * 104729) % 1000) / 1000
        h3 = ((i * 1299709) % 1000) / 1000
        speed = 60 + 120 * h2
        y = AH + 20 - ((t * speed + h1 * (AH + 40)) % (AH + 40))
        x = (h3 * W + 40 * math.sin(t * (0.6 + h1) + i)) % W
        life = 1 - (AH - y) / AH
        r = 2 + 3 * h2
        flick = 0.6 + 0.4 * math.sin(t * 9 + i * 1.7)
        al = int(255 * a * flick * max(0.15, life))
        c = hot if h1 > 0.6 else col
        d.ellipse([x - r * 2.2, y - r * 2.2, x + r * 2.2, y + r * 2.2], fill=c + (int(al * 0.18),))
        d.ellipse([x - r, y - r, x + r, y + r], fill=c + (al,))


def cannon_flash(frame, t, t0):
    """The tribute cannon: one white-hot slot flash + a fading ember tint."""
    dt = t - t0
    if dt < 0 or dt > 0.5:
        return
    a = int(230 * (1 - dt / 0.5) ** 2)
    ov = Image.new("RGBA", (W, AH), (255, 236, 200, a))
    frame.alpha_composite(ov, (0, LAYER_Y))


# ───────────────────────────── cards ─────────────────────────────

def emblem(size=420):
    """Custom games crest: gold ring, crossed arrows, Claude starburst in the middle."""
    def build():
        pad = 40
        S_ = size + pad * 2
        img = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
        glow = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([pad - 10, pad - 10, pad + size + 10, pad + size + 10], fill=GOLD + (110,))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(22)))
        d = ImageDraw.Draw(img)
        c = S_ / 2
        for ang in (45, 135):
            r = size * 0.62
            dx, dy = math.cos(math.radians(ang)) * r, math.sin(math.radians(ang)) * r
            d.line([(c - dx, c - dy), (c + dx, c + dy)], fill=GOLD + (255,), width=12)
            hx, hy = c + dx, c + dy
            ux, uy = dx / r, dy / r
            d.polygon([(hx + ux * 34, hy + uy * 34), (hx - uy * 20, hy + ux * 20), (hx + uy * 20, hy - ux * 20)],
                      fill=GOLD + (255,))
            fx, fy = c - dx, c - dy
            for k in (0, 1):
                d.line([(fx + ux * (k * 16), fy + uy * (k * 16)), (fx + ux * (k * 16) - uy * 22, fy + uy * (k * 16) + ux * 22)],
                       fill=GOLD + (255,), width=6)
                d.line([(fx + ux * (k * 16), fy + uy * (k * 16)), (fx + ux * (k * 16) + uy * 22, fy + uy * (k * 16) - ux * 22)],
                       fill=GOLD + (255,), width=6)
        d.ellipse([pad, pad, pad + size, pad + size], fill=INK + (255,), outline=GOLD + (255,), width=14)
        d.ellipse([pad + 26, pad + 26, pad + size - 26, pad + size - 26], outline=GOLD + (150,), width=3)
        inner = size - 60
        sph = Image.open("assets/logos/claude-sphinx.png").convert("RGBA")
        bb = sph.getbbox()
        sph = sph.crop(bb)
        z = int(inner * 1.18)
        sph = sph.resize((z, z), Image.LANCZOS).crop(((z - inner) // 2, (z - inner) // 2, (z - inner) // 2 + inner,
                                                      (z - inner) // 2 + inner))
        m = Image.new("L", (inner, inner), 0)
        ImageDraw.Draw(m).ellipse([0, 0, inner - 1, inner - 1], fill=255)
        sph.putalpha(Image.composite(sph.split()[3], m, m))
        img.alpha_composite(sph, (int(c - inner / 2), int(c - inner / 2)))
        ImageDraw.Draw(img).ellipse([c - inner / 2, c - inner / 2, c + inner / 2, c + inner / 2], outline=GOLD + (255,), width=6)
        return img
    return cached(("emblem", size), build)


def gold_plate(txt, fsz=86, w=980, h=150, sub=None):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 24, fill=INK + (240,), outline=GOLD + (255,), width=6)
        d.rounded_rectangle([12, 12, w - 13, h - 13], 16, outline=GOLD + (120,), width=2)
        y = h / 2 - (14 if sub else 0)
        d.text((w / 2, y), txt, font=F(AR, fsz), fill=GOLD + (255,), anchor="mm")
        if sub:
            d.text((w / 2, h - 30), sub, font=F(AR, 26), fill=SILVER + (255,), anchor="mm")
        return img
    return cached(("goldplate", txt, fsz, w, h, sub), build)


CHAT_Q = "help me brainstorm a name for my coffee subscription"


def chat_card(p, w=560, h=430):
    k = int(clamp01(p) * 40)

    def build():
        card = shadow_card((w, h), 26, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + 26, pad + 36), "CLAUDE  ·  BRAINSTORM", font=F(AR, 30), fill=WHITE + (255,), anchor="lm")
        q = k / 40
        shown = typewriter(CHAT_Q, q / 0.45, cursor=False)
        lines, cur = [], ""
        fnt = F(AR, 28)
        for wd in shown.split(" "):
            test = (cur + " " + wd).strip()
            if d.textlength(test, font=fnt) > w - 120:
                lines.append(cur)
                cur = wd
            else:
                cur = test
        lines.append(cur)
        bh = 30 + 40 * len(lines)
        d.rounded_rectangle([pad + 60, pad + 84, pad + w - 24, pad + 84 + bh], 22, fill=CYAN + (255,))
        for i, ln in enumerate(lines):
            d.text((pad + 80, pad + 100 + i * 40), ln, font=fnt, fill=INK + (255,))
        y = pad + 100 + bh
        if q > 0.55:
            for i, idea in enumerate(["Bean There", "Daily Grind Club", "Roast Post"][: 1 + int((q - 0.55) / 0.12)]):
                d.rounded_rectangle([pad + 24, y + i * 62, pad + w - 140, y + i * 62 + 50], 18, fill=CHAR + (255,))
                d.text((pad + 46, y + i * 62 + 25), f"{i + 1}. {idea}", font=F(AR, 26), fill=SILVER + (255,), anchor="lm")
        return card
    return cached(("chat", k, w, h), build)


def idea_bulb(size=110, col=GOLD):
    def build():
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        g = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([8, 4, size - 8, size - 20], fill=col + (120,))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(10)))
        d = ImageDraw.Draw(img)
        d.ellipse([size * 0.22, size * 0.12, size * 0.78, size * 0.66], fill=col + (255,))
        d.rectangle([size * 0.38, size * 0.6, size * 0.62, size * 0.8], fill=SILVER + (255,))
        d.line([(size * 0.38, size * 0.7), (size * 0.62, size * 0.7)], fill=STEEL + (255,), width=3)
        d.line([(size * 0.42, size * 0.48), (size * 0.5, size * 0.3), (size * 0.58, size * 0.48)], fill=WHITE + (255,), width=4)
        return img
    return cached(("bulb", size, col), build)


CMD = "/hunger-games name our new coffee subscription"
PLAN = ["100 tributes, 5 days, 471 sub-agent calls", "spawning tributes in waves of 10..."]


def term_card(p, w=980, h=230):
    k = int(clamp01(p) * 50)

    def build():
        card = shadow_card((w, h), 26, TERM_BG + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        for i, c in enumerate([RED, ORANGE, NEON]):
            d.ellipse([pad + 22 + i * 30, pad + 18, pad + 40 + i * 30, pad + 36], fill=c + (255,))
        d.text((pad + w / 2, pad + 27), "claude", font=F(ML, 20), fill=STEEL + (255,), anchor="mm")
        q = k / 50
        d.text((pad + 26, pad + 62), "> " + typewriter(CMD, q / 0.55, cursor=False), font=F(ML, 28), fill=WHITE + (255,))
        if q > 0.62:
            d.text((pad + 26, pad + 112), typewriter(PLAN[0], (q - 0.62) / 0.2, cursor=False), font=F(ML, 26), fill=GOLD + (255,))
        if q > 0.85:
            d.text((pad + 26, pad + 156), PLAN[1], font=F(ML, 24), fill=STEEL + (255,))
        return card
    return cached(("term", k, w, h), build)


DISTRICT = [ORANGE, CYAN, NEON, (190, 120, 255), RED, GOLD, BLUE, (255, 120, 200), (120, 220, 200), SILVER]


def tribute_sprite(i, size=56, dead=False):
    """Tiny invader tinted by district (i // 10). Fallen = grey + red X."""
    def build():
        base = load_invader_sprite(size)
        if dead:
            g = base.convert("LA").convert("RGBA")
            a = base.split()[3].point(lambda v: int(v * 0.35))
            g.putalpha(a)
            d = ImageDraw.Draw(g)
            d.line([(6, 6), (size - 6, size - 6)], fill=BLOOD + (230,), width=5)
            d.line([(size - 6, 6), (6, size - 6)], fill=BLOOD + (230,), width=5)
            return g
        col = DISTRICT[(i // 10) % 10]
        tint = Image.new("RGBA", base.size, col + (255,))
        lum = base.convert("L").point(lambda v: min(255, int(v * 1.25)))
        out = Image.composite(tint, Image.new("RGBA", base.size, (0, 0, 0, 0)), base.split()[3])
        out = Image.blend(out, base, 0.35)
        out.putalpha(base.split()[3])
        del lum
        return out
    return cached(("trib", i if not dead else -1, size, dead), build)


GRID_X0, GRID_Y0, CELL_W, CELL_H = 108, 92, 96, 64       # 10 x 10 arena in layer px


def cell_xy(i):
    r, c = divmod(i, 10)
    return GRID_X0 + c * CELL_W, GRID_Y0 + r * CELL_H


def arena_grid(layer, n_shown, dead=frozenset(), glow=frozenset(), dim=1.0, size=52):
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([GRID_X0 - 66, GRID_Y0 - 50, GRID_X0 + 9 * CELL_W + 66, GRID_Y0 + 9 * CELL_H + 50], 28,
                        fill=INK + (int(150 * dim),), outline=GOLD + (int(120 * dim),), width=3)
    for i in range(n_shown):
        x, y = cell_xy(i)
        if i in glow:
            d.ellipse([x - 36, y - 36, x + 36, y + 36], fill=GOLD + (int(70 * dim),))
        sp = tribute_sprite(i, size, dead=i in dead)
        if dim < 1:
            sp = sp.copy()
            sp.putalpha(sp.split()[3].point(lambda v: int(v * dim)))
        layer.alpha_composite(sp, (int(x - size / 2), int(y - size / 2)))


REASONING = ['First principles', 'Inversion', 'Analogy', 'Adversarial', 'Contrarian', 'Systems thinking']
WORKFLOW = ['Build, then break', 'Three drafts, pick one', 'Outline first', 'Options matrix', 'Test first']
STRATEGY = ['Edge cases first', 'Simplest thing that works', 'User empathy first', 'Maximal rigour', 'Speed']


def tribute_card(n, w=300, h=420):
    def build():
        card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        col = DISTRICT[(n // 10) % 10]
        d.rounded_rectangle([0, 0, w - 1, h - 1], 26, fill=(24, 22, 26, 255), outline=GOLD + (255,), width=5)
        d.rounded_rectangle([12, 12, w - 13, 176], 18, fill=col + (60,))
        sp = tribute_sprite(n, 128)
        card.alpha_composite(sp, ((w - 128) // 2, 32))
        d.text((w / 2, 196), f"TRIBUTE #{n}", font=F(AR, 34), fill=GOLD + (255,), anchor="mm")
        rows = [("REASONING", REASONING[n % len(REASONING)]), ("WORKFLOW", WORKFLOW[n % len(WORKFLOW)]),
                ("STRATEGY", STRATEGY[n % len(STRATEGY)])]
        for i, (lab, val) in enumerate(rows):
            y = 232 + i * 60
            d.text((22, y), lab, font=F(AR, 18), fill=STEEL + (255,))
            fs = 26
            while d.textlength(val, font=F(AR, fs)) > w - 44 and fs > 16:
                fs -= 1
            d.text((22, y + 22), val, font=F(AR, fs), fill=WHITE + (255,))
        return card
    return cached(("tcard", n, w, h), build)


RUBRIC = [("CORRECTNESS", 30), ("COMPLETENESS", 25), ("ROBUSTNESS", 20), ("SPECIFICITY", 15), ("CLARITY", 10)]


def scorecard(p, w=420, h=400):
    k = int(clamp01(p) * 30)

    def build():
        card = shadow_card((w, h), 24, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rectangle([pad, pad + 18, pad + 8, pad + h - 18], fill=GOLD + (255,))
        d.text((pad + 28, pad + 36), "GAMEMAKER", font=F(AR, 34), fill=GOLD + (255,), anchor="lm")
        d.text((pad + w - 24, pad + 36), "CLASH 7", font=F(AR, 22), fill=STEEL + (255,), anchor="rm")
        q = k / 30
        for i, (lab, wt) in enumerate(RUBRIC):
            y = pad + 84 + i * 60
            d.text((pad + 28, y), lab, font=F(AR, 22), fill=SILVER + (255,))
            d.text((pad + w - 24, y), f"x{wt}", font=F(AR, 22), fill=STEEL + (255,), anchor="ra")
            fill = clamp01(q * 1.6 - i * 0.15) * (0.55 + 0.4 * ((i * 37) % 10) / 10)
            d.rounded_rectangle([pad + 28, y + 30, pad + w - 24, y + 44], 7, fill=CHAR + (255,))
            if fill > 0:
                d.rounded_rectangle([pad + 28, y + 30, pad + 28 + int((w - 52) * fill), y + 44], 7, fill=GOLD + (255,))
        return card
    return cached(("score", k, w, h), build)


PENTA_R = 200
PENTA_C = (330, 250)           # authored (PACK_DY applied when drawn)
CLASH_IDS = [7, 23, 42, 58, 91]


def penta_xy(j, spin=0.0):
    ang = -math.pi / 2 + j * 2 * math.pi / 5 + spin
    return PENTA_C[0] + PENTA_R * math.cos(ang), PENTA_C[1] + PACK_DY + PENTA_R * math.sin(ang)


def clash(layer, lt, t_fire, t_boom, survivors=(2, 4)):
    """Free for all: five tributes on a pentagon, every one firing at every rival."""
    d = ImageDraw.Draw(layer)
    cx, cy = PENTA_C[0], PENTA_C[1] + PACK_DY
    d.ellipse([cx - PENTA_R - 70, cy - PENTA_R - 70, cx + PENTA_R + 70, cy + PENTA_R + 70],
              outline=RED + (110,), width=4)
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], outline=GOLD + (120,), width=3)
    pairs = [(a, b) for a in range(5) for b in range(5) if a != b]
    if lt >= t_fire and lt < t_boom + 0.05:
        for k, (a_, b_) in enumerate(pairs):
            ph = ((lt - t_fire) * 2.2 + k * 0.137) % 1.0
            if ph > 0.55:
                continue
            ax, ay = penta_xy(a_)
            bx, by = penta_xy(b_)
            q = ph / 0.55
            hx, hy = ax + (bx - ax) * q, ay + (by - ay) * q
            tx, ty = ax + (bx - ax) * max(0, q - 0.25), ay + (by - ay) * max(0, q - 0.25)
            col = DISTRICT[CLASH_IDS[a_] // 10 % 10]
            d.line([(tx, ty), (hx, hy)], fill=col + (90,), width=12)
            d.line([(tx, ty), (hx, hy)], fill=(255, 250, 235, 255), width=4)
    for j, tid in enumerate(CLASH_IDS):
        x, y = penta_xy(j)
        if lt >= t_boom and j not in survivors:
            age = lt - t_boom
            sp = tribute_sprite(tid, 120)
            shatter(layer, sp, x, y, age)
            if age < 0.6:
                place(layer, stamp("X", BLOOD, 60, pad=20), x, y - PACK_DY, lt, t_boom, dur=0.08, scale_pop=True, idle=0)
            continue
        sp = tribute_sprite(tid, 120)
        if lt < t_boom:
            jit = 4 * math.sin(lt * 31 + j * 2.1) if lt >= t_fire else 0
            layer.alpha_composite(sp, (int(x - 60 + jit), int(y - 60)))
        else:
            d.ellipse([x - 78, y - 78, x + 78, y + 78], fill=GOLD + (60,))
            layer.alpha_composite(sp, (int(x - 60), int(y - 60)))
        d.text((x, y + 74), f"#{tid}", font=F(AR, 24), fill=SILVER + (255,), anchor="mm")


# elimination order: the survivor of each day is a fixed subset so the grid tells the true story
_rng = np.random.default_rng(2026)
ORDER = list(_rng.permutation(100))
VICTOR = 42
ORDER.remove(VICTOR)
ORDER.append(VICTOR)                     # last one standing
ALIVE = [100, 40, 16, 8, 4, 1]


def dead_after(day):
    n_alive = ALIVE[day]
    return frozenset(ORDER[: 100 - n_alive])


def crown(size=160):
    def build():
        img = Image.new("RGBA", (size, int(size * 0.7)), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        w_, h_ = size, int(size * 0.7)
        pts = [(4, h_ - 8), (4, h_ * 0.25), (w_ * 0.28, h_ * 0.55), (w_ * 0.5, 4), (w_ * 0.72, h_ * 0.55),
               (w_ - 4, h_ * 0.25), (w_ - 4, h_ - 8)]
        d.polygon(pts, fill=GOLD + (255,), outline=(170, 110, 20, 255))
        d.rectangle([4, h_ - 30, w_ - 4, h_ - 8], fill=(230, 160, 40, 255))
        for x in (w_ * 0.25, w_ * 0.5, w_ * 0.75):
            d.ellipse([x - 9, h_ - 28, x + 9, h_ - 10], fill=RED + (255,))
        for x, y in [(4, h_ * 0.25), (w_ * 0.5, 4), (w_ - 4, h_ * 0.25)]:
            d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=WHITE + (255,))
        return img
    return cached(("crown", size), build)


def confetti(layer, lt, t0, n=60):
    if lt < t0:
        return
    d = ImageDraw.Draw(layer)
    age = lt - t0
    for i in range(n):
        h1 = ((i * 7919) % 1000) / 1000
        h2 = ((i * 104729) % 1000) / 1000
        x = W * h1 + 60 * math.sin(age * 3 + i)
        y = -20 + age * (220 + 260 * h2) + 30 * math.sin(i)
        if y > AH:
            continue
        c = [GOLD, WHITE, EMBER, NEON][i % 4]
        ang = age * (4 + 6 * h2) + i
        dx, dy = 10 * math.cos(ang), 5 * math.sin(ang)
        d.polygon([(x - dx, y - dy), (x + dy, y - dx), (x + dx, y + dy), (x - dy, y + dx)], fill=c + (230,))


def win_card(p, w=520, h=430):
    k = int(clamp01(p) * 24)

    def build():
        card = shadow_card((w, h), 26, INK + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad, pad, pad + w - 1, pad + h - 1], 26, outline=GOLD + (255,), width=5)
        d.text((pad + w / 2, pad + 48), "THE WINNING IDEA", font=F(AR, 40), fill=GOLD + (255,), anchor="mm")
        rows = [("tributes in", "100"), ("days", "5"), ("left standing", "1"), ("rivals faced", "17")]
        q = k / 24
        for i, (lab, val) in enumerate(rows[: int(q * 4.99)]):
            y = pad + 106 + i * 72
            d.rounded_rectangle([pad + 26, y, pad + w - 26, y + 58], 14, fill=GRAPHITE + (255,))
            d.text((pad + 48, y + 29), lab.upper(), font=F(AR, 26), fill=SILVER + (255,), anchor="lm")
            d.text((pad + w - 48, y + 29), val, font=F(AR, 34), fill=GOLD + (255,), anchor="rm")
        return card
    return cached(("win", k, w, h), build)


def bubble(d, x, y, txt, fnt, fill, fg, right=False, maxw=380):
    tw = d.textlength(txt, font=fnt)
    bw = min(maxw, tw + 40)
    x0 = x - bw if right else x
    d.rounded_rectangle([x0, y, x0 + bw, y + 58], 24, fill=fill)
    d.text((x0 + 20, y + 29), txt, font=fnt, fill=fg, anchor="lm")
    return y + 72


def inbox_card(p, w=460, h=440):
    k = int(p * 24)

    def build():
        card = shadow_card((w, h), 26, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + 26, pad + 36), "COMMENTS  ·  DM", font=F(AR, 30), fill=WHITE + (255,), anchor="lm")
        d.ellipse([pad + w - 44, pad + 28, pad + w - 24, pad + 48], fill=NEON + (255,))
        fnt = F(AR, 28)
        y = pad + 100
        q = k / 24
        y = bubble(d, pad + 24, y, "@you: GAMES", fnt, CHAR + (255,), SILVER + (255,))
        if q > 0.3:
            d.text((pad + w / 2, y + 6), "▼  keyword matched", font=MONO_S, fill=NEON + (255,), anchor="mt")
            y += 48
        if q > 0.5:
            y = bubble(d, pad + w - 24, y, typewriter("Let the games begin!", (q - 0.5) / 0.3, cursor=False),
                       fnt, GOLD + (255,), INK + (255,), right=True)
        if q > 0.85:
            bubble(d, pad + w - 24, y, "/hunger-games skill", MONO_S, BLUE + (255,), INK + (255,), right=True)
        return card
    return cached(("inbox", k, w, h), build)


# ───────────────────────────── sections ─────────────────────────────

BULBS = [(120, -150, 0.0), (960, -120, 0.25), (90, 120, 0.5), (980, 160, 0.7), (150, 400, 0.9), (930, 420, 1.1)]


def hook(layer, lt):
    """Frame 0: the brainstorm. Giant invader + Claude chat filling with ideas, bulbs popping."""
    gw = ghost_word("BRAINSTORM", 110, 40)
    layer.alpha_composite(gw, ((W - gw.width) // 2, 4))
    ix, iy = 270, 230 + PACK_DY
    bloom_orb(layer, ix, iy, 230, CYAN, a=60)
    grab_t = clamp01((lt - T_SKILL) / 0.35) * 0.85 if lt >= T_SKILL else 0.0
    place_claude_invader(layer, ix, iy, lt, size=400, look_at=(760, 200 + PACK_DY),
                         grab="right" if grab_t else None, grab_at=(ix + 160, iy - 170), grab_t=grab_t,
                         hold=skill_chip("SKILL.md") if grab_t else None)
    place(layer, chat_card(clamp01((lt + 0.6) / 2.4)), 760, 210, lt, -0.4, dur=0.01, idle=0)
    for i, (x, y, t0) in enumerate(BULBS[:3] if lt < T_BUILT else BULBS):
        place(layer, idea_bulb(96), x, y, lt, t0 - 0.4 if i < 2 else T_BRAIN + t0 * 0.6, dur=0.2,
              scale_pop=True, idle=3)
    if lt >= T_BUILT:
        place(layer, os_chip("I BUILT A SKILL", NEON, 32), 270, 470, lt, T_BUILT, dur=0.2, frm="up", idle=0)


def title(layer, lt, a):
    t_c2, t_h, t_id, t_fun = T_CLAUDE2 - a, T_HUNGER - a, T_IDEAS - a, T_FUN - a
    embers(layer, a + lt)
    if lt < t_c2:
        place(layer, gold_plate("CLAUDE ...", 90), 540, -150, lt, 0.0, dur=0.16, frm="down", idle=0)
        bloom_orb(layer, 290, 210 + PACK_DY, 200, GOLD, a=60)
        place(layer, emblem(400), 290, 210, lt, 0.0, dur=0.2, frm="left", idle=0)
        for i, (x, y) in enumerate([(700, 120), (860, 260), (720, 380)]):
            place(layer, reticle(170, GOLD, locked=False), x, y, lt, 0.05 * i, dur=0.16, idle=0)
        return
    title_txt = "CLAUDE" if lt < t_h - 0.03 else "CLAUDE HUNGER GAMES"
    place(layer, gold_plate(title_txt, 88 if len(title_txt) > 8 else 96), 540, -150, lt, t_c2 if lt < t_h else t_h,
          dur=0.14, frm="down", scale_pop=True, idle=0)
    rot = (lt - t_c2) * 6
    em = emblem(400).rotate(-4 + 4 * math.sin(rot * 0.3), resample=Image.BICUBIC, expand=False)
    bloom_orb(layer, 290, 210 + PACK_DY, 260, GOLD, a=90)
    place(layer, em, 290, 210, lt, t_c2, dur=0.22, frm="left", scale_pop=True, idle=0)
    light_rays(layer, 290, 210 + PACK_DY, lt, GOLD)
    if lt >= t_h:
        light_hit(layer, 540, -150 + PACK_DY, lt, t_h, GOLD)
        front_gif(gif_card("happy-hg", max(0, lt - t_h), w=500, frame="round"), 790, 130, lt, t_h + 0.05,
                  **entrance(1), idle=0)
    if lt >= t_id:
        for i, (x, y) in enumerate([(640, 380), (800, 410), (960, 370)]):
            place(layer, idea_bulb(110), x, y, lt, t_id + i * 0.1, dur=0.2, scale_pop=True, idle=3)
    if lt >= t_fun:
        place(layer, stamp("FUN", NEON, 70), 860, 260, lt, t_fun, dur=0.12, frm="down", scale_pop=True, tilt=-8, idle=0)


def idea(layer, lt, a):
    t_give, t_idea, t_create = T_GIVE - a, T_IDEA - a, T_CREATE - a
    embers(layer, a + lt, n=26, a=0.6)
    place(layer, term_card(clamp01((lt - t_give + 0.3) / 1.9)), 540, -110, lt, -0.4, dur=0.01, idle=0)
    ix, iy = 280, 320 + PACK_DY
    bloom_orb(layer, ix, iy, 180, CYAN, a=60)
    place_claude_invader(layer, ix, iy, lt + 2.0, size=280, look_at=(540, -110 + PACK_DY))
    if lt >= t_idea:
        place(layer, idea_bulb(150, GOLD), ix + 150, 210, lt, t_idea, dur=0.2, scale_pop=True, idle=0)
        light_hit(layer, ix + 150, 210 + PACK_DY, lt, t_idea, GOLD)
    if lt < t_idea:
        place(layer, emblem(240), 790, 300, lt, -0.4, dur=0.01, idle=0, exit_at=t_idea - 0.2)
    elif lt < t_create - 0.1:
        place(layer, gold_plate("YOUR IDEA", 54, w=480, h=200, sub="name our new coffee subscription"), 770, 300,
              lt, t_idea, dur=0.2, frm="right", scale_pop=True, idle=0, exit_at=t_create - 0.3)
    if lt >= t_create - 0.1:
        front_gif(gif_card("volunteer", max(0, lt - t_create + 0.1), w=520, frame="round"), 760, 330, lt,
                  t_create - 0.1, **entrance(4), idle=0)


def spawn(layer, lt, a):
    t = a + lt
    t_h, t_ch, t_at, t_cen = T_HUNDRED - a, T_CHARS - a, T_ATTR - a, T_CENTERED - a
    embers(layer, t, n=30, a=0.7)
    t_land = t_ch - 0.05
    if lt < t_land + 0.1:
        p = 0.0 if lt < t_h else clamp01((lt - t_h) / max(0.3, t_land - t_h))
        beat = {"t": T_HUNDRED, "value": 100, "label": "tributes"}
        place(layer, counter_card(beat, p, w=760, h=400, accent=GOLD), 540, 160, lt, -0.4, dur=0.01, idle=0,
              exit_at=t_land)
        if lt >= t_land - 0.05:
            light_hit(layer, 540, 160 + PACK_DY, lt, t_land - 0.05, GOLD)
        return
    waves = 1 + int(clamp01((lt - t_ch) / 1.2) * 9.99)
    dim = 0.45 if lt >= t_at else 1.0
    arena_grid(layer, min(100, waves * 10), dim=dim)
    if lt < t_at:
        place(layer, os_chip(f"WAVE {min(10, waves)} / 10", GOLD, 30), 540, -190, lt, t_ch, dur=0.18, frm="down", idle=0)
    else:
        for j, (n, x, tilt) in enumerate([(37, 250, 9), (42, 540, 0), (81, 830, -9)]):
            place(layer, tribute_card(n), x, 210 + abs(x - 540) * 0.08, lt, t_at + j * 0.12, dur=0.24,
                  frm="up", tilt=tilt, scale_pop=j == 1, idle=0, exit_at=t_cen - 0.2)
        if lt >= t_at:
            place(layer, os_chip("EVERY ONE GETS A STRATEGY CARD", GOLD, 30), 540, -190, lt, t_at, dur=0.18,
                  frm="down", idle=0, exit_at=t_cen - 0.2)
    if lt >= t_cen:
        arena_grid(layer, 100)
        place(layer, gold_plate("SAME IDEA  x100", 70, w=620, h=120), 540, 210, lt, t_cen, dur=0.2, scale_pop=True, idle=0)
        place(layer, idea_bulb(120), 540, 105, lt, t_cen + 0.1, dur=0.2, scale_pop=True, idle=0)


def battle(layer, lt, a):
    t = a + lt
    t_b, t_d = T_BATTLE - a, T_DEATH - a
    embers(layer, t, n=50, col=RED, a=0.9)
    place(layer, title_card("FREE FOR ALL", RED, fsz=66, h=110), 540, -180, lt, -0.4, dur=0.01, idle=0)
    clash(layer, lt, t_b - 0.1, t_d)
    if lt >= t_b + 0.5:
        place(layer, scorecard(clamp01((lt - t_b - 0.5) / 1.2)), 820, 250, lt, t_b + 0.5, dur=0.2, frm="right", idle=0)
    if lt < t_b + 0.55:
        front_gif(gif_card("odds", max(0, lt), w=400, frame="round"), 820, 230, lt, -0.4, dur=0.01, idle=0,
                  exit_at=t_b + 0.3)
    if lt >= t_d:
        place(layer, stamp("BOOM", BLOOD, 120, pad=44), 820, 30, lt, t_d, dur=0.1, frm="down", scale_pop=True,
              tilt=-7, idle=0)
        light_hit(layer, PENTA_C[0], PENTA_C[1] + PACK_DY, lt, t_d, BLOOD)


DAY_T = [0.05, 0.6, 1.15, 1.7]              # after "until": days 1-4, the finale lands on "winner"


def days(layer, lt, a):
    t = a + lt
    embers(layer, t, n=40, a=0.8)
    day = sum(1 for dt in DAY_T if lt >= dt)
    fin = T_EXACT - a
    if lt >= fin:
        day = 4
    dead = dead_after(day)
    alive = frozenset(range(100)) - dead
    arena_grid(layer, 100, dead=dead, glow=alive if day >= 3 else frozenset())
    label = "FINALE" if lt >= fin else f"DAY {max(1, day)}"
    n_left = ALIVE[day]
    place(layer, gold_plate(f"{label}  ·  {n_left} LEFT", 64, w=640, h=110), 540, -190, lt, -0.4, dur=0.01, idle=0)
    if day >= 1:
        k = DAY_T[day - 1]
        if lt - k < 0.35:
            light_hit(layer, 540, -190 + PACK_DY, lt, k, EMBER)
    if lt >= fin:
        place(layer, stamp("ONLY ONE WALKS OUT", GOLD, 60), 540, 230, lt, fin, dur=0.12, frm="down", scale_pop=True,
              tilt=-4, idle=0)


def victor(layer, lt, a):
    t = a + lt
    t_ans = T_ANSWER - a
    embers(layer, t, n=36, col=GOLD, hot=WHITE, a=0.8)
    vx, vy = 280, 240 + PACK_DY
    bloom_orb(layer, vx, vy, 280, GOLD, a=110)
    light_rays(layer, vx, vy, lt, GOLD)
    place_claude_invader(layer, vx, vy + 20, lt + 5.0, size=360, look_at=(vx + 300, vy))
    cr = crown(190)
    drop = 1 - ease(clamp01(lt / 0.35))
    layer.alpha_composite(cr, (int(vx - cr.width / 2), int(vy - 250 - 160 * drop)))
    place(layer, stamp("VICTOR  #42", GOLD, 64), 280, -150, lt, 0.0, dur=0.14, frm="down", scale_pop=True,
          tilt=-5, idle=0)
    light_hit(layer, vx, vy, lt, 0.05, GOLD)
    confetti(layer, lt, 0.05)
    if lt < t_ans - 0.05:
        front_gif(gif_card("champion", max(0, lt), w=480, frame="round"), 790, 220, lt, 0.08, **entrance(5), idle=0,
                  exit_at=t_ans - 0.25)
    else:
        place(layer, win_card(clamp01((lt - t_ans) / 0.8)), 790, 230, lt, t_ans, dur=0.2, frm="right", idle=0)


def cta(layer, lt, a):
    t_h2, t_c = T_HUNGER2 - a, T_COMMENT - a
    embers(layer, a + lt)
    if lt < t_c - 0.12:
        ex = t_c - 0.34
        bloom_orb(layer, 290, 220 + PACK_DY, 240, GOLD, a=80)
        place(layer, emblem(380), 290, 220, lt, -0.4, dur=0.01, idle=0, exit_at=ex)
        place(layer, gold_plate("HUNGER GAMES AGENTS", 70, w=960, h=120), 540, -170, lt, t_h2, dur=0.16,
              frm="down", scale_pop=True, idle=0, exit_at=ex)
        front_gif(gif_card("salute", max(0, lt - t_h2), w=440, frame="round"), 800, 230, lt, t_h2 + 0.05,
                  **entrance(6), idle=0, exit_at=ex)
        return
    place(layer, title_card("COMMENT  \"GAMES\"", GOLD, fsz=80, h=140), 540, -150, lt, t_c - 0.12, dur=0.18,
          scale_pop=True, idle=0)
    light_hit(layer, 540, -150 + PACK_DY, lt, t_c, GOLD)
    light_rays(layer, 540, -150 + PACK_DY, lt, GOLD)
    front_gif(gif_card("comment", max(0, lt - t_c), w=420, frame="round"), 270, 220, lt, t_c - 0.08,
              **entrance(2), idle=0)
    place(layer, inbox_card(clamp01((lt - t_c) / 0.9)), 790, 220, lt, t_c - 0.02, frm="right", idle=0)


def scene(layer, name, lt, a):
    {
        "hook": lambda: hook(layer, lt),
        "title": lambda: title(layer, lt, a),
        "idea": lambda: idea(layer, lt, a),
        "spawn": lambda: spawn(layer, lt, a),
        "battle": lambda: battle(layer, lt, a),
        "days": lambda: days(layer, lt, a),
        "victor": lambda: victor(layer, lt, a),
        "cta": lambda: cta(layer, lt, a),
    }[name]()


# ───────────────────────────── compose ─────────────────────────────

if not os.path.isfile("renders/talking_band45.mp4"):
    raise SystemExit("missing renders/talking_band45.mp4")

band_cap = cv2.VideoCapture("renders/talking_band45.mp4")
band_mask = Image.new("L", (BAND_W, BAND_H), 0)
ImageDraw.Draw(band_mask).rounded_rectangle([0, 0, BAND_W - 1, BAND_H - 1], 60, fill=255)


def word_at(t):
    for w, a, b in words:
        if a <= t <= b + 0.08:
            return w.strip().rstrip(".,!?").lower()
    return None


PUNCH_T = [T_HUNGER, T_DEATH]                          # one hero word per section, >=8s apart
HIT_T = [T_HUNGER, T_IDEA, T_DEATH, T_WINNER, T_COMMENT]
CUT_T = [T_CALLED, T_SO2, T_A, T_AND, T_UNTIL, T_WINNER - 0.06, T_IF]
WHIP_T, HF_T = CUT_T[::2], CUT_T[1::2]

print("sections", [(s[0], round(s[1], 2)) for s in SECT])

os.makedirs("frames/out5", exist_ok=True)
PREVIEW = os.environ.get("PREVIEW")
if PREVIEW:
    todo = [min(N - 1, int(round(float(x) * FPS))) for x in PREVIEW.split(",")]
else:
    todo = list(range(N))
    if os.environ.get("RANGE"):
        _a, _b = os.environ["RANGE"].split(":")
        todo = list(range(int(_a), min(N, int(_b))))

if todo and not PREVIEW:
    band_cap.set(cv2.CAP_PROP_POS_FRAMES, todo[0])

last_band = None
prev_layer = None
prev_name = None

for n in todo:
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
    scene(layer, name, lt, a)
    flush_gifs(layer)
    slot_vignette(layer, a=22)
    speed_streaks(layer, t, PUNCH_T, NEON)

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
    cannon_flash(frame, t, T_DEATH)
    acc = SECT_ACCENT[name]
    hd = ImageDraw.Draw(frame)
    hd.rectangle([48, BAND_Y - 8, W - 48, BAND_Y - 4], fill=acc + (200,))
    hd.rectangle([48, LAYER_Y + 2, W - 48, LAYER_Y + 4], fill=SILVER + (70,))
    if name != "hook":
        hyperframe(frame, t, HF_T, FPS, region=(0, LAYER_Y, W, AH))

    if PREVIEW:
        band_cap.set(cv2.CAP_PROP_POS_FRAMES, n)
    ok, fr = band_cap.read()
    if ok:
        bf = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGBA")
        bf.putalpha(band_mask)
        last_band = bf
    if last_band is not None:
        frame.alpha_composite(last_band, (12, BAND_Y))

    wd = word_at(t)
    if wd:
        d = ImageDraw.Draw(frame)
        key = wd in KEYWORDS
        col = (KEY_COL.get(wd, ORANGE) + (255,)) if key else (255, 255, 255, 255)
        ons = next((aa for ww, aa, bb2 in words if ww.strip().rstrip(".,!?").lower() == wd and aa <= t <= bb2 + 0.08), t)
        fs = int(66 * caption_impact(t, ons, key))
        cf = F(CAP, fs)
        label = wd.upper()
        tw = d.textlength(label, font=cf)
        x = (W - tw) / 2
        y = BAND_Y - 8 - 7 - 3
        if key:
            caption_bloom(frame, x, y - fs, tw, fs, KEY_COL.get(wd, NEON))
        d.text((x, y), label, font=cf, fill=col, anchor="ls", stroke_width=7, stroke_fill=(0, 0, 0, 255))

    frame.convert("RGB").save(f"frames/out5/f{n:05d}.jpg", quality=92)
    if PREVIEW:
        print(f"preview t={t:.2f} {name}", flush=True)
    elif n % 60 == 0:
        print(f"{n}/{N}", flush=True)

band_cap.release()
print("frames done", len(todo), flush=True)