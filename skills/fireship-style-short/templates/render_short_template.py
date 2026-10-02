#!/usr/bin/env python3
"""Vertical Fireship-style short: copy to projects/<slug>-short/render.py (setup_short.sh does it).

Narration drives everything: audio/voice.wav + audio/words.json ([[word, start, end], ...]).
Every Layer is timed to the spoken word with A("word"). Backgrounds are vertical-aware helpers from
short_kit; long-form cards go through card() so they fit the 960 px safe width.
"""
import os

from short_kit import *  # noqa: F401,F403  (sets FIRESHIP_CANVAS=9:16 before importing the engine)

WORDS = words_onsets("audio/words.json")
DUR = min(60.0, WORDS[-1][2] + 0.4)
KEYWORDS = []            # words to paint yellow in the captions (product names, numbers, punchlines)


def A(word, after=0.0):
    return at(WORDS, word, after)


SHOTS = []


def shot(t0, t1, bg=None, glitch_in=False, note=""):
    s = Shot(t0, t1, bg=bg, glitch_in=glitch_in, note=note)
    SHOTS.append(s)
    return s


def L(t_abs, s, img, xy=(CX, 320), tilt=0.0, anim="pop", until=99):
    """Layer timed by ABSOLUTE spoken time. Default spot: the sticker slot above the band."""
    return Layer(max(0.0, t_abs - s.t0), until, img=img, xy=xy, tilt=tilt, anim=anim)


# Example shape (replace):
# s = shot(0.0, A("openai") - 0.05, bg=footage_band("assets/footage/bbc_4.5.mp4"), note="hook")
# s.layers += [L(0.0, s, sticker("FIRST IN HISTORY", "starburst", 60), xy=(CX, 330), tilt=-6)]
# s = shot(SHOTS[-1].t1, ..., note="tweet")
# s.layers += [L(A("people"), s, card(tweet_card("name", "@handle", "text")), xy=(CX, 760))]

if __name__ == "__main__":
    if os.environ.get("LIST"):
        for i, sh in enumerate(SHOTS):
            print(f"{i:2d} {sh.t0:6.2f}-{sh.t1:6.2f} ({sh.t1 - sh.t0:4.2f}s) {sh.note}")
    else:
        render(SHOTS, duration=DUR, out_dir=os.environ.get("OUT", "frames/out"), post=make_captions(WORDS, KEYWORDS))
