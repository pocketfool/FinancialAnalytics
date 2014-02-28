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
""" Client interface for viewing nodes

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'node.py,v 0.3 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.3',
}

import qt

import kdeui

import profit.device.link as link
import profit.device.util as util
import profit.device.widgets.node as nodewidgets

import profit.lib.base as base


def nodeWidgetType(node, default=nodewidgets.DefaultNode):
    """ nodeWidgetType(node, [default]) -> returns widget suitable for node

    """
    try:
        node_widget_name = '%sNode' % (node.__class__.__name__, )
    except AttributeError:
        node_widget_name = ''
    node_type = nodewidgets.__dict__.get(node_widget_name, default)
    if node_type is default:
        if isinstance(node, (tuple, list, )):
            node_type = nodewidgets.SequenceNode
        elif isinstance(node, (dict, )):
            node_type = nodewidgets.MappingNode
    return node_type


def nodeWidgetFactory(parent, node):
    """ nodeWidgetFactory(parent, node) -> creates widgets suitable to a node

    """
    default = nodewidgets.DefaultNode
    node_widget_type = nodeWidgetType(node, default)
    node_widget = node_widget_type(parent, node)
    parent.layout().addWidget(node_widget)
    if issubclass(node_widget_type, default):
        parent.layout().addStretch(100)
    link.connect(node_widget)
    return node_widget


class NodeFrame(qt.QFrame):
    """ NodeFrame(...) -> the frame wrapper for displaying a node.

        Using a frame allows the client, the viewer, to include other types of
        widgets in its display.
    """
    def __init__(self, parent, node, label):
        qt.QFrame.__init__(self, parent)
        self.label = label
        self.node = node
        self.box_layout = qt.QVBoxLayout(self, 3, 3)
        self.node_widget = nodeWidgetFactory(self, node)


class NodeViewer(qt.QObject):
    """ NodeViewer() -> displays node items on its parent

    """
    def viewNode(self, item):
        """ viewNode(item) -> show a new node as a tab page

        """
        iconname = ''
        try:
            node = item.node
        except (AttributeError, ):
            node = item
        try:
            iconname = nodeWidgetType(node).iconName
        except (AttributeError, ):
            pass
        try:
            iconname = item.symbol.lower()
        except (AttributeError, ):
            pass
        try:
            if item.parent():
                label = '%s.%s' % (item.parent().text(0), item.text(0), )
            else:
                label = '%s' % (item.text(0), )
        except (AttributeError, ):
            try:
                label = item.symbol
            except (AttributeError, ):
                label = str(item)

        parent = self.parent()
        framector = base.PartialCall(NodeFrame, node=node, label=label)
        center = kdeui.KDockWidget.DockCenter
        dock, obj = parent.buildDock(label, iconname, framector, transient=True)
        dock.manualDock(parent.getMainDockWidget(), center, 20)
        dock.dockManager().makeWidgetDockVisible(obj)
        self.connect(dock, util.sigDockClosed, self.closeClicked)

    def closeClicked(self):
        """ closeClicked() -> signal the parent to remove a dock

        """
        dock = self.sender()
        self.parent().removeDock(dock)
