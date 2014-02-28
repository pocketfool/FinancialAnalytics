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

This module defines examples of session builder functions.  These functions 
are used during session object creation, and they must take keyword-style 
arguments


"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'simple.py,v 0.4 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.4',
}

import Ib.Socket as ibsocket
import profit.lib.account as account
import profit.lib.policies as policies


def connection_id_from_database(**kwds):
    """ here's a perfect opportunity to lookup a client id from an external 
        datasource.  this example doesn't do that, of course.

    """
    client_id = 1234
    return ibsocket.build(client_id=client_id)


def modified_account_object(connection=None, **kwds):
    """ this function does pretty much the same thing as the default account 
        builder (profit.lib.account.build).

    """
    min_cash = 10000
    initial_order_id = 1234
    executions = account.AccountExecutions()
    positions = account.AccountPortfolio()
    policy = policies.OrderPolicyHandler(auto_start=True)
    return account.AccountSupervisor(connection, min_cash, executions,
                                     positions, policy, initial_order_id)


def small_tickers_listing(**kwds):
    """ this builder specifies a short list of tickers.

    """
    somesymbols = ('AAPL,ADBE,AMAT,BEAS,BRCD,CEPH,CHKP,CNXT,CSCO,CTXS,DELL,'
                   'DISH,EBAY,GILD,JNPR,KLAC,MEDI,MERQ,NVDA,NVLS,PDLI')
    somesymbols = somesymbols.split(',')
    somesymbols.sort()
    return [(index+100, symbol) for index, symbol in enumerate(somesymbols)]


