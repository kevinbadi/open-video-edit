#!/usr/bin/env python3
"""VIKTOR intro — long-form landscape hyper-edit (Kevin 09-25) on top of longform_engine.

Story: big-company AI rollouts are a nightmare (every employee on a different model, no shared
memory, tools don't talk) -> the biggest hack: VIKTOR -> integrates with anything, one memory,
lives in Slack -> 99% + five business fields -> solo agency can onboard more big clients ->
massive time saver -> clients just text it -> your first AI employee.
"""
import math, os
from PIL import Image, ImageDraw
import longform_engine as E
from longform_engine import *  # noqa: F401,F403
from longform_engine import words, DUR

OUT = os.environ.get("OUT", "frames/out")

# Viktor-flavoured code rain instead of the Jev glyphs
E.GLYPHS[:] = ["viktor", "slack", "memory", "agent", "integrate", "hubspot", "notion", "gmail", "sync",
               "team", "onboard", "client", "task ✓", "#ops"]

# ── word anchors ──
T_BIGGEST = tabs("biggest", 1.0)
T_COMPANIES = tabs("companies", 1.3)
T_AGENCY = tabs("agency", 4.0)
T_IMPL = tabs("implementing", 7.0)
T_TEAMS = tabs("teams", 8.9)
T_NIGHT = tabs("nightmare", 11.0)
T_EMP = tabs("employees", 11.8)
T_CLAUDE = tabs("claude", 12.5)
T_GPT = tabs("chatgpt", 13.5)
T_NEVER = tabs("never", 14.9)
T_NONE = tabs("none", 16.9)
T_MEM = tabs("memories", 17.2)
T_TOOLS = tabs("tools", 20.0)
T_MORE = tabs("more", 24.4)
T_SCOPE = tabs("scope", 25.4)
T_MUCH = tabs("much", 27.0)
T_BIGCO = tabs("big", 30.0)
T_TODAY = tabs("today", 31.9)
T_BIGGEST2 = tabs("biggest", 34.0)
T_HACK = tabs("hack", 34.2)
T_VIK = tabs("viktor", 35.5)
T_VIK2 = tabs("viktor", 36.9)
T_BUSINESSES = tabs("businesses", 38.3)
T_CLIENTS = tabs("clients", 39.0)
T_INTERNAL = tabs("internally", 40.0)
T_GROUP = tabs("group", 41.8)
T_EASIER = tabs("easier", 43.9)
T_VIK3 = tabs("viktor", 46.4)
T_FIRST = tabs("first", 47.3)
T_INTEG = tabs("integrates", 49.5)
T_ANY = tabs("any", 50.3)
T_SHARES = tabs("shares", 53.4)
T_MEMORY = tabs("memory", 54.5)
T_CHAT = tabs("chat", 57.3)
T_AGENT = tabs("agent", 58.1)
T_SLACK = tabs("slack", 59.7)
T_EVERYONE = tabs("everyone", 60.4)
T_AGENCY2 = tabs("agency", 62.9)
T_SOCIAL = tabs("social", 64.5)
T_AUTO = tabs("automations", 65.7)
T_BREAK = tabs("break", 67.5)
T_99 = tabs("99%", 68.0)
T_KNOW = tabs("know", 71.0)
T_FIVE = tabs("five", 72.8)
T_FIELDS = tabs("fields", 73.9)
T_BIGGER = tabs("bigger", 78.3)
T_INDIV = tabs("individual", 81.6)
T_ENTRE = tabs("entrepreneur", 82.1)
T_CONF = tabs("confidence", 86.0)
T_BIGCO2 = tabs("big", 87.6)
T_ONBOARD = tabs("onboard", 88.7)
T_BEFORE = tabs("before", 91.0)
T_MASSIVE = tabs("massive", 92.7)
T_TIME = tabs("time", 93.2)
T_RECEIVE = tabs("receive", 96.5)
T_TEXT = tabs("text", 100.0)
T_DO = tabs("do", 101.1)
T_WANT = tabs("want", 102.5)
T_FIRST2 = tabs("first", 105.3)
T_EMPLOYEE = tabs("employee", 106.2)
T_HIRE = tabs("hire", 106.7)
T_ONBOARDING = tabs("onboarding", 108.8)
T_AIEMP = tabs("employee", 110.6)
T_MSG = tabs("messaging", 111.8)

SECT = [
    ("hook",         0.00,   5.06,   "FULL",  VIOLET),
    ("nightmare",    5.06,   11.70,  "SPLIT", RED),
    ("chaos",        11.70,  19.86,  "HERO",  ORANGE),
    ("tools",        19.86,  25.36,  "SPLIT", ORANGE),
    ("scope",        25.36,  32.02,  "SPLIT", RED),
    ("hack",         32.02,  35.37,  "FULL",  VIOLET),
    ("reveal",       35.37,  37.97,  "SOLO",  VIOLET),   # source has a logo slate here (no face)
    ("viktor",       37.97,  41.28,  "SPLIT", VIOLET),
    ("group",        41.28,  46.22,  "SPLIT", NEON),
    ("integrations", 46.22,  55.96,  "HERO",  VIOLET),
    ("slack",        55.96,  62.62,  "SPLIT", CYAN),
    ("agency",       62.62,  66.58,  "SPLIT", PINK),
    ("breakdown",    66.58,  75.53,  "HERO",  NEON),
    ("fields",       75.53,  78.06,  "SOLO",  NEON),     # second logo slate in the source
    ("bigdeal",      78.06,  85.80,  "SPLIT", PINK),
    ("onboard",      85.80,  92.36,  "SPLIT", CYAN),
    ("timesaver",    92.36,  95.86,  "SPLIT", NEON),
    ("clients",      95.86,  103.92, "SPLIT", CYAN),
    ("employee",     103.92, 108.56, "SPLIT", VIOLET),
    ("close",        108.56, DUR,    "FULL",  VIOLET),
]

KEY_COL = {
    "biggest": VIOLET, "companies": VIOLET, "ai": VIOLET, "agency": VIOLET,
    "implementing": RED, "systems": RED, "big": RED, "teams": RED, "nightmare": RED,
    "employees": ORANGE, "claude": ORANGE, "chatgpt": NEON, "never": ORANGE, "touched": ORANGE,
    "memories": ORANGE, "interact": ORANGE, "none": RED, "tools": ORANGE,
    "more": RED, "work": RED, "scope": RED, "much": RED,
    "today": VIOLET, "hack": VIOLET, "viktor": VIOLET, "businesses": VIOLET, "clients": CYAN,
    "internally": VIOLET, "group": NEON, "easier": NEON,
    "first": VIOLET, "tool": VIOLET, "literally": ORANGE, "integrates": VIOLET, "integration": VIOLET,
    "any": VIOLET, "third": VIOLET, "party": VIOLET, "shares": CYAN, "one": CYAN, "consistent": CYAN,
    "memory": CYAN, "chat": CYAN, "agent": CYAN, "slack": CYAN, "everyone": CYAN,
    "social": PINK, "media": PINK, "marketing": PINK, "automations": PINK,
    "break": NEON, "99%": NEON, "anything": NEON, "five": NEON, "fields": NEON, "business": NEON,
    "bigger": PINK, "deal": PINK, "individual": PINK, "entrepreneur": PINK,
    "confidence": CYAN, "onboard": CYAN, "before": CYAN,
    "massive": NEON, "time": NEON, "saver": NEON,
    "receive": CYAN, "communicate": CYAN, "text": CYAN, "want": CYAN,
    "employee": VIOLET, "hire": VIOLET, "company": VIOLET, "onboarding": VIOLET, "messaging": VIOLET,
    "channels": VIOLET,
}
KEYWORDS = set(KEY_COL)

WHITE_TILE = (255, 252, 248, 255)
INTEG = ["slack", "notion", "gmail", "hubspot", "gdrive", "salesforce", "shopify", "instagram", "zapier", "youtube"]
STACK = [b for b in (logo_badge(s, 116, punch=False, fill=WHITE_TILE) for s in INTEG) if b is not None]
MODELS = [b for b in (logo_badge(s, 116, punch=False, fill=WHITE_TILE) for s in ("claude", "openai", "slack", "notion"))
          if b is not None]


# ───────────── bespoke cards ─────────────
def big_num(txt, col, fsz=260):
    """Giant stat text sized from the real glyph bbox (wordmark clips tall Oswald digits)."""
    def build():
        f = F(AR, fsz)
        d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        x0, y0, x1, y1 = d0.textbbox((0, 0), txt, font=f)
        img = Image.new("RGBA", (x1 - x0 + 40, y1 - y0 + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((20 - x0 + 6, 20 - y0 + 6), txt, font=f, fill=(0, 0, 0, 160))
        d.text((20 - x0, 20 - y0), txt, font=f, fill=col + (255,))
        return img
    return cached(("bignum", txt, col, fsz), build)


def viktor_badge(size=300):
    return round_logo("viktor", size)


def tile(slug, size=150):
    return logo_badge(slug, size, punch=False, fill=WHITE_TILE)


def avatar(initial, col, size=96):
    def build():
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse([0, 0, size - 1, size - 1], fill=col + (255,))
        d.text((size / 2, size / 2), initial, font=F(AR, int(size * 0.5)), fill=INK + (255,), anchor="mm")
        return im
    return cached(("avatar", initial, col, size), build)


def employee_card(name, initial, col, slug=None, note="", w=400, h=330):
    """Team member tile: avatar + name + the AI they use (logo) or a note."""
    def build():
        card = shadow_card((w, h), 24, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        card.alpha_composite(avatar(initial, col, 110), (pad + w // 2 - 55, pad + 26))
        d.text((pad + w / 2, pad + 168), name, font=F(AR, 34), fill=WHITE + (255,), anchor="mm")
        if slug:
            m = tile(slug, 92)
            card.alpha_composite(m, (int(pad + w / 2 - m.width / 2), pad + 200))
        else:
            d.text((pad + w / 2, pad + 250), note, font=F(AR, 30), fill=col + (255,), anchor="mm")
        d.rectangle([pad, pad + 10, pad + 8, pad + h - 10], fill=col + (255,))
        return card
    return cached(("emp", name, slug, note, w, h), build)


def chat_card(lt, msgs, title="# team-ops", w=900, h=560, accent=CYAN, logo="slack"):
    """Slack-ish channel. msgs = [(t0, who, initial, col, text, is_bot)] appear at t0 (card-local)."""
    shown = tuple(i for i, m in enumerate(msgs) if lt >= m[0])
    typing = next((i for i, m in enumerate(msgs) if m[0] - 0.7 <= lt < m[0] and m[5]), None)
    tick = int(lt * 6) % 3 if typing is not None else 0

    def build():
        card = shadow_card((w, h), 24, (26, 28, 34, 255))
        pad = 32
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad, pad, pad + w, pad + 70], 24, fill=INK + (255,))
        d.rectangle([pad, pad + 40, pad + w, pad + 70], fill=INK + (255,))
        lm = logo_mark(logo, 40, punch=False)
        if lm is not None:
            card.alpha_composite(lm, (pad + 22, pad + 15))
        d.text((pad + 78, pad + 35), title, font=F(AR, 30), fill=WHITE + (255,), anchor="lm")
        d.text((pad + w - 24, pad + 35), "● 14 members", font=MONO_S, fill=NEON + (220,), anchor="rm")
        y = pad + 96
        rows = [msgs[i] for i in shown][-4:]
        for _t0, who, ini, col, text, bot in rows:
            if bot:
                vb = logo_mark("viktor", 60, punch=False)
                card.alpha_composite(vb, (pad + 24, y))
            else:
                card.alpha_composite(avatar(ini, col, 60), (pad + 24, y))
            d.text((pad + 100, y + 2), who, font=F(AR, 26), fill=(col if not bot else VIOLET) + (255,))
            if bot:
                tw = d.textlength(who, font=F(AR, 26))
                d.rounded_rectangle([pad + 112 + tw, y + 6, pad + 172 + tw, y + 30], 6, fill=VIOLET + (255,))
                d.text((pad + 142 + tw, y + 18), "APP", font=F(AR, 16), fill=WHITE + (255,), anchor="mm")
            d.text((pad + 100, y + 40), text, font=MONO, fill=SILVER + (255,))
            y += 104
        if typing is not None:
            d.text((pad + 24, pad + h - 44), "Viktor is typing" + "." * (tick + 1), font=MONO_S, fill=STEEL + (255,))
        return card
    return cached(("chat", shown, typing, tick, title, w, h), build)


def scope_card(p, w=960, h=300):
    """Expected vs actual scope bars; the actual bar overflows the card."""
    k = int(clamp01(p) * 40)
    def build():
        card = shadow_card((w, h), 22, GRAPHITE + (255,))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + 24, pad + 18), "SCOPE OF WORK", font=F(AR, 28), fill=RED + (255,))
        bx0, bw = pad + 220, w - 260
        d.text((pad + 24, pad + 96), "expected", font=F(AR, 30), fill=SILVER + (255,))
        d.rounded_rectangle([bx0, pad + 92, bx0 + int(bw * 0.3), pad + 136], 12, fill=CYAN + (255,))
        d.text((pad + 24, pad + 186), "actual", font=F(AR, 30), fill=SILVER + (255,))
        aw = int(bw * (0.3 + 0.72 * k / 40))
        d.rounded_rectangle([bx0, pad + 182, bx0 + min(aw, bw), pad + 226], 12, fill=RED + (255,))
        if k >= 36:
            d.text((bx0 + bw - 10, pad + 204), "OVER", font=F(AR, 30), fill=WHITE + (255,), anchor="rm")
        return card
    return cached(("scope", k, w, h), build)


def field_tile(i, on, w=300, h=300, col=NEON):
    def build():
        card = shadow_card((w, h), 24, (col + (255,)) if on else (GRAPHITE + (255,)))
        pad = 32
        d = ImageDraw.Draw(card)
        d.text((pad + w / 2, pad + h / 2 - 20), f"0{i}", font=F(AR, 130), fill=(INK if on else STEEL) + (255,), anchor="mm")
        d.text((pad + w / 2, pad + h - 44), "FIELD", font=F(AR, 30), fill=(INK if on else STEEL) + (255,), anchor="mm")
        return card
    return cached(("field", i, on, w, h, col), build)


def building(col, size=110):
    def build():
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([14, 8, size - 14, size - 4], 10, fill=GRAPHITE + (255,), outline=col + (255,), width=4)
        for r in range(4):
            for c in range(3):
                x = 28 + c * (size - 56) / 2.4
                y = 20 + r * 20
                d.rectangle([x, y, x + 12, y + 10], fill=col + (200,))
        return im
    return cached(("bldg", col, size), build)


def id_badge(w=520, h=640):
    """Hanging employee ID for the first AI hire."""
    def build():
        card = shadow_card((w, h), 30, WHITE_TILE)
        pad = 32
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad, pad, pad + w, pad + 130], 30, fill=VIOLET + (255,))
        d.rectangle([pad, pad + 90, pad + w, pad + 130], fill=VIOLET + (255,))
        d.rounded_rectangle([pad + w / 2 - 60, pad + 22, pad + w / 2 + 60, pad + 42], 10, fill=(26, 28, 34, 255))
        d.text((pad + w / 2, pad + 94), "AI EMPLOYEE  #001", font=F(AR, 34), fill=WHITE + (255,), anchor="mm")
        vb = logo_mark("viktor", 230, punch=False)
        card.alpha_composite(vb, (int(pad + w / 2 - 115), pad + 160))
        d.text((pad + w / 2, pad + 440), "VIKTOR", font=F(AR, 72), fill=INK + (255,), anchor="mm")
        d.text((pad + w / 2, pad + 505), "Team: everyone  ·  Lives in: Slack", font=F(AR, 26), fill=STEEL + (255,), anchor="mm")
        d.rounded_rectangle([pad + 60, pad + 548, pad + w - 60, pad + 600], 14, fill=NEON + (255,))
        d.text((pad + w / 2, pad + 574), "HIRED", font=F(AR, 32), fill=INK + (255,), anchor="mm")
        return card
    return cached(("idbadge", w, h), build)


def hub(layer, cx, cy, lt, t0, slugs, radius=330, size=130, stagger=0.12, spin=0.08, core=280, ring_ry=0.62):
    """Viktor in the centre, integration tiles on an elliptical orbit, wired in one by one."""
    d = ImageDraw.Draw(layer)
    n = len(slugs)
    for i, slug in enumerate(slugs):
        ti = t0 + i * stagger
        if lt < ti:
            continue
        ang = 2 * math.pi * i / n + lt * spin - math.pi / 2
        x = cx + radius * math.cos(ang)
        y = cy + radius * ring_ry * math.sin(ang)
        p = clamp01((lt - ti) / 0.25)
        lx = cx + (x - cx) * p
        ly = cy + (y - cy) * p
        d.line([cx, cy, lx, ly], fill=VIOLET + (150,), width=4)
        ph = ((lt - ti) * 0.9 + i * 0.17) % 1.0
        px, py = x + (cx - x) * ph, y + (cy - y) * ph
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=CYAN + (230,))
        place(layer, tile(slug, size), x, y, lt, ti, dur=0.22, scale_pop=True, idle=0)
    bloom_orb(layer, cx, cy, int(core * 0.75), VIOLET, a=70)
    place(layer, viktor_badge(core), cx, cy, lt, -0.3, dur=0.01, idle=0)


# ───────────── scenes ─────────────
def scene(layer, name, lt, t, a, acc):
    lw, lh = layer.size
    r = lambda T: max(0.0, T - 0.08 - a)  # noqa: E731
    cx0 = lw // 2

    if name == "hook":
        # FULL: bright on-topic billboard from frame 0 (no dark wash, no "?")
        tb, tag = r(T_BIGGEST), r(T_AGENCY)
        bloom_orb(layer, 1600, 230, 200, VIOLET, a=60)
        place(layer, viktor_badge(270), 1600, 230, lt, -0.4, dur=0.01, idle=0)
        place(layer, wordmark("VIKTOR", WHITE, 120), 1600, 460, lt, -0.4, dur=0.01, idle=0)
        place(layer, chip("the AI employee for big teams", VIOLET, fsz=30), 1600, 580, lt, -0.4, dur=0.01, idle=0)
        if lt >= tb:
            place(layer, stamp_card("BIGGEST COMPANIES", VIOLET, fsz=60, w=620, h=140), 1600, 760, lt, tb, dur=0.2,
                  tilt=-6, scale_pop=True, idle=0)
            light_hit(layer, 1600, 760, t, T_BIGGEST, VIOLET)
        if lt >= tag:
            place(layer, chip("my AI agency", ORANGE, fsz=30), 1600, 890, lt, tag, frm="down")
            light_hit(layer, 1600, 890, t, T_AGENCY, ORANGE)

    elif name == "nightmare":
        draw_code_rain(layer, lt, n=14, col=RED)
        layer.alpha_composite(ghost_img("BIG TEAMS", 140, lw), (-60 + int(30 * math.sin(lt * 0.6)), 0))
        ticker(layer, "  IMPLEMENTING AI  ·  FOR BIG TEAMS  ·  HONESTLY A NIGHTMARE  ·  ", 850, lt, fill=RED + (110,))
        ti, tt, tn = r(T_IMPL), r(T_TEAMS), r(T_NIGHT)
        place(layer, big_text_card("AI SYSTEMS FOR BIG TEAMS", RED, fsz=54, w=1000, h=126), cx0, 70, lt, -0.35,
              dur=0.01, scale_pop=True)
        if lt < tn - 0.06:
            lines = [(0.0, "$ rollout ai --org acme", SILVER), (0.5, "! 212 employees, 0 shared setup", ORANGE),
                     (1.0, "! 6 tools, 0 connected", ORANGE), (1.5, "✗ memory: fragmented", RED),
                     (2.0, "✗ scope: exploding", RED)]
            place(layer, terminal_card(lt - max(0, ti - 0.3), lines, title="ENTERPRISE ROLLOUT", w=640, h=300, accent=RED),
                  370, 420, lt, -0.3, dur=0.01, frm="left", exit_at=tn - 0.06)
            for k in range(6):
                bx = 820 + (k % 2) * 150
                by = 300 + (k // 2) * 130
                place(layer, avatar("ABCDEF"[k], (ORANGE, CYAN, PINK, NEON, VIOLET, SILVER)[k], 100), bx, by, lt,
                      tt + k * 0.07, dur=0.2, scale_pop=True, idle=3)
            if lt >= tt:
                place(layer, chip("big teams", RED), 900, 700, lt, tt, frm="down", exit_at=tn - 0.06)
        else:
            place(layer, stamp_card("NIGHTMARE", RED, fsz=90, w=620, h=170), 330, 300, lt, tn, dur=0.2, tilt=-8,
                  scale_pop=True, idle=0)
            light_hit(layer, 330, 300, t, T_NIGHT, RED)
            light_rays(layer, 330, 300, t, RED, a=16)
            front_gif(gif_card("fine", max(0, lt - tn), w=520, frame="round"), 820, 470, lt, tn + 0.05, **entrance(1))
        guarded_conveyor(layer, 800, lt, STACK, conveyor_marks, name="stack-n", speed=170, gap=22)

    elif name == "chaos":
        # HERO: three employees, three different AI setups; memories don't talk
        draw_code_rain(layer, lt, n=20, col=ORANGE)
        ticker(layer, "  ONE USES CLAUDE  ·  ONE USES CHATGPT  ·  ONE NEVER TOUCHED AI  ·  NO SHARED MEMORY  ·  ",
               880, lt, fill=ORANGE + (110,))
        te, tc, tg, tv, tno, tm = r(T_EMP), r(T_CLAUDE), r(T_GPT), r(T_NEVER), r(T_NONE), r(T_MEM)
        place(layer, big_text_card("EVERY EMPLOYEE, A DIFFERENT AI", ORANGE, fsz=54, w=1100, h=126), 640, 70, lt,
              -0.35, dur=0.01, scale_pop=True)
        xs = [230, 680, 1130]
        cards = [(tc, employee_card("EMPLOYEE 1", "A", ORANGE, "claude"), T_CLAUDE),
                 (tg, employee_card("EMPLOYEE 2", "B", NEON, "openai"), T_GPT),
                 (tv, employee_card("EMPLOYEE 3", "C", PINK, None, "never touched AI"), T_NEVER)]
        blanks = [employee_card("EMPLOYEE 1", "A", ORANGE, None, "uses..."),
                  employee_card("EMPLOYEE 2", "B", NEON, None, "uses..."),
                  employee_card("EMPLOYEE 3", "C", PINK, None, "...")]
        for k, (t0, img, T) in enumerate(cards):
            show = img if lt >= t0 else blanks[k]
            place(layer, show, xs[k], 380, lt, -0.35 + k * 0.08, dur=0.25, frm=("left", "up", "right")[k], idle=0)
            if lt >= t0:
                light_hit(layer, xs[k], 380, t, T, ORANGE)
        if lt >= tm:
            d = ImageDraw.Draw(layer)
            for k in range(2):
                x0, x1 = xs[k] + 215, xs[k + 1] - 215
                for s in range(0, int(x1 - x0), 26):
                    d.line([x0 + s, 380, x0 + s + 14, 380], fill=RED + (220,), width=6)
                place(layer, x_mark(90), (x0 + x1) / 2, 380, lt, tm + k * 0.1, dur=0.15, scale_pop=True, idle=0)
            place(layer, strike_chip("shared memory", RED), 640, 640, lt, tm, frm="down")
            light_hit(layer, 640, 380, t, T_MEM, RED)
        if lt >= tno:
            front_gif(gif_card("confused", max(0, lt - tno), w=420, frame="round"), 1560, 330, lt, tno, **entrance(3))
            place(layer, chip("none of it talks", RED, fsz=30), 1560, 560, lt, tno + 0.1, frm="down")

    elif name == "tools":
        draw_code_rain(layer, lt, n=14, col=ORANGE)
        ticker(layer, "  NONE OF THE TOOLS INTERACT  ·  MORE WORK FOR ME  ·  ", 850, lt, fill=ORANGE + (110,))
        tt, tm = r(T_TOOLS), r(T_MORE)
        place(layer, big_text_card("NONE OF THE TOOLS TALK", ORANGE, fsz=56, w=1000, h=130), cx0, 70, lt, -0.35,
              dur=0.01, scale_pop=True)
        grid = ["slack", "notion", "gmail", "hubspot", "gdrive", "salesforce"]
        for k, s in enumerate(grid):
            x = 180 + (k % 3) * 190
            y = 300 + (k // 3) * 190
            place(layer, tile(s, 150), x, y, lt, -0.3 + k * 0.05, dur=0.2, idle=0)
            if lt >= tt + k * 0.09:
                place(layer, x_mark(120), x, y, lt, tt + k * 0.09, dur=0.15, scale_pop=True, idle=0)
        if lt >= tt:
            light_hit(layer, 370, 400, t, T_TOOLS, ORANGE)
        if lt < tm - 0.06:
            place(layer, chip("siloed", ORANGE, fsz=32), 900, 300, lt, tt + 0.3, frm="right", exit_at=tm - 0.06)
        else:
            front_gif(gif_card("stressed", max(0, lt - tm), w=380, frame="round"), 900, 380, lt, tm, **entrance(2))
            place(layer, stamp_card("MORE WORK", RED, fsz=64, w=440, h=130), 900, 650, lt, tm + 0.05, dur=0.2, tilt=6,
                  scale_pop=True, idle=0)
            light_hit(layer, 900, 650, t, T_MORE, RED)
        guarded_conveyor(layer, 800, lt, STACK, conveyor_marks, name="stack-t", speed=170, gap=22)

    elif name == "scope":
        draw_code_rain(layer, lt, n=14, col=RED)
        layer.alpha_composite(ghost_img("SCOPE", 150, lw), (-60 + int(30 * math.sin(lt * 0.6)), 0))
        ticker(layer, "  THE SCOPE KEPT GROWING  ·  FOR THESE BIG COMPANIES  ·  ", 850, lt, fill=RED + (110,))
        ts, tmu, tb = r(T_SCOPE), r(T_MUCH), r(T_BIGCO)
        place(layer, big_text_card("THE SCOPE OF MY WORK", RED, fsz=56, w=1000, h=130), cx0, 70, lt, -0.35, dur=0.01,
              scale_pop=True)
        place(layer, scope_card((lt - ts) / 3.0, w=1000, h=300), cx0, 340, lt, ts - 0.1, dur=0.25, frm="up")
        if lt >= ts:
            light_hit(layer, cx0, 340, t, T_SCOPE, RED)
        if lt >= tmu:
            place(layer, stamp_card("SO MUCH MORE", RED, fsz=64, w=560, h=140), 330, 620, lt, tmu, dur=0.2, tilt=-6,
                  scale_pop=True, idle=0)
            light_hit(layer, 330, 620, t, T_MUCH, RED)
        if lt >= tb:
            for k in range(5):
                place(layer, building(RED, 110), 700 + k * 90, 640, lt, tb + k * 0.06, dur=0.2, scale_pop=True, idle=0)
            place(layer, chip("for these big companies", RED), 880, 750, lt, tb + 0.2, frm="down")
        guarded_conveyor(layer, 850, lt, STACK, conveyor_marks, name="stack-s", speed=170, gap=22) if lt < tb else None

    elif name == "hack":
        # FULL: the reveal promise — biggest hack
        tb, th = r(T_BIGGEST2), r(T_HACK)
        place(layer, chip("today I'm going to show you...", VIOLET, fsz=32), 1600, 160, lt, -0.3, dur=0.01, frm="right",
              idle=0)
        if lt >= tb:
            place(layer, wordmark("THE BIGGEST HACK", WHITE, 100), 1580, 300, lt, tb, dur=0.25, scale_pop=True, idle=0)
            light_hit(layer, 1580, 300, t, T_BIGGEST2, VIOLET)
            light_rays(layer, 1580, 300, t, VIOLET, a=18)
        if lt >= th:
            front_gif(gif_card("mindblown", max(0, lt - th), w=440, frame="round"), 1600, 590, lt, th, **entrance(4))
            sil = viktor_badge(170).copy()
            sil.putalpha(sil.split()[3].point(lambda v: int(v * 0.45)))
            place(layer, sil, 1600, 840, lt, th + 0.3, dur=0.2, scale_pop=True, idle=0)

    elif name == "reveal":
        # SOLO (full-width, no head: the source is a logo slate here) — the name drop
        draw_code_rain(layer, lt, n=26, col=VIOLET)
        layer.alpha_composite(ghost_img("VIKTOR  VIKTOR  VIKTOR", 170, lw), (-120 + int(40 * math.sin(lt * 0.6)), 690))
        tv, tv2 = r(T_VIK), r(T_VIK2)
        place(layer, chip("it's called", VIOLET, fsz=40), 920, 110, lt, -0.3, dur=0.01, idle=0)
        bloom_orb(layer, 560, 430, 300, VIOLET, a=80)
        place(layer, viktor_badge(460), 560, 430, lt, -0.3, dur=0.01, idle=0)
        if lt >= tv:
            light_hit(layer, 560, 430, t, T_VIK, VIOLET)
            light_rays(layer, 560, 430, t, VIOLET)
            place(layer, big_num("VIKTOR", WHITE, 230), 1260, 400, lt, tv + 0.06, dur=0.25, frm="right", scale_pop=True,
                  idle=0)
        if lt >= tv2:
            place(layer, chip("I use it in every client business", ORANGE, fsz=36), 1260, 600, lt, tv2, frm="down")
            light_hit(layer, 1260, 600, t, T_VIK2, ORANGE)

    elif name == "viktor":
        draw_code_rain(layer, lt, n=16, col=VIOLET)
        layer.alpha_composite(ghost_img("VIKTOR", 150, lw), (-60 + int(30 * math.sin(lt * 0.6)), 0))
        ticker(layer, "  IT'S CALLED VIKTOR  ·  EVERY CLIENT BUSINESS  ·  AND INTERNALLY  ·  ", 850, lt, fill=VIOLET + (110,))
        tbz, tcl, tin = r(T_BUSINESSES), r(T_CLIENTS), r(T_INTERNAL)
        place(layer, big_text_card("ALL MY CLIENTS + MY OWN TEAM", VIOLET, fsz=54, w=1000, h=126), cx0, 70, lt, -0.35,
              dur=0.01, scale_pop=True)
        place(layer, viktor_badge(300), 260, 380, lt, -0.3, dur=0.01, idle=0)
        d = ImageDraw.Draw(layer)
        if lt >= tcl:
            for k in range(4):
                x, y = 640 + (k % 2) * 260, 300 + (k // 2) * 180
                if lt >= tcl + k * 0.08:
                    d.line([260, 380, x, y], fill=VIOLET + (150,), width=4)
                place(layer, building(CYAN, 120), x, y, lt, tcl + k * 0.08, dur=0.2, scale_pop=True, idle=0)
            place(layer, chip("my clients", CYAN, fsz=30), 770, 560, lt, tcl + 0.1, frm="down")
            light_hit(layer, 770, 380, t, T_CLIENTS, CYAN)
        elif lt >= tbz:
            place(layer, chip("the businesses", VIOLET, fsz=30), 770, 380, lt, tbz, frm="right")
        if lt >= tin:
            place(layer, stamp_card("+ INTERNALLY", ORANGE, fsz=56, w=440, h=130), 260, 640, lt, tin, dur=0.2, tilt=-6,
                  scale_pop=True, idle=0)
            light_hit(layer, 260, 640, t, T_INTERNAL, ORANGE)
        guarded_conveyor(layer, 800, lt, STACK, conveyor_marks, name="stack-v", speed=170, gap=22)

    elif name == "group":
        draw_code_rain(layer, lt, n=14, col=NEON)
        ticker(layer, "  GROUP WORK  ·  A LOT EASIER  ·  FOR THESE TEAMS  ·  ", 850, lt, fill=NEON + (110,))
        tg, te = r(T_GROUP), r(T_EASIER)
        place(layer, big_text_card("GROUP WORK, MADE EASY", NEON, fsz=56, w=1000, h=130), cx0, 70, lt, -0.35, dur=0.01,
              scale_pop=True)
        # team avatars wired into one Viktor node
        cx, cy = 330, 420
        d = ImageDraw.Draw(layer)
        cols = (ORANGE, CYAN, PINK, NEON, SILVER, VIOLET)
        for k in range(6):
            ang = 2 * math.pi * k / 6 - math.pi / 2
            x, y = cx + 230 * math.cos(ang), cy + 200 * math.sin(ang)
            if lt >= tg + k * 0.06:
                d.line([cx, cy, x, y], fill=NEON + (170,), width=4)
            place(layer, avatar("ABCDEF"[k], cols[k], 96), x, y, lt, -0.3 + k * 0.04, dur=0.2, idle=3)
        place(layer, viktor_badge(170), cx, cy, lt, -0.3, dur=0.01, idle=0)
        if lt >= tg:
            light_hit(layer, cx, cy, t, T_GROUP, NEON)
        if lt < te - 0.06:
            place(layer, chip("one agent, whole team", NEON, fsz=30), 860, 300, lt, tg, frm="right", exit_at=te - 0.06)
        else:
            front_gif(gif_card("easy", max(0, lt - te), w=420, frame="round"), 860, 380, lt, te, **entrance(5))
            place(layer, stamp_card("EASIER", NEON, fsz=80, w=440, h=150), 860, 650, lt, te + 0.05, dur=0.2, tilt=-6,
                  scale_pop=True, idle=0)
            light_hit(layer, 860, 650, t, T_EASIER, NEON)

    elif name == "integrations":
        # HERO: Viktor hub, any third-party integration wires in; then ONE shared memory
        draw_code_rain(layer, lt, n=22, col=VIOLET)
        layer.alpha_composite(ghost_img("INTEGRATES", 150, lw), (-60 + int(30 * math.sin(lt * 0.6)), 0))
        ticker(layer, "  THE FIRST TOOL  ·  ANY THIRD PARTY INTEGRATION  ·  ONE CONSISTENT MEMORY  ·  ", 880, lt,
               fill=VIOLET + (110,))
        tf, ti, tan, tsh, tme = r(T_FIRST), r(T_INTEG), r(T_ANY), r(T_SHARES), r(T_MEMORY)
        place(layer, big_text_card("THE FIRST TOOL THAT INTEGRATES WITH ANYTHING", VIOLET, fsz=50, w=1240, h=120),
              680, 66, lt, -0.35, dur=0.01, scale_pop=True)
        hub(layer, 620, 480, lt, ti, INTEG, radius=430, size=128, stagger=0.1, core=260, ring_ry=0.68)
        if lt < ti:
            place(layer, chip("the first tool I've seen", VIOLET, fsz=32), 620, 700, lt, tf, frm="down", exit_at=ti - 0.05)
        else:
            light_hit(layer, 620, 480, t, T_INTEG, VIOLET)
        if lt >= tan:
            place(layer, stamp_card("ANY INTEGRATION", VIOLET, fsz=56, w=560, h=130), 1500, 220, lt, tan, dur=0.2,
                  tilt=6, scale_pop=True, idle=0)
            light_hit(layer, 1500, 220, t, T_ANY, VIOLET)
        if lt >= tsh:
            lines = [(0.0, "client: acme co", SILVER), (0.4, "brand voice: bold, no fluff", CYAN),
                     (0.8, "q4 goals: +30% leads", CYAN), (1.2, "synced → 14 teammates ✓", NEON)]
            place(layer, terminal_card(lt - tsh, lines, title="ONE SHARED MEMORY", w=520, h=250, accent=CYAN, prompt=False),
                  1500, 470, lt, tsh, dur=0.25, frm="right")
        if lt >= tme:
            light_hit(layer, 1500, 470, t, T_MEMORY, CYAN)

    elif name == "slack":
        draw_code_rain(layer, lt, n=12, col=CYAN)
        ticker(layer, "  EVERY EMPLOYEE CAN CHAT WITH IT  ·  RIGHT INSIDE SLACK  ·  WHERE THE TEAM LIVES  ·  ", 870, lt,
               fill=CYAN + (110,))
        tc, ta, ts, te = r(T_CHAT), r(T_AGENT), r(T_SLACK), r(T_EVERYONE)
        place(layer, big_text_card("CHAT WITH IT IN SLACK", CYAN, fsz=56, w=1000, h=130), cx0, 70, lt, -0.35, dur=0.01,
              scale_pop=True)
        msgs = [(0.2, "Sarah · Marketing", "S", PINK, "@Viktor draft 3 posts for launch", False),
                (1.3, "Viktor", "V", VIOLET, "Done. Drafts in Notion, scheduled ✓", True),
                (2.6, "Mike · Sales", "M", ORANGE, "@Viktor update the HubSpot deal", False),
                (3.8, "Viktor", "V", VIOLET, "Updated + pinged the account owner ✓", True)]
        place(layer, chat_card(lt - tc + 0.2, msgs, title="# team-ops", w=820, h=500), 470, 460, lt, tc - 0.2, dur=0.25,
              frm="left")
        if lt >= tc:
            light_hit(layer, 470, 460, t, T_CHAT, CYAN)
        if lt >= ts:
            place(layer, tile("slack", 180), 1000, 330, lt, ts, dur=0.25, scale_pop=True, idle=0)
            light_hit(layer, 1000, 330, t, T_SLACK, CYAN)
            light_rays(layer, 1000, 330, t, CYAN, a=14)
        if lt >= te:
            place(layer, chip("where everyone lives", CYAN, fsz=26), 960, 560, lt, te, frm="down")

    elif name == "agency":
        draw_code_rain(layer, lt, n=14, col=PINK)
        ticker(layer, "  MY AI AGENCY  ·  SOCIAL MEDIA MARKETING AUTOMATIONS  ·  ", 850, lt, fill=PINK + (110,))
        ta, tso, tau = r(T_AGENCY2), r(T_SOCIAL), r(T_AUTO)
        place(layer, big_text_card("MY AI AGENCY", PINK, fsz=60, w=1000, h=136), cx0, 70, lt, -0.35, dur=0.01,
              scale_pop=True)
        socials = ("instagram", "youtube", "slack")
        for k, s in enumerate(socials):
            place(layer, tile(s, 170), 200 + k * 220, 330, lt, tso + k * 0.1, dur=0.22, scale_pop=True, idle=0)
        if lt >= tso:
            light_hit(layer, 420, 330, t, T_SOCIAL, PINK)
            place(layer, chip("social media marketing", PINK, fsz=30), 420, 480, lt, tso + 0.1, frm="down")
        lines = [(0.0, "> post scheduled · IG reel", SILVER), (0.5, "> comment → DM sent", PINK),
                 (1.0, "> weekly report → #client", CYAN), (1.5, "✓ automations running", NEON)]
        place(layer, terminal_card(lt - max(0, tau - 0.2), lines, title="AUTOMATIONS", w=560, h=250, accent=PINK),
              cx0, 700, lt, tau - 0.2, dur=0.25, frm="up")
        if lt >= tau:
            light_hit(layer, cx0, 700, t, T_AUTO, PINK)

    elif name == "breakdown":
        # HERO: 99% of what you need + the five fields
        draw_code_rain(layer, lt, n=20, col=NEON)
        ticker(layer, "  IN THIS VIDEO  ·  99% OF WHAT YOU NEED TO KNOW  ·  FIVE FIELDS IN A BUSINESS  ·  ", 880, lt,
               fill=NEON + (110,))
        tb, t99, tk, t5, tfi = r(T_BREAK), r(T_99), r(T_KNOW), r(T_FIVE), r(T_FIELDS)
        place(layer, big_text_card("IN THIS VIDEO", NEON, fsz=56, w=800, h=130), 560, 70, lt, -0.35, dur=0.01,
              scale_pop=True)
        if lt < t5 - 0.06:
            if lt >= t99:
                p = clamp01((lt - t99) / 0.9)
                val = int(round(99 * (1 - (1 - p) ** 3)))
                place(layer, big_num(f"{val}%", NEON, 280), 520, 400, lt, t99, dur=0.2, scale_pop=True, idle=0,
                      exit_at=t5 - 0.06)
                light_hit(layer, 520, 420, t, T_99, NEON)
                light_rays(layer, 520, 420, t, NEON, a=16)
                place(layer, chip("of what you need to know", NEON, fsz=32), 520, 640, lt, t99 + 0.3, frm="down",
                      exit_at=t5 - 0.06)
            place(layer, viktor_badge(260), 1200, 360, lt, tb, dur=0.25, scale_pop=True, idle=0, exit_at=t5 - 0.06)
            if lt >= tk:
                place(layer, chip("everything about Viktor", VIOLET, fsz=30), 1200, 560, lt, tk, frm="down",
                      exit_at=t5 - 0.06)
        else:
            place(layer, big_num("5 FIELDS", NEON, 130), 1260, 80, lt, t5, dur=0.25, scale_pop=True, idle=0)
            place(layer, chip("in a business Viktor can be used for", NEON, fsz=30), 780, 700, lt, t5 + 0.3, frm="down")
            light_hit(layer, 1260, 90, t, T_FIVE, NEON)
            for k in range(5):
                on = lt >= tfi + k * 0.25
                place(layer, field_tile(k + 1, on, w=250, h=250), 180 + k * 300, 440, lt, t5 + k * 0.1, dur=0.25,
                      frm=("up", "down")[k % 2], scale_pop=True, idle=0)
            if lt >= tfi:
                light_hit(layer, 780, 440, t, T_FIELDS, NEON)

    elif name == "fields":
        # SOLO (logo slate in the source): the five fields board, full width
        draw_code_rain(layer, lt, n=24, col=NEON)
        place(layer, viktor_badge(200), 200, 150, lt, -0.3, dur=0.01, idle=0)
        place(layer, big_num("5 FIELDS VIKTOR CAN RUN", WHITE, 110), 1000, 150, lt, -0.3, dur=0.01, idle=0)
        for k in range(5):
            x = 200 + k * 360
            place(layer, field_tile(k + 1, True, w=300, h=300), x, 520, lt, -0.3 + k * 0.08, dur=0.25,
                  frm=("up", "down")[k % 2], idle=0)
        light_hit(layer, 920, 520, t, a, NEON)
        ticker(layer, "  FIVE FIELDS IN A BUSINESS  ·  ALL BROKEN DOWN IN THIS VIDEO  ·  ", 860, lt, fill=NEON + (140,))

    elif name == "bigdeal":
        draw_code_rain(layer, lt, n=14, col=PINK)
        layer.alpha_composite(ghost_img("BIGGER DEAL", 140, lw), (-60 + int(30 * math.sin(lt * 0.6)), 0))
        ticker(layer, "  A BIGGER DEAL THAN I CAN PAINT  ·  SOLO ENTREPRENEUR  ·  AI AGENCY  ·  ", 850, lt,
               fill=PINK + (110,))
        tbg, tin, ten = r(T_BIGGER), r(T_INDIV), r(T_ENTRE)
        place(layer, big_text_card("A BIGGER DEAL THAN IT LOOKS", PINK, fsz=54, w=1000, h=126), cx0, 70, lt, -0.35,
              dur=0.01, scale_pop=True)
        front_gif(gif_card("bigdeal", max(0, lt - tbg), w=560, frame="round"), 340, 380, lt, tbg, **entrance(6))
        if lt >= tbg:
            light_hit(layer, 340, 380, t, T_BIGGER, PINK)
        if lt >= tin:
            place(layer, avatar("K", PINK, 190), 880, 330, lt, tin, dur=0.25, scale_pop=True, idle=0)
            place(layer, chip("1 person", PINK, fsz=32), 880, 480, lt, tin + 0.1, frm="down")
            light_hit(layer, 880, 330, t, T_INDIV, PINK)
        if lt >= ten:
            place(layer, stamp_card("SOLO FOUNDER", PINK, fsz=60, w=520, h=130), 560, 680, lt, ten, dur=0.2, tilt=-5,
                  scale_pop=True, idle=0)
            light_hit(layer, 560, 680, t, T_ENTRE, PINK)
        guarded_conveyor(layer, 820, lt, STACK, conveyor_marks, name="stack-b", speed=170, gap=22)

    elif name == "onboard":
        draw_code_rain(layer, lt, n=14, col=CYAN)
        ticker(layer, "  THE CONFIDENCE  ·  TO WORK WITH BIG COMPANIES  ·  ONBOARD MORE THAN EVER  ·  ", 850, lt,
               fill=CYAN + (110,))
        tco, tbc, ton, tbe = r(T_CONF), r(T_BIGCO2), r(T_ONBOARD), r(T_BEFORE)
        place(layer, big_text_card("ONBOARD MORE COMPANIES", CYAN, fsz=56, w=1000, h=130), cx0, 70, lt, -0.35, dur=0.01,
              scale_pop=True)
        place(layer, chip("the confidence", CYAN, fsz=32), 240, 210, lt, tco, frm="left")
        if lt >= tco:
            light_hit(layer, 240, 210, t, T_CONF, CYAN)
        # company grid grows on "onboard"
        n_on = 0 if lt < ton else min(24, int((lt - ton) / 0.07) + 1)
        base = 2 if lt >= tbc else 0
        for i in range(max(base, n_on + base)):
            col = i % 8
            row = i // 8
            x = 130 + col * 125
            y = 360 + row * 130
            c = CYAN if i >= base else SILVER
            place(layer, building(c, 110), x, y, lt, (tbc if i < base else ton + (i - base) * 0.07), dur=0.18,
                  scale_pop=True, idle=0)
        if lt >= ton:
            light_hit(layer, cx0, 480, t, T_ONBOARD, CYAN)
            place(layer, stamp_card("MORE THAN EVER", CYAN, fsz=62, w=600, h=140), 800, 760, lt, tbe - 0.3, dur=0.2,
                  tilt=5, scale_pop=True, idle=0)
        if lt >= tbe:
            light_hit(layer, 800, 760, t, T_BEFORE, CYAN)

    elif name == "timesaver":
        draw_code_rain(layer, lt, n=16, col=NEON)
        ticker(layer, "  MASSIVE TIME SAVER  ·  MASSIVE TIME SAVER  ·  ", 850, lt, fill=NEON + (110,))
        tma, tti = r(T_MASSIVE), r(T_TIME)
        place(layer, stamp_card("MASSIVE TIME SAVER", NEON, fsz=76, w=900, h=170), cx0, 160, lt, tma, dur=0.2, tilt=-4,
              scale_pop=True, idle=0)
        light_hit(layer, cx0, 160, t, T_MASSIVE, NEON)
        light_rays(layer, cx0, 160, t, NEON, a=16)
        front_gif(gif_card("fast", max(0, lt - tti), w=560, frame="round"), 340, 520, lt, tti, **entrance(7))
        # clock hand spinning fast
        d = ImageDraw.Draw(layer)
        ccx, ccy, rr = 880, 520, 150
        if lt >= tti:
            d.ellipse([ccx - rr, ccy - rr, ccx + rr, ccy + rr], fill=GRAPHITE + (255,), outline=NEON + (255,), width=8)
            for k in range(12):
                ang = 2 * math.pi * k / 12
                d.line([ccx + (rr - 22) * math.cos(ang), ccy + (rr - 22) * math.sin(ang),
                        ccx + (rr - 8) * math.cos(ang), ccy + (rr - 8) * math.sin(ang)], fill=SILVER + (255,), width=4)
            ang = (lt - tti) * 9 - math.pi / 2
            d.line([ccx, ccy, ccx + (rr - 30) * math.cos(ang), ccy + (rr - 30) * math.sin(ang)], fill=NEON + (255,), width=8)
            d.line([ccx, ccy, ccx + (rr - 70) * math.cos(ang / 12), ccy + (rr - 70) * math.sin(ang / 12)],
                   fill=WHITE + (255,), width=10)
            d.ellipse([ccx - 12, ccy - 12, ccx + 12, ccy + 12], fill=NEON + (255,))
            light_hit(layer, ccx, ccy, t, T_TIME, NEON)

    elif name == "clients":
        draw_code_rain(layer, lt, n=12, col=CYAN)
        ticker(layer, "  CLIENTS JUST TEXT IT  ·  IT GOES AND DOES THE WORK  ·  ", 870, lt, fill=CYAN + (110,))
        tr, tx, td, tw = r(T_RECEIVE), r(T_TEXT), r(T_DO), r(T_WANT)
        place(layer, big_text_card("CLIENTS JUST TEXT IT", CYAN, fsz=56, w=1000, h=130), cx0, 70, lt, -0.35, dur=0.01,
              scale_pop=True)
        msgs = [(0.0, "Client · Owner", "J", ORANGE, "can you pull last week's leads?", False),
                (1.0, "Viktor", "V", VIOLET, "On it. 48 leads → sheet + CRM ✓", True),
                (2.4, "Client · Owner", "J", ORANGE, "and email the hot ones a follow up", False),
                (3.6, "Viktor", "V", VIOLET, "Sent 12 follow ups. Replies → #sales ✓", True)]
        place(layer, chat_card(lt - tx + 1.0, msgs, title="# client-acme", w=820, h=500), 470, 460, lt, tr, dur=0.25,
              frm="left")
        if lt >= tr:
            light_hit(layer, 470, 460, t, T_RECEIVE, CYAN)
        if lt >= tx:
            place(layer, chip("via text", CYAN, fsz=32), 1000, 300, lt, tx, frm="right")
            light_hit(layer, 1000, 300, t, T_TEXT, CYAN)
        if lt >= td:
            place(layer, stamp_card("DONE!", NEON, fsz=64, w=280, h=130), 1000, 520, lt, td, dur=0.2, tilt=8,
                  scale_pop=True, idle=0)
            light_hit(layer, 1000, 520, t, T_DO, NEON)

    elif name == "employee":
        draw_code_rain(layer, lt, n=16, col=VIOLET)
        layer.alpha_composite(ghost_img("AI EMPLOYEE", 140, lw), (-60 + int(30 * math.sin(lt * 0.6)), 0))
        ticker(layer, "  THINK OF IT AS  ·  THE FIRST AI EMPLOYEE HIRE  ·  ", 850, lt, fill=VIOLET + (110,))
        tf, te, th = r(T_FIRST2), r(T_EMPLOYEE), r(T_HIRE)
        place(layer, big_text_card("THE FIRST AI EMPLOYEE", VIOLET, fsz=56, w=1000, h=130), cx0, 70, lt, -0.35,
              dur=0.01, scale_pop=True)
        place(layer, id_badge(460, 580), 320, 500, lt, te - 0.1, dur=0.3, frm="down", scale_pop=True, idle=0)
        if lt >= te:
            light_hit(layer, 320, 500, t, T_EMPLOYEE, VIOLET)
        if lt < th:
            place(layer, chip("think of this AI as...", VIOLET, fsz=30), 860, 300, lt, -0.3, dur=0.01, frm="right")
        else:
            front_gif(gif_card("newjob", max(0, lt - th), w=440, frame="round"), 860, 420, lt, th, **entrance(0))
            light_hit(layer, 860, 420, t, T_HIRE, VIOLET)
            place(layer, chip("hire #1", NEON, fsz=32), 860, 700, lt, th + 0.15, frm="down")

    else:  # close — FULL, the one-line takeaway
        to, tai, tms = r(T_ONBOARDING), r(T_AIEMP), r(T_MSG)
        bloom_orb(layer, 1600, 240, 180, VIOLET, a=60)
        place(layer, viktor_badge(240), 1600, 240, lt, -0.3, dur=0.01, idle=0)
        place(layer, chip("onboarding your first", VIOLET, fsz=32), 1600, 420, lt, to, frm="right")
        if lt >= tai:
            place(layer, wordmark("AI EMPLOYEE", WHITE, 110), 1600, 540, lt, tai, dur=0.25, scale_pop=True, idle=0)
            light_hit(layer, 1600, 540, t, T_AIEMP, VIOLET)
            light_rays(layer, 1600, 540, t, VIOLET, a=16)
        if lt >= tms:
            for k, s in enumerate(("slack", "gmail", "notion")):
                place(layer, tile(s, 130), 1450 + k * 150, 760, lt, tms + k * 0.08, dur=0.2, scale_pop=True, idle=0)
            light_hit(layer, 1600, 760, t, T_MSG, VIOLET)


if __name__ == "__main__":
    run(SECT, scene,
        punch_words=["nightmare", "hack", "integrates", "slack", "99%", "onboard", "hire"],
        extra_hits=[T_NIGHT, T_VIK, T_99, T_SLACK, T_HIRE],
        keywords=KEYWORDS, key_col=KEY_COL, out=OUT)
