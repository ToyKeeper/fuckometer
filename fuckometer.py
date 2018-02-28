#!/usr/bin/env python

import math
import os
import random
import re
import sys
import time

import pycfg

cfg = None
program_name = 'fuckometer'


def main(args):
    """Fuckometer.  Calculates how fucked you are.
    (uses a bunch of data sources to calculate this)
    Usage: ./fuckometer.py [options]
    Options include:
      -h   --help      Display this info, and exit.
      -c   --cfg       Print the current configuration, and exit.
      -o F --log F     Log fuckometer data to file F every 10 minutes.
      -n   --dry-run   Don't write to the log file.
      -1   --once      Calculate current value and exit.
                       (otherwise keeps running, and logs periodically)
    """

    init()

    i = 0
    while i < len(args):
        a = args[i]
        if a in ('-h', '--help'):
            return usage()
        elif a in ('-c', '--cfg'):
            print(cfg)
            return
        elif a in ('-o', '--log'):
            i += 1
            a = args[i]
            cfg.logpath = a
        elif a in ('-n', '--dryrun', '--dry-run'):
            cfg.dryrun = True
        elif a in ('-1', '--once'):
            cfg.once = True
        else:
            return usage()

        i += 1


    if not os.path.exists(cfg.feedpath):
        os.makedirs(cfg.feedpath)


    f = Fuckometer(cfg)

    while True:
        f.update()
        print('%s (%s)' % (f.text, f.value))

        if not cfg.dryrun:
            f.save()
            f.log()

        if cfg.once:
            return

        time.sleep(0.5)


def init():
    global cfg
    cfg = pycfg.config(program_name)
    set_defaults(cfg)
    cfg.load()
    #TODO: cfg.validate()


def usage():
    print(main.__doc__)


def set_defaults(cfg):
    rcdir = '%s/.%s' % (os.environ['HOME'], program_name)

    cfg.doc(verbose="Print extra info.")
    cfg.default(verbose=False)

    cfg.doc(dryrun="Don't log computed data.")
    cfg.default(dryrun=False)

    cfg.doc(once='Run only once, then exit.')
    cfg.default(once=False)

    cfg.doc(logpath='Where to save computed data.')
    cfg.default(logpath='%s/log' % (rcdir))

    cfg.doc(feedpath='Directory to check for data sources.')
    cfg.default(feedpath='%s/factors' % (rcdir))

    cfg.doc(weights=[
            'How much each factor counts in the total.',
            'For example:',
            '  weights = [(100, "todo_done"),',
            '             (100, "windows_open"),',
            '             (75, "inboxes"),',
            '             (50, "time_to_live"),',
            '            ]',])
    cfg.default(weights=[])


class Factor:
    """Base class for deriving fuckometer factors.
    See factors/*.py for examples of how to use this.
    """
    def __init__(self, period=60, condition=None, history=None,
                 pad_history=True):
        self.updated_at = 0
        self.period = period
        self.condition = condition
        self.history_size = history
        self.history = []
        self.pad_history = pad_history
        self.raw = 0.0
        self.text = ''

    def fucks(self):
        """How many fucks do we give about the current value?
        Return a float to indicate severity of our situation.
        The scale is:
              0.0 - Everything is great.
            100.0 - We're 100% fucked.
           >100.0 - More than 100% fucked.
        Override this function.
        """
        return self.raw

    def update(self):
        """Do whatever is necessary to gather current data.
        Override this function.
        """
        self.raw = 0.0
        self.text = 'Factor: %.1f' % (self.raw)

    def on_update(self):
        """Override this to execute an action after each update."""
        pass

    def loop(self):
        """Run forever, updating when necessary."""
        while True:
            self.check()
            time.sleep(0.5)

    def __call__(self):
        return self.check()

    def check(self):
        """Update if it's time.  Otherwise don't."""
        now = time.time()
        update_now = False
        if self.condition:
            if self.condition(self.updated_at, now):
                update_now = True
        else:
            if now > (self.updated_at + self.period):
                update_now = True
        if update_now:
            self.update()
            self.updated_at = now
            if self.history_size:
                self.history.append(self.raw)
                # if not populated yet, populate history
                if self.pad_history:
                    while len(self.history) < self.history_size:
                        self.history.append(self.raw)
                # don't grow beyond intended size
                while len(self.history) > self.history_size:
                    del self.history[0]
            self.log()
            self.on_update()
        return self.text

    def log(self):
        """Save current values to files in the factors/ tree."""
        #print('log(fucks=%s, raw=%s): %s' % (self.fucks(), self.raw, self.text))
        basedir = '%s/%s' % (cfg.feedpath, self.path)
        if not os.path.exists(basedir):
            os.makedirs(basedir)

        def save(path, value):
            #print('log(%s): %s' % (path, value))
            path = '%s/%s' % (basedir, path)
            fp = open(path, 'w')
            fp.write('%s\n' % value)
            fp.close()

        save('fucks', self.fucks())
        save('raw', self.raw)
        save('text', self.text)


class Fuckometer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.factors = []
        self.update_seconds = 15.0
        self.history_seconds = 60 * 60
        self.history = []
        self.trend = ''
        self.most_fucked = []

    def update(self):
        if not hasattr(self, 'last_update_time'):
            self.last_update_time = 0.0
        if time.time() - self.last_update_time < 5.0:
            return self.value

        #print('fuckometer.update()')
        # load all configured "factor" data
        self.factors = []
        for weight, name in self.cfg.weights:
            path = '%s/%s/fucks' % (self.cfg.feedpath, name)
            try:
                fp = open(path, 'r')
                value = weight * float(fp.readline())
                fp.close()
            except IOError:
                value = 50.0
            except ValueError:
                value = 50.0
            self.factors.append((value, weight, name))

        # sort by most to least fucked
        self.factors.sort()
        self.factors.reverse()
        # calculate current fuckometer value
        value_sum = sum([f[0] for f in self.factors])
        weight_sum = sum([f[1] for f in self.factors])
        self.factor_weight_sum = weight_sum
        # save the answer
        self.value = value_sum / weight_sum
        self.last_update_time = time.time()

        # figure out which factors contribute the most to being fucked
        self.calc_most_fucked()

        # calculate the overall trend: \, -, or /
        if self.history:
            diff = self.value - self.history[0][0]
            if abs(diff) < 0.66666:
                trend = '-'
            elif diff < 0:
                trend = '\\'
            else:
                trend = '/'
            self.trend = trend

        self.text = 'Fuckometer:%6.2f%% %s' % (self.value, self.trend)

        # save this value for later
        self.history.append((self.value, self.last_update_time))
        # get rid of all entries older than the threshold
        while self.last_update_time - self.history[0][1] > self.history_seconds:
            del self.history[0]
        return self.value

    def calc_most_fucked(self):
        self.most_fucked = [(val, name) for (val, weight, name) in self.factors]
        lines = ['%.2f %s' % (val/self.factor_weight_sum, name)
                for (val, name) in self.most_fucked]
        self.fires = '\n'.join(lines)

    def save(self):
        """Update ~/.fuckometer/* status files if the values have changed.
        """
        # FIXME: inherit this from cfg instead of hardcoding it?
        basedir = '%s/.%s' % (os.environ['HOME'], program_name)

        # cache last-saved values to avoid overwriting when not necessary
        if not hasattr(self, 'prev_value'):
            self.prev_value = None
            self.prev_trend = None
            self.prev_text = None
            self.prev_fires = None

        # don't save more often than necessary
        def s(name, key):
            """save self.key to ~/.fuckometer/name
            (but only if self.key has changed)
            """
            value = getattr(self, key)
            if value != getattr(self, 'prev_%s' % key):
                #print('fuckometer.save(%s)' % (key))
                fp = open('%s/%s' % (basedir, name), 'w')
                fp.write('%s\n' % str(value))
                fp.close()
                setattr(self, 'prev_%s' % (key), value)

        s('raw', 'value')
        s('trend', 'trend')
        s('text', 'text')
        s('fires', 'fires')

    def log(self):
        now = time.time()
        if not hasattr(self, 'prev_log_time'):
            self.prev_log_time = now

        log_now = ten_minutes(self.prev_log_time, now)
        #log_now = one_minute(self.prev_log_time, now)
        if log_now:
            print('fuckometer.log()')
            self.prev_log_time = now
            stamp = time.strftime('%Y-%m-%d %H:%M:%S')
            line = '%s\t%s\n' % (stamp, self.value)
            fp = open(self.cfg.logpath, 'a')
            fp.write(line)
            fp.close()


def six_am(prev, now):
    """Daily at 6am"""
    when = time.localtime(now)
    if (now-prev > 60*60*24*365):  # activate on first call
        return True
    #if (now-prev > 9) and ((when[5]%10) == 6):
    if (now-prev > 60*60) and (when[3] == 6):
      return True
    return False


def ten_minutes(prev, now):
    """Every ten minutes at HH:M0:00"""
    when = time.localtime(now)
    #if (now-prev > 9) and (when[5]%10 == 0):
    if (now-prev > 61) and (when[4]%10 == 0):
      return True
    return False


def one_minute(prev, now):
    """Every minute at HH:MM:00"""
    when = time.localtime(now)
    #if (now-prev > 10) and (when[5]%10 == 0):
    if (now-prev > 10) and (when[5] < 9):
      return True
    return False


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

