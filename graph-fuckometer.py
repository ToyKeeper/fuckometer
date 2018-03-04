#!/usr/bin/env python

import math
import matplotlib as mpl
import pylab as pl


def main(args):
    """fuckometer-graph.py: Makes graphs of fuckometer data.
    Usage: ./fuckometer-graph.py fuckometer.log 1008 -o fuckometer-7d.png
    Options:
      -o F  --out     Save graph to file F.
      -n N  --last    Only show the last N entries.
      -c    --conky   Format graph for use in conky.
    """
    import time
    import os

    show_avg = True
    conky_mode = False
    conky_scale = 1.0
    linecolor = '#aa4444'
    avgcolor = '#ffbbbb'
    shade = '#000000'

    last = 0
    sourcefiles = []
    destfile = '/tmp/fuckometer.png'
    i = 0
    while i < len(args):
        a = args[i]
        if a in ('-h', '--help'):
            return usage()
        elif a in ('-o', '--out'):
            i += 1
            a = args[i]
            destfile = a
        elif a in ('-n', '--last'):
            i += 1
            a = args[i]
            last = int(a)
        elif a in ('-c', '--conky'):
            conky_mode = True
            conky_scale = 0.4
            pl.rcParams['axes.facecolor'] = 'black'
            pl.rcParams['figure.facecolor'] = 'black'
            pl.rcParams['figure.edgecolor'] = 'black'
            pl.rcParams['savefig.edgecolor'] = 'black'
            pl.rcParams['savefig.facecolor'] = 'black'
            pl.rcParams['savefig.pad_inches'] = 0.0
            pl.rcParams['savefig.transparent'] = True
            #print(pl.rcParams)
            linecolor = '#ff0000'
            avgcolor = '#880000'
            shade = '#ffffff'
        else:
            try:
                last = int(a)
            except ValueError:
                sourcefiles.append(a)

        i += 1

    for path in sourcefiles:
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
            # don't change date until 6am after midnight
            when = time.localtime(time.mktime(when) - (6*60*60))
            # well, this is convoluted...  1 + days since 0001-01-01
            # (not sure if it does time of day or just date)
            #mplwhen = mpl.dates.datestr2num(time.strftime('%m/%d/%Y %H:%M', when))
            #when = mplwhen
            #mplwhen = mpl.dates.datestr2num(time.strftime('%m/%d/%Y', when))
            mplwhen = mpl.dates.datestr2num(time.strftime('%Y-%m-%d %H:%M', when))
            #when = mplwhen + (when[3]/24.0/365.24) + (when[4]/24.0/60.0/365.24) + (when[5]/24.0/60.0/60.0/365.24)
            when = mplwhen

            value = float(parts[2])
            points.append((when, value))

        points = [(when, value) for when,value in points]
        times = [t for t,s in points]
        values = [s for t,s in points]

        # show dates as dates
        #fmt = '%Y-%m-%d %H:%M'
        #fmt = '%Y-%m-%d'
        #fmt = '%m-%d'
        fmt = '%a'
        pl.gca().xaxis.set_major_formatter(mpl.dates.DateFormatter(fmt))
        #locator = mpl.dates.AutoDateLocator
        #formatter = mpl.dates.AutoDateFormatter(locator)
        #pl.gca().xaxis.set_major_formatter(formatter)
        #pl.gca().xaxis.set_major_locator(mpl.dates.MonthLocator())


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

            def mean(data):
                result = sum(data) / float(len(data))
                return result

            samples = 6
            def avg_value(n):
                #func = end_weighted_mean
                func = mean
                if n == 0:
                    return values[n]
                elif n < samples:
                    #return end_weighted_mean(values[:n+1])
                    return func(values[:n+1])
                else:
                    #return end_weighted_mean(values[n-samples:n+1])
                    return func(values[n-samples:n+1])
            avgs = [avg_value(n+3) for n in range(len(values))]
            pl.plot(times, avgs, label=title + ' (avg)',
                    color=avgcolor, linewidth=8*conky_scale)


        pl.plot(times, values, label=title, color=linecolor,
                linewidth=2*conky_scale)

    # shade every other day
    begin = times[0]
    end = times[-1]
    span = end - begin
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
            pl.axvspan(left, right, facecolor=shade, alpha=alpha,
                       ymax=1.0, ymin=0.0)

    #pl.xlabel('date'); pl.ylabel('fuckometer')
    #pl.legend(loc=0)

    # get rid of the effing padding
    fig = pl.gcf()
    fig.set_frameon(False)
    bbox_inches = 'tight'
    pad_inches = 0.05
    granularity = 2.0
    # change image size based on the amount of data
    if len(values) < 500:
        fig.set_size_inches(4,3)
    else:
        fig.set_size_inches(8,3)
    fig.tight_layout(pad=0.0)
    if conky_mode:
        scale = 0.2125  # 85x63 pixels
        fig.set_size_inches(scale*4,scale*3)
        # scale almost as wide as possible
        granularity = 1.0
        # get rid of as much padding as possible
        fig.axes[0].get_xaxis().set_visible(False)
        fig.axes[0].get_yaxis().set_visible(False)
        ax = pl.Axes(fig, [0,0,1,1])
        bbox_inches = 0.0
        pad_inches = 0.0
        fig.subplots_adjust(left=0.01, bottom=0.03, right=1-0.02, top=1-0.03, wspace=0, hspace=0)

    # adjust boundaries
    highest = max(values)
    lowest = min(values)
    highest = highest + (granularity - (highest % granularity))
    lowest = lowest - (lowest % granularity)
    pl.ylim((lowest, highest))
    #pl.ylim((0, 100))

    pl.xlim((min(times), max(times)))

    pl.savefig(destfile, bbox_inches=bbox_inches, pad_inches=pad_inches)
    #pl.show()


def usage():
    print(main.__doc__)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

