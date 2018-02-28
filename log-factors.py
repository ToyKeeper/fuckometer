#!/usr/bin/env python

# fuck you python; why make it so hard to cleanly import from parent dir?
from os.path import dirname, abspath
import sys ; sys.path.insert(1, dirname(dirname(abspath(__file__))))

import os
import time

import fuckometer


def main(args):
    fuckometer.init()
    flog = FactorLog(condition=fuckometer.hourly)
    flog.loop()  # run forever


class FactorLog(fuckometer.Factor):
    """Log factor data over time"""

    path = 'factors.log'
    dtsfmt = '%Y-%m-%d %H:%M:%S'

    def log(self):
        pass

    def on_update(self):
        print('log-factors: updated at %s' % (time.strftime(self.dtsfmt)))

    def update(self):
        factors = []
        base = fuckometer.cfg.feedpath
        logpath = '%s/%s' % (os.path.dirname(fuckometer.cfg.logpath), self.path)
        now = time.strftime(self.dtsfmt)
        for name in os.listdir(base):
            try:
                fp = open('%s/%s/fucks' % (base, name))
                fucks = fp.readline().strip()
                factors.append((name, fucks))
            except Exception, e:
                print('log-factors: error opening %s: %s' % (name, str(e)))

        factors.sort()
        fp = open(logpath, 'a')
        for name, fucks in factors:
            line = '%s\t%s\t%s\n' % (now, name, fucks)
            fp.write(line)
        fp.close()


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

