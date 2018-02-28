#!/usr/bin/env python

import os
import random
import time

import mtxorb
import pycfg

cfg = None
program_name = 'fuckometer_lcd'

# TODO: maybe make each line of the display its own file, writable by anything?
# TODO: don't hardcode LCD size

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
            cfg.use_terminal = True
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
            ('tkdo_scores', 300),
            ('tkdo_scores', 300),
            ('todo_list', 300),
            ('todo_list', 300),
            ('todo_list', 300),
            ('windows_open', 60),
            ]:
        randoms.append(fucksource(name, interval))

    r1 = randomized(randoms, None, 31)
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
        lines = render(feeds)

        # display precisely every half-second at 0.0s and 0.5s
        sleep_until_500ms()
        # update the date line again to make sure the clock is spot-on
        for i, func in enumerate(feeds):
            if func == datetime:
                lines[i] = '%-20s' % (datetime()[:20])

        if cfg.use_lcd:
            # replace trend char with a graphic
            # (because MtxOrb displays have no backslash glyph)
            lcopy = lines[:]
            #trends = {'/':0, '-':4, '\\':2}  # bigchars font
            trends = {'/':1, '-':2, '\\':3, '^':4, 'v':5}  # my custom font
            trend = lcopy[3][-1]
            if trend in trends:
                lcopy[3] = lcopy[3][:-1] + chr(trends[trend])
            # actually update the screen
            mtxorb.lcdwrite(lcopy)
        if cfg.use_terminal:
            print('-' * 20)
            for line in lines:
                print(line)


def usage():
    print(main.__doc__)


def set_defaults(cfg):
    home = os.environ['HOME']

    cfg.doc(fuckometer_path='Where to find the .fuckometer/ dir.')
    cfg.default(fuckometer_path='%s/.fuckometer' % (home))

    cfg.doc(use_terminal=['If true, print to the terminal.'])
    cfg.default(use_terminal=True)

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
    now = time.time()
    if (now % 1.0) < 0.5:
        colon = ':'
    else:
        colon = ' '

    fmt = ' %%a %%m-%%d %%H%s%%M%s%%S' % (colon, colon)
    return time.strftime(fmt, time.localtime(now))


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
            lines = [l.strip() for l in fp.readlines() if l.strip()]
            func.value = random.choice(lines)
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
            # FIXME: make avoidance work both ways,
            #        two instances avoiding each other, instead of just one
            comp = None
            if compare:
                comp = compare.index
            func.index = comp
            while func.index == comp:
                func.index = random.randint(0, len(sources)-1)

            func.rotated_at = now

        return sources[func.index]()

    return func


def render(feeds):
    # remember state
    if not hasattr(render, 'scrolls'):
        render.scrolls = [0, 0, 0, 0]
    if not hasattr(render, 'prev_values'):
        render.prev_values = ['', '', '', '']

    # convenience
    scrolls = render.scrolls
    prev_values = render.prev_values

    values = ['%s' % func() for func in feeds]

    # reset scroll position on value change
    for i, v in enumerate(values):
        if v != prev_values[i]:
            scrolls[i] = 0
            prev_values[i] = v

    #lines = ['%-20s' % (v[scrolls[i]:scrolls[i]+20]) for i,v in enumerate(values)]
    # instead of that simple solution, let's make long lines scroll
    lines = []
    for i, v in enumerate(values):
        # short lines are easy
        if len(v) <= 20:
            text = '%-20s' % (v[scrolls[i]:scrolls[i]+20])
        else:
            # scroll long entries in a continuous loop
            v_orig = len(v)
            v = v + '  ' + v
            text = '%-20s' % (v[scrolls[i]:scrolls[i]+20])
            scrolls[i] += 1
            if scrolls[i] > v_orig + 2:
                scrolls[i] -= v_orig + 2

        lines.append(text)

    return lines


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

