#!/usr/bin/env bash
# make-evidence.sh <source.mp4> <output.mp4> "<AFTER label>" [outdir]
set -euo pipefail
SRC=$1; OUT=$2; LABEL=${3:-AFTER}; DIR=${4:-.}; mkdir -p "$DIR"
FONT=$(fc-match -f '%{file}' 'DejaVu Sans:bold' 2>/dev/null || true); FONTOPT=${FONT:+fontfile=$FONT:}
LBL="fontsize=22:fontcolor=white:box=1:boxcolor=black@0.5:x=10:y=10"
FC="[0:v]scale=-2:360,fps=24,drawtext=${FONTOPT}text='BEFORE (source)':${LBL}[a];[1:v]scale=-2:360,fps=24,drawtext=${FONTOPT}text='${LABEL}':${LBL}[b];[a][b]hstack=shortest=1[v]"
ffmpeg -v error -y -i "$SRC" -i "$OUT" -filter_complex "$FC" -map "[v]" -an -c:v libx264 -preset ultrafast -crf 23 -pix_fmt yuv420p "$DIR/before-after.mp4"
ffmpeg -v error -y -t 6 -i "$DIR/before-after.mp4" -vf "fps=6,scale=640:-2:flags=fast_bilinear,split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3" "$DIR/before-after.gif"
ffmpeg -v error -y -i "$DIR/before-after.mp4" -vf "select='eq(n\,12)+eq(n\,120)+eq(n\,216)',tile=1x3" -frames:v 1 -vsync vfr "$DIR/before-after-frames.png"
