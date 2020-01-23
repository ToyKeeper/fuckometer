#!/usr/bin/env python

# fuck you python; why make it so hard to cleanly import from parent dir?
from os.path import dirname, abspath
import sys ; sys.path.insert(1, dirname(dirname(abspath(__file__))))

import math
import os
import subprocess
import time

import fuckometer

# try to increase worth by at least this much each month
monthly_goal = 1000
beanfile = '%s/bank/bean/selene.bean' % (os.environ['HOME'])

datefmt = '%Y-%m-%d'


def main(args):
    fuckometer.init()
    cashflow = Beancount(condition=fuckometer.six_am)
    if args:  # just run once, print info, and exit
        cashflow.update()
        print(cashflow.text)
        f = cashflow.fucks()
        print('Fucks: %.2f' % (f))
    else:
        cashflow.loop()  # run forever


class Beancount(fuckometer.Factor):
    """Money flow gauge from Beancount
    Gauges monetary situation based on cash flow for the most-recent month on 
    record.
    """

    path = 'money_flow'

    def fucks(self):
        adjusted = self.raw - monthly_goal
        balance_fucks = 100.0 * (2.0 - math.log(max(1,self.raw2-20000), 500))
        if adjusted > 0:
            flow_fucks = -math.sqrt(adjusted)
        else:
            flow_fucks = math.sqrt(-adjusted)
        if fuckometer.cfg.verbose:
            print('balance_fucks: %s' % balance_fucks)
            print('flow_fucks: %s' % flow_fucks)
        fucks = balance_fucks + flow_fucks
        return fucks

    def on_update(self):
        if fuckometer.cfg.verbose:
            print(self.text)
            print('Fucks: %s' % self.fucks())

    def update(self):
        self.raw = self.flow_last_month()
        self.raw2 = self.current_balance
        sign = '+'
        if self.raw < 0: sign = '-'
        amt = abs(self.raw)
        self.text = 'Money: %s$%.2f / M' % (sign, amt)

    def detect_start_date(self):
        """Return a date one month before the last recorded transaction.
        """
        # returns all transactions in order
        cmd = ('bean-query', beanfile, 'select *;')
        err, text = run(cmd)
        text = text[-1000:]
        lines = text.split('\n')
        lines = [l for l in lines if l.strip()]
        parts = lines[-1].split()
        date = parts[0]
        when = list(time.strptime(date, datefmt))
        when[1] -= 1  # one month ago
        when = time.localtime(time.mktime(when))
        #print(when)
        return when

    def flow_last_month(self):
        begin = self.detect_start_date()
        begin = time.strftime(datefmt, begin)

        before = self.balance(begin)
        after = self.balance_now()

        flow = after - before
        return flow

    def balance(self, when):
        cmd = ('bean-query', beanfile,
                'balances at cost from close on %s where account ~ "Assets" and currency="USD";' % (when,))
        err, text = run(cmd)
        #print(text)
        lines = [l.strip() for l in text.split('\n') if ' USD' in l]
        #print(lines)
        total = 0.0
        for line in lines:
            parts = line.split()
            amount = float(parts[1])
            total += amount
        return total

    def balance_now(self):
        when = time.strftime(datefmt)
        balance = self.balance(when)
        self.current_balance = balance
        if fuckometer.cfg.verbose:
            print('balance_now(): %s' % balance)
        return balance


def run(cmd):
    """Execute a command (tuple), return its errcode and text output"""
    err = 0
    text = ''

    # catches stdout+stderr+retcode
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, close_fds=True)
    # wait for process to finish and get its output
    stdout, foo = p.communicate()
    text = stdout.decode()
    err = p.returncode

    return err, text


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

