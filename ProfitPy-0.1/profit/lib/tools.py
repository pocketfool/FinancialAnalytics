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
""" Various bits

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'tools.py,v 0.4 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.4',
}

import cPickle
import time

import profit.lib.session as session
import profit.lib.tickers as tickers


class DataOnlyTicker(object):
    """ DataOnlyTicker() -> simple and unadorned ticker objectTrees
    
        This type is kept separate and simple so that it can adjust easily to 
        changes in the classes of this package.
    """
    def __init__(self, id, symbol):
        self.id, self.symbol = id, symbol


def save_object(obj, filename, proto=-1):
    """ save_object(obj, filename, proto=-1) -> pickle obj to filename

    """
    fd = open(filename, "wb")
    cPickle.dump(obj, fd, proto)
    fd.close()


def load_object(filename):
    """ load_object(filename) -> load the pickled contents of filename

    """
    fd = open(filename)
    obj = cPickle.load(fd)
    fd.close()
    return obj


def strip_tickers(original_supervisor):
    """ strip_tickers() -> duplicate supervisor from original_supervisor

    """
    ret = tickers.build([])
    for (id, sym), oldtick in original_supervisor.items():
        ret[(id, sym)] = newtick = DataOnlyTicker(id, sym)
        newtick.series = {}
        for pricekey, priceupdates in oldtick.series.items():
            newtick.series[pricekey] = priceupdates[:]
    return ret


def ticker_rebuild(source_ticker, strategy_builder, ltrim=0):
    """ ticker_rebuild(...) -> rebuilds a ticker object

    """
    src_id = source_ticker.id
    src_sym = source_ticker.symbol

    def as_ticker_mapping(**kwds):
        return [(src_id, src_sym), ]

    def account_factory(*a, **b):
        class fakie_account(object):
            positions = {}
            orders = {}
        return fakie_account()

    def empty_factory(*a, **b):
        return {}

    sess = session.Session(tickers_mapping_builder=as_ticker_mapping, 
                           strategy_builder=strategy_builder, 
                           account_builder=account_factory, 
                           order_builder=empty_factory)
    temp_supervisor = sess.tickers
    rebuilt_ticker = temp_supervisor[src_sym]

    ## fill in the ticker from its series data
    fill_func = temp_supervisor.tick_message
    for ser_idx, series in source_ticker.series.items():
        for value in series[ltrim:]:
            fill_func(src_id, ser_idx, value)
    return rebuilt_ticker


def timed_ticker_rebuild(source_ticker, strategy_builder, ltrim=0):
    """ timed_ticker_rebuild(...) -> timed version of ticker_rebuild

    """
    t1 = time.time()
    ts = ticker_rebuild(source_ticker, strategy_builder, ltrim)
    t2 = time.time()
    msg_count = sum([len(s) for s in ts.series.values()])
    return (t2 - t1), msg_count, ts
