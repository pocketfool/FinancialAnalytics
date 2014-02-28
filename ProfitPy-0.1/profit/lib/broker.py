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
""" Interconnects library objects with the broker.

    The BrokerProxy class defined below connects an account supervisor, a ticker
    supervisor, and an Ib socket connection.

    Clients will want to connect the proxy to the broker and request data feeds:

    >>> broker.connect(('localhost', 7496))
    >>> broker.request_external()

    After connecting to the broker, the Ib socket connection will execute
    the callback methods defined below.  The BrokerProxy instances shuffle 
    these method calls between the account and ticker objects, and add some 
    other simple behavior.

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'broker.py,v 0.3 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.3',
}

import sys
import time

import profit.lib.base as base


class BrokerProxy(base.AttributeMaskMixin, object):
    """ BrokerProxy(...) -> proxies calls from the broker to library objects

    """
    def __init__(self, account, connection, tickers):
        self.account = account
        self.connection = connection
        self.tickers = tickers
        self.errors = {}
        self.news = []
        self.maskattrs('connection')


    def connect(self, address):
        """ connect((host, port)) -> connect to the broker at host:port

            When called to connect, instances append themselves to the socket's
            handlers list and call the socket's connect function.
        """
        base.common_broker_register(self, self.connection)
        self.connection.connect(address)

    def test_order(self, ticker, direction=1, reverse=0):
        """ test_order(ticker, ...) -> submit an order

        """
        sig = base.TickerSignal(ticker, direction, reverse)
        self.account.put_ticker_signal(sig)

    def request_external(self, log_level=1):
        """ request_external() -> requests all broker data feeds

            This method requests execution, order, and account data.  It also
            requests ticker data and market depth for the ticker objects managed
            by the ticker supervisor.
        """
        connection = self.connection
        connection.set_server_log_level(log_level)
        connection.request_executions()
        connection.request_open_orders()
        connection.request_account_updates()
        connection.request_news_bulletins()

        id_syms = self.tickers.keys()
        id_syms.sort()

        for ticker_id, ticker_sym in id_syms:
            contract = base.Contract.stock_factory(ticker_sym)
            connection.request_market_data(ticker_id, contract)

        ## market depth isn't yet used, but this block requests it for the first
        ## three tickers to exercise the code related to it
        #for ticker_id, ticker_sym in id_syms[0:3]:
        #    contract = base.Contract.stock_factory(ticker_sym)
        #    connection.request_market_depth(ticker_id, contract)


    def ib_account(self, evt):
        """ update_account_value(...) -> message the account supervisor 
            with authoritative account data 
        """
        self.account.update_account_value(evt.key, evt.value, evt.currency)

    def ib_error(self, evt):
        """ error(id, code, msg) -> saves error data to this instance

        """
        error_id, error_code, error_msg = \
            evt.error_id, evt.error_code, evt.error_msg

        self.errors.setdefault(error_code, [])
        self.errors[error_code].append((time.time(), error_id, error_msg))

    def ib_execution_details(self, evt):
        """ execution_details(...) -> messages the account supervisor 
            with the execution reports

            This method converts the contract object supplied by Ib into the
            contract type from the base module.
        """
        co = base.Contract()
        co.__dict__.update(evt.contract.__dict__)
        self.account.execution_details(evt.order_id, co, evt.details)

    def ib_next_id(self, evt):
        """ next_valid_id(order_id) -> messages the account supervisor 
            with the next order id that the broker will accept
        """
        self.account.next_valid_id(evt.next_valid_id)

    def ib_news_bulletin(self, evt):
        item = (evt.news_id, evt.news_type, evt.news_message, evt.news_exchange)
        self.news.append(item)

    def ib_open_order(self, evt):
        """ open_order(...) -> message the account supervisor
            with the details of a new order

            This method converts the contract and order objects supplied by Ib
            into the contract and order types from the base module.
        """
        order_id, contract, order = evt.order_id, evt.contract, evt.order
        co, oo = base.Contract(), base.Order()
        co.__dict__.update(contract.__dict__)
        oo.__dict__.update(order.__dict__)
        self.account.existing_order(order_id, co, oo)

    def ib_order_status(self, evt):
        """ order_status(...) -> message the account supervisor 
            with new details for an existing order
        """
        hfunc = self.account.order_status

        order_id, message, filled, remaining, avg_fill_price, perm_id, \
            parent_id, last_fill_price = evt.order_id, evt.message, evt.filled, \
            evt.remaining, evt.avg_fill_price, evt.perm_id, evt.parent_id, \
            evt.last_fill_price
        hfunc(order_id, message, filled, remaining, avg_fill_price, perm_id, 
              parent_id, last_fill_price)

    def ib_ticker(self, evt):
        """ tick_message(...) -> message the tickers supervisor 
            with new ticker data 

            The results of the ticker message, if any, are treated as a buy/sell
            signal.  This signal is passed to the account supervisor for 
            consideration.
        """
        ticker_id, field, value = evt.ticker_id, evt.field, evt.value
        try:
            signal = self.tickers.tick_message(ticker_id, field, value)
            #print >> sys.__stdout__, signal, self.tickers[ticker_id]
            if signal and signal.direction:
                self.account.put_ticker_signal(signal)
        except (Exception, ), ex:
            self.tick_message_exception = ex

    def ib_market_depth(self, evt):
        """ update_market_depth(...) -> messages the tickers supervisor 
            with market depth data 
        """
        ticker_id, position, operation, side, price, size = \
            evt.ticker_id, evt.position, evt.operation, evt.side, evt.price, evt.size
        self.tickers.depth_message(ticker_id, position, operation, side, price, 
                                   size)

    def ib_portfolio(self, evt):
        """ update_portfolio(...) -> messages the account supervisor 
            with new portfolio data 
        """
        contract, position, market_price, market_value = \
            evt.contract, evt.position, evt.market_price, evt.market_value
        for ob in (self.account, self.tickers, ):
            ob.update_portfolio(contract, position, market_price, market_value)


def build(account=None, connection=None, tickers=None, **kwds):
    """ build(...) -> returns a new BrokerProxy

    """
    return BrokerProxy(account, connection, tickers)
