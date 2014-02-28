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
""" The session tree list view

The use of Save/Open for session items is questionable.  Even worse, the widget
that does so doesn't bother to send any signals that the objects have changed,
which leaves the shell widget out of sync.

Also, opened objects might not have all of the state necessary to participate in
session trading operations.

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'session.py,v 0.4 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.4',
}

import inspect

import qt

import kdecore
import kfile
import kdeui

import profit.device.util as util
import profit.device.widgets.node as nodewidgets

import profit.lib.base as base
import profit.lib.tools as tools


class TreeItemFormat(object):
    """ TreeItemFormat() -> helper for interpreting node labels and children

    """
    key_formats = {
        0 : lambda key, value: str(key),
        'TechnicalTicker' : lambda idsym, tobj: tobj.symbol,
    }

    label_formats = {
        0 : lambda obj: obj.__class__.__name__,
        'TechnicalTicker' : lambda obj: obj.symbol,
    }

    def getLabel(self, node):
        """ getLabel(node) -> returns an appropriate label for a node

        """
        lookup = self.label_formats.get
        formatter = lookup(node.__class__.__name__, self.label_formats[0])
        return formatter(node)

    def hasNodes(self, node):
        """ hasNodes(node) -> returns the number of usable children of a node

        """
        count = 0

        ## check for these explicitly because len(node) might give string len
        if isinstance(node, (list, tuple, dict, )):
            count += len(node)

        try:
            count += len([k for k in node.__dict__ 
                              if not str(k).startswith('_')])
        except (AttributeError, ):
            pass

        return count

    def getNodes(self, node):
        """ getNodes(node) -> returns children of node in (label, child) pairs

        """
        some = []
        more = []
        lookup = self.key_formats.get

        try:
            some += node.__dict__.items()
        except (AttributeError, ):
            pass

        ## lame
        if node.__class__.__name__ == 'TickerPriceSizeMap':
            some += [(base.PriceSizeLookup[n], v) for n, v in node.items()]
        elif isinstance(node, (dict, )):
            some += node.items()
        some = [(k, v) for k, v in some if not str(k).startswith('_')]

        for k, v in some:
            formatter = lookup(v.__class__.__name__, self.key_formats[0])
            more.append((formatter(k, v), v))

        more.sort(lambda x, y: cmp(y, x))
        return more

    def getPixmap(self, node):
        """ getPixmap(node) -> returns an appropriate pixmap for a node

        """
        node_type_name = node.__class__.__name__
        pxm = util.loadIcon(nodewidgets.DefaultNode.iconName)

        if isinstance(node, (tuple, list, )):
            pxm = util.loadIcon(nodewidgets.SequenceNode.iconName)
        elif isinstance(node, (dict, )):
            pxm = util.loadIcon(nodewidgets.MappingNode.iconName)

        some_node_class = getattr(nodewidgets, '%sNode' % node_type_name, None)
        some_icon_name = getattr(some_node_class, 'iconName', None)

        if node_type_name == 'TechnicalTicker':
            ticker_pxm = util.loadIcon(node.symbol.lower())
            if not ticker_pxm.isNull():
                pxm = ticker_pxm
        elif some_icon_name is not None:
            pxm  = util.loadIcon(some_icon_name)
        return pxm


class TreeViewItem(qt.QListViewItem):
    """ TreeViewItem(parent, node) -> a QListViewItem for session nodes

    """
    format = TreeItemFormat()

    def __init__(self, parent, node, label):
        qt.QListViewItem.__init__(self, parent, label)

        self.node = node
        self.nodes = []

        if self.format.hasNodes(node):
            self.setExpandable(1)

        pixmap = self.format.getPixmap(node)
        if pixmap:
            self.setPixmap(0, pixmap)

    def setOpen(self, which):
        """ setOpen() -> add or remove TreeViewItems to the list view

        """
        if which:
            for label, subnode in self.format.getNodes(self.node):
                newnode = TreeViewItem(self, subnode, label)
                if isinstance(subnode, (str, unicode, float, int, )):
                    newnode.setText(1, str(subnode))
                self.nodes.append(newnode)
        else:
            for node in self.nodes:
                self.takeItem(node)
            self.nodes = []
        qt.QListViewItem.setOpen(self, which)


class SessionListView(qt.QListView):
    """ SessionListView(parent) -> a QListView for displaying an session

    """
    def __init__(self, parent):
        qt.QListView.__init__(self, parent)
        self.setRootIsDecorated(1)
        self.setSorting(-1)
        self.addColumn(kdecore.i18n('Name'))
        self.addColumn(kdecore.i18n('Value'))
        self.setColumnAlignment(1, qt.Qt.AlignRight)
        self.setColumnWidth(0, 100)
        self.setAllColumnsShowFocus(True)
        self.actions = actions = kdeui.KActionCollection(self)

        self.viewItemAction = \
            util.buildAction('view_item', 'View', 'viewmag', '', 
                            'View this item', actions)
        self.viewSourceAction = \
            util.buildAction('view_source', 'View Source', 'source_py', '',
                            'View item source code', actions)
        self.separateAction = kdeui.KActionSeparator()
        self.saveAction = \
            util.buildAction('save_item', 'Save', 'filesave', '', 
                            'Save item', actions)

        self.popMenu = pop = qt.QPopupMenu(self)
        self.viewItemAction.plug(pop)
        self.viewSourceAction.plug(pop)
        self.separateAction.plug(pop)
        self.saveAction.plug(pop)

        sigAct = util.sigActivated
        self.connect(self, util.sigListContext, self.contextMenu)
        self.connect(self.viewItemAction, sigAct, self.viewItem)
        self.connect(self.viewSourceAction, sigAct, self.viewItemNodeSource)
        self.connect(self.saveAction, sigAct, self.saveItemNode)

    def setSession(self, session):
        """ setSession(session) -> clear the list and add the root item

        """
        self.clear()
        TreeViewItem(self, session, label='session')

    def contextMenu(self, item, pos, col):
        """ contextMenu(...) -> display a node-specific context menu

        """
        if item:
            self.context = item
            try:
                sourcefile = inspect.getsourcefile(item.node.__class__)
            except (TypeError, ):
                sourcefile = False
                col = col
            self.viewSourceAction.setEnabled(not not sourcefile)
            self.popMenu.popup(pos)
        else:
            self.context = None

    def viewItem(self):
        """ viewItem() -> emit a signal to view an item

        """
        self.emit(util.sigDoubleClicked, (self.context, ))

    def viewItemNodeSource(self):
        """ viewItemNodeSource() -> emit a signal to view the source of a node

        """
        args = (util.SourceCodeRequest(self.context.node), )
        self.emit(util.sigViewSource, args)

    def saveItemNode(self):
        """ saveItemNode() -> save an items node to a file

        """
        dlg = kfile.KFileDialog('', '*', None, 'Save As', True)
        if dlg.exec_loop() == kfile.KFileDialog.Accepted:
            filename = '%s' % dlg.selectedFile()
        else:
            return

        try:
            tools.save_object(self.context.node, filename)
        except (Exception, ), ex:
            util.displayException(self, 'Error saving item', ex)

    def readItemNode(self):
        """ readItemNode() -> read a pickle into the items node object

        """
        filename = kfile.KFileDialog.getOpenFileName('', '*', self)
        filename = str(filename)
        if not filename:
            return

        item = self.context
        itemkey = str(item.text(0))
        parent = item.parent()
        if not parent:
            return

        parentnodey = parent.node
        if hasattr(parentnodey, itemkey):
            ## the parent node has the context label as an attribute
            ## open and load the file onto that
            try:
                graft_node = tools.load_object(filename)
            except (Exception, ), ex:
                #self.displayException('Error opening item', ex)
                util.displayException(self, 'Error opening item', ex)
                return
            else:
                setattr(parentnodey, itemkey, graft_node)
                parent.setOpen(False)
        elif isinstance(item, (tuple, list, )):
            util.displayException(self, 'Cannot read file into this item', '')
        else:
            try:
                parentnodey[itemkey] = tools.load_object(filename)
            except (Exception, ), ex:
                util.displayException(self, 'Error opening item', ex)
            else:
                parent.setOpen(False)

    def contentsMouseDoubleClickEvent(self, event):
        """

            This probably breaks some kde/qt ui standard because the list view
            items are *not* expanded.  I just can't stand this list opening its
            items on a double click, so the event is sunk here and a signal is
            emitted just the same.
        """
        event.ignore()
        self.emit(util.sigDoubleClicked, (self.selectedItem(), ))
