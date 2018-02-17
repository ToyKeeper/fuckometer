#!/bin/sh

OUTFILE='/tmp/fuckometer.png'
INFILE='fuckometer.log'
while true ; do
  sleep 10
  if [ "$INFILE" -nt "$OUTFILE" ]; then
    ./fuckometer-graph.py fuckometer.log
    echo -n 'Graph update: ' ; date
  fi
done
