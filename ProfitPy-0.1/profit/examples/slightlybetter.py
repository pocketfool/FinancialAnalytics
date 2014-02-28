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
    'file' : 'slightlybetter.py,v 1.5 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '1.5',
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


def slightly_better_factory(tickers, strategy_keys=[base.PriceTypes.Bid, ], 
                            **session):
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
    series_slope = set_index('Series Slope', series.LinearRegressionSlope, ser, periods=100, scale=100)
    set_plot(series_slope, '#770000', axis='osc left')

    kama = set_index('KAMA', series.KAMA, ser, 10)
    set_plot(kama, color='#007700', axis='main left')

    #kama_slope = set_index('KAMA Slope', series.LinearRegressionSlope, kama, periods=100, scale=100)
    #set_plot(kama_slope, color='#007700', axis='osc left')

    kama_sig = set_index('KAMA Signal', series.KAMA, kama, 10) ## kama line of the kama line
    set_plot(kama_sig, color='#000077', axis='main left')

    #kama_sig_slope = set_index('KAMA Signal Slope', series.LinearRegressionSlope, kama_sig, periods=100, scale=100)
    #set_plot(kama_sig_slope, color='#000077', axis='osc left')

    kama_macd = set_index('KAMA-Signal MACD', series.PercentConvergence, ser, kama) #, kama_sig)
    set_plot(kama_macd, color='#ffffff', axis='osc right', curve_style='stick')

    if 0: 
        bb_upper = set_index('Bollinger Band Upper', series.BollingerBand, series=ser, period=30, dev_factor=10)
        set_plot(bb_upper, color='#fa1800')
    
        bb_lower = set_index('Bollinger Band Lower', series.BollingerBand, series=ser, period=30, dev_factor=-10)
        set_plot(bb_lower, color='#0af800')

    if 0:
        cog = set_index('Center of Gravity', series.CenterOfGravity, series=ser, periods=30)
        set_plot(cog, '#6633CC', axis='osc right')

    
    #signs = set_index('Slope Side Match', SignMatchFilter, series_slope, kama_slope, kama_sig_slope)
    gap = set_index('KAMA-Sig MACD Gap', GapSizeFilter, kama_macd, bounds=(-0.215, 0.215))
    vof = set_index('Vertical Order Filter', VerticalOrderFilter, ser, kama, kama_sig)
    ser.trend = trend = set_index('Trend', ConcurrentTrends, gap, vof)
    set_plot(trend, color='#b3b3b3', axis='main right', curve_type='trend')

    ser.strategy = strategy = set_index('Strategy', SligntlyBetterThanRandomStrategy, ser, trend, 100)
    set_plot(strategy, color='#b3b3b3', axis='main right', curve_type='strategy')


class SligntlyBetterThanRandomStrategy(strategy.StrategyIndex):
    """ SligntlyBetterThanRandomStrategy -> really, it's only slightly better       (than nothing :)

    """
    def __init__(self, series, trend, size, snooze=50):
        strategy.StrategyIndex.__init__(self, series, size)
        self.trend = trend
        self.snooze = snooze
        self.last = NoDirection
        self.silence_marker = [0, ] * 50

    def query(self):
        signal = self.trend.query()
        ## TODO:  add a warder-thing here

        if len(self) < self.snooze:
            return NoDirection

        ## filter out repeated signals after the first one
        if signal:
            if self.last == signal:
                signal = NoDirection
            else:
                self.last = signal
        else:
            ## no signal, maybe too long w/o one?
            if (self.trend[-len(self.silence_marker):] == self.silence_marker) and self.last:
                signal = self.last * -1
                self.last = NoDirection
        return signal

class SignMatchFilter(strategy.TrendIndex):
    def __init__(self, *seqs):
        strategy.TrendIndex.__init__(self, None)
        self.seqs = seqs
        #self.all_long = [float(Long), ] * len(seqs)
        #self.all_short = [float(Short), ] * len(seqs)

    def query(self):
        seqs = self.seqs
        lens = len(seqs)
        lasts = [seq[-1] for seq in seqs if seq[-1]]
        if len(lasts) != lens:
            return NoDirection

        if len([item for item in lasts if item > 0]) == lens:
            return Long
        elif len([item for item in lasts if item < 0]) == lens:
            return Short
        else:
            return NoDirection


class GapSizeFilter(strategy.TrendIndex):
    def __init__(self, ser, bounds):
        strategy.TrendIndex.__init__(self, None)
        self.series = ser
        self.bounds = bounds

    def query(self):
        current = self.series[-1]
        lowerbound, upperbound = self.bounds

        if current > upperbound:
            return Long
        elif current < lowerbound:
            return Short
        else:
            return NoDirection


class VerticalOrderFilter(strategy.TrendIndex):
    def __init__(self, a, b, c):
        strategy.TrendIndex.__init__(self, None)
        self.a, self.b, self.c = a, b, c

        
    def query(self):
        level = NoDirection
        a, b, c = self.a[-1], self.b[-1], self.c[-1]
        if a < b < c:
             level = Short
        elif a > b > c:
             level = Long
        return level


class ConcurrentTrends(strategy.TrendIndex):
    def __init__(self, *trends):
        strategy.TrendIndex.__init__(self, None)
        self.trends = trends
        self.all_long = [Long, ] * len(trends)
        self.all_short = [Short, ] * len(trends)

    def query(self):
        results = [trend.query() for trend in self.trends]
        if self.all_long == results:
            return Long
        elif self.all_short == results:
            return Short
        else:
            return NoDirection
