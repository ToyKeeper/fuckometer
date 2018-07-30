#!/usr/bin/env python

import time

lcd = None


def main(args):
    init()

    lines = [
            ' ' * 20,
            '  Well hello there! ',
            ' How are you today? ',
            ' ' * 20,
            ]
    lcdwrite(lines)


def lcdclear():
    lcd.write('\xfe\x58')
    lcd.flush()


def reset_cursor():
    lcd.write('\xfe\x48')
    lcd.flush()


def lcdwrite(lines):
    #lcdclear()
    reset_cursor()

    seq = 0, 2, 1, 3
    for n in seq:
        line = lines[n][:20]
        # replace Yen symbol (WTF, MtxOrb?) w/ custom backslash glyph
        line = line.replace('\\', chr(0))
        lcd.write(line)
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

    up = [
            (0, 0, 1, 0, 0),
            (0, 1, 1, 1, 0),
            (1, 0, 1, 0, 1),
            (0, 0, 1, 0, 0),
            (0, 0, 1, 0, 0),
            (0, 0, 1, 0, 0),
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

    down = [
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 1, 0, 0),
            (0, 0, 1, 0, 0),
            (0, 0, 1, 0, 0),
            (1, 0, 1, 0, 1),
            (0, 1, 1, 1, 0),
            (0, 0, 1, 0, 0),
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

    customs = (backslash, upright, right, downright, up, down)

    for i, custom in enumerate(customs):
        data = to_bytes(custom)
        # define custom char
        lcd.write('\xfe\x4e' + chr(i))
        lcd.write(data)


def init(path=None):
    global lcd
    if not path:
        path = '/dev/ttyUSB1'
    import serial
    #lcd = open(path, 'wb')
    lcd = serial.Serial(port=path, baudrate=19200, rtscts=False, dsrdtr=False)
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

