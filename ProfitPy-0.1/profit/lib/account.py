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
""" Defines the AccountSupervisor and related types

    The AccountSupervisor manages orders, positions, and interprets the 
    authoritative data updates from the broker.

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'account.py,v 0.3 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.3',
}

import time

import profit.lib.base as base
import profit.lib.orders as orders
import profit.lib.policies as policies


def order_id_gen(order_id):
    """ order_id_gen(order_id) -> simple generator for consecutive order ids

    """
    while True:
        yield order_id
        order_id += 1


class AccountSupervisor(base.AttributeMaskMixin):
    """AccountSupervisor(...)  -> manages account data, orders, and positions

    """
    def __init__(self, connection, min_cash, executions, positions, 
                 policy, initial_order_id):
        self.connection = connection
        self.min_cash = min_cash
        self.executions = executions
        self.positions = positions
        self.policy = policy
        self.orders = orders.build(account=self)
        self.order_id_generator = order_id_gen(initial_order_id)

        self.current_data = {}
        self.history_data = {}
        self.initial_data = {}
        self.maskattrs('connection', 'policy', 'order_id_generator', 
                       'orders')

    def __str__(self):
        return '<%s %s current_data: %s>' % (self.__class__.__name__, 
                                             id(self), self.current_data, )

    def cash_minus_orders(self):
        """cash_minus_orders() -> available cash minus cost of pending orders 

        """
        cash = self.current_data[base.AccountKeys.SettledCash]
        pending_balance = self.orders.pending_balance()
        return float(cash) - pending_balance

    def execution_details(self, order_id, contract, execution):
        """execution_details(...) -> stow away the execution data 

        """
        self.executions.setdefault(order_id, [])
        self.executions[order_id].append((time.time(), contract, execution))

    def existing_order(self, order_id, contract, order):
        """existing_order(...) -> broker indicates an existing order 

        """
        if self.orders.has_key(order_id):
            return 0
        else:
            return self.orders.new_order(order_id, contract, order)

    def next_valid_id(self, order_id):
        """next_valid_id(order_id) -> broker indicates next valid order id

        """
        self.order_id_generator = order_id_gen(order_id)

    def order_acceptable(self, order):
        """order_acceptable(order) -> determines if an order is acceptable 

        """
        if order.open_close == base.OrderPositions.Close:
            return 1

        if order.action == base.OrderActions.Sell:
            return 1

        mvalpos = self.current_data[base.AccountKeys.StockMarketValue] > 0
        if order.action == base.OrderActions.ShortSell and mvalpos:
            return 1

        order_cost = base.Order.cost_long(order)
        available_cash = self.cash_minus_orders()
        
        nottoolow = available_cash > self.min_cash
        nottoomuch = (available_cash - order_cost) > self.min_cash
        return nottoolow and nottoomuch

    def order_status(self, order_id, status, filled, remaining, avg_fill_price,
                     perm_id, parent_id, last_fill_price):
        """order_status(...) -> broker indicates current status of an order

        """
        try:
            order_monitor = self.orders[order_id]
            order_monitor(status, filled, remaining, avg_fill_price, perm_id, 
                          parent_id, last_fill_price)
            return 1
        except (KeyError, ):
            return 0

    def put_ticker_signal(self, signal):
        """put_ticker_signal(signal) -> indication of new ticker guidance 

        """
        self.policy.guidance_queue.put_nowait((self, signal))

    def update_account_value(self, key, value, currency):
        """update_account_value(...) -> broker indicates an account value
        
        """
        try:
            value = float(value)
        except ValueError:
            ## probably a string; it's fine as-is
            pass

        self.initial_data.setdefault(key, value)
        self.history_data.setdefault(key, [])
        self.current_data[key] = value
        self.history_data[key].append((time.time(), value))
        return value

    def update_portfolio(self, contract, position, marketprice, marketvalue):
        """update_portfolio(...) -> broker indicates an update to the portfolio

        """
        sym = contract.symbol
        pos = AccountPosition(contract, position, marketprice, marketvalue)
        self.positions[sym] = pos


class AccountExecutions(dict):
    """AccountExecutions() -> allows executions to be identified by type 

    """


class AccountPortfolio(dict):
    """AccountPortfolio() -> allows the portfolio to be identified by type 

    """


class AccountPosition(object):
    """AccountPosition(...) -> encapsulates a position

    """
    def __init__(self, contract, position, marketprice, marketvalue):
        self.contract = contract
        self.position = position
        self.marketprice = marketprice
        self.marketvalue = marketvalue
        self.created = time.time()


def build(connection=None, **kwds):
    """ build(...) -> construct an AccountSupervisor

    """
    min_cash = kwds.get('minimum_cash_balance', 100)
    initial_order_id = kwds.get('initial_order_id', 100)
    executions = kwds.get('executions', AccountExecutions())
    positions = kwds.get('positions', AccountPortfolio())
    policy = kwds.get('policy', None)
    if policy is None:
        policy = policies.OrderPolicyHandler(auto_start=True)

    return AccountSupervisor(connection, min_cash, executions, 
                             positions, policy, initial_order_id)
