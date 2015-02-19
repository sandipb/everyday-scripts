#!/bin/bash
SRC=${1:?Need source video}
DST=${2:?Need dest video}
shift
shift
/usr/bin/avconv -ss 0 -i "$SRC" $* -c:v libx264 -c:a libmp3lame \
                 -strict experimental \
                 -preset medium \
                 -crf 20 \
                 -bufsize 1835k \
                 -b:a 128k \
                 -flags +cgop -threads 0 \
                 "$DST"


