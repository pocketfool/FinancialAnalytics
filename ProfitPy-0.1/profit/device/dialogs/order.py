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

This module defines the Profit Device application order entry dialog.

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'order.py,v 0.3 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.3',
}

import qt

import kdecore
import kdeui

import profit.device.util as util
import profit.lib.base as base


i18n = kdecore.i18n


class OrderDialog(kdeui.KDialogBase):
    """OrderDialog(...) -> dialog box for placing orders

    """
    exchanges = {
        'Smart' : 'SMART', 
    }

    actions = {
        'Buy' : base.OrderActions.Buy,
        'Sell' : base.OrderActions.Sell,
        'Short': base.OrderActions.ShortSell,
    }

    types = {
        'Limit' : base.OrderTypes.Limit,
        'Market' : base.OrderTypes.Market,
        'Stop' : base.OrderTypes.Stop,
        'Stop Limit' : base.OrderTypes.StopLimit,
    }

    def __init__(self, parent=None):
        buttons = kdeui.KDialogBase.Ok | kdeui.KDialogBase.Cancel
        kdeui.KDialogBase.__init__(self, parent, None, False, None, buttons)
        self.setupControls()
        self.setupLayout()
        self.setupValues()
        self.setupLabels()
        self.setupFinal()


    def setupControls(self):
        """ setupControls() -> create the widgets for this dialog

        """
        mainframe = qt.QFrame(self)
        self.setMainWidget(mainframe)

        self.quantitySpin = kdeui.KIntNumInput(mainframe)
        self.quantitySpin.setRange(1, 5000, 100, True)

        dblnames = ('aux', 'price', )
        combonames = ('symbol', 'action', 'type', 'exchange', )
        labelnames = ('symbol', 'aux', 'action', 'price', 'exchange', 'type', 
                      'quantity', )

        for name in dblnames:
            name = '%sEdit' % name
            setattr(self, name, kdeui.KDoubleNumInput(mainframe))
            getattr(self, name).setRange(0.0, 150.0, 0.01, True)

        for name in combonames:
            setattr(self, '%sCombo' % name, qt.QComboBox(0, mainframe))

        for name in labelnames:
            setattr(self, '%sLabel' % name, qt.QLabel(mainframe))


    def setupLayout(self):
        """ setupLayout() -> layout the widgets in the dialog

        """
        layout = qt.QGridLayout(self.mainWidget(), 1, 1, 6)
        addwidget = layout.addWidget
        addwidget(self.symbolLabel, 0, 0)
        addwidget(self.symbolCombo, 0, 1)
        addwidget(self.actionLabel, 1, 0)
        addwidget(self.actionCombo, 1, 1)
        addwidget(self.typeLabel, 2, 0)
        addwidget(self.typeCombo, 2, 1)
        addwidget(self.exchangeLabel, 3, 0)
        addwidget(self.exchangeCombo, 3, 1)
        addwidget(self.quantityLabel, 0, 2)
        addwidget(self.quantitySpin, 0, 3)
        addwidget(self.priceLabel, 1, 2)
        addwidget(self.priceEdit, 1, 3)
        addwidget(self.auxLabel, 2, 2)
        addwidget(self.auxEdit, 2, 3)

        layout.setColStretch(1, 10)
        layout.setColStretch(3, 10)

        #self.setTabOrder(self.quantitySpin, self.priceEdit)
        #self.setTabOrder(self.priceEdit, self.auxEdit)
        #self.setTabOrder(self.auxEdit, self.symbolCombo)
        #self.setTabOrder(self.symbolCombo, self.actionCombo)
        #self.setTabOrder(self.actionCombo, self.typeCombo)
        #self.setTabOrder(self.typeCombo, self.exchangeCombo)

    def setupValues(self):
        """ setupValues() -> fill a few combo boxes

        """
        defs = ((self.exchanges, self.exchangeCombo),
                (self.actions, self.actionCombo),
                (self.types, self.typeCombo), )

        for lookup, widget in defs:
            widget.clear()
            values = lookup.keys()
            values.sort()
            for value in values:
                widget.insertItem(i18n(value))


    def setupLabels(self):
        """ setupLabels() -> set the labels

        """
        self.setCaption(i18n('Order Entry'))
        self.setButtonOKText(i18n('Submit'))
        self.symbolLabel.setText(i18n('Symbol'))
        self.auxLabel.setText(i18n('Aux'))
        self.actionLabel.setText(i18n('Action'))
        self.priceLabel.setText(i18n('Price'))
        self.exchangeLabel.setText(i18n('Exchange'))
        self.typeLabel.setText(i18n('Type'))
        self.quantityLabel.setText(i18n('Quantity'))


    def setupFinal(self):
        """ setupFinal() -> final stuff

        """
        self.connect(self, qt.SIGNAL('okClicked()'), self.emitOrder)
        self.resize(self.mainWidget().minimumSizeHint())


    def configFromSymTable(self, table):
        """ configFromSymTable(table) -> configure the dialog from a sym table

        """
        symcombo = self.symbolCombo
        symcombo.clear()
        for item in table:
            symcombo.insertItem(item[1])


    def configFromSymView(self, parent):
        """ configFromSymView(parent) -> set some widget values from parent

        """
        context = parent.context
        context_sym = context.text(0)

        symcombo = self.symbolCombo
        symcombo.clear()

        listview_items = [item for item in parent.items()]
        listview_items.sort()

        for listview_item in listview_items:
            symcombo.insertItem(listview_item.pixmap(0), listview_item.text(0))
            if context_sym == listview_item.text(0):
                symcombo.setCurrentItem(symcombo.count() - 1)

        ## setup the price line entries
        currentbid = context.ticker.current_data.get(1, 0.0)
        for wid in (self.priceEdit, self.auxEdit):
            wid.setRange(currentbid-10, currentbid+10, 0.01, 0.1)
            wid.setValue(currentbid)


    def emitOrder(self):
        """ emitOrder() -> emit an order and a contract

        """
        symbol = '%s' % self.symbolCombo.currentText()
        action = self.actions['%s' % self.actionCombo.currentText()]
        orty = self.types['%s' % self.typeCombo.currentText()]

        quan = self.quantitySpin.value()
        lmt = self.priceEdit.value()
        aux = self.auxEdit.value()

        contract = base.Contract.stock_factory(symbol)
        order = base.Order(quantity=quan, limit_price=lmt, aux_price=aux, 
                           open_close='O', action=action, order_type=orty)
        self.emit(util.sigSubmitOrder, (contract, order))


if __name__ == '__main__':
    import profit.device.about as about
    ttl = 'Profit Device Configuration'
    win, app = util.kMain(OrderDialog, ttl, about=about.aboutData)

    win.configFromSymTable(([100, 'ADBE'], [101, 'AAPL']))
    win.show()
    app.exec_loop()
