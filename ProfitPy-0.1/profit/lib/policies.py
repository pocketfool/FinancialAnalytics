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
""" A hierarchy of policy handlers

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'policies.py,v 0.4 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.4',
}

import Queue
import threading
import time

import profit.lib.base as base


class AccountPolicy(object):
    """ AccountPolicy() -> base account policy type

    """


class EnforceDirectionPolicy(AccountPolicy):
    """ EnforceDirectionPolicy() -> ensures guidance has a direction 

    """
    def handle(self, parent, ticker, guidance):
        try:
            return not not guidance.direction
        except AttributeError:
            return 0


class LimitPositionSizePolicy(AccountPolicy):
    """ LimitPositionSizePolicy() -> limits position size

    """
    max_long = 600
    max_short = -300

    def handle(self, parent, ticker, guidance):
        ## needs to account for open order size + current position size
        if guidance.order.open_close == base.OrderPositions.Close:
            return 1

        try:
            ## match size and direction to current position if any
            csize = parent.positions[ticker.symbol].position
            cdir = csize / abs(csize)
        except (KeyError, ZeroDivisionError, ):
            ## no open position, nothing to limit
            return 1 

        if csize > 0:
            return csize <= self.max_long
        elif csize < 0:
            return csize > self.max_short
        else:
            ## unreachable
            return 0


class NetEquityPolicy(AccountPolicy):
    """ NetEquityPolicy() -> reject guidance when net equity < initial margin

    """
    def handle(self, parent, ticker, guidance):
        current_data = parent.current_data
        neteq = current_data.get(base.AccountKeys.EquityWithLoanValue, 0)
        initmarg = current_data.get(base.AccountKeys.InitMarginReq, 0)
        return neteq > initmarg


class OrderDataPolicy(AccountPolicy):
    """ OrderDataPolicy() -> construct contract and order based on guidance

    """
    default_size = 100

    def handle(self, parent, ticker, guidance):
        symb = ticker.symbol
        csize, cdir = 0, 0
        try:
            ## match size and direction to current position if any
            csize = parent.positions[symb].position
            cdir = csize / abs(csize)
        except (KeyError, ZeroDivisionError, ):
            pass

        if guidance.direction == base.Directions.Long:
            ## long guidance; determine buy/open or close/sell
            if cdir == 0 or cdir == base.Directions.Long:
                size = self.default_size
                ooc = base.OrderPositions.Open
                oact = base.OrderActions.Buy
            elif cdir == base.Directions.Short:
                size = csize
                ooc = base.OrderPositions.Close
                oact = base.OrderActions.Buy
        elif guidance.direction == base.Directions.Short:
            ## short guidance; determine ssell/open or close/sell
            if cdir == 0 or cdir == base.Directions.Short:
                size = self.default_size
                ooc = base.OrderPositions.Open
                oact = base.OrderActions.ShortSell
            elif cdir == base.Directions.Long:
                size = csize
                ooc = base.OrderPositions.Close
                oact = base.OrderActions.Sell

        elif guidance.direction == base.Directions.NoDirection:
            ## guidance was neither long or short; nothing to do
            return 0
        else:
            ## unknown direction 
            return 0

        ## add 'contract' and 'order' attributes to the guidance for other
        ## handlers to reference
        guidance.contract = base.Contract.stock_factory(symb)
        guidance.order = base.Order(quantity=abs(size), limit_price=0,
                                          aux_price=0, open_close=ooc,
                                          origin=0, transmit=1, tif="DAY",
                                          action=oact, order_type="LMT")
        return 1


class PricePolicy(AccountPolicy):
    """ PricePolicy() -> tweak the order price

    """
    open_adjust = 0.02
    close_adjust = 0.02

    def handle(self, parent, ticker, guidance):
        try:
            ask = ticker.current_data[base.PriceTypes.Ask]
            bid = ticker.current_data[base.PriceTypes.Bid]
            #lst = ticker.current_data[base.PriceTypes.Last]
        except (KeyError, ):
            return 0

        price = ask
        if guidance.order.action == base.OrderActions.ShortSell:
            price = bid
        if guidance.order.open_close == base.OrderPositions.Close:
            price = bid

        guidance.order.limit_price = price
        guidance.order.aux_price = price
        return 1


class ConflictingOrderPolicy(AccountPolicy):
    """ ConflictingOrderPolicy() -> reject guidance in conflict with open orders

    """
    def handle(self, parent, ticker, guidance):
        sym = guidance.contract.symbol
        ordd = parent.orders.active_items()
        theseords = [o for oid, o in ordd if o.contract.symbol == sym]

        if theseords:
            return not reduce(base.orders_agree, theseords)
        else:
            return 1


class ReverseDirectionPolicy(AccountPolicy):
    """ ReverseDirectionPolicy() -> rejects reverse directions without an existing position

    """
    def handle(self, parent, ticker, guidance):
        if not guidance.reverse:
            ## not a reverse - okay as is
            return 1
        else:
            try:
                csize = parent.positions[ticker.symbol].position
                ## reverse - reject an empty position or allow an open one
                return not not csize
            except (KeyError, ):
                ## reverse - don't even have a position so reject the guidance
                return 0


class LeverageValuePolicy(AccountPolicy):
    """ LeverageValuePolicy() -> reject guidance when leverage is too high

    """
    max_leverage = 1.5

    def handle(self, parent, ticker, guidance):
        iscloseorder = guidance.order.open_close == base.OrderPositions.Close
        cleverage = parent.current_data[base.AccountKeys.Leverage]
        leverageok = cleverage < self.max_leverage
        return  iscloseorder or leverageok


class OrderPlacingPolicy(AccountPolicy):
    """ OrderPlacingPolicy() -> sends acceptable orders to the socket connection

    """
    def handle(self, parent, ticker, guidance):
        if not parent.order_acceptable(guidance.order):
            return 0

        oid = parent.order_id_generator.next()
        c = guidance.contract
        o = guidance.order

        parent.orders.new_order(order_id=oid, contract=c, order=o)
        parent.connection.place_order(oid, c, o)
        return 1


class OrderPolicyHandler(threading.Thread):
    """ OrderPolicyHandler -> maps ticker guidance to policies
        
    """
    ## a specific, ordered list of policies
    policy_classes = [
        ## explicity enforce guidance with specific direction
        EnforceDirectionPolicy,

        ## ensures net equity > init margin
        NetEquityPolicy,

        ## ensures reverse directions aren't treated as opening 
        ReverseDirectionPolicy,

        ## adds .contract and .order attributes to guidance
        OrderDataPolicy,

        ## rejects orders when too far leveraged
        LeverageValuePolicy,
                
        ## rejects guidance conflicting with open orders
        ConflictingOrderPolicy,

        ## rejects guidance when a position would be too large
        LimitPositionSizePolicy,

        ## adjusts order prices
        PricePolicy,

        ## places orders using parent.connection
        OrderPlacingPolicy,
    ]


    def __init__(self, auto_start=False):
        threading.Thread.__init__(self)
        self.setDaemon(1)
        self.guidance_queue = Queue.Queue()
        self.policies = [pc() for pc in self.policy_classes]
        self.guidance_reports = []
        if auto_start:
            self.start()

    def run(self):
        """ loop over the guidance queue and process its items """
        while 1:
            supervisor, guidance = self.guidance_queue.get()
            ticker = guidance.ticker
            last_check = 0
            for policy in self.policies:
                ## bust up the for loop if one of the
                ## policies does not handle the guidance
                last_check = policy.handle(supervisor, ticker, guidance)
                if not last_check:
                    break

            ## unsure of the usefulness of this
            report = {'time' : time.time(),
                      'symbol' : ticker.symbol,
                      'direction' : guidance.direction,
                      'last policy' : policy.__class__.__name__,
                      'last result' : last_check, }
            self.guidance_reports.append(report)
