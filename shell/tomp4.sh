#!/bin/bash
SRC=${1:?Need source video}
DST=${2:?Need dest video}
FFMPEG=${FFMPEG:-$(which ffmpeg)}
FFMPEG=${FFMPEG:-/usr/bin/ffmpeg}
shift
shift
echo "Using ffmpeg: $FFMPEG"
$FFMPEG -ss 0 -i "$SRC" $* -c:v libx264 -c:a aac \
                 -strict experimental \
                 -pix_fmt yuv420p \
                 -crf 18 \
                 -preset slow \
                 -bufsize 1835k \
                 -b:a 192k -ar 44100 \
                 -movflags faststart \
                 -flags +cgop -threads 0 \
                 "$DST"


#                 -preset medium \
