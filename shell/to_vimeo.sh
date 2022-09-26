#!/bin/bash

# https://vimeo.com/help/compression 

SRC=${1:?Need source video}
DST=${2:?Need dest video}
FFMPEG=${FFMPEG:-$(which ffmpeg)}
FFMPEG=${FFMPEG:-/usr/bin/ffmpeg}
shift
shift
echo "Using ffmpeg: $FFMPEG"
$FFMPEG -ss 0 -i "$SRC" $* -c:v libx264 -c:a libfdk_aac \
                 -profile:v high -profile:a aac_he_v2 \
                 -pix_fmt yuv420p \
                 -crf 18 -coder 1 -r 30 \
                 -preset slow \
                 -bufsize 1835k \
                 -b:a 192k -ar 48000 \
                 -movflags faststart \
                 -flags +cgop -threads 0 \
                 "$DST"


#                 -preset medium \
#                 -strict experimental \
