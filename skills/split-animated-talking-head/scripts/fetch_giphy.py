#!/usr/bin/env python3
"""Pull a reaction GIF from Giphy (or the dashboard's favorited allow-list)
and explode it into a 30fps PNG frame bank the split renderer can play.

Reads GIPHY_API_KEY (and DATABASE_URL for --favorites) from
.env.local (repo or project root). Writes, per GIF:

  assets/gifs/<slug>.mp4              original Giphy mp4 rendition
  assets/gifs/<slug>/f0000.png ...    RGB frames at --fps (default 30)
  assets/gifs/<slug>/meta.json        id, title, query, fps, frames, w, h, dur

Usage (from projects/<slug>-animated/):
  # look before you pick — prints the top 10 with ids + sizes
  python3 .../fetch_giphy.py --query "mind blown" --list
  # take the best one (default pick 0) as assets/gifs/mind-blown/
  python3 .../fetch_giphy.py --query "mind blown" --slug mind-blown
  # a specific Giphy id
  python3 .../fetch_giphy.py --id 75ZaxapnyMp2w --slug mind-blown
  # curated dashboard favorites (gifs table) whose title/query/notes match
  python3 .../fetch_giphy.py --favorites --query "money" --slug money-rain --mark-used

Rules: max ~4s per GIF (--max-seconds), one GIF per beat, never as the hero
for >2.5s. GIFs are supporting reaction beats — the graphic still has to
match what is being said.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (compatible; CreatorOS-split-animated/1.0)"
HERE = os.path.dirname(os.path.abspath(__file__))


def find_env() -> dict:
    """Walk up from this script to the nearest .env.local and parse KEY=VALUE."""
    d = HERE
    for _ in range(8):
        p = os.path.join(d, ".env.local")
        if os.path.isfile(p):
            out = {}
            for line in open(p, encoding="utf-8"):
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
            return out
        d = os.path.dirname(d)
    return {}


ENV = {**find_env(), **os.environ}


def http_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))


def http_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def _map(g: dict) -> dict | None:
    img = g.get("images") or {}
    orig = img.get("original") or {}
    mp4 = orig.get("mp4") or (img.get("fixed_width") or {}).get("mp4") or ""
    if not g.get("id") or not mp4:
        return None
    return {
        "id": str(g["id"]),
        "title": str(g.get("title") or "GIF"),
        "mp4": mp4,
        "width": int(orig.get("width") or 0),
        "height": int(orig.get("height") or 0),
        "frames": int(orig.get("frames") or 0),
        "url": str(g.get("url") or ""),
    }


def giphy_search(q: str, limit: int = 12, rating: str = "pg-13") -> list[dict]:
    key = ENV.get("GIPHY_API_KEY")
    if not key:
        sys.exit("GIPHY_API_KEY not set (.env.local (repo or project root))")
    url = (
        "https://api.giphy.com/v1/gifs/search?api_key=" + key
        + "&q=" + urllib.parse.quote(q)
        + f"&limit={limit}&rating={rating}&bundle=messaging_non_clips"
    )
    j = http_json(url)
    return [m for m in (_map(g) for g in j.get("data", [])) if m]


def giphy_by_id(gid: str) -> dict:
    key = ENV.get("GIPHY_API_KEY")
    if not key:
        sys.exit("GIPHY_API_KEY not set (.env.local (repo or project root))")
    j = http_json(f"https://api.giphy.com/v1/gifs/{gid}?api_key={key}")
    m = _map(j.get("data") or {})
    if not m:
        sys.exit(f"giphy id {gid} returned no mp4")
    return m


def _pg_dsn(dsn: str) -> str:
    """Strip node-pg-only query params (uselibpqcompat, ...) that libpq rejects."""
    keep = {"sslmode", "sslrootcert", "sslcert", "sslkey", "application_name", "connect_timeout", "options"}
    u = urllib.parse.urlsplit(dsn)
    qs = [(k, v) for k, v in urllib.parse.parse_qsl(u.query) if k in keep]
    return urllib.parse.urlunsplit((u.scheme, u.netloc, u.path, urllib.parse.urlencode(qs), u.fragment))


def favorites(q: str | None) -> list[dict]:
    """Dashboard-favorited GIFs (gifs table), unchecked / least-used first."""
    dsn = ENV.get("DATABASE_URL")
    if not dsn:
        sys.exit("DATABASE_URL not set — cannot read favorites")
    try:
        import psycopg2  # type: ignore
    except ImportError:
        sys.exit("pip install psycopg2-binary for --favorites")
    sql = (
        "select id, title, mp4_url, query, coalesce(notes,''), checked, used_count "
        "from gifs order by checked asc, last_used_at asc nulls first, created_at desc"
    )
    with psycopg2.connect(_pg_dsn(dsn)) as conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    out = []
    for gid, title, mp4, query, notes, checked, used in rows:
        hay = f"{title} {query} {notes}".lower()
        if q and not all(tok in hay for tok in q.lower().split()):
            continue
        out.append({"id": gid, "title": title, "mp4": mp4, "width": 0, "height": 0,
                    "frames": 0, "url": "", "query": query, "checked": checked, "used": used})
    return out


def mark_used(gid: str) -> None:
    dsn = ENV.get("DATABASE_URL")
    if not dsn:
        return
    try:
        import psycopg2  # type: ignore
        with psycopg2.connect(_pg_dsn(dsn)) as conn, conn.cursor() as cur:
            cur.execute(
                "update gifs set checked = true, used_count = coalesce(used_count,0)+1, "
                "last_used_at = now() where id = %s", (gid,))
    except Exception as e:  # noqa: BLE001
        print(f"warn: could not mark used: {e}")


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:40] or "gif"


def explode(mp4_path: str, out_dir: str, fps: int, width: int, max_seconds: float) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        if f.endswith(".png"):
            os.remove(os.path.join(out_dir, f))
    vf = f"fps={fps},scale={width}:-2:flags=lanczos"
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", mp4_path, "-t", str(max_seconds),
           "-vf", vf, "-pix_fmt", "rgb24", os.path.join(out_dir, "f%04d.png")]
    subprocess.run(cmd, check=True)
    frames = sorted(f for f in os.listdir(out_dir) if f.endswith(".png"))
    if not frames:
        sys.exit("ffmpeg produced no frames")
    from PIL import Image
    w, h = Image.open(os.path.join(out_dir, frames[0])).size
    return {"fps": fps, "frames": len(frames), "width": w, "height": h,
            "duration": round(len(frames) / fps, 3)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default=None, help="Giphy search / favorites filter")
    ap.add_argument("--id", default=None, help="Giphy id (skips search)")
    ap.add_argument("--slug", default=None, help="assets/gifs/<slug>")
    ap.add_argument("--pick", type=int, default=0, help="index into results (default 0)")
    ap.add_argument("--list", action="store_true", help="print candidates and exit")
    ap.add_argument("--favorites", action="store_true", help="use dashboard-favorited gifs table")
    ap.add_argument("--mark-used", action="store_true", help="check off the favorite after fetching")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--width", type=int, default=720, help="frame width (even)")
    ap.add_argument("--max-seconds", type=float, default=4.0)
    ap.add_argument("--rating", default="pg-13")
    ap.add_argument("--out", default="assets/gifs")
    args = ap.parse_args()

    if args.id:
        cands = [giphy_by_id(args.id)]
    elif args.favorites:
        cands = favorites(args.query)
    elif args.query:
        cands = giphy_search(args.query, rating=args.rating)
    else:
        sys.exit("need --query, --id, or --favorites")

    if not cands:
        sys.exit("no candidates")
    if args.list:
        for i, c in enumerate(cands):
            dur = f"{c['frames'] / 12:.1f}s~" if c.get("frames") else "?"
            print(f"[{i}] {c['id']:<18} {c['width']}x{c['height']:<5} {dur:<6} {c['title']}")
        return

    c = cands[min(args.pick, len(cands) - 1)]
    slug = args.slug or slugify(args.query or c["title"])
    os.makedirs(args.out, exist_ok=True)
    mp4_path = os.path.join(args.out, f"{slug}.mp4")
    open(mp4_path, "wb").write(http_bytes(c["mp4"]))
    width = args.width - (args.width % 2)
    info = explode(mp4_path, os.path.join(args.out, slug), args.fps, width, args.max_seconds)
    meta = {"id": c["id"], "title": c["title"], "query": args.query, "source": "giphy",
            "giphy_url": c.get("url", ""), "mp4": mp4_path, **info}
    json.dump(meta, open(os.path.join(args.out, slug, "meta.json"), "w"), indent=2)
    if args.mark_used and args.favorites:
        mark_used(c["id"])
    print(f"ok assets/gifs/{slug}/  {info['frames']} frames @{args.fps}fps  "
          f"{info['width']}x{info['height']}  {info['duration']}s  <- {c['title']} ({c['id']})")


if __name__ == "__main__":
    main()
