#!/usr/bin/env bash
# Create projects/<slug>-short/ with the vertical kit + the shared Fireship engine, fonts and marks.
#   bash "${CLAUDE_SKILL_DIR}/scripts/setup_short.sh" <slug>      (projects land under $PROJECTS_DIR, default ./projects)
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
ENGINE="$(cd "$SKILL/../fireship-style-edit/templates" && pwd)"   # the engine is shared with the long-form skill
SLUG="${1:?slug}"
WD="${PROJECTS_DIR:-$PWD/projects}/${SLUG}-short"
mkdir -p "$WD"/{audio,assets/{footage,logos,gifs,figures,shots},frames,renders}
cp "$ENGINE/fireship_engine.py" "$WD/"
cp -R "$ENGINE/fonts" "$WD/"
mkdir -p "$WD/assets" && cp "$ENGINE/assets/"*-mark.png "$WD/assets/"
cp "$SKILL/templates/short_kit.py" "$WD/"
[ -f "$WD/render.py" ] || cp "$SKILL/templates/render_short_template.py" "$WD/render.py"
echo "workdir: $WD"
