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
from backtrader.utils import flushfile  # win32 quick stdout flushing


class St(bt.Strategy):
    params = dict(
    )

    def __init__(self):
        dsma = bt.ind.SMA(self.dnames.days, period=5)
        dsignal = bt.ind.CrossOver(self.dnames.days, dsma)

        msma = bt.ind.SMA(self.dnames.minutes, period=10)
        msignal = bt.ind.CrossOver(msma, self.dnames.minutes)

        self.osignal = bt.And(msignal, dsignal())

    def start(self):
        header = [
            'Datetime', 'Open', 'High', 'Low', 'Close', 'Volume',
            # 'SMA'
        ]
        print(', '.join(header))

    def notify_data(self, data, status, *args, **kwargs):
        print('*' * 5, 'DATA NOTIF:', data._getstatusname(status), *args)
        if status == data.LIVE:
            print('COULD DO SOMETHING')

    def notify_store(self, msg, *args, **kwargs):
        print('*' * 5, 'STORE NOTIF:', msg)

    def next(self):
        if False:
            print('{},{},{}'.format(
                len(self), self.datetime.datetime(), self.osignal[0])
            )
        pass
        txt = list()
        txt.append('Data0')
        txt.append('%04d' % len(self.data0))
        dtfmt = '%Y-%m-%dT%H:%M:%S.%f'
        txt.append('%s' % self.data.datetime.datetime(0).strftime(dtfmt))
        txt.append('{}'.format(self.data.open[0]))
        txt.append('{}'.format(self.data.high[0]))
        txt.append('{}'.format(self.data.low[0]))
        txt.append('{}'.format(self.data.close[0]))
        txt.append('{}'.format(self.data.volume[0]))
        # txt.append('{}'.format(self.osignal[0]))
        # txt.append('{}'.format(self.sma[0]))
        print(', '.join(txt))

        if len(self.datas) > 1:  # and len(self.data1):
            txt = list()
            txt.append('Data1')
            txt.append('%04d' % len(self.data1))
            dtfmt = '%Y-%m-%dT%H:%M:%S.%f'
            txt.append('%s' % self.data1.datetime.datetime(0).strftime(dtfmt))
            txt.append('{}'.format(self.data1.open[0]))
            txt.append('{}'.format(self.data1.high[0]))
            txt.append('{}'.format(self.data1.low[0]))
            txt.append('{}'.format(self.data1.close[0]))
            txt.append('{}'.format(self.data1.volume[0]))
            print(', '.join(txt))


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

    ibstore = bt.stores.IBStore(**eval('dict(' + args.store + ')'))
    cerebro.broker = ibstore.getbroker()  # Broker

    data0 = ibstore.getdata(dataname='TWTR',
                            timeframe=bt.TimeFrame.Minutes, compression=5)
    cerebro.resampledata(data0, timeframe=bt.TimeFrame.Minutes,
                         compression=5, name='minutes')

    data1 = bt.feeds.YahooFinanceCSVData(dataname='twtr-eomay.csv',
                                         timeframe=bt.TimeFrame.Days,)
    cerebro.resampledata(data1, timeframe=bt.TimeFrame.Days, name='days')

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

    # Defaults for dates
    parser.add_argument('--fromdate', required=False, default='',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--todate', required=False, default='',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--replay', required=False, action='store_true',
                        help='replay the larger timeframe')

    parser.add_argument('--cerebro', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--store', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--strat', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--plot', required=False, default='',
                        nargs='?', const='{}',
                        metavar='kwargs', help='kwargs in key=value format')

    return parser.parse_args(pargs)


if __name__ == '__main__':
    runstrat()
