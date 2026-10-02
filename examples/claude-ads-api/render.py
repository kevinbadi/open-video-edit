#!/usr/bin/env python3
"""Split animated talking-head: Claude killed social ads managers (Social Agents + Creator OS Ads API).

1080x1920. Sequel to social-agents-animated: invader shoots Meta + Google Ads, the
social-agents terminal banner as the repo reveal, hub-and-spoke ads API, Meta/Google/TikTok
CEOs, codebase tree -> Meta Agent Pipeline checklist (steps from the real meta-campaign-builder
skill) with a per-step ad-builder panel, LAUNCH button + rocket, COMMENT "ADS".
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



from media_marks import figure_round, globe_card  # noqa: E402
from claude_marks import skill_chip  # noqa: E402

T_CLAUDE = trel("claude")
T_KILLED = trel("killed")
T_ADS1 = trel("ads")
T_MANAGERS = trel("managers")
T_BECAUSE = trel("because")
T_NEW = trel("new")
T_OPEN = trel("open")
T_REPO = trel("repo")
T_SA = trel("social", 4.5)
T_AND1 = trel("and", 6.0)
T_CONNECT = trel("connect")
T_EVERY = trel("every")
T_PLATFORM = trel("platform")
T_WORLD = trel("world")
T_META = trel("meta")
T_GOOGLE = trel("google")
T_TIKTOK = trel("tiktok")
T_LIST = trel("list")
T_AND2 = trel("and", 13.4)
T_CODE = trel("code")
T_SKILL = trel("skill")
T_META2 = trel("meta", 15.5)
T_PIPELINE = trel("pipeline")
T_CAN = trel("can", 17.4)
T_CREATE = trel("create")
T_CONSTRUCT = trel("construct")
T_THE3 = trel("the", 19.8)
T_ADVERT = trel("advertisement")
T_RUN = trel("run")
T_IT3 = trel("it", 23.3)
T_LAUNCH = trel("launch")
T_AUTO = trel("autonomously")
T_IF = trel("if", 25.0)
T_AI = trel("ai", 26.0)
T_MANAGER = trel("manager")
T_COMMENT = trel("comment")

SECT = [
    ("hook", 0.00, T_BECAUSE),
    ("repo", T_BECAUSE, T_AND1),
    ("connect", T_AND1, T_META - 0.12),
    ("platforms", T_META - 0.12, T_AND2),
    ("skill", T_AND2, T_CAN),
    ("build", T_CAN, T_IT3),
    ("launch", T_IT3, T_IF),
    ("cta", T_IF, DUR + 0.05),
]
KEYWORDS = {
    "claude", "killed", "social", "ads", "managers", "open", "source", "repo", "agents", "connect",
    "every", "platform", "world", "meta", "google", "tiktok", "list", "skill", "pipeline", "create",
    "construct", "entire", "advertisement", "run", "launch", "autonomously", "ai", "manager", "comment",
}
KEY_COL = {
    "claude": ORANGE, "killed": RED, "social": NEON, "ads": ORANGE, "managers": RED, "open": NEON,
    "source": NEON, "repo": NEON, "agents": ORANGE, "connect": CYAN, "every": ORANGE, "platform": CYAN,
    "world": CYAN, "meta": BLUE, "google": NEON, "tiktok": RED, "list": ORANGE, "skill": NEON,
    "pipeline": BLUE, "create": NEON, "construct": ORANGE, "entire": ORANGE, "advertisement": CYAN,
    "run": NEON, "launch": RED, "autonomously": NEON, "ai": ORANGE, "manager": ORANGE, "comment": NEON,
}
SECT_ACCENT = {
    "hook": ORANGE, "repo": NEON, "connect": CYAN, "platforms": BLUE,
    "skill": NEON, "build": ORANGE, "launch": RED, "cta": NEON,
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
BROLL_T0 = 0.0


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

def repo_card(p, w=520, h=300):
    k = int(p * 30)

    def build():
        card = shadow_card((w, h), 26, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        badge_at(card, "github", 60, pad + 24, pad + 22)
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
            place(layer, stamp("KILLED", RED, 48), authored[0], authored[1] + 16, lt, impact, dur=0.1,
                  frm="down", scale_pop=True, tilt=-8, idle=0, exit_at=impact + 0.62)
        light_hit(layer, cx, cy, lt, impact, accent)



BGS = {
    "hook": textured_bg((48, 36, 32), 7, ORANGE),
    "repo": textured_bg((36, 48, 42), 11, NEON),
    "connect": textured_bg((32, 44, 52), 13, CYAN),
    "platforms": textured_bg((32, 40, 52), 17, BLUE),
    "skill": textured_bg((34, 46, 44), 29, NEON),
    "build": textured_bg((48, 38, 32), 31, ORANGE),
    "launch": textured_bg((50, 32, 36), 23, RED),
    "cta": textured_bg((36, 48, 44), 19, NEON),
}


def badge_at(card, slug, size, x, y, fill=WHITE + (255,), punch=True):
    """logo_badge carries 32px of shadow padding; put the visible tile's top-left at (x, y)."""
    b = logo_badge(slug, size, fill=fill, punch=punch)
    if b is not None:
        card.alpha_composite(b, (x - 32, y - 32))


ADS_LANE = ["meta", "google-ads", "tiktok", "linkedin", "x", "openai", "instagram", "facebook", "creatoros"]


def ads_marks(size=120):
    return [m for m in (logo_badge(s_, size, fill=WHITE + (255,)) for s_ in ADS_LANE) if m is not None]


def hub_card(w=560, h=150):
    def build():
        card = shadow_card((w, h), 28, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rectangle([pad, pad + 20, pad + 10, pad + h - 20], fill=CYAN + (255,))
        badge_at(card, "creatoros", 96, pad + 30, pad + (h - 96) // 2, fill=INK + (255,), punch=False)
        d.text((pad + 150, pad + 48), "CREATOR OS", font=F(AR, 46), fill=WHITE + (255,), anchor="lm")
        d.text((pad + 150, pad + 102), "ADS API  ·  /v1/ads", font=F(ML, 24), fill=CYAN + (255,), anchor="lm")
        return card
    return cached(("hub", w, h), build)


SPOKES = [("meta", 150, 30), ("google-ads", 930, 30), ("tiktok", 110, 250),
          ("linkedin", 970, 250), ("x", 170, 470), ("openai", 910, 470)]
HUB = (540, 250)


def spokes(layer, lt, t0, stagger=0.12):
    """Hub-and-spoke: every ad network wires into the Creator OS API, packets running both ways."""
    d = ImageDraw.Draw(layer)
    hx, hy = HUB[0], HUB[1] + PACK_DY
    for i, (slug, x, y) in enumerate(SPOKES):
        ti = t0 + i * stagger
        if lt < ti:
            continue
        p = clamp01((lt - ti) / 0.28)
        px, py = x, y + PACK_DY
        ex, ey = hx + (px - hx) * p, hy + (py - hy) * p
        d.line([(hx, hy), (ex, ey)], fill=CYAN + (70,), width=14)
        d.line([(hx, hy), (ex, ey)], fill=(200, 245, 255, 230), width=4)
        if p >= 1:
            for k in range(2):
                q = ((lt - ti) * 0.9 + k * 0.5 + i * 0.13) % 1.0
                qx, qy = hx + (px - hx) * q, hy + (py - hy) * q
                d.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=NEON + (255,))
    for i, (slug, x, y) in enumerate(SPOKES):
        ti = t0 + i * stagger + 0.2
        place(layer, logo_badge(slug, 150, fill=WHITE + (255,)), x, y, lt, ti, dur=0.22, **entrance(i), idle=3)


TREE = [
    ("social-agents/", SILVER), ("├ skills/", SILVER), ("│ ├ meta-agent-pipeline/", NEON),
    ("│ │ └ SKILL.md", NEON), ("│ ├ google-ads/", STEEL), ("│ ├ tiktok-ads/", STEEL),
    ("│ └ linkedin-ads/", STEEL), ("└ README.md", STEEL),
]


def tree_card(p, hl, w=480, h=470):
    k = int(clamp01(p) * 40)

    def build():
        card = shadow_card((w, h), 26, TERM_BG + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        badge_at(card, "github", 48, pad + 20, pad + 16)
        d.text((pad + 82, pad + 40), "CODEBASE", font=F(AR, 30), fill=WHITE + (255,), anchor="lm")
        n = int(k / 40 * len(TREE) + 0.999)
        for i, (ln, col) in enumerate(TREE[:n]):
            y = pad + 92 + i * 44
            if hl and i in (2, 3):
                d.rounded_rectangle([pad + 12, y - 6, pad + w - 14, y + 36], 10, fill=(30, 70, 46, 255),
                                    outline=NEON + (220,), width=2)
            d.text((pad + 24, y), ln, font=F(ML, 24), fill=col + (255,))
        return card
    return cached(("tree", k, hl, w, h), build)


STEPS = ["OBJECTIVE", "BUDGET", "AUDIENCE", "CREATIVE", "DRY RUN", "LAUNCH"]


def pipeline_card(n_done, active, w=440):
    row_h = 70

    def build():
        h = 92 + row_h * len(STEPS) + 6
        card = shadow_card((w, h), 26, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rectangle([pad, pad + 20, pad + 8, pad + h - 20], fill=BLUE + (255,))
        badge_at(card, "meta", 52, pad + 26, pad + 16)
        d.text((pad + 92, pad + 42), "META AGENT PIPELINE", font=F(AR, 30), fill=WHITE + (255,), anchor="lm")
        for i, label in enumerate(STEPS):
            y = pad + 92 + i * row_h
            on = i < n_done
            col = RED if label == "LAUNCH" else NEON
            if i == active:
                d.rounded_rectangle([pad + 18, y - 4, pad + w - 18, y + row_h - 12], 14, fill=CHAR + (255,),
                                    outline=col + (200,), width=2)
            bx = pad + 34
            d.rounded_rectangle([bx, y + 10, bx + 34, y + 44], 8, outline=(col if on else STEEL) + (255,), width=3,
                                fill=(col + (255,)) if on else None)
            if on:
                d.line([(bx + 7, y + 27), (bx + 15, y + 36), (bx + 28, y + 17)], fill=INK + (255,), width=5)
            d.text((bx + 54, y + 27), label, font=F(AR, 32), fill=(WHITE if on else STEEL) + (255,), anchor="lm")
            d.text((pad + w - 34, y + 27), f"{i + 1:02d}", font=F(ML, 20), fill=STEEL + (255,), anchor="rm")
        return card
    return cached(("pipe", n_done, active, w), build)


def ui_card(title, accent, rows, w=500, h=None, foot=None):
    """Generic ad-builder panel: a header + label/value rows (+ optional footer)."""
    def build():
        hh = h or (110 + 78 * len(rows) + (70 if foot else 0))
        card = shadow_card((w, hh), 26, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rectangle([pad, pad + 20, pad + 8, pad + hh - 20], fill=accent + (255,))
        d.text((pad + 30, pad + 40), title, font=F(AR, 36), fill=WHITE + (255,), anchor="lm")
        for i, (lab, val, vcol) in enumerate(rows):
            y = pad + 96 + i * 78
            d.rounded_rectangle([pad + 26, y, pad + w - 24, y + 64], 14, fill=CHAR + (255,))
            d.text((pad + 46, y + 32), lab, font=F(AR, 22), fill=STEEL + (255,), anchor="lm")
            d.text((pad + w - 44, y + 32), val, font=F(AR, 30), fill=vcol + (255,), anchor="rm")
        if foot:
            d.text((pad + w / 2, pad + hh - 54), foot, font=F(AR, 28), fill=accent + (255,), anchor="mm")
        return card
    return cached(("ui", title, tuple(rows), w, h, foot), build)


def reach_card(p, w=500):
    k = int(clamp01(p) * 30)

    def build():
        card = ui_card("AUDIENCE", CYAN, [("WHERE", "Toronto +25 km", WHITE), ("AGE", "25 to 45", WHITE),
                                          ("INTEREST", "Social media marketing", WHITE)], w=w, h=470)
        card = card.copy()
        pad = 32
        d = ImageDraw.Draw(card)
        y = pad + 340
        d.text((pad + 30, y), "ESTIMATED REACH", font=F(AR, 22), fill=STEEL + (255,), anchor="lm")
        q = ease(k / 30)
        d.rounded_rectangle([pad + 26, y + 26, pad + w - 24, y + 50], 12, fill=CHAR + (255,))
        d.rounded_rectangle([pad + 26, y + 26, pad + 26 + int((w - 50) * 0.72 * q), y + 50], 12, fill=CYAN + (255,))
        if q > 0.6:
            d.text((pad + w - 24, y), "480K to 570K", font=F(AR, 26), fill=CYAN + (255,), anchor="rm")
        return card
    return cached(("reach", k, w), build)


def ad_mock(p, w=440):
    """Instagram feed ad the pipeline builds: page row, square creative, headline + Learn more."""
    k = int(clamp01(p) * 24)

    def build():
        img_w = w - 40
        src = Image.open("assets/covers/c1.png").convert("RGB")
        sq = src.crop((0, int(src.height * 0.06), src.width, int(src.height * 0.06) + src.width))
        sq = sq.resize((img_w, img_w), Image.LANCZOS)
        h = img_w + 230
        card = shadow_card((w, h), 26, WHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        badge_at(card, "creatoros", 54, pad + 20, pad + 16, fill=INK + (255,), punch=False)
        d.text((pad + 86, pad + 30), "creatoros", font=F(AR, 26), fill=INK + (255,), anchor="lm")
        d.text((pad + 86, pad + 56), "Sponsored", font=F(AR, 20), fill=STEEL + (255,), anchor="lm")
        q = k / 24
        reveal = int(img_w * ease(clamp01(q / 0.6)))
        if reveal > 0:
            card.paste(sq.crop((0, 0, img_w, reveal)), (pad + 20, pad + 84))
        y = pad + 84 + img_w + 18
        if q > 0.5:
            d.text((pad + 24, y), typewriter("The operating system for social media", (q - 0.5) / 0.35, cursor=False),
                   font=F(AR, 24), fill=INK + (255,))
        if q > 0.85:
            d.rounded_rectangle([pad + 20, y + 50, pad + w - 20, y + 104], 14, fill=BLUE + (255,))
            d.text((pad + w / 2, y + 77), "LEARN MORE", font=F(AR, 28), fill=WHITE + (255,), anchor="mm")
        return card
    return cached(("admock", k, w), build)


def launch_button(pressed, w=500, h=150):
    def build():
        img = Image.new("RGBA", (w, h + 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        dy = 10 if pressed else 0
        d.rounded_rectangle([0, 16, w - 1, h + 15], 40, fill=(120, 16, 26, 255))
        d.rounded_rectangle([0, dy, w - 1, h - 1 + dy], 40, fill=(RED if not pressed else NEON) + (255,))
        d.text((w / 2, h / 2 + dy), "LAUNCHED" if pressed else "LAUNCH AD", font=F(AR, 66),
               fill=(WHITE if not pressed else INK) + (255,), anchor="mm")
        return img
    return cached(("launchbtn", pressed, w, h), build)


def inbox_card(p, w=460, h=440):
    k = int(p * 24)

    def build():
        card = shadow_card((w, h), 26, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        badge_at(card, "instagram", 60, pad + 24, pad + 6, fill=CHAR + (255,))
        d.text((pad + 110, pad + 36), "INBOX  ·  AUTO", font=F(AR, 30), fill=WHITE + (255,), anchor="lm")
        d.ellipse([pad + w - 44, pad + 28, pad + w - 24, pad + 48], fill=NEON + (255,))
        fnt = F(AR, 28)
        y = pad + 110
        q = k / 24
        y = bubble(d, pad + 24, y, "@you: ADS", fnt, CHAR + (255,), SILVER + (255,))
        if q > 0.25:
            d.text((pad + w / 2, y + 6), "▼  keyword matched", font=MONO_S, fill=NEON + (255,), anchor="mt")
            y += 48
        if q > 0.45:
            y = bubble(d, pad + w - 24, y, typewriter("Here's your access!", (q - 0.45) / 0.35, cursor=False),
                       fnt, NEON + (255,), INK + (255,), right=True)
        if q > 0.85:
            bubble(d, pad + w - 24, y, "AI social ads manager", MONO_S, BLUE + (255,), INK + (255,), right=True)
        return card
    return cached(("inbox", k, w, h), build)


def bubble(d, x, y, txt, fnt, fill, fg, right=False, maxw=380):
    tw = d.textlength(txt, font=fnt)
    bw = min(maxw, tw + 40)
    x0 = x - bw if right else x
    d.rounded_rectangle([x0, y, x0 + bw, y + 58], 24, fill=fill)
    d.text((x0 + 20, y + 29), txt, font=fnt, fill=fg, anchor="lm")
    return y + 72


# ───────────────────────────── sections ─────────────────────────────

def hook(layer, lt):
    """Frame 0: giant invader locked on two ad managers. Shoots Meta on 'killed', Google Ads on 'ads'."""
    gw = ghost_word("ADS MANAGER", 80, 40)
    layer.alpha_composite(gw, (W - gw.width - 30, 6))
    looking = layer_pt(HOOT_C if lt < T_KILLED + 0.35 else SPR_C)
    aim = (INV_C[0] + 150, INV_C[1] + PACK_DY - 20)
    bloom_orb(layer, INV_C[0], INV_C[1] + PACK_DY, 230, ORANGE, a=70)
    place_claude_sphinx(layer, INV_C[0] - 150, INV_C[1] + PACK_DY - 200, lt, size=150)
    pose = place_claude_invader(layer, INV_C[0], INV_C[1] + PACK_DY, lt, size=460,
                                look_at=looking, grab="right", grab_at=aim, grab_t=0.85)
    muzzle = (int((INV_C[0] - pose.origin[0]) + pose.right_hand[0]),
              int((INV_C[1] + PACK_DY - pose.origin[1]) + pose.right_hand[1]))
    shoot_target(layer, "meta", HOOT_C, lt, T_KILLED, muzzle, RED)
    if lt >= T_KILLED + 0.45:
        shoot_target(layer, "google-ads", SPR_C, lt, T_ADS1, muzzle, NEON)
    else:
        place(layer, reticle(270, NEON, locked=False), SPR_C[0], SPR_C[1], lt, -0.4, dur=0.01, idle=0)
    place(layer, os_chip("CLAUDE", ORANGE, 30), INV_C[0], 430, lt, -0.4, dur=0.01, idle=0, exit_at=T_MANAGERS - 0.1)
    if lt >= T_MANAGERS:
        place(layer, title_card("SOCIAL ADS MANAGERS", RED, fsz=70, h=130), 540, 440, lt, T_MANAGERS, dur=0.16,
              frm="up", scale_pop=True, idle=0)
        place(layer, stamp("KILLED", RED, 70), 860, 330, lt, T_MANAGERS + 0.12, dur=0.12, frm="down",
              scale_pop=True, tilt=-8, idle=0)
        light_hit(layer, 540, 440 + PACK_DY, lt, T_MANAGERS, RED)


def repo(layer, lt, a):
    t_repo, t_new, t_sa = T_REPO - a, T_NEW - a, T_SA - a
    if lt < t_sa - 0.05:
        ex = t_sa - 0.26
        place(layer, title_card("OPEN SOURCE", NEON, fsz=84, h=140), 540, -140, lt, -0.4, dur=0.01, idle=0, exit_at=ex)
        place(layer, logo_badge("github", 300, fill=WHITE + (255,)), 210, 150, lt, -0.4, dur=0.01, idle=0, exit_at=ex)
        if lt >= t_new:
            place(layer, os_chip("BRAND NEW", ORANGE, 34), 210, 380, lt, t_new, dur=0.18, frm="up",
                  scale_pop=True, idle=0, exit_at=ex)
        if lt >= t_repo - 0.05:
            place(layer, repo_card(clamp01((lt - t_repo) / 1.0)), 710, 140, lt, t_repo - 0.05, frm="right",
                  idle=0, exit_at=ex)
        guarded_conveyor(layer, 490 + PACK_DY - 4, lt, ads_marks(120), conveyor_marks, name="ads-lane",
                         speed=180, gap=22)
        return
    place(layer, crop_img("banner", 980, glow=ORANGE), 540, 110, lt, t_sa, dur=0.2, scale_pop=True, idle=0)
    light_hit(layer, 540, 110 + PACK_DY, lt, t_sa, ORANGE)
    light_rays(layer, 540, 110 + PACK_DY, lt, ORANGE)
    if lt >= t_sa + 0.35:
        place(layer, crop_img("cmd", 820, glow=NEON), 540, 400, lt, t_sa + 0.35, frm="up", idle=0)


def connect(layer, lt, a):
    t_c, t_e, t_w = T_CONNECT - a, T_EVERY - a, T_WORLD - a
    ix, iy = HUB[0], HUB[1] + PACK_DY
    if lt < t_c:
        bloom_orb(layer, ix, iy, 200, ORANGE, a=70)
        place_claude_invader(layer, ix, iy - 20, lt + 3.0, size=340, look_at=(ix + 300, iy))
        gw = ghost_word("CONNECT", 150, 46)
        layer.alpha_composite(gw, ((W - gw.width) // 2, 10))
        place(layer, os_chip("YOUR AGENTS", ORANGE, 32), 540, 385, lt, -0.4, dur=0.01, idle=0, exit_at=t_c - 0.1)
        for i, (slug, x, y) in enumerate([("meta", 180, 60), ("google-ads", 900, 60)]):
            place(layer, reticle(220, CYAN, locked=lt > 0.6), x, y, lt, -0.4, dur=0.01, idle=0)
        guarded_conveyor(layer, 490 + PACK_DY - 4, lt + 2.0, ads_marks(120), conveyor_marks, name="ads-lane",
                         speed=180, gap=22)
        return
    spokes(layer, lt, t_e - 0.05)
    if lt >= t_w - 0.05:
        g = globe_card(lt, size=300)
        place(layer, g, 540, 40, lt, t_w - 0.05, dur=0.22, frm="down", scale_pop=True, idle=0)
        light_hit(layer, 540, 40 + PACK_DY, lt, t_w, CYAN)
    else:
        place_claude_invader(layer, 540, 40 + PACK_DY, lt + 3.0, size=220, look_at=(540, iy))
    bloom_orb(layer, ix, iy, 180, CYAN, a=60)
    place(layer, hub_card(), HUB[0], HUB[1], lt, t_c, dur=0.2, frm="up", scale_pop=True, idle=0)
    if lt >= T_PLATFORM - a:
        place(layer, os_chip("EVERY ADS PLATFORM", CYAN, 30), 540, 470, lt, T_PLATFORM - a, dur=0.2, frm="up", idle=0)


COLS = [("meta", "mark-zuckerberg", T_META, BLUE, 190), ("google-ads", "sundar-pichai", T_GOOGLE, NEON, 540),
        ("tiktok", "shou-zi-chew", T_TIKTOK, RED, 890)]


def platforms(layer, lt, a):
    t_list = T_LIST - a
    if lt < t_list - 0.05:
        ex = t_list - 0.25
        for i, (logo, fig, tw, col, x) in enumerate(COLS):
            t0 = tw - a
            if lt < t0 - 0.02:
                continue
            bloom_orb(layer, x, 10 + PACK_DY, 150, col, a=60)
            place(layer, logo_badge(logo, 220, fill=WHITE + (255,)), x, 10, lt, t0, dur=0.16, frm="down",
                  scale_pop=True, tilt=(-4, 3, -3)[i], idle=0, exit_at=ex)
            place(layer, figure_round(fig, 290, ring=col), x, 285, lt, t0 + 0.08, dur=0.22, frm="up",
                  tilt=(3, -3, 4)[i], idle=0, exit_at=ex)
            light_hit(layer, x, 10 + PACK_DY, lt, t0, col)
    else:
        front_gif(gif_card("list-on", max(0, lt - t_list), w=440, frame="round"), 270, 200, lt, t_list,
                  **entrance(2), idle=0)
        for i, slug in enumerate(["linkedin", "x", "openai", "instagram"]):
            place(layer, logo_badge(slug, 170, fill=WHITE + (255,)), 690 + (i % 2) * 210, 80 + (i // 2) * 230, lt,
                  t_list + 0.1 + i * 0.1, dur=0.2, **entrance(i + 3), idle=3)
    guarded_conveyor(layer, 490 + PACK_DY - 4, lt + 4.0, ads_marks(120), conveyor_marks, name="ads-lane",
                     speed=190, gap=22)


def skill(layer, lt, a):
    t_code, t_sk, t_m2, t_pl = T_CODE - a, T_SKILL - a, T_META2 - a, T_PIPELINE - a
    place(layer, tree_card(clamp01((lt - t_code + 0.2) / 0.9), lt >= t_sk), 290, 190, lt, -0.4, dur=0.01, idle=0)
    ix, iy = 790, 250 + PACK_DY
    grab_t = clamp01((lt - t_sk) / 0.4) * 0.85 if lt >= t_sk else 0.0
    bloom_orb(layer, ix, iy, 190, NEON, a=60)
    if lt < t_m2:
        place_claude_invader(layer, ix, iy, lt, size=320, look_at=(290, 190 + PACK_DY), grab="right",
                             grab_at=(ix + 170, iy - 150), grab_t=grab_t, hold=skill_chip("SKILL.md"))
        place(layer, os_chip("THIS SKILL", NEON, 30), 790, 470, lt, t_sk, dur=0.2, frm="up", idle=0)
    else:
        place(layer, title_card("META AGENT PIPELINE", BLUE, fsz=70, h=130), 540, -160, lt, t_m2, dur=0.18,
              frm="down", scale_pop=True, idle=0)
        light_hit(layer, 540, -160 + PACK_DY, lt, t_m2, BLUE)
        place(layer, logo_badge("meta", 280, fill=WHITE + (255,)), 790, 200, lt, t_m2 + 0.05, dur=0.2,
              frm="right", scale_pop=True, idle=0)
        if lt >= t_pl:
            place(layer, os_chip("AGENT PIPELINE", BLUE, 32), 790, 420, lt, t_pl, dur=0.18, frm="up",
                  scale_pop=True, idle=0)


STEP_T = [T_CREATE, T_CONSTRUCT, T_THE3, T_ADVERT, T_RUN, T_LAUNCH]


def build(layer, lt, a):
    t = a + lt
    n_done = sum(1 for ts in STEP_T if t >= ts)
    active = n_done - 1
    place(layer, pipeline_card(n_done, active), 255, 230, lt, -0.4, dur=0.01, idle=0)
    rx = 790
    if active < 0:
        place_claude_invader(layer, rx, 230 + PACK_DY, lt, size=300, look_at=(255, 230 + PACK_DY))
        return
    ts = STEP_T[active] - a
    nxt = (STEP_T[active + 1] - a) if active + 1 < len(STEP_T) else 99
    ex = nxt - 0.22
    if active == 0:
        place(layer, ui_card("OBJECTIVE", NEON, [("GOAL", "Website visits", WHITE), ("LINK", "creatoros.ca", CYAN),
                                                  ("BUTTON", "Learn more", WHITE)]), rx, 200, lt, ts, frm="right",
              tilt=2, idle=0, exit_at=ex)
        light_hit(layer, rx, 200 + PACK_DY, lt, ts, NEON)
    elif active == 1:
        place(layer, ui_card("BUDGET", ORANGE, [("DAILY", "CA$2 / day", ORANGE), ("BIDDING", "Highest volume", WHITE),
                                                 ("SCHEDULE", "Runs 24h+", WHITE)]), rx, 200, lt, ts, frm="down",
              idle=0, exit_at=ex)
    elif active == 2:
        place(layer, reach_card(clamp01((lt - ts) / 0.7)), rx, 230, lt, ts, frm="up", tilt=-2, idle=0, exit_at=ex)
    elif active == 3:
        place(layer, ad_mock(clamp01((lt - ts) / 1.3)), rx, 250, lt, ts, frm="right", idle=0, exit_at=ex)
    else:
        rows = [("FIELDS + GOAL", "passed", NEON), ("BUDGET + DATES", "passed", NEON),
                ("CREATIVE", "passed", NEON), ("META DRY RUN", "passed", NEON)]
        k = min(4, 1 + int(max(0, lt - ts) / 0.18))
        place(layer, ui_card("DRY RUN", NEON, rows[:k], h=110 + 78 * 4), rx, 220, lt, ts, frm="down", idle=0)


def launch(layer, lt, a):
    t_l, t_au = T_LAUNCH - a, T_AUTO - a
    t = a + lt
    n_done = sum(1 for ts in STEP_T if t >= ts)
    place(layer, pipeline_card(n_done, n_done - 1), 255, 230, lt, -0.4, dur=0.01, idle=0)
    if lt < t_l + 0.05:
        place(layer, launch_button(False), 790, 120, lt, -0.4, dur=0.01, idle=0)
        place_claude_invader(layer, 790, 390 + PACK_DY, lt, size=240, look_at=(790, 120 + PACK_DY),
                             grab="right", grab_at=(790, 190 + PACK_DY), grab_t=clamp01((lt + 0.4) / (t_l + 0.4)))
        return
    place(layer, launch_button(True), 790, -110, lt, t_l, dur=0.12, frm="down", idle=0)
    light_hit(layer, 790, -110 + PACK_DY, lt, t_l, RED)
    front_gif(gif_card("rocket", max(0, lt - t_l), w=400, frame="round"), 790, 200, lt, t_l + 0.05,
              **entrance(1), idle=0)
    if lt >= t_au:
        place(layer, stamp("AUTONOMOUS", NEON, 72), 640, 440, lt, t_au, dur=0.14, frm="down", scale_pop=True,
              tilt=-5, idle=0)
        light_rays(layer, 640, 440 + PACK_DY, lt, NEON)


def cta(layer, lt, a):
    t_ai, t_c = T_AI - a, T_COMMENT - a
    if lt < t_c - 0.05:
        ex = t_c - 0.24
        bloom_orb(layer, 540, 200 + PACK_DY, 220, ORANGE, a=70)
        place_claude_invader(layer, 540, 200 + PACK_DY, lt, size=380, look_at=(540, 470 + PACK_DY))
        for i, (slug, x, y) in enumerate([("meta", 190, 90), ("google-ads", 890, 90), ("tiktok", 190, 330),
                                          ("linkedin", 890, 330)]):
            place(layer, logo_badge(slug, 160, fill=WHITE + (255,)), x, y, lt, -0.4 + i * 0.08, dur=0.2,
                  **entrance(i), idle=3, exit_at=ex)
        if lt >= t_ai:
            place(layer, title_card("AI SOCIAL ADS MANAGER", ORANGE, fsz=68, h=130), 540, 450, lt, t_ai, dur=0.18,
                  frm="up", scale_pop=True, idle=0, exit_at=ex)
        return
    place(layer, title_card("COMMENT  \"ADS\"", NEON, fsz=80, h=140), 540, -150, lt, t_c, dur=0.18,
          scale_pop=True, idle=0)
    light_hit(layer, 540, -150 + PACK_DY, lt, t_c, NEON)
    light_rays(layer, 540, -150 + PACK_DY, lt, NEON)
    front_gif(gif_card("comment", max(0, lt - t_c), w=420, frame="round"), 270, 220, lt, t_c + 0.06,
              **entrance(2), idle=0)
    place(layer, inbox_card(clamp01((lt - t_c - 0.1) / 0.8)), 790, 220, lt, t_c + 0.1, frm="right", idle=0)


def scene(layer, name, lt, a):
    {
        "hook": lambda: hook(layer, lt),
        "repo": lambda: repo(layer, lt, a),
        "connect": lambda: connect(layer, lt, a),
        "platforms": lambda: platforms(layer, lt, a),
        "skill": lambda: skill(layer, lt, a),
        "build": lambda: build(layer, lt, a),
        "launch": lambda: launch(layer, lt, a),
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



PUNCH_T = [T_KILLED, T_META, T_LAUNCH]                    # one hero word per section, >=8s apart
HIT_T = [T_KILLED + 0.28, T_ADS1 + 0.28, T_MANAGERS, T_SA, T_PIPELINE - 0.7, T_LAUNCH, T_AUTO, T_COMMENT]
CUT_T = [T_BECAUSE, T_AND1, T_META - 0.12, T_AND2, T_CAN, T_IF]   # build -> launch is one continuous card
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