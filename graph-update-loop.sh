#!/bin/sh

OUTFILE='/tmp/fuckometer.png'
INFILE="$HOME/.fuckometer/log"
while true ; do
  sleep 10
  if [ "$INFILE" -nt "$OUTFILE" ]; then
    ./fuckometer-graph.py "$INFILE" $(expr 6 \* 24 \* 7)
    echo -n 'Graph update: ' ; date
  fi
done
