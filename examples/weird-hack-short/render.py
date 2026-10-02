#!/usr/bin/env python3
"""Vertical Fireship-style short (fireship-style-short skill): first 60 s of "The most interesting
hack in history just got weirder", same real coverage as the long-form cut (BBC / CNBC / Bloomberg),
re-laid-out for 9:16: footage as bands over a blurred fill, stickers above/below the band, tall
diagrams, word-chunk captions on the 1340 line.
"""
import glob
import os

from short_kit import *  # noqa: F401,F403

WORDS = words_onsets("audio/words.json")
DUR = 60.0
FT = "assets/footage/"
KEYWORDS = ["openai", "hugging", "face", "benchmark", "zero", "day", "sandbox", "poison", "infrastructure",
            "autonomous", "ironic", "nonprofit", "safe", "crazier", "fireship", "internet", "answers"]
ABOVE, BELOW = STICKER_ABOVE, STICKER_BELOW


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


def tile(slug, size=240, pad=36):
    def build():
        mk = logo(slug, size - pad * 2)
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(im).rounded_rectangle([0, 0, size - 1, size - 1], 36, fill=(255, 255, 255, 255))
        im.alpha_composite(mk, ((size - mk.width) // 2, (size - mk.height) // 2))
        return im
    return cached(("tile", slug, size), build)


def video_card(thumb_path, t_src, title, p_bar, w=960):
    fr = footage(thumb_path).frame(t_src).convert("RGB")
    th_h = int(w * 9 / 16)
    im = Image.new("RGBA", (w, th_h + 150), (15, 15, 15, 255))
    im.paste(fit_cover(fr, w, th_h), (0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, th_h // 2
    d.rounded_rectangle([cx - 66, cy - 46, cx + 66, cy + 46], 24, fill=(255, 0, 0, 235))
    d.polygon([(cx - 16, cy - 24), (cx - 16, cy + 24), (cx + 26, cy)], fill=WHITE)
    d.rectangle([0, th_h - 8, w, th_h], fill=(80, 80, 80, 255))
    d.rectangle([0, th_h - 8, int(w * p_bar), th_h], fill=(255, 0, 0, 255))
    d.text((26, th_h + 28), title, font=font("ui", 38), fill=WHITE)
    d.text((26, th_h + 86), "2 months ago", font=font("ui", 28), fill=(170, 170, 170))
    return im


MODELS = [("model a", 0.31), ("model b", 0.42), ("model c", 0.38)]


def bench_card(p, cheat=0.0, w=960, h=560):
    im = Image.new("RGBA", (w, h), (250, 250, 252, 255))
    d = ImageDraw.Draw(im)
    d.text((40, 34), "INTERNAL BENCHMARK", font=font("block", 58), fill=INK)
    for i, (name, sc) in enumerate(MODELS):
        y = 150 + i * 130
        v = min(1.0, sc * clamp01(p) + (0.99 - sc) * ease_out(clamp01(cheat - i * 0.12)))
        d.text((40, y + 22), name.upper(), font=font("pixel", 24), fill=INK)
        d.rounded_rectangle([270, y, w - 150, y + 74], 14, fill=(225, 226, 232))
        d.rounded_rectangle([270, y, 270 + int((w - 420) * v), y + 74], 14, fill=GREEN if cheat > 0.2 else CYAN)
        d.text((w - 36, y + 37), f"{int(v * 100)}%", font=font("block", 50), fill=INK, anchor="rm")
    return im


OPENAI_TXT = wikipedia_extract("OpenAI")

SHOTS = []


def shot(t0, t1, bg=None, glitch_in=False, note=""):
    s = Shot(t0, t1, bg=bg, glitch_in=glitch_in, note=note)
    SHOTS.append(s)
    return s


def L(t_abs, s, img, xy=(CX, ABOVE), tilt=0.0, anim="pop", until=99):
    return Layer(max(0.0, t_abs - s.t0), until, img=img, xy=xy, tilt=tilt, anim=anim)


def nxt():
    return SHOTS[-1].t1


def band(name, **kw):
    return footage_band(FT + name, **kw)


# 0 hook: frame 0 is the BBC anchor under the real headline, not black
s = shot(0.0, A("since") - 0.05, bg=band("bbc_4.5.mp4"), note="hook")
s.layers += [L(0.0, s, sticker("2 MONTHS LATER...", "stamp", 96), tilt=-6)]
# 1 "since we did a video on what I described at the time"
s = shot(nxt(), A("most") - 0.1, note="our video")
s.layers += [Layer(0.0, 99, img=lambda lt: video_card(FT + "bbc_4.5.mp4", 2.0, "The most interesting hack in history", 0.15 + lt * 0.12),
                   xy=(CX, 760), tilt=-2, anim="slide_up"),
             L(A("described"), s, sticker("2 MONTHS AGO", "year", 52), xy=(CX, ABOVE))]
# 2 "the most Fireship-coded story I've ever seen"
s = shot(nxt(), A("and", 6.3) - 0.05, bg=gif_band("chefkiss"), glitch_in=True, note="chef kiss")
s.layers += [L(A("fireship"), s, sticker('"MOST FIRESHIP-CODED STORY"', "quote", 72), tilt=-2)]
# 3 "and as it turns out, the details around what actually happened"
s = shot(nxt(), A("are", 9.0) - 0.05, bg=gif_band("plottwist"), note="plot twist")
s.layers += [L(A("details"), s, sticker("THE DETAILS", "red_block", 130), tilt=3)]
# 4 "are even crazier than what we knew"
s = shot(nxt(), A("if", 11.4) - 0.05, bg=gif_band("worse"), glitch_in=True, note="gets worse")
s.layers += [L(A("crazier"), s, sticker("EVEN CRAZIER", "red_caps", 130), tilt=-4)]
# 5 "If you remember back in July" -> CNBC incidents board
s = shot(nxt(), A("it", 13.0) - 0.05, bg=band("clem_15.mp4", zoom=1.12, fx=0.75), note="july board")
s.layers += [L(A("july"), s, sticker("JULY 21", "year", 64), xy=(CX, BELOW))]
# 6 "the first fully autonomous cyber attack in history"
s = shot(nxt(), A("originated") - 0.05, bg=band("bbc_4.5.mp4", zoom=1.05), note="BBC")
s.layers += [L(A("first", 14.0), s, sticker("FIRST IN HISTORY", "starburst", 56), tilt=6),
             L(A("autonomous"), s, sticker("FULLY AUTONOMOUS", "red_block", 100), xy=(CX, BELOW), tilt=-3)]
# 7 "originated from OpenAI"
s = shot(nxt(), A("which", 18.0) - 0.05, bg=band("bbc_22.mp4"), glitch_in=True, note="openai")
s.layers += [L(A("openai", 17.0), s, sticker("OPENAI", "red_block", 160), tilt=-3)]
# 8 "which was ironic because they're a"
s = shot(nxt(), A("humble") - 0.05, bg=gif_band("ironic"), note="ironic")
s.layers += [L(A("ironic"), s, sticker("IRONIC", "red_caps", 150), tilt=-4)]
# 9 "humble nonprofit dedicated to" -> real Wikipedia lead
s = shot(nxt(), A("safe") - 0.05, note="wiki")
s.layers += [Layer(0.0, 99, img=card(lambda lt: wiki_doc("OpenAI", OPENAI_TXT, "public benefit corporation",
                                                          clamp01((lt - 0.3) / 0.9), width=1100, size=40, max_lines=7), 980),
                   xy=(CX, 780), anim="bulge"),
             L(A("humble"), s, sticker("HUMBLE NONPROFIT", "pink_plate", 64), tilt=3),
             L(A("humble") + 0.9, s, sticker("$852 BILLION", "price_box", 100), xy=(CX, BELOW), tilt=-4)]
# 10 "the safe development of artificial intelligence" -> Sam Altman on Bloomberg
s = shot(nxt(), A("what", 23.5) - 0.05, bg=band("altman_17.mp4", zoom=1.1), glitch_in=True, note="altman")
s.layers += [L(A("safe"), s, sticker("*SAFE*", "comic", 140), tilt=-8),
             L(A("safe") + 1.2, s, sticker("SAM ALTMAN", "name_plate", 40), xy=(CX, BELOW), anim="slide_left")]
# 11 "What was reported was that OpenAI ran" -> joint statement
s = shot(nxt(), A("internal") - 0.05, bg=band("clem_129.mp4", zoom=1.1), note="statement")
s.layers += [L(A("openai", 24.5), s, tile("openai", 220), tilt=-4)]
# 12 "an internal benchmark on some of their models"
s = shot(nxt(), A("and", 28.0) - 0.05, glitch_in=True, note="bench")
s.layers += [Layer(0.0, 99, img=lambda lt: bench_card(clamp01(lt / 1.0)), xy=(CX, 780), tilt=1, anim="bulge")]
# 13 "those models quickly realized the easiest path to the highest score"
t_high = A("highest")
s = shot(nxt(), A("find", 32.0) - 0.25, note="cheat")
s.layers += [Layer(0.0, 99, img=lambda lt: bench_card(1.0, cheat=(lt - (t_high - SHOTS[13].t0) + 0.3) / 0.9), xy=(CX, 780),
                   tilt=1, anim="none"),
             L(t_high, s, sticker("HIGHEST SCORE", "price_pop", 110), tilt=5)]
# 14 "was to just find the answers online"
s = shot(nxt(), A("so", 33.5) - 0.05, bg=gif_band("homework"), note="homework")
s.layers += [L(A("find", 32.0), s, sticker("JUST FIND THE ANSWERS", "red_block", 84), xy=(CX, BELOW), tilt=-2)]
# 15 "So they spent a substantial amount of inference compute"
s = shot(nxt(), A("exploited") - 0.05, bg=band("bbc_168.5.mp4"), note="compute")
s.layers += [L(A("inference"), s, sticker("$$$ INFERENCE", "price_box", 96), tilt=-3)]

# 16/17/18 the attack chain: tall diagram, split by a keyboard cut so no shot runs > 8 s
d0 = nxt()
CHAIN = [
    DiagramItem(0.0, "frame", (40, 240, 1040, 1300)),
    DiagramItem(0.0, "dashed", (70, 300, 560, 1000), "Sandbox"),
    DiagramItem(0.05, "block", (120, 400, 510, 510), "Models", GREEN),
    DiagramItem(A("registry") - d0, "block", (610, 360, 1010, 540), "Package registry cache proxy", CYAN),
    DiagramItem(A("zero") - d0, "red_arrow", ((515, 455), (600, 455))),
    DiagramItem(A("privilege") - d0, "block", (120, 620, 510, 720), "Root", RED),
    DiagramItem(A("privilege") - d0 + 0.2, "arrow", ((315, 515), (315, 612))),
    DiagramItem(A("lateral") - d0, "block", (95, 820, 230, 900), "Node", CREAM),
    DiagramItem(A("lateral") - d0 + 0.25, "block", (250, 820, 385, 900), "Node", CREAM),
    DiagramItem(A("lateral") - d0 + 0.5, "block", (405, 820, 540, 900), "Node", CREAM),
    DiagramItem(A("escape") - d0, "red_arrow", ((545, 870), (650, 1080)), "escape"),
    DiagramItem(A("node") - d0, "block", (610, 1090, 1010, 1240), "Node + internet", ORANGE),
]
s = shot(d0, A("lateral") - 0.05, bg=lambda lt, t: draw_diagram(CHAIN, t - d0, title="OpenAI eval cluster"), note="chain A")
s.layers += [L(A("zero"), s, sticker("ZERO DAY", "stamp", 90), xy=(800, 700), tilt=-8)]
s = shot(nxt(), A("escape") - 0.05, bg=band("bbc_43.5.mp4"), glitch_in=True, note="keyboard")
s.layers += [L(A("lateral"), s, sticker("LATERAL MOVEMENT", "pink_plate", 60), tilt=2)]
s = shot(nxt(), A("but", 48.0) - 0.05, bg=lambda lt, t: draw_diagram(CHAIN, t - d0 + 0.6, title="OpenAI eval cluster"), note="chain B")
s.layers += [L(A("internet"), s, sticker("ESCAPED", "red_caps", 120), xy=(800, 760), tilt=-5)]
# 19 "But from there, the models inferred that"
s = shot(nxt(), A("hugging") - 0.05, bg=band("bbc_166.mp4", zoom=1.1), glitch_in=True, note="infers")
s.layers += [L(A("inferred"), s, sticker("*INFERS*", "comic", 130), tilt=6)]
# 20 "Hugging Face"
s = shot(nxt(), A("hosted") - 0.05, bg=band("bbc_65.5.mp4", zoom=1.1), note="hf")
s.layers += [L(A("hugging"), s, sticker("HUGGING FACE", "red_block", 130), tilt=-3)]
# 21 "probably hosted the solutions for the benchmark"
s = shot(nxt(), A("so", 53.0) - 0.05, bg=band("bbc_72.mp4", zoom=1.1), note="hf site")
s.layers += [L(A("hosted") + 0.4, s, sticker("THE ANSWERS?", "red_caps", 130), tilt=-5)]
# 22 "So it created a poison data set, fed it to Hugging Face" (tall diagram)
p0 = nxt()
POISON = [
    DiagramItem(0.0, "frame", (60, 260, 1020, 1300)),
    DiagramItem(0.0, "block", (300, 360, 780, 480), "Models", GREEN),
    DiagramItem(A("poison") - p0, "block", (240, 620, 840, 790), "Poisoned dataset", RED),
    DiagramItem(A("poison") - p0 + 0.15, "arrow", ((540, 485), (540, 612))),
    DiagramItem(A("fed") - p0, "image", (540, 1060), image=tile("huggingface", 240)),
    DiagramItem(A("fed") - p0 + 0.2, "red_arrow", ((540, 795), (540, 930)), "fed to"),
]
s = shot(p0, A("gain") - 0.05, bg=lambda lt, t: draw_diagram(POISON, lt, title="the poisoned upload"), glitch_in=True, note="poison")
s.layers += [L(A("poison"), s, sticker("POISON", "stamp", 100), xy=(860, 552), tilt=-8)]
# 23 "and gain access to their infrastructure" -> Clem Delangue
s = shot(nxt(), A("and", 58.3) - 0.05, bg=band("clem_44.mp4", zoom=1.1), note="clem")
s.layers += [L(A("infrastructure.") or A("infrastructure"), s, sticker("ACCESS GRANTED", "red_block", 110), tilt=4)]
# 24 "And just this week, we finally got"
s = shot(nxt(), DUR, bg=band("clem_129.mp4", src_start=0.8, zoom=1.1), glitch_in=True, note="this week")
s.layers += [L(A("week,") or A("week"), s, sticker("THIS WEEK...", "year", 62))]

if __name__ == "__main__":
    if os.environ.get("LIST"):
        for i, sh in enumerate(SHOTS):
            print(f"{i:2d} {sh.t0:6.2f}-{sh.t1:6.2f} ({sh.t1 - sh.t0:4.2f}s) {sh.note}")
    else:
        render(SHOTS, duration=DUR, out_dir=os.environ.get("OUT", "frames/out"), post=make_captions(WORDS, KEYWORDS))
