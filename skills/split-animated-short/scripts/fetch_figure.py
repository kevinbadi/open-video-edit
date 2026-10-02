#!/usr/bin/env python3
"""Source real portraits of notable figures for a spoken niche / company so
viewers who recognize them lock in (Kevin 2026-09-05).

"Claude" → Anthropic founders, "SpaceX" → Musk + Shotwell, "OpenAI" →
Altman / Brockman / Sutskever, "marketing" → GaryVee / Godin / Hormozi,
"business" / "sales" → Buffett / Bezos / Cardone / Belfort ... Every niche
below is a curated, ordered list; the first 2–4 are the ones people know.

Sources, in order: Wikipedia REST summary (Commons original image, free
license) → Wikidata P18 → unavatar.io X avatar (public profile picture) for
people with no Wikipedia photo. Faces are detected (Haar) and square-cropped
head-and-shoulders so every portrait fits a round badge or a portrait card.

Writes assets/figures/<slug>.png (600x600 RGBA) + assets/figures/<slug>.json
{name, role, org, niche, source, credit}.

Usage (from projects/<slug>-animated/):
  python3 .../fetch_figure.py --list
  python3 .../fetch_figure.py --niche claude            # all Anthropic founders
  python3 .../fetch_figure.py --niche openai --top 3    # the 3 most-known
  python3 .../fetch_figure.py --name "Alex Hormozi" --x AlexHormozi --role "Acquisition.com"
  python3 .../fetch_figure.py --name "Jensen Huang" --wiki Jensen_Huang --role "NVIDIA CEO"
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request

UA = f"open-video-edit/1.0 (contact: {os.environ.get('OVE_CONTACT', 'https://github.com/kevinbadi/open-video-edit')})"

# niche → ordered figures. Keys are lowercase; ALIASES map spoken words here.
# Fields: name, wiki (Wikipedia title), x (X/Twitter handle fallback), role.
NICHES: dict[str, list[dict]] = {
    "claude": [
        {"name": "Dario Amodei", "wiki": "Dario_Amodei", "x": "DarioAmodei", "role": "Anthropic CEO & co-founder"},
        {"name": "Daniela Amodei", "wiki": "Daniela_Amodei", "x": "DanielaAmodei", "role": "Anthropic President & co-founder"},
        {"name": "Jack Clark", "wiki": "Jack_Clark_(journalist)", "x": "jackclarkSF", "role": "Anthropic co-founder"},
        {"name": "Jared Kaplan", "wiki": "Jared_Kaplan", "x": "jaredkaplan", "role": "Anthropic co-founder, CSO"},
        {"name": "Chris Olah", "wiki": "Chris_Olah", "x": "ch402", "role": "Anthropic co-founder"},
        {"name": "Tom Brown", "wiki": None, "x": "nottombrown", "role": "Anthropic co-founder"},
    ],
    "spacex": [
        {"name": "Elon Musk", "wiki": "Elon_Musk", "x": "elonmusk", "role": "SpaceX founder & CEO"},
        {"name": "Gwynne Shotwell", "wiki": "Gwynne_Shotwell", "x": None, "role": "SpaceX President & COO"},
        {"name": "Tom Mueller", "wiki": "Tom_Mueller", "x": "lrocket", "role": "SpaceX founding engineer"},
    ],
    "openai": [
        {"name": "Sam Altman", "wiki": "Sam_Altman", "x": "sama", "role": "OpenAI CEO & co-founder"},
        {"name": "Greg Brockman", "wiki": "Greg_Brockman", "x": "gdb", "role": "OpenAI President & co-founder"},
        {"name": "Ilya Sutskever", "wiki": "Ilya_Sutskever", "x": "ilyasut", "role": "OpenAI co-founder"},
        {"name": "Mira Murati", "wiki": "Mira_Murati", "x": "miramurati", "role": "former OpenAI CTO"},
        {"name": "Wojciech Zaremba", "wiki": "Wojciech_Zaremba", "x": "woj_zaremba", "role": "OpenAI co-founder"},
        {"name": "John Schulman", "wiki": "John_Schulman", "x": "johnschulman2", "role": "OpenAI co-founder"},
    ],
    "marketing": [
        {"name": "Gary Vaynerchuk", "wiki": "Gary_Vaynerchuk", "x": "garyvee", "role": "VaynerMedia"},
        {"name": "Alex Hormozi", "wiki": "Alex_Hormozi", "x": "AlexHormozi", "role": "Acquisition.com"},
        {"name": "Seth Godin", "wiki": "Seth_Godin", "x": "ThisIsSethsBlog", "role": "author, Purple Cow"},
        {"name": "Neil Patel", "wiki": "Neil_Patel_(marketer)", "x": "neilpatel", "role": "NP Digital"},
        {"name": "Russell Brunson", "wiki": "Russell_Brunson", "x": "russellbrunson", "role": "ClickFunnels"},
        {"name": "Philip Kotler", "wiki": "Philip_Kotler", "x": None, "role": "father of modern marketing"},
        {"name": "David Ogilvy", "wiki": "David_Ogilvy_(businessman)", "x": None, "role": "father of advertising"},
    ],
    "business": [
        {"name": "Warren Buffett", "wiki": "Warren_Buffett", "x": "WarrenBuffett", "role": "Berkshire Hathaway"},
        {"name": "Jeff Bezos", "wiki": "Jeff_Bezos", "x": "JeffBezos", "role": "Amazon founder"},
        {"name": "Steve Jobs", "wiki": "Steve_Jobs", "x": None, "role": "Apple co-founder"},
        {"name": "Elon Musk", "wiki": "Elon_Musk", "x": "elonmusk", "role": "Tesla, SpaceX, xAI"},
        {"name": "Mark Cuban", "wiki": "Mark_Cuban", "x": "mcuban", "role": "Shark Tank investor"},
        {"name": "Alex Hormozi", "wiki": "Alex_Hormozi", "x": "AlexHormozi", "role": "Acquisition.com"},
        {"name": "Naval Ravikant", "wiki": "Naval_Ravikant", "x": "naval", "role": "AngelList founder"},
        {"name": "Codie Sanchez", "wiki": "Codie_Sanchez", "x": "Codie_Sanchez", "role": "Contrarian Thinking"},
        {"name": "Dan Martell", "wiki": "Dan_Martell", "x": "danmartell", "role": "SaaS Academy"},
        {"name": "Peter Thiel", "wiki": "Peter_Thiel", "x": "peterthiel", "role": "PayPal co-founder"},
    ],
    "sales": [
        {"name": "Grant Cardone", "wiki": "Grant_Cardone", "x": "GrantCardone", "role": "10X, Cardone Capital"},
        {"name": "Jordan Belfort", "wiki": "Jordan_Belfort", "x": "wolfofwallst", "role": "Wolf of Wall Street"},
        {"name": "Alex Hormozi", "wiki": "Alex_Hormozi", "x": "AlexHormozi", "role": "$100M Offers"},
        {"name": "Zig Ziglar", "wiki": "Zig_Ziglar", "x": None, "role": "sales legend"},
        {"name": "Brian Tracy", "wiki": "Brian_Tracy", "x": "BrianTracy", "role": "Psychology of Selling"},
        {"name": "Tony Robbins", "wiki": "Tony_Robbins", "x": "TonyRobbins", "role": "peak performance"},
    ],
    "google": [
        {"name": "Sundar Pichai", "wiki": "Sundar_Pichai", "x": "sundarpichai", "role": "Google CEO"},
        {"name": "Larry Page", "wiki": "Larry_Page", "x": None, "role": "Google co-founder"},
        {"name": "Sergey Brin", "wiki": "Sergey_Brin", "x": None, "role": "Google co-founder"},
        {"name": "Demis Hassabis", "wiki": "Demis_Hassabis", "x": "demishassabis", "role": "Google DeepMind CEO"},
    ],
    "nvidia": [
        {"name": "Jensen Huang", "wiki": "Jensen_Huang", "x": None, "role": "NVIDIA founder & CEO"},
    ],
    "meta": [
        {"name": "Mark Zuckerberg", "wiki": "Mark_Zuckerberg", "x": None, "role": "Meta founder & CEO"},
    ],
    "microsoft": [
        {"name": "Satya Nadella", "wiki": "Satya_Nadella", "x": "satyanadella", "role": "Microsoft CEO"},
        {"name": "Bill Gates", "wiki": "Bill_Gates", "x": "BillGates", "role": "Microsoft co-founder"},
    ],
    "apple": [
        {"name": "Steve Jobs", "wiki": "Steve_Jobs", "x": None, "role": "Apple co-founder"},
        {"name": "Tim Cook", "wiki": "Tim_Cook", "x": "tim_cook", "role": "Apple CEO"},
    ],
    "tesla": [
        {"name": "Elon Musk", "wiki": "Elon_Musk", "x": "elonmusk", "role": "Tesla CEO"},
    ],
    "amazon": [
        {"name": "Jeff Bezos", "wiki": "Jeff_Bezos", "x": "JeffBezos", "role": "Amazon founder"},
        {"name": "Andy Jassy", "wiki": "Andy_Jassy", "x": "ajassy", "role": "Amazon CEO"},
    ],
    "xai": [
        {"name": "Elon Musk", "wiki": "Elon_Musk", "x": "elonmusk", "role": "xAI founder"},
    ],
}

ALIASES = {
    "anthropic": "claude", "claude code": "claude", "opus": "claude", "sonnet": "claude",
    "haiku": "claude", "fable": "claude",
    "chatgpt": "openai", "gpt": "openai", "chat gpt": "openai", "sora": "openai",
    "starship": "spacex", "starlink": "spacex", "falcon": "spacex",
    "marketer": "marketing", "marketers": "marketing", "ads": "marketing", "advertising": "marketing",
    "entrepreneur": "business", "entrepreneurs": "business", "founder": "business",
    "founders": "business", "ceo": "business", "money": "business", "investing": "business",
    "selling": "sales", "closing": "sales", "closer": "sales", "sell": "sales",
    "gemini": "google", "deepmind": "google", "youtube": "google",
    "facebook": "meta", "instagram": "meta", "llama": "meta",
    "grok": "xai", "iphone": "apple", "aws": "amazon", "copilot": "microsoft", "openai founders": "openai",
}


def resolve_niche(word: str) -> str | None:
    w = (word or "").strip().lower()
    if w in NICHES:
        return w
    return ALIASES.get(w)


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def http(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def wiki_image(title: str) -> tuple[str, str] | None:
    """(image_url, credit) from the Wikipedia REST summary, or None."""
    try:
        j = json.loads(http("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title)))
    except Exception:
        return None
    src = (j.get("originalimage") or {}).get("source") or (j.get("thumbnail") or {}).get("source")
    if not src:
        return None
    return src, f"Wikipedia/Wikimedia Commons ({j.get('title') or title})"


def _small(url: str, min_px: int = 400) -> bool:
    """True when a Wikipedia originalimage is under min_px wide (reads the
    REST summary width via the URL's page; cheap: one HEAD-less GET of bytes)."""
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(http(url, timeout=30)))
        return min(im.size) < min_px
    except Exception:
        return False


def wikidata_image(name: str) -> tuple[str, str] | None:
    try:
        q = urllib.parse.quote(name)
        j = json.loads(http(f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={q}&language=en&format=json&limit=1"))
        hits = j.get("search") or []
        if not hits:
            return None
        qid = hits[0]["id"]
        e = json.loads(http(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"))
        claims = e["entities"][qid].get("claims", {})
        p18 = claims.get("P18")
        if not p18:
            return None
        fname = p18[0]["mainsnak"]["datavalue"]["value"].replace(" ", "_")
        return (f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(fname)}?width=1200",
                f"Wikimedia Commons ({fname})")
    except Exception:
        return None


def x_avatar(handle: str) -> tuple[str, str] | None:
    for svc in ("x", "twitter"):
        url = f"https://unavatar.io/{svc}/{handle}?fallback=false"
        try:
            data = http(url, timeout=25)
            if len(data) > 2000:
                return url, f"X profile photo (@{handle})"
        except Exception:
            continue
    return None


def face_square(img_bytes: bytes, out_size: int = 600) -> "Image.Image":
    """Square head-and-shoulders crop around the largest detected face."""
    import numpy as np
    import cv2
    from PIL import Image, ImageOps

    im = Image.open(io.BytesIO(img_bytes))
    im = ImageOps.exif_transpose(im).convert("RGB")
    w, h = im.size
    arr = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(max(24, w // 20), max(24, h // 20)))
    if len(faces):
        x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
        cx, cy = x + fw / 2, y + fh * 0.5
        side = int(max(fw, fh) * 2.3)
    else:
        cx, cy = w / 2, h * 0.38
        side = int(min(w, h) * 0.9)
    side = max(64, min(side, min(w, h)))
    x0 = int(min(max(0, cx - side / 2), w - side))
    y0 = int(min(max(0, cy - side * 0.48), h - side))
    crop = im.crop((x0, y0, x0 + side, y0 + side)).resize((out_size, out_size), Image.LANCZOS)
    return crop.convert("RGBA")


def fetch_one(fig: dict, niche: str | None, out: str, force: bool = False) -> bool:
    slug = slugify(fig["name"])
    png = os.path.join(out, f"{slug}.png")
    meta_p = os.path.join(out, f"{slug}.json")
    if os.path.isfile(png) and not force:
        print(f"have {png}")
        return True
    # Order: Wikipedia (free, recognizable) → X avatar (current, the face
    # people know from their feed) → Wikidata name search LAST: it matches by
    # name only and has returned the wrong "Tom Brown" (2026-09-05).
    found = None
    if fig.get("wiki"):
        found = wiki_image(fig["wiki"])
        # tiny Commons originals (<400px, e.g. Ilya / Altman) look muddy at
        # 600px — take the current X avatar instead when we have a handle.
        if found and fig.get("x") and _small(found[0]):
            alt = x_avatar(fig["x"])
            found = alt or found
    if not found and fig.get("x"):
        found = x_avatar(fig["x"])
    if not found:
        found = wikidata_image(fig["name"])
        if found:
            print(f"warn {fig['name']}: Wikidata name-match photo — eyeball it ({found[1]})")
    if not found:
        print(f"MISS {fig['name']} — no Wikipedia/Wikidata photo and no X avatar")
        return False
    url, credit = found
    try:
        data = http(url, timeout=60)
        im = face_square(data)
    except Exception as e:  # noqa: BLE001
        print(f"fail {fig['name']}: {e}")
        return False
    os.makedirs(out, exist_ok=True)
    im.save(png)
    json.dump({"name": fig["name"], "role": fig.get("role", ""), "org": fig.get("org", ""),
               "niche": niche, "source": url, "credit": credit, "slug": slug},
              open(meta_p, "w"), indent=2)
    print(f"ok {png} <- {credit}")
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--niche", action="append", default=[], help="claude | spacex | openai | marketing | business | sales | google | ... (repeatable; aliases ok)")
    ap.add_argument("--top", type=int, default=0, help="only the first N of the niche (0 = all)")
    ap.add_argument("--name", default=None, help="ad-hoc figure name")
    ap.add_argument("--wiki", default=None, help="Wikipedia title for --name")
    ap.add_argument("--x", default=None, help="X handle fallback for --name")
    ap.add_argument("--role", default="", help="role line under the name")
    ap.add_argument("--out", default="assets/figures")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--list", action="store_true", help="print the niche map and exit")
    args = ap.parse_args()

    if args.list:
        for k, figs in NICHES.items():
            print(f"{k:<10} " + ", ".join(f["name"] for f in figs))
        print("aliases:", ", ".join(sorted(ALIASES)))
        return

    ok = True
    if args.name:
        ok &= fetch_one({"name": args.name, "wiki": args.wiki, "x": args.x, "role": args.role}, None, args.out, args.force)
    for n in args.niche:
        key = resolve_niche(n)
        if not key:
            print(f"unknown niche {n!r} — add it to NICHES or use --name/--wiki/--x")
            ok = False
            continue
        figs = NICHES[key][: args.top] if args.top else NICHES[key]
        for fig in figs:
            ok &= fetch_one(fig, key, args.out, args.force)
    if not args.name and not args.niche:
        sys.exit("need --niche or --name (or --list)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
