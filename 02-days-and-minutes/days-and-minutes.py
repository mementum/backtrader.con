#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2017 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import datetime

import backtrader as bt


class St(bt.Strategy):
    params = dict(
        printout=False,
    )

    def __init__(self):
        dsma = bt.ind.SMA(self.dnames.days, period=5)
        self.dsignal = dsignal = bt.ind.CrossOver(self.dnames.days, dsma)
        dsignal.plotinfo.plotname = 'MSignal'

        msma = bt.ind.SMA(self.dnames.minutes, period=10)
        self.msignal = msignal = bt.ind.CrossOver(msma, self.dnames.minutes)
        msignal.plotinfo.plotname = 'DSignal'

        # mixing signals from 2 timeframes
        self.osignal = bt.And(msignal, dsignal.lines[0]())

        # Plotting it
        pi = bt.LinePlotterIndicator(self.osignal, name='osignal')
        pi.plotinfo.plotname = 'OSignal'

    def start(self):
        if self.p.printout:
            print('Len', 'Datetime',
                  'MinLen', 'MinTime', 'MinClose',
                  'DaysLen', 'DaysTime', 'DaysClose',
                  'MinSignal', 'DaysSignal', 'OSignal')

    def next(self):
        if self.p.printout:
            txt = []
            txt.append('{:05d}'.format(len(self)))
            txt.append('{}'.format(self.datetime.datetime()))

            txt.append('{:05d}'.format(len(self.dnames.minutes)))
            txt.append('{}'.format(self.dnames.minutes.datetime.datetime()))
            txt.append('{:.2f}'.format(self.dnames.minutes.close[0]))

            txt.append('{:05d}'.format(len(self.dnames.days)))
            txt.append('{}'.format(self.dnames.days.datetime.datetime()))
            txt.append('{:.2f}'.format(self.dnames.days.close[0]))

            txt.append('{:.2f}'.format(self.msignal[0]))
            txt.append('{:.2f}'.format(self.dsignal[0]))
            txt.append('{:.2f}'.format(self.osignal[0]))
            print(','.join(txt))


def runstrat(args=None):
    args = parse_args(args)

    cerebro = bt.Cerebro()

    # Data feed kwargs
    kwargs = dict(timeframe=bt.TimeFrame.Minutes, compression=5)

    # Parse from/to-date
    dtfmt, tmfmt = '%Y-%m-%d', 'T%H:%M:%S'
    for a, d in ((getattr(args, x), x) for x in ['fromdate', 'todate']):
        if a:
            strpfmt = dtfmt + tmfmt * ('T' in a)
            kwargs[d] = datetime.datetime.strptime(a, strpfmt)

    data0 = bt.feeds.BacktraderCSVData(dataname=args.data0, **kwargs)
    cerebro.adddata(data0, name='minutes')

    cerebro.resampledata(data0, timeframe=bt.TimeFrame.Days, compression=1,
                         name='days')

    # Broker
    cerebro.broker = bt.brokers.BackBroker(**eval('dict(' + args.broker + ')'))

    # Sizer
    cerebro.addsizer(bt.sizers.FixedSize, **eval('dict(' + args.sizer + ')'))

    # Strategy
    cerebro.addstrategy(St, **eval('dict(' + args.strat + ')'))

    # Execute
    cerebro.run(**eval('dict(' + args.cerebro + ')'))

    if args.plot:  # Plot if requested to
        cerebro.plot(**eval('dict(' + args.plot + ')'))


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            'Sample Skeleton'
        )
    )

    parser.add_argument('--data0', default='../../datas/2006-min-005.txt',
                        required=False, help='Data to read in')

    if False:
        parser.add_argument('--data0',
                            default='../../datas/2005-2006-day-001.txt',
                            required=False, help='Data to read in')

    # Defaults for dates
    parser.add_argument('--fromdate', required=False, default='',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--todate', required=False, default='',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--cerebro', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--broker', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--sizer', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--strat', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--plot', required=False, default='',
                        nargs='?', const='{}',
                        metavar='kwargs', help='kwargs in key=value format')

    return parser.parse_args(pargs)


if __name__ == '__main__':
    runstrat()
