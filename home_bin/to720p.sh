#!/bin/bash
SRC=${1:?Need source video}
DST=${2:?Need dest video}
shift
shift
avconv -ss 0 -i "$SRC" $* -c:v libx264 \
                 -c:a aac \
                 -strict experimental \
                 -preset medium \
                 -crf 20 \
                 -s:v hd720 \
                 -b 5000k \
                 -ab 320k \
                 -flags +cgop \
                 -threads 0 \
                 "$DST"


