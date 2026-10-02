#!/usr/bin/env python3
"""Type lock for split-animated talking-head.

Kevin 2026-09-15: overlay / component text is Oswald Bold — the condensed
display face (the big AND over a UI). Never Arial in the slot.

  AR / OSWALD  title cards, chips, huge_word, counters, name plates, ghosts
  CAP / LUCKIEST GUY  the kinetic captions only (Kevin 2026-09-19: CapCut-style
               chunky comic caps, white fill + 7px black stroke, resting on the line)
  ML / MENLO   terminals, code rain, tickers (machine texture only)

Copy templates/fonts/Oswald-Bold.ttf + LuckiestGuy-Regular.ttf into the workdir with the other templates.
"""
from __future__ import annotations

import os

from PIL import ImageFont

_HERE = os.path.dirname(os.path.abspath(__file__))
_CWD = os.getcwd()

_OSWALD_CANDIDATES = (
    os.path.join(_HERE, "fonts", "Oswald-Bold.ttf"),
    os.path.join(_CWD, "fonts", "Oswald-Bold.ttf"),
    os.path.join(_CWD, "assets", "fonts", "Oswald-Bold.ttf"),
    os.path.join(_HERE, "..", "assets", "fonts", "Oswald-Bold.ttf"),
)
_CAP_CANDIDATES = (
    os.path.join(_HERE, "fonts", "LuckiestGuy-Regular.ttf"),
    os.path.join(_CWD, "fonts", "LuckiestGuy-Regular.ttf"),
    os.path.join(_CWD, "assets", "fonts", "LuckiestGuy-Regular.ttf"),
)
_MENLO_CANDIDATES = (
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Supplemental/Menlo.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
)
_ARIAL = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
_GEORGIA = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"


def _first_file(*paths: str) -> str | None:
    for p in paths:
        if p and os.path.isfile(p):
            return p
    return None


OSWALD = _first_file(*_OSWALD_CANDIDATES) or _ARIAL
if OSWALD == _ARIAL:
    print("WARN: fonts/Oswald-Bold.ttf missing — overlay falling back to Arial Bold")

MENLO = _first_file(*_MENLO_CANDIDATES) or OSWALD
CAP = _first_file(*_CAP_CANDIDATES) or OSWALD
if CAP == OSWALD:
    print("WARN: fonts/LuckiestGuy-Regular.ttf missing — captions falling back to Oswald")
AR = OSWALD
ML = MENLO
GA = _first_file(_GEORGIA) or OSWALD


def F(path: str, size: int):
    """Load a face. Menlo.ttc needs collection index 0 or glyphs double-print."""
    if path.endswith(".ttc"):
        return ImageFont.truetype(path, size, index=0)
    return ImageFont.truetype(path, size)
