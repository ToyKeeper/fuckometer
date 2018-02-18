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

# TODO: split fuckometer data into a bunch of individual files in a subdir,
#       with a config somewhere to select them and assign weights to each
# TODO: generate fuckometer data points from a bunch of independent processes
#       instead of all in one
# TODO: split fuckometer into its own standalone script
# TODO: maybe make each line of the display its own file, writable by anything?

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

    dryrun = False
    fucklogpath = 'fuckometer.log'

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


    # periodically log the fuckometer value so I can graph it later
    if not cfg.dryrun:
        fucklog = PeriodicLog(cfg.logpath, fuckometer, condition=ten_minutes)

    f = Fuckometer(cfg)
    #f.update()

    #print('Fuckometer: %s' % (f.value))

    while True:
        f.update()
        print('Fuckometer: %s' % (f.value))

        if not cfg.dryrun:
            fucklog()

        if cfg.once:
            return

        time.sleep(5)


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
    def __init__(self, period=60, condition=None, history=None):
        self.updated_at = 0
        self.period = period
        self.condition = condition
        self.history_size = history
        self.history = []
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
                self.values.append(self.raw)
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


class Periodic:
    def __init__(self, update=None, period=60*60, condition=None, history=None):
        self.period = period
        if update: self.update = update
        self.updated_at = 0
        self.value = 0.0
        self.text = ''
        self.condition = condition
        self.history = history
        if history:
            self.values = []

    def __call__(self):
        now = time.time()
        update_now = False
        if self.condition:
            if self.condition(self.updated_at, now):
                update_now = True
        else:
            if now > (self.updated_at + self.period):
                update_now = True
        if update_now:
            self.value, self.text = self.update()
            self.updated_at = now
            if self.history:
                self.values.append(self.value)
                while len(self.values) > self.history:
                    del self.values[0]
        return self.text

    def update(self):
        return 0, ''


class PeriodicLog(Periodic):
    def __init__(self, path, obj, *args, **kwargs):
        Periodic.__init__(self, *args, **kwargs)
        self.path = path
        self.obj = obj

    def update(self):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        line = '%s\t%s\n' % (now, self.obj.value)
        fp = open(self.path, 'a')
        fp.write(line)
        fp.close()
        return 0, ''


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
    if (now-prev > 60*9) and (when[4]%10 == 0):
      return True
    return False


def datetime():
    if not hasattr(datetime, 'colons'):
        datetime.colons = True
    else:
        datetime.colons = not datetime.colons

    if datetime.colons:
        colon = ':'
    else:
        colon = ' '
    #fmt = '%%Y-%%m-%%d %%H%s%%M%s%%S' % (colon, colon)
    fmt = ' %%a %%m-%%d %%H%s%%M%s%%S' % (colon, colon)
    return time.strftime(fmt)


class Fuckometer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.factors = []

    def update(self):
        self.factors = []
        for weight, name in self.cfg.weights:
            path = '%s/%s/fucks' % (self.cfg.feedpath, name)
            fp = open(path, 'r')
            value = weight * float(fp.readline())
            fp.close()
            self.factors.append((value, weight, name))

        value_sum = sum([f[0] for f in self.factors])
        weight_sum = sum([f[1] for f in self.factors])
        self.value = value_sum / weight_sum
        return self.value

    def save(self):
        # FIXME: detect this instead of hardcoding it
        path = '%s/%s/now' % (os.environ['HOME'], '.fuckometer')
        fp = open(path, 'w')
        fp.write('%s\n' % str(self.value))
        fp.close()


def fuckometer_update():
    factors = []

    # Steins;Gate world line divergence number
    # (meh, too random, makes fuckometer less meaningful)
    #factors.append(max(0.0, 1.0 - divergence.value))

    # how close am I to death?
    factors.append(max(0.0, (20-deathclock.value) / 10.0))

    # factor in number of windows / tabs currently open
    open_windows()
    windows = open_windows.value
    value = (windows - 100) / 250.0
    value = min(1.0, max(0.0, value))
    factors.append(value)

    # factor in the state of my todo list today
    todo_list()
    factors.append(todo_list.value)

    # TODO: gather the actual data async, and save it to files in a subdir,
    #       then simply load the data here quickly
    # TODO: give each factor a weight value
    # TODO: factor in recent monetary flow and balance
    # TODO: factor in my overall health
    #       (have I exercised lately?  is my weight too high/low?)
    # TODO: factor in recent news
    # TODO: factor in how much time I've spent working today vs slacking
    # TODO: factor in unprocessed papers?
    # TODO: factor in windows open on my other computer(s)
    # TODO: factor in current weather
    # TODO: factor in the size of my combined email inboxes
    # TODO: factor in my tkdo data (avg of top 20 items?)

    # average the values
    value = sum(factors) / len(factors)
    value = max(0.0, value)

    # include trend info: /, -, \ 
    prev = value
    diff = 0.0
    if len(fuckometer.values) > 1:
        diff = 100.0 * (value - fuckometer.values[0])
    if abs(diff) < 0.66666:
        trend = '-'
    elif diff < 0:
        trend = '\\'
    else:
        trend = '/'

    #return value, 'Fuckometer: %.0f%%' % (100.0 * value)
    return value, 'Fuckometer: %5.1f%% %s' % (100.0 * value, trend)


# FIXME: defining this globally is a nasty kludge
fuckometer = Periodic(fuckometer_update, 60, history=60)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

