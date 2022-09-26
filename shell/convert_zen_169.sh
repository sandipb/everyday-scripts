#!/bin/bash

mencoder $1 -o $(basename $1 $2)avi -vf scale=320:180 -oac mp3lame -ovc xvid -xvidencopts bitrate=700
