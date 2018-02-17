#!/usr/bin/env python

import time

lcd = None
lcddelay = 0.001


def main(args):
    init()

    lines = [
            ' ' * 20,
            '  Well hello there! ',
            ' How are you today? ',
            ' ' * 20,
            ]
    lcdwrite(lines)


def chr2lcd(c):
    c = ord(c)
    if c < 128:
        return 1 + (254 - (c<<1))
    return c


def lcdclear():
    lcd.write('8')
    lcd.flush()
    time.sleep(lcddelay)


def lcdwrite(lines):
    #lcdclear()
    seq = 0, 2, 1, 3
    for n in seq:
        line = lines[n][:20]
        for c in line:
            c = (chr2lcd(c))
            lcd.write(chr(c))
            lcd.flush()
            time.sleep(lcddelay)
    lcd.flush()


def init():
    global lcd
    lcd = open('/dev/ttyUSB1', 'wb')
    lcdclear()


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

