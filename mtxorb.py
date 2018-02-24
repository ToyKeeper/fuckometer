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
    return ord(c)
    #c = ord(c)
    #if c < 128:
    #    return 1 + (254 - (c<<1))
    #return c


def lcdclear():
    #lcd.write('8')
    lcd.write('\xfe\x58')
    lcd.flush()
    time.sleep(lcddelay)


def reset_cursor():
    lcd.write('\xfe\x48')
    lcd.flush()
    time.sleep(lcddelay)


def lcdwrite(lines):
    #lcdclear()
    reset_cursor()

    #lines = lines[:]
    #f=0
    #lines[0] = ''.join(chr(n) for n in range(f,f+8))

    seq = 0, 2, 1, 3
    for n in seq:
        line = lines[n][:20]
        line = line.replace('\\', chr(0))
        lcd.write(line)
        #for c in line:
        #    c = (chr2lcd(c))
        #    lcd.write(chr(c))
        #    lcd.flush()
        #    time.sleep(lcddelay)
    lcd.flush()


def set_custom_chars():
    backslash = [
            (0, 0, 0, 0, 0),
            (1, 0, 0, 0, 0),
            (0, 1, 0, 0, 0),
            (0, 0, 1, 0, 0),
            (0, 0, 0, 1, 0),
            (0, 0, 0, 0, 1),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            ]

    upright = [
            (0, 1, 1, 1, 1),
            (0, 0, 0, 1, 1),
            (0, 0, 1, 0, 1),
            (0, 1, 0, 0, 1),
            (1, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            ]

    right = [
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 1, 0, 0),
            (0, 0, 0, 1, 0),
            (1, 1, 1, 1, 1),
            (0, 0, 0, 1, 0),
            (0, 0, 1, 0, 0),
            (0, 0, 0, 0, 0),
            ]

    downright = [
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (1, 0, 0, 0, 0),
            (0, 1, 0, 0, 1),
            (0, 0, 1, 0, 1),
            (0, 0, 0, 1, 1),
            (0, 1, 1, 1, 1),
            ]

    def to_bytes(bits):
        result = []
        for row in bits:
            x = 0
            for bit in row:
                x <<= 1
                x += bit
            result.append(chr(x))
        return ''.join(result)

    customs = (backslash, upright, right, downright)

    for i, custom in enumerate(customs):
        data = to_bytes(custom)
        # define custom char
        lcd.write('\xfe\x4e' + chr(i))
        lcd.write(data)


def init(path=None):
    global lcd
    if not path:
        path = '/dev/ttyUSB1'
    lcd = open(path, 'wb')
    # turn cursor off
    lcd.write('\xfe\x4b') ; lcd.flush()
    # init large digits
    lcd.write('\xfe\x6e') ; lcd.flush()
    # fix some font issues
    set_custom_chars()
    lcdclear()


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

