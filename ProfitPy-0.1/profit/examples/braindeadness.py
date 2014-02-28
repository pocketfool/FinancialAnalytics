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
"""

profit.examples.braindeadness -> defines a strategy that won't make moeny


"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'braindeadness.py,v 1.6 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '1.6',
}

import random   ## this is not a good sign!

import profit.lib.base as base
import profit.lib.series as series
import profit.lib.strategy as strategy


Reverse = base.Directions.Reverse
NoReverse = base.Directions.NoReverse

Short = base.Directions.Short
Long = base.Directions.Long
NoDirection = base.Directions.NoDirection

OpenCloseLookup = {
    NoReverse : 'O', 
    Reverse : 'C',
}


def braindead_strategy_factory(tickers, strategy_keys=[base.PriceTypes.Bid, ], **session):
    """ the purpose of the strategy builder is to add a strategy object to 
        each ticker.  each ticker is modified to include technical indicators
        as well.
    """
    style_func = base.set_plot_style
    targets = [(ticker, ser)
                    for ticker in tickers.values()
                        for (key, ser) in ticker.series.items()
                            if key in strategy_keys]

    for (ticker, ticker_series) in targets:
        index_func = ticker_series.index_map.set
        style_func(ticker_series, color='#aa0000')
        make_series_indexes(ticker_series, index_func, style_func)


def make_series_indexes(ser, set_index, set_plot):
    """ one of the duties of a strategy builder is to add index objects to the
        series of a ticker.

    """
    kama = set_index('KAMA', series.KAMA, ser, 10)
    set_plot(kama, color='#00aa00', axis='main left')

    kama_sig = set_index('KAMA Signal', series.KAMA, kama, 10)
    set_plot(kama_sig, color='#0000aa', axis='main left')

    kama_slope = set_index('KAMA Slope', series.LinearRegressionSlope, kama, 4)
    set_plot(kama_slope, color='yellow', axis='osc left', init_display=True)

    kama_macd = set_index('KAMA-Signal MACD', series.Convergence, kama_sig, kama)
    set_plot(kama_macd, color='#ffffff', axis='osc left', curve_style='stick')

    ser.strategy = strategy = \
       set_index('Strategy', BrainDeadRandomStrategy, series=ser, size=100)
    set_plot(strategy, color='#b3b3b3', axis='main right', curve_type='strategy')


class BrainDeadRandomStrategy(strategy.StrategyIndex):
    """ BrainDeadRandomStrategy -> works as well as you might expect, or worse


    """
    def __init__(self, series, size):
        strategy.StrategyIndex.__init__(self, series, size)
        self.signals = [Short, Long, ] + [NoDirection ,] * 50
        random.shuffle(self.signals)

    def query(self):
        signal = random.choice(self.signals)
        return signal
