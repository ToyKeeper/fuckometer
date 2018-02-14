#!/usr/bin/env python

import math
import os
import random
import re
import sys
import time

# TODO: periodically log the fuckometer value so I can graph it later


def main(args):
    rotation_speed = 10  # seconds per screen
    if args:
        rotation_speed = float(args[0])

    leftsides = [datetime]
    #rightsides = [deathclock, divergence, fuckometer]
    rightsides = [deathclock, fuckometer]

    lhs, rhs = 0, 0
    rotated = time.time()
    while True:
        lfunc = leftsides[lhs]
        rfunc = rightsides[rhs]

        # TODO: shorten output to fit on a 8-character display
        #print('\n%s  %s' % (lfunc(), rfunc()))
        sys.stdout.write('\n%s  %s' % (lfunc(), rfunc()))
        sys.stdout.flush()

        time.sleep(0.5)

        if time.time() > (rotated + rotation_speed):
            rhs = (rhs + 1) % len(rightsides)
            rotated = time.time()


class Periodic:
    def __init__(self, update, period=60*60):
        self.period = period
        self.update = update
        self.updated_at = 0
        self.value = 0.0
        self.text = ''

        # FIXME: if period is 1 day, set each cycle to 6am
        #        (so it'll only update only when I'm asleep)

    def __call__(self):
        now = time.time()
        if now > (self.updated_at + self.period):
            self.value, self.text = self.update()
            self.updated_at = now
        return self.text


def datetime():
    if not hasattr(datetime, 'colons'):
        datetime.colons = True
    else:
        datetime.colons = not datetime.colons

    if datetime.colons:
        colon = ':'
    else:
        colon = ' '
    fmt = '%%Y-%%m-%%d %%H%s%%M%s%%S' % (colon, colon)
    return time.strftime(fmt)


def deathclock_update():
    """How much time do I have left to live, approximately?"""
    #print('deathclock_update()')
    #return open('%s/ram/deathclock' % (os.environ['HOME'])).readline().strip()
    # https://www.cdc.gov/nchs/fastats/life-expectancy.htm
    # https://www.cdc.gov/nchs/data/hus/hus16.pdf page 16
    # TODO: my grandparents died at ages 87?, 83?, 63? (unnatural), and 96?
    # TODO: my parents died at ages 77 (unnatural) and (still alive, 73+)
    # TODO: ... so my ETD is probably between 80 and 100?
    expected_years = 81.1  # US white female life expectancy as of 2015
    stddev_years = 15.0  # www.nber.org/papers/w14093
    born = (1978,1,12,6,8,0,0,0,-1)

    today_years = (time.time() - time.mktime(born)) / 365.24 / 24 / 60 / 60

    random_expected_years = random.gauss(expected_years, stddev_years)
    remaining_years = random_expected_years - today_years

    #print('You are %.2f years old.' % (today_years))

    display_years = remaining_years
    fmt = 'ETD %.2f y / %i d'
    if remaining_years < 0:
        fmt = 'You are %.2f years past your expiration date.  (%i days)'
        display_years = -remaining_years
    return remaining_years, (fmt % (remaining_years, remaining_years * 365.24))


def divergence_update():
    #print('divergence_update()')
    value = (random.random() * 1.5)
    return value, 'Divergence: %.6f' % (value)


# FIXME: defining these globally is a nasty kludge
# FIXME: make these reset at 6am, not 24 hours from script start
deathclock = Periodic(deathclock_update, 60*60*24)
divergence = Periodic(divergence_update, 60*60*24)


def open_windows_update():
    line = open('%s/.open/open.otl.stats' % (os.environ['HOME'])).readline()
    parts = line.split()
    windows = int(parts[0])
    text = line.strip()
    return windows, text

open_windows = Periodic(open_windows_update, 63)


def todo_list_update():
    """Check my todo list daily status for items done and days to review.
    """
    value = 0.0
    text = ''

    # set low expectations in the morning, but rise throughout the day
    # (can't be expected to have stuff done already in the morning)
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
        line = open('%s/ram/.todo.slate' % (os.environ['HOME'])).readline()
        text = line.strip()
    except IOError:
        line = ''
    # TODO: maybe factor in results from yesterday too?
    # factor in a few things...
    # - items done today
    # - days needing review
    # - how many "[F]" fail entries there have been today
    pat = re.compile(r'''([\.\d]+)/(\d+) .* \((\d+) to review\)( \[F+\])?''')
    found = pat.search(line)
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

    return value, text

todo_list = Periodic(todo_list_update, 61)


def fuckometer_update():
    factors = []

    # Steins;Gate world line divergence number
    # (meh, too random, makes fuckometer less meaningful)
    #factors.append(max(0.0, 1.0 - divergence.value))

    # how close am I to death?
    factors.append(max(0.0, (20-deathclock.value) / 10.0))

    # factor in number of windows / tabs currently open
    open_windows()
    windows = open_windows.value
    value = (windows - 100) / 250.0
    value = min(1.0, max(0.0, value))
    factors.append(value)

    # factor in the state of my todo list today
    todo_list()
    factors.append(todo_list.value)

    # TODO: factor in recent monetary flow and balance
    # TODO: factor in my overall health
    #       (have I exercised lately?  is my weight too high/low?)
    # TODO: factor in recent news
    # TODO: factor in how much time I've spent working today vs slacking
    # TODO: factor in unprocessed papers?
    # TODO: factor in windows open on my other computer(s)
    # TODO: factor in current weather
    # TODO: factor in the size of my combined email inboxes

    # average the values
    value = sum(factors) / len(factors)
    value = max(0.0, value)

    #return value, 'Fuckometer: %.0f%%' % (100.0 * value)
    return value, 'Fuckometer: %.1f%%' % (100.0 * value)


# FIXME: defining this globally is a nasty kludge
fuckometer = Periodic(fuckometer_update, 60)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

