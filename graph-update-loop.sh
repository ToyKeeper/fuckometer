#!/bin/sh

OUTFILE='/tmp/fuckometer-7d.png'
INFILE="$HOME/.fuckometer/log"
while true ; do
  if [ "$INFILE" -nt "$OUTFILE" ]; then
    echo -n 'Graph update: ... ' ; date
    ./fuckometer-graph.py "$INFILE" -o /tmp/fuckometer-7d.png -n $(expr 6 \* 24 \* 7)
    ./fuckometer-graph.py "$INFILE" -o /tmp/fuckometer-24h.png -n $(expr 6 \* 24)
    rsync -a /tmp/fuckometer-*.png tknet:www/tmp/
  fi
  sleep 10
done
