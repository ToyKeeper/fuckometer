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
            return 100.0 * self.raw

    def on_update(self):
        if fuckometer.cfg.verbose:
            print('%s fucks, %s raw, %s' % (self.fucks(), self.raw, self.text))

    def update(self):
        if not hasattr(self, 'floor'):
            self.floor = 0.0  # how fucked we are at the beginning of the day
            self.floor_tomorrow = 0.0

        value = 0.0
        text = ''
        random_item = '[none yet]'
        random_items = [random_item]

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
            random_items = [random_item]
            if incomplete:
                random_item = random.choice(incomplete[:limit]).strip()[4:]
                random_items = [l.strip()[4:] for l in incomplete[:limit]]
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
        to_review = 1.0
        if found.group(3):
            v = found.group(3)
            v = v[2:].split()[0]
            # give a grace period of a day before punishment starts
            to_review = max(1.0, float(v)-1)
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
        if fuckometer.cfg.verbose:
            print('todo(obligation=%.3f, completion=%.3f)' % (obligation, completion))

        # set new floor level for tomorrow
        now = time.localtime()
        if (now[3] == morning_hour):
            self.floor = self.floor_tomorrow
        elif (now[3] == morning_hour-1):
            self.floor_tomorrow = obligation - completion

        # how much are we expected to have done right now, and how much
        # is actually done?
        factors.append(obligation - completion)

        # build-up of days needing review
        factors.append(max(0.0, min(1.0, math.log(to_review, 100))))

        # final value is the average of all factors
        value = sum(factors) / len(factors)

        #print('\ntodo_list_update(%.2f * (%s, %s)) -> %.2f (%s)' % (scale, done, to_review, value, factors))

        self.raw = value
        #self.text = random_item
        self.text = '\n'.join(random_items)

    def calculate_done(self, done, failcount):
        # obligation holds steady from (morning_hour - grace_period) to 
        # (morning_hour + grace_period), holding its last value...
        # but in-between it rises along a sine curve from self.floor to 1.0
        # (so:
        #   floor from 6am to 10am,
        #   sine up from 10am to 2am,
        #   then it's 1.0 from 2am to 6am)
        hour = time.localtime(time.time() - (60*60*(morning_hour)))[3]
        if hour < grace_period:
            obligation = self.floor
        elif hour >= (24 - grace_period):
            obligation = 1.0
        else:
            now = time.localtime(time.time() - (60*60*(morning_hour+grace_period)))
            daylength = 24.0 - grace_period - grace_period
            phase = (now[3]/daylength) + (now[4]/daylength/60) \
                    + (now[5]/daylength/60/60)
            phase = max(0.0, min(1.0, phase))  # trim range, just in case
            # smooth curve from floor to 1
            size = 1.0 - self.floor
            obligation = self.floor \
                         + (size * (0.5 - (math.cos(phase * math.pi) / 2.0)))
        """
        # set low expectations in the morning, but rise throughout the day
        # (can't be expected to have stuff done already in the morning)
        daylength = 24.0 - grace_period  # don't start until morning_hour+grace_period
        now = time.localtime(time.time() - (60*60*(morning_hour+grace_period)))
        if now[3] >= daylength:  # if it's tomorrow, reset to the floor
            obligation = self.floor
        else:
            # stop rising at grace_period hours before morning_hour
            daylength -= grace_period
            scale = (now[3]/daylength) + (now[4]/daylength/60) \
                    + (now[5]/daylength/60/60)
            scale = max(0.0, min(1.0, scale))  # trim range
            # smooth curve from floor to 1
            diff = 1.0 - self.floor
            obligation = self.floor + (diff * (0.5 - (math.cos(scale * math.pi) / 2.0)))
            """
        completion = (done - failcount) / daily_target
        #print('\ntodo_list_update(): obligation=%.2f, completion=%.2f' \
        #        % (obligation, completion))

        return obligation, completion

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

