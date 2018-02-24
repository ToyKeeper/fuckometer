#!/usr/bin/env python

# fuck you python; why make it so hard to cleanly import from parent dir?
from os.path import dirname, abspath
import sys ; sys.path.insert(1, dirname(dirname(abspath(__file__))))

import os
import random
import subprocess

import fuckometer

host = 'chi'


def main(args):
    fuckometer.init()
    windows = WindowsOpen(period=60*9)
    windows.loop()  # run forever


class WindowsOpen(fuckometer.Factor):
    """How many windows are open on my notebook?"""

    path = 'windows_open_%s' % (host,)

    def fucks(self):
        floor = 50.0
        ceil = 300.0
        value = (self.raw - floor) / (ceil-floor)
        value = min(1.0, max(0.0, value))
        return 100.0 * value

    def on_update(self):
        if fuckometer.cfg.verbose:
            print('%.1f fucks: %s' % (self.fucks(), self.text))

    def update(self):
        try:
            home = os.environ['HOME']
            cmd = ('rsync', '-a', '%s:.open/open.otl.stats' % (host),
                    '%s/.open/open.otl.stats.%s' % (home, host))
            subprocess.check_call(cmd)
        except:
            print("%s - Couldn't contact %s." % (time.strftime('%Y-%m-%d %H:%M:%S'), host))
            return
        line = open('%s/.open/open.otl.stats.%s' % (os.environ['HOME'], host)).readline()
        parts = line.split()
        self.raw = int(parts[0])
        self.text = line.strip()


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

