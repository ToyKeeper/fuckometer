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

verbose = True
# how many tasks per day should we aim for?
daily_target = 8.0
# reset todo status daily at this hour
# (should be a time when you are almost always asleep)
morning_hour = 6
# how many hours before we start ramping up?
grace_period = 4


def main(args):
    fuckometer.init()
    todo = TodoList(period=30, history=120)
    todo.loop()  # run forever


class TodoList(fuckometer.Factor):
    """Check my todo list daily status for items done and days to review."""

    path = 'todo_list'

    def fucks(self):
        # smooth out the jagged sawtooth curve if possible
        if self.history:
            return 100.0 * sum(self.history) / len(self.history)
        else:
            return 100.0 * self.avg()

    def on_update(self):
        if verbose:
            print('%s fucks, %s raw, %s' % (self.fucks(), self.raw, self.text))

    def update(self):
        value = 0.0
        text = ''
        random_item = '[none yet]'

        # first, load up and parse the data
        try:
            fp = open('%s/ram/.todo.slate' % (os.environ['HOME']))
            firstline = fp.readline()
            text = firstline.strip()
            incomplete = []
            for line in fp:
                if line.startswith('[_] ') or line.startswith('[+] '):
                    incomplete.append(line)
            limit = min(20, len(incomplete))
            random_item = '[todo empty]'
            if incomplete:
                random_item = random.choice(incomplete[:limit]).strip()[4:]
        except IOError:
            firstline = ''
            self.text = '[load error]'
            return

        # TODO: maybe factor in results from yesterday too?
        # factor in a few things...
        # - items done today
        # - days needing review
        # - how many "[F]" fail entries there have been today
        # FIXME: parsing is annoying and messy
        pat = re.compile(r'''([\.\d]+)/(\d+) done: [-\d]+ [A-Z][a-z][a-z]( \(\d+ to review\))?( \[F+\])?''')
        found = pat.search(firstline)
        if not found:
            self.text = '[regex error]'
            return

        # parse the rest
        #for i, v in enumerate(found.groups()):
        #    print('%s: %s' % (i+1, v))
        done = float(found.group(1))
        remaining = float(found.group(2))
        to_review = 0.0001
        if found.group(3):
            v = found.group(3)
            v = v[2:].split()[0]
            to_review = max(1.0, float(v))
        failtext = found.group(4)
        failcount = 0
        if failtext:
            for letter in failtext:
                if 'F' == letter:
                    failcount += 1
        #for v in ('done', 'to_review', 'failcount'):
        #    print('%s: %s' % (v, locals()[v]))

        # calculate scores
        factors = []

        # daily task obligation vs completion
        obligation, completion = self.calculate_done(done, failcount)

        # how much are we expected to have done right now, and how much
        # is actually done?
        factors.append(obligation - completion)

        # build-up of days needing review
        factors.append(max(0.0, min(1.0, math.log(to_review, 100))))

        # final value is the average of all factors
        value = sum(factors) / len(factors)

        #print('\ntodo_list_update(%.2f * (%s, %s)) -> %.2f (%s)' % (scale, done, to_review, value, factors))

        self.raw = value
        self.text = random_item

    def calculate_done(self, done, failcount):
        # set low expectations in the morning, but rise throughout the day
        # (can't be expected to have stuff done already in the morning)
        daylength = 24.0 - grace_period
        now = time.localtime(time.time() - (60*60*(morning_hour+grace_period)))
        if now[3] >= daylength:
            obligation = 0.0
        else:
            scale = (now[3]/daylength) + (now[4]/daylength/60) \
                    + (now[5]/daylength/60/60)
            # smooth curve from 0 to 1
            obligation = (1.0 - math.cos(scale * math.pi)) / 2.0
        completion = (done - failcount) / daily_target
        #print('\ntodo_list_update(): obligation=%.2f, completion=%.2f' \
        #        % (obligation, completion))

        return obligation, completion

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

