#!/usr/bin/env python3
"""Split animated talking-head: Jev x 10k App Store search.

1080x1920. Someone scraped the top-chart apps from the App Store + Google Play,
trained Jev on them, and shipped a search site. Kevin's screen recording of the
site (assets/broll/broll.mp4, 1280x720) is the hook, the live search card
(src = t - 12.0 lines up with "search ... competitors ... best performing"),
the icon crops for the topic lane, and the CTA card.
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
    entrance,
    guarded_conveyor,
    hyperframe,
    lanes,
    punch_scale,
    punch_zoom,
    shake_offset,
    typewriter,
    whip_dir,
    whip_wipe,
)
from media_marks import figure_round, gif_card, logo_badge, name_plate, odometer_card  # noqa: E402
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
PINK = (236, 72, 153)      # TypeSafe / JEV brand pink
CORAL = ORANGE
PAPER = GRAPHITE
WHITE = (255, 252, 248)
TERM_BG = (27, 28, 32)
MONO = F(ML, 24)
MONO_S = F(ML, 20)

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


T_WILD = trel("wildest")
T_JEV = trel("jev")
T_CASES = trel("cases")
T_SEEN = trel("seen")
T_SOMEONE = trel("someone")
T_GRABBED = trel("grabbed")
T_BEST = trel("best")
T_WINNING = trel("winning")
T_MOBILE = trel("mobile")
T_GOOGLE = trel("google")
T_THEN = trel("then", 9.5)
T_TRAINED = trel("trained")
T_JEV2 = trel("jev", 11.0)
T_SO = trel("so", 12.0)
T_SEARCH = trel("search")
T_FIND = trel("find")
T_CATEGORY = trel("category")
T_THINK = trel("think")
T_AND2 = trel("and", 18.3)
T_COMPET = trel("competitors")
T_GENERATE = trel("generate")
T_IDEAS = trel("ideas")
T_PERF = trel("performing")
T_OF2026 = trel("of", 22.5)
T_2026 = trel("2026")
T_IF = trel("if", 23.5)
T_MARKET = trel("market")
T_WEBSITE = trel("website")
T_COMMENT = trel("comment")
T_APPS_W = trel("apps", 25.7)

SECT = [
    ("hook", 0.00, T_SOMEONE),
    ("grab", T_SOMEONE, T_THEN),
    ("trained", T_THEN, T_SO),
    ("search", T_SO, T_AND2),
    ("compete", T_AND2, T_OF2026),
    ("year", T_OF2026, T_IF),
    ("cta", T_IF, DUR + 0.05),
]
KEYWORDS = {
    "wildest", "jev", "ai", "someone", "grabbed", "best", "winning", "applications", "mobile",
    "google", "play", "trained", "search", "find", "any", "category", "competitors", "generate",
    "ideas", "performing", "apps", "2026", "market", "research", "website", "comment",
}
KEY_COL = {
    "wildest": RED, "jev": PINK, "ai": PINK, "someone": ORANGE, "grabbed": ORANGE, "best": NEON,
    "winning": NEON, "applications": CYAN, "mobile": BLUE, "google": NEON, "play": NEON,
    "trained": PINK, "search": NEON, "find": NEON, "any": ORANGE, "category": ORANGE,
    "competitors": RED, "generate": CYAN, "ideas": CYAN, "performing": NEON, "apps": NEON,
    "2026": ORANGE, "market": BLUE, "research": BLUE, "website": CYAN, "comment": NEON,
}
SECT_ACCENT = {
    "hook": PINK, "grab": ORANGE, "trained": PINK, "search": NEON,
    "compete": ORANGE, "year": NEON, "cta": NEON,
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
    "hook": textured_bg((54, 44, 54), 7, PINK),
    "grab": textured_bg((48, 38, 32), 23, ORANGE),
    "trained": textured_bg((54, 44, 54), 11, PINK),
    "search": textured_bg((36, 48, 42), 13, NEON),
    "compete": textured_bg((48, 38, 32), 29, ORANGE),
    "year": textured_bg((36, 48, 44), 31, NEON),
    "cta": textured_bg((36, 48, 44), 19, NEON),
}


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


def check_chip(txt, on, accent=NEON, fsz=30):
    def build():
        fnt = F(AR, fsz)
        tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(txt, font=fnt))
        w, h = tw + 96, fsz + 36
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 16, fill=GRAPHITE + (255,),
                            outline=(accent if on else STEEL) + (255,), width=3)
        bx, by = 20, h / 2 - 17
        d.rounded_rectangle([bx, by, bx + 34, by + 34], 8, outline=(accent if on else STEEL) + (255,), width=3,
                            fill=(accent + (255,)) if on else None)
        if on:
            d.line([(bx + 7, by + 17), (bx + 15, by + 26), (bx + 28, by + 8)], fill=INK + (255,), width=5)
        d.text((bx + 52, h / 2), txt, font=fnt, fill=(WHITE if on else STEEL) + (255,), anchor="lm")
        return img
    return cached(("check", txt, on, accent, fsz), build)


def title_card(txt, accent=ORANGE, fsz=72, w=960, h=150):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 28, fill=GRAPHITE + (255,))
        d.rectangle([0, 0, 14, h], fill=accent + (255,))
        d.text((w / 2 + 6, h / 2 - 2), txt, font=F(AR, fsz), fill=WHITE + (255,), anchor="mm")
        return img
    return cached(("title", txt, accent, fsz, w, h), build)


def stamp(txt, col=RED, fsz=64, pad=34):
    def build():
        fnt = F(AR, fsz)
        tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(txt, font=fnt))
        w, h = tw + pad * 2, fsz + 44
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 16, fill=INK + (210,), outline=col + (255,), width=8)
        d.rounded_rectangle([12, 12, w - 13, h - 13], 10, outline=col + (150,), width=2)
        d.text((w / 2, h / 2 - 2), txt, font=fnt, fill=col + (255,), anchor="mm")
        return img
    return cached(("stamp", txt, col, fsz), build)


def jev_hero(size=420):
    return cached(("jevhero", size), lambda: logo_badge("jev", size, fill=INK + (255,), punch=False))


def jev_wordmark(w=960, h=140):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w, h], 30, fill=PINK + (255,), outline=SILVER + (80,), width=2)
        d.text((w / 2 - 60, h / 2 - 6), "JEV AI", font=F(AR, 104), fill=INK + (255,), anchor="mm")
        d.text((w - 150, h / 2), "by TypeSafe", font=F(AR, 26), fill=INK + (220,), anchor="mm")
        return img
    return cached(("jevword", w, h), build)


# ───────────────────────────── b-roll: the 10k x Jev search site ─────────────────────────────

class Broll:
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
        if len(self.cache) > 24:
            self.cache.clear()
        self.cache[i] = img
        return img


BROLL = Broll("assets/broll/broll.mp4")
BW, BH = 1280, 720
SEARCH_SHIFT = 12.0          # search + compete: src = t - 12.0

# camera keyframes over src time: (src_t, view width in source px, center x, center y)
# typing -> punch in on the search bar; results / detail pages -> pull back.
CAM = [
    (0.0, 640, 640, 360), (1.30, 640, 640, 360), (1.60, 980, 640, 300),
    (3.75, 980, 640, 300), (4.05, 640, 640, 360), (7.30, 640, 640, 360),
    (7.60, 980, 640, 300), (30.0, 980, 640, 300),
]


def cam_at(src_t):
    for (t0, w0, x0, y0), (t1, w1, x1, y1) in zip(CAM, CAM[1:]):
        if t0 <= src_t <= t1:
            p = (src_t - t0) / max(1e-6, t1 - t0)
            p = p * p * (3 - 2 * p)
            return w0 + (w1 - w0) * p, x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    return CAM[-1][1:]


def broll_view(src_t, w=1000, h=540, accent=NEON, live=True):
    fr = BROLL.frame(src_t)
    if fr is None:
        return None
    sw, cx, cy = cam_at(src_t)
    sh = sw * h / w
    x0 = max(0, min(BW - sw, cx - sw / 2))
    y0 = max(0, min(BH - sh, cy - sh / 2))
    im = fr.crop((int(x0), int(y0), int(x0 + sw), int(y0 + sh))).resize((w, h), Image.BICUBIC).convert("RGBA")
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], 20, fill=255)
    im.putalpha(mask)
    pad = 12
    card = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, card.width - 1, card.height - 1], 28, fill=GRAPHITE + (255,),
                        outline=accent + (160,), width=3)
    card.alpha_composite(im, (pad, pad))
    if live:
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([w - 110, pad + 16, w - 4, pad + 56], 12, fill=INK + (220,))
        d.ellipse([w - 98, pad + 28, w - 82, pad + 44], fill=RED + (255,))
        d.text((w - 72, pad + 22), "LIVE", font=F(AR, 24), fill=SILVER + (255,))
    return card


ICON_BOXES = {  # real app icons cropped from the recording (src_t, box)
    "tasty": (7.8, (340, 212, 432, 303)), "chef": (7.8, (444, 212, 536, 303)),
    "epi": (7.8, (549, 212, 641, 303)), "mealprep": (7.8, (653, 212, 745, 303)),
    "cookpad": (7.8, (758, 212, 850, 303)), "chefgreen": (7.8, (862, 212, 955, 303)),
    "cat": (1.7, (324, 106, 406, 188)), "blackcat": (1.7, (512, 106, 594, 188)),
    "catface": (1.7, (606, 106, 688, 188)), "checker": (1.7, (700, 106, 782, 188)),
    "paw": (1.7, (888, 106, 972, 190)),
}


def app_icon(slug, size=120):
    src_t, box = ICON_BOXES[slug]

    def build():
        im = BROLL.frame(src_t).crop(box).resize((size, size), Image.LANCZOS).convert("RGBA")
        m = Image.new("L", (size, size), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], int(size * 0.22), fill=255)
        im.putalpha(m)
        out = Image.new("RGBA", (size + 16, size + 16), (0, 0, 0, 0))
        sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([6, 10, size + 10, size + 14], int(size * 0.24), fill=(0, 0, 0, 120))
        out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
        out.alpha_composite(im, (8, 8))
        return out
    return cached(("appicon", slug, size), build)


LANE = ["tasty", "app-store", "cat", "epi", "google-play", "mealprep", "catface", "cookpad",
        "jev", "checker", "chef", "paw"]


def lane_marks(size=120):
    out = []
    for s_ in LANE:
        if s_ in ICON_BOXES:
            out.append(app_icon(s_, size - 16))
        else:
            out.append(logo_badge(s_, size, fill=(INK if s_ == "jev" else WHITE) + (255,), punch=s_ != "jev"))
    return [m for m in out if m is not None]


TOP_ROWS = [("tasty", "Tasty: Recipes", "4.9"), ("cookpad", "Cookpad Recipes", "4.8"),
            ("epi", "Epicurious", "4.8"), ("mealprep", "MealPrepPro", "4.7"),
            ("cat", "Cat Translator", "4.6")]


def top_chart_card(n_rows, p_stamp=0.0, w=470):
    row_h = 86

    def build():
        h = 92 + row_h * len(TOP_ROWS) + 10
        card = shadow_card((w, h), 26, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rectangle([pad, pad + 20, pad + 8, pad + h - 20], fill=ORANGE + (255,))
        d.text((pad + 30, pad + 24), "TOP CHARTS", font=F(AR, 36), fill=WHITE + (255,))
        d.text((pad + w - 26, pad + 34), "FREE", font=F(AR, 24), fill=STEEL + (255,), anchor="ra")
        for i, (slug, name, stars) in enumerate(TOP_ROWS[:n_rows]):
            y = pad + 90 + i * row_h
            d.text((pad + 26, y + 36), f"{i + 1}", font=F(AR, 34), fill=ORANGE + (255,), anchor="lm")
            card.alpha_composite(app_icon(slug, 64), (pad + 52, y - 2))
            d.text((pad + 140, y + 24), name, font=F(AR, 30), fill=WHITE + (255,), anchor="lm")
            d.text((pad + 140, y + 54), f"★ {stars}", font=F(AR, 22), fill=SILVER + (255,), anchor="lm")
            d.rounded_rectangle([pad + w - 120, y + 18, pad + w - 30, y + 54], 18, fill=CHAR + (255,))
            d.text((pad + w - 75, y + 36), "GET", font=F(AR, 22), fill=BLUE + (255,), anchor="mm")
        return card
    return cached(("topchart", n_rows, w), build)


TRAIN_LINES = [
    ("$ jev train --data top-charts", SILVER),
    ("> App Store top charts ......... ok", NEON),
    ("> Google Play top charts ....... ok", NEON),
    ("> icons, screenshots, ratings .. ok", NEON),
    ("> training Jev", PINK),
]


def train_card(p, w=600, h=430):
    k = int(clamp01(p) * 60)

    def build():
        card = shadow_card((w, h), 26, TERM_BG + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        for i, c in enumerate([RED, ORANGE, NEON]):
            d.ellipse([pad + 22 + i * 30, pad + 20, pad + 40 + i * 30, pad + 38], fill=c + (255,))
        d.text((pad + w / 2, pad + 29), "jev-train", font=MONO_S, fill=STEEL + (255,), anchor="mm")
        q = k / 60
        n_lines = len(TRAIN_LINES)
        for i, (ln, col) in enumerate(TRAIN_LINES):
            lp = clamp01(q * (n_lines + 1) - i)
            if lp <= 0:
                break
            d.text((pad + 24, pad + 74 + i * 44), typewriter(ln, lp, cursor=False), font=F(ML, 21), fill=col + (255,))
        bp = clamp01((q - 0.62) / 0.36)
        y = pad + h - 96
        d.rounded_rectangle([pad + 24, y, pad + w - 24, y + 26], 12, fill=CHAR + (255,))
        if bp > 0:
            d.rounded_rectangle([pad + 24, y, pad + 24 + int((w - 48) * bp), y + 26], 12, fill=PINK + (255,))
        d.text((pad + w - 24, y + 52), f"{int(bp * 100)}%", font=F(AR, 30), fill=(NEON if bp >= 1 else SILVER) + (255,),
               anchor="rm")
        d.text((pad + 24, y + 52), "model: jev" if bp < 1 else "ready: search any app", font=F(ML, 20),
               fill=(NEON if bp >= 1 else STEEL) + (255,), anchor="lm")
        return card
    return cached(("train", k, w, h), build)


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
        y = bubble(d, pad + 24, y, "@you: APPS", fnt, CHAR + (255,), SILVER + (255,))
        if q > 0.3:
            d.text((pad + w / 2, y + 6), "▼  keyword matched", font=MONO_S, fill=NEON + (255,), anchor="mt")
            y += 48
        if q > 0.5:
            y = bubble(d, pad + w - 24, y, typewriter("Here's the site!", (q - 0.5) / 0.3, cursor=False),
                       fnt, NEON + (255,), INK + (255,), right=True)
        if q > 0.85:
            bubble(d, pad + w - 24, y, "10k x Jev  ·  link", MONO_S, BLUE + (255,), INK + (255,), right=True)
        return card
    return cached(("inbox", k, w, h), build)


# ───────────────────────────── sections ─────────────────────────────

def hook(layer, lt):
    """Frame 0 = the live site (cat-icon results). WILDEST slam, then the JEV billboard."""
    t_b_out = T_JEV - 0.18
    if lt < T_JEV:
        place(layer, broll_view(1.75 + lt * 0.8, w=1000, h=540, accent=PINK), 540, 80, lt, -0.4, dur=0.01,
              idle=0, exit_at=t_b_out)
        place(layer, os_chip("APP STORE  x  AI", PINK, 30), 230, -168, lt, -0.4, dur=0.01, idle=0, exit_at=t_b_out)
        if lt >= T_WILD:
            place(layer, stamp("WILDEST", RED, 120, pad=48), 540, 150, lt, T_WILD, dur=0.14, frm="down",
                  scale_pop=True, tilt=-6, idle=0, exit_at=t_b_out)
            light_hit(layer, 540, 150 + PACK_DY, lt, T_WILD, RED)
        if lt < t_b_out + 0.2:
            guarded_conveyor(layer, 490 + PACK_DY - 4, lt, lane_marks(120), conveyor_marks, name="app-lane",
                             speed=190, gap=22)
        return
    place(layer, jev_wordmark(960, 140), 540, -150, lt, T_JEV, dur=0.2, frm="down", scale_pop=True, idle=0)
    bloom_orb(layer, 290, 180 + PACK_DY, 230, PINK, a=70)
    place(layer, jev_hero(400), 290, 180, lt, T_JEV + 0.05, dur=0.24, frm="left", scale_pop=True, idle=0)
    light_hit(layer, 290, 180 + PACK_DY, lt, T_JEV, PINK)
    light_rays(layer, 290, 180 + PACK_DY, lt, PINK)
    if lt >= T_CASES:
        place(layer, os_chip("AI USE CASE", PINK, 32), 290, 430, lt, T_CASES, dur=0.2, frm="up", idle=0)
    t_gif = T_SEEN - 0.1
    if lt < t_gif:
        place(layer, figure_round("diogo-almeida", 380, ring=PINK), 790, 170, lt, T_JEV + 0.15,
              dur=0.26, frm="right", scale_pop=True, tilt=4, idle=0, exit_at=t_gif - 0.2)
        place(layer, name_plate("Diogo Almeida", "TypeSafe CEO"), 790, 410, lt, T_JEV + 0.3, frm="down",
              idle=0, exit_at=t_gif - 0.2)
    else:
        front_gif(gif_card("mind-blown", max(0, lt - t_gif), w=420, frame="round"), 790, 200, lt, t_gif,
                  **entrance(1), idle=0)


def grab(layer, lt, a):
    t_gr, t_best, t_win = T_GRABBED - a, T_BEST - a, T_WINNING - a
    t_mob, t_goo = T_MOBILE - a, T_GOOGLE - a
    ex = t_mob - 0.2
    if lt < t_mob - 0.05:
        title = "SOMEONE GRABBED ALL" if lt < t_best - 0.05 else "THE BEST WINNING APPS"
        place(layer, title_card(title, ORANGE, fsz=74, h=140), 540, -150, lt, 0.0 if lt < t_best - 0.05 else t_best,
              dur=0.2, frm="down", scale_pop=lt >= t_best - 0.05, idle=0, exit_at=ex)
        front_gif(gif_card("take-it", max(0, lt - t_gr), w=400, frame="round"), 260, 180, lt, t_gr,
                  **entrance(0), idle=0, exit_at=ex)
        n = 1 + int(clamp01((lt - t_gr) / 1.4) * (len(TOP_ROWS) - 1)) if lt >= t_gr else 1
        place(layer, top_chart_card(n), 780, 170, lt, -0.4, dur=0.01, idle=0, exit_at=ex)
        if lt >= t_win:
            place(layer, stamp("WINNERS ONLY", NEON, 52), 780, 330, lt, t_win, dur=0.14, frm="down",
                  scale_pop=True, tilt=-6, idle=0, exit_at=ex)
            light_hit(layer, 780, 330 + PACK_DY, lt, t_win, NEON)
    else:
        bloom_orb(layer, 280, 20 + PACK_DY, 160, BLUE, a=60)
        place(layer, logo_badge("app-store", 230, fill=WHITE + (255,), punch=False), 280, 10, lt, t_mob,
              dur=0.2, frm="left", scale_pop=True, tilt=-4, idle=0)
        place(layer, figure_round("tim-cook", 290, ring=BLUE), 280, 285, lt, t_mob + 0.1, frm="up", tilt=-3, idle=0)
        if lt >= t_goo:
            bloom_orb(layer, 800, 20 + PACK_DY, 160, NEON, a=60)
            place(layer, logo_badge("google-play", 230, fill=WHITE + (255,), punch=False), 800, 10, lt, t_goo,
                  dur=0.2, frm="right", scale_pop=True, tilt=4, idle=0)
            place(layer, figure_round("sundar-pichai", 290, ring=NEON), 800, 285, lt, t_goo + 0.1, frm="up",
                  tilt=3, idle=0)
        if lt >= t_goo + 0.3:
            place(layer, stamp("+", ORANGE, 90, pad=30), 540, 140, lt, t_goo + 0.3, dur=0.14, scale_pop=True, idle=0)
    guarded_conveyor(layer, 490 + PACK_DY - 4, lt, lane_marks(120), conveyor_marks, name="app-lane",
                     speed=190, gap=22)


def trained(layer, lt, a):
    t_tr, t_j = T_TRAINED - a, T_JEV2 - a
    p = clamp01((lt - t_tr) / max(0.4, (T_SO - a) - t_tr - 0.15)) if lt >= t_tr else 0.0
    place(layer, train_card(p), 360, 150, lt, -0.4, dur=0.01, idle=0)
    if lt < t_j - 0.05:
        front_gif(gif_card("training", max(0, lt - t_tr), w=400, frame="round"), 830, 150, lt, t_tr,
                  **entrance(5), idle=0, exit_at=t_j - 0.22)
    else:
        bloom_orb(layer, 830, 140 + PACK_DY, 200, PINK, a=80)
        place(layer, jev_hero(340), 830, 140, lt, t_j, dur=0.16, frm="down", scale_pop=True, idle=0)
        light_hit(layer, 830, 140 + PACK_DY, lt, t_j, PINK)
        place(layer, os_chip("JEV AI MODEL", PINK, 32), 830, 360, lt, t_j + 0.15, frm="up", idle=0)
    guarded_conveyor(layer, 490 + PACK_DY - 4, lt + 3.0, lane_marks(120), conveyor_marks, name="app-lane",
                     speed=190, gap=22)


QUERIES = [(1.45, "CAT ICON", ORANGE), (1.95, "DOG ICON", NEON), (3.0, "ROBOT ICON", CYAN), (4.4, "COOKING APP", PINK)]


def search(layer, lt, a):
    t = a + lt
    src = t - SEARCH_SHIFT
    place(layer, broll_view(src, accent=NEON), 540, 70, lt, -0.4, dur=0.01, idle=0)
    shown = [q for q in QUERIES if src >= q[0]]
    xs = [180, 420, 660, 900]
    for i, (qs, txt, col) in enumerate(shown):
        place(layer, os_chip(txt, col, 30), xs[i], 440, lt, qs + SEARCH_SHIFT - a, dur=0.22,
              **{k: v for k, v in entrance(i + 2).items() if k in ("frm", "tilt")}, idle=0)
    t_cat = T_CATEGORY - a
    if t_cat <= lt < T_THINK - a + 0.2:
        place(layer, stamp("ANY CATEGORY", ORANGE, 64), 720, 270, lt, t_cat, dur=0.14, frm="down",
              scale_pop=True, tilt=-5, idle=0, exit_at=T_THINK - a)
        light_hit(layer, 720, 270 + PACK_DY, lt, t_cat, ORANGE)
    t_th = T_THINK - a
    if lt >= t_th - 0.1:
        front_gif(gif_card("searching", max(0, lt - t_th), w=320, frame="round"), 860, 250, lt, t_th - 0.1,
                  **entrance(4), idle=0)
    if lt < T_SEARCH - a + 0.9 and lt >= T_SEARCH - a:
        place(layer, stamp("SEARCH", NEON, 70), 300, 260, lt, T_SEARCH - a, dur=0.14, frm="down", scale_pop=True,
              tilt=5, idle=0, exit_at=T_SEARCH - a + 0.7)


def compete(layer, lt, a):
    t = a + lt
    src = t - SEARCH_SHIFT
    t_c, t_g, t_p = T_COMPET - a, T_GENERATE - a, T_PERF - a
    place(layer, broll_view(src, accent=ORANGE), 540, 70, lt, -0.4, dur=0.01, idle=0)
    items = [("FIND COMPETITORS", t_c, RED), ("NEW IDEAS", t_g, CYAN), ("TOP PERFORMERS", t_p, NEON)]
    xs = [215, 545, 860]
    for (txt, ti, col), x in zip(items, xs):
        place(layer, check_chip(txt, lt >= ti, col, 28), x, 440, lt, -0.4, dur=0.01, idle=0)
        if lt >= ti:
            light_hit(layer, x, 440 + PACK_DY, lt, ti, col)
    if t_c <= lt < t_g - 0.05:
        front_gif(gif_card("spying", max(0, lt - t_c), w=320, frame="round"), 860, 230, lt, t_c,
                  **entrance(6), idle=0, exit_at=t_g - 0.25)
    t_i = T_IDEAS - a
    if t_i - 0.1 <= lt < t_p - 0.05:
        front_gif(gif_card("idea", max(0, lt - t_i), w=320, frame="round"), 860, 230, lt, t_i - 0.1,
                  **entrance(3), idle=0, exit_at=t_p - 0.25)


def year(layer, lt, a):
    t_y = T_2026 - a
    t_land = t_y + 0.65
    p = 0.0 if lt < t_y else clamp01((lt - t_y) / (t_land - t_y))
    beat = {"t": T_2026, "value": 2026, "style": "year"}
    place(layer, odometer_card(beat, p, w=1000, h=400, label="BEST PERFORMING APPS", accent=NEON),
          540, 120, lt, -0.4, dur=0.01, idle=0)
    if lt >= t_land:
        light_hit(layer, 540, 120 + PACK_DY, lt, t_land, NEON)
    guarded_conveyor(layer, 490 + PACK_DY - 4, lt + 6.0, lane_marks(120), conveyor_marks, name="app-lane",
                     speed=190, gap=22)


def cta(layer, lt, a):
    t_m, t_w, t_c = T_MARKET - a, T_WEBSITE - a, T_COMMENT - a
    if lt < t_c - 0.05:
        ex = t_c - 0.24
        place(layer, broll_view(7.6 + lt * 0.9, w=960, h=500, accent=BLUE), 540, 120, lt, -0.4, dur=0.01,
              idle=0, exit_at=ex)
        if lt >= t_m:
            place(layer, title_card("YOUR OWN MARKET RESEARCH", BLUE, fsz=62, h=120), 540, -170, lt, t_m,
                  dur=0.18, frm="down", scale_pop=True, idle=0, exit_at=ex)
        if lt >= t_w:
            place(layer, os_chip("THIS WEBSITE", CYAN, 34), 540, 420, lt, t_w, dur=0.18, frm="up",
                  scale_pop=True, idle=0, exit_at=ex)
        return
    place(layer, title_card("COMMENT  \"APPS\"", NEON, fsz=80, h=140), 540, -150, lt, t_c, dur=0.18,
          scale_pop=True, idle=0)
    light_hit(layer, 540, -150 + PACK_DY, lt, t_c, NEON)
    light_rays(layer, 540, -150 + PACK_DY, lt, NEON)
    front_gif(gif_card("comment", max(0, lt - t_c), w=420, frame="round"), 270, 220, lt, t_c + 0.08,
              **entrance(2), idle=0)
    place(layer, inbox_card(clamp01((lt - t_c - 0.1) / 0.9)), 790, 220, lt, t_c + 0.12, frm="right", idle=0)


def scene(layer, name, lt, a):
    {
        "hook": lambda: hook(layer, lt),
        "grab": lambda: grab(layer, lt, a),
        "trained": lambda: trained(layer, lt, a),
        "search": lambda: search(layer, lt, a),
        "compete": lambda: compete(layer, lt, a),
        "year": lambda: year(layer, lt, a),
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


PUNCH_T = [T_JEV, T_JEV2, T_COMPET]                      # one hero word per section, >=8s apart
HIT_T = [T_WILD, T_JEV, T_JEV2, T_CATEGORY, T_2026 + 0.65, T_COMMENT]
CUT_T = [T_SOMEONE, T_THEN, T_SO, T_OF2026, T_IF]        # search -> compete is one continuous b-roll shot
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
