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
""" Core ticker types

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'tickers.py,v 1.4 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '1.4',
}

import sys

import profit.lib.base as base
import profit.lib.series as series


class TickerSupervisor(dict):
    """ TickerSupervisor() -> 

    """
    def __init__(self):
        self.id_map = {}
        self.sym_map = {}

    def __getitem__(self, key):
        """ convenience function to retrieve ticker by id or symbol

        """
        try:
            return self.id_map[key]
        except (KeyError, ):
            pass
        try:
            return self.sym_map[key]
        except (KeyError, ):
            pass
        return dict.__getitem__(self, key)

    def __setitem__(self, (tid, tsym), ticker):
        """ enforce keys to be in the form of (id, sym)

        """
        try:
            sym_map = self.sym_map
        except (AttributeError, ):
            self.sym_map = sym_map = {}
        try:
            id_map = self.id_map
        except (AttributeError, ):
            self.id_map = id_map = {}
        sym_map[tsym] = id_map[tid] = ticker
        dict.__setitem__(self, (tid, tsym), ticker)

    def tick_message(self, ticker_id, field, value):
        """ tick_message(ticker_id, field, value) -> lots of updates goin on

        """
        ## tws sucks so much i break my own rule about newlines after the 'if'
        ## statement.  further, i add useless comments to force the maintainer
        ## to notice this suckage:  bad values come in from tws!
        if not value: return

        ## second cut at bad data:  filter out
        ## base.PriceTypes.Bid == 1 and value < 2
        if field == 1 and value < 2.0: return

        ## the appropriate ticker object and default signal
        ticker = self[ticker_id]
        direction, reverse = 0, 0

        ## save the previous data and update the current data
        ticker.previous_data[field] = ticker.current_data.get(field, 0)
        ticker.current_data[field] = value

        ## optionally add the value to the corresponding series
        try:
            ser = ticker.series[field]
        except (KeyError, ):
            pass
        else:
            ser.append(value)
            ## if there's a series, check it's strategy
            try:
                direction, reverse = ser.strategy.indication
            except (AttributeError, ):
                pass

        ## construct and return a signal from the direction, if any
        if direction:
            return base.TickerSignal(ticker, direction, reverse)
        else:
            return 0

    def update_portfolio(self, contract, position, market_price, market_value):
        try:
            ticker = self[contract.symbol]
        except (KeyError, ):
            return 0

        items = (('position', position),
                 ('market_price', market_price),
                 ('market_value', market_value), )
        for field, value in items:
            ticker.previous_data[field] = ticker.current_data.get(field, 0)
            ticker.current_data[field] = value

    def depth_message(self, ticker_id, position, operation, side, price, size):
        """ 

        """
        if operation in (0, 1):
            self[ticker_id].depth_table[position] = (side, price, size)
        elif operation == 2:
            try:
                del(self[ticker_id].depth_table[position])
            except (KeyError, ), ke:
                pass

    if 0:
        def report(self, price_size=base.PriceTypes.Bid):
            tids = [(tsym, len(tobj.series[price_size])) 
                        for (tsym, tid), tobj in self.items()]
            tids.sort(lambda x, y: cmp(x[1], y[1]))
    
            rowfs = '%s\t\t%s'
            print rowfs % ('Symbol', 'Len ' + base.PriceSizeLookup[price_size], )
            for tsym, rptlen in tids:
                print rowfs % (tsym, rptlen)


class TechnicalTicker(object):
    """ TechnicalTicker(id, symbol) -> ticker type with multiple data mappings

    """
    strategy_keys = [base.PriceTypes.Bid, ]

    def __init__(self, id, symbol):
        self.id = id
        self.symbol = symbol
        
        self.current_data = TickerPriceSizeMap()
        self.previous_data = TickerPriceSizeMap()
        self.series = TickerPriceSizeMap()

        self.depth_table = {}

    def __str__(self):
        items = self.current_data.items()
        items.sort()
        keys = dict([(k, v.replace(' ', '')) 
                        for k, v in base.PriceSizeLookup.items()])
        s = str.join(' ', ['%s=%s' % (keys[k], v) for k, v in items])
        return '<%s(%s, %s) %s>' % (self.__class__.__name__, 
                                  self.id, self.symbol, s)


class TickerPriceSizeMap(dict):
    """ TickerPriceSizeMap() -> identifies a mapping with price and/or size keys

    """


default_syms = [
    'AAPL', 'ADBE', 'ALTR', 'AMAT', 'AMZN',
    'BBBY', 'BEAS', 'BRCD', 'BRCM', 'CEPH',
    'CHKP', 'CNXT', 'COST', 'CSCO', 'CTXS',
    'DELL', 'DISH', 'EBAY', 'FLEX', 'GILD',
    'JDSU', 'JNPR', 'KLAC', 'MEDI', 'MERQ',
    'MSFT', 'MXIM', 'NTAP', 'NVDA', 'NVLS',
    'NXTL', 'ORCL', 'PDLI', 'PMCS', 'PSFT',
    'QCOM', 'SBUX', 'SPOT', 'SUNW', 'YHOO']


def default_mapping(symbol_table=default_syms, **kwds):
    return zip(range(100, 100 + len(symbol_table)), symbol_table)



def build(symbol_table, **kwds):
    """ build(symbol_table) -> build a ticker supervisor with ticker objects
        
        The id+symbol two tuple is used as the key for each ticker object 
        created.  The ticker objects have a data series, but no index or
        strategy objects.
    """
    new_supervisor = TickerSupervisor()
    for id_sym in symbol_table:
        tobj = new_supervisor[id_sym] = TechnicalTicker(*id_sym)
        for series_key in base.PriceSizeTypes:
            tobj.series[series_key] = ser = series.build()
            base.set_plot_style(ser, '#0000bb')
    return new_supervisor
