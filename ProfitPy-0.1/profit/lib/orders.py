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
""" Defines the OrderSupervisor and related types.

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'orders.py,v 0.3 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.3',
}

import threading
import time

import profit.lib.base as base


class OrderSupervisor(dict, base.AttributeMaskMixin):
    """ OrderSupervisor(account) -> maps order ids to monitor objects

    """
    def __init__(self, account, monitor_type, mutator_type):
        self.account = account
        self.monitor_type = monitor_type
        self.mutator = mutator_type(supervisor=self)
        self.maskattrs('mutator')

    def active_items(self):
        """ active_items() -> returns sequence of (order_id, order_object) pairs

        """
        return [(o_id, o_obj) for o_id, o_obj in self.items() if o_obj.active]

    def resend_as_market(self, order_id):
        """ resend_as_market(order_id) -> resends order_id as Market order

        """
        mon = self[order_id]
        mon.order.order_type = base.OrderTypes.Market
        self.account.connection.place_order(order_id, mon.contract, mon.order)

    def cancel(self, order_id):
        """ cancel(order_id) -> cancels order identified by order_id 

        """
        self.account.connection.cancel_order(order_id)

    def new_order(self, order_id, contract, order):
        """ new_order(order_id, contract, order) -> makes new order monitor

        """
        self[order_id] = self.monitor_type(self, contract, order, order_id)

    def pending_balance(self):
        """ pending_balance() -> cost of active and open orders

        """
        cost = base.Order.cost_ignore_sells
        return sum([cost(o.order) for o in self.values() if o.active])


class OrderMonitor(object):
    """ OrderMonitor(...) -> monitors an individual order 

    """
    def __init__(self, supervisor, contract, order, order_id):
        self.supervisor = supervisor
        self.contract = contract
        self.order = order
        self.order_id = order_id

        self.active = 1
        self.filled = 0
        self.created = time.time()

        self.reports = []
        self.messages = []

        self.status_calls  = {
            base.OrderStatus.Cancelled : self.message_cancel,
    
            base.OrderStatus.PendingCancel : 
                base.PartialCall(self.message_basic, msg='Pending Cancel'),
    
            base.OrderStatus.Submitted :
                base.PartialCall(self.message_basic, msg='Submitted'),
    
            base.OrderStatus.PendingSubmit :
                base.PartialCall(self.message_basic, msg='Pending Submit'),
    
            base.OrderStatus.Inactive :
                base.PartialCall(self.message_basic, msg='Inactive'),
    
            base.OrderStatus.PreSubmitted :
                base.PartialCall(self.message_basic, msg='Pre Submit'),
        }
        self.message_basic('Created')


    def __call__(self, status, filled, remaining, avg_fill_price, perm_id,
                 parent_id, last_fill_price):
        """ tws sucks in the area of proper and reliable order notification 

        """
        self.reports.append((
            time.time(), status, filled, remaining, avg_fill_price, perm_id, 
            parent_id, last_fill_price,
        ))

        status_func = self.status_calls.get(status, None)
        if status_func is not None:
            status_func()
        elif status == base.OrderStatus.Filled:
            self.filled += filled
            self.message_basic("Filled %s Remaining %s" % (filled, remaining))
            filled_max = self.order.quantity == filled
            filled_all = remaining == 0
            if filled_all or filled_max:
                self.active = 0
        else:
            um = {'status':status, 'filled':filled, 'remaining':remaining,
                  'price':avg_fill_price, 'perm_id':perm_id, }
            self.message_basic('Unknown %s' % (um, ))

    def message_basic(self, msg):
        """ message_basic(msg) -> add a message

        """
        self.messages.append((time.time(), msg))

    def message_cancel(self):
        """ message_cancel() -> add a cancel message and set inactive

        """
        self.message_basic('Canceled')
        self.active = 0


class OrderMutator(threading.Thread):
    """ OrderMutator(supervisor, [order_ttl]) -> order modification thread

    """
    def __init__(self, supervisor, order_ttl=120, snooze=5, automatic=True):
        threading.Thread.__init__(self)

        self.supervisor = supervisor
        self.order_ttl = order_ttl
        self.snooze = snooze
        self.history = []

        self.setDaemon(1)
        if automatic:
            self.start()

    def run(self):
        history_func = self.history.append
        cancel_func = self.supervisor.cancel
        resend_func = self.supervisor.resend_as_market
        orders_func = self.supervisor.items

        time_func = time.time
        open_pos = base.OrderPositions.Open
        close_pos = base.OrderPositions.Close

        while 1:
            time.sleep(self.snooze)
            now = time.time()
            ttl = self.order_ttl

            mutate_orders = [(oid, oobj)
                                for oid, oobj in orders_func()
                                    if oobj.active and now > oobj.created + ttl]

            for orderid, ordermon in mutate_orders:
                try:
                    if ordermon.order.open_close == open_pos:
                        cancel_func(orderid)
                        history_func((time_func(), 'cancel', orderid))
                    elif ordermon.order.open_close == close_pos:
                        resend_func(orderid)
                        history_func((time_func(), 'adjusted', orderid))
                except (Exception, ), ex:
                    history_func((time_func(), 'exception', '%s' % ex))


def build(account):
    """ build(account) -> build an OrderSupervisor for the account

    """
    return OrderSupervisor(account=account,
                           mutator_type=OrderMutator,
                           monitor_type=OrderMonitor)
