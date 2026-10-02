#!/usr/bin/env python3
"""v2: 3x more animated + fast-paced. Beat engine (sub-scene cuts every
~2-3s), fast tilted entrances/exits, Ken Burns drift, flash cuts, popping
kinetic captions with coral keywords. Same Megan narration."""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
# Talking-head pack lock (opensource-100, 2026-09-03): when this file is the
# asset half of a split render, the compositor must use AH=770, LAYER_Y=90,
# PACK_DY=210. Do not composite a 840-tall layer at y=42 — that hugs the top.
S = 1.5  # 1080/720 — asset sizes were authored at 720p; scale them, never the footage
def s(n):
    return int(round(n * S))
INK = (30, 28, 26); CORAL = (217, 111, 78); PAPER = (239, 232, 218); SAGE = (174, 191, 168)
from fonts import AR, CAP, GA, ML, F  # noqa: E402  Oswald display / Luckiest Guy captions / Menlo terminals
CAP_F = F(AR, s(58)); MONO = F(ML, s(22)); MONO_S = F(ML, s(19))

try:
    from claude_marks import (
        CLAUDE_WORDS,
        claude_kind,
        place_claude_invader,
        place_claude_sphinx,
        ensure_claude_marks,
    )
    ensure_claude_marks("assets/logos")
except Exception:
    CLAUDE_WORDS = {"claude", "anthropic", "opus", "sonnet", "haiku", "fable", "claudecode", "clod"}
    claude_kind = lambda *_a, **_k: None
    place_claude_invader = None
    place_claude_sphinx = None


def place_claude(layer, cx, cy, lt, word="", size=280, look_at=None, grab=None, grab_at=None, grab_t=0.0, hold=None):
    """Bundled Claude invader (dance / look / grab) + sphinx badge."""
    kind = claude_kind(word) if word else "invader"
    if place_claude_invader is None:
        return
    kw = dict(look_at=look_at, grab=grab, grab_at=grab_at, grab_t=grab_t, hold=hold)
    if kind == "sphinx" and place_claude_sphinx:
        place_claude_sphinx(layer, cx, cy, lt, size=max(120, int(size * 0.7)))
        place_claude_invader(layer, cx + size * 0.55, cy + size * 0.15, lt, size=int(size * 0.55), **kw)
    else:
        place_claude_invader(layer, cx, cy, lt, size=size, **kw)
        if place_claude_sphinx and grab_t < 0.2:
            place_claude_sphinx(layer, cx - size * 0.55, cy - size * 0.35, lt, size=int(size * 0.42))

words = json.load(open("audio/words.json"))
DUR = 62.9
SECT = [("hook", 0, 8.82), ("install", 8.82, 19.66), ("mvp", 19.66, 29.94),
        ("test", 29.94, 35.5), ("store", 35.5, 44.72), ("approve", 44.72, 51.88), ("cta", 51.88, DUR)]
KEYWORDS = {"claude", "app", "apps", "mvp", "expo", "zero", "apple", "chrome", "course", "free", "store",
            "opus", "sonnet", "haiku", "fable", "anthropic"}

ease = lambda p: 1 - (1 - max(0.0, min(1.0, p))) ** 3
def outp(p):  # overshoot pop
    p = max(0.0, min(1.0, p))
    return 1.15 - 0.15 * ease(p) if p < 1 else 1.0

def textured_bg(base, seed):
    rng = np.random.default_rng(seed)
    arr = np.tile(np.array(base, np.float32), (H + 160, W + 160, 1))
    arr += rng.normal(0, 3.5, (H + 160, W + 160, 1))
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    sh = Image.new("L", (W + 160, H + 160), 0); d = ImageDraw.Draw(sh)
    for cx, cy, rx, ry in [(140, 240, 400, 280), (700, 1040, 440, 320), (560, 110, 320, 200)]:
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=26)
    sh = sh.filter(ImageFilter.GaussianBlur(90))
    dark = Image.new("RGB", (W + 160, H + 160), tuple(max(0, c - 28) for c in base))
    return Image.composite(dark, img, sh)

BGS = {"paper": textured_bg(PAPER, 7), "sage": textured_bg(SAGE, 9), "white": textured_bg((246, 244, 239), 11)}

def shadow_card(size, radius, fill, blur=16, alpha=70):
    w, h = size; pad = blur * 2
    card = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + w, pad + h + 10], radius, fill=(20, 18, 16, alpha))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(blur // 2)))
    ImageDraw.Draw(card).rounded_rectangle([pad, pad, pad + w, pad + h], radius, fill=fill)
    return card

def mascot_on(card, x, y):
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([x, y, x + 46, y + 40], 10, fill=CORAL + (255,))
    d.rectangle([x + 8, y - 8, x + 14, y], fill=CORAL + (255,))
    d.rectangle([x + 30, y - 8, x + 36, y], fill=CORAL + (255,))
    d.ellipse([x + 10, y + 12, x + 18, y + 20], fill=(25, 22, 20, 255))
    d.ellipse([x + 28, y + 12, x + 36, y + 20], fill=(25, 22, 20, 255))

CACHE = {}
def cached(key, fn):
    if key not in CACHE: CACHE[key] = fn()
    return CACHE[key]

def terminal_card(nlines):
    def build():
        LINES = [("cmd", "claude install react-native expo"), ("dim", "resolving packages…"),
                 ("ok", "✓ react-native@0.76 installed"), ("ok", "✓ expo@52 installed"),
                 ("cmd", "npx expo start"), ("ok", "✓ metro running — scan QR")]
        card = shadow_card((560, 320), 22, (18, 17, 16, 255))
        d = ImageDraw.Draw(card); pad = 32
        d.text((pad + 24, pad + 14), "installing react native & expo", font=MONO_S, fill=(150, 145, 138, 255))
        d.line([pad, pad + 48, pad + 560, pad + 48], fill=(50, 48, 45, 255), width=1)
        y = pad + 68
        for kind, txt in LINES[:nlines]:
            col = {"cmd": (240, 238, 232, 255), "ok": (159, 227, 180, 255), "dim": (130, 126, 120, 255)}[kind]
            d.text((pad + 24, y), ("> " if kind == "cmd" else "  ") + txt, font=MONO, fill=col)
            y += 36
        mascot_on(card, pad + 462, pad - 30)
        return card
    return cached(("term", nlines), build)

def skill_tiles(n_on, cols=4, rows=3):
    """Computer / skills talk: a grid of SKILL.md files filling up."""
    def build():
        cw, ch, gap = s(140), s(78), s(10)
        w = cols * cw + (cols - 1) * gap
        h = rows * ch + (rows - 1) * gap
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        names = ["web-scrape", "inbox-bot", "seo-post", "dm-agent", "lead-gen",
                 "clone-vid", "tweet-ai", "pdf-parse", "cal-book", "sql-dump",
                 "ssh-keys", "wallet-sync"]
        pal = [CORAL, (120, 140, 235), (90, 200, 170), (230, 200, 120), (150, 110, 210), (210, 80, 80)]
        for i in range(cols * rows):
            r, c = divmod(i, cols)
            x = c * (cw + gap); y = r * (ch + gap)
            on = i < n_on
            fill = pal[i % len(pal)] + (255,) if on else (220, 214, 204, 255)
            d.rounded_rectangle([x, y, x + cw, y + ch], 12, fill=fill)
            if on:
                d.text((x + 10, y + 12), "SKILL.md", font=MONO_S, fill=(255, 252, 248, 255))
                d.text((x + 10, y + 40), names[i % len(names)], font=MONO_S, fill=(255, 252, 248, 220))
        return img
    return cached(("stiles", n_on, cols, rows), build)

def pc_monitor(lines):
    """A laptop/monitor with terminal lines. Use for computer / hack / code talk."""
    def build():
        card = shadow_card((s(640), s(300)), s(18), (18, 17, 16, 255))
        d = ImageDraw.Draw(card); pad = 32
        d.rounded_rectangle([pad + 20, pad + 16, pad + 560, pad + 220], 12, fill=(28, 26, 24, 255))
        d.rectangle([pad + 260, pad + 220, pad + 320, pad + 248], fill=(50, 48, 45, 255))
        d.rounded_rectangle([pad + 180, pad + 248, pad + 400, pad + 262], 6, fill=(70, 68, 64, 255))
        y = pad + 36
        cols = {"cmd": (159, 227, 180, 255), "bad": (231, 120, 100, 255), "dim": (130, 126, 120, 255)}
        for kind, txt in lines:
            d.text((pad + 36, y), txt, font=MONO_S, fill=cols[kind])
            y += 28
        return card
    return cached(("pc", tuple(lines)), build)

def scan_ring(size=220, col=(118, 185, 0)):
    def build():
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for i, r in enumerate((size * 0.22, size * 0.38, size * 0.48)):
            d.ellipse([size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r],
                      outline=col + (180 - i * 40,), width=4)
        d.ellipse([size / 2 - 8, size / 2 - 8, size / 2 + 8, size / 2 + 8], fill=col + (255,))
        return img
    return cached(("sring", size, col), build)

def draw_code_rain(layer, lt, n=18):
    glyphs = ["0x4f", "curl", "SKILL", "rm -rf", "ssh", "eval", "wget", "sudo",
              "token", "api_key", "chmod", "npm", "git", "YAML"]
    d = ImageDraw.Draw(layer)
    for i in range(n):
        x = 8 + (i * s(42)) % s(700)
        y = int((lt * s(110) + i * s(53)) % s(540)) - s(40)
        d.text((x, y), glyphs[i % len(glyphs)], font=MONO_S, fill=(118, 110, 98, 78))

def orbit_marks(layer, cx, cy, rx, ry, lt, imgs, speed=90):
    n = max(1, len(imgs))
    lw, lh = layer.size
    for i, im in enumerate(imgs):
        ang = math.radians(lt * speed + i * (360 / n))
        x = cx + int(rx * math.cos(ang)) - im.width // 2
        y = cy + int(ry * math.sin(ang)) - im.height // 2
        x = max(s(24), min(lw - im.width - s(24), x))
        y = max(0, min(lh - im.height, y))
        layer.alpha_composite(im, (x, y))

def conveyor_marks(layer, y, lt, imgs, speed=160, gap=22):
    """Horizontal conveyor. Use instead of orbit when the beat is a list/stream."""
    if not imgs:
        return
    total = sum(im.width + gap for im in imgs)
    if total < 1:
        return
    off = int((lt * speed) % total)
    x0 = s(24) - off
    lw = layer.size[0]
    for cycle in range(4):
        xx = x0 + cycle * total
        for im in imgs:
            if -im.width < xx < lw:
                layer.alpha_composite(im, (int(xx), int(y - im.height / 2)))
            xx += im.width + gap

def zigzag_marks(layer, cx, cy, rx, ry, lt, imgs, speed=70):
    """Triangle-wave lane + bounce. Not a circle."""
    n = max(1, len(imgs))
    lw, lh = layer.size
    for i, im in enumerate(imgs):
        phase = (lt * speed + i * (100 / n)) % 100
        u = phase / 50.0
        if u > 1:
            u = 2 - u
        x = int(cx - rx + 2 * rx * u - im.width / 2)
        y = int(cy + ry * math.sin(math.radians(phase * 7.2)) - im.height / 2)
        x = max(s(24), min(lw - im.width - s(24), x))
        y = max(0, min(lh - im.height, y))
        layer.alpha_composite(im, (x, y))

def explode_marks(layer, cx, cy, lt, t0, imgs, radius=200):
    """Burst from a point, then hold on the rim."""
    p = 1 - (1 - max(0.0, min(1.0, (lt - t0) / 0.42))) ** 3
    if p <= 0:
        return
    n = max(1, len(imgs))
    lw, lh = layer.size
    for i, im in enumerate(imgs):
        ang = math.radians(i * (360 / n) - 90)
        r = radius * p
        x = int(cx + r * math.cos(ang) - im.width / 2)
        y = int(cy + r * math.sin(ang) - im.height / 2)
        x = max(s(24), min(lw - im.width - s(24), x))
        y = max(0, min(lh - im.height, y))
        layer.alpha_composite(im, (x, y))

def ticker(layer, text, y, lt, speed=110, fill=(118, 110, 98, 88)):
    """News-ticker strip across the slot."""
    d = ImageDraw.Draw(layer)
    tw = int(d.textlength(text, font=MONO))
    span = tw + 80
    x = layer.size[0] - int((lt * speed) % (span + layer.size[0]))
    d.text((x, y), text, font=MONO, fill=fill)

def phone_card(ui_key, scale, extra=0):
    def build():
        w, h = int(s(300) * scale), int(s(620) * scale)
        card = shadow_card((w, h), int(s(46) * scale), (28, 27, 26, 255), blur=s(12))
        d = ImageDraw.Draw(card); pad = 24
        m = int(10 * scale)
        d.rounded_rectangle([pad + m, pad + m, pad + w - m, pad + h - m], int(38 * scale), fill=(250, 249, 246, 255))
        nw = int(90 * scale)
        d.rounded_rectangle([pad + w // 2 - nw // 2, pad + m + 6, pad + w // 2 + nw // 2, pad + m + 18], 8, fill=(28, 27, 26, 255))
        x, y, iw, ih, s = pad + m, pad + m, w - 2 * m, h - 2 * m, scale
        if ui_key == "grid":
            cols = [(217, 111, 78), (110, 140, 200), (140, 190, 140), (230, 200, 120), (190, 140, 190), (120, 190, 200)]
            i = 0
            for r in range(2):
                for c in range(3):
                    bx = x + int((30 + c * 90) * s); by = y + int((70 + r * 96) * s)
                    d.rounded_rectangle([bx, by, bx + int(64 * s), by + int(64 * s)], int(16 * s), fill=cols[i] + (255,)); i += 1
            d.rounded_rectangle([x + int(26 * s), y + ih - int(90 * s), x + iw - int(6 * s), y + ih - int(44 * s)], int(20 * s), fill=(236, 232, 224, 255))
        elif ui_key == "skeleton":
            for i in range(4):
                by = y + int((80 + i * 90) * s)
                d.rounded_rectangle([x + int(24 * s), by, x + iw - int(14 * s), by + int(60 * s)], int(12 * s), outline=(205, 200, 190, 255), width=3)
        elif ui_key.startswith("dash"):
            items = extra
            d.text((x + int(24 * s), y + int(40 * s)), "Your MVP", font=F(AR, int(26 * s)), fill=(35, 33, 30, 255))
            for i in range(items):
                by = y + int((100 + i * 74) * s)
                d.rounded_rectangle([x + int(24 * s), by, x + iw - int(14 * s), by + int(52 * s)], int(12 * s), fill=(240, 236, 228, 255))
                d.ellipse([x + int(36 * s), by + int(14 * s), x + int(60 * s), by + int(38 * s)], fill=(140, 190, 140, 255))
                d.rectangle([x + int(74 * s), by + int(18 * s), x + int(74 * s) + int((120 - i * 14) * s), by + int(34 * s)], fill=(180, 174, 164, 255))
        if extra == 99:
            d.ellipse([pad + w - 44, pad + 28, pad + w - 22, pad + 50], fill=(90, 190, 110, 255))
        return card
    return cached(("ph", ui_key, scale, extra), build)

def qr_card():
    def build():
        card = shadow_card((300, 300), 20, (18, 17, 16, 255))
        d = ImageDraw.Draw(card); rng = random.Random(42)
        cell = 11; ox, oy = 32 + 34, 32 + 34
        for r in range(21):
            for c in range(21):
                fixed = (r < 7 and c < 7) or (r < 7 and c > 13) or (r > 13 and c < 7)
                if fixed:
                    border = r % 7 in (0, 6) or c % 7 in (0, 6)
                    inner = 2 <= r % 7 <= 4 and 2 <= c % 7 <= 4
                    on = border or inner
                else:
                    on = rng.random() < 0.45
                if on: d.rectangle([ox + c * cell, oy + r * cell, ox + c * cell + cell - 2, oy + r * cell + cell - 2], fill=(248, 246, 242, 255))
        return card
    return cached("qr", build)

def chrome_card():
    def build():
        card = shadow_card((560, 360), 18, (250, 249, 246, 255))
        d = ImageDraw.Draw(card); pad = 32
        d.rounded_rectangle([pad, pad, pad + 560, pad + 44], 18, fill=(232, 228, 220, 255))
        for i, c in enumerate([(235, 100, 90), (240, 190, 80), (120, 200, 120)]):
            d.ellipse([pad + 16 + i * 26, pad + 15, pad + 30 + i * 26, pad + 29], fill=c + (255,))
        d.rounded_rectangle([pad + 100, pad + 10, pad + 460, pad + 34], 12, fill=(250, 249, 246, 255))
        d.text((pad + 114, pad + 12), "localhost:8081", font=MONO_S, fill=(120, 116, 110, 255))
        for i in range(3):
            by = pad + 80 + i * 80
            d.rounded_rectangle([pad + 30, by, pad + 530, by + 56], 12, fill=(238, 234, 226, 255))
            d.rectangle([pad + 50, by + 18, pad + 250 - i * 40, by + 36], fill=(200, 195, 186, 255))
        return card
    return cached("chrome", build)

def listing_card(rows):
    def build():
        card = shadow_card((560, 380), 22, (250, 249, 246, 255))
        d = ImageDraw.Draw(card); pad = 32
        d.rounded_rectangle([pad + 24, pad + 30, pad + 100, pad + 106], 18, fill=CORAL + (255,))
        labels = ["title", "description", "certificates"]
        for i in range(rows):
            yy = pad + 40 + i * 44 if i else pad + 40
            yy = pad + 36 + i * 50
            d.rounded_rectangle([pad + 120, yy, pad + 530, yy + 36], 10, fill=(238, 234, 226, 255))
            d.text((pad + 134, yy + 6), labels[i] if i < 3 else "", font=F(AR, 20), fill=(120, 116, 110, 255))
            d.line([pad + 470, yy + 12, pad + 482, yy + 26, pad + 502, yy + 6], fill=(90, 190, 110, 255), width=5)
        for i in range(4):
            by = pad + 210 + i * 36
            d.rectangle([pad + 24, by, pad + 530 - (i % 3) * 60, by + 14], fill=(210, 205, 196, 255))
        return card
    return cached(("list", rows), build)

def check_row(label, on):
    def build():
        img = Image.new("RGBA", (480, 70), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, 480, 66], 16, fill=(250, 249, 246, 255))
        col = (90, 190, 110, 255) if on else (205, 200, 190, 255)
        d.ellipse([16, 15, 52, 51], fill=col)
        if on: d.line([25, 33, 34, 43, 46, 24], fill=(255, 255, 255, 255), width=5)
        d.text((70, 16), label, font=F(AR, 30), fill=(35, 33, 30, 255))
        return img
    return cached(("chk", label, on), build)

def big_text_card(txt, fill=CORAL, fg=(255, 252, 248, 255), fsz=58, w=620, h=140):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w, h], 26, fill=fill + (255,))
        f2 = F(AR, fsz)
        d.text(((w - d.textlength(txt, font=f2)) / 2, (h - fsz) / 2 - 6), txt, font=f2, fill=fg)
        return img
    return cached(("btc", txt, fsz, w, h), build)

def chip(txt):
    def build():
        f2 = MONO
        tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(txt, font=f2))
        img = Image.new("RGBA", (tw + 44, 54), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, tw + 44, 54], 14, fill=(24, 22, 20, 255))
        d.text((22, 14), txt, font=f2, fill=(159, 227, 180, 255))
        return img
    return cached(("chip", txt), build)

def ghost_img(text, size):
    def build():
        img = Image.new("RGBA", (W + 400, size + 60), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        f2 = F(GA, size)
        d.text((200, 10), text, font=f2, fill=(118, 110, 98, 80))
        return img
    return cached(("gh", text, size), build)

def loop_arrows(angle):
    img = Image.new("RGBA", (260, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for a0 in (20, 200):
        d.arc([20, 20, 240, 240], a0, a0 + 130, fill=CORAL + (255,), width=14)
        tip = math.radians(a0 + 130)
        tx, ty = 130 + 110 * math.cos(tip), 130 + 110 * math.sin(tip)
        pa = math.radians(a0 + 130 + 12)
        d.polygon([(tx, ty), (130 + 128 * math.cos(pa), 130 + 128 * math.sin(pa)), (130 + 92 * math.cos(pa), 130 + 92 * math.sin(pa))], fill=CORAL + (255,))
    return img.rotate(angle, resample=Image.BICUBIC)

def place(frame, img, cx, cy, lt, t0, dur=0.3, frm="up", tilt=0.0, idle=5, scale_pop=False, exit_at=None):
    """fast entrance from a direction + optional tilt + idle bob + exit."""
    p = ease((lt - t0) / dur)
    if p <= 0: return
    alpha = p
    if exit_at is not None:
        q = (lt - exit_at) / 0.22
        if q >= 1: return
        if q > 0:
            alpha = min(alpha, 1 - q); p2 = ease(q)
        else: p2 = 0
    else: p2 = 0
    off = s(90) * (1 - p)
    dx, dy = {"up": (0, off), "down": (0, -off), "left": (off, 0), "right": (-off, 0)}[frm]
    # Idle drift (Kevin 2026-09-11, second-brain: "far too much pulsing"):
    # big pieces (>=400px) sit still; small pieces drift slowly with their
    # own phase + period so the slot never breathes in sync.
    if img.width < 400 and idle:
        seed = (int(cx) * 73 + int(cy) * 151) % 1000 / 1000.0
        period = 3.2 + 2.4 * seed
        amp = min(idle, 3)
        dx += amp * 0.6 * math.sin((lt * 2 * math.pi) / (period * 1.37) + seed * 6.28)
        dy += amp * math.sin((lt * 2 * math.pi) / period + seed * 6.28)
    dy -= s(120) * p2  # exit: fly up
    im = img
    if scale_pop:
        s = outp((lt - t0) / dur)
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    if tilt:
        im = im.rotate(tilt, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    x = int(cx - im.width / 2 + dx)
    y = int(cy - im.height / 2 + dy)
    # Keep left/right edges on the 1080 canvas
    x = max(s(24), min(W - im.width - s(24), x)) if im.width + s(48) <= W else max(0, min(W - im.width, x))
    frame.alpha_composite(im, (x, y))

def word_at(t):
    for w, a, b in words:
        if a <= t <= b + 0.1: return w.strip().rstrip(".,!?").lower()
    return None

os.makedirs("frames/out2", exist_ok=True)
N = int(DUR * FPS)
SECT_BG = {"hook": "paper", "install": "paper", "mvp": "sage", "test": "paper", "store": "white", "approve": "sage", "cta": "paper"}
CAP_DARK = {"hook": 1, "install": 1, "mvp": 0, "test": 1, "store": 1, "approve": 0, "cta": 1}

for n in range(N):
    t = n / FPS
    name, a, b = next(s for s in SECT if s[1] <= t < s[2] or s is SECT[-1])
    lt, sd = t - a, b - a
    # Ken Burns: slow zoom-in across the section on the oversized bg
    z = 1.0 + 0.06 * (lt / sd)
    bw, bh = int((W + 160) / z), int((H + 160) / z)
    bg = BGS[SECT_BG[name]]
    ox, oy = (bg.width - bw) // 2, (bg.height - bh) // 2
    frame = bg.crop((ox, oy, ox + bw, oy + bh)).resize((W, H), Image.BICUBIC).convert("RGBA")
    gsl = int(40 * math.sin(lt * 0.6))  # ghost parallax drift

    if name == "hook":
        frame.alpha_composite(ghost_img("zero code", 128), (-200 + gsl, 90))
        place(frame, phone_card("grid", 0.9), W // 2, 540, lt, 0.05, frm="up", scale_pop=True, exit_at=2.6)
        place(frame, big_text_card("BUILD AN APP", INK, fsz=54), W // 2, 300, lt, 2.7, frm="left", tilt=-2, exit_at=5.4)
        place(frame, phone_card("grid", 0.55), 210, 640, lt, 2.85, frm="left", tilt=-6, exit_at=5.4)
        place(frame, phone_card("skeleton", 0.55), 510, 640, lt, 3.0, frm="right", tilt=6, exit_at=5.4)
        place(frame, big_text_card("ZERO CODE", CORAL, fsz=64, w=560, h=150), W // 2, 460, lt, 5.55, scale_pop=True)
        place(frame, big_text_card("App Store ready", (246, 244, 239), (30, 28, 26, 255), 40, 460, 100), W // 2, 640, lt, 6.1, frm="down")
    elif name == "install":
        frame.alpha_composite(ghost_img("first", 140), (-140 + gsl, 50))
        nl = min(6, 1 + int(lt / 0.5))
        place(frame, terminal_card(nl), W // 2, 380, lt, 0.05, frm="up", exit_at=5.6)
        place(frame, chip("claude install react-native expo"), W // 2, 720, lt, 0.6, frm="down", exit_at=5.6)
        place(frame, phone_card("grid", 0.5), 200, 480, lt, 5.8, frm="left", tilt=-7)
        place(frame, phone_card("grid", 0.5), 520, 480, lt, 6.0, frm="right", tilt=7)
        place(frame, big_text_card("iOS", (28, 27, 26), fsz=44, w=200, h=92), 200, 830, lt, 6.3, scale_pop=True)
        place(frame, big_text_card("ANDROID", (140, 190, 140), fsz=40, w=280, h=92), 520, 830, lt, 6.5, scale_pop=True)
        place(frame, big_text_card("ONE CODEBASE", CORAL, fsz=48, w=520, h=110), W // 2, 990, lt, 7.6, frm="up", scale_pop=True)
    elif name == "mvp":
        frame.alpha_composite(ghost_img("MVP", 170), (-80 + gsl, 60))
        items = min(4, 1 + int(max(0, lt - 2.0) / 1.1))
        place(frame, phone_card("skeleton", 0.8), W // 2, 560, lt, 0.05, frm="up", exit_at=2.0)
        place(frame, phone_card("dash", 0.8, items), W // 2, 560, lt, 2.1, frm="up")
        place(frame, big_text_card("core function first", (246, 244, 239), (30, 28, 26, 255), 36, 440, 90), W // 2, 1000, lt, 0.7, frm="down", exit_at=4.6)
        if lt > 6.2:
            frame.alpha_composite(loop_arrows(-(lt - 6.2) * 140), (W // 2 - 130, 250))
        place(frame, big_text_card("REACTIVATION LOOP", CORAL, fsz=40, w=520, h=100), W // 2, 1010, lt, 6.4, scale_pop=True)
    elif name == "test":
        frame.alpha_composite(ghost_img("test it", 120), (-140 + gsl, 50))
        place(frame, chrome_card(), W // 2, 380, lt, 0.05, frm="up", exit_at=2.1)
        place(frame, qr_card(), 230, 480, lt, 2.25, frm="left", tilt=-4)
        place(frame, phone_card("grid", 0.55), 530, 520, lt, 2.45, frm="right", tilt=5)
        place(frame, big_text_card("works on your phone", (28, 27, 26), fsz=40, w=560, h=100), W // 2, 920, lt, 3.4, scale_pop=True)
    elif name == "store":
        frame.alpha_composite(ghost_img("polish", 130), (-140 + gsl, 40))
        rows = min(3, 1 + int(lt / 1.2))
        place(frame, listing_card(rows), W // 2, 400, lt, 0.05, frm="up", exit_at=4.7)
        place(frame, chip("/app-store-screens"), W // 2, 740, lt, 1.2, frm="down", exit_at=4.7)
        for i, xx in enumerate([170, 360, 550]):
            place(frame, phone_card("grid" if i != 1 else "dash", 0.42, 3 if i == 1 else 0), xx, 560, lt, 4.9 + i * 0.18, frm="up", tilt=(-8, 0, 8)[i])
        place(frame, big_text_card("screenshots: automatic", (28, 27, 26), fsz=38, w=540, h=96), W // 2, 950, lt, 5.6, scale_pop=True)
    elif name == "approve":
        frame.alpha_composite(ghost_img("approved", 118), (-140 + gsl, 46))
        for i, lab in enumerate(["Submitted", "In review", "Approved"]):
            on = lt > 0.6 + i * 1.5
            place(frame, check_row(lab, on), W // 2, 330 + i * 92, lt, 0.15 + i * 0.15, frm="left" if i % 2 == 0 else "right", scale_pop=on and lt < 0.9 + i * 1.5)
        place(frame, phone_card("grid", 0.55, 99), W // 2, 800, lt, 4.7, frm="up", scale_pop=True)
        place(frame, big_text_card("YOUR APP IS LIVE", (90, 160, 100), fsz=44, w=540, h=104), W // 2, 1040, lt, 5.1, scale_pop=True)
    else:
        frame.alpha_composite(ghost_img("one-hour course", 84), (-160 + gsl, 60))
        card = shadow_card((560, 300), 22, (18, 17, 16, 255))
        dd = ImageDraw.Draw(card)
        cols = [(217, 111, 78), (110, 140, 200), (140, 190, 140), (230, 200, 120)]
        for i in range(4):
            bx = 32 + 36 + (i % 2) * 260; by = 32 + 30 + (i // 2) * 120
            dd.rounded_rectangle([bx, by, bx + 220, by + 92], 14, fill=(32, 30, 28, 255))
            dd.rectangle([bx + 14, by + 16, bx + 56, by + 76], fill=cols[i] + (255,))
            dd.rectangle([bx + 70, by + 24, bx + 200, by + 38], fill=(150, 145, 138, 255))
            dd.rectangle([bx + 70, by + 48, bx + 170, by + 60], fill=(90, 87, 82, 255))
        place(frame, card, W // 2, 380, lt, 0.05, frm="up", tilt=-2, exit_at=5.6)
        place(frame, big_text_card("FULL 1-HOUR COURSE", (28, 27, 26), fsz=42, w=560, h=100), W // 2, 680, lt, 1.1, frm="down", exit_at=5.6)
        # CTA lands once (overshoot) and then holds still: no continuous pulse.
        big = big_text_card('COMMENT "APP"', CORAL, fsz=60, w=620, h=150)
        if lt > 5.8:
            pop = outp(min(1, (lt - 5.8) / 0.4))
            bb = big.resize((max(1, int(620 * pop)), max(1, int(150 * pop))))
            frame.alpha_composite(bb, (int(W / 2 - bb.width / 2), int(560 - bb.height / 2)))
            ar = Image.new("RGBA", (90, 110), (0, 0, 0, 0))
            d2 = ImageDraw.Draw(ar)
            d2.polygon([(45, 100), (10, 55), (30, 55), (30, 10), (60, 10), (60, 55), (80, 55)], fill=INK + (255,))
            bounce = int(14 * abs(math.sin(lt * 5)))
            frame.alpha_composite(ar, (W // 2 - 45, 720 + bounce))

    # flash cut at later section boundaries only (never wipe frame 0)
    if lt < 0.1 and a > 0.05:
        white = Image.new("RGBA", (W, H), (255, 253, 248, int(200 * (1 - lt / 0.1))))
        frame.alpha_composite(white)

    wd = word_at(t)
    if wd:
        d = ImageDraw.Draw(frame)
        key = wd in KEYWORDS
        col = (CORAL + (255,)) if key else (INK + (255,) if CAP_DARK[name] else (252, 251, 248, 255))
        shcol = (255, 255, 255, 150) if CAP_DARK[name] else (20, 18, 16, 170)
        # pop scale on word onset
        ons = next((aa for ww, aa, bb2 in words if ww.strip().rstrip(".,!?").lower() == wd and aa <= t <= bb2 + 0.1), t)
        fs = int(58 * (1 + 0.18 * max(0, 1 - (t - ons) / 0.12))) if key else int(58 * (1 + 0.10 * max(0, 1 - (t - ons) / 0.10)))
        cf = F(AR, fs)
        tw = d.textlength(wd, font=cf)
        x, y = (W - tw) / 2, 1150 - (fs - 58) // 2
        d.text((x + 2, y + 4), wd, font=cf, fill=shcol)
        d.text((x, y), wd, font=cf, fill=col)

    frame.convert("RGB").save(f"frames/out2/f{n:05d}.jpg", quality=90)
    if n % 300 == 0: print(f"{n}/{N}")
print("frames done")
