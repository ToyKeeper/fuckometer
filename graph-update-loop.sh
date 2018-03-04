#!/bin/sh

FUCKLOG="$HOME/.fuckometer/log"
FACTORLOG="$HOME/.fuckometer/factors.log"

main() {
  while true ; do
    update fucks 1 /tmp/fuckometer-conky.png --conky
    update fucks 1 /tmp/fuckometer-24h.png
    update fucks 7 /tmp/fuckometer-7d.png

    update factors   7 /tmp/factors-7d.png
    update factors 183 /tmp/factors-6m.png

    sleep 10
  done
}

update() {
  # parse args
  TYPE=$1 ; shift
  PERIOD=$1 ; shift
  OUTFILE=$1 ; shift
  ARGS=$*
  if [ "$TYPE" = 'fucks' ]; then
    INFILE="$FUCKLOG"
    # convert days to number of entries
    PERIOD=$(( 6 * 24 * $PERIOD ))
  else
    INFILE="$FACTORLOG"
  fi

  # update graph
  if [ ! -e "$OUTFILE" -o "$INFILE" -nt "$OUTFILE" ]; then
    if [ "$TYPE" = 'fucks' ]; then
      ./graph-fuckometer.py "$INFILE" -o "$OUTFILE" -n "$PERIOD" $ARGS
    else
      ./graph-factors.py "$INFILE" -o "$OUTFILE" -d "$PERIOD" $ARGS
    fi
    rsync -a "$OUTFILE" tknet:www/fuckometer/
    echo -n "Updated '$OUTFILE' ... " ; date
  fi
}

main
