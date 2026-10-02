#!/usr/bin/env python3
"""v3 SPLIT FORMAT for a USER talking-head clip: animations in the top 55%
(safe-zone padded), the provided talking-head in a rounded band across the
bottom 45%. Beat engine + pacing from v2.

THIS FILE IS AN EXAMPLE (first Megan course video). Copy it into
projects/<slug>-animated/, then rewrite the per-section choreography
to match THIS clip's narration. Keep the band reader, 1:1 composite, flash-cut,
and caption code. Band footage is renders/talking_band45.mp4 from
scripts/prep_talking_head.py (not a HeyGen export).

Layout (Kevin 2026-09-03, opensource-100 pack lock): ALWAYS 1080×1920.
AH=770 composited 1:1 at LAYER_Y=90 (canvas 90..860). PACK_DY=210 on every
place() cy so the pack sits just above captions (CAP_Y=867), not hugging
the top. Band is 1056×960 at y=960 from a 1080p talking-head crop — never
704×640 on a 720 canvas. Cards ~960 wide. Beat t0 = spoken_word_start -
section_start (max 0.1s lead). Example y values below are 720-era; wrap
with s() (×1.5) so they land on 1080, then PACK_DY drops them.
"""
import json, math, os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import importlib.util
spec = importlib.util.spec_from_file_location("r2", "render2_assets.py")

# ---- reuse v2 asset builders by importing render2's functions via exec of its top half
SRC = open("render2.py").read()
ASSETS = SRC.split("os.makedirs")[0]  # everything before the render loop
exec(compile(ASSETS, "render2_assets", "exec"))

# Hyper-edit + media marks (2026-09-05): copy hyper_edits.py + media_marks.py
# next to this file. See SKILL.md 5b/5c/7b/7c for the rules.
from hyper_edits import (keyword_onsets, hyperframe, whip_wipe, whip_dir, caption_impact)
from media_marks import gif_card, figure_row, figure_spotlight, figure_card, figure_round

AH = 770            # slot ABOVE captions — 1080x1920 (opensource-100 pack lock)
LAYER_Y = 90        # sit the pack just above captions, not hugging the top
PACK_DY = 210       # drop authored cy so heroes meet the caption line
BAND_Y = 960        # talking-head band top
CAP_Y = 867         # caption baseline (in the gap above the band)
SAFE_X = (36, 1044) # keep asset edges on-canvas
BAND_W, BAND_H = 1056, 960
if (W, H) != (1080, 1920):
    raise SystemExit(f"split talking-head must be 1080x1920, got {W}x{H}")
DUR = 62.9
N = int(DUR * FPS)

# Talking-head band (1056x960 @30fps — 1080p crop, never 704x640)
band_cap = cv2.VideoCapture("renders/talking_band45.mp4")
band_mask = Image.new("L", (BAND_W, BAND_H), 0)
ImageDraw.Draw(band_mask).rounded_rectangle([0, 0, BAND_W - 1, BAND_H + 60], 60, fill=255)

def band_frame():
    ok, fr = band_cap.read()
    if not ok:
        return None
    img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    img.putalpha(band_mask)
    return img

R = lambda img, sc: img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BICUBIC) if sc != 1 else img
px = lambda n: int(round(n * 1.5))  # 720-era example coords → 1080 canvas
_place = place
def place(frame, img, cx, cy, *args, **kwargs):
    return _place(frame, img, px(cx), px(cy) + PACK_DY, *args, **kwargs)

os.makedirs("frames/out5", exist_ok=True)
last_band = None
CUT_T = [a for _, a, _ in SECT[1:]]              # section cuts (never the hook)
WHIP_T, HF_T = CUT_T[::2], CUT_T[1::2]           # one treatment per cut, never both
prev_layer = None
for n in range(N):
    t = n / FPS
    name, a, b = next(s for s in SECT if s[1] <= t < s[2] or s is SECT[-1])
    lt, sd = t - a, b - a
    z = 1.0 + 0.05 * (lt / sd)
    bg = BGS[SECT_BG[name]] if False else BGS[{"hook": "paper", "install": "paper", "mvp": "sage", "test": "paper", "store": "white", "approve": "sage", "cta": "paper"}[name]]
    bw, bh = int((W + 160) / z), int((H + 160) / z)
    ox, oy = (bg.width - bw) // 2, (bg.height - bh) // 2
    frame = bg.crop((ox, oy, ox + bw, oy + bh)).resize((W, H), Image.BICUBIC).convert("RGBA")
    layer = Image.new("RGBA", (W, AH), (0, 0, 0, 0))
    gsl = int(30 * math.sin(lt * 0.6))

    if name == "hook":
        layer.alpha_composite(R(ghost_img("zero code", 96), 1), (-160 + gsl, 70))
        place(layer, phone_card("grid", 0.62), 360, 430, lt, -0.4, dur=0.01, frm="up", scale_pop=True, exit_at=2.6)
        place(layer, big_text_card("BUILD AN APP", INK, fsz=40, w=440, h=100), 360, 220, lt, 2.7, frm="left", tilt=-2, exit_at=5.4)
        place(layer, phone_card("grid", 0.40), 230, 520, lt, 2.85, frm="left", tilt=-6, exit_at=5.4)
        place(layer, phone_card("skeleton", 0.40), 490, 520, lt, 3.0, frm="right", tilt=6, exit_at=5.4)
        place(layer, big_text_card("ZERO CODE", CORAL, fsz=50, w=430, h=118), 360, 360, lt, 5.55, scale_pop=True)
        place(layer, big_text_card("App Store ready", (246, 244, 239), (30, 28, 26, 255), 30, 350, 78), 360, 520, lt, 6.1, frm="down")
    elif name == "install":
        layer.alpha_composite(R(ghost_img("first", 104), 1), (-110 + gsl, 44))
        nl = min(6, 1 + int(lt / 0.5))
        place(layer, R(terminal_card(nl), 0.82), 360, 330, lt, 0.05, frm="up", exit_at=5.6)
        place(layer, R(chip("claude install react-native expo"), 0.9), 360, 590, lt, 0.6, frm="down", exit_at=5.6)
        place(layer, phone_card("grid", 0.38), 215, 380, lt, 5.8, frm="left", tilt=-7)
        place(layer, phone_card("grid", 0.38), 505, 380, lt, 6.0, frm="right", tilt=7)
        place(layer, big_text_card("iOS", (28, 27, 26), fsz=34, w=150, h=72), 215, 640, lt, 6.3, scale_pop=True)
        place(layer, big_text_card("ANDROID", (140, 190, 140), fsz=30, w=210, h=72), 505, 640, lt, 6.5, scale_pop=True)
        place(layer, big_text_card("ONE CODEBASE", CORAL, fsz=36, w=400, h=86), 360, 745, lt, 7.6, frm="up", scale_pop=True)
    elif name == "mvp":
        layer.alpha_composite(R(ghost_img("MVP", 120), 1), (-60 + gsl, 50))
        items = min(4, 1 + int(max(0, lt - 2.0) / 1.1))
        place(layer, phone_card("skeleton", 0.58), 360, 430, lt, 0.05, frm="up", exit_at=2.0)
        place(layer, phone_card("dash", 0.58, items), 360, 430, lt, 2.1, frm="up")
        place(layer, big_text_card("core function first", (246, 244, 239), (30, 28, 26, 255), 28, 340, 70), 360, 740, lt, 0.7, frm="down", exit_at=4.6)
        if lt > 6.2:
            la = R(loop_arrows(-(lt - 6.2) * 140), 0.72)
            layer.alpha_composite(la, (360 - la.width // 2, 160 - la.height // 2 + 60))
        place(layer, big_text_card("REACTIVATION LOOP", CORAL, fsz=30, w=390, h=76), 360, 745, lt, 6.4, scale_pop=True)
    elif name == "test":
        layer.alpha_composite(R(ghost_img("test it", 90), 1), (-110 + gsl, 44))
        place(layer, R(chrome_card(), 0.82), 360, 320, lt, 0.05, frm="up", exit_at=2.1)
        place(layer, R(qr_card(), 0.9), 235, 400, lt, 2.25, frm="left", tilt=-4)
        place(layer, phone_card("grid", 0.42), 505, 430, lt, 2.45, frm="right", tilt=5)
        place(layer, big_text_card("works on your phone", (28, 27, 26), fsz=30, w=420, h=76), 360, 730, lt, 3.4, scale_pop=True)
    elif name == "store":
        layer.alpha_composite(R(ghost_img("polish", 96), 1), (-110 + gsl, 36))
        rows = min(3, 1 + int(lt / 1.2))
        place(layer, R(listing_card(rows), 0.82), 360, 330, lt, 0.05, frm="up", exit_at=4.7)
        place(layer, R(chip("/app-store-screens"), 0.9), 360, 600, lt, 1.2, frm="down", exit_at=4.7)
        for i, xx in enumerate([190, 360, 530]):
            place(layer, phone_card("grid" if i != 1 else "dash", 0.30, 3 if i == 1 else 0), xx, 440, lt, 4.9 + i * 0.18, frm="up", tilt=(-8, 0, 8)[i])
        place(layer, big_text_card("screenshots: automatic", (28, 27, 26), fsz=28, w=400, h=72), 360, 730, lt, 5.6, scale_pop=True)
    elif name == "approve":
        layer.alpha_composite(R(ghost_img("approved", 88), 1), (-110 + gsl, 40))
        for i, lab in enumerate(["Submitted", "In review", "Approved"]):
            on = lt > 0.6 + i * 1.5
            place(layer, R(check_row(lab, on), 0.9), 360, 240 + i * 78, lt, 0.15 + i * 0.15, frm="left" if i % 2 == 0 else "right", scale_pop=on and lt < 0.9 + i * 1.5)
        place(layer, phone_card("grid", 0.40, 99), 360, 560, lt, 4.7, frm="up", scale_pop=True)
        place(layer, big_text_card("YOUR APP IS LIVE", (90, 160, 100), fsz=32, w=400, h=80), 360, 745, lt, 5.1, scale_pop=True)
    else:
        layer.alpha_composite(R(ghost_img("one-hour course", 64), 1), (-130 + gsl, 50))
        card = shadow_card((560, 300), 22, (18, 17, 16, 255))
        dd = ImageDraw.Draw(card)
        cols = [(217, 111, 78), (110, 140, 200), (140, 190, 140), (230, 200, 120)]
        for i in range(4):
            bx = 32 + 36 + (i % 2) * 260; by = 32 + 30 + (i // 2) * 120
            dd.rounded_rectangle([bx, by, bx + 220, by + 92], 14, fill=(32, 30, 28, 255))
            dd.rectangle([bx + 14, by + 16, bx + 56, by + 76], fill=cols[i] + (255,))
            dd.rectangle([bx + 70, by + 24, bx + 200, by + 38], fill=(150, 145, 138, 255))
            dd.rectangle([bx + 70, by + 48, bx + 170, by + 60], fill=(90, 87, 82, 255))
        place(layer, R(card, 0.78), 360, 300, lt, 0.05, frm="up", tilt=-2, exit_at=5.6)
        place(layer, big_text_card("FULL 1-HOUR COURSE", (28, 27, 26), fsz=32, w=430, h=80), 360, 520, lt, 1.1, frm="down", exit_at=5.6)
        pulse = 1 + 0.05 * math.sin(lt * 6)
        big = big_text_card('COMMENT "APP"', CORAL, fsz=46, w=470, h=116)
        if lt > 5.8:
            bb = R(big, pulse * min(1, outp((lt - 5.8) / 0.4)))
            layer.alpha_composite(bb, (int(360 - bb.width / 2), int(360 - bb.height / 2)))
            ar = Image.new("RGBA", (76, 96), (0, 0, 0, 0))
            d2 = ImageDraw.Draw(ar)
            d2.polygon([(38, 88), (8, 48), (26, 48), (26, 8), (50, 8), (50, 48), (68, 48)], fill=INK + (255,))
            bounce = int(12 * abs(math.sin(lt * 5)))
            layer.alpha_composite(ar, (360 - 38, 520 + bounce))

    # cuts alternate: even section cuts whip, odd ones get a hyperframe insert
    if lt < 0.16 and a in WHIP_T and prev_layer is not None:
        layer = whip_wipe(prev_layer, layer, lt / 0.16, direction=whip_dir(name))
    else:
        prev_layer = layer  # last full frame of this section feeds the next whip
    frame.alpha_composite(layer, (0, LAYER_Y))  # 1:1 fill, nudged down toward captions
    hyperframe(frame, t, HF_T, FPS, region=(0, LAYER_Y, W, AH))

    # talking-head band (bottom 45%) — LOCKED STILL (Kevin 2026-09-05): no
    # punch-in zoom, no shake, no offset. The hyper-edit lives in the
    # animation slot only; a moving talking head bothers viewers.
    bf = band_frame()
    if bf is not None: last_band = bf
    if last_band is not None:
        frame.alpha_composite(last_band, (12, BAND_Y))

    # caption in the gap above the band
    wd = word_at(t)
    if wd:
        d = ImageDraw.Draw(frame)
        dark = name not in ("mvp", "approve")
        key = wd in KEYWORDS
        col = (CORAL + (255,)) if key else (INK + (255,) if dark else (252, 251, 248, 255))
        shcol = (255, 255, 255, 150) if dark else (20, 18, 16, 170)
        ons = next((aa for ww, aa, bb2 in words if ww.strip().rstrip(".,!?").lower() == wd and aa <= t <= bb2 + 0.1), t)
        fs = int(px(44) * caption_impact(t, ons, key))
        cf = F(AR, fs)
        tw = d.textlength(wd, font=cf)
        x, y = (W - tw) / 2, CAP_Y - (fs - px(44)) // 2
        d.text((x + 2, y + 4), wd, font=cf, fill=shcol)
        d.text((x, y), wd, font=cf, fill=col)

    frame.convert("RGB").save(f"frames/out5/f{n:05d}.jpg", quality=95)
    if n % 300 == 0: print(f"{n}/{N}")
band_cap.release()
print("frames done")
