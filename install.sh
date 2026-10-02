#!/usr/bin/env bash
# Install the OPEN VIDEO EDIT skills.
#   ./install.sh                 -> ~/.claude/skills
#   ./install.sh /path/to/proj   -> /path/to/proj/.claude/skills
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ $# -ge 1 ]; then DEST="$1/.claude/skills"; else DEST="$HOME/.claude/skills"; fi
mkdir -p "$DEST"
for s in "$HERE"/skills/*/; do
  name="$(basename "$s")"
  rm -rf "$DEST/$name"
  cp -R "$s" "$DEST/$name"
  echo "installed $name -> $DEST/$name"
done
