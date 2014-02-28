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
""" Defines the Session type, the top-most container in the library

The Session class defined below is used by clients to construct a mapping
of well-known keys to objects from this library.  The client using this 
class will have a ready-built set of objects that can connect to the broker
and start trading.

The client can influence construction behavior by specifying keywords to the
constructor.  The useful keywords are:

    tickers_builder
    tickers_mapping_builder
    strategy_builder
    account_builder
    broker_builder

In each case, the nnn_call keywords can be either a callable object or a 
string that names a callable object.  In the case of strings, it should be
in the form of:

    package.subpackage.module.callable

All callables, either passed explicitly or imported, must be callable with
only keyword parameters.  The keywords passed are the session contents and 
the keywords to the constructor.
"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'session.py,v 0.5 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.5',
}

import inspect
import sys

class Defaults(object):
    """ Defaults -> a place holder type for method default arguments

    """
    connection = 'Ib.Socket.build'
    account = 'profit.lib.account.build'
    broker = 'profit.lib.broker.build'
    tickers = 'profit.lib.tickers.build'
    tickers_mapping = 'profit.lib.tickers.default_mapping'
    strategy = None


class Session(dict):
    """ Session(**kwds) -> construct a new session

    """
    defaults = Defaults()
    known_keys = ('connection', 'account', 'tickers', 'broker', 'strategy', )

    def __init__(self, **kwds):
        dict.__init__(self)
        for key in self.known_keys:
            call = getattr(self, 'build_%s' % key)
            self[key] = call(**kwds)
        ## extra references that are nice to have
        self['orders'] = self['account'].orders
        self['positions'] = self['account'].positions

    def call_builder(self, builder, kwdargs):
        """ call_builder(builder, kwdargs) -> call a builder, maybe w/ kwdargs

        This method supports only two call types:  with no args or with kwds.
        """
        ## print >> sys.__stdout__, builder, kwdargs
        if not builder:
            return None

        params = self.copy()
        params.update(kwdargs)
        if not callable(builder):
            builder = import_item(builder)
        args, varargs, varkw, defaults = inspect.getargspec(builder)
        if len(args or ()) == len(defaults or ()) and not varkw:
            return builder()
        else:
            return builder(**params)

    def build_connection(self, connection_builder=defaults.connection, **kwds):
        
        """ build_connection(..) -> return a new socket connection object  

        """
        return self.call_builder(connection_builder, {})

    def build_account(self, account_builder=defaults.account, **kwds):
        """ build_account(...) -> return a new account object  

        """
        return self.call_builder(account_builder, kwds)

    def build_tickers(self, tickers_mapping_builder=defaults.tickers_mapping,
                     tickers_builder=defaults.tickers, **kwds):
        """ build_tickers(...) -> return a new tickers object

        """
        kwds['symbol_table'] = self.call_builder(tickers_mapping_builder, kwds)
        return self.call_builder(tickers_builder, kwds)

    def build_broker(self, broker_call=defaults.broker, **kwds):
        """ build_broker(...) -> return a new broker proxy object


        """
        return self.call_builder(broker_call, kwds)

    def build_strategy(self, strategy_builder=defaults.strategy, **kwds):
        """ build_strategy(...) -> return a new strategy object

        """
        return self.call_builder(strategy_builder, kwds)

    def __getattr__(self, name):
        """ __getattr__(name) -> simulate dict keys as attributes

        """
        try:
            return self[name]
        except (KeyError, ):
            extxt = "'%s' object has no attribute '%s'" 
            extxt = extxt % (self.__class__.__name__, name)
            raise AttributeError(extxt)


def import_name(name):
    """ import_name(name) -> import and return a module by name in dotted form

        Copied from the Python lib docs.
    """
    mod = __import__(name)
    for comp in name.split('.')[1:]:
        mod = getattr(mod, comp)
    return mod


def import_item(name):
    """ import_item(name) -> import an item from a module by dotted name

    """
    names = name.split('.')
    modname, itemname = names[0:-1], names[-1]
    mod = import_name(str.join('.', modname))
    return getattr(mod, itemname)
