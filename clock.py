#!/usr/bin/env python

import os
import random
import time


def main(args):
    rotation_speed = 10  # seconds per screen

    deathclock = Periodic(deathclock_update, 60*60)
    divergence = Periodic(divergence_update, 60*60*24)
    fuckometer = Periodic(fuckometer_update, 60*60)

    leftsides = [datetime]
    rightsides = [deathclock, divergence, fuckometer]

    lhs, rhs = 0, 0
    rotated = time.time()
    while True:
        lfunc = leftsides[lhs]
        rfunc = rightsides[rhs]
        print('%s  %s' % (lfunc(), rfunc()))
        time.sleep(0.5)

        if time.time() > (rotated + rotation_speed):
            rhs = (rhs + 1) % len(rightsides)
            rotated = time.time()


class Periodic:
    def __init__(self, update, period=60*60):
        self.period = period
        self.update = update
        self.updated_at = 0
        self.value = ''

    def __call__(self):
        now = time.time()
        if now > (self.updated_at + self.period):
            self.value = self.update()
            self.updated_at = now
        return self.value


def deathclock_update():
    #print('deathclock_update()')
    return open('%s/ram/deathclock' % (os.environ['HOME'])).readline().strip()


def divergence_update():
    #print('divergence_update()')
    return 'Divergence: %.6f' % (random.random() * 1.5)


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


def fuckometer_update():
    return 'Fuckometer: NaN'


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

