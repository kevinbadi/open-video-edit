#!/usr/bin/env python3
"""Split animated talking-head: Social Agents (open-source repo kills the SMM).

1080x1920. Sequel to social-sdk-killed-hootsuite: invader shoots Hootsuite +
Sprout, KILLED stamp on the managers line, the real `npm start` terminal
recording (Kevin's b-roll) as the reveal + live card, then every spoken skill
ticks on a checklist with a real visual (our own reel covers, thumbnails, a
comment-to-DM inbox, caption, hashtags, SEO climb) and a terminal crop of the
matching line.
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


T_CLAUDE = trel("claude")
T_REPLACE = trel("replace")
T_SCHED = trel("scheduling")
T_HOOT = trel("hootsuite")
T_SPROUT = trel("sprout")
T_ITS = trel("it's")
T_KILLED = trel("killed")
T_SOCIAL1 = trel("social", 4.9)
T_MARKETING = trel("marketing", 5.0)
T_MANAGERS = trel("managers")
T_OPEN = trel("open")
T_REPO = trel("repo")
T_LAUNCHED = trel("launched")
T_SA = trel("social", 9.0)
T_HERES = trel("here's")
T_NPM = trel("npm")
T_COMMAND = trel("command")
T_AGENT = trel("agent", 13.0)
T_SUDDEN = trel("sudden")
T_SKILLS = trel("skills")
T_SENIOR = trel("senior")
T_FROM = trel("from", 18.0)
T_COVER = trel("cover")
T_THUMBS = trel("thumbnails")
T_CDM = trel("comment", 20.5)
T_RESP = trel("responding")
T_CAPTIONS = trel("captions")
T_HASH = trel("hashtags")
T_SEO = trel("seo")
T_LIST = trel("the", 26.0)
T_RID0 = trel("it's", 27.5)
T_RID = trel("ridiculous")
T_IF = trel("if", 28.0)
T_ACCESS = trel("access")
T_COMMENT = trel("comment", 30.0)

SECT = [
    ("hook", 0.00, T_ITS),
    ("managers", T_ITS, T_OPEN),
    ("repo", T_OPEN, T_HERES),
    ("npm", T_HERES, T_FROM),
    ("skills", T_FROM, T_LIST),
    ("list", T_LIST, T_IF),
    ("cta", T_IF, DUR + 0.05),
]
KEYWORDS = {
    "claude", "hootsuite", "sprout", "killed", "managers", "open", "source", "repo",
    "agents", "npm", "start", "skills", "senior", "cover", "thumbnails", "comment",
    "dm", "captions", "hashtags", "seo", "ridiculous", "social",
}
KEY_COL = {
    "claude": ORANGE, "hootsuite": RED, "sprout": NEON, "killed": RED, "managers": RED,
    "open": NEON, "source": NEON, "repo": NEON, "agents": ORANGE, "social": NEON,
    "npm": RED, "start": NEON, "skills": NEON, "senior": ORANGE, "cover": CYAN,
    "thumbnails": ORANGE, "comment": NEON, "dm": NEON, "captions": CYAN,
    "hashtags": ORANGE, "seo": BLUE, "ridiculous": RED,
}
SECT_ACCENT = {
    "hook": ORANGE, "managers": RED, "repo": NEON, "npm": BLUE,
    "skills": NEON, "list": ORANGE, "cta": NEON,
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
    "managers": textured_bg((50, 32, 36), 23, RED),
    "repo": textured_bg((36, 48, 42), 11, NEON),
    "npm": textured_bg((32, 40, 52), 13, BLUE),
    "skills": textured_bg((34, 46, 44), 29, NEON),
    "list": textured_bg((48, 38, 32), 31, ORANGE),
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


# ───────────────────────────── b-roll: Kevin's `npm start` recording ─────────────────────────────

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
        if len(self.cache) > 12:
            self.cache.clear()
        self.cache[i] = img
        return img


BROLL = Broll("assets/broll/npm-start.mov")
TX0, TX1 = 448, 1471                       # terminal window inside the 1920 frame
CROPS = {                                  # (src_t, box)
    "banner": (7.8, (TX0, 288, TX1, 645)),
    "cmd": (0.2, (TX0, 104, 1180, 136)),
    "msg": (7.8, (TX0, 962, 1250, 1052)),
    "posts": (8.7, (TX0, 1044, 1180, 1068)),
    "longform": (7.8, (TX0, 742, 1100, 766)),
    "posting": (7.8, (TX0, 700, TX1, 862)),
}
BROLL_T0 = T_NPM - 0.15                    # recording's src 0 lands just before "NPM"


def crop_img(kind, w, radius=18, glow=None):
    src_t, box = CROPS[kind]

    def build():
        fr = BROLL.frame(src_t)
        im = fr.crop(box)
        h = int(im.height * w / im.width)
        im = im.resize((w, h), Image.LANCZOS).convert("RGBA")
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=255)
        im.putalpha(mask)
        pad = 14
        card = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
        if glow:
            gl = Image.new("RGBA", card.size, (0, 0, 0, 0))
            ImageDraw.Draw(gl).rounded_rectangle([4, 4, card.width - 5, card.height - 5], radius + 8, fill=glow + (120,))
            card.alpha_composite(gl.filter(ImageFilter.GaussianBlur(9)))
        ImageDraw.Draw(card).rounded_rectangle([pad - 4, pad - 4, pad + w + 3, pad + h + 3], radius + 4,
                                               fill=TERM_BG + (255,), outline=(glow or STEEL) + (200,), width=3)
        card.alpha_composite(im, (pad, pad))
        return card
    return cached(("crop", kind, w, glow), build)


def strip_card(kind, w=960, label=None, accent=NEON):
    """Terminal line crop as a HUD strip: 'LIVE FROM THE REPO' tab + the real line."""
    def build():
        c = crop_img(kind, w - 20, radius=10)
        tab_h = 40 if label else 0
        img = Image.new("RGBA", (c.width, c.height + tab_h), (0, 0, 0, 0))
        if label:
            d = ImageDraw.Draw(img)
            fnt = F(AR, 22)
            tw = d.textlength(label, font=fnt)
            d.rounded_rectangle([14, 0, 14 + tw + 34, tab_h + 10], 10, fill=accent + (255,))
            d.text((31, tab_h / 2 + 2), label, font=fnt, fill=INK + (255,), anchor="lm")
        img.alpha_composite(c, (0, tab_h))
        return img
    return cached(("strip", kind, w, label, accent), build)


def broll_view(src_t, y_off, w=1000, h=700, hl=0.0, accent=BLUE, zoom=1.0):
    """Live terminal card. y_off scrolls down the window as output fills.
    zoom>1 punches in on the `npm start` line (top-left) before the banner loads."""
    fr = BROLL.frame(src_t)
    if fr is None:
        return None
    full = TX1 - TX0
    sw = full / zoom
    sh = h * sw / w
    zx = 110 * (zoom - 1) / 0.8            # pan toward the command as we punch in
    zy = 50 * (zoom - 1) / 0.8
    x0 = TX0 + zx
    y0 = max(0, min(1080 - sh, y_off + zy))
    im = fr.crop((int(x0), int(y0), int(x0 + sw), int(y0 + sh))).resize((w, h), Image.BILINEAR).convert("RGBA")
    sc = w / sw
    if hl > 0:
        d = ImageDraw.Draw(im)
        bx0, by0, bx1, by1 = (TX0 + 296 - x0) * sc, (104 - y0) * sc, (TX0 + 672 - x0) * sc, (136 - y0) * sc
        x1 = bx0 + (bx1 - bx0) * clamp01(hl)
        d.rounded_rectangle([bx0 - 8, by0 - 6, x1 + 8, by1 + 6], 8, outline=NEON + (255,), width=4)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], 20, fill=255)
    im.putalpha(mask)
    pad = 12
    card = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, card.width - 1, card.height - 1], 28, fill=GRAPHITE + (255,))
    card.alpha_composite(im, (pad, pad))
    d = ImageDraw.Draw(card)
    d.rectangle([0, 30, 8, card.height - 30], fill=accent + (255,))
    d.rounded_rectangle([w - 110, pad + 16, w - 4, pad + 56], 12, fill=INK + (220,))
    d.ellipse([w - 98, pad + 28, w - 82, pad + 44], fill=RED + (255,))
    d.text((w - 72, pad + 22), "LIVE", font=F(AR, 24), fill=SILVER + (255,))
    return card


# ───────────────────────────── skills section visuals ─────────────────────────────

SKILL_ROWS = [
    ("Cover photos", "cover"),
    ("Thumbnails", "thumbnails"),
    ("Comment-to-DM", "cdm"),
    ("Message replies", "resp"),
    ("Captions", "captions"),
    ("Hashtags", "hashtags"),
    ("SEO ranking", "seo"),
]


def checklist_card(n_done, active, w=440):
    row_h = 66

    def build():
        h = 84 + row_h * len(SKILL_ROWS) + 12
        card = shadow_card((w, h), 26, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rectangle([pad, pad + 20, pad + 8, pad + h - 20], fill=NEON + (255,))
        d.text((pad + 30, pad + 22), "SKILLS LOADED", font=F(AR, 34), fill=WHITE + (255,))
        d.text((pad + w - 26, pad + 32), f"{n_done}/{len(SKILL_ROWS)}", font=F(AR, 26),
               fill=(NEON if n_done else STEEL) + (255,), anchor="ra")
        for i, (label, _) in enumerate(SKILL_ROWS):
            y = pad + 84 + i * row_h
            on = i < n_done
            if i == active:
                d.rounded_rectangle([pad + 18, y - 4, pad + w - 18, y + row_h - 10], 14, fill=CHAR + (255,),
                                    outline=NEON + (200,), width=2)
            bx = pad + 34
            d.rounded_rectangle([bx, y + 10, bx + 34, y + 44], 8, outline=(NEON if on else STEEL) + (255,), width=3,
                                fill=(NEON + (255,)) if on else None)
            if on:
                d.line([(bx + 7, y + 27), (bx + 15, y + 36), (bx + 28, y + 17)], fill=INK + (255,), width=5)
            d.text((bx + 54, y + 27), label.upper(), font=F(AR, 30),
                   fill=(WHITE if on else STEEL) + (255,), anchor="lm")
        return card
    return cached(("checklist", n_done, active, w), build)


def bubble(d, x, y, txt, fnt, fill, fg, right=False, maxw=360):
    tw = d.textlength(txt, font=fnt)
    bw = min(maxw, tw + 40)
    x0 = x - bw if right else x
    d.rounded_rectangle([x0, y, x0 + bw, y + 58], 24, fill=fill)
    d.text((x0 + 20, y + 29), txt, font=fnt, fill=fg, anchor="lm")
    return y + 72


def inbox_card(stage, p, w=500, h=500):
    """Comment-to-DM + auto replies. stage 0: comment -> DM. stage 1: replies."""
    k = int(p * 24)

    def build():
        card = shadow_card((w, h), 26, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        ig = logo_badge("instagram", 64, fill=CHAR + (255,))
        if ig is not None:
            card.alpha_composite(ig, (pad + 10, pad + 2))
        d.text((pad + 110, pad + 36), "INBOX  ·  AUTO", font=F(AR, 30), fill=WHITE + (255,), anchor="lm")
        d.ellipse([pad + w - 44, pad + 28, pad + w - 24, pad + 48], fill=NEON + (255,))
        fnt = F(AR, 28)
        y = pad + 110
        q = k / 24
        if stage == 0:
            y = bubble(d, pad + 24, y, "@maya: SOCIAL", fnt, CHAR + (255,), SILVER + (255,))
            if q > 0.25:
                d.text((pad + w / 2, y + 6), "▼  keyword matched", font=MONO_S,
                       fill=NEON + (255,), anchor="mt")
                y += 48
            if q > 0.45:
                y = bubble(d, pad + w - 24, y, typewriter("Here's your link!", (q - 0.45) / 0.35, cursor=False),
                           fnt, NEON + (255,), INK + (255,), right=True)
            if q > 0.85:
                bubble(d, pad + w - 24, y, "creatoros.ca/go/social", MONO_S, BLUE + (255,), INK + (255,), right=True)
        else:
            y = bubble(d, pad + 24, y, "how much is it??", fnt, CHAR + (255,), SILVER + (255,))
            if q > 0.2:
                y = bubble(d, pad + w - 24, y, typewriter("Free to start. Link sent!", (q - 0.2) / 0.35, cursor=False),
                           fnt, NEON + (255,), INK + (255,), right=True)
            if q > 0.6:
                y = bubble(d, pad + 24, y, "legend, thank you", fnt, CHAR + (255,), SILVER + (255,))
            if q > 0.8:
                bubble(d, pad + w - 24, y, "Anytime!", fnt, NEON + (255,), INK + (255,), right=True)
        return card
    return cached(("inbox", stage, k, w, h), build)


CAPTION_TXT = "Your AI agent just replaced the whole social team."


def caption_card(p, w=500):
    k = int(p * 40)

    def build():
        thumb = Image.open("assets/thumbs/t2.png").convert("RGB")
        th = int(thumb.height * (w - 40) / thumb.width)
        thumb = thumb.resize((w - 40, th), Image.LANCZOS)
        h = th + 230
        card = shadow_card((w, h), 26, GRAPHITE + (255,))
        pad = 32
        card.paste(thumb, (pad + 20, pad + 20))
        d = ImageDraw.Draw(card)
        d.text((pad + 20, pad + th + 40), "CAPTION", font=F(AR, 24), fill=CYAN + (255,))
        shown = typewriter(CAPTION_TXT, k / 40, cursor=False)
        lines, cur = [], ""
        fnt = F(AR, 32)
        for wd in shown.split(" "):
            test = (cur + " " + wd).strip()
            if d.textlength(test, font=fnt) > w - 50:
                lines.append(cur)
                cur = wd
            else:
                cur = test
        lines.append(cur)
        for i, ln in enumerate(lines[:3]):
            d.text((pad + 20, pad + th + 76 + i * 44), ln, font=fnt, fill=WHITE + (255,))
        return card
    return cached(("capcard", k, w), build)


HASHTAGS = [("#socialmedia", ORANGE), ("#aiagents", NEON), ("#contentcreator", CYAN),
            ("#marketing", RED), ("#creatoros", NEON)]


def hash_chip(txt, col):
    def build():
        fnt = F(AR, 38)
        tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(txt, font=fnt))
        w, h = tw + 44, 70
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 35, fill=GRAPHITE + (255,), outline=col + (255,), width=4)
        d.text((w / 2, h / 2 - 2), txt, font=fnt, fill=col + (255,), anchor="mm")
        return img
    return cached(("hash", txt, col), build)


def seo_card(p, w=500, h=470):
    """Search results: our repo climbs from #5 to #1."""
    k = int(p * 30)

    def build():
        card = shadow_card((w, h), 26, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        g = logo_badge("google", 60, fill=WHITE + (255,))
        if g is not None:
            card.alpha_composite(g, (pad + 22, pad + 22))
        d.rounded_rectangle([pad + 92, pad + 24, pad + w - 22, pad + 74], 25, fill=CHAR + (255,))
        d.text((pad + 116, pad + 49), "social media agent", font=MONO_S, fill=SILVER + (255,), anchor="lm")
        others = ["hootsuite.com", "sproutsocial.com", "later.com", "buffer.com"]
        q = ease(k / 30)
        ours = 4 - 4 * q                       # slot index: 4 -> 0
        row_h = 70
        top = pad + 104
        for i, name in enumerate(others):
            s_ = i + clamp01(i + 1 - ours)
            y = top + s_ * row_h
            d.rounded_rectangle([pad + 20, y, pad + w - 20, y + row_h - 12], 12, fill=CHAR + (255,))
            d.text((pad + 40, y + (row_h - 12) / 2), f"{name}", font=F(AR, 28), fill=STEEL + (255,), anchor="lm")
        y = top + ours * row_h
        d.rounded_rectangle([pad + 12, y - 4, pad + w - 12, y + row_h - 8], 14, fill=INK + (255,),
                            outline=NEON + (255,), width=4)
        d.text((pad + 36, y + (row_h - 12) / 2), "creatoros / social-agents", font=F(AR, 30),
               fill=WHITE + (255,), anchor="lm")
        rank = max(1, int(round(5 - 4 * q)))
        d.text((pad + w - 36, y + (row_h - 12) / 2), f"#{rank}", font=F(AR, 38),
               fill=(NEON if rank == 1 else ORANGE) + (255,), anchor="rm")
        return card
    return cached(("seo", k, w, h), build)


def repo_card(p, w=520, h=300):
    k = int(p * 30)

    def build():
        card = shadow_card((w, h), 26, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        gh = logo_badge("github", 60, fill=WHITE + (255,))
        if gh is not None:
            card.alpha_composite(gh, (pad + 24, pad + 24))
        d.text((pad + 96, pad + 52), "creatoros / ", font=F(AR, 34), fill=SILVER + (255,), anchor="lm")
        tw = d.textlength("creatoros / ", font=F(AR, 34))
        d.text((pad + 96 + tw, pad + 52), "social-agents", font=F(AR, 34), fill=WHITE + (255,), anchor="lm")
        d.rounded_rectangle([pad + 24, pad + 100, pad + 124, pad + 138], 19, outline=NEON + (255,), width=3)
        d.text((pad + 74, pad + 119), "Public", font=F(AR, 22), fill=NEON + (255,), anchor="mm")
        desc = typewriter("the operating system for social media", k / 30, cursor=False)
        d.text((pad + 24, pad + 172), desc, font=MONO_S, fill=SILVER + (255,))
        d.ellipse([pad + 24, pad + 226, pad + 42, pad + 244], fill=BLUE + (255,))
        d.text((pad + 54, pad + 235), "TypeScript", font=F(AR, 24), fill=STEEL + (255,), anchor="lm")
        d.text((pad + 200, pad + 235), "MIT  ·  open source", font=F(AR, 24), fill=STEEL + (255,), anchor="lm")
        return card
    return cached(("repo", k, w, h), build)


def scroll_list_card(off, w=500, h=560):
    """The recording's skill list, scrolling like a ticker: 'the list goes on'."""
    def src():
        fr = BROLL.frame(8.4)
        im = fr.crop((TX0, 650, TX0 + 690, 1080))
        sc = w / im.width
        im = im.resize((w, int(im.height * sc)), Image.LANCZOS)
        tall = Image.new("RGB", (w, im.height * 2), TERM_BG)
        tall.paste(im, (0, 0))
        tall.paste(im, (0, im.height))
        return tall
    tall = cached(("listsrc", w), src)
    half = tall.height // 2
    y0 = int(off) % half
    view = tall.crop((0, y0, w, y0 + h - 60)).convert("RGBA")
    card = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, card.width - 1, card.height - 1], 26, fill=GRAPHITE + (255,))
    d.text((24, 36), "SOCIAL AGENTS  ·  SKILLS", font=F(AR, 28), fill=WHITE + (255,), anchor="lm")
    mask = Image.new("L", view.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, view.width - 1, view.height - 1], 16, fill=255)
    view.putalpha(mask)
    card.alpha_composite(view, (12, 72))
    fade = Image.new("RGBA", (w, 60), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for i in range(60):
        fd.line([(0, i), (w, i)], fill=GRAPHITE + (int(255 * i / 60),))
    card.alpha_composite(fade, (12, card.height - 12 - 60))
    return card


# ───────────────────────────── sections ─────────────────────────────

INV_C = (300, 190)
HOOT_C = (810, 60)
SPR_C = (810, 300)


def layer_pt(authored):
    return authored[0], authored[1] + PACK_DY


def shoot_target(layer, slug, authored, lt, t_word, muzzle, accent):
    cx, cy = layer_pt(authored)
    arrive = t_word - 0.1
    impact = t_word + 0.28
    if lt < arrive:
        place(layer, reticle(270, accent, locked=lt > t_word - 0.7), authored[0], authored[1],
              lt, -0.4, dur=0.01, idle=0)
        return
    badge = logo_badge(slug, size=260, punch=True, fill=WHITE + (255,))
    if lt < impact:
        place(layer, badge, authored[0], authored[1], lt, arrive, dur=0.14,
              frm="right", scale_pop=True, tilt=-3, idle=0)
        if muzzle and lt >= t_word - 0.02:
            laser(layer, muzzle[0], muzzle[1], cx, cy, (lt - (t_word - 0.02)) / 0.30, accent)
        return
    age = lt - impact
    if age < 0.85 and badge is not None:
        shatter(layer, badge, cx, cy, age)
        if age < 0.45:
            place(layer, stamp("REPLACED", RED, 44), authored[0], authored[1] + 16, lt, impact, dur=0.1,
                  frm="down", scale_pop=True, tilt=-8, idle=0, exit_at=impact + 0.62)
        light_hit(layer, cx, cy, lt, impact, accent)


def hook(layer, lt):
    """Frame 0: giant invader + two locked reticles. Shoots Hootsuite, then Sprout."""
    gw = ghost_word("SCHEDULING TOOLS", 74, 40)
    layer.alpha_composite(gw, (W - gw.width - 30, 6))
    looking = layer_pt(HOOT_C if lt < T_HOOT + 0.35 else SPR_C)
    aim = (INV_C[0] + 150, INV_C[1] + PACK_DY - 20)
    grab_t = 0.85 if lt >= T_REPLACE else 0.0
    bloom_orb(layer, INV_C[0], INV_C[1] + PACK_DY, 230, ORANGE, a=70)
    if lt < T_REPLACE:
        place_claude_sphinx(layer, INV_C[0] - 150, INV_C[1] + PACK_DY - 200, lt, size=150)
    pose = place_claude_invader(layer, INV_C[0], INV_C[1] + PACK_DY, lt, size=460,
                                look_at=looking, grab="right", grab_at=aim, grab_t=grab_t)
    muzzle = (int((INV_C[0] - pose.origin[0]) + pose.right_hand[0]),
              int((INV_C[1] + PACK_DY - pose.origin[1]) + pose.right_hand[1]))
    shoot_target(layer, "hootsuite", HOOT_C, lt, T_HOOT, muzzle, RED)
    if lt >= T_HOOT + 0.45:
        shoot_target(layer, "sprout-social", SPR_C, lt, T_SPROUT, muzzle, NEON)
    else:
        place(layer, reticle(270, NEON, locked=False), SPR_C[0], SPR_C[1], lt, -0.4, dur=0.01, idle=0)
    place(layer, os_chip("CLAUDE", ORANGE, 30), INV_C[0], 430, lt, -0.4, dur=0.01, idle=0, exit_at=T_SCHED)
    if T_SCHED <= lt < T_HOOT - 0.12:
        place(layer, os_chip("TARGET LOCK", RED, 32), 560, -30, lt, T_SCHED, frm="down", idle=0, exit_at=T_HOOT - 0.1)


SOCIAL_LANE = ["instagram", "tiktok", "youtube", "x", "linkedin", "facebook", "threads"]


def managers(layer, lt, a):
    t_k = T_KILLED - a
    t_mk = T_MARKETING - a
    t_mg = T_MANAGERS - a
    t_soc = T_SOCIAL1 - a
    # cold-open atmosphere: the job still exists
    if lt < t_k:
        place(layer, title_card("SOCIAL MEDIA MANAGER", STEEL, fsz=64, h=130), 540, 60, lt, -0.4, dur=0.01, idle=0)
    elif lt < t_mk - 0.05:
        place(layer, title_card("SOCIAL MEDIA MANAGER", STEEL, fsz=64, h=130), 540, 60, lt, -0.4, dur=0.01, idle=0,
              exit_at=t_mk - 0.26)
        place(layer, stamp("KILLED", RED, 150, pad=48), 540, 150, lt, t_k, dur=0.14, frm="down",
              scale_pop=True, tilt=-7, idle=0, exit_at=t_mk - 0.24)
        light_hit(layer, 540, 150 + PACK_DY, lt, t_k, RED)
    else:
        strike = clamp01((lt - (t_mg + 0.1)) / 0.35)
        place(layer, title_card("MARKETING MANAGERS", RED, fsz=76, strike=strike), 540, -30, lt, t_mk,
              frm="left", tilt=-2, idle=0)
        front_gif(gif_card("fired", max(0, lt - t_mk), w=420, frame="round"), 270, 225, lt, t_mk, **entrance(3), idle=0)
        place(layer, logo_badge("linkedin", 200, fill=WHITE + (255,)), 800, 200, lt, t_mk + 0.08,
              frm="up", idle=0)
        if lt >= t_mg + 0.3:
            place(layer, stamp("REPLACED", RED, 52), 800, 215, lt, t_mg + 0.3, dur=0.12, frm="down",
                  scale_pop=True, tilt=8, idle=0)
    if lt >= t_soc - 0.05:
        marks = topic_marks(SOCIAL_LANE, size=120, fill=WHITE + (255,))
        guarded_conveyor(layer, 440 + PACK_DY, max(0, lt - (t_soc - 0.05)), marks,
                         conveyor_marks, name="social-lane", speed=190, gap=22)


def repo(layer, lt, a):
    t_repo = T_REPO - a
    t_l = T_LAUNCHED - a
    t_sa = T_SA - a
    if lt < t_sa - 0.05:
        ex = t_sa - 0.26
        place(layer, title_card("OPEN SOURCE", NEON, fsz=84, h=140), 540, -40, lt, 0.0, dur=0.22,
              frm="down", scale_pop=True, idle=0, exit_at=ex)
        place(layer, logo_badge("github", 300, fill=WHITE + (255,)), 210, 230, lt, 0.05, **entrance(1), idle=0, exit_at=ex)
        if lt >= t_repo - 0.05:
            place(layer, repo_card(clamp01((lt - t_repo) / 1.0)), 710, 210, lt, t_repo - 0.05, frm="right", idle=0, exit_at=ex)
        if lt >= t_l:
            place(layer, os_chip("JUST LAUNCHED", ORANGE, 32), 760, 400, lt, t_l, dur=0.18, frm="up",
                  scale_pop=True, idle=0, exit_at=ex)
        return
    # reveal: the real banner from his terminal
    place(layer, crop_img("banner", 980, glow=ORANGE), 540, 130, lt, t_sa, dur=0.2, scale_pop=True, idle=0)
    light_hit(layer, 540, 130 + PACK_DY, lt, t_sa, ORANGE)
    light_rays(layer, 540, 130 + PACK_DY, lt, ORANGE)
    if lt >= t_sa + 0.35:
        place(layer, crop_img("cmd", 820, glow=NEON), 540, 410, lt, t_sa + 0.35, frm="up", idle=0)


def npm(layer, lt, a):
    t = a + lt
    src_t = max(0.0, t - BROLL_T0)
    y_off = 364 * clamp01((src_t - 2.0) / 5.6)
    t_npm = T_NPM - a
    hl = clamp01((lt - t_npm) / 0.5) if lt >= t_npm else 0.0
    zp = clamp01((src_t - 0.85) / 0.45)
    zoom = 1.8 - 0.8 * (zp * zp * (3 - 2 * zp))
    place(layer, broll_view(src_t, y_off, hl=hl, zoom=zoom), 540, 190, lt, 0.0, dur=0.22, frm="up", idle=0)
    if lt < t_npm + 0.1:
        place(layer, stamp("HOW IT WORKS", ORANGE, 56), 540, 330, lt, 0.12, dur=0.16, frm="down",
              scale_pop=True, tilt=3, idle=0, exit_at=t_npm - 0.12)
    if t_npm <= lt < T_AGENT - a:
        place(layer, stamp("ONE COMMAND", NEON, 56), 540, 330, lt, t_npm + 0.1, dur=0.14, frm="down",
              scale_pop=True, tilt=-4, idle=0, exit_at=T_AGENT - a - 0.22)
    t_ag = T_AGENT - a
    if lt >= t_ag:
        ix, iy = 930, 470 + PACK_DY - 30
        bloom_orb(layer, ix, iy, 150, ORANGE, a=60)
        place_claude_invader(layer, ix, iy, lt, size=230, look_at=(540, 300))
    t_sud = T_SUDDEN - a
    if t_sud - 0.05 <= lt < T_SENIOR - a - 0.1:
        front_gif(gif_card("mind-blown", max(0, lt - t_sud), w=340, frame="round"), 210, 420, lt, t_sud - 0.05,
                  **entrance(4), idle=0, exit_at=T_SENIOR - a - 0.3)
    t_sk = T_SKILLS - a
    if t_sk <= lt < T_SENIOR - a:
        place(layer, os_chip("+ SKILLS INSTALLED", NEON, 32), 300, -170, lt, t_sk, frm="left", idle=0,
              exit_at=T_SENIOR - a - 0.2)
    t_sn = T_SENIOR - a
    if lt >= t_sn:
        place(layer, title_card("SENIOR MARKETING MANAGER", ORANGE, fsz=62, h=130), 540, 400, lt, t_sn,
              dur=0.16, frm="down", scale_pop=True, idle=0)
        place(layer, stamp("LEVEL UP", NEON, 40), 880, 300, lt, t_sn + 0.35, dur=0.12, frm="down",
              scale_pop=True, tilt=6, idle=0)
        light_hit(layer, 540, 400 + PACK_DY, lt, t_sn, ORANGE)


SKILL_T = [T_COVER, T_THUMBS, T_CDM, T_RESP, T_CAPTIONS, T_HASH, T_SEO]
STRIPS = {  # which real terminal line backs each skill
    0: ("posts", "LIVE FROM THE REPO"), 1: ("posts", "LIVE FROM THE REPO"),
    2: ("msg", "LIVE FROM THE REPO"), 3: ("msg", "LIVE FROM THE REPO"),
    4: ("posts", "LIVE FROM THE REPO"), 5: ("longform", "LIVE FROM THE REPO"),
    6: ("longform", "LIVE FROM THE REPO"),
}


def skills(layer, lt, a):
    t = a + lt
    n_done = sum(1 for ts in SKILL_T if t >= ts)
    active = n_done - 1
    place(layer, checklist_card(n_done, active), 255, 250, lt, -0.4, dur=0.01, idle=0)
    if active >= 0:
        kind, lab = STRIPS[active]
        first = active
        while first > 0 and STRIPS[first - 1][0] == kind:
            first -= 1
        place(layer, strip_card(kind, 960, lab), 540, -150, lt, SKILL_T[first] - a, dur=0.2, frm="down", idle=0)
    # right column visual per skill
    if active < 0:
        ix, iy = 790, 250 + PACK_DY
        bloom_orb(layer, ix, iy, 190, NEON, a=60)
        place_claude_invader(layer, ix, iy, lt, size=320, look_at=(255, 250 + PACK_DY))
        place(layer, os_chip("YOUR AI AGENT", NEON, 30), 790, 470, lt, -0.4, dur=0.01, idle=0)
        return
    ts = SKILL_T[active] - a
    nxt = (SKILL_T[active + 1] - a) if active + 1 < len(SKILL_T) else (T_LIST - a)
    ex = nxt - 0.22
    rx = 780
    if active == 0:
        for i, (dx, tilt) in enumerate([(-160, 8), (0, 0), (160, -8)]):
            place(layer, img_card(f"assets/covers/c{i + 1}.png", 250), rx + dx, 240 + abs(dx) * 0.12, lt,
                  ts + i * 0.1, dur=0.24, frm="up", tilt=tilt, idle=0, exit_at=ex)
        light_hit(layer, rx, 250 + PACK_DY, lt, ts, CYAN)
    elif active == 1:
        for i in range(3):
            place(layer, img_card(f"assets/thumbs/t{i + 1}.png", 470), rx, 60 + i * 175, lt, ts + i * 0.12,
                  **entrance(i + 5), idle=0, exit_at=ex)
    elif active == 2:
        place(layer, inbox_card(0, clamp01((lt - ts) / 1.2)), rx, 250, lt, ts, frm="right", tilt=3, idle=0, exit_at=ex)
    elif active == 3:
        place(layer, inbox_card(1, clamp01((lt - ts) / 1.3)), rx, 250, lt, -1, dur=0.01, idle=0, exit_at=ex)
    elif active == 4:
        place(layer, caption_card(clamp01((lt - ts) / 0.8)), rx, 250, lt, ts, frm="down", idle=0, exit_at=ex)
    elif active == 5:
        place(layer, caption_card(1.0), rx, 250, lt, -1, dur=0.01, idle=0, exit_at=ts - 0.02)
        spots = [(730, 20), (850, 130), (740, 240), (840, 350), (760, 460)]
        for i, ((txt, col), (x, y)) in enumerate(zip(HASHTAGS, spots)):
            place(layer, hash_chip(txt, col), x, y, lt, ts + i * 0.1, dur=0.2, frm="up",
                  scale_pop=True, tilt=(-5 if i % 2 else 5), idle=3, exit_at=ex)
    else:
        place(layer, seo_card(clamp01((lt - (ts + 0.2)) / 0.6)), rx, 250, lt, ts, frm="right", idle=0)
        if lt >= ts + 0.8:
            light_hit(layer, rx, 150 + PACK_DY, lt, ts + 0.8, NEON)


def list_sect(layer, lt, a):
    t_r0 = T_RID0 - a
    t_r = T_RID - a
    place(layer, scroll_list_card(lt * 260), 790, 250, lt, -0.4, dur=0.01, idle=0)
    if lt < t_r0 - 0.05:
        front_gif(gif_card("list-on", lt + 0.2, w=440, frame="round"), 270, 250, lt, -0.4, dur=0.01, idle=0,
                  exit_at=t_r0 - 0.24)
    else:
        front_gif(gif_card("ridiculous", max(0, lt - t_r0), w=440, frame="round"), 270, 250, lt, t_r0,
                  **entrance(6), idle=0)
        if lt >= t_r:
            place(layer, stamp("RIDICULOUS", RED, 60), 700, 40, lt, t_r, dur=0.14, frm="down",
                  scale_pop=True, tilt=-6, idle=0)
            light_hit(layer, 700, 40 + PACK_DY, lt, t_r, RED)


def cta(layer, lt, a):
    t_ac = T_ACCESS - a
    t_c = T_COMMENT - a
    if lt < t_c - 0.05:
        place(layer, crop_img("banner", 980, glow=ORANGE), 540, 120, lt, 0.0, dur=0.22, frm="up", idle=0,
              exit_at=t_c - 0.24)
        if lt >= t_ac:
            place(layer, os_chip("FREE ACCESS", NEON, 36), 540, 390, lt, t_ac, dur=0.2, frm="up",
                  scale_pop=True, idle=0, exit_at=t_c - 0.24)
        return
    place(layer, title_card("COMMENT  \"SOCIAL\"", NEON, fsz=78, h=140), 540, -20, lt, t_c, dur=0.18,
          scale_pop=True, idle=0)
    light_hit(layer, 540, -20 + PACK_DY, lt, t_c, NEON)
    light_rays(layer, 540, -20 + PACK_DY, lt, NEON)
    front_gif(gif_card("comment", max(0, lt - t_c), w=440, frame="round"), 270, 260, lt, t_c + 0.08,
              **entrance(2), idle=0)
    place(layer, inbox_card(0, clamp01((lt - t_c - 0.1) / 0.9), w=460, h=440), 790, 270, lt, t_c + 0.12,
          frm="right", idle=0)


def scene(layer, name, lt, a):
    {
        "hook": lambda: hook(layer, lt),
        "managers": lambda: managers(layer, lt, a),
        "repo": lambda: repo(layer, lt, a),
        "npm": lambda: npm(layer, lt, a),
        "skills": lambda: skills(layer, lt, a),
        "list": lambda: list_sect(layer, lt, a),
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


PUNCH_T = [T_KILLED, T_SA, T_SENIOR, T_COMMENT]          # one hero word per section
HIT_T = [T_HOOT + 0.28, T_SPROUT + 0.28, T_KILLED, T_SA, T_SENIOR, T_RID, T_COMMENT]
CUT_T = [s[1] for s in SECT[1:]]
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
