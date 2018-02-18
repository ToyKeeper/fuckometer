#!/usr/bin/env python

import os
import random
import time

import mtxorb
import pycfg

cfg = None
program_name = 'fuckometer_lcd'


def main(args):
    """Fuckometer LCD clock.
    Usage: ./clock.py [options]
    Options include:
      -h   --help      Display this info, and exit.
      -t   --text      Display only in text in the terminal.
      -l D --lcd D     Display on the LCD at device D.
                       (default /dev/ttyUSB1)
    """

    global cfg
    cfg = pycfg.config(program_name)
    set_defaults(cfg)
    cfg.load()

    i = 0
    while i < len(args):
        a = args[i]
        if a in ('-h', '--help'):
            return usage()
        elif a in ('-c', '--cfg'):
            print(cfg)
            return
        elif a in ('-t', '--text'):
            cfg.use_lcd = False
        elif a in ('-l', '--lcd'):
            i += 1
            a = args[i]
            cfg.lcdpath = a
            if os.path.exists(cfg.lcdpath):
                cfg.use_lcd = True
        else:
            return usage()

        i += 1

    randoms = [ topfire(), ]
    for name, interval in [
            ('chrome_tabs', 60),
            ('email_inboxes', 60),
            ('email_todo', 60),
            ('steins_gate', 300),
            ('time_to_live', 300),
            ('tkdo_scores', 60),
            ('todo_list', 180),
            ('todo_list', 180),
            ('todo_list', 180),
            ('windows_open', 60),
            ]:
        randoms.append(fucksource(name, interval))

    r1 = randomized(randoms, None, 30)
    r2 = randomized(randoms, r1, 10)

    feeds = [
            datetime,
            #fucksource('time_to_live', interval=300),
            #fucksource('todo_list'),
            r1,
            r2,
            fuckometer(),
            ]

    if cfg.use_lcd:
        mtxorb.init(cfg.lcdpath)

    while True:
        lines = ['%-20s' % (func()[:20]) for func in feeds]

        if cfg.use_lcd:
            if random.random() < 0.01:
                mtxorb.lcdclear()
            mtxorb.lcdwrite(lines)
        else:
            print('-' * 20)
            for line in lines:
                print(line)

        sleep_until_500ms()


def usage():
    print(main.__doc__)


def set_defaults(cfg):
    home = os.environ['HOME']

    cfg.doc(fuckometer_path='Where to find the .fuckometer/ dir.')
    cfg.default(fuckometer_path='%s/.fuckometer' % (home))

    cfg.doc(use_lcd=['If true, use an external LCD.',
                     'If false, print text in terminal.'])
    cfg.default(use_lcd=False)

    cfg.doc(lcdpath=[
            'Path to LCD device.',
            '/dev/ttyUSB1',
            ])
    cfg.default(lcdpath = '/dev/ttyUSB1')


def sleep_until_500ms():
    """Wait until clock is evenly divisible by 0.5s.
    (and wait at least until the next occurrence)
    """
    time.sleep(0.1)
    while time.time() % 0.5 > 0.06:
        time.sleep(0.02)


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


def periodic(path, interval=10):
    def func():
        if not hasattr(func, 'value'):
            func.value = ''
        if not hasattr(func, 'updated_at'):
            func.updated_at = 0.0
        now = time.time()
        if (now - func.updated_at) > interval:
            #print('update(%s)' % (path))
            func.updated_at = now
            fp = open(path)
            func.value = fp.readline().strip()
            fp.close()
        return func.value

    return func


def fucksource(name, interval=10):
    path = '%s/factors/%s/text' % (cfg.fuckometer_path, name)
    return periodic(path, interval)


def fuckometer():
    interval = 10
    path = '%s/text' % (cfg.fuckometer_path)
    return periodic(path, interval)


def topfire():
    # FIXME: formatting is bad
    # FIXME: should show more than just the biggest fire
    interval = 60
    path = '%s/fires' % (cfg.fuckometer_path)
    return periodic(path, interval)


def randomized(sources, compare=None, interval=10):
    def func():
        # init
        if not hasattr(func, 'index'):
            func.index = 0
        if not hasattr(func, 'rotated_at'):
            func.rotated_at = 0.0

        now = time.time()
        if (now - func.rotated_at) > interval:
            # randomize...
            # but don't randomly pick the same as another randomizer instance
            comp = None
            if compare:
                comp = compare.index
            func.index = comp
            while func.index == comp:
                func.index = random.randint(0, len(sources)-1)

            func.rotated_at = now

        return sources[func.index]()

    return func


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

