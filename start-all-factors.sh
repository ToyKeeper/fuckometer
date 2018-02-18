#!/bin/sh

cd factors
for script in *.py *.sh ; do
  pid=$(ps axuwww | egrep -v 'grep|vim' | grep "$script" | awk '{print $2}')
  if [ "$pid" != "" ]; then
    for p in "$pid" ; do
      echo kill "$pid"
      ps axuwww | grep -v grep | grep " $pid "
      kill "$pid"
    done
  fi
  echo "Starting $script ..."
  "./$script" &
done
