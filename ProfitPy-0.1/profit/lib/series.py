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
""" Series -> technical series sequences and indexes

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'series.py,v 0.7 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.7',
}

import time

from Numeric import arctan, array, log
from scipy.stats import linregress, mean, std, median, mode


##-----------------------------------------------------------------------------
##
## Series Type
##
##-----------------------------------------------------------------------------
class Series(list):
    """ Series() -> list that maintains indexes

    """
    def __init__(self, data=None):
        list.__init__(self, data or [])
        self.indexes = indexes = []
        self.index_map = IndexMapping(indexes)

    def append(self, item):
        """ append(item) -> append item to this series and update all indexes

        """
        list.append(self, item)
        for idx in self.indexes:
            idx.reindex()


class IndexMapping(object):
    """ IndexMapping(indexes) -> partial dictionary emulator for Series clients

    """
    def __init__(self, indexes):
        self.indexes = indexes

    def __getitem__(self, key):
        for idx in self.indexes:
            if idx.key == key:
                return idx
        raise IndexError("index out of range")

    def items(self):
        return [(index.key, index) for index in self.indexes]

    def set(self, key, func, *args, **kwds):
        indexes = self.indexes
        if key in [idx.key for idx in indexes]:
            index = [idx for idx in indexes if idx.key==key][0]
        else:
            index = func(*args, **kwds)
            index.key = key
            indexes.append(index)
        return index


def build():
    """ build() -> a new series object 

    """
    return Series()


##-----------------------------------------------------------------------------
##
## Series Index Types
##
##-----------------------------------------------------------------------------
class BaseIndex(list):
    """ """


class SeriesIndex(BaseIndex):
    """ SeriesIndex(series) -> base index type

    """
    def __init__(self, series):
        BaseIndex.__init__(self)
        self.series = series


##-----------------------------------------------------------------------------
##
## Moving Average Index Type
##
##-----------------------------------------------------------------------------
class MovingAverageIndex(SeriesIndex):
    """ MovingAverageIndex -> base class for moving average indexes 
    
    """
    def __init__(self, series, periods):
        SeriesIndex.__init__(self, series)
        self.periods = periods
        self.periods_range = range(periods)


##-----------------------------------------------------------------------------
##
## Rocket Science Index Types
##
##-----------------------------------------------------------------------------
class CenterOfGravity(MovingAverageIndex):
    """ CenterOfGravity -> center of gravity oscillator

    """
    def reindex(self):
        periods = self.periods
        period = self.series[-periods:]
        try:
            n, d = 0, 0
            for c in range(periods):
                n += (1+c) * period[-c]
                d += period[-c]
            cg = -n/d
            # bah - these adjustments are for plotting
            # need a way to identify plot axis
            #cg += 50.5
            cg += 15.5
        except (TypeError, IndexError, ZeroDivisionError, ):
            cg = None
        self.append(cg)


class FisherTransform(MovingAverageIndex):
    """ FisherTransform -> er?

    """
    def __init__(self, series, periods):
        MovingAverageIndex.__init__(self, series, periods)
        self.inter = []

    def reindex(self):
        periods = self.periods
        period = self.series[-periods:]
        current = period[-1]
        mx = max(period)
        mn = min(period)
        try:
            inter = 0.33 * 2 * ((current - mn) / (mx - mn) - 0.5) + (0.67 * self.inter[-1])
            if inter > 0.99: 
                inter = 0.99
            elif inter < -0.99:
                inter = -0.99
            fish = 0.5 * log((1 + inter) / (1 - inter)) + (0.5 * self[-1])
        except (TypeError, IndexError, ZeroDivisionError, ):
            inter = 0
            fish = 0

        self.inter.append(inter)
        self.append(fish)


class MAMA(MovingAverageIndex):
    """ MAMA - Mother of Adaptave Moving Averages - broken beyond belief, too

    """
    fast_limit = 0.5
    slow_limit = 0.05

    def __init__(self, series, periods):
        MovingAverageIndex.__init__(self, series, periods)
        self.hist = {'q1':[], 'i1':[], 'q2':[], 'i2':[], 're':[], 'im':[], 
                     'sms':[], 'dts':[], 'prs':[], 'sps':[], 'phs':[], }


    def reindex(self):
        hist = self.hist
        sms, dts, prs, sps, phs = \
            hist['sms'], hist['dts'], hist['prs'], hist['sps'], hist['phs']
        q1, i1, q2, i2, re, im = \
            hist['q1'], hist['i1'], hist['q2'], hist['i2'], hist['re'], hist['im']

        series = self.series
        periods = self.periods

        if len(series) > periods:
            sm = sum((4*series[-1], 3*series[-2], 2*series[-3], series[-4])) / 10
            sms.append(sm)

            dt = (0.0962*sms[-1] + 0.5769*sms[-3] - 0.5769*sms[-5] - 0.0962*sms[-7]) * (0.075*prs[-2] + 0.54)
            dts.append(dt)

            qa = (.0962*dts[-1] + 0.5769*dts[-3] - 0.5769*dts[-5] - 0.0962*dts[-7]) * (0.075*prs[-2] + 0.54)
            q1.append(qa)

            ia = dts[-4]
            i1.append(ia)

            jI = (0.0962*i1[-1] + 0.5769*i1[-3] - 0.5769*i1[-5] - 0.0962*i1[-7]) * (0.075*prs[-2] + 0.54)
            jQ = (0.0962*q1[-1] + 0.5769*q1[-3] - 0.5769*q1[-5] - 0.0962*q1[-7]) * (0.075*prs[-2] + 0.54)

            ib = i1[-1] - jQ
            qb = q1[-1] - jI
            ib = 0.2*ib + 0.8*i2[-1]
            qb = 0.2*qb + 0.8*q2[-1]
            i2.append(ib)
            q2.append(qb)

            ra = i2[-1]*i2[-2] + q2[-1]*q2[-2]
            ima = i2[-1]*q2[-2] - q2[-1]*i2[-2]
            ra = 0.2*ra + 0.8*re[-1]
            ima = 0.2*ra + 0.8*im[-1]
            re.append(ra)
            im.append(ima)

            if im[-1] != 0 and re[-1] != 0:
                pra = 360 / arctan(im[-1]/re[-1])
            else:
                pra = 0

            if pra > 1.5*prs[-1]: pra = 1.5*prs[-1]
            if pra < 0.67*prs[-1]: prs = 0.67*prs[-1]
            if pra < 6: pra = 6
            if pra > 50: pra = 50
            pra = 0.2*pra + 0.8*prs[-1]
            prs.append(pra)

            spa = 0.33*prs[-1] + 0.67*sps[-1]
            sps.append(spa)
        
            if i1[-1] != 0:
                ph = arctan(q1[-1] / i1[-1])
            else:
                ph = 0
            phs.append(ph)

            dp = phs[-2] - phs[-1]
            if dp < 1: dp = 1
            alpha = self.fast_limit / dp
            if alpha < self.slow_limit: alpha = self.slow_limit
            mama = alpha*series[-1] + (1 - alpha)*self[-1]
            #FAMA = .5*alpha*MAMA + (1 - .5*alpha)*FAMA[1];
            self.append(mama)
        else:
            last = series[-1]
            for vlst in hist.values():
                vlst.append(last)
            self.append(last)


class SmoothedRSI(MovingAverageIndex):
    """ SmoothedRSI -> smoothed relative strength

    """
    def __init__(self, series, periods):
        MovingAverageIndex.__init__(self, series, periods)
        self.smooth = []

    def reindex(self):
        periods = self.periods
        period = self.series[-periods:]
        smooth = self.smooth

        try:
            s = (period[-1] + 2*period[-2] + 2*period[-3] + period[-4]) / 6.0
            smooth.append(s)
        except (IndexError, ):
            self.append(0)
            return

        smooth.append(s)
        cu = cd = 0
        try:
            for count in range(1, periods):
                s = smooth[-count]
                ps = smooth[-count-1]
                if s > ps:
                    cu += s - ps
                if s < ps:
                    cd += ps - s
        except (IndexError, ):
            self.append(0)
            return
    
        try:
            srsi = cu/(cu+cd)
        except (ZeroDivisionError, ):
            srsi = 0
        self.append(srsi)


##-----------------------------------------------------------------------------
##
## Simple Index Types
##
##-----------------------------------------------------------------------------
class SMA(MovingAverageIndex):
    """ SMA -> Simple Moving Average Index 
    
    """
    def reindex(self):
        periods = self.periods
        period = self.series[-periods:]
        sma = None

        if len(period) == periods:
            try:
                sma = mean(period)
            except (TypeError, IndexError):
                pass
        self.append(sma)


class EMA(MovingAverageIndex):
    """ EMA -> Exponential Moving Average Index
    
    """

    def __init__(self, series, periods, k=2.0):
        MovingAverageIndex.__init__(self, series, periods)
        self.k = k

    def reindex(self):
        try:
            last = self[-1]
        except (IndexError, ):
            self.append(None)
            return

        periods = self.periods
        ema = None
        if last is None:
            try:
                period = self.series[-periods:]
                if len(period) == periods:
                    ema = mean(period)
            except (TypeError, ):
                pass
        else:
            pt = self.series[-1]
            k = self.k / (periods + 1)
            ema = last + (k * (pt - last))
        self.append(ema)


class KAMA(MovingAverageIndex):
    def __init__(self, series, periods, fast_look=2, slow_look=30):
        MovingAverageIndex.__init__(self, series, periods)
        self.fastest = 2.0 / (fast_look+1)
        self.slowest = 2.0 / (slow_look+1)
        self.efficiency_factor = (self.fastest - self.slowest) + self.slowest ## er?

    def reindex(self):
        " kama = S * price + (1 - S) * kama[-1] "

        series = self.series
        periods = self.periods
        last = series[-1]

        try:
            prev = series[-2]
        except (IndexError, ):
            self.append(last)
            return

        noise = 0
        eff = 1
        try:
            p1 = series[-periods:]
            p2 = series[-periods-1:-1]
            noise = sum([abs(a-b) for a, b in zip(p1, p2)])
        except (IndexError, ):
            pass

        if noise:
            eff = abs(last - prev) / noise

        s = eff * self.efficiency_factor
        s = s * s

        kama = s*last + (1-s)*self[-1]
        self.append(kama)


class DistanceCoefficient(MovingAverageIndex):
    """ DistanceCoefficient -> Distance Coefficient
    
    """
    def __init__(self, series, periods):
        MovingAverageIndex.__init__(self, series, periods)

    def reindex(self):
        series = self.series
        periods = self.periods
        period = self.series[-periods:]

        dists = [0, ] * periods
        coeff = [0, ] * periods


        try:
            for i in range(-1, -periods, -1):
                for k in range(-2, -periods, -1):
                    dists[i] = dists[i] + (series[i] - series[i+k]) * (series[i] - series[i+k])
                coeff[i] = dists[i]
    
            num = sumcoeff = 0
            for k in range(periods):
                num += coeff[i]*period[i]
                sumcoeff += coeff[i]
            if sumcoeff:
                filt = num / sumcoeff
            else:
                filt = 0
        except (IndexError, ):
            filt = None
        self.append(filt)

class WMA(MovingAverageIndex):
    """ WMA -> Weighted Moving Average Index
    
    """
    def __init__(self, series, periods):
        MovingAverageIndex.__init__(self, series, periods)
        offsets = range(1, periods+1)
        periods_sum = float(sum(offsets))
        self.weights = array([x/periods_sum for x in offsets])


    def reindex(self):
        periods = self.periods
        period = self.series[-periods:]
        wma = None

        if len(period) == periods:
            try:
                wma = sum(period * self.weights)
            except (TypeError, ):
                pass
        self.append(wma)


class Convergence(SeriesIndex):
    """ Convergence -> Convergence Line

    """
    def __init__(self, series, signal):
        SeriesIndex.__init__(self, series)
        self.signal = signal

    def reindex(self):
        try:
            self.append(self.signal[-1] - self.series[-1])
        except (TypeError, ):
            self.append(None)


class PercentConvergence(SeriesIndex):
    """ PercentConvergence -> Convergence as a percentage

    """
    def __init__(self, series, signal):
        SeriesIndex.__init__(self, series)
        self.signal = signal

    def reindex(self):
        try:
            self.append((1 - self.signal[-1] / self.series[-1]) * 100)
        except (TypeError, ZeroDivisionError, ):
            self.append(None)


class MACDHistogram(SeriesIndex):
    """ MACDHistogram -> Tracks difference between line and its signal

    """
    def __init__(self, series, signal):
        SeriesIndex.__init__(self, series)
        self.signal = signal

    def reindex(self):
        try:
            self.append(self.series[-1] - self.signal[-1])
        except (TypeError, ):
            self.append(None)


class DetrendedPriceOscillator(SeriesIndex):
    """ DPO = Close - Simple moving average [from (n / 2 + 1) days ago]

    """
    def __init__(self, series, moving_average):
        self.series, self.moving_average = series, moving_average

    def reindex(self):
        last = self.series[-1]
        lookback = (self.moving_average.periods/2) + 1
        try:
            dpo = last - self.moving_average[-lookback]
        except (TypeError, IndexError):
            dpo = None
        self.append(dpo)


class Trix(SeriesIndex):
    def reindex(self):
        try:
            current, previous = self.series[-1], self.series[-2]
            trix = (current - previous) / previous
            trix *= 100
        except (TypeError, IndexError):
            trix = None
        self.append(trix)


##-----------------------------------------------------------------------------
##
## Volatility Indexes
##
##-----------------------------------------------------------------------------
class Volatility(MovingAverageIndex):
    """ Volatility(series, periods) -> volatility index

        Volatility = standard deviation of closing price [for n periods] / average closing price [for n periods]
    """
    def reindex(self):
        periods = self.periods
        period = self.series[-periods:]
        vol = None
        if len(period) == periods:
            try:
                vol = std(period) / mean(period)
                vol *= 100
            except TypeError:
                pass
        self.append(vol)


##-----------------------------------------------------------------------------
##
## Momentum Indexes
##
##-----------------------------------------------------------------------------
class Momentum(SeriesIndex):
    def __init__(self, series, lookback):
        SeriesIndex.__init__(self, series)
        self.lookback = lookback

    def reindex(self):
        try:
            last, prev = self.series[-1], self.series[-self.lookback] 
            momentum = last - prev
        except (IndexError, TypeError):
            momentum = None
        self.append(momentum)


class RateOfChange(SeriesIndex):
    def __init__(self, series, lookback):
        SeriesIndex.__init__(self, series)
        self.lookback = lookback

    def reindex(self):
        try:
            last, prev = self.series[-1], self.series[-self.lookback]
            momentum = last - prev
            rate = momentum / (prev*100)
            rate *= 100
        except (IndexError, TypeError, ZeroDivisionError):
            rate = None
        self.append(rate)


class VerticalHorizontalFilter(MovingAverageIndex):
    """ VerticalHorizontalFilter ->

    """
    def reindex(self):
        periods = self.periods
        period = self.series[-periods:]
        vhf = None

        if len(period) == periods:
            try:
                diffs = array(period[1:]) - period[0:-1]
                vhf = (max(period) - min(period)) / sum(abs(diffs))
            except (IndexError, TypeError, ZeroDivisionError):
                pass

        self.append(vhf)


class Stochastic(MovingAverageIndex):
    """ Stochastic ->

    """
    def reindex(self):
        periods = self.periods
        period = self.series[-periods:]
        lowest = min(period)
        highest = max(period)

        cl = self.series[-1] - lowest
        hl = highest - lowest

        if cl == 0:
            k = 0.0
        else:
            k = cl / float(hl)
        self.append(k)


class WilliamsR(MovingAverageIndex):
    """ WilliamsR is almost the same as Stochastic except that it's 
        adjusted * -100

    """
    def reindex(self):
        periods = self.periods
        period = self.series[-periods:]
        lowest = min(period)
        highest = max(period)

        hc = highest - self.series[-1]
        hl = highest - lowest
        try:
            r = (hc / hl) * -100 
        except (ZeroDivisionError, ):
            r = 0
        self.append(r)


class BollingerBand(SeriesIndex):
    def __init__(self, series, period, dev_factor):
        SeriesIndex.__init__(self, series)
        self.period = period # allows for periods != periods of series
        self.dev_factor = dev_factor

    def reindex(self):
        period = self.series[-self.period:]
        last = self.series[-1]
        try:
            dev = std(period)
            dev *= self.dev_factor
            dev += last
        except (TypeError, ZeroDivisionError, ):
            dev = None
        self.append(dev)


class LinearRegressionSlope(SeriesIndex):
    """ LinearRegressionSlope(series, periods) -> slope of the linear regression

    """
    def __init__(self, series, periods, scale=1):
        SeriesIndex.__init__(self, series)
        self.periods = periods
        self.scale = scale
        self.xarray = array(range(0, periods))

    def reindex(self):
        xa = self.xarray
        ya = array(self.series[-self.periods:])
        try:
            slope, intercept, r, two_tail_prob, est_stderr = linregress(xa, ya)
        except (TypeError, ValueError, ZeroDivisionError):
            slope = 0.0
        self.append(slope * self.scale)


class TrueRange(MovingAverageIndex):
    """ TrueRange(series, periods) -> true range index

        True Range is the greater of:
    
        * High for the period less the Low for the period.
        * High for the period less the Close for the previous period.
        * Close for the previous period and the Low for the current period.
    """
    def reindex(self):
        periods = self.periods
        items = self.series[-periods:]
        if len(items) == periods and periods > 1:
            high = max(items)
            low = min(items)
            prev_last = self.series[-2]
            truerange = max((high-low, high-prev_last, prev_last-low))
        else:
            truerange = None
        self.append(truerange)


##-----------------------------------------------------------------------------
##
## Utility Index Types
##
##-----------------------------------------------------------------------------
class OrderStatisticFilter(MovingAverageIndex):
    """ OrderStatisticFilter -> os filter base class

        OS filters base their operation on the ranking of the samples within 
        the filter window.  The data are ranked by their summary statistics, 
        such as their mean or variance,  rather than by their temporal position.
    """


class MedianValue(OrderStatisticFilter):
    """ MedianValue -> indexes a series by the median

    """
    def reindex(self):
        values = self.series[-self.periods:]
        m = median(values).toscalar()
        self.append(m)


class ModeValue(OrderStatisticFilter):
    """ ModeValue -> indexes a series by the mode

    """
    def reindex(self):
        values = self.series[-self.periods:]
        m = mode(values)[0].toscalar()
        self.append(m)


class DelayFilter(SeriesIndex):
    """ DelayFilter -> duplicates a series by a previous value

    """
    def __init__(self, series, lookback):
        self.series = series
        self.lookback = lookback

    def reindex(self):
        try:
            v = self.series[-self.lookback]
        except (IndexError, ):
            v = None
        self.append(v)


class TimeIndex(SeriesIndex):
    """ TimeIndex(series) -> tracks the time stamps of updates

    """
    def reindex(self, time_func=time.time):
        self.append(time_func())


class ChangeIndex(SeriesIndex):
    """ ChangeIndex(series) -> tracks the difference between updates

    """
    def reindex(self):
        try:
            change = self.series[-1] - self.series[-2]
        except (TypeError, IndexError):
            change = None
        self.append(change)


class IndexIndex(SeriesIndex):
    """ IndexIndex -> index that maintains the current series length
    
    """
    idx = 0
    def reindex(self):
        self.append(self.idx)
        self.idx += 1


class LevelIndex(SeriesIndex):
    """ LevelIndex -> constant level indexing 
    
    """
    def __init__(self, series, level):
        SeriesIndex.__init__(self, series)
        self.level = level

    def reindex(self):
        self.append(self.level)


class OffsetIndex(SeriesIndex):
    def __init__(self, series, offset):
        SeriesIndex.__init__(self, series)
        self.offset = offset

    def reindex(self):
        last = self.series[-1] 
        try:
            offset = last + (self.offset * last)
        except TypeError:
            offset = None
        self.append(offset)

class Slope(SeriesIndex):
    """ Slope -> slope values as an index

    """
    def reindex(self):
        try:
            Y1, Y2 = self.series[-2], self.series[-1]
            slope = Y2-Y1 ## X1-X2 is always 1
        except (IndexError, TypeError):
            slope = None
        self.append(slope)


class DifferenceIndex(SeriesIndex):
    def __init__(self, series, other):
        SeriesIndex.__init__(self, series)
        self.other = other

    def reindex(self):
        try:
            diff = self.series[-1] - self.other[-1]
        except:
            diff = None
        self.append(diff)


##-----------------------------------------------------------------------------
##
## Unfinished Indexes
##
##-----------------------------------------------------------------------------
class RSI(MovingAverageIndex):
    """ Relative Strength Index -> NEEDS WORK

    """
    def __init__(self, series, periods, change_line):
        MovingAverageIndex.__init__(self, series, periods)
        self.change_line = change_line
        self._prevs = []

    def get_avgs(self):
        thisdata = self.series[-self.periods:]
        thischange = self.change_line[-self.periods:]
        gains = filter(lambda x: x>=0, thischange)
        losses = filter(lambda x: x<0, thischange)
        avggain = gains / float(self.periods)
        avgloss = losses / float(self.periods)
        return avggain, avgloss

    def reindex(self):
        if len(self.series) < self.periods:
            rsi = None
        elif len(self.series) == self.periods:
            avggain, avgloss = self.get_avgs()
            self._prevs.append((avggain, avgloss))
            rsi = avggain  / avgloss
        else:
            periods = self.periods
            pavggain, pavgloss = self._prevs.pop()
            rsi = None
        self.append(rsi)


##-----------------------------------------------------------------------------
##
## Unclassified Index Types
##
##-----------------------------------------------------------------------------
class LoPassFilter(SeriesIndex):
    def __init__(self, series, cutoff):
        self.series = series
        self.cutoff = cutoff

    def reindex(self):
        v = self.series[-1]
        if v is not None and v > self.cutoff:
            v = self.cutoff
        self.append(v)


class HiPassFilter(SeriesIndex):
    def __init__(self, series, cutoff):
        self.series = series
        self.cutoff = cutoff

    def reindex(self):
        v = self.series[-1]
        if v is not None and v < self.cutoff:
            v = self.cutoff
        self.append(v)


class BandPassFilter(SeriesIndex):
    def __init__(self, series, hi, low):
        self.series = series
        self.hi = hi
        self.low = low

    def reindex(self):
        v = self.series[-1]
        if v is None:
            pass
        if v > self.hi:
            v = self.hi
        if v < self.low:
            v = self.low
        self.append(v)


class UpMovement(SeriesIndex):
    def reindex(self):
        try:
            prev, current = self.series[-2:]
            throw_away = prev + current # purposeful type error
            up = current > prev
        except (IndexError, TypeError):
            up = 0
        self.append(int(up))


class DownMovement(SeriesIndex):
    def reindex(self):
        try:
            prev, current = self.series[-2:]
            throw_away = prev + current # purposeful type error
            dn = current < prev
        except (IndexError, TypeError):
            dn = 0
        self.append(int(dn))
