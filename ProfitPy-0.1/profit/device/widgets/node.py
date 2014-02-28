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
    'file' : 'node.py,v 0.3 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.3',
}

import qt

import profit.device.util as util

import profit.device.widgets.nodebase as nodebase
import profit.device.widgets.accountnode as accountnode
import profit.device.widgets.ordernode as ordernode
import profit.device.widgets.tickernode as tickernode


def selectSourceCodeNode():
    try:
        import profit.device.widgets.sourceeditor as sourcewidget
    except (ImportError, ):
        import profit.device.widgets.sourceviewer as sourcewidget
    return sourcewidget.SourceCodeRequestNode

SourceCodeRequestNode = selectSourceCodeNode()


##-----------------------------------------------------------------------------
##
## Naming these is useful for subclassing and necessary for introspection
##
##-----------------------------------------------------------------------------
shortStr = nodebase.shortStr

BaseNodeWidget = nodebase.BaseNodeWidget
BaseNodeSplitter = nodebase.BaseNodeSplitter
BaseNodeTabWidget = nodebase.BaseNodeTabWidget
BaseNodeListView = nodebase.BaseNodeListView
MappingNode = nodebase.MappingNode
SequenceNode = nodebase.SequenceNode

AccountSupervisorNode = accountnode.AccountSupervisorNode
AccountExecutionsNode = accountnode.AccountExecutionsNode
AccountPortfolioNode = accountnode.AccountPortfolioNode

ContractNode = ordernode.ContractNode
OrderMonitorNode = ordernode.OrderMonitorNode
OrderSupervisorNode = ordernode.OrderSupervisorNode

TickerSupervisorNode = tickernode.TickerSupervisorNode
TechnicalTickerNode = tickernode.TechnicalTickerNode
TickerSeriesDataNode = tickernode.TickerSeriesDataNode
TickerPriceSizeMapNode = tickernode.TickerPriceSizeMapNode


class DefaultNode(qt.QLabel):
    """DefaultNode(parent, node) -> displays node as a label

    """
    iconName = 'tab_new_bg'
    defaultFrameStyle = qt.QFrame.LineEditPanel | qt.QFrame.Sunken
    defaultMargin = 4

    def __init__(self, parent, node):
        qt.QLabel.__init__(self, shortStr("%s" % (node, )), parent)
        self.setFrameStyle(self.defaultFrameStyle)
        self.setMargin(self.defaultMargin)


class BrokerProxyNode(DefaultNode):
    iconName = 'kcmsystem'


class SessionNode(qt.QIconView):
    """ SessionNode(parent, node) -> widget for a Session object

    """
    iconName = 'blockdevice'

    settings = (
        ('setArrangement', qt.QIconView.LeftToRight),
        ('setResizeMode', qt.QIconView.Adjust),
        ('setSpacing', 10),
        ('setItemsMovable', False),
    )

    def __init__(self, parent, node):
        qt.QIconView.__init__(self, parent)
        self.icons = {}
        for assm_key, assm_value in node.items():
            icon = self.icons[assm_key] = qt.QIconViewItem(self, assm_key)
            pxm = util.loadIcon(assm_value .__class__.__name__)
            icon.setPixmap(pxm)
        for setting_funcname, setting_value in self.settings:
            getattr(self, setting_funcname)(setting_value)



class _socketobjectNode(MappingNode):
    """ _socketobjectNode(parent, node) -> widget for viewing a _socketobject

    """
    focusAllColumns = True

    def refreshNode(self):
        """refreshNode() -> update list view contents from node subject

        """
        import socket

        self.clear()
        socket_object = self.node
        func_attrs = ('fileno', 'getsockname', 'getpeername', 'gettimeout')

        for method_name in func_attrs:
            try:
                results = getattr(socket_object, method_name)()
            except (socket.error, ):
                pass
            else:
                qt.QListViewItem(self, method_name, str(results))
