#!/bin/bash
FLAC=$1
MP3="${FLAC%.flac}.mp3"
echo "Converting '$FLAC' -> '$MP3'"
[ -r "$FLAC" ] || { echo can not read file \"$FLAC\" >&1 ; exit 1 ; } ;
echo "Exporting metadata"
metaflac --export-tags-to=- "$FLAC" | sed -e 's/=\(.*\)/="\1"/' -e 's/ALBUM ARTIST/ALBUM_ARTIST/'>tmp.tmp
cat tmp.tmp
. ./tmp.tmp
rm tmp.tmp
flac -sdc "$FLAC" | lame --verbose -V 2  --tt "$TITLE" \
--tn "$TRACKNUMBER" \
--tg "$GENRE" \
--ty "$DATE" \
--ta "$ARTIST" \
--tl "$ALBUM" \
--add-id3v2 \
- "$MP3"

#TITLE="It's Gonna Be Alright"
#ALBUM="Colonial Cousins"
#TRACKNUMBER="01"
#ARTIST="Colonial Cousins"
#GENRE="Other"
#DATE="1996"

