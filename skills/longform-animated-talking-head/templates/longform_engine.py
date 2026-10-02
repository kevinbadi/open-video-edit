#!/usr/bin/env python3
"""Long-form LANDSCAPE hyper-edit engine (1920x1080) for Kevin's YouTube talking heads.

Built reverse-first on the JEV AI x HyperEdit intro (2026-09-21, Kevin: "really good, solid
long form skill start"). Per video you write a small render.py (sections + scene()) and call
run(); this module owns everything else: palette, the three layouts, place(), cards, phrase
captions on the accent line, the head reader, hyper-edit timing and the frame loop.

Layouts (switch per section so a long-form head never sits still):
  FULL  head full-bleed 1920x1080 + a transparent overlay layer (billboard / stamps / GIF on the sides)
  SPLIT animation slot 1140x950 at (40,46) LEFT, head card 680x950 at x=1200 RIGHT (1:1 crop from meta)
  HERO  animation slot 1840x950 full width, head PIP 520x292 bottom-right (behind nothing, over lanes)

Locked (Kevin 2026-09-21):
  - NO mystery cold open for long-form: frame 0 is a bright billboard on the actual topic.
  - NO bottom strip (progress bar / label / timecode). Accent line at y=1038, captions rest on it.
  - Head is never zoomed or shaken; punch_zoom + shake go on the slot layer only.
  - View changes (SPLIT/FULL/HERO) zoom-dissolve; cuts never shake (Kevin 09-30).
  - Captions = Luckiest Guy phrase groups (<=4 words), active word in KEY_COL, unspoken words dim.
"""
import json, math, os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fonts import AR, CAP, ML, F  # noqa: E402
from hyper_edits import (  # noqa: E402
    clamp01, ease_out_cubic, ease_in_out_quad, ease_back_out, punch_beats, word_onset, punch_scale, punch_zoom,
    shake_offset, hyperframe, whip_wipe, whip_dir, typewriter, caption_impact, entrance, lanes,
    guarded_conveyor, zoom_blur, slam_in,
)
from media_marks import gif_card, logo_mark, logo_badge, topic_marks  # noqa: E402
from light_fx import (  # noqa: E402
    scanlines, hud_scan, neon_grid, slot_vignette, bloom_orb, light_hit, light_rays, speed_streaks,
    caption_bloom,
)
from claude_marks import place_claude_invader, ensure_claude_marks  # noqa: E402

ensure_claude_marks("assets/logos")


W, H, FPS = 1920, 1080, 30
# ───────────── palette lock (consistent across the whole series) ─────────────
INK = (10, 11, 14)
SILVER = (198, 204, 214)
STEEL = (92, 98, 108)
GRAPHITE = (36, 38, 46)
CHAR = (48, 50, 58)
PINK = (236, 72, 153)      # Jev
VIOLET = (139, 92, 246)    # HyperEdit
CYAN = (56, 200, 248)
NEON = (57, 255, 132)
RED = (255, 48, 64)
ORANGE = (255, 122, 24)
WHITE = (255, 252, 248)
MONO = F(ML, 24)
MONO_S = F(ML, 19)

meta = json.load(open("source/meta.json")) if os.path.isfile("source/meta.json") else {}
_words_raw = json.load(open("audio/words.json"))
words = [[w.strip(), float(a), float(b)] for w, a, b in _words_raw]
DUR = float(meta.get("DUR") or max(b for _w, _a, b in words))
N = int(DUR * FPS)

# ───────────── layouts ─────────────
LINE_Y = 1038                # accent line the captions rest on (no bottom strip, Kevin 09-21)
SLOT_Y = 46
SLOT_H = 950
SPLIT_SLOT = (40, SLOT_Y, 1140, SLOT_H)      # x, y, w, h
HERO_SLOT = (40, SLOT_Y, 1840, SLOT_H)
HEAD_CARD = (1200, SLOT_Y, 680, SLOT_H)      # split: head card on the right
HEAD_CROP = tuple(meta.get("HEAD_CROP") or (510, 130, 1190, 1080))   # source px, 680x950 1:1 around the face (prep writes it)
PIP = (1330, 690, 520, 292)                  # hero: head PIP bottom-right of the slot
CAP_BASE = LINE_Y - 8 - 7 - 3                # stroke bottom rests on the line top


def tabs(word, after):
    """Absolute onset of the first `word` at/after `after` (falls back to `after`)."""
    o = word_onset(words, word, after=after)
    return o if o is not None else after

def tabs_any(cands, after):
    """First onset among several spellings ("workflows.", "workflows")."""
    for c in cands:
        o = word_onset(words, c, after=after)
        if o is not None:
            return o
    return after

# ───────────── caches / primitives ─────────────
CACHE = {}
def cached(key, fn):
    if key not in CACHE:
        CACHE[key] = fn()
    return CACHE[key]

ease = lambda p: 1 - (1 - max(0.0, min(1.0, p))) ** 3  # noqa: E731
def outp(p):
    p = max(0.0, min(1.0, p))
    return 1.15 - 0.15 * ease(p) if p < 1 else 1.0

def shadow_card(size, radius, fill, blur=16, alpha=90):
    w, h = size
    pad = blur * 2
    card = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 12, pad + w, pad + h + 12], radius, fill=(0, 0, 0, alpha))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(blur // 2)))
    ImageDraw.Draw(card).rounded_rectangle([pad, pad, pad + w, pad + h], radius, fill=fill)
    return card

def textured_bg(base, seed, glow, size=(W + 160, H + 160)):
    ww, hh = size
    rng = np.random.default_rng(seed)
    arr = np.tile(np.array(base, np.float32), (hh, ww, 1))
    arr += rng.normal(0, 2.4, (hh, ww, 1))
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    sh = Image.new("L", (ww, hh), 0)
    d = ImageDraw.Draw(sh)
    for cx, cy, rx, ry in [(300, 260, 520, 320), (1500, 900, 520, 340), (1000, 120, 420, 220)]:
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=48)
    sh = sh.filter(ImageFilter.GaussianBlur(110))
    lift = Image.new("RGB", (ww, hh), tuple(min(255, c + 18) for c in base))
    base_img = Image.composite(lift, img, sh)
    gl = Image.new("L", (ww, hh), 0)
    ImageDraw.Draw(gl).ellipse([200, -100, 1400, 700], fill=64)
    gl = gl.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB", (ww, hh), glow), base_img, gl)

BGS = {}
ACCENT = {}
def bg_for(name):
    if name not in BGS:
        acc = ACCENT[name]
        base = tuple(int(CHAR[i] * 0.86 + acc[i] * 0.08) for i in range(3))
        BGS[name] = textured_bg(base, 7 + len(name) * 3, acc)
    return BGS[name]

# ───────────── place() for any layer size ─────────────
def place(layer, img, cx, cy, lt, t0, dur=0.3, frm="up", tilt=0.0, idle=5, scale_pop=False, exit_at=None):
    if img is None:
        return
    p = ease((lt - t0) / dur)
    if p <= 0:
        return
    alpha = p
    p2 = 0
    if exit_at is not None:
        q = (lt - exit_at) / 0.22
        if q >= 1:
            return
        if q > 0:
            alpha = min(alpha, 1 - q)
            p2 = ease(q)
    off = 90 * (1 - p)
    dx, dy = {"up": (0, off), "down": (0, -off), "left": (off, 0), "right": (-off, 0)}.get(frm, (0, off))
    if idle and img.width < 400 and img.height < 400:
        seed = (int(cx) * 73 + int(cy) * 151) % 1000 / 1000.0
        period = 3.2 + 2.4 * seed
        amp = min(idle, 3)
        dx += amp * 0.6 * math.sin((lt * 2 * math.pi) / (period * 1.37) + seed * 6.28)
        dy += amp * math.sin((lt * 2 * math.pi) / period + seed * 6.28)
    dy -= 120 * p2
    im = img
    if scale_pop:
        s = outp((lt - t0) / dur)
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    if tilt:
        im = im.rotate(tilt, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    lw, lh = layer.size
    x = int(cx - im.width / 2 + dx)
    y = int(cy - im.height / 2 + dy)
    x = max(0, min(lw - im.width, x)) if im.width <= lw else x
    y = max(0, min(lh - im.height, y)) if im.height <= lh else y
    layer.alpha_composite(im, (x, y))

GIF_Q = []
def front_gif(*a, **k):
    GIF_Q.append((a, k))
def flush_gifs(layer):
    while GIF_Q:
        a, k = GIF_Q.pop(0)
        place(layer, *a, **k)

def conveyor_marks(layer, y, lt, imgs, speed=160, gap=22):
    if not imgs:
        return
    total = sum(im.width + gap for im in imgs)
    off = int((lt * speed) % total)
    x0 = 24 - off
    lw = layer.size[0]
    for cycle in range(6):
        xx = x0 + cycle * total
        for im in imgs:
            if -im.width < xx < lw:
                layer.alpha_composite(im, (int(xx), int(y - im.height / 2)))
            xx += im.width + gap

# ───────────── cards ─────────────
def chip(txt, accent=None, fsz=26):
    accent = accent or PINK
    def build():
        f2 = F(AR, fsz)
        tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(txt, font=f2))
        h = fsz + 34
        img = Image.new("RGBA", (tw + 52, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, tw + 51, h - 1], 16, fill=GRAPHITE + (255,))
        d.rectangle([0, 0, 8, h - 1], fill=accent + (255,))
        d.text((26, 15), txt, font=f2, fill=SILVER + (255,))
        return img
    return cached(("chip", txt, accent, fsz), build)

def strike_chip(txt, accent=RED):
    def build():
        base = chip(txt, accent)
        img = base.copy()
        d = ImageDraw.Draw(img)
        d.line([(18, img.height // 2 + 5), (img.width - 12, img.height // 2 - 7)], fill=accent + (255,), width=7)
        return img
    return cached(("strike", txt, accent), build)

def big_text_card(txt, fill=PINK, fg=None, fsz=56, w=1000, h=136):
    if fg is None:
        fg = INK + (255,) if fill in (NEON, ORANGE, CYAN) else WHITE + (255,)
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w, h], 26, fill=fill + (255,), outline=SILVER + (70,), width=2)
        f2 = F(AR, fsz)
        d.text((w / 2, h / 2 - 2), txt, font=f2, fill=fg, anchor="mm")
        return img
    return cached(("btc", txt, fill, fsz, w, h), build)

def stamp_card(txt, col=RED, fsz=78, w=640, h=160):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([6, 6, w - 6, h - 6], 22, outline=col + (255,), width=12)
        d.rounded_rectangle([22, 22, w - 22, h - 22], 14, outline=col + (150,), width=3)
        d.text((w / 2, h / 2 - 4), txt, font=F(AR, fsz), fill=col + (255,), anchor="mm")
        return img
    return cached(("stamp", txt, col, fsz, w, h), build)

def ghost_img(text, size, lw):
    def build():
        img = Image.new("RGBA", (lw + 400, size + 60), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((200, 10), text, font=F(AR, size), fill=SILVER + (40,))
        return img
    return cached(("ghost", text, size, lw), build)

def ticker(layer, text, y, lt, speed=150, fill=SILVER + (80,)):
    d = ImageDraw.Draw(layer)
    tw = int(d.textlength(text, font=MONO))
    span = tw + 90
    x = layer.size[0] - int((lt * speed) % (span + layer.size[0]))
    d.text((x, y), text, font=MONO, fill=fill)

GLYPHS = ["jev", "hyperedit", "cut 00:12", "b-roll", "captions", "p=0.97", "choice", "score", "noul",
          "timeline", "render", "agent", "198ms", "typed"]
def draw_code_rain(layer, lt, n=18, col=CYAN):
    d = ImageDraw.Draw(layer)
    lw, lh = layer.size
    for i in range(n):
        x = 16 + (i * 97) % (lw - 80)
        y = int((lt * 120 + i * 53) % (lh - 60)) - 40
        d.text((x, y), GLYPHS[i % len(GLYPHS)], font=MONO_S, fill=col + (70,))

def sparkle(size, col=WHITE):
    def build():
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        c = size / 2
        pts = []
        for i in range(8):
            ang = math.radians(i * 45 - 90)
            r = c * (0.98 if i % 2 == 0 else 0.26)
            pts.append((c + r * math.cos(ang), c + r * math.sin(ang)))
        d.polygon(pts, fill=col + (255,))
        # small satellite sparkle
        s2 = size * 0.22
        pts2 = []
        for i in range(8):
            ang = math.radians(i * 45 - 90)
            r = s2 / 2 * (1 if i % 2 == 0 else 0.28)
            pts2.append((size * 0.83 + r * math.cos(ang), size * 0.2 + r * math.sin(ang)))
        d.polygon(pts2, fill=col + (255,))
        return img
    return cached(("sparkle", size, col), build)

def sparkle_badge(size=260, col=VIOLET):
    """Rounded square badge with a vector sparkle (the HyperEdit mark)."""
    def build():
        card = shadow_card((size, size), int(size * 0.2), col + (255,))
        sp = sparkle(int(size * 0.62))
        card.alpha_composite(sp, ((card.width - sp.width) // 2, (card.height - sp.height) // 2))
        return card
    return cached(("sparklebadge", size, col), build)

def round_logo(slug, size=260, punch=False):
    """A logo that is already a filled round/square mark (jev.png), with a soft drop shadow."""
    def build():
        m = logo_mark(slug, size, punch=punch)
        if m is None:
            return None
        card = Image.new("RGBA", (size + 60, size + 60), (0, 0, 0, 0))
        sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([30, 42, 30 + size, 42 + size], fill=(0, 0, 0, 110))
        card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(10)))
        card.alpha_composite(m, (30, 30))
        return card
    return cached(("roundlogo", slug, size, punch), build)

def wordmark(txt, col, fsz=96, sub=None):
    def build():
        f1 = F(AR, fsz)
        d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        tw = int(d0.textlength(txt, font=f1))
        h = fsz + 30 + (40 if sub else 0)
        img = Image.new("RGBA", (tw + 40, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((20 + 4, 4 + 4), txt, font=f1, fill=(0, 0, 0, 160))
        d.text((20, 4), txt, font=f1, fill=col + (255,))
        if sub:
            d.text((22, fsz + 14), sub, font=F(AR, 30), fill=SILVER + (230,))
        return img
    return cached(("wm", txt, col, fsz, sub), build)

def thumb_card(i, w=560, tilt_label=None):
    def build():
        im = Image.open(f"assets/thumbs/thumb_{i}.png").convert("RGBA")
        # crop the YouTube card to the thumbnail image only (top ~ 16:9 region)
        th = int(im.width * 9 / 16)
        im = im.crop((0, 0, im.width, min(th, im.height)))
        im = im.resize((w, int(w * 9 / 16)), Image.LANCZOS)
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], 22, fill=255)
        im.putalpha(mask)
        card = shadow_card((im.width + 16, im.height + 16), 28, GRAPHITE + (255,))
        card.alpha_composite(im, (32 + 8, 32 + 8))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([32 + 8, 32 + 8, 32 + 8 + 74, 32 + 8 + 46], 12, fill=RED + (240,))
        d.polygon([(32 + 8 + 28, 32 + 8 + 12), (32 + 8 + 28, 32 + 8 + 34), (32 + 8 + 50, 32 + 8 + 23)], fill=WHITE + (255,))
        return card
    return cached(("thumb", i, w), build)

def terminal_card(lt, lines, title="AGENT", w=700, h=360, accent=CYAN, prompt=True):
    shown = []
    for t0, txt, col in lines:
        if lt >= t0:
            shown.append((typewriter(txt, clamp01((lt - t0) / 0.4), cursor=False), col))
    key = tuple(shown)
    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad, pad, pad + w, pad + 52], 22, fill=INK + (255,))
        d.rectangle([pad, pad + 30, pad + w, pad + 52], fill=INK + (255,))
        for i, col in enumerate([RED, ORANGE, NEON]):
            d.ellipse([pad + 22 + i * 30, pad + 16, pad + 40 + i * 30, pad + 34], fill=col + (255,))
        d.text((pad + 124, pad + 13), title, font=F(AR, 24), fill=accent + (255,))
        y = pad + 74
        for txt, col in shown:
            d.text((pad + 24, y), txt, font=MONO, fill=col + (255,))
            y += 40
        if not shown and prompt:
            d.text((pad + 24, y), "> _", font=MONO, fill=STEEL + (255,))
        return card
    return cached(("term", key, title, w, h, accent), build)

def timeline_card(lt, w=1000, h=330, accent=CYAN, playhead=True):
    """Fake NLE timeline: 3 tracks, clips, playhead sweeping, agent cursor."""
    k = int(lt * 30)
    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad, pad, pad + w, pad + 46], 22, fill=INK + (255,))
        d.rectangle([pad, pad + 28, pad + w, pad + 46], fill=INK + (255,))
        d.text((pad + 24, pad + 10), "TIMELINE  ·  hyperedit.timeline", font=F(AR, 22), fill=SILVER + (255,))
        tc = f"00:00:{int(lt * 4) % 60:02d}:{(k * 3) % 30:02d}"
        d.text((pad + w - 190, pad + 12), tc, font=MONO_S, fill=accent + (255,))
        tracks = [("V2  b-roll", VIOLET, [(0.05, 0.22), (0.30, 0.42), (0.55, 0.68), (0.80, 0.95)]),
                  ("V1  talking head", CYAN, [(0.02, 0.98)]),
                  ("A1  narration", NEON, [(0.02, 0.98)]),
                  ("FX  hyper-edit", PINK, [(0.08, 0.10), (0.21, 0.23), (0.41, 0.43), (0.66, 0.68), (0.88, 0.90)])]
        y = pad + 66
        x0 = pad + 190
        tw = w - 210
        th = 48
        for name, col, clips in tracks:
            d.text((pad + 20, y + 12), name, font=MONO_S, fill=STEEL + (255,))
            d.rounded_rectangle([x0, y, x0 + tw, y + th], 8, fill=INK + (255,))
            for a, b in clips:
                d.rounded_rectangle([x0 + tw * a, y + 4, x0 + tw * b, y + th - 4], 8, fill=col + (200,))
                d.rectangle([x0 + tw * a, y + 4, x0 + tw * a + 5, y + th - 4], fill=WHITE + (200,))
            if name.startswith("A1"):
                rng = np.random.default_rng(3)
                for i in range(0, int(tw * 0.96), 6):
                    hh = int(rng.uniform(4, th - 12))
                    d.line([x0 + tw * 0.02 + i, y + th / 2 - hh / 2, x0 + tw * 0.02 + i, y + th / 2 + hh / 2],
                           fill=INK + (200,), width=2)
            y += th + 14
        if playhead:
            px = x0 + int(tw * ((lt * 0.12) % 1.0))
            d.rectangle([px - 2, pad + 56, px + 2, y - 6], fill=RED + (255,))
            d.polygon([(px - 12, pad + 50), (px + 12, pad + 50), (px, pad + 66)], fill=RED + (255,))
        # agent cursor
        cxp = x0 + int(tw * (0.5 + 0.42 * math.sin(lt * 1.3)))
        cyp = pad + 90 + int(60 * (1 + math.sin(lt * 2.1)))
        d.polygon([(cxp, cyp), (cxp + 18, cyp + 14), (cxp + 7, cyp + 15), (cxp + 2, cyp + 26)], fill=WHITE + (255,))
        d.text((cxp + 22, cyp + 8), "agent", font=MONO_S, fill=accent + (255,))
        return card
    return cached(("timeline", k, w, h, accent), build)

def x_mark(size=120, col=RED):
    def build():
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        m = int(size * 0.14)
        d.line([m, m, size - m, size - m], fill=col + (255,), width=int(size * 0.14))
        d.line([size - m, m, m, size - m], fill=col + (255,), width=int(size * 0.14))
        return img
    return cached(("xmark", size, col), build)

def tool_badge(slug, size=300, fill=None):
    return logo_badge(slug, size, punch=(slug != "capcut"), fill=fill or (GRAPHITE + (255,)))

def whisper_line(text, p, w=900, h=64, col=STEEL):
    shown = typewriter(text, p, cursor=False)
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((w / 2, h / 2), shown, font=F(AR, 34), fill=col + (255,), anchor="mm")
        return img
    return cached(("whisper", shown, w, h, col), build)

def workflow_card(p, w=1000, h=300, title="VIDEO EDITING WORKFLOW", nodes=None, foot="", accent=PINK):
    """Pipeline of nodes lighting up with p (clip -> JEV -> cuts -> b-roll -> render)."""
    nodes = nodes or [("CLIP", CYAN), ("JEV", PINK), ("CUTS", VIOLET), ("B-ROLL", VIOLET), ("RENDER", NEON)]
    n_on = int(clamp01(p) * len(nodes) + 0.001)
    key = (n_on, w, h, title, tuple(nodes), foot, accent)
    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + 24, pad + 16), title, font=F(AR, 24), fill=accent + (255,))
        bw = 160
        gap = (w - 48 - bw * len(nodes)) / max(1, len(nodes) - 1)
        y = pad + 90
        for i, (name, col) in enumerate(nodes):
            x = pad + 24 + i * (bw + gap)
            on = i < n_on
            d.rounded_rectangle([x, y, x + bw, y + 120], 20, fill=(col + (255,)) if on else (INK + (255,)),
                                outline=col + (255,), width=3)
            d.text((x + bw / 2, y + 60), name, font=F(AR, 34), fill=(INK + (255,)) if on else (STEEL + (255,)), anchor="mm")
            if i < len(nodes) - 1:
                ax = x + bw + 8
                d.line([ax, y + 60, ax + gap - 16, y + 60], fill=(SILVER + (255,)) if i < n_on - 1 else (STEEL + (120,)), width=5)
                d.polygon([(ax + gap - 16, y + 48), (ax + gap - 16, y + 72), (ax + gap - 2, y + 60)],
                          fill=(SILVER + (255,)) if i < n_on - 1 else (STEEL + (120,)))
        if foot:
            d.text((pad + 24, pad + 236), foot, font=MONO_S, fill=STEEL + (255,))
        return card
    return cached(("workflow",) + key, build)

def demo_card(lt, w=760, h=420):
    k = int(lt * 30)
    def build():
        card = shadow_card((w, h), 24, INK + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        # scan-line screen
        for y in range(pad + 10, pad + h - 10, 5):
            d.line([pad + 10, y, pad + w - 10, y], fill=(20, 22, 30, 255))
        cx, cy = pad + w / 2, pad + h / 2 - 10
        r = 90 + 4 * math.sin(lt * 5)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED + (255,))
        d.polygon([(cx - 30, cy - 46), (cx - 30, cy + 46), (cx + 48, cy)], fill=WHITE + (255,))
        d.text((cx, pad + h - 60), "DEMO", font=F(AR, 54), fill=WHITE + (255,), anchor="mm")
        d.rounded_rectangle([pad + w - 130, pad + 22, pad + w - 24, pad + 62], 12, fill=GRAPHITE + (255,))
        d.ellipse([pad + w - 118, pad + 32, pad + w - 98, pad + 52], fill=RED + (255,))
        d.text((pad + w - 88, pad + 30), "REC", font=F(AR, 22), fill=SILVER + (255,))
        d.rectangle([pad, pad + 8, pad + 8, pad + h - 8], fill=RED + (255,))
        return card
    return cached(("demo", k % 19, w, h), build)

# ───────────── captions (phrase groups) ─────────────
def caption_groups(ws, max_words=4, max_gap=0.35, max_dur=1.8):
    groups, cur = [], []
    for w, a, b in ws:
        if cur and (len(cur) >= max_words or a - cur[-1][2] > max_gap or a - cur[0][1] > max_dur
                    or cur[-1][0].endswith((".", ",", "!", "?"))):
            groups.append(cur)
            cur = []
        cur.append((w, a, b))
    if cur:
        groups.append(cur)
    return groups

GROUPS = caption_groups(words)
def group_at(t):
    for g in GROUPS:
        if g[0][1] - 0.05 <= t <= g[-1][2] + 0.12:
            return g
    return None

KEYWORDS = set()
KEY_COL = {}

def draw_captions(frame, t, acc):
    g = group_at(t)
    if not g:
        return
    d = ImageDraw.Draw(frame)
    fs = 60
    cf = F(CAP, fs)
    gap = 22
    pieces = []
    for w, a, b in g:
        k = w.rstrip(".,!?").lower()
        key = k in KEYWORDS or w.lower() in KEYWORDS
        active = a <= t <= b + 0.1
        txt = w.upper()
        pieces.append((txt, key, active, a, w.lower()))
    widths = [d.textlength(p[0], font=cf) for p in pieces]
    total = sum(widths) + gap * (len(pieces) - 1)
    x = (W - total) / 2
    for (txt, key, active, a, raw), tw in zip(pieces, widths):
        col = KEY_COL.get(raw, KEY_COL.get(raw.rstrip(".,!?"), acc)) if key else WHITE
        if not active and t < a:
            col = STEEL  # not yet spoken: dim
        elif not active:
            col = col if key else SILVER
        sc = caption_impact(t, a, key) if active else 1.0
        f2 = cf if sc == 1.0 else F(CAP, int(fs * sc))
        tw2 = d.textlength(txt, font=f2)
        xx = x + (tw - tw2) / 2
        if active and key:
            caption_bloom(frame, xx, CAP_BASE - fs, tw2, fs, col)
        d.text((xx, CAP_BASE), txt, font=f2, fill=col + (255,), anchor="ls", stroke_width=7, stroke_fill=(0, 0, 0, 255))
        x += tw + gap

# ───────────── head reader ─────────────
head_cap = cv2.VideoCapture("source/talking_head.mp4")
HEAD_N = int(head_cap.get(cv2.CAP_PROP_FRAME_COUNT))
_head_idx = -10
_head_last = None
def head_frame(n):
    global _head_idx, _head_last
    n = min(n, HEAD_N - 1)
    if n == _head_idx:
        return _head_last
    if n != _head_idx + 1:
        head_cap.set(cv2.CAP_PROP_POS_FRAMES, n)
    ok, fr = head_cap.read()
    if ok:
        _head_last = fr
    _head_idx = n
    return _head_last

CARD_MASK = Image.new("L", (HEAD_CARD[2], HEAD_CARD[3]), 0)
ImageDraw.Draw(CARD_MASK).rounded_rectangle([0, 0, HEAD_CARD[2] - 1, HEAD_CARD[3] - 1], 44, fill=255)
PIP_MASK = Image.new("L", (PIP[2], PIP[3]), 0)
ImageDraw.Draw(PIP_MASK).rounded_rectangle([0, 0, PIP[2] - 1, PIP[3] - 1], 26, fill=255)

def head_full(fr):
    return Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))

def head_card(fr, acc):
    x0, y0, x1, y1 = HEAD_CROP
    crop = fr[y0:y1, x0:x1]
    im = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)).convert("RGBA")
    im.putalpha(CARD_MASK)
    return im

def head_pip(fr):
    small = cv2.resize(fr, (PIP[2], PIP[3]), interpolation=cv2.INTER_AREA)
    im = Image.fromarray(cv2.cvtColor(small, cv2.COLOR_BGR2RGB)).convert("RGBA")
    im.putalpha(PIP_MASK)
    return im

def ring(frame, box, col, r, w=6):
    x, y, ww, hh = box
    ImageDraw.Draw(frame).rounded_rectangle([x - w, y - w, x + ww + w, y + hh + w], r + w, outline=col + (255,), width=w)

def bottom_grad():
    def build():
        g = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
        d = ImageDraw.Draw(g)
        for i in range(200):
            d.line([0, i, W, i], fill=(0, 0, 0, int(200 * (i / 200) ** 1.4)))
        return g
    return cached(("bgrad",), build)


def run(SECT, scene, punch_words=(), extra_hits=(), keywords=None, key_col=None, out="frames/out"):
    """Render loop. SECT = [(name, start, end, "FULL"|"SPLIT"|"HERO", accent_rgb), ...].
    scene(layer, name, lt, t, a, acc) draws the section into the slot layer (slot-local px).
    punch_words: ONE hero word per section (rare punches). extra_hits: abs times that shake.
    Env: PREVIEW="0.0,2.2,..." renders those seconds only; RANGE="a:b" renders frame range."""
    global KEYWORDS, KEY_COL
    if keywords is not None:
        KEYWORDS = set(keywords)
    if key_col is not None:
        KEY_COL = dict(key_col)
    ACCENT.clear()
    ACCENT.update({s[0]: s[4] for s in SECT})
    PUNCH_T = punch_beats(words, list(punch_words))
    CUT_T = [s[1] for s in SECT[1:]]
    # Kevin 2026-09-30: no shake on view changes. Cuts never shake; only extra_hits (impact beats) do.
    HIT_T = list(extra_hits)
    LAYOUT_CHANGES = [s[1] for i, s in enumerate(SECT) if i > 0 and s[3] != SECT[i - 1][3]]
    WHIP_T = [c for c in CUT_T if c not in LAYOUT_CHANGES]
    print("punches", [round(p, 2) for p in PUNCH_T])
    print("layout changes", [round(p, 2) for p in LAYOUT_CHANGES])

    os.makedirs(out, exist_ok=True)
    PREVIEW = os.environ.get("PREVIEW")
    if PREVIEW:
        times = [float(x) for x in PREVIEW.split(",")]
        todo = [int(round(tt * FPS)) for tt in times]
    else:
        todo = list(range(N))
        if os.environ.get("RANGE"):
            _a, _b = os.environ["RANGE"].split(":")
            todo = list(range(int(_a), min(N, int(_b))))

    def compose(n, t, sec, whip_from=None):
        """Full frame for section `sec` at time t (no accent line / captions).
        Returns (frame, raw slot layer before punch/shake) so whips can reuse the layer."""
        name, a, b, layout, acc = sec
        lt, sd = t - a, max(0.01, b - a)
        fr = head_frame(n)

        if layout == "FULL":
            frame = head_full(fr).convert("RGBA")
            frame.alpha_composite(bottom_grad(), (0, H - 200))
            slot = (0, 0, W, H)
        else:
            z = 1.0 + 0.05 * min(1.0, lt / sd)
            bg = bg_for(name)
            bw, bh = int((W + 160) / z), int((H + 160) / z)
            ox, oy = (bg.width - bw) // 2, (bg.height - bh) // 2
            frame = bg.crop((ox, oy, ox + bw, oy + bh)).resize((W, H), Image.BICUBIC).convert("RGBA")
            slot = SPLIT_SLOT if layout == "SPLIT" else HERO_SLOT

        sx0, sy0, sw, sh = slot
        layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        lanes.reset()
        GIF_Q.clear()
        if layout != "FULL":
            scanlines(layer, t)
            hud_scan(layer, t, acc)
            neon_grid(layer, t, STEEL, y0=int(sh * 0.62))
        scene(layer, name, lt, t, a, acc)
        flush_gifs(layer)
        if layout != "FULL":
            slot_vignette(layer, a=22)
        speed_streaks(layer, t, PUNCH_T, acc)
        raw = layer

        if whip_from is not None and whip_from.size == layer.size:
            layer = whip_wipe(whip_from, layer, lt / 0.16, direction=whip_dir(name))

        layer = punch_zoom(layer, punch_scale(t, PUNCH_T, amt=0.045))
        shx, shy = shake_offset(t, HIT_T, amp=14)
        if layout == "SPLIT":
            # slot frame + head card
            frame.alpha_composite(head_card(fr, acc), (HEAD_CARD[0], HEAD_CARD[1]))
            ring(frame, HEAD_CARD, acc, 44)
            d = ImageDraw.Draw(frame)
            d.rounded_rectangle([sx0 - 2, sy0 - 2, sx0 + sw + 2, sy0 + sh + 2], 30, outline=SILVER + (60,), width=2)
        frame.alpha_composite(layer, (sx0 + shx, sy0 + shy))
        if layout == "HERO":
            frame.alpha_composite(head_pip(fr), (PIP[0], PIP[1]))
            ring(frame, PIP, acc, 26)
        return frame, raw

    XFADE = 0.24  # view-change zoom-dissolve length (s)
    prev_layer = None
    prev_name = None

    for n in todo:
        t = n / FPS
        idx = next(i for i, s in enumerate(SECT) if s[1] <= t < s[2] or i == len(SECT) - 1)
        sec = SECT[idx]
        name, a, b, layout, acc = sec
        lt = t - a

        if name != prev_name:
            prev_layer = None if (idx == 0 or a in LAYOUT_CHANGES) else prev_layer
            prev_name = name
        whip = prev_layer if (lt < 0.16 and a in WHIP_T) else None
        frame, raw = compose(n, t, sec, whip_from=whip)
        if whip is None:
            prev_layer = raw.copy()

        # View change (SPLIT/FULL/HERO): smooth zoom-dissolve from the outgoing view, rendered
        # live at the same t (head keeps talking), no flash, no shake. Works per frame, so
        # PREVIEW / RANGE chunks get it too.
        if a in LAYOUT_CHANGES and lt < XFADE and idx > 0:
            p = ease_in_out_quad(lt / XFADE)
            out_frame, _ = compose(n, t, SECT[idx - 1])
            zin = 1.035 - 0.035 * ease_out_cubic(lt / XFADE)
            if zin > 1.0005:
                zw, zh = int(W / zin), int(H / zin)
                frame = frame.crop(((W - zw) // 2, (H - zh) // 2, (W - zw) // 2 + zw, (H - zh) // 2 + zh)).resize((W, H), Image.BICUBIC)
            frame = Image.blend(out_frame, frame, p)

        # accent line the captions rest on (no strip / progress bar: Kevin 09-21 "truly pointless")
        d = ImageDraw.Draw(frame)
        d.rectangle([60, LINE_Y - 8, W - 60, LINE_Y - 4], fill=acc + (220,))

        draw_captions(frame, t, acc)

        frame.convert("RGB").save(f"{out}/f{n:05d}.jpg", quality=94)
        if PREVIEW:
            print(f"preview {n} t={t:.2f} {name} {layout}", flush=True)
        elif n % 60 == 0:
            print(f"{n}/{N}", flush=True)


    head_cap.release()
    print("frames done", len(todo), flush=True)
