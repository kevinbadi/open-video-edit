#!/usr/bin/env python3
"""Per-video choreography for the long-form landscape engine. Copy into the workdir as render.py.

Author: SECT (sections with layout + accent), T_* word anchors, KEYWORDS / KEY_COL (caption colours),
any bespoke cards, and scene(). Everything else (layouts, place(), cards, captions, head, loop)
comes from longform_engine. Reference cut: clone-projects/jev-intro-longform-animated/render.py.

LAYOUT RULE (Kevin 2026-09-21): SPLIT (slot left + head card right) is the DEFAULT for every
talking-to-camera stretch — it is the layout he likes most. FULL only for the hook / one
dramatic claim / the CTA. HERO only when a grid, thumbnails or b-roll IS the content.
"""
import math, os
from PIL import Image, ImageDraw
from longform_engine import *  # noqa: F401,F403
from longform_engine import words, DUR

OUT = os.environ.get("OUT", "frames/out")

# ── word anchors (absolute seconds; tabs() = first onset of the word at/after t) ──
T_HOOKWORD = tabs("treat", 1.0)
T_PRODUCT = tabs_any(["hyperedit", "hyper"], 4.0)
T_NUMBER = tabs("hundreds", 12.0)
T_CTA = tabs("demo", DUR - 8)

# ── sections: (name, start, end, layout, accent). SPLIT by default; switch on a spoken anchor. ──
SECT = [
    ("hook",    0.00,        3.00,    "FULL",  PINK),
    ("product", 3.00,        12.00,   "SPLIT", VIOLET),
    ("proof",   12.00,       20.00,   "HERO",  NEON),
    ("how",     20.00,       DUR - 6, "SPLIT", CYAN),
    ("cta",     DUR - 6,     DUR,     "SPLIT", RED),
]
KEYWORDS = {"treat", "hyperedit", "hundreds", "demo"}
KEY_COL = {"treat": PINK, "hyperedit": VIOLET, "hundreds": NEON, "demo": RED}

STACK = topic_marks(["claude", "openai", "github", "youtube"], size=120, fill=GRAPHITE + (255,))


def scene(layer, name, lt, t, a, acc):
    lw, lh = layer.size
    r = lambda T: max(0.0, T - 0.08 - a)  # noqa: E731  section-local onset (max 0.08 s lead)
    cx0 = lw // 2

    if name == "hook":
        # FULL layout: bright billboard on the RIGHT from frame 0 (no dark wash, no "?").
        place(layer, round_logo("jev", 300), 1330, 200, lt, -0.4, dur=0.01, idle=0)
        place(layer, sparkle_badge(250, VIOLET), 1700, 200, lt, -0.4, dur=0.01, idle=0)
        place(layer, wordmark("PRODUCT × PRODUCT", WHITE, 84), 1500, 420, lt, -0.4, dur=0.01, idle=0)
        place(layer, chip("what this video is about", PINK, fsz=30), 1500, 520, lt, -0.4, dur=0.01, idle=0)
        th = r(T_HOOKWORD)
        if lt >= th:
            place(layer, stamp_card("ABSOLUTE TREAT", PINK, fsz=72, w=700, h=160), 1500, 640, lt, th, dur=0.2, tilt=-8,
                  scale_pop=True, idle=0)
            light_hit(layer, 1500, 640, t, T_HOOKWORD, PINK)
            front_gif(gif_card("treat", max(0, lt - th), w=300, frame="round"), 1740, 860, lt, th + 0.05, **entrance(2))

    elif name == "product":
        # SPLIT: title top, left card + right hero, chips ~700, lane ~800
        draw_code_rain(layer, lt, n=14, col=acc)
        layer.alpha_composite(ghost_img("PRODUCT", 130, lw), (-60 + int(30 * math.sin(lt * 0.6)), 0))
        ticker(layer, "  TICKER COPY  ·  WHAT IT IS  ·  WHY IT MATTERS  ·  ", 850, lt, fill=acc + (110,))
        tp = r(T_PRODUCT)
        place(layer, big_text_card("SECTION TITLE", acc, fsz=56, w=1000, h=130), cx0, 70, lt, -0.35, dur=0.01, scale_pop=True)
        place(layer, terminal_card(lt + 0.4, [(0.0, "$ command", SILVER), (0.5, "✓ done", NEON)], title="TERMINAL",
                                   w=560, h=280, accent=acc), 340, 420, lt, -0.3, dur=0.01, frm="left")
        if lt >= tp:
            place(layer, sparkle_badge(320, VIOLET), 850, 420, lt, tp, dur=0.25, scale_pop=True, idle=0)
            light_hit(layer, 850, 420, t, T_PRODUCT, acc)
            light_rays(layer, 850, 420, t, acc)
        guarded_conveyor(layer, 800, lt, STACK, conveyor_marks, name="stack", speed=170, gap=22)

    elif name == "proof":
        # HERO: keep the bottom-right 520x292 (PIP) free of hero pieces; lanes may pass behind it.
        draw_code_rain(layer, lt, n=20, col=acc)
        tn = r(T_NUMBER)
        place(layer, big_text_card("PROOF", acc, fsz=56, w=1000, h=130), 700, 70, lt, -0.35, dur=0.01, scale_pop=True)
        if lt >= tn:
            place(layer, wordmark("HUNDREDS", acc, 150, sub="of forks"), 1440, 220, lt, tn, scale_pop=True, idle=0)
            light_hit(layer, 1440, 220, t, T_NUMBER, acc)
            front_gif(gif_card("clapping", max(0, lt - tn), w=560, frame="round"), 700, 520, lt, tn + 0.1, **entrance(4))

    elif name == "how":
        draw_code_rain(layer, lt, n=14, col=acc)
        place(layer, big_text_card("HOW IT WORKS", acc, fsz=56, w=1000, h=130), cx0, 70, lt, -0.35, dur=0.01, scale_pop=True)
        place(layer, workflow_card(min(1.0, lt / 1.5), w=1040, h=300, title="WORKFLOW", accent=acc), cx0, 380, lt, 0.2, frm="up")
        place(layer, timeline_card(lt, w=1040, h=330, accent=acc), cx0, 720, lt, 1.0, frm="up")

    else:  # cta (SPLIT)
        tc = r(T_CTA)
        place(layer, big_text_card("BUT FIRST... THE DEMO", acc, fsz=56, w=1000, h=130), cx0, 70, lt, -0.35, dur=0.01,
              scale_pop=True)
        place(layer, demo_card(lt, w=720, h=400), 420, 440, lt, tc - 0.6, frm="left", scale_pop=True)
        if lt >= tc:
            light_hit(layer, 420, 440, t, T_CTA, acc)
            place(layer, stamp_card("INSANE", acc, fsz=88, w=520, h=160), 900, 800, lt, tc + 0.3, dur=0.2, tilt=-8,
                  scale_pop=True, idle=0)


if __name__ == "__main__":
    run(SECT, scene,
        punch_words=["treat", "hyperedit", "hundreds", "demo"],   # ONE hero word per section, >=8 s apart
        extra_hits=[T_PRODUCT, T_NUMBER],                            # abs times that shake the slot
        keywords=KEYWORDS, key_col=KEY_COL, out=OUT)
