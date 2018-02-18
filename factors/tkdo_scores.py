#!/usr/bin/env python

# fuck you python; why make it so hard to cleanly import from parent dir?
from os.path import dirname, abspath
import sys ; sys.path.insert(1, dirname(dirname(abspath(__file__))))

import random
import subprocess

import fuckometer


def main(args):
    fuckometer.init()
    tkdo = TKDO(period=120)
    tkdo.loop()  # run forever


class TKDO(fuckometer.Factor):
    """Average of top items from my TKDO list"""

    path = 'tkdo_scores'

    def fucks(self):
        return max(0.0, self.raw)

    def on_update(self):
        print(self.text)

    def update(self):
        """Take the average of the top 20 TKDO tasks,
        with a floor threshold of 50.
        Pick a task at random as our summary.
        """
        scores = []
        items = []
        fp = subprocess.check_output(('tkdo', 'list', '-20'))
        for line in fp.split('\n'):
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            # the score is easy
            score = float(parts[0])
            scores.append(score)

            # shorten the line for display purposes,
            # by flattening the tasks to leaves only
            score_ = parts[0]
            shortened = []
            parts.reverse()
            for p in parts:
                if p == '::':
                    break
                shortened.append(p)
            shortened.append(score_)
            shortened.reverse()
            #items.append(line)
            items.append(' '.join(shortened))

        if not scores:
            return

        total = sum([x-50 for x in scores])
        avg = total / len(scores)

        randitem = random.choice(items)

        self.raw = avg
        #self.text = 'TKDO: %.1f' % (self.raw)
        self.text = randitem


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

