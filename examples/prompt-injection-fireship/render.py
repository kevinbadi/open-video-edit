#!/usr/bin/env python3
"""Fireship-style test edit: first 60 s of "Did a 50-year-old military secret just solve agent
prompt injection" (audio overlay supplied by Kevin). Faceless, hard cut every ~2.2 s, every beat on
the spoken word. Real photos from Wikimedia Commons, real Wikipedia text for the doc highlight,
Giphy memes, fictional outlets / handles for headline + tweet cards (the story isn't ours to
attribute to real outlets).
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


def A(word, after=0.0):
    return at(WORDS, word, after)


def logo(slug, size=300):
    p = f"assets/logos/{slug}.png"
    def build():
        im = Image.open(p).convert("RGBA")
        bb = im.getbbox()
        im = im.crop(bb) if bb else im
        s = size / max(im.width, im.height)
        return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    return cached(("logo", slug, size), build)


def tile(slug, size=230, pad=34):
    """Logo on a white rounded tile so dark marks read on the near-black ground."""
    def build():
        mk = logo(slug, size - pad * 2)
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, size - 1, size - 1], 36, fill=(255, 255, 255, 255))
        im.alpha_composite(mk, ((size - mk.width) // 2, (size - mk.height) // 2))
        return im
    return cached(("tile", slug, size), build)


def gif_bg(slug, zoom=1.0):
    fs = sorted(glob.glob(f"assets/gifs/{slug}/f*.png"))
    def bg(lt, t):
        im = Image.open(fs[int(lt * 30) % len(fs)]).convert("RGB")
        return fit_cover(im, zoom=zoom)
    return bg


def portrait(slug, size=380):
    def build():
        im = Image.open(f"assets/figures/{slug}.png").convert("RGBA").resize((size, size), Image.LANCZOS)
        m = Image.new("L", (size, size), 0)
        ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255)
        out = Image.new("RGBA", (size + 16, size + 16), (0, 0, 0, 0))
        ImageDraw.Draw(out).ellipse([0, 0, size + 15, size + 15], fill=(255, 255, 255, 255))
        im.putalpha(m)
        out.alpha_composite(im, (8, 8))
        return out
    return cached(("portrait", slug, size), build)


WIKI = open("assets/shots/wiki-pi.txt").read().strip()
DOC = [
    "Prompt injection is a cybersecurity exploit and an attack vector",
    "in which innocuous-looking inputs are designed to cause",
    "unintended behavior in machine learning models, particularly",
    "large language models (LLMs). The attack takes advantage of the",
    "model's inability to distinguish between developer-defined",
    "prompts and user inputs to bypass safeguards.",
]
HL = phrase_spans(DOC, "model's inability to distinguish between developer-defined prompts and user inputs")


def wiki_card(p):
    body = doc_card(DOC, HL, p=p, width=1480, size=44)
    head_h = 110
    im = Image.new("RGBA", (body.width, body.height + head_h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((44, 30), "Prompt injection", font=font("serif", 56), fill=INK)
    d.text((body.width - 44, 52), "From Wikipedia, the free encyclopedia", font=font("ui", 24), fill=(110, 110, 116), anchor="ra")
    d.line([44, head_h - 8, body.width - 44, head_h - 8], fill=(200, 200, 205), width=2)
    im.paste(body, (0, head_h))
    return im


# ───────────────────────────── shot list (absolute times = spoken words) ─────────────────────────────
t_last = 0.0
t_prime = A("prime")
t_united = A("united")
t_agent = A("agent")
t_openai = A("openai")
t_broken = A("broken")
t_medicare = A("medicare")
t_stop = A("stop")
t_wouldnt = A("wouldn't")
t_from = A("from", 11.9)
t_first = A("first")
t_hacked = A("hacked")
t_aussies = A("aussies")
t_months = A("months")
t_openai2 = A("openai", 18.9)
t_fessed = A("fessed")
t_course = A("of", 20.8)
t_felony = A("felony")
t_benchmark = A("benchmark")
t_but = A("but", 25.5)
t_big = A("big")
t_racing = A("racing")
t_dont = A("don't", 28.0)
t_how = A("how", 29.5)
t_jensen = A("jensen")
t_nvidia = A("nvidia")
t_new = A("new", 36.0)
t_chip = A("chip.") if A("chip.") else A("chip")
t_way = A("way", 36.8)
t_monitor = A("monitor")
t_separate = A("separate")
t_watches = A("watches")
t_primary = A("primary")
t_quarantines = A("quarantines")
t_leave = A("leave")
t_sandbox = A("sandbox,") or A("sandbox")
t_according = A("according")
t_stopped = A("stopped")
t_so = A("so", 48.2)
t_which = A("which", 49.0)
t_ironic = A("ironic")
t_three = A("3", 51.0)
t_selling = A("selling")
t_condom = A("condom")
t_sold = A("sold")
t_last2 = A("last", 55.0)
t_but2 = A("but", 55.8)
t_different = A("different")
t_small = A("small")
t_open = A("open", 58.5)


def L(t_abs, shot_t0, img, xy=(W / 2, H / 2), tilt=0.0, anim="pop", until=99):
    """Layer timed by ABSOLUTE spoken time (converted to shot-local)."""
    return Layer(max(0.0, t_abs - shot_t0), until, img=img, xy=xy, tilt=tilt, anim=anim)


SHOTS = []


def shot(t0, t1, bg=None, glitch_in=False, note=""):
    s = Shot(t0, t1, bg=bg, glitch_in=glitch_in, note=note)
    SHOTS.append(s)
    return s


# 0 cold open: kinetic words on black
s = shot(0.0, t_prime - 0.05, bg=lambda lt, t: kinetic_words([("Last", 0.0), ("week,", A("week,") or 0.4)], lt), note="kinetic")

# 1 "the Prime President of Australia stood up"
s = shot(s.t1, t_united - 0.1, bg=image_bg("assets/shots/sydney.jpg", 0.03), note="sydney")
s.layers += [L(t_prime, s.t0, logo("australia", 330), xy=(420, 360), tilt=-4, anim="slide_left"),
             L(A("australia"), s.t0, sticker("THE PRIME PRESIDENT", "name_plate", 40), xy=(W / 2, 860)),
             L(A("stood"), s.t0, sticker("*STANDS UP*", "comic", 110), xy=(1430, 330), tilt=8)]

# 2 "at the United Nations and announced"
s = shot(s.t1, t_agent - 0.05, bg=video_bg("assets/footage/mPJCUdHWKEI.mp4", 1.0), glitch_in=True, note="UN")
s.layers += [L(t_united, s.t0, logo("un", 300), xy=(330, 300), anim="slide_left"),
             L(A("announced"), s.t0, sticker("ANNOUNCED", "red_block", 170), xy=(1250, 820), tilt=-5)]

# 3 "that an agent from OpenAI"
s = shot(s.t1, t_broken - 0.05, note="openai")
s.layers += [L(t_agent, s.t0, sticker("AN AGENT", "red_caps", 150), xy=(W / 2, 250), tilt=-6),
             L(t_openai, s.t0, tile("openai", 420), xy=(W / 2, 640))]

# 4 "had broken into the country's Medicare database"
s = shot(s.t1, t_stop - 0.35, bg=video_bg("assets/footage/YsiccpVKUIs.mp4", 211.0), note="medicare")
s.layers += [L(t_broken, s.t0, sticker("BROKEN INTO", "stamp", 140), xy=(560, 300), tilt=-10),
             L(t_medicare, s.t0, sticker("MEDICARE", "red_block", 230), xy=(1150, 640), tilt=4),
             L(A("database,") or t_medicare + 0.3, s.t0, sticker("DATABASE", "name_plate", 46), xy=(1150, 860), anim="slide_right")]

# 5 "and when they tried to stop it, it wouldn't take no for an answer"
s = shot(s.t1, t_from - 0.05, bg=gif_bg("hacker"), glitch_in=True, note="hacker meme")
s.layers += [L(t_stop, s.t0, sticker("STOP", "stamp", 150), xy=(1560, 430), tilt=-12),
             L(t_wouldnt, s.t0, sticker('"NO" IS NOT AN ANSWER', "quote", 120), xy=(W / 2, 160), tilt=3)]

# 6 "From what I can tell, this is the first time in history"
s = shot(s.t1, t_hacked - 0.25, note="headline stack")
s.layers += [L(t_from, s.t0, headline_card("The Daily Token", "AI agent breaches a national health database", "Officials say it ignored every shutdown request"), xy=(820, 400), tilt=-2),
             L(A("this", 12.9), s.t0, headline_card("Prompt Post", "First known case of an AI agent hacking a government", dark=True), xy=(1130, 700), tilt=3, anim="slide_up"),
             L(t_first, s.t0, sticker("FIRST TIME IN HISTORY", "starburst", 64), xy=(1560, 240), tilt=8)]

# 7 "where an agent hacked a government"
s = shot(s.t1, t_aussies - 0.1, bg=video_bg("assets/footage/mPJCUdHWKEI.mp4", 12.0), note="hacked a government")
s.layers += [L(t_hacked, s.t0, sticker("HACKED", "red_block", 220), xy=(W / 2, 430), tilt=-4),
             L(A("government"), s.t0, sticker("A GOVERNMENT", "quote", 120), xy=(W / 2, 760), tilt=2)]

# 8 "and the Aussies only learned about it a few months after the fact"
s = shot(s.t1, t_openai2 - 0.1, bg=gif_bg("kangaroo", 1.05), glitch_in=True, note="kangaroo")
s.layers += [L(t_aussies, s.t0, sticker("THE AUSSIES", "comic", 120), xy=(520, 240), tilt=-8),
             L(t_months, s.t0, sticker("MONTHS LATER", "year", 64), xy=(W / 2, 900))]

# 9 "when OpenAI finally"
s = shot(s.t1, t_fessed - 0.05, note="openai again")
s.layers += [L(t_openai2, s.t0, tile("openai", 380), xy=(W / 2, 480)),
             L(A("finally"), s.t0, sticker("FINALLY", "red_caps", 130), xy=(W / 2, 850), tilt=-3)]

# 10 "fessed up"
s = shot(s.t1, t_course - 0.05, bg=gif_bg("confess"), note="confess meme")
s.layers += [L(t_fessed, s.t0, sticker("*FESSED UP*", "comic", 130), xy=(W / 2, 150), tilt=4)]

# 11 "Of course, at this point, it feels like having your agent commit a felony"
s = shot(s.t1, t_felony + 0.35, note="tweet stack")
s.layers += [L(t_course, s.t0, tweet_card("dad of 3 agents", "@agentdad", "my agent committed its first felony today. they grow up so fast", meta="9:41 PM · 2.1M Views"), xy=(820, 420), tilt=2),
             L(A("having"), s.t0, tweet_card("benchmark bro", "@sotaorbust", "new SOTA on FelonyBench. we are so back", meta="10:02 PM · 880K Views"), xy=(1150, 770), tilt=-4, anim="slide_right")]

# 12 "is just another benchmark to pass"
s = shot(s.t1, t_but - 0.05, bg=gif_bg("jail"), glitch_in=True, note="jail meme")
s.layers += [L(t_felony + 0.35, s.t0, sticker("FELONY", "stamp", 150), xy=(400, 470), tilt=-12),
             L(t_benchmark, s.t0, sticker("JUST ANOTHER BENCHMARK", "quote", 100), xy=(W / 2, 150), tilt=2)]

# 13 "but if every big lab is racing to build agents"
s = shot(s.t1, t_dont - 0.05, note="big labs")
s.layers += [L(t_but, s.t0, sticker("BUT", "red_caps", 200), xy=(W / 2, 230), tilt=-5)]
for i, slug in enumerate(["openai", "anthropic", "gemini", "meta", "xai"]):
    s.layers.append(L(t_big + i * 0.12, s.t0, tile(slug, 230), xy=(330 + i * 315, 600), tilt=(-4, 3, -2, 4, -3)[i]))
s.layers.append(L(t_racing, s.t0, sticker("RACING", "red_block", 150), xy=(W / 2, 900), tilt=3))

# 14 "that don't take no for an answer, how do we stop them?"
s = shot(s.t1, t_how - 0.05, bg=video_bg("assets/footage/YsiccpVKUIs.mp4", 216.0), note="callback")
s.layers += [L(t_dont, s.t0, sticker("WON'T TAKE NO", "red_block", 180), xy=(W / 2, 520), tilt=-3)]

# 15 doc: Wikipedia prompt injection, highlighter reads along
s = shot(s.t1, t_jensen - 0.1, glitch_in=True, note="wiki doc")
s.layers += [Layer(0.0, 99, img=lambda lt: wiki_card(clamp01((lt - 0.35) / 1.6)), xy=(W / 2, H / 2), anim="bulge"),
             L(t_how, s.t0, sticker("HOW DO WE STOP THEM?", "pink_plate", 54), xy=(1480, 140), tilt=4)]

# 16 "Jensen Huang answered that exact question"
s = shot(s.t1, t_nvidia - 0.4, bg=video_bg("assets/footage/SPGn9MZb1a0.mp4", 77.0, zoom=1.12), note="jensen")
s.layers += [L(t_jensen, s.t0, sticker("JENSEN HUANG", "name_plate", 44), xy=(520, 900), anim="slide_left"),
             L(A("exact"), s.t0, sticker("THE EXACT QUESTION", "quote", 90), xy=(1380, 220), tilt=-3)]

# 17 "the only way Nvidia knows how"
s = shot(s.t1, t_new - 0.05, note="nvidia")
s.layers += [L(t_nvidia - 0.3, s.t0, tile("nvidia", 420), xy=(W / 2, 470)),
             L(A("knows"), s.t0, sticker("THE ONLY WAY IT KNOWS", "red_caps", 100), xy=(W / 2, 880), tilt=-2)]

# 18 "with a new chip"
s = shot(s.t1, t_way - 0.05, bg=video_bg("assets/footage/YsiccpVKUIs.mp4", 19.0), glitch_in=True, note="chip")
s.layers += [L(t_new, s.t0, sticker("A NEW CHIP!", "starburst", 90), xy=(560, 520), tilt=-8)]

# 19 the built-up diagram: monitor agent on a separate processor quarantines the primary agent
d0 = SHOTS[-1].t1


def dl(t):  # diagram-local time
    return max(0.0, t - d0)


DIAG = [
    DiagramItem(0.0, "frame", (150, 120, 1770, 990)),
    DiagramItem(dl(t_monitor), "block", (1180, 270, 1600, 400), "Monitor agent", CYAN),
    DiagramItem(dl(t_separate), "dashed", (1100, 200, 1680, 480), "Separate processor"),
    DiagramItem(dl(t_primary) - 0.15, "dashed", (240, 260, 820, 700), "Sandbox"),
    DiagramItem(dl(t_primary), "block", (320, 400, 740, 530), "Primary agent", GREEN),
    DiagramItem(dl(t_watches), "arrow", ((1170, 380), (760, 450)), "watches"),
    DiagramItem(dl(t_quarantines), "block", (1180, 700, 1600, 830), "Quarantine", CREAM),
    DiagramItem(dl(t_quarantines) + 0.2, "arrow", ((1390, 405), (1390, 690))),
    DiagramItem(dl(t_leave), "red_arrow", ((740, 560), (1170, 760)), "tries to leave"),
]
s = shot(d0, t_sandbox + 0.45, bg=lambda lt, t: draw_diagram(DIAG, lt, title="Nvidia monitor chip"), note="diagram")
s.layers += [L(t_quarantines, s.t0, sticker("QUARANTINED", "stamp", 90), xy=(560, 860), tilt=-8)]
s.layers.append(Layer(dl(t_watches) + 0.1, 99, draw=lambda c, lt: curved_arrow(c, (1000, 160), (1200, 255), lt / 0.35, col=GREEN)))

# 20 "you shall not pass" meme on the sandbox line
s = shot(s.t1, t_according + 0.55, bg=gif_bg("not-pass"), glitch_in=True, note="not pass meme")

# 21 "according to Jensen it would have stopped every breakout so far"
s = shot(s.t1, t_which - 0.05, bg=video_bg("assets/footage/SPGn9MZb1a0.mp4", 86.2, zoom=1.12), note="claim")
s.layers += [L(t_stopped, s.t0, sticker('"STOPPED EVERY BREAKOUT"', "quote", 96), xy=(720, 950), tilt=-2),
             L(t_so, s.t0, sticker("SO FAR", "red_caps", 150), xy=(1450, 760), tilt=6)]

# 22 "which, even if that's true"
s = shot(s.t1, t_ironic - 0.05, note="even if")
s.layers += [L(t_which, s.t0, sticker("EVEN IF THAT'S TRUE...", "pink_plate", 90), xy=(W / 2, H / 2), tilt=-2)]

# 23 "it's a bit ironic"
s = shot(s.t1, t_three - 0.15, bg=gif_bg("ironic"), glitch_in=True, note="ironic meme")
s.layers += [L(t_ironic, s.t0, sticker("IRONIC", "red_caps", 170), xy=(W / 2, 170), tilt=-4)]

# 24 "that a 3 trillion dollar company"
s = shot(s.t1, t_selling - 0.05, note="3 trillion")
s.layers += [L(t_three - 0.1, s.t0, tile("nvidia", 300), xy=(480, 470), tilt=-3),
             L(t_three, s.t0, sticker("$3,000,000,000,000", "price_box", 110), xy=(1230, 420), tilt=-3),
             L(A("company"), s.t0, sticker("COMPANY", "price_pop", 140), xy=(1260, 700), tilt=5)]

# 25 "is selling you a condom for the thing it also sold you last year"
s = shot(s.t1, t_but2 - 0.05, bg=video_bg("assets/footage/YsiccpVKUIs.mp4", 118.0), note="protection")
s.layers += [L(t_condom, s.t0, sticker("PROTECTION", "pink_plate", 90), xy=(520, 260), tilt=-5),
             L(t_sold, s.t0, sticker("ALSO SOLD YOU THIS", "red_block", 110), xy=(560, 760), tilt=3),
             L(t_last2, s.t0, sticker("LAST YEAR", "year", 56), xy=(560, 920))]
s.layers.append(Layer(max(0.0, t_sold - s.t0) + 0.15, 99, draw=lambda c, lt: curved_arrow(c, (900, 700), (1350, 520), lt / 0.35)))

# 26 "but there's a different answer to the same question from a small open source project"
s = shot(s.t1, DUR, glitch_in=True, note="tease")
s.layers += [L(t_but2, s.t0, sticker("BUT", "red_caps", 190), xy=(W / 2, 220), tilt=-5),
             L(t_different, s.t0, sticker("A DIFFERENT ANSWER", "quote", 120), xy=(W / 2, 470), tilt=2),
             L(t_small, s.t0, tile("github", 260), xy=(W / 2 - 330, 780), tilt=-4),
             L(t_open, s.t0, sticker("SMALL OPEN SOURCE PROJECT", "name_plate", 40), xy=(W / 2 + 230, 790), anim="slide_right")]

if __name__ == "__main__":
    for i, sh in enumerate(SHOTS):
        if os.environ.get("LIST"):
            print(f"{i:2d} {sh.t0:6.2f}-{sh.t1:6.2f} ({sh.t1 - sh.t0:4.2f}s) {sh.note}")
    if not os.environ.get("LIST"):
        render(SHOTS, duration=DUR, out_dir=os.environ.get("OUT", "frames/out"))
