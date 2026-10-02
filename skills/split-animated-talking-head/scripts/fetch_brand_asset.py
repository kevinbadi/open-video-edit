#!/usr/bin/env python3
"""Download a product/tool logo or social card into assets/logos or assets/shots.

Tries, in order: explicit URL, GitHub avatar, GitHub OpenGraph card, Wikimedia
Special:FilePath, Google s2 favicon, jsDelivr simple-icons SVG (converted with
macOS qlmanage when present).

Usage (from projects/<slug>-animated/):
  python3 .../fetch_brand_asset.py --name claude --domain claude.ai
  python3 .../fetch_brand_asset.py --name gitnexus --github abhigyanpatwari/GitNexus
  python3 .../fetch_brand_asset.py --name omniroute --url https://example.com/logo.png
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import urllib.request

UA = "Mozilla/5.0 (compatible; CreatorOS-split-animated/1.0)"


# Bundled Claude marks live in this skill. Never fetch a generic favicon
# for Claude / Opus / Sonnet / Haiku / Fable / Claude Code / Anthropic.
_HERE = os.path.dirname(os.path.abspath(__file__))
_BUNDLED_ASSETS = os.path.abspath(os.path.join(_HERE, "..", "assets"))
_CLAUDE_BUNDLED = {
    "claude": "claude-sphinx.png",
    "anthropic": "claude-sphinx.png",
    "opus": "claude-sphinx.png",
    "sonnet": "claude-sphinx.png",
    "haiku": "claude-sphinx.png",
    "fable": "claude-invader.png",
    "claude-code": "claude-invader.png",
    "claudecode": "claude-invader.png",
    "claude-invader": "claude-invader.png",
    "claude-sphinx": "claude-sphinx.png",
}


def _copy_bundled_claude(name: str, dest: str) -> bool:
    src_name = _CLAUDE_BUNDLED.get((name or "").strip().lower())
    if not src_name:
        return False
    src = os.path.join(_BUNDLED_ASSETS, src_name)
    if not os.path.isfile(src):
        return False
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    import shutil
    shutil.copy2(src, dest)
    print(f"ok {dest} <- bundled {src_name}")
    return True


def fetch(url: str, dest: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        if not data or len(data) < 80:
            return False
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        open(dest, "wb").write(data)
        print(f"ok {dest} ({len(data)} bytes) <- {url}")
        return True
    except Exception as e:
        print(f"skip {url}: {e}")
        return False


def svg_to_png(svg: str, png: str, size: int = 512) -> bool:
    if not os.path.isfile(svg):
        return False
    outdir = os.path.dirname(os.path.abspath(png)) or "."
    try:
        subprocess.run(
            ["qlmanage", "-t", "-s", str(size), "-o", outdir, svg],
            check=True, capture_output=True,
        )
        produced = os.path.join(outdir, os.path.basename(svg) + ".png")
        if os.path.isfile(produced):
            os.replace(produced, png)
            print(f"converted {svg} -> {png}")
            return True
    except Exception as e:
        print(f"svg convert failed: {e}")
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="slug, written as assets/logos/<name>.png")
    ap.add_argument("--domain", default=None)
    ap.add_argument("--github", default=None, help="owner/repo or owner (avatar)")
    ap.add_argument("--wikimedia", default=None, help="File:Name.svg on Commons")
    ap.add_argument("--simpleicon", default=None, help="simple-icons slug e.g. github")
    ap.add_argument("--url", default=None, help="direct image URL")
    ap.add_argument("--shot", action="store_true", help="write to assets/shots instead of logos")
    args = ap.parse_args()
    folder = "assets/shots" if args.shot else "assets/logos"
    os.makedirs(folder, exist_ok=True)
    dest = os.path.join(folder, f"{args.name}.png")
    svg_tmp = os.path.join(folder, f"{args.name}.svg")

    if _copy_bundled_claude(args.name, dest):
        # Always also drop the pair so choreography can dance the invader
        # and badge the sphinx in the same video.
        _copy_bundled_claude("claude-invader", os.path.join(folder, "claude-invader.png"))
        _copy_bundled_claude("claude-sphinx", os.path.join(folder, "claude-sphinx.png"))
        return

    if args.url and fetch(args.url, dest):
        return
    if args.github:
        gh = args.github.strip("/")
        if "/" in gh:
            if fetch(f"https://opengraph.githubassets.com/1/{gh}", os.path.join("assets/shots", f"{args.name}.png")):
                pass
            owner = gh.split("/")[0]
            fetch(f"https://github.com/{owner}.png?size=240", dest)
        else:
            fetch(f"https://github.com/{gh}.png?size=240", dest)
        if os.path.isfile(dest):
            return
    if args.wikimedia:
        name = args.wikimedia.replace("File:", "").replace(" ", "_")
        if fetch(f"https://commons.wikimedia.org/wiki/Special:FilePath/{name}", svg_tmp):
            if svg_to_png(svg_tmp, dest):
                return
    if args.simpleicon:
        url = f"https://cdn.jsdelivr.net/npm/simple-icons@v13/icons/{args.simpleicon}.svg"
        if fetch(url, svg_tmp) and svg_to_png(svg_tmp, dest):
            return
    if args.domain:
        if fetch(f"https://www.google.com/s2/favicons?domain={args.domain}&sz=256", dest):
            return
    sys.exit(f"could not fetch a mark for {args.name}")


if __name__ == "__main__":
    main()
