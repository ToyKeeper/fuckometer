#!/usr/bin/env python

# fuck you python; why make it so hard to cleanly import from parent dir?
from os.path import dirname, abspath
import sys ; sys.path.insert(1, dirname(dirname(abspath(__file__))))

import os
import random

import fuckometer


def main(args):
    fuckometer.init()
    windows = OpenWindows(period=59)
    windows.loop()  # run forever


class OpenWindows(fuckometer.Factor):
    """How many windows are open on my desktop?"""

    path = 'open_windows'

    def fucks(self):
        floor = 50.0
        ceil = 400.0
        value = (self.raw - floor) / (ceil-floor)
        value = min(1.0, max(0.0, value))
        return 100.0 * value

    def on_update(self):
        print('%.1f fucks: %s' % (self.fucks(), self.text))

    def update(self):
        line = open('%s/.open/open.otl.stats' % (os.environ['HOME'])).readline()
        parts = line.split()
        self.raw = int(parts[0])
        self.text = line.strip()


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

