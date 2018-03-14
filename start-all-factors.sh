#!/bin/sh

cd factors
for script in *.py *.sh ; do
  STARTTHIS=y
  pid=$(ps axuwww | egrep -v 'grep|vim' | grep "$script" | awk '{print $2}')
  if [ "$pid" != "" ]; then
    STARTTHIS=n
    for p in "$pid" ; do
      echo "=== process $pid ==="
      ps axuwww | grep -v grep | grep " $pid  "
      # TODO: ask user whether to kill this process
      echo -n 'Kill this? [y/N] '
      read ANS
      if [ "$ANS" = 'y' ]; then
        kill "$pid"
        STARTTHIS=y
      fi
    done
  fi
  if [ "$STARTTHIS" = 'y' ]; then
    echo "Starting $script ..."
    "./$script" &
  fi
done
