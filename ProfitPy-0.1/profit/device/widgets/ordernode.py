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
""" profit.widgets.node -> widgets to display session objects


"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'ordernode.py,v 0.5 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.5',
}

import time

import qt

import profit.device.link as link
import profit.device.util as util
import profit.device.widgets.nodebase as nodebase


alignCenter = qt.Qt.AlignCenter
alignLeft = qt.Qt.AlignLeft
alignRight = qt.Qt.AlignRight


shortStr = nodebase.shortStr
BaseNodeWidget = nodebase.BaseNodeWidget
BaseNodeListView = nodebase.BaseNodeListView
MappingNode = nodebase.MappingNode
SequenceNode = nodebase.SequenceNode


def unwrapOrder(item):
    """ unwrapOrder(item) -> returns the order monitor given a list view item

    """
    return item.om[1]


##-------------------------------------------------------------------------
##
## Order Supervisor Node and related widgets
##
##-------------------------------------------------------------------------
class OrderMonitorNode(qt.QVBox):
    """ OrderMonitorNode() -> widget for an OrderMonitor object

    """
    defaultMargin = 4

    def __init__(self, parent, node):
        qt.QVBox.__init__(self, parent)
        d = dict([(k, v) for k, v in node.__dict__.items()])
        self.listView = MappingNode(self, d)
        self.listView.setColumnText(1, "Type")
        self.listView.setColumnAlignment(1, alignLeft)


class ContractNode(qt.QVBox):
    """ ContractNode(parent, node) -> widget for a viewing a Contract object

    """
    defaultMargin = 4

    def __init__(self, parent, node):
        qt.QVBox.__init__(self, parent)
        self.listView = MappingNode(parent=self, node=node.__dict__)


class OrderSupervisorNode(BaseNodeWidget):
    """OrderSupervisorNode(...) -> combined display of orders

    """
    iconName = 'kcalc'

    def __init__(self, parent, node):
        BaseNodeWidget.__init__(self, parent, node)

        mainsplitter = qt.QSplitter(qt.QSplitter.Vertical, self)
        orderslistview = OrderSupervisorList(mainsplitter, node)
        tabssplitter = qt.QSplitter(qt.QSplitter.Horizontal, mainsplitter)

        ordertabs = qt.QTabWidget(tabssplitter)
        ordertab = OrderTab(ordertabs, {})
        ordertabs.insertTab(ordertab, "Order")

        reporttab = ReportTab(ordertabs, [])
        ordertabs.insertTab(reporttab, "Report")

        messagestab = MessagesTab(ordertabs, {})
        ordertabs.insertTab(messagestab, "Messages")

        contracttabs = qt.QTabWidget(tabssplitter)
        contracttab = ContractTab(contracttabs, {})
        contracttabs.insertTab(contracttab, "Contract")

        layout = qt.QVBoxLayout(self)
        layout.addWidget(mainsplitter)

        for widget in (ordertabs, tabssplitter, contracttabs, ):
            widget.setMargin(0)

        for widget in (ordertab, contracttab, messagestab, reporttab):
            self.connect(orderslistview, util.sigSelectChanged, 
                         widget.displayOrderItem)
            self.connect(orderslistview, util.sigOrdersUpdated,
                         widget.displayOrderItem)

        firstitem = orderslistview.firstChild()
        if firstitem:
            orderslistview.setSelected(firstitem, True)
        link.connect(orderslistview)

class OrderSupervisorListItem(qt.QListViewItem):
    def compare(self, item, column, ascending):
        a = self.text(column)
        b = item.text(column)
        try:
            a = int(str(a))
        except (ValueError, ):
            pass
        try:
            b = int(str(b))
        except:
            pass
        return cmp(a, b)


class OrderSupervisorList(BaseNodeListView):
    """OrderSupervisorNode(parent, node) -> displays orders

    """
    focusAllColumns = True
    activeLookup = {1 : 'Yes', 0 : 'No', }
    actionLookup = {'BUY' : 'Buy', 'SELL' : 'Sell', 'SSHORT' : 'Short', }
    orderTypeLookup = {'LMT' : 'Limit', 'MKT' : 'Market', }
    openCloseLookup = {'O' : 'Open', 'C' : 'Close', }

    columnDefs = (
        ('Order Id', 60, alignRight,),
        ('Symbol', 60, alignLeft,),
        ('Size', 50, alignRight,),
        ('Active', 60, alignRight,),
        ('Action', 60, alignRight,),
        ('Type', 60, alignRight,),
        ('Limit Price', 70, alignRight,),
        ('Aux Price', 70, alignRight,),
        ('Open Close', 80, alignRight,),
        ('Filled', 80, alignRight,),
        ('Remaining', 80, alignRight,),
    )

    def __init__(self, parent, node):
        BaseNodeListView.__init__(self, parent, node)
        self.setupNode()
        self.connect(self, util.sigDoubleClicked, self.handleShowTicker)

    def handleShowTicker(self, item):
        """handleShowTicker(item) -> display a ticker node in separate window

        """
        sym, pixmap = unwrapOrder(item).contract.symbol, item.pixmap(1)
        self.emit(util.sigViewTicker, (sym, pixmap))

    def setupNode(self):
        """setupNode() -> build this objectTrees

        """
        for oid, order_mon in self.node.items():
            self.setupItem(oid, order_mon, None)

    def setupItem(self, oid, omon, item):
        """setupItem(...) -> build a list view item

        """
        if not item:
            #item = qt.QListViewItem(self)
            item = OrderSupervisorListItem(self)
        item.om = (oid, omon)
        vals = self.valueList(oid, omon)
        for c, v in enumerate(vals):
            item.setText(c, v)
        sym = omon.contract.symbol.lower()
        item.setPixmap(1, util.loadIcon(sym))

    def valueList(self, oid, omon):
        """valueList(oid, omon) -> list of values for a row item

        """
        active_get = self.activeLookup.get
        order_type_get = self.orderTypeLookup.get
        order = omon.order

        items = [
            self.formatOrderId(oid), 
            omon.contract.symbol, 
            order.quantity,
            active_get(omon.active, omon.active),
            active_get(order.action, order.action),
            order_type_get(order.order_type, order.order_type),
            order.limit_price,
            order.aux_price,
            self.openCloseLookup.get(order.open_close, order.open_close),
            omon.filled,
            order.quantity - omon.filled,
        ]
        return [str(item) for item in items]

    def formatOrderId(self, oid):
        """formatOrderId(order_id) -> zero-padded string for an order id

        """
        return '%s' % (oid, )

    def slotOpenOrder(self, event):
        """ slotOpenOrder(event) -> set the order list view item

            uncertain of the actual value of this
        """
        oid = event.order_id
        if not self.node.has_key(oid):
            return

        item = self.findItem(str(oid), 0)
        self.setupItem(oid, self.node[oid], item)

    def slotOrderStatus(self, event):
        """ slotOrderStatus(event) -> set the order list view item

        """
        oid = event.order_id
        if not self.node.has_key(oid):
            return
        item = self.findItem(self.formatOrderId(str(oid)), 0)
        self.setupItem(oid, self.node[oid], item)
        if item == self.currentItem():
            self.emit(util.sigOrdersUpdated, (item, ))

    def refreshNode(self):
        """refreshNode() -> handle a request to refresh this node

        """
        self.clear()
        self.setupNode()


class OrderTab(MappingNode):
    """ OrderTab() -> a tab for an order viewer

    """
    focusAllColumns = True
    columnDefs = (
        ('Item', 75, alignLeft,),
        ('Value', -1, alignLeft,),
    )

    def displayOrderItem(self, item):
        """ displayOrderItem(item) ->

        """
        order = unwrapOrder(item)
        self.node = {
            'Order Id' : order.order_id, 
            'Active' : str(bool(order.active)),
            'Created' : time.ctime(order.created),
            'Filled' : order.filled, 
        }
        self.refreshNode()


class ReportTab(SequenceNode):
    """ReportTab(parent, node) -> 

    """
    focusAllColumns = True
    sorting = (-1, )
    columnDefs = (
        ('Time', 75, alignLeft,),
        ('Status', 100, alignLeft,),
        ('Filled', -1, alignRight,),
        ('Remaining', -1, alignRight,),
        ('Avg Fill', -1, alignRight,),
        ('Perm Id', -1, alignRight,),
        ('Parent Id', -1, alignRight,),
        ('Last Fill', -1, alignRight,),
    )

    def displayOrderItem(self, item):
        """ displayOrderItem(item) -> 

        """
        order = unwrapOrder(item)
        self.node = order.reports
        self.refreshNode()

    def refreshNode(self):
        """ refreshNode() -> 

        """
        self.clear()
        node = self.node[:]
        node.reverse()
        for values in node:
            values = list(values)
            values[0] = time.ctime(values[0]).split()[3]
            values = [self, ] + ['%s' % value for value in values]
            qt.QListViewItem(*values)


class MessagesTab(MappingNode):
    """

    """
    focusAllColumns = True
    columnDefs = (
        ('Item', 75, alignLeft,),
        ('Value', -1, alignLeft,),
    )

    def displayOrderItem(self, item):
        """ displayOrderItem(item) ->

        """
        order = unwrapOrder(item)
        self.node = dict(order.messages)
        self.refreshNode()

    def refreshNode(self):
        """ refreshNode() -> refresh callback

        """
        self.clear()

        items = self.node.items()
        items.sort()
        for key, value in items:
            index = time.ctime(key).split()[3]
            qt.QListViewItem(self, index, shortStr(value))


class ContractTab(MappingNode):
    """

    """
    focusAllColumns = True
    columnDefs = (
        ('Item', 100, alignLeft,),
        ('Value', 100, alignLeft,),
    )

    def displayOrderItem(self, item):
        self.node = unwrapOrder(item).contract.__dict__
        self.refreshNode()
