#!/usr/bin/env python

import math
import matplotlib as mpl
import pylab as pl


def main(args):
    """factor-graph.py: Makes graphs of fuckometer factor data.
    Usage: ./factor-graph.py factors.log 1008 -o factors-7d.png
    Options:
      -o F  --out     Save graph to file F.
      -d N  --days    Only show the last N days of data.
    """
    import time
    import os

    show_avg = True

    days = 7
    sourcefile = ''
    destfile = '/tmp/factors.png'
    i = 0
    while i < len(args):
        a = args[i]
        if a in ('-h', '--help'):
            return usage()
        elif a in ('-o', '--out'):
            i += 1
            a = args[i]
            destfile = a
        elif a in ('-d', '--days'):
            i += 1
            a = args[i]
            days = float(a)
        elif a in ('-n', '--dryrun', '--dry-run'):
            cfg.dryrun = True
        elif a in ('-1', '--once'):
            cfg.once = True
        else:
            sourcefile = a

        i += 1

    if not sourcefile:
        return usage()

    now = time.time()
    graph_start = now
    graph_end = 0.0
    graph_top = 0.0
    graph_bottom = 100.0
    factors = {}

    for path in [sourcefile]:
        if not os.path.exists(path):
            continue
        #title = os.path.basename(path)
        start = now - (days * 60 * 60 * 24)
        fp = open(path, "rb")
        source = fp
        for line in source:
            parts = line.split('\t')
            #print('parts: %s' % (parts,))

            when = time.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
            stamp = time.mktime(when)

            # only show last N days
            if stamp < start:
                continue

            # don't change date until 6am after midnight
            when = time.localtime(time.mktime(when) - (6*60*60))
            # well, this is convoluted...  1 + days since 0001-01-01
            mplwhen = mpl.dates.datestr2num(time.strftime('%Y-%m-%d %H:%M', when))
            when = mplwhen

            if when < graph_start:
                graph_start = when
            if when > graph_end:
                graph_end = when

            name = parts[1]
            value = float(parts[2])

            #print('when: %s, name: %s, value: %s' % (when, name, value))

            if value > graph_top:
                graph_top = value
            if value < graph_bottom:
                graph_bottom = value

            if name not in factors:
                factors[name] = []

            factors[name].append((when, value))

        # sort by most-recent value, descending
        foo = [(-factors[name][-1][1], name) for name in factors.keys()]
        foo.sort()
        names = [x[-1] for x in foo]
        # sort by name
        #names = factors.keys()
        #names.sort()
        for name in names:
            #print(name)
            times = [t for t,s in factors[name]]
            values = [s for t,s in factors[name]]
            title = '%.1f %s' % (values[-1], name)
            pl.plot(times, values, label=title, linewidth=5, alpha=0.666)

    # show dates as dates
    #fmt = '%Y-%m-%d %H:%M'
    #fmt = '%Y-%m-%d'
    #fmt = '%m-%d'
    fmt = '%a'
    pl.gca().xaxis.set_major_formatter(mpl.dates.DateFormatter(fmt))

    # shade every other day
    begin = graph_start
    end = graph_end
    span = end - begin
    color = '#000000'
    alpha = 0.05
    if span > 0.1:
        #print('%.2f days spanned.' % (span))
        # ensure today is never shaded
        odd = 0
        if span % 2 > 1:
            odd = 1
            #print('Odd.')
        # kludge: was backward when 0.01 < fpart(span) < 0.49
        if span % 1 < 0.5:
            odd -= 1
            #print('Odder.')
        # add a grey background to yesterday and every 2 days before
        for offset in range(odd, int(math.ceil(span)+1), 2):
            left = math.floor(begin) + offset
            right = left + 1
            pl.axvspan(left, right, facecolor=color, alpha=alpha,
                       ymax=1.0, ymin=0.0)

    #pl.xlabel('date'); pl.ylabel('fuckometer')
    pl.legend(loc=2, bbox_to_anchor=(1.02, 1), borderaxespad=0.0)

    # get rid of the effing padding
    fig = pl.gcf()
    fig.set_frameon(False)
    # change image size based on the amount of data
    if span < 3:
        fig.set_size_inches(4,3)
    else:
        fig.set_size_inches(8,3)
    fig.tight_layout(pad=0.0)

    # adjust boundaries
    granularity = 10.0
    highest = graph_top
    lowest = graph_bottom
    highest = highest + (granularity - (highest % granularity))
    lowest = lowest - (lowest % granularity)
    pl.ylim((lowest, highest))

    pl.xlim((graph_start, graph_end))

    pl.savefig(destfile, bbox_inches='tight')
    #pl.show()


def usage():
    print(main.__doc__)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

