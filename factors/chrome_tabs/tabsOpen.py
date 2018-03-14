#!/usr/bin/env python

"""This is a shitty kluge to parse a single value out of an IndexedDB file
from a Chrome extension, because as far as I can tell, that is the *only*
way to get an extension to actually write data to disk without caching or
encryption or other fuckery.  But it's a binary file in a format nothing else
seems to support, so I made this script to extract the value I need.
"""

import os

verbose = False
extension_dir = os.environ['HOME'] + '/.config/chromium/Default/IndexedDB/chrome-extension_mibenjgaoiggjllplmamfhkifbodhdaa_0.indexeddb.leveldb'


def main(args):
    # find the most recent IndexedDB transaction log file
    logs = [p for p in os.listdir(extension_dir) if p.startswith('0') and p.endswith('.log')]
    logs.sort()
    infile = '%s/%s' % (extension_dir, logs[-1])
    # only read the last KiB, we don't care about old values
    fp = open(infile, 'rb')
    fp.seek(-1024, 2)

    tabsOpen = 0

    done = False
    def read():
        b = fp.read(1)
        if len(b) == 0:
            raise EOFError, 'end of file'
        return ord(b)

    def read_until_marker(expect='\xff\x0d\xff'):
        for e in expect:
            while read() != ord(e):
                pass

    try:
        while not done:
            read_until_marker('\x08\x00')
            expect = 't\x00a\x00b\x00s\x00O\x00p\x00e\x00n'
            dat = fp.read(len(expect))
            if dat == expect:
                if verbose:
                    print('tabsOpen...')
                # scan until the next marker...  dunno what it means
                read_until_marker('\xff\x0d\xff')
                # how many bytes in our next value? (should be 1 to 4 bytes)
                l = read()
                if l > 6:
                    continue
                # eat a '"'
                q = read()
                if q != 0x22:
                    continue
                # read the encoded value
                # chars are written out of order, like 21436587
                rounded = l + (l%2)
                dat = fp.read(rounded)
                chars = []
                odd = 1
                for i in range(l):
                    chars.append(dat[i+odd])
                    odd *= -1
                text = ''.join(chars)
                tabsOpen = int(text)
                if verbose:
                    print('tabsOpen: %s' % (text,))
    except EOFError:
        pass

    print(tabsOpen)
    return tabsOpen


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

