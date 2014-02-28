#!/usr/bin/env python
##~
##~ Copyright 2004 Troy Melhase <troy@gci.net>
##~ 
##~ This file is part of the ProfitPy package.
##~ 
##~ ProfitPy is free software; you can redistribute it and/or modify
##~ it under the terms of the GNU General Public License as published by
##~ the Free Software Foundation; either version 2 of the License, or
##~ (at your option) any later version.
##~ 
##~ ProfitPy is distributed in the hope that it will be useful,
##~ but WITHOUT ANY WARRANTY; without even the implied warranty of
##~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##~ GNU General Public License for more details.
##~ 
##~ You should have received a copy of the GNU General Public License
##~ along with ProfitPy; if not, write to the Free Software
##~ Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##~
""" Coverage testing bits.


"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'coverage.py,v 0.8 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.8',
}

import os
import sys
import time
import traceback

import profit.lib.base as base
import profit.lib.session as session
import profit.lib.tickers as tickers
import profit.lib.tools as tools


sep = '-' * 79
altsep = sep.replace('-', '=')


def files_sorter(a, b):
    splt = os.path.split
    try:
        return cmp(int(splt(a)[-1].split('.')[-1]),
                   int(splt(b)[-1].split('.')[-1]))
    except (AttributeError, ValueError, IndexError, ):
        return cmp(a, b)


def ticker_report(ticker, fh=None):
    strat_format = 'at %4s price %2.2f position %6.2f shares %s'
    index_format = 'index key=%s len=%s'

    print >> fh, '\n'
    print >> fh, sep
    print >> fh, ticker
    print >> fh, sep

    for rpt_key in ticker.strategy_keys:
        series = ticker.series[rpt_key]
        key_name = base.PriceSizeLookup[rpt_key]
        print >> fh, '%s Series:' % (key_name, )
        print >> fh, '\tseries len=%s' % (len(series), )
        for index in series.indexes:
            print >> fh, '\t', index_format % (index.key, len(index), )

        try:
            strategy = series.strategy
        except (KeyError, AttributeError, ):
            pass
        else:
            print >> fh, '%s Strategy:' % (key_name, )
            for item in strategy.gauge():
                x, y = item[0]
                pos, siz = item[1]
                print >> fh, '\t', strat_format % (x, y, pos, siz, )
    print >> fh, sep


def profit_on_close(strat, records):
    last_record = records[-1]
    value, position = last_record[1]
    last_update = strat.series[-1]
    last_order = base.Order(quantity=abs(position), limit_price=last_update, 
                       transmit=0, open_close='C')
    close = last_order.cost_long() * (abs(position) / position)
    return value + close


def simulate_final(aseries, astrategy):
    tick_results = list(astrategy.gauge())
    tick_trades = len(tick_results)
    tick_profit = 0
    if tick_trades:
        ## last_trade looks something like this:
        ## ((138, 8.06), (795., -100), <base.Order object at 0x431a3fec>)
        last_trade = tick_results[-1]
        last_size = last_trade[1][1]
        if last_size:
            ## the last trade left an open position; calculate it's closing 
            ## price
            tick_profit = profit_on_close(astrategy, tick_results)

            ## now adjust the last history record in the strategy
            last_index = len(aseries)
            sig = (abs(last_size) / last_size) * -1
            rev = base.Directions.Reverse
            quan = astrategy.order_size
            ## the history records look something like this:
            ## (1200, 67.549999999999997, 0, 0, 0)]
            astrategy.history[-1] = (last_index-1, aseries[-1], sig, rev, quan)
            astrategy[-1] = sig


def strategy_report(strategy, supervisors, fh=None, print_headfoot=True, 
                    print_subtotal=True, print_grandtotal=True):
    start = time.time()
    total_profit = 0
    total_trades = 0
    report = {}
    
    if print_headfoot:
        print >> fh, 'Strategy coverage run started at %s' % (time.ctime(), )
        print >> fh, altsep
        print >> fh, 'Using strategy name %s' % (strategy, )
        print >> fh

    for file_name, source_tickers in supervisors:
        source_tickers.sort(lambda a, b: cmp(a.symbol, b.symbol))
        file_profit = 0
        file_trades = 0
        file_report = report[file_name] = {}
        
        print >> fh, 'File %s' % (file_name, )
        print >> fh, 'Symbol\tTrades\t  Profit\tEffective'
        print >> fh, sep

        for source_ticker in source_tickers:
            symbol = source_ticker.symbol
            secs, count, rebuilt_ticker = \
                tools.timed_ticker_rebuild(source_ticker, strategy)
            
            strat_objs = [rebuilt_ticker.series[key].strategy 
                            for key in rebuilt_ticker.strategy_keys]
            try:
                strat_obj = strat_objs[0]
            except (IndexError, ):
                pass
            tick_results = list(strat_obj.gauge())
            tick_trades = len(tick_results)
            tick_profit = 0.0
            tick_effective = 0.0

            if tick_trades:
                last_trade = tick_results[-1]
                if last_trade[1][1]:
                    tick_profit = profit_on_close(strat_obj, tick_results)
                else:
                    tick_profit = last_trade[1][0]
                if tick_profit:
                    tick_effective = tick_profit / tick_trades

            file_trades += tick_trades
            file_profit += tick_profit
            tick_record = (symbol, tick_trades, tick_profit, tick_effective)
            print >> fh, '%4s\t%6s\t%8.2f\t%8.2f' % tick_record
            file_report[symbol] = (tick_trades, tick_profit)

        if file_trades:
            rpt = (file_trades, file_profit, file_profit/file_trades)
        else:
            rpt = (file_trades, file_profit, 0)
        total_trades += file_trades
        total_profit += file_profit
        if print_subtotal:
            print >> fh, 'Sub Total'
            print >> fh, '\t%6s\t%8.2f\t%8.2f' % rpt
            print

    if total_trades:
        rpt = (total_trades, total_profit, total_profit/total_trades)
    else:
        rpt = (total_trades, total_profit, 0)

    if print_grandtotal:
        print >> fh, 'Grand Total'
        print >> fh, sep
        print >> fh, '\t%6s\t%8.2f\t%8.2f' % rpt
        print >> fh
    if print_headfoot:
        print >> fh, altsep
        rpt = 'Strategy coverage run completed in %2.2f seconds' 
        print >> fh, rpt % (time.time() - start, )

    return (strategy, report)


def print_usage(name):
    print 'Usage:'
    print '\t%s strategy file [file [file [...]]]' % (name, )
    print


def print_coverage_ex(err):
    print sep
    traceback.print_exc()
    print sep
    print err
    print


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    try:
        strat = args[0]
        files = args[1:]
        files.sort(files_sorter)
        if not files:
            raise IndexError()
    except (IndexError, ):
        print_usage(name=sys.argv[0])
        return

    try:
        strat_session = session.Session(strategy_builder=strat)
    except (Exception, ), ex:
        msg = 'Exception loading strategy builder named "%s"' % (strat, )
        print_coverage_ex(msg)
        return

    try:
        supervisors = [(fn, tools.load_object(fn).values()) for fn in files]
        results = strategy_report(strat, supervisors)
    except (KeyboardInterrupt, ):
        print 'Keyboard interrupt'
    except (Exception, ), ex:
        msg = 'Exception executing strategy "%s"' % (ex, )
        print_coverage_ex(msg)
        return
    return results


if __name__ == '__main__':
    data = main()
