#!/usr/bin/env python

# fuck you python; why make it so hard to cleanly import from parent dir?
from os.path import dirname, abspath
import sys ; sys.path.insert(1, dirname(dirname(abspath(__file__))))

import random
import time

import fuckometer

# Specify your time of birth:
# (year, month, day, hour, minute, second, 0, 0, -1)
born = (1978,1,12,6,8,0,0,0,-1)


def main(args):
    fuckometer.init()
    deathclock = Deathclock(condition=fuckometer.six_am)
    #deathclock = Deathclock(period=5)  # debug
    #deathclock()  # execute only once
    deathclock.loop()  # run forever


class Deathclock(fuckometer.Factor):
    """How much time do I have left to live, approximately?"""

    path = 'time_to_live'

    def fucks(self):
        value = self.raw
        x = max(0.0, (20-value) * 5)
        return x

    def on_update(self):
        print('ETD: %s' % (self.text))
        print('Fucks: %s' % (self.fucks()))

    def update(self):
        #print('deathclock_update()')
        #return open('%s/ram/deathclock' % (os.environ['HOME'])).readline().strip()
        # https://www.cdc.gov/nchs/fastats/life-expectancy.htm
        # https://www.cdc.gov/nchs/data/hus/hus16.pdf page 16
        # TODO: my grandparents died at ages 87?, 83?, 63? (unnatural), and 96?
        # TODO: my parents died at ages 77 (unnatural) and (still alive, 73+)
        # TODO: ... so my ETD is probably between 80 and 100?
        expected_years = 81.1  # US white female life expectancy as of 2015
        stddev_years = 15.0  # www.nber.org/papers/w14093

        today_years = (time.time() - time.mktime(born)) / 365.24 / 24 / 60 / 60

        random_expected_years = random.gauss(expected_years, stddev_years)
        remaining_years = random_expected_years - today_years

        #print('You are %.2f years old.' % (today_years))

        display_years = remaining_years
        fmt = 'ETD %.1f y / %i d'
        if remaining_years < 0:
            #fmt = 'You are %.2f years past your expiration date.  (%i days)'
            fmt = 'Died %.1f y ago / %i d'
            display_years = -remaining_years

        self.raw = remaining_years
        self.text = fmt % (remaining_years, remaining_years*365.24)
        #return remaining_years, (fmt % (remaining_years, remaining_years * 365.24))
        #return self.raw, self.text


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

