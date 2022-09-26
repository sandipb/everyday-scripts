#!/bin/bash

mencoder -quiet $1 -o $(basename $1 $2)avi -vf scale=320:240 -oac mp3lame -ovc xvid -xvidencopts bitrate=700
