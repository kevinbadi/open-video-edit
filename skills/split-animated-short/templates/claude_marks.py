#!/usr/bin/env python3
"""Canonical Claude marks for split-animated shorts.

Whenever the transcript says Claude / Claude Code / Opus / Sonnet / Haiku /
Fable / Anthropic / any Claude model: use these two bundled marks, never a
favicon or a text pill.

  claude-invader  — block Space-Invader. Dances, looks, grabs, morphs.
  claude-sphinx   — Anthropic starburst badge.

Copy this file + ../assets/claude-*.png into the project (or call
ensure_claude_marks()).

Choreography (layer pixels):

    place_claude_invader(layer, cx, cy, t, size=280,
                         look_at=(tx, ty),      # eyes track this point
                         grab="right",          # None | left | right | both
                         grab_at=(gx, gy),      # hand reaches this point
                         grab_t=0.0..1.0,       # 0 rest, 1 holding
                         hold=skill_card)       # RGBA pasted at the hand
"""
from __future__ import annotations

import math
import os
import shutil
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(HERE, ".."))
BUNDLED = os.path.join(SKILL, "assets")

CLAUDE_ALIASES = {
    "claude": "sphinx",
    "claude code": "invader",
    "claudecode": "invader",
    "anthropic": "sphinx",
    "opus": "sphinx",
    "sonnet": "sphinx",
    "haiku": "sphinx",
    "fable": "invader",
    "claude opus": "sphinx",
    "claude sonnet": "sphinx",
    "claude haiku": "sphinx",
    "claude fable": "invader",
    "claude 3": "sphinx",
    "claude 4": "sphinx",
    "claude 4.5": "sphinx",
    "claude 4.6": "sphinx",
}

CLAUDE_WORDS = {
    "claude", "anthropic", "opus", "sonnet", "haiku", "fable",
    "claudecode", "clod",
}

CORAL = (206, 105, 87, 255)
CORAL_DARK = (168, 78, 64, 255)
EYE = (18, 16, 15, 255)
INK = (18, 16, 15, 255)

_GRID = [
    "..######..",
    "..######..",
    "AA######AA",
    "AA######AA",
    "..######..",
    ".L.L..L.L.",
    ".L.L..L.L.",
]
_EYES = [(3, 1), (6, 1)]


def ease(p: float) -> float:
    p = max(0.0, min(1.0, p))
    return 1 - (1 - p) ** 3


def _bundled(name: str) -> str:
    p = os.path.join(BUNDLED, name)
    if os.path.isfile(p):
        return p
    for local in (os.path.join("assets", "logos", name), os.path.join("assets", name)):
        if os.path.isfile(local):
            return local
    return p


def ensure_claude_marks(dest_dir: str = "assets/logos") -> dict[str, str]:
    os.makedirs(dest_dir, exist_ok=True)
    out = {}
    for slug, src_name in (
        ("claude-invader", "claude-invader.png"),
        ("claude-sphinx", "claude-sphinx.png"),
        ("claude", "claude-sphinx.png"),
        ("anthropic", "claude-sphinx.png"),
        ("opus", "claude-sphinx.png"),
        ("sonnet", "claude-sphinx.png"),
        ("haiku", "claude-sphinx.png"),
        ("fable", "claude-invader.png"),
        ("claude-code", "claude-invader.png"),
        ("claudecode", "claude-invader.png"),
    ):
        src = _bundled(src_name)
        if not os.path.isfile(src):
            continue
        dest = os.path.join(dest_dir, f"{slug}.png")
        if os.path.abspath(src) != os.path.abspath(dest):
            shutil.copy2(src, dest)
        out[slug] = dest
    return out


def claude_kind(word: str) -> str | None:
    t = (word or "").strip().lower().rstrip(".,!?")
    if t in ("claude", "anthropic", "opus", "sonnet", "haiku"):
        return "sphinx"
    if t in ("fable", "claudecode", "clod"):
        return "invader"
    if t in CLAUDE_WORDS:
        return CLAUDE_ALIASES.get(t, "sphinx")
    return None


def load_sphinx(size: int = 220) -> Image.Image:
    return Image.open(_bundled("claude-sphinx.png")).convert("RGBA").resize((size, size), Image.LANCZOS)


def load_invader_sprite(size: int = 220) -> Image.Image:
    return Image.open(_bundled("claude-invader.png")).convert("RGBA").resize((size, size), Image.NEAREST)


def _cell_rects(cell: int, gap: int = 0):
    body, left_arm, right_arm, legs, eyes = [], [], [], [], []
    cols = len(_GRID[0])
    mid = cols / 2
    for r, row in enumerate(_GRID):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            x, y = c * (cell + gap), r * (cell + gap)
            box = (x, y, x + cell, y + cell)
            if ch == "A":
                (left_arm if c < mid else right_arm).append(box)
            elif ch == "L":
                legs.append(box)
            else:
                body.append(box)
    for c, r in _EYES:
        x, y = c * (cell + gap), r * (cell + gap)
        eyes.append((x, y, x + cell, y + cell))
    w = cols * (cell + gap) - gap
    h = len(_GRID) * (cell + gap) - gap
    return body, left_arm, right_arm, legs, eyes, w, h


def _apply(box, dx, dy, squish_y=1.0, origin=(0, 0)):
    x0, y0, x1, y1 = box
    cx, cy = origin
    y0 = cy + (y0 - cy) * squish_y
    y1 = cy + (y1 - cy) * squish_y
    return (x0 + dx, y0 + dy, x1 + dx, y1 + dy)


def _round_box(d: ImageDraw.ImageDraw, box, fill, radius: int):
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    if x1 <= x0 or y1 <= y0:
        return
    d.rounded_rectangle([x0, y0, x1, y1], radius, fill=fill)


def _centroid(boxes):
    if not boxes:
        return 0.0, 0.0
    xs = [(b[0] + b[2]) / 2 for b in boxes]
    ys = [(b[1] + b[3]) / 2 for b in boxes]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def _look_offset(look_x: float, look_y: float, cell: float, limit: float | None = None):
    lim = cell * 0.32 if limit is None else limit
    dist = math.hypot(look_x, look_y) or 1.0
    s = min(1.0, lim / dist)
    return look_x * s, look_y * s


@dataclass
class InvaderPose:
    image: Image.Image
    origin: tuple[float, float]
    left_hand: tuple[float, float]
    right_hand: tuple[float, float]
    left_eye: tuple[float, float]
    right_eye: tuple[float, float]


def claude_invader(
    t: float,
    size: int = 280,
    morph: float = 0.0,
    look: tuple[float, float] | None = None,
    grab: str | None = None,
    grab_local: tuple[float, float] | None = None,
    grab_t: float = 0.0,
) -> InvaderPose:
    """Block invader posed at time t.

    look: direction from sprite center (sprite-local px). Eyes slide that way.
    grab: 'left' | 'right' | 'both' | None
    grab_local: where the hand should go, sprite-local from center.
    grab_t: 0 rest, 1 fully reached / holding.
    """
    cell = max(8, size // 10)
    gap = max(0, cell // 12)
    body, left_arm, right_arm, legs, eyes, w, h = _cell_rects(cell, gap)
    gt = max(0.0, min(1.0, grab_t))
    pad = cell * (2 + int(4 * gt) + int(2 * morph))
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    ox, oy = pad, pad
    origin = (ox + w / 2, oy + h / 2)
    rad = max(8, cell // 4)

    bob = math.sin(t * 6.2) * cell * 0.18 * (1 - 0.6 * gt)
    squish = 1.0 - 0.08 * abs(math.sin(t * 6.2)) * (1 - 0.5 * gt)
    arm_flap = math.sin(t * 8.0) * cell * 0.55 * (1 - gt)
    walk = math.sin(t * 10.0) * (1 - 0.5 * gt)
    lx, ly = look or (0.0, 0.0)
    eye_dx, eye_dy = _look_offset(lx, ly, cell)

    def shift(box, extra_dx=0, extra_dy=0, scatter=0.0):
        x0, y0, x1, y1 = box
        mx, my = (x0 + x1) / 2 + ox, (y0 + y1) / 2 + oy
        ang = math.atan2(my - origin[1], mx - origin[0])
        burst = scatter * cell * 3.2
        dx = extra_dx + math.cos(ang) * burst
        dy = extra_dy + bob + math.sin(ang) * burst
        return _apply(
            (x0 + ox, y0 + oy, x1 + ox, y1 + oy),
            dx, dy, squish_y=squish, origin=origin,
        )

    for box in body:
        _round_box(d, shift(box, scatter=morph), CORAL, rad)

    def paint_arm(boxes, side: str):
        idle_dx = (-cell * 0.12 * math.sin(t * 8) if side == "left" else cell * 0.12 * math.sin(t * 8))
        idle_dy = (-arm_flap if side == "left" else arm_flap)
        reaching = grab in (side, "both") and gt > 0.02
        rest_cx, rest_cy = _centroid(boxes)
        rest = (rest_cx + ox - origin[0], rest_cy + oy - origin[1])
        if reaching and grab_local is not None:
            gx, gy = grab_local
            # 0-0.55 reach, 0.55-1 hold (hand stays on target, slight lift)
            p = ease(min(1.0, gt / 0.55))
            hold = ease(max(0.0, (gt - 0.55) / 0.45))
            tx = rest[0] + (gx - rest[0]) * p
            ty = rest[1] + (gy - rest[1]) * p - hold * cell * 0.9
            extra_dx, extra_dy = tx - rest[0], ty - rest[1]
            # forearm stretch: extra blocks between shoulder and hand
            shx = origin[0] + (cell * (-2.2 if side == "left" else 2.2))
            shy = origin[1] + cell * 0.2
            hx = origin[0] + tx
            hy = origin[1] + ty + bob
            n_seg = 3
            for i in range(n_seg):
                u = (i + 1) / (n_seg + 1)
                bx = shx + (hx - shx) * u - cell * 0.45
                by = shy + (hy - shy) * u - cell * 0.45
                _round_box(d, (bx, by, bx + cell * 0.9, by + cell * 0.9), CORAL, rad)
            hand = (hx, hy)
        else:
            extra_dx, extra_dy = idle_dx, idle_dy
            hand = None
        last = None
        for box in boxes:
            posed = shift(box, extra_dx=extra_dx, extra_dy=extra_dy, scatter=morph)
            _round_box(d, posed, CORAL, rad)
            last = posed
        if hand is None and last is not None:
            hand = ((last[0] + last[2]) / 2, (last[1] + last[3]) / 2)
        return hand or origin

    left_hand = paint_arm(left_arm, "left")
    right_hand = paint_arm(right_arm, "right")

    for i, box in enumerate(legs):
        phase = walk if (i % 2 == 0) else -walk
        _round_box(d, shift(box, extra_dy=phase * cell * 0.45, scatter=morph), CORAL, rad)

    blink = (t % 2.6) < 0.11
    eye_pts = []
    for box in eyes:
        sock = shift(box, scatter=morph * 0.35)
        _round_box(d, sock, CORAL_DARK, max(2, rad // 2))
        x0, y0, x1, y1 = sock
        cw, ch = x1 - x0, y1 - y0
        px = (x0 + x1) / 2 + eye_dx
        py = (y0 + y1) / 2 + eye_dy
        pw, ph = cw * 0.55, (ch * 0.18 if blink else ch * 0.55)
        pupil = (px - pw / 2, py - ph / 2, px + pw / 2, py + ph / 2)
        _round_box(d, pupil, EYE, max(2, rad // 3))
        eye_pts.append((px, py))

    if morph > 0.15:
        rays = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        rd = ImageDraw.Draw(rays)
        for i in range(14):
            ang = math.radians(i * (360 / 14) + t * 40)
            length = cell * (2.2 + 1.4 * morph) * (0.7 + 0.3 * math.sin(t * 3 + i))
            thick = max(3, int(cell * 0.28 * morph))
            x = origin[0] + math.cos(ang) * length
            y = origin[1] + math.sin(ang) * length
            rd.line([origin, (x, y)], fill=(255, 252, 248, int(210 * morph)), width=thick)
        canvas = Image.alpha_composite(canvas, rays)

    return InvaderPose(
        image=canvas,
        origin=origin,
        left_hand=left_hand,
        right_hand=right_hand,
        left_eye=eye_pts[0] if eye_pts else origin,
        right_eye=eye_pts[1] if len(eye_pts) > 1 else origin,
    )


def claude_sphinx(t: float, size: int = 200) -> Image.Image:
    base = load_sphinx(size)
    pulse = 1.0 + 0.08 * math.sin(t * 5.0)
    w = max(8, int(base.width * pulse))
    img = base.resize((w, w), Image.BICUBIC)
    return img.rotate((t * 55) % 360, expand=True, resample=Image.BICUBIC)


def skill_chip(label: str = "SKILL.md", w: int = 200, h: int = 86) -> Image.Image:
    """Tiny file card the invader can pick up."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 14, fill=(32, 30, 28, 255))
    d.rounded_rectangle([8, 8, w - 9, h - 9], 10, fill=(217, 111, 78, 255))
    font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    font = ImageFont.truetype(font_path, 22) if os.path.isfile(font_path) else ImageFont.load_default()
    d.text((w / 2, h / 2), label, font=font, fill=(255, 252, 248, 255), anchor="mm")
    return img


def place_claude_invader(
    layer: Image.Image,
    cx: float,
    cy: float,
    t: float,
    size: int = 280,
    morph: float = 0.0,
    look_at: tuple[float, float] | None = None,
    grab: str | None = None,
    grab_at: tuple[float, float] | None = None,
    grab_t: float = 0.0,
    hold: Image.Image | None = None,
) -> InvaderPose:
    look = None
    if look_at is not None:
        look = (look_at[0] - cx, look_at[1] - cy)
    grab_local = None
    if grab_at is not None:
        grab_local = (grab_at[0] - cx, grab_at[1] - cy)
    pose = claude_invader(
        t, size=size, morph=morph, look=look, grab=grab, grab_local=grab_local, grab_t=grab_t,
    )
    im = pose.image
    x = int(cx - pose.origin[0])
    y = int(cy - pose.origin[1])
    if hold is not None and grab_t > 0.55:
        which = grab or "right"
        hand = pose.left_hand if which == "left" else pose.right_hand
        if which == "both":
            hand = pose.right_hand
        hx = int(hand[0] - hold.width / 2)
        hy = int(hand[1] - hold.height + 8)
        im = im.copy()
        im.alpha_composite(hold, (hx, hy))
    layer.alpha_composite(im, (x, y))
    return pose


def place_claude_sphinx(layer: Image.Image, cx: float, cy: float, t: float, size: int = 200):
    im = claude_sphinx(t, size=size)
    x = int(cx - im.width / 2)
    y = int(cy - im.height / 2)
    layer.alpha_composite(im, (x, y))
    return im


def dance_path(t: float, w: int, h: int, margin: int = 180):
    ux = 0.5 + 0.36 * math.sin(t * 0.9)
    uy = 0.5 + 0.28 * math.sin(t * 1.8)
    x = margin + ux * (w - 2 * margin)
    y = margin + uy * (h - 2 * margin)
    return x, y
