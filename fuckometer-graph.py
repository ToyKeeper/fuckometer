#!/usr/bin/env python

import matplotlib as mpl
import pylab as pl


def main(args):
    import time
    import os

    show_avg = False

    last = 0
    for path in args:
        try:
            last = int(path)
            print 'Showing only last %s values' % (last)
            continue
        except ValueError:
            pass

    for path in args:
        if not os.path.exists(path):
            continue
        title = os.path.basename(path)
        points = []
        start = None
        fp = open(path, "rb")
        if last:
            source = fp.readlines()[-last:]
        else:
            source = fp
        for line in source:
            parts = line.split()

            when = time.strptime(' '.join(parts[0:2]), "%Y-%m-%d %H:%M:%S")
            # well, this is convoluted...  1 + days since 0001-01-01
            # (not sure if it does time of day or just date)
            #mplwhen = mpl.dates.datestr2num(time.strftime('%m/%d/%Y %H:%M', when))
            #when = mplwhen
            mplwhen = mpl.dates.datestr2num(time.strftime('%m/%d/%Y', when))
            when = mplwhen + (when[3]/24.0/365.24) + (when[4]/24.0/60.0/365.24) + (when[5]/24.0/60.0/60.0/365.24)

            value = float(parts[2]) * 100.0
            points.append((when, value))

        points = [(when, value) for when,value in points]
        times = [t for t,s in points]
        values = [s for t,s in points]

        # show dates as dates
        #fmt = '%Y-%m-%d'
        #fmt = '%m-%d'
        fmt = '%a'
        pl.gca().xaxis.set_major_formatter(mpl.dates.DateFormatter(fmt))
        #locator = mpl.dates.AutoDateLocator
        #formatter = mpl.dates.AutoDateFormatter(locator)
        #pl.gca().xaxis.set_major_formatter(formatter)
        #pl.gca().xaxis.set_major_locator(mpl.dates.MonthLocator())

        pl.plot(times, values, label=title)

        #pl.gcf().autofmt_xdate()  # tilt the labels so more can fit

        if show_avg:
            # show average value over time...
            # (kinda sucks; needs to be time-based instead of sample-based)
            def end_weighted_mean(data):
                """weighted average, most-recent weighs more"""
                if not data:
                    return 0
                if len(data) == 1:
                    return data[0]
                weighted = [(x*(i+0.5))/(len(data)/2.0) for (i,x) in enumerate(data)]
                result = sum(weighted) / float(len(weighted))
                return result

            samples = 8
            def avg_value(n):
                if n == 0:
                    return values[n]
                elif n < samples:
                    return end_weighted_mean(values[:n+1])
                else:
                    return end_weighted_mean(values[n-samples:n+1])
            avgs = [avg_value(n) for n in range(len(values))]
            pl.plot(times, avgs, label=title + ' (avg)')

    #pl.xlabel('date'); pl.ylabel('fuckometer')
    #pl.legend(loc=0)

    # get rid of the effing padding
    fig = pl.gcf()
    fig.set_frameon(False)
    fig.set_size_inches(4,3)
    fig.tight_layout(pad=0.333)

    # adjust boundaries
    granularity = 5.0
    highest = max(values)
    lowest = min(values)
    #highest = max(100, max(values))
    highest = highest + (granularity - (highest % granularity))
    lowest = lowest - (lowest % granularity)
    #pl.ylim((0.0, highest))
    pl.ylim((lowest, highest))

    pl.xlim((min(times), max(times)))

    #pl.show()
    pl.savefig('/tmp/fuckometer.png')


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

