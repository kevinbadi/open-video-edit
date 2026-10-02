#!/usr/bin/env node
/**
 * capture_page.mjs: screenshot a real article / doc / tweet for Fireship-style B-roll, with the
 * orange highlighter applied IN THE PAGE (so it wraps real text perfectly) and an optional
 * "clean" pass that hides cookie banners, navbars and ads.
 *
 *   node capture_page.mjs --url <url> --out assets/shots/meta-post.png \
 *     [--selector "article"] [--highlight "phrase one" --highlight "phrase two"] \
 *     [--width 1400] [--scale 2] [--dark] [--boxes assets/shots/meta-post.boxes.json]
 *
 * --boxes writes the highlighted text rects (image px) so the engine's highlight_image()
 * can SWEEP the highlight in on the spoken words instead of showing it pre-filled: capture
 * once WITHOUT --highlight for the base image, once WITH --boxes for the rects.
 * Needs: npm i playwright (Chromium already cached under ~/Library/Caches/ms-playwright).
 */
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const get = (k, d) => { const i = args.indexOf(`--${k}`); return i >= 0 ? args[i + 1] : d; };
const all = (k) => args.flatMap((a, i) => (a === `--${k}` ? [args[i + 1]] : []));
const url = get("url");
const out = get("out");
if (!url || !out) { console.error("usage: --url <url> --out <png> [--selector css] [--highlight text]... [--boxes json]"); process.exit(1); }
const width = Number(get("width", 1400));
const scale = Number(get("scale", 2));
const selector = get("selector", "");
const highlights = all("highlight");
const boxesOut = get("boxes", "");

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width, height: 1000 }, deviceScaleFactor: scale,
  colorScheme: args.includes("--dark") ? "dark" : "light",
  userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
});
const page = await ctx.newPage();
await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
await page.waitForTimeout(2500);
// clean pass: banners, sticky headers, ads, modals
await page.addStyleTag({ content: `
  [id*="cookie" i],[class*="cookie" i],[class*="consent" i],[id*="consent" i],[class*="newsletter" i],
  [class*="modal" i],[class*="popup" i],[class*="banner" i][class*="ad" i],iframe[src*="ads"],
  header[class*="sticky" i],[class*="paywall" i]{display:none!important}
  mark.fs-hl{background:#f7a458!important;color:inherit!important;padding:0 1px;border-radius:2px}` });
if (highlights.length) {
  await page.evaluate(([phrases, sel]) => {
    // Match across text nodes (links / <b> split a sentence into several nodes): build one
    // whitespace-normalised string with per-char node offsets, find the phrase, wrap each piece.
    const root = (sel && document.querySelector(sel)) || document.body;
    for (const phrase of phrases) {
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      let flat = "", map = [], prevSpace = true;
      while (walker.nextNode()) {
        const n = walker.currentNode;
        for (let i = 0; i < n.nodeValue.length; i++) {
          const ch = n.nodeValue[i];
          const sp = /\s/.test(ch);
          if (sp && prevSpace) continue;
          flat += sp ? " " : ch.toLowerCase(); map.push([n, i]); prevSpace = sp;
        }
      }
      const q = phrase.toLowerCase().replace(/\s+/g, " ").trim();
      const at = flat.indexOf(q);
      if (at < 0) { console.log("highlight not found:", phrase); continue; }
      const pieces = new Map();
      for (let k = at; k < at + q.length; k++) {
        const [n, i] = map[k];
        const cur = pieces.get(n) || [i, i];
        pieces.set(n, [Math.min(cur[0], i), Math.max(cur[1], i)]);
      }
      for (const [n, [a, b]] of pieces) {
        const r = document.createRange();
        r.setStart(n, a); r.setEnd(n, b + 1);
        const m = document.createElement("mark"); m.className = "fs-hl";
        try { r.surroundContents(m); } catch {}
      }
    }
  }, [highlights, selector]);
}
const target = selector ? page.locator(selector).first() : null;
fs.mkdirSync(path.dirname(out), { recursive: true });
if (target) await target.screenshot({ path: out });
else await page.screenshot({ path: out });
if (boxesOut) {
  const origin = target ? await target.boundingBox() : { x: 0, y: 0 };
  const rects = await page.evaluate(() => [...document.querySelectorAll("mark.fs-hl")].flatMap((m) =>
    [...m.getClientRects()].map((r) => [r.left, r.top, r.right, r.bottom])));
  const boxes = rects.map(([l, t, r, b]) => [l - origin.x, t - origin.y, r - origin.x, b - origin.y].map((v) => Math.round(v * scale)));
  fs.writeFileSync(boxesOut, JSON.stringify(boxes));
  console.log(`✓ ${boxes.length} highlight boxes -> ${boxesOut}`);
}
console.log(`✓ ${out}`);
await browser.close();
