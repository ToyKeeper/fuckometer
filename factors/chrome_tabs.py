#!/usr/bin/env python

# fuck you python; why make it so hard to cleanly import from parent dir?
from os.path import dirname, abspath
import sys ; sys.path.insert(1, dirname(dirname(abspath(__file__))))

import math
import subprocess

import fuckometer


def main(args):
    fuckometer.init()
    tabs = ChromeTabs(period=60)
    tabs.loop()  # run forever


class ChromeTabs(fuckometer.Factor):
    """How many tabs are open in Chrome?
    Uses this extension, and one of the extension's scripts:
    https://github.com/ToyKeeper/tab-counteroo
    """

    path = 'chrome_tabs'

    def fucks(self):
        #return (self.raw - 10) * 2 / 3.0
        return math.pow(max(1, self.raw - 10), 1/1.1)

    def on_update(self):
        if fuckometer.cfg.verbose:
            print(self.text)

    def update(self):
        # getting the data is messy, so put it in another script
        basedir = sys.path[1]
        cmd = ('%s/%s' % (basedir, 'factors/chrome_tabs/tabsOpen.py'),)
        text = subprocess.check_output(cmd)
        value = int(text)
        self.raw = value
        self.text = 'Chrome Tabs: %i' % (self.raw)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

