#!/bin/zsh

OUTDIR="$HOME/.fuckometer/factors/chrome_tabs"

method1() {
  # parse chrome's "Current Tabs" file
  # (except that file sucks and changes a lot for no reason)
  cd $HOME/src/nixieclock/chrome_info/Chromagnon
  NUMTABS=$(python chromagnonTab.py "$HOME/.config/chromium/Default/Current Tabs" \
    | grep http \
    | wc -l)
  NUMTABS=$(python chromagnonTab.py "$HOME/.config/chromium/Default/Current Tabs" \
    | wc -l)
}
method2() {
  # estimate tabs from number of processes
  NUMTABS=$(ps axuwww | grep chro | egrep -v 'grep|python|sh$' | wc -l)
  NUMTABS=$(( $NUMTABS * 1.33333 ))
}

mkdir -p "$OUTDIR"

while true ; do
  method2
  echo "$NUMTABS" > "$OUTDIR/raw"
  echo "$NUMTABS" > "$OUTDIR/text"
  echo $(( ( $NUMTABS - 10 ) * 0.6666666 )) > "$OUTDIR/fucks"
  sleep 9m
done
