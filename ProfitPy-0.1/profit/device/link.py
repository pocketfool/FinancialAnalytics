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
""" link -> connects messages from the broker reader thread to the gui

Propegating data from python-threads into Qt seems brittle.  The implementation
below works with a sip/pyqt snapshot, but may break at any point (as has happened
many times).

Previous implementations used qt.qApp.postEvent to propegate data from the 
reader thread, and alternately, locked and unlocked the Qt library mutex.  Both
approaches just stopped working.

This version seems a bit more strong:

    1.  The Ib.Message module is inspected for a set of message types.
    This helps prevent cut-and-paste and hard-coding the method names.

    2.  The QIbSocketReader type inherits QThread, making it safe as a source
    of calls to the gui.

    3.  The MessageTransmitter type uses a metaclass to inject callback methods 
    into its namespace.  This, too, helps get around a whole bunch of poor 
    cut-n-paste reuse.

    4.  A decent client interface is provided for widgets that wish to receive
    signals originating from the IbPy connection.  Clients need only specify the
    receiver of the signal.

The basic idea of this module is that it provides an alternate socket reader
for IbPy connections.  This reader type is a QThread that can interact with
the Qt framework for delivering messages.  In addition to the thread type, 
this module defines a simple way for Qt widgets to hook into the delivery of
these messages.  The client simply defines one or more methods with well-known
names, then passes instances of these widgets to the link.connect function.

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'link.py,v 0.4 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.4',
}

import qt

import Ib.Message
import Ib.Socket


""" The first side of the link defines a QThread for reading IbPy sockets.

This QThread socket reader and the alternate builder function defined for
IbPy connections form a way to read socket data in a Qt-friendly way.

"""


class QIbSocketReader(Ib.Socket.SocketReaderBase, qt.QThread):
    """ QIbSocketReader(...) -> a Qt thread for reading an IbPy socket

    This reader type is an alternate to the default Python threading.Thread 
    subtype.  By making QThread a superclass, instances can readily interoperate
    with the Qt framework.

    This type relies on SocketReaderBase.run for its primary purpose of reading
    socket data.

    The connection object starts its reader on demand; neither the client nor 
    the instance should do that.
    """
    def __init__(self, readers, socket):
        Ib.Socket.SocketReaderBase.__init__(self, readers, socket)
        qt.QThread.__init__(self)

    def build(cls, client_id=0):
        """ buildSocketReader(client_id=0) -> alternate builder for Ib.Sockets
    
        The class method complements the construction by providing a builder
        suitable making an IbPy connection with this reader type.
        """
        return Ib.Socket.build(client_id=client_id, reader_type=cls)
    build = classmethod(build)


""" These functions allow all sides of the link to refer objects and names for 
them in a consistent way.

"""


def messageTypes():
    """ messageTypes() -> returns a list of suitable IbPy message types

    This function returns a mapping of names and message types from the 
    IbPy.Message module.  These types are what IbPy instantiates and delivers
    as messages.
    """
    def isreader(cls):
        """ returns true if a class is a SocketReader subclass """
        basecls = Ib.Message.SocketReader
        return issubclass(cls, basecls) and not cls is basecls

    def istype(cls):
        """ returns true if an object is a type """
        return isinstance(cls, (type, ))

    src = Ib.Message.__dict__.values()
    types = [typ for typ in src if istype(typ) and isreader(typ)]
    return dict([(typ.__name__, typ) for typ in types])


def methodName(name):
    """ methodName(name) -> names a message-to-signal method

    """
    return 'messageSignalLink__%s' % (name, )


def slotName(name):
    """ slotName(name) -> names a slot method

    Clients define methods named 'slotAccount', 'slotTicker', 'slotPortfolio',
    etc.  This module uses that format for introspection of objects wishing to
    connect to the message transmitter.
    """
    return 'slot%s' % (name, )


""" The second side of the link is the MessageTransmitter class.

Instances of this type connect signals that they receive back to the parent
for the magic of qt signal re-emitting.  The transmitMethod static method
builder and the TransmitMethodInjector are used to create the methods 
suitable for callbacks from the IbPy socket reader defined above.

"""


class TransmitMethodInjector(type):
    """ TransmitMethodInjector(...) -> linkage between IbPy msgs and Qt signals

    This metaclass is useful because we can't add methods to instances (e.g., 
    in __init__) because the sip/pyqt framework can't see them.  Adding the 
    methods to the class as it's constructed allows us a resonable way to 
    accomplish the goal.  Plus, it's shorter and stops the need for lame reuse.
    """
    def __new__(cls, name, bases, namespace):
        for msgname in messageTypes():
            namespace[methodName(msgname)] = cls.transmitMethod(msgname)
        return type(name, bases, namespace)

    def transmitMethod(name):
        """ transmitMethod(name) -> returns a method to emit socket messages
    
        """
        signal = qt.PYSIGNAL(name)
    
        def transmit(self, msg):
            """ transmit(msg) -> emit the message as a qt signal
    
            """
            self.emit(signal, (msg, ))
        return transmit
    transmitMethod = staticmethod(transmitMethod)


class MessageTransmitter(qt.QObject):
    """ MessageTransmitter(...) -> proxies IbPy messages to Qt signals

    The metaclass builds methods for receiving IbPy messages.  When constructed,
    instances register these methods with the sessions broker object to receive
    the IbPy messages.  The methods then emit signals with the messages as their
    argument.
    """
    __metaclass__ = TransmitMethodInjector

    def __init__(self, parent, session):
        qt.QObject.__init__(self, parent)

        register = session.broker.connection.register
        for name, msg in messageTypes().items():
            parent.connect(self, qt.PYSIGNAL(name), parent, qt.PYSIGNAL(name))
            slot = getattr(self, methodName(name), None)
            register(msg, slot)


""" The third side of the link is for widgets that want to react to messages.

Widgets can call this connect function as a convenience for connecting to 
the signals from IbPy.  The side effect is that the signal source is hidden
from the client.

"""


def connect(widget, parent=None):
    """ connect(widget) -> connect a widgets known slots to the main gui widget

    """
    if not parent:
        parent = qt.qApp.mainWidget()

    for name in messageTypes():
        meth = getattr(widget, slotName(name), None)
        if meth:
            signal = qt.PYSIGNAL(name)
            parent.connect(parent, signal, meth)
