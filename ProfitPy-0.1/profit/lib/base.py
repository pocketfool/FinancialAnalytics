#! /usr/bin/env python
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
""" Common constants, enumerations, functions, and types

When imported, this module redefines sys.stdout and sys.stderr if it hasn't
already done that.  The replacements are MultiCast instances, which supports
writing to multiple file handles.

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'base.py,v 0.9 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.9',
}

import Ib.Message
import Ib.Socket
import Ib.Type


class ComboLeg(Ib.Type.ComboLeg):
    """ ComboLeg(...) -> local comboleg wrapper

    """
    def __eq__(self, other):
        if other is self:
            return True
        elif not other:
            return False

        return self.action.lower() == other.action.lower() and \
               self.exchange.lower() == other.exchange.lower() and \
               self.con_id == other.con_id and \
               self.ratio == other.ratio and \
               self.open_close == other.open_close


class Contract(Ib.Type.Contract):
    """ Contract(...) -> local contract wrapper

    """
    never_expire = "200912"

    def __eq__(self, other):
        """ __eq__(other) -> does this contract match another 

        """
        return self.sec_type == other.sec_type and self.symbol == other.symbol

    def stock_factory(cls, symbol):
        """ stock_factory(cls, symbol) -> make a new stock contract 

        """
        c = cls(symbol)
        c.sec_type = SecurityTypes.Stock
        c.expiry = cls.never_expire
        c.strike, c.right, c.exchange, c.currency =  0.0, "C", "SMART", "USD"
        return c
    stock_factory = classmethod(stock_factory)


class Order(Ib.Type.Order):
    """ Order(...) -> local order wrapper

    """
    commission_per_share = 0.01

    def cost_long(self, commission_per_share=commission_per_share):
        """ cost_long() -> compute the cost of an order 

        """
        price = self.limit_price * self.quantity
        if self.quantity < 100:
            ## minimum order price is a dollar for lots less than 100
            return price + (100.0 * commission_per_share)

        if self.quantity <= 500:
            ## up to 500 shares is a penny per
            return price + (self.quantity * commission_per_share)

        if self.quantity > 500:
            ## over 500 shares is a bit different and maybe not accurate
            price += 500 * commission_per_share
            price += (self.quantity - 500) * (commission_per_share * 0.5)
            return price

    def cost_ignore_sells(self):
        """ cost_ignore_sells() -> order cost ignoring Sell or ShortSell

        """
        if self.action in (OrderActions.Sell, OrderActions.ShortSell):
            cost = 0.0
        else:
            cost = self.cost_long()
        return cost

    def buy_open_factory(cls, size, price, aux_price):
        """ buy_open_factory(...) -> make an open-buy order 

        """
        o = cls()
        o.action = OrderActions.Buy
        o.open_close = OrderPositions.Open
        o.quantity = size
        o.limit_price = price
        o.aux_price = aux_price
        o.order_type = OrderTypes.Limit
        return o
    buy_open_factory = classmethod(buy_open_factory)

    def sell_close_factory(cls, size, price, aux_price):
        """ sell_close_factory(...) -> make a new sell-close order 

        """
        o = cls()
        o.action = OrderActions.Sell
        o.open_close = OrderPositions.Close
        o.quantity = size
        o.limit_price = price
        o.aux_price = aux_price
        o.order_type = OrderTypes.Limit
        return o
    sell_close_factory = classmethod(sell_close_factory)


class TickerSignal(object):
    """ TickerSignal(...) -> encapsulates a buy or sell signal

    """
    def __init__(self, ticker, direction, reverse):
        self.ticker = ticker
        self.direction = direction
        self.reverse = reverse

    def __int__(self):
        return self.direction

    def __nonzero__(self):
        return not not self.direction


class AttributeMaskMixin(object):
    """ AttributeMaskMixin() -> helper to mask attributes that cannot be pickled

    """
    def __getstate__(self):
        """ __getstate__() -> returns state dictionary excluding masked objects

        """
        masked = self.masked + ('masked', )
        data = [(key, val) for key, val in self.__dict__.items() 
                               if key not in masked]
        return dict(data)

    def maskattrs(self, *names):
        """ maskattrs(*names) -> masks attributes against pickling

        """
        self.masked = names


class PartialCall(object):
    """ PartialCall(f, *a, **k) -> a callable object from a function

        Arguments are stored initially, and then used when the object is later
        called as a function.  Arguments may also be passed in during the 
        function call.
    """
    def __init__(self, fun, *args, **kwargs):
        self.fun = fun
        self.pending = args[:]
        self.kwargs = kwargs.copy()

    def __call__(self, *args, **kwargs):
        if kwargs and self.kwargs:
            kw = self.kwargs.copy()
            kw.update(kwargs)
        else:
            kw = kwargs or self.kwargs
        return self.fun(*(self.pending + args), **kw)


class AttributeMapping(dict):
    """ AttributeMapping(**kwds) -> matches attributes to keyword arguments

    """
    def __init__(self, **kwds):
        self.update(kwds)

    def update(self, mapping):
        """ update(mapping) -> adds attributes from mapping

        """
        dict.update(self, mapping)
        for key, value in mapping.items():
            setattr(self, key, value)
        

AccountKeys = AttributeMapping(
    FutureOptionValue='FutureOptionValue',
    EquityWithLoanValue='EquityWithLoanValue-S',
    Leverage='Leverage-S',
    NetLiquidation='NetLiquidation',
    OptionMarketValue='OptionMarketValue',
    TotalCashBalance='TotalCashBalance',
    TimeStamp='TimeStamp',
    DayTradesRemaining='DayTradesRemaining',
    GrossPositionValue='GrossPositionValue',
    FuturesPNL='FuturesPNL',
    MaintMarginReq='MaintMarginReq',
    InitMarginReq='InitMarginReq-S',
    StockMarketValue='StockMarketValue',
    SettledCash='SettledCash',
)


AccountLabels = AttributeMapping(
    FutureOptionValue='Futures Value',
    EquityWithLoanValue='Equity with Loan',
    Leverage='Leverage',
    NetLiquidation='Net Liquidation',
    OptionMarketValue='Options Value',
    TotalCashBalance='Total Cash Balance',
    TimeStamp='Time Stamp',
    DayTradesRemaining='Remaining Day Trades',
    GrossPositionValue='Gross Position',
    FuturesPNL='Futures PnL',
    MaintMarginReq='Maint Margin Requirement',
    InitMarginReq='Initial Margin Requirement',
    StockMarketValue='Stocks Value',
    AccountDescription='Account Description',
    LongOptionValue='Long Option Value',
    SettledCash='Settled Cash',
)


Directions = AttributeMapping(
    Long=+1, 
    Short=-1, 
    NoDirection=0,

    Reverse=1,
    NoReverse=0,
)


OrderActions = AttributeMapping(
    Buy='BUY', 
    Sell='SELL', 
    ShortSell='SSHORT',
)


OrderPositions = AttributeMapping(
    Close='C', 
    Open='O',
)


OrderStatus = AttributeMapping(
    Cancelled='Cancelled',
    Filled='Filled',
    Submitted='Submitted',
    PendingCancel='PendingCancel',
    PendingSubmit='PendingSubmit',
    PreSubmitted='PreSubmitted',
    Inactive='Inactive',
)


OrderTypes = AttributeMapping(
    Market='MKT',
    Limit='LMT',
    Stop='STP',
    StopLimit='STP_LMT',
    Relative='REL',
    VolumeWeighted='VWAP',
    MarketOnClose='MOC',
    LimitOnClose='LOC',
    MarketOnOpen='MOO',
    LimitOnOpen='LOO',
)


PriceTypes = AttributeMapping(
    Ask=Ib.Socket.ASK_PRICE,
    Bid=Ib.Socket.BID_PRICE,
    Last=Ib.Socket.LAST_PRICE,
    High=Ib.Socket.HIGH_PRICE,
    Low=Ib.Socket.LOW_PRICE,
    Close=Ib.Socket.CLOSE_PRICE,
)


SecurityTypes = AttributeMapping(
    Stock='STK',
    Option='OPT',
    Future='FUT',
    Index='IND',
    FutureOption='FOP',
    Cash='CASH',
)


SizeTypes = AttributeMapping(
    Ask=Ib.Socket.ASK_SIZE,
    Bid=Ib.Socket.BID_SIZE,
    Last=Ib.Socket.LAST_SIZE,
    Volume=Ib.Socket.VOLUME_SIZE,
)


def PriceSizeLookup():
    pslkup = {}
    pslkup.update(dict([(y, '%s Price' % x) for x, y in PriceTypes.items()]))
    pslkup.update(dict([(y, '%s Size' % x) for x, y in SizeTypes.items()]))
    pslkup['market_value'] = 'Market Value'
    pslkup['market_price'] = 'Market Price'
    pslkup['position'] = 'Position'
    return pslkup
PriceSizeLookup = PriceSizeLookup()


## all the price and size keys for building series objects
PriceSizeTypes  = PriceTypes.values() + SizeTypes.values()


##-----------------------------------------------------------------------------
##
## Plot Style
##
##-----------------------------------------------------------------------------
class PlotStyleMarker(object):
    """ PlotStyleMarker() -> place holder for plot style attributes

    """
    def __init__(self, color, 
                       width=0,
                       axis='main left',
                       init_display=True,
                       curve_type=None,
                       curve_style=None,
                       line_style=None):
        self.color = color
        self.width = width
        self.init_display = init_display
        self.pkey, self.yaxis = axis.split()
        self.curve_type = curve_type
        self.curve_style = curve_style
        self.line_style = line_style


def set_plot_style(series, color, 
                           width=0, 
                           axis='main left', 
                           init_display=True,
                           curve_type=None,
                           curve_style=None,
                           line_style=None):
    """ set_plot_style(color, ...) -> one way to set the plot style of a series

    """
    series.plot_style = plot_style = PlotStyleMarker(color)
    plot_style.width = width
    plot_style.init_display = init_display
    plot_style.pkey, plot_style.yaxis = axis.split()
    plot_style.curve_type = curve_type
    plot_style.curve_style = curve_style
    plot_style.line_style = line_style


def orders_agree(oa, ob):
    """ orders_agree(a, b) -> returns True if orders action and open-close match

    """
    return oa.action == ob.action and oa.open_close == ob.open_close


def common_broker_register(obj, connection):
    common = {
        'Account' :  ('ib_account', ),
        'Error' : ('ib_error', ),
        'ExecutionDetails' : ('ib_execution_details', ),
        'MarketDepth' : ('ib_market_depth', ),
        'NextId' : ('ib_next_id', ),
        'OpenOrder' : ('ib_open_order', ),
        'OrderStatus' : ('ib_order_status', ),
        'Portfolio' : ('ib_portfolio', ),
        'Ticker' : ('ib_ticker', ),
        'ReaderStart' : ('ib_reader_start', ),
        'ReaderStop' : ('ib_reader_stop', ),
        'NewsBulletin' : ('ib_news_bulletin', ),
    }

    for message_class_name, method_names in common.items():
        for m in method_names:
            if hasattr(obj, m):
                meth = getattr(obj, m)
                msg_type = getattr(Ib.Message, message_class_name)
                connection.register(msg_type, meth)


class MultiCast(list):
    """ MultiCast() -> multiplexes messages to registered objects 

        MultiCast is based on Multicast by Eduard Hiti (no license stated):
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52289
    """
    def __init__(self, *items):
        list.__init__(self)
        self.extend(items)

    def __call__(self, *args, **kwargs):
        """ () -> map object calls to result as a MultiCast

        """
        itemreturns = [obj(*args, **kwargs) for obj in self]
        return self.__class__(*itemreturns)

    def __getattr__(self, name):
        """ returns attribute wrapper for further processing """
        attrs = [getattr(obj, name) for obj in self]
        return self.__class__(*attrs)

    def __nonzero__(self):
        """ logically true if all delegate values are logically true """
        return not not reduce(lambda a, b: a and b, self, 1)


##
## support for sys.stdout and sys.stderr multicasting
##
import sys

def stdinit():
    """ stdinit() -> initialize sys.stdout and sys.stderr

    """
    import __main__
    isinteractive = hasattr(sys, 'ps1') 
    isipython = '__IP' in dir(__main__)
    if not isinteractive and not isipython:
        if not isinstance(sys.stdout, MultiCast):
            sys.stdout = MultiCast(sys.stdout)
        if not isinstance(sys.stderr, MultiCast):
            sys.stderr = MultiCast(sys.stderr)

stdinit()
del(stdinit)


def stdtee(obj, *names):
    """ stdtee(writable, [...]) -> add object to multicasting output

    """
    for name in names:
        which = getattr(sys, name)
        if obj not in which:
            which.append(obj)


def stdnotee(obj, *names):
    """ stdnotee(obj, [...]) -> remove object from multicasting output

    """
    for name in names:
        which = getattr(sys, name)
        if obj in which:
            which.remove(obj)
