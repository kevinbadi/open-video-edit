#!/usr/bin/env bash
# Create projects/<slug>-longform/ and copy the engine + shared modules + fonts + Claude marks.
#   bash "${CLAUDE_SKILL_DIR}/scripts/setup_workdir.sh" <slug>   (projects land under $PROJECTS_DIR, default ./projects)
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
SLUG="${1:?slug}"
WD="${PROJECTS_DIR:-$PWD/projects}/${SLUG}-longform"
mkdir -p "$WD"/{source,audio,renders,frames,fonts,assets/logos,assets/gifs,assets/figures,assets/thumbs,assets/shots}
cp "$SKILL"/templates/{longform_engine,media_marks,hyper_edits,light_fx,fonts,claude_marks}.py "$WD/"
cp "$SKILL"/templates/fonts/*.ttf "$WD/fonts/"
cp "$SKILL"/assets/claude-*.png "$WD/assets/"
[ -f "$WD/render.py" ] || cp "$SKILL/templates/render_template.py" "$WD/render.py"
echo "workdir: $WD"
