#!/bin/bash

# Check if at least two arguments were provided
if [ $# -lt 2 ]; then
  echo "Usage: $0 <interval> <command>"
  exit 1
fi

INTERVAL=$1
shift
COUNT=0
START=$(date +%s)

while true; do
  COUNT=$((COUNT + 1))
  NOW=$(date +%s)
  ELAPSED=$((NOW - START))

  echo "=== Count: $COUNT, Duration: ${ELAPSED}s ==="
  date

  "$@"
  AFTER=$(date +%s)
  echo
  echo "=== Done in $((AFTER - NOW))s ==="
  echo

  sleep $INTERVAL
done