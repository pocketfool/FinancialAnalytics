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
""" The main window status bar

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'statusbar.py,v 0.4 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.4',
}

import qt

import kdeui

import profit.device.util as util
import profit.lib.base as base


class MainStatusBar(kdeui.KStatusBar):
    """ MainStatusBar() -> status bar with multiple labels for multiple events

    """
    label_width = 150
    message_width = 220

    def __init__(self, parent=None, name=None):
        kdeui.KStatusBar.__init__(self, parent)

        self.event_labels = event_labels = {}
        for name in ['account', 'error', 'ticker', ]:
            event_labels[name] = label = qt.QLabel('', None)
            label.setMinimumWidth(self.label_width)
            self.addWidget(label, 2, False)

        self.message_label = qt.QLabel('', self)
        self.message_label.setAlignment(qt.Qt.AlignRight)
        self.addWidget(self.message_label, 1, True)

        signal_method_map = (
            (util.sigNewSession, self.newSession),
            (util.sigStartTws, self.startTws),
            (util.sigStartTwsFail, self.failStartTws),
            (util.sigConnectedTws, self.connectedTws),
            (util.sigConnectedTwsError, self.failConnectTws),
            (util.sigFinishTws, self.finishTws),
        )
        for signal, method in signal_method_map:
            self.connect(parent, signal, method)

    ##-------------------------------------------------------------------------
    ##
    ## Custom Slots
    ##
    ##-------------------------------------------------------------------------
    def connectedTws(self):
        """ connectedTws() -> display a banner

        """
        self.message_label.setText('Connected to TWS')

    def finishTws(self, process):
        """ finishTws(process) -> display a message that a tws process is done

        """
        txt = 'TWS process %s finished' % (process.processIdentifier(), )
        self.message_label.setText(txt)

    def failConnectTws(self, exception):
        """ failConnectTws() -> display a failure banner

        """
        txt = 'Error connecting to TWS: %s' % (exception, )
        self.message_label.setText(txt)


    def newSession(self, session):
        """ newSession(session) -> display a new session banner

        """
        txt = 'Built session at 0x%x' % (id(session), )
        self.message_label.setText(txt)


    def startTws(self, process):
        """ startTws(process) -> display a banner with tws pid

        """
        txt = 'Stand-alone TWS started, pid %s' % process.processIdentifier()
        self.message_label.setText(txt)


    def failStartTws(self, code):
        """ failStartTws(code) -> show tws startup error banner

        """
        txt = 'Error starting TWS, exit code %s' % (code, )
        self.message_label.setText(txt)


    ##-------------------------------------------------------------------------
    ##
    ## Reimplemented Slots
    ##
    ##-------------------------------------------------------------------------
    def slotTicker(self, event):
        """ slotTicker(event) -> display ticker update banner

        """
        ticker_id, field, value = event.ticker_id, event.field, event.value
        self.setBrokerText('ticker', ticker_id, field, value)


    def slotReaderStop(self, event):
        """ slotReaderStop(event) -> broker disconnect banner

        """
        self.message_label.setText('Broker disconnected')

    def slotAccount(self, event):
        """ slotAccount(event) -> broker update account banner

        """
        key, value, currency = event.key, event.value, event.currency
        self.setBrokerText('account', key, value, currency)


    def slotError(self, event):
        """ slotBrokerError(event) -> display broker error banner

        """
        error_id, error_code, error_msg = \
            event.error_id, event.error_code, event.error_msg
        self.setBrokerText('error', error_id, error_code, error_msg)


    def setBrokerText(self, signal_key, *args):
        """ setBrokerText(key, [...]) -> show broker text appropriatly

        """
        label = self.event_labels.get(signal_key, None)
        format = getattr(self, '%sFormat' % (signal_key, ), None)
        if label and format:
            label.setText(format(*args))


    def tickerFormat(self, ticker_id, field, value):
        """ tickerFormat(...) -> formatted ticker data

        """
        try:
            sym = self.parent().session.tickers[ticker_id].symbol
            label = base.PriceSizeLookup[field]
            return '%4.4s %12.12s %6.6s' % (sym, label, value, )
        except (KeyError, AttributeError, ):
            return ''


    def errorFormat(self, error_id, error_code, error_msg):
        """ errorFormat(...) -> formatted error

        """
        error_msg = error_msg.strip()[0:50]
        return 'Error %s - %s - %s' % (error_id, error_code, error_msg, )


    def accountFormat(self, key, value, *args):
        """ accountFormat(...) -> formatted account data

        """
        return '%s : %s' % (key, value, )

