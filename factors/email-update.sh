#!/bin/sh

BASE="$HOME/.fuckometer/factors"
#TMP="$BASE/email_todo/text"

ONCE=0
if [ "$1" = "--once" ]; then
  ONCE=1
fi

while true ; do
  TMP=$(mktemp email-update.XXXXX)
  ssh mutt mail/.fuckometer-count.sh > $TMP
  if [ "$?" = 1 ]; then
    # skip update if host can't be reached
    echo -n "$0: WARN: 'ssh mutt' failed...  " ; date
  else

    # my email TODO box
    (echo -n 'Mail: ' && grep TODO "$TMP") > "$BASE/email_todo/text"
    N=$(grep TODO "$TMP" | awk '{ print $1 }')
    echo "$N" > "$BASE/email_todo/raw"
    python -c "import math ; print(math.sqrt(max(0, $N - 5)) * 10)" > "$BASE/email_todo/fucks"

    # all email inboxes combined
    (echo -n 'Mail: ' && grep INBOX "$TMP") > "$BASE/email_inboxes/text"
    N=$(grep INBOX "$TMP" | awk '{ print $1 }')
    echo "$N" > "$BASE/email_inboxes/raw"
    python -c "import math ; print(math.sqrt(max(0, $N - 50)))" > "$BASE/email_inboxes/fucks"

  fi  # if host could/couldn't be reached

  rm -f "$TMP"
  if [ "$ONCE" = 1 ]; then exit 0 ; fi
  sleep 9m
done
