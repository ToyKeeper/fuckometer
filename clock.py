#!/usr/bin/env python

import os
import random
import sys
import time


def main(args):
    rotation_speed = 10  # seconds per screen
    if args:
        rotation_speed = float(args[0])

    leftsides = [datetime]
    rightsides = [deathclock, divergence, fuckometer]

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
deathclock = Periodic(deathclock_update, 60*60*24)
divergence = Periodic(divergence_update, 60*60*24)

def open_windows_update():
    line = open('%s/.open/open.otl.stats' % (os.environ['HOME'])).readline()
    parts = line.split()
    windows = int(parts[0])
    text = line.strip()
    return windows, text

open_windows = Periodic(open_windows_update, 60*60)

def fuckometer_update():
    factors = []

    # Steins;Gate world line divergence number
    factors.append(max(0.0, 1.0 - divergence.value))

    # how close am I to death?
    factors.append(max(0.0, (20-deathclock.value) / 10.0))

    # factor in number of windows / tabs currently open
    open_windows()
    windows = open_windows.value
    value = (windows - 100) / 250.0
    value = min(1.0, max(0.0, value))
    factors.append(value)

    # TODO: factor in recent monetary flow and balance
    # TODO: factor in my overall health
    #       (have I exercised lately?  is my weight too high/low?)
    # TODO: factor in recent news
    # TODO: factor in the state of my todo list today
    # TODO: factor in how much time I've spent working today vs slacking

    # average the values
    value = sum(factors) / len(factors)
    value = max(0.0, value)
    return value, 'Fuckometer: %.0f%%' % (100.0 * value)


# FIXME: defining this globally is a nasty kludge
fuckometer = Periodic(fuckometer_update, 60)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

