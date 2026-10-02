#!/usr/bin/env python3
"""Fireship-style template + device demo reel. Copy into a workdir as render.py and replace SHOTS.

Real edits: narration drives everything. Put the VO at audio/voice.wav, transcribe to
audio/words.json ([[word, start, end], ...], small.en + initial_prompt of product names),
then time every Layer to the spoken word with at(WORDS, "word", after).
Demo mode (no audio/words.json): renders a ~24 s silent reel of every device.
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fireship_engine import *  # noqa: F401,F403
from PIL import Image

FOOTAGE = os.environ.get("DEMO_FOOTAGE", "")          # any 16:9 clip (keynote / screen recording)
LOGO = os.environ.get("DEMO_LOGO", "")                # a product logo PNG
GIF_DIR = os.environ.get("DEMO_GIF_DIR", "")          # a fetched Giphy frame dir (fetch_giphy.py)


def gif_frame(lt: float):
    fs = sorted(glob.glob(os.path.join(GIF_DIR, "f*.png"))) if GIF_DIR else []
    if not fs:
        return None
    return Image.open(fs[int(lt * 30) % len(fs)]).convert("RGBA")


logo = Image.open(LOGO).convert("RGBA").resize((260, 260)) if LOGO else None

DOC = [
    "VIKTOR is a personal AI agent. It doesn't just answer",
    "questions, it actually does the work. It helps teams",
    "stay on top of things, takes tasks off their plate,",
    "and turns long-term goals into action plans.",
]

SHOTS = [
    # 0: kinetic cold open, words land on (demo) onsets
    Shot(0.0, 2.0, bg=lambda lt, t: kinetic_words([("Earlier", 0.0), ("this", 0.35), ("week,", 0.7), ("while", 1.2), ("I", 1.45), ("was", 1.6)], lt),
         note="kinetic opener"),
    # 1: doc card bulges in, then the orange highlighter reads along
    Shot(2.0, 5.2, layers=[
        Layer(0.0, 9, img=lambda lt: doc_card(DOC, phrase_spans(DOC, "It helps teams stay on top of things, takes tasks off their plate,"), p=clamp01((lt - 0.8) / 2.0),
                                               bullet=True), xy=(W / 2, H / 2), anim="bulge"),
    ], note="doc + highlighter"),
    # 2: footage, logo slides in, red block sticker on the product name
    Shot(5.2, 8.0, bg=video_bg(FOOTAGE, 3.0) if FOOTAGE else black_bg, glitch_in=True, layers=[
        Layer(0.3, 9, img=logo, xy=(330, 300), anim="slide_left"),
        Layer(1.2, 9, img=sticker("VIKTOR", "red_block", 220), xy=(W / 2, 840), anim="pop"),
    ], note="footage + logo + red block"),
    # 3: tweet stack (tilted, offset) on black
    Shot(8.0, 10.4, layers=[
        Layer(0.0, 9, img=tweet_card("Kev Builds Apps", "@kevbuildsapps", "VIKTOR just onboarded our whole client team into Slack. One agent, one memory, zero chaos.", meta="12:37 AM · Sep 26, 2026 · 94.6K Views"), xy=(820, 430), tilt=2, anim="pop"),
        Layer(0.9, 9, img=tweet_card("Agency Owner", "@agencyowner", "ok this is actually insane for client onboarding"), xy=(1180, 780), tilt=-4, anim="slide_right"),
    ], note="tweet stack"),
    # 4: headline cards stacking + stamp
    Shot(10.4, 12.8, glitch_in=True, layers=[
        Layer(0.0, 9, img=headline_card("The Verge", "AI agents are coming for your group chats", "Teams are handing Slack to autonomous assistants"), xy=(820, 420), tilt=-2),
        Layer(0.7, 9, img=headline_card("Reuters", "Startups race to build the first real AI employee", dark=True), xy=(1120, 700), tilt=3, anim="slide_up"),
        Layer(1.4, 9, img=sticker("DISCONTINUED", "stamp", 96), xy=(1350, 250), tilt=-12),
    ], note="headlines + stamp"),
    # 5: meme cut-in + comic sticker + starburst
    Shot(12.8, 15.0, bg=lambda lt, t: fit_cover(g.convert("RGB")) if (g := gif_frame(lt)) is not None else black_bg(lt, t), layers=[
        Layer(0.3, 9, img=sticker("*GULP*", "comic", 150), xy=(560, 360), tilt=-10),
        Layer(1.0, 9, img=sticker("FREE!", "starburst", 150), xy=(1500, 560), tilt=8),
    ], note="meme + stickers"),
    # 6: price + year + name plate over footage
    Shot(15.0, 17.6, bg=video_bg(FOOTAGE, 20.0) if FOOTAGE else black_bg, layers=[
        Layer(0.2, 9, img=sticker("2018", "year", 90), xy=(W / 2, 170)),
        Layer(0.8, 9, img=sticker("ALEXANDR WANG", "name_plate", 40), xy=(520, 880), anim="slide_left"),
        Layer(1.4, 9, img=sticker("$1,300", "price_box", 110), xy=(1480, 460), tilt=-4),
        Layer(1.9, 9, img=sticker("$449", "price_pop", 160), xy=(1480, 760), tilt=6),
    ], note="year + name plate + prices"),
    # 7: the built-up systems diagram
    Shot(17.6, 23.4, bg=lambda lt, t: draw_diagram([
        DiagramItem(0.0, "frame", (180, 110, 1420, 990)),
        DiagramItem(0.6, "dashed", (260, 200, 900, 690), "Agent sandbox"),
        DiagramItem(1.0, "label", (320, 310), "Browser"),
        DiagramItem(1.2, "label", (320, 390), "Storage"),
        DiagramItem(1.4, "label", (320, 490), "Hatch (Rust harness)"),
        DiagramItem(2.0, "block", (1030, 230, 1350, 360), "Passwords", GREEN),
        DiagramItem(2.8, "block", (1030, 800, 1350, 930), "Sentinel", CYAN),
        DiagramItem(3.1, "arrow", ((1190, 370), (1190, 790)), "real token"),
        DiagramItem(3.4, "arrow", ((600, 700), (1020, 860)), "fake token"),
        DiagramItem(4.0, "block", (1560, 820, 1780, 910), "Web", CREAM),
        DiagramItem(4.3, "arrow", ((1355, 865), (1550, 865))),
        DiagramItem(5.0, "red_arrow", ((520, 330), (520, 470))),
    ], lt, title="Linux virtual machine"), note="diagram build"),
    # 8: title card
    Shot(23.4, 25.4, bg=lambda lt, t: title_card("The Kev Report", "Sep 29th, 2026", lt), glitch_in=True, note="title card"),
]

# curved pointer arrow drawn on the tweet shot
SHOTS[3].layers.append(Layer(1.4, 9, draw=lambda c, lt: curved_arrow(c, (1500, 250), (1180, 360), lt / 0.35)))

if __name__ == "__main__":
    render(SHOTS, duration=25.4, out_dir=os.environ.get("OUT", "frames/out"))
