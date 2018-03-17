#!/usr/bin/env python

# fuck you python; why make it so hard to cleanly import from parent dir?
from os.path import dirname, abspath
import sys ; sys.path.insert(1, dirname(dirname(abspath(__file__))))

import math
import subprocess
import time

import fuckometer

host = 'chi'


def main(args):
    fuckometer.init()
    tabs = ChromeTabs(period=60*5)
    tabs.loop()  # run forever


class ChromeTabs(fuckometer.Factor):
    """How many tabs are open in Chrome on my notebook?
    Uses this extension, and one of the extension's scripts:
    https://github.com/ToyKeeper/tab-counteroo
    """

    path = 'chrome_tabs_chi'

    def fucks(self):
        #return (self.raw - 10) * 2 / 3.0
        return math.pow(max(1, self.raw - 5), 1/1.05)

    def on_update(self):
        if fuckometer.cfg.verbose:
            print(self.text)

    def update(self):
        try:
            cmd = ('ssh', host, 'src/tab-counteroo/src/tabsOpen.py')
            text = subprocess.check_output(cmd)
        except:
            print("%s - Couldn't contact %s." % (time.strftime('%Y-%m-%d %H:%M:%S'), host))
            return
        line = text.split('\n')[0]
        value = int(line)
        self.raw = value
        self.text = 'Chrome Tabs Chi: %i' % (self.raw)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

