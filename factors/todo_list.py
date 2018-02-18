#!/usr/bin/env python

# fuck you python; why make it so hard to cleanly import from parent dir?
from os.path import dirname, abspath
import sys ; sys.path.insert(1, dirname(dirname(abspath(__file__))))

import math
import os
import random
import re
import time

import fuckometer


def main(args):
    fuckometer.init()
    todo = TodoList(period=59)
    todo.loop()  # run forever


class TodoList(fuckometer.Factor):
    """Check my todo list daily status for items done and days to review."""

    path = 'todo_list'

    def fucks(self):
        return 100.0 * self.raw

    def on_update(self):
        print('%s fucks, %s done, %s' % (self.fucks(), self.raw, self.text))

    def update(self):
        value = 0.0
        text = ''

        # set low expectations in the morning, but rise throughout the day
        # (can't be expected to have stuff done already in the morning)
        # FIXME: use a cleaner method of shifting everything by 6 hours
        scale = 1.0
        now = time.localtime()
        compare = list(now)
        morning_hour = 6
        if now[3] < morning_hour:  # if it's after midnight, measure from previous morning
            compare[2] -= 1
        compare[3:8] = [morning_hour, 0, 0, 0, 0]
        scale = (time.mktime(now) - time.mktime(compare)) / (24.0*60*60)
        #print('\ntodo_list_update(): scale=%.2f' % (scale))

        try:
            fp = open('%s/ram/.todo.slate' % (os.environ['HOME']))
            firstline = fp.readline()
            text = firstline.strip()
            incomplete = []
            for line in fp:
                if line.startswith('[_] '):
                    incomplete.append(line)
            limit = min(10, len(incomplete))
            random_item = random.choice(incomplete[:limit]).strip()[4:]
        except IOError:
            firstline = ''
            random_item = '[load error]'
        # TODO: maybe factor in results from yesterday too?
        # factor in a few things...
        # - items done today
        # - days needing review
        # - how many "[F]" fail entries there have been today
        pat = re.compile(r'''([\.\d]+)/(\d+) .* \((\d+) to review\)( \[F+\])?''')
        found = pat.search(firstline)
        if found:
            done = float(found.group(1))
            remaining = float(found.group(2))
            to_review = max(1.0, float(found.group(3)))
            failtext = found.group(4)
            failcount = 0
            if failtext:
                for letter in failtext:
                    if 'F' == letter:
                        failcount += 1
            factors = []
            #factors.append(scale * max(0.0, (6 - done) / 6.0))
            factors.append(scale * (failcount + 6 - done) / 6.0)
            factors.append(scale * max(0.0, min(1.0, math.log(to_review, 100))))
            value = sum(factors) / len(factors)
        #print('\ntodo_list_update(%.2f * (%s, %s)) -> %.2f (%s)' % (scale, done, to_review, value, factors))

        self.raw = value
        self.text = random_item


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

