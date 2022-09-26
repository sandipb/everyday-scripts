#!/bin/bash

SSH_HOST=${1:-udbcrawl.corp.yahoo.com}
echo "Starting autossh to $SSH_HOST"
/usr/bin/autossh -M 0 -f -N -D 127.0.0.1:1080 $SSH_HOST
