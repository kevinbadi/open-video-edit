#!/usr/bin/env python3
"""Print every number the transcript says, with the counter it will get.

  python3 .../number_beats.py                # reads audio/words.json in cwd
  python3 .../number_beats.py path/to/words.json

Use it in step 6 when planning beats: every line here must appear on screen
as a counter_card (bespoke in the section, or via auto_counters)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "templates"))
from hyper_edits import number_beats, fmt_number  # noqa: E402

path = sys.argv[1] if len(sys.argv) > 1 else "audio/words.json"
words = json.load(open(path))
beats = number_beats(words)
if not beats:
    print("no numbers spoken")
for b in beats:
    print(f"{b['t']:6.2f}s  {fmt_number(b['value'], b['prefix'], b['suffix'], style=b.get('style','')):>10}  {b['label'] or '':<12} <- \"{b['raw']}\"")
