#!/usr/bin/env python

"""Keep yesterday's end-of-day todo_list score going an extra day,
so that progress (or lack of it) won't be erased every night.
(or otherwise generally make past task performance carry forward
somehow, like a long-tail reverb or something)
"""

# fuck you python; why make it so hard to cleanly import from parent dir?
from os.path import dirname, abspath
import sys ; sys.path.insert(1, dirname(dirname(abspath(__file__))))

import os
import time

import fuckometer


def main(args):
    fuckometer.init()
    period = 60
    history = 3*24*60*60 / period
    yesterday = Yesterday(period=period, history=history, pad_history=False)
    yesterday.loop()  # run forever


class Yesterday(fuckometer.Factor):
    """Check my todo list daily status for items done and days to review."""

    path = 'todo_list_yesterday'

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
        self.text = '%s hour todo lowpass' % (len(self.history) * self.period / 60.0 / 60.0)
        try:
            inpath = '%s/%s/raw' % (fuckometer.cfg.feedpath, 'todo_list')
            self.raw = float(open(inpath).readline())
        except Exception, e:
            self.text = str(e)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

