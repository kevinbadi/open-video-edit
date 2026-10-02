#!/usr/bin/env bash
# Render every frame in N parallel chunks, encode with the clip's own audio, copy to ~/Downloads.
#   bash .../scripts/render_parallel.sh "Readable Name"   [chunks=4]     (run from the workdir)
set -euo pipefail
NAME="${1:?readable output name}"
CHUNKS="${2:-4}"
N=$(python3 -c "import json;m=json.load(open('source/meta.json'));print(int(float(m['DUR'])*30)+1)")
rm -rf frames/out; mkdir -p frames/out
STEP=$(( (N + CHUNKS - 1) / CHUNKS ))
for ((i=0; i<CHUNKS; i++)); do
  A=$(( i * STEP )); B=$(( A + STEP ))
  RANGE="$A:$B" python3 render.py > "frames/log_$i.txt" 2>&1 &
done
wait
GOT=$(ls frames/out | wc -l | tr -d ' ')
echo "frames: $GOT / $N"
grep -l "Traceback" frames/log_*.txt && { echo "render errors, see frames/log_*.txt"; exit 1; } || true
ffmpeg -y -loglevel error -framerate 30 -i frames/out/f%05d.jpg -i audio/narration.m4a \
  -c:v libx264 -pix_fmt yuv420p -preset medium -crf 16 -c:a aac -b:a 192k -movflags +faststart -shortest renders/final.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=width,height:format=duration -of csv=p=0 renders/final.mp4
cp renders/final.mp4 "$HOME/Downloads/$NAME.mp4"
echo "-> ~/Downloads/$NAME.mp4"
