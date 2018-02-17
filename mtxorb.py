#!/usr/bin/env python

import time

chars = {
        ' ': 36,
        '!': 189,
        '"': 187,
        '#': 185,
        '$': 183,
        '%': 181,
        '&': 179,
        '(': 175,
        ')': 173,
        '*': 171,
        '+': 169,
        ',': 167,
        '-': 165,
        '.': 163,
        '/': 161,
        '0': 159,
        '1': 157,
        '2': 155,
        '3': 153,
        '4': 151,
        '5': 149,
        '6': 147,
        '7': 145,
        '8': 143,
        '9': 141,
        ':': 139,
        ';': 137,
        '<': 135,
        '=': 133,
        '>': 131,
        '?': 129,
        '@': 127,
        'A': 125,
        'B': 123,
        'C': 121,
        'D': 119,
        'E': 117,
        'F': 115,
        'G': 113,
        'H': 111,
        'I': 109,
        'J': 107,
        'K': 105,
        'L': 103,
        'M': 101,
        'N': 99,
        'O': 97,
        'P': 95,
        'Q': 93,
        'R': 91,
        'S': 89,
        'T': 87,
        'U': 85,
        'V': 83,
        'W': 81,
        'X': 79,
        'Y': 77,
        'Z': 75,
        '[': 73,
        '': 71,
        ']': 69,
        '': 67,
        '_': 65,
        '': 63,
        'a': 61,
        'b': 59,
        'c': 57,
        'd': 55,
        'e': 53,
        'f': 51,
        'g': 49,
        'h': 47,
        'i': 45,
        'j': 43,
        'k': 41,
        'l': 39,
        'm': 37,
        'n': 35,
        'o': 33,
        'p': 31,
        'q': 29,
        'r': 27,
        's': 25,
        't': 23,
        'u': 21,
        'v': 19,
        'w': 17,
        'x': 15,
        'y': 13,
        'z': 11,
        '': 9,
        '': 7,
        '': 5,
        '': 3,
        '': 1,
        }

lcd = None
lcddelay = 0.001

def main(args):
    global lcd
    lcd = open('/dev/ttyUSB1', 'wb')
    # clear the screen
    lcd.write('8') ; lcd.flush() ; time.sleep(0.5)

    if 0:
        while True:
            for n in range(75, 0, -1):
                data = n
                print(data)
                lcd.write(chr(data))
                lcd.flush()
                time.sleep(3)

    if 0:
        for c in 'Hello there.':
            b = chr2lcd(c)
            lcd.write(chr(b))
            #lcd.flush()
            #time.sleep(0.1)
        lcd.flush()

    if 1:
        lines = [
                ' ' * 20,
                '  Well hello there! ',
                ' How are you today? ',
                ' ' * 20,
                ]
        lcdwrite(lines)

def chr2lcd(c):
    #c = ord(c)
    #c = (c) + 130
    #if c in chars:
    #   return chars[c]
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

