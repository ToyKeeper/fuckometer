#!/usr/bin/env python

# fuck you python; why make it so hard to cleanly import from parent dir?
from os.path import dirname, abspath
import sys ; sys.path.insert(1, dirname(dirname(abspath(__file__))))

import random

import fuckometer


def main(args):
    fuckometer.init()
    divergence = Divergence(condition=fuckometer.six_am)
    divergence.loop()  # run forever


class Divergence(fuckometer.Factor):
    """Divergence factor from Steins;Gate"""

    path = 'steins_gate'

    def fucks(self):
        return 100.0 * max(0.0, 1.0 - self.raw)

    def on_update(self):
        print(self.text)

    def update(self):
        self.raw = random.random() * 1.5
        self.text = 'Divergence: %.6f' % (self.raw)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

