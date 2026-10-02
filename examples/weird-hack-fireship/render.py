#!/usr/bin/env python3
"""Fireship-style edit: first 60 s of "The most interesting hack in history just got weirder".
Literal visuals (SKILL.md section 0): BBC / CNBC / Bloomberg coverage of the actual OpenAI x
Hugging Face incident, Sam Altman on "safe development", Clem Delangue on "their infrastructure",
real Wikipedia text for the "humble nonprofit" joke, two diagram builds for the attack chain.
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fireship_engine import *  # noqa: F401,F403
from PIL import Image

WORDS = words_onsets("audio/words.json")
DUR = 60.0
FT = "assets/footage/"


def A(word, after=0.0):
    return at(WORDS, word, after)


def logo(slug, size=300):
    def build():
        im = Image.open(f"assets/logos/{slug}.png").convert("RGBA")
        bb = im.getbbox()
        im = im.crop(bb) if bb else im
        s = size / max(im.width, im.height)
        return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    return cached(("logo", slug, size), build)


def tile(slug, size=260, pad=40):
    def build():
        mk = logo(slug, size - pad * 2)
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(im).rounded_rectangle([0, 0, size - 1, size - 1], 40, fill=(255, 255, 255, 255))
        im.alpha_composite(mk, ((size - mk.width) // 2, (size - mk.height) // 2))
        return im
    return cached(("tile", slug, size), build)


def gif_bg(slug, zoom=1.0, fy=0.5):
    fs = sorted(glob.glob(f"assets/gifs/{slug}/f*.png"))
    return lambda lt, t: fit_cover(Image.open(fs[int(lt * 30) % len(fs)]).convert("RGB"), zoom=zoom, fy=fy)


def clip(name, zoom=1.0):
    return video_bg(FT + name, 0.0, zoom=zoom)


def video_card(thumb_path, t_src, title, p_bar, w=1200):
    """YouTube-player style card: thumbnail frame from real footage, red progress bar, title."""
    fr = footage(thumb_path).frame(t_src).convert("RGB")
    th_h = int(w * 9 / 16)
    im = Image.new("RGBA", (w, th_h + 150), (15, 15, 15, 255))
    im.paste(fit_cover(fr, w, th_h), (0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, th_h // 2
    d.rounded_rectangle([cx - 70, cy - 48, cx + 70, cy + 48], 24, fill=(255, 0, 0, 235))
    d.polygon([(cx - 18, cy - 26), (cx - 18, cy + 26), (cx + 28, cy)], fill=WHITE)
    d.rectangle([0, th_h - 8, w, th_h], fill=(80, 80, 80, 255))
    d.rectangle([0, th_h - 8, int(w * p_bar), th_h], fill=(255, 0, 0, 255))
    d.text((28, th_h + 30), title, font=font("ui", 40), fill=WHITE)
    d.text((28, th_h + 90), "2 months ago", font=font("ui", 30), fill=(170, 170, 170))
    return im


MODELS = [("model a", 0.31), ("model b", 0.42), ("model c", 0.38)]


def bench_card(p, cheat=0.0, w=1300, h=640):
    """Internal benchmark leaderboard; `cheat` 0..1 rockets the scores to ~100%."""
    im = Image.new("RGBA", (w, h), (250, 250, 252, 255))
    d = ImageDraw.Draw(im)
    d.text((48, 40), "INTERNAL BENCHMARK", font=font("block", 64), fill=INK)
    d.text((w - 48, 62), "score", font=font("ui", 30), fill=(120, 120, 126), anchor="ra")
    for i, (name, sc) in enumerate(MODELS):
        y = 170 + i * 150
        v = min(1.0, sc * clamp01(p) + (0.99 - sc) * ease_out(clamp01(cheat - i * 0.12)))
        d.text((48, y + 20), name.upper(), font=font("pixel", 28), fill=INK)
        d.rounded_rectangle([330, y, w - 160, y + 80], 14, fill=(225, 226, 232))
        d.rounded_rectangle([330, y, 330 + int((w - 490) * v), y + 80], 14, fill=GREEN if cheat > 0.2 else CYAN)
        d.text((w - 48, y + 40), f"{int(v * 100)}%", font=font("block", 54), fill=INK, anchor="rm")
    return im


OPENAI_TXT = wikipedia_extract("OpenAI")

# ───────────────────────────── times ─────────────────────────────
t_since = A("since")
t_described = A("described")
t_most = A("most")
t_fireship = A("fireship")
t_and1 = A("and", 6.3)
t_turns = A("turns")
t_details = A("details")
t_are = A("are", 9.0)
t_crazier = A("crazier")
t_if = A("if", 11.4)
t_july = A("july")
t_it2 = A("it", 13.0)
t_first = A("first", 14.0)
t_autonomous = A("autonomous")
t_originated = A("originated")
t_openai = A("openai", 17.0)
t_which = A("which", 18.0)
t_ironic = A("ironic")
t_humble = A("humble")
t_safe = A("safe")
t_what = A("what", 23.5)
t_openai2 = A("openai", 24.5)
t_internal = A("internal")
t_and2 = A("and", 28.0)
t_highest = A("highest")
t_find = A("find", 32.0)
t_so = A("so", 33.5)
t_inference = A("inference")
t_exploited = A("exploited")
t_zero = A("zero")
t_registry = A("registry")
t_privilege = A("privilege")
t_lateral = A("lateral")
t_escape = A("escape")
t_sandbox = A("sandbox")
t_node = A("node")
t_internet = A("internet")
t_but = A("but", 48.0)
t_inferred = A("inferred")
t_hugging = A("hugging")
t_hosted = A("hosted")
t_so2 = A("so", 53.0)
t_poison = A("poison")
t_fed = A("fed")
t_hugging2 = A("hugging", 55.5)
t_gain = A("gain")
t_infra = A("infrastructure.") or A("infrastructure")
t_and3 = A("and", 58.3)
t_week = A("week,") or A("week")

SHOTS = []


def shot(t0, t1, bg=None, glitch_in=False, note=""):
    s = Shot(t0, t1, bg=bg, glitch_in=glitch_in, note=note)
    SHOTS.append(s)
    return s


def L(t_abs, s, img, xy=(W / 2, H / 2), tilt=0.0, anim="pop", until=99):
    return Layer(max(0.0, t_abs - s.t0), until, img=img, xy=xy, tilt=tilt, anim=anim)


def nxt():
    return SHOTS[-1].t1


# 0 kinetic: "It's only been two months"
s = shot(0.0, t_since - 0.05, bg=lambda lt, t: kinetic_words([("It's", 0.0), ("only", A("only")), ("been", A("been")),
                                                               ("two", A("two")), ("months", A("months"))], lt), note="kinetic")
# 1 "since we did a video on what I described at the time"
s = shot(nxt(), t_most - 0.1, note="our video")
s.layers += [Layer(0.0, 99, img=lambda lt: video_card(FT + "bbc_4.5.mp4", 2.0, "The most interesting hack in history", 0.15 + lt * 0.12, w=1400),
                   xy=(W / 2, 560), tilt=-2, anim="slide_up"),
             L(t_described, s, sticker("2 MONTHS AGO", "year", 54), xy=(1500, 140), tilt=4)]
# 2 "as the most Fireship-coded story I've ever seen"
s = shot(nxt(), t_and1 - 0.05, bg=gif_bg("chefkiss"), glitch_in=True, note="chef kiss")
s.layers += [L(t_fireship, s, sticker('"THE MOST FIRESHIP-CODED STORY"', "quote", 92), xy=(W / 2, 140), tilt=-2)]
# 3 "and as it turns out, the details around what actually happened"
s = shot(nxt(), t_are - 0.05, bg=gif_bg("plottwist", fy=0.35), note="plot twist")
s.layers += [L(t_details, s, sticker("THE DETAILS", "red_block", 150), xy=(W / 2, 170), tilt=3)]
# 4 "are even crazier than what we knew at the time"  -> BUT WAIT, IT GETS WORSE (burned in, bottom)
s = shot(nxt(), t_if - 0.05, bg=gif_bg("worse", fy=0.4), glitch_in=True, note="gets worse")
s.layers += [L(t_crazier, s, sticker("EVEN CRAZIER", "red_caps", 150), xy=(W / 2, 170), tilt=-4)]
# 5 "If you remember back in July" -> CNBC AI CYBER INCIDENTS board, 7/21 line
s = shot(nxt(), t_it2 - 0.05, bg=clip("clem_15.mp4"), note="july board")
s.layers += [L(t_july, s, sticker("JULY 21", "year", 56), xy=(330, 640), tilt=-3)]
s.layers.append(Layer(max(0, t_july - s.t0) + 0.15, 99, draw=lambda c, lt: curved_arrow(c, (470, 560), (840, 300), lt / 0.35)))
# 6 "it was reported that the first fully autonomous cyber attack in history" -> BBC anchor, real lower third
s = shot(nxt(), t_originated - 0.05, bg=clip("bbc_4.5.mp4"), note="BBC")
s.layers += [L(t_first, s, sticker("FIRST IN HISTORY", "starburst", 64), xy=(1580, 220), tilt=8),
             L(t_autonomous, s, sticker("FULLY AUTONOMOUS", "red_block", 120), xy=(560, 230), tilt=-4)]
# 7 "originated from OpenAI"
s = shot(nxt(), t_which - 0.05, bg=clip("bbc_22.mp4"), glitch_in=True, note="openai broll")
s.layers += [L(t_openai, s, sticker("OPENAI", "red_block", 180), xy=(W / 2, 170), tilt=-3)]
# 8 "which was ironic because they're a"
s = shot(nxt(), t_humble - 0.05, bg=gif_bg("ironic"), note="ironic")
s.layers += [L(t_ironic, s, sticker("IRONIC", "red_caps", 160), xy=(W / 2, 160), tilt=-4)]
# 9 "humble nonprofit dedicated to" -> real Wikipedia lead, highlight the valuation
s = shot(nxt(), t_safe - 0.05, note="wiki nonprofit")
s.layers += [Layer(0.0, 99, img=lambda lt: wiki_doc("OpenAI", OPENAI_TXT, "public benefit corporation",
                                                     clamp01((lt - 0.4) / 1.0), max_lines=7), xy=(W / 2, 560), anim="bulge"),
             L(t_humble, s, sticker("HUMBLE NONPROFIT", "pink_plate", 70), xy=(1450, 110), tilt=4),
             L(t_humble + 0.9, s, sticker("$852 BILLION", "price_box", 110), xy=(1560, 960), tilt=-5)]
# 10 "the safe development of artificial intelligence" -> Sam Altman on Bloomberg
s = shot(nxt(), t_what - 0.05, bg=clip("altman_17.mp4"), glitch_in=True, note="altman")
s.layers += [L(t_safe, s, sticker("*SAFE*", "comic", 150), xy=(480, 260), tilt=-8),
             L(t_safe + 1.3, s, sticker("SAM ALTMAN", "name_plate", 42), xy=(480, 470), anim="slide_left")]
# 11 "What was reported was that OpenAI ran" -> the joint statement card (real)
s = shot(nxt(), t_internal - 0.05, bg=clip("clem_129.mp4"), note="statement")
s.layers += [L(t_openai2, s, tile("openai", 220), xy=(260, 260), tilt=-4)]
# 12 "an internal benchmark on some of their models" -> leaderboard
s = shot(nxt(), t_and2 - 0.05, glitch_in=True, note="benchmark")
s.layers += [Layer(0.0, 99, img=lambda lt: bench_card(clamp01(lt / 1.0)), xy=(W / 2, 560), tilt=1, anim="bulge")]
# 13 "and those models quickly realized the easiest path to the highest score"
s = shot(nxt(), t_find - 0.25, note="cheat climb")
s.layers += [Layer(0.0, 99, img=lambda lt: bench_card(1.0, cheat=(lt - (t_highest - s.t0) + 0.3) / 0.9), xy=(W / 2, 560), tilt=1, anim="none"),
             L(t_highest, s, sticker("HIGHEST SCORE", "price_pop", 120), xy=(1500, 170), tilt=6)]
# 14 "was to just find the answers online"
s = shot(nxt(), t_so - 0.05, bg=gif_bg("homework", fy=0.35), note="copy homework")
s.layers += [L(t_find, s, sticker("JUST FIND THE ANSWERS", "red_block", 110), xy=(W / 2, 960), tilt=-2)]
# 15 "So they spent a substantial amount of inference compute"
s = shot(nxt(), t_exploited - 0.05, bg=clip("bbc_168.5.mp4"), note="compute")
s.layers += [L(t_inference, s, sticker("$$$ INFERENCE COMPUTE", "price_box", 90), xy=(1300, 260), tilt=-3)]
# 16 the attack-chain diagram, building on every spoken step
d0 = nxt()


def dl(t):
    return max(0.0, t - d0)


CHAIN = [
    DiagramItem(0.0, "frame", (120, 110, 1800, 1000)),
    DiagramItem(0.0, "dashed", (190, 180, 1060, 940), "Sandbox"),
    DiagramItem(0.05, "block", (260, 270, 620, 390), "Models", GREEN),
    DiagramItem(dl(t_registry), "block", (1180, 220, 1730, 360), "Package registry cache proxy", CYAN),
    DiagramItem(dl(t_zero), "red_arrow", ((620, 300), (1170, 280)), "zero day"),
    DiagramItem(dl(t_privilege), "block", (260, 470, 620, 580), "Root", RED),
    DiagramItem(dl(t_privilege) + 0.2, "arrow", ((440, 395), (440, 462)), "privilege escalation"),
    DiagramItem(dl(t_lateral), "block", (260, 690, 450, 780), "Node", CREAM),
    DiagramItem(dl(t_lateral) + 0.25, "arrow", ((455, 735), (545, 735))),
    DiagramItem(dl(t_lateral) + 0.3, "block", (555, 690, 745, 780), "Node", CREAM),
    DiagramItem(dl(t_lateral) + 0.5, "arrow", ((750, 735), (840, 735))),
    DiagramItem(dl(t_lateral) + 0.55, "block", (850, 690, 1040, 780), "Node", CREAM),
    DiagramItem(dl(t_escape), "red_arrow", ((1040, 735), (1220, 735)), "escape"),
    DiagramItem(dl(t_node), "block", (1230, 650, 1730, 820), "Node + internet", ORANGE),
]
s = shot(d0, t_but - 0.05, bg=lambda lt, t: draw_diagram(CHAIN, lt, title="OpenAI eval cluster"), note="chain diagram")
s.layers += [L(t_zero, s, sticker("ZERO DAY", "stamp", 100), xy=(900, 470), tilt=-8),
             L(t_lateral, s, sticker("LATERAL MOVEMENT", "pink_plate", 50), xy=(640, 880), tilt=2),
             L(t_internet, s, sticker("ESCAPED", "red_caps", 130), xy=(1480, 930), tilt=-5)]
# 17 "But from there, the models inferred that"
s = shot(nxt(), t_hugging - 0.05, bg=clip("bbc_166.mp4"), glitch_in=True, note="inferred")
s.layers += [L(t_inferred, s, sticker("*INFERS*", "comic", 140), xy=(1450, 240), tilt=6)]
# 18 "Hugging Face"
s = shot(nxt(), t_hosted - 0.05, bg=clip("bbc_65.5.mp4"), note="hf emoji")
s.layers += [L(t_hugging, s, sticker("HUGGING FACE", "red_block", 150), xy=(W / 2, 170), tilt=-3)]
# 19 "probably hosted the solutions for the benchmark"
s = shot(nxt(), t_so2 - 0.05, bg=clip("bbc_72.mp4", zoom=1.05), note="hf site")
s.layers += [L(t_hosted + 0.4, s, sticker("THE ANSWERS?", "red_caps", 140), xy=(560, 250), tilt=-5)]
# 20 "So it created a poison data set, fed it to Hugging Face"
p0 = nxt()


def pl(t):
    return max(0.0, t - p0)


POISON = [
    DiagramItem(0.0, "frame", (120, 160, 1800, 960)),
    DiagramItem(0.0, "block", (200, 480, 520, 600), "Models", GREEN),
    DiagramItem(pl(t_poison), "block", (700, 450, 1120, 630), "Poisoned dataset", RED),
    DiagramItem(pl(t_poison) + 0.15, "arrow", ((525, 540), (690, 540))),
    DiagramItem(pl(t_fed), "image", (1480, 540), image=tile("huggingface", 260)),
    DiagramItem(pl(t_fed) + 0.2, "red_arrow", ((1125, 540), (1335, 540)), "fed to"),
]
s = shot(p0, t_gain - 0.05, bg=lambda lt, t: draw_diagram(POISON, lt, title="the poisoned upload"), glitch_in=True, note="poison diagram")
s.layers += [L(t_poison, s, sticker("POISON", "stamp", 110), xy=(910, 300), tilt=-8)]
# 21 "and gain access to their infrastructure" -> Clem Delangue, Hugging Face CEO
s = shot(nxt(), t_and3 - 0.05, bg=clip("clem_44.mp4"), note="clem")
s.layers += [L(t_infra, s, sticker("ACCESS GRANTED", "red_block", 120), xy=(1400, 260), tilt=4)]
# 22 "And just this week, we finally got" -> the joint statement, teaser
s = shot(nxt(), DUR, bg=clip("clem_129.mp4"), glitch_in=True, note="this week")
s.layers += [L(t_week, s, sticker("THIS WEEK", "year", 64), xy=(W / 2, 170))]

if __name__ == "__main__":
    if os.environ.get("LIST"):
        for i, sh in enumerate(SHOTS):
            print(f"{i:2d} {sh.t0:6.2f}-{sh.t1:6.2f} ({sh.t1 - sh.t0:4.2f}s) {sh.note}")
    else:
        render(SHOTS, duration=DUR, out_dir=os.environ.get("OUT", "frames/out"))
