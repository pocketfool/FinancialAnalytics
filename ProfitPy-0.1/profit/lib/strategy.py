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
""" Defines the StrategyIndex type.

StrategyIndex is the base class for types that indicate a trading signal.  
Subclasses must reimplement the query method.  The inherited methods provide
the functionality for tracking the signals and for interfacing with the ticker
and series objects.


"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'strategy.py,v 1.7 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '1.7',
}

import profit.lib.base as base
import profit.lib.series as series


Reverse = base.Directions.Reverse
NoReverse = base.Directions.NoReverse

Short = base.Directions.Short
Long = base.Directions.Long
NoDirection = base.Directions.NoDirection


class StrategyIndex(series.SeriesIndex):
    """ StrategyIndex(...) -> a base type for user strategies

        Clients should use this class as a base and reimplement the 'query' 
        method, and return Short, Long, or NoDirection from that.
    """
    def __init__(self, ser, order_size):
        series.SeriesIndex.__init__(self, ser)
        self.order_size = order_size
        self.indication = (NoDirection, NoReverse)
        self.history = []
        self.position = 0

    def query(self):
        """ query() -> this method must be implemented by clients

        """
        exmsg = "Class %s does not reimplement 'query' method'"
        exmsg = exmsg % (self.__class__.__name__, )
        raise NotImplementedError(exmsg)

    def reindex(self):
        """ reindex() -> calculate a signal for this strategy

            This implementation defers strategy calculation to the 'query' 
            method then uses that result to determine the Reverse-NoReverse
            value, then finally uses both values together to form an 
            indication.
        """
        signal = self.query()
        shares = self.order_size
        lastposition = self.position
        reverse = NoReverse

        ## if there is an existing position, a new signal, and if the position
        ## direction is different than the current signal, indicate a reverse
        if lastposition and signal:
            if (abs(lastposition) / lastposition) != signal:
                reverse = 1
        
        ## formulate the current indication
        if signal:
            self.indication = (signal, reverse)
        else:
            self.indication = (NoDirection, NoReverse)

        ## adjust the position according to the signal and reverse.  if there
        ## is a previous position and no reverse, the position is furthered.
        if not signal:
            quan = 0
        elif lastposition and reverse:
            quan = -lastposition
            self.position = 0
        else:
            quan = shares * signal
            self.position += quan

        series = self.series
        self.history.append((len(series)-1, series[-1], signal, reverse, quan))
        self.append(signal)

    def gauge(self):
        """ gauge() -> a generator for strategy performance measurement

        """
        running_pnl = 0
        running_pos = 0
        opencloselookup = {NoReverse : 'O', Reverse : 'C'}

        for record in self.history:
            index, price, direction, reverse, movesize = record[0:5]
            if not direction:
                continue
            order = base.Order(quantity=movesize, limit_price=price, 
                               transmit=0, open_close=opencloselookup[reverse])
            cost = base.Order.cost_long(order)
            running_pnl +=  -cost
            running_pos += movesize
            yield ((index, price), (running_pnl, running_pos), order, )

    def __str__(self):
        format = '<%s.%s object at 0x%x>'
        args = (__name__, self.__class__.__name__, id(self), )
        return format % args

    __repr__ = __str__


class TrendIndex(series.SeriesIndex):
    """ TrendIndex -> tracks calculated trend

    """
    def __init__(self, ser):
        series.SeriesIndex.__init__(self, ser)

    def reindex(self):
        trend = self.query()
        self.append(trend)

