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


"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'nodebase.py,v 0.3 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.3',
}

import qt


alignCenter = qt.Qt.AlignCenter
alignLeft = qt.Qt.AlignLeft
alignRight = qt.Qt.AlignRight


def shortStr(item, limit=100):
    """shortStr(item, max_len) -> returns string not longer than max_len

    """
    item = str(item)
    if len(item) > limit:
        return '%s...' % (item[0:limit-3], )
    else:
        return item


class BaseNodeWidget(qt.QWidget):
    """BaseNodeWidget() -> base widget with broker behavior

    """
    def __init__(self, parent, node):
        qt.QWidget.__init__(self, parent)
        self.node = node


class BaseNodeSplitter(qt.QSplitter):
    """BaseNodeSplitter() -> base splitter with broker behavior

    """
    def __init__(self, parent):
        qt.QSplitter.__init__(self, parent)


class BaseNodeTabWidget(qt.QTabWidget):
    """BaseNodeTabWidget() -> base tab widget with broker behavior

    """
    def __init__(self, parent):
        qt.QTabWidget.__init__(self, parent)


class BaseNodeListView(qt.QListView):
    """BaseNodeListView(parent, node) -> simplified list view widget

    """
    ## sequence of (name, width, alignment) values
    columnDefs = ()

    ## set to true value for selecting an entire row at a time
    focusAllColumns = False

    ## set to (-1, ) to disable sorting
    ## or to (col, direction) for specific column sorting
    sorting = False

    def __init__(self, parent, node):
        qt.QListView.__init__(self, parent)
        self.node = node

        for coldef in self.columnDefs:
            colidx = self.addColumn(coldef[0], coldef[1])
            self.setColumnAlignment(colidx, coldef[2])

        if getattr(self, 'focusAllColumns', None):
            self.setAllColumnsShowFocus(self.focusAllColumns)

        if getattr(self, 'sorting', None):
            self.setSorting(*self.sorting)

        if getattr(self, 'defaultSelectionMode', None):
            self.setSelectionMode(self.defaultSelectionMode)

    def items(self):
        """ items() -> generates a sequence of list view items

        """
        it = qt.QListViewItemIterator(self)
        current = it.current()
        while current:
            yield current
            current = it.current()
            it += 1


class MappingNode(BaseNodeListView):
    """MappingNode(parent, node) -> displays a mapping node as a list view

    """
    iconName = 'view_choose'
    columnDefs = (
        ('Key', -1, alignLeft,),
        ('Value', -1, alignRight,),
    )

    def __init__(self, parent, node):
        BaseNodeListView.__init__(self, parent, node)
        self.refreshNode()

    def refreshNode(self):
        """refreshNode() -> update list view contents from node subject

        """
        self.clear()
        for k, v in self.node.items():
            qt.QListViewItem(self, shortStr(k), shortStr(v))


class SequenceNode(BaseNodeListView):
    """SequenceNode(parent, node) -> displays a sequence node as a list view

    """
    iconName = 'list'
    sorting = (-1, )
    columnDefs = (
        ('Index', -1, alignLeft,),
        ('Value', -1, alignRight,),
    )

    def __init__(self, parent, node):
        BaseNodeListView.__init__(self, parent, node)
        self.refreshNode()

    def refreshNode(self):
        """refreshNode() -> update list view contents from node subject

        """
        self.clear()
        for idx, val in enumerate(self.node):
            qt.QListViewItem(self, shortStr(idx), shortStr(val))
