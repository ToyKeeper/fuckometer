#!/bin/sh

OUTFILE='/tmp/fuckometer-7d.png'
INFILE="$HOME/.fuckometer/log"

OUTFILE2='/tmp/factors.png'
INFILE2="$HOME/.fuckometer/factors.log"
while true ; do
  # update fuckometer graphs
  if [ "$INFILE" -nt "$OUTFILE" ]; then
    echo -n 'Graph update: ... ' ; date
    ./fuckometer-graph.py "$INFILE" -o /tmp/fuckometer-7d.png -n $(expr 6 \* 24 \* 7)
    ./fuckometer-graph.py "$INFILE" -o /tmp/fuckometer-24h.png -n $(expr 6 \* 24)
    rsync -a /tmp/fuckometer-*.png tknet:www/tmp/
  fi
  # update factor graphs
  if [ "$INFILE2" -nt "$OUTFILE2" ]; then
    echo -n 'Factor graph update: ... ' ; date
    ./factor-graph.py "$INFILE2" -o "$OUTFILE2" -d 7
    ./factor-graph.py "$INFILE2" -o "factors-6m.png" -d 183
  fi
  sleep 10
done
