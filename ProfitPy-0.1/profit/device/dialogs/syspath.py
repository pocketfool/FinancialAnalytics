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

This module defines a widget for browsing sys.path.  

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'syspath.py,v 0.4 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.4',
}

import os
import pyclbr
import sys

import qt
import kdecore
import kdeui

import profit.device.util as util

i18n = kdecore.i18n
KDialogBase = kdeui.KDialogBase


## .so and .zip not supported
sourceExts = ('.py', '.pyc', '.pyo', )


class CallableViewItem(qt.QListViewItem):
    """ CallableViewItem() -> a list item to represent a callable in a module

    Because it's too confusing to display methods of classes, and because in 
    most cases only the class __init__ method is needed, we disable the 
    construction and addition of view items for methods.  Set the attribute
    includeMethods to a true value to enable browsing of class methods.
    """
    icons = {
        pyclbr.Class : 'blockdevice',
        pyclbr.Function : 'exec',
        'method' : 'network',
    }

    includeMethods = False 

    def __init__(self, parent, name, descriptor):
        qt.QListViewItem.__init__(self, parent)
        self.setText(0, name)
        
        iconame = self.icons.get(descriptor, None) or \
                  self.icons.get(descriptor.__class__, None)
        if iconame:
            self.setPixmap(0, util.loadIcon(iconame))

        try:
            methods = descriptor.methods
        except (AttributeError, ):
            pass
        else:
            if self.includeMethods:
                for name in methods:
                    CallableViewItem(self, name, 'method')


class ImportableViewItem(qt.QListViewItem):
    """ ImportableViewItem(...) -> a list item to represent a package or module

    """
    def __init__(self, parent, name, label, full=False):
        qt.QListViewItem.__init__(self, parent)
        self.icons = dict([(ext, 'source_py') for ext in sourceExts])
        self.setText(0, label)

        self.name = name
        try:
            self.name = name = os.path.join(parent.name, name)
        except (AttributeError, ):
            pass
        
        ico = self.iconForPath(name)
        if ico:
            self.setPixmap(0, ico)

        self.isDir = isdir = os.path.isdir(name) 
        self.isSrc = issrc = (os.path.splitext(name)[-1] in sourceExts)

        if isdir:
            paths = [os.path.join(name, pth) for pth in os.listdir(name)]
            if [pth for pth in paths if self.pathContentFilter(pth)]:
                self.setExpandable(True)
        elif issrc:
            pathname, filename = os.path.split(name)
            filename = os.path.splitext(filename)[0]
            try:
                readmodule = pyclbr.readmodule_ex
                self.pyitems = items = readmodule(filename, [pathname, ])
                if items:
                    self.setExpandable(True)
            except (ImportError, ):
                pass

    def setOpen(self, which):
        """ setOpen(which) -> add or remove items

        """
        if which:
            if self.isSrc:
                items = self.pyitems.items()
                items = [(name, desc) 
                            for name, desc in items 
                                if not name.startswith('_')]
                items.sort()
                items.reverse()
                for name, desc in items:
                    CallableViewItem(self, name, desc)
            else:
                name = self.name
                paths = [os.path.join(name, pth) for pth in os.listdir(name)]
                paths = [pth for pth in paths if self.pathContentFilter(pth)]
                paths.sort()
                paths.reverse()
                for path in paths:
                    ImportableViewItem(self, path, os.path.basename(path))
        qt.QListViewItem.setOpen(self, which)

    def iconForPath(self, item):
        """ iconForPath(item) -> returns an icon appropriate to the item
    
        """
        if os.path.isdir(item):
            return util.loadIcon('folder')
    
        name = self.icons.get(os.path.splitext(item)[-1], None)
        if name:
            return util.loadIcon(name)

    def pathContentFilter(item, exts=sourceExts):
        """ pathContentFilter(item) -> true if item is a package, module, or source
    
        """
        isdir = os.path.isdir(item) 
        ispkg = isdir and ('__init__.py' in os.listdir(item))
        issrc = os.path.splitext(item)[-1] in exts
        return (ispkg) or (issrc)
    pathContentFilter = staticmethod(pathContentFilter)


class SysPathView(qt.QListView):
    """ SysPathView() ->

    """
    def __init__(self, parent=None):
        qt.QListView.__init__(self, parent)
        self.addColumn(i18n('Name'))
        self.setRootIsDecorated(1)
        self.setSorting(-1)
        self.setAllColumnsShowFocus(True)

        for path in [pth for pth in sys.path if self.pathContentFilter(pth)]:
            ImportableViewItem(self, path, path)

    def pathContentFilter(item, exts=sourceExts):
        """ pathContentFilter(item) -> true if item is a package, module, or source
    
        """
        isdir = os.path.isdir(item) 
        isnotempty = (isdir and os.listdir(item))
        if isnotempty:
            items = [os.path.join(item, pth) for pth in os.listdir(item)]
            items = [pth for pth in items 
                         if os.path.isdir(pth) or 
                            os.path.splitext(pth)[-1] in exts]
            return not not items

    pathContentFilter = staticmethod(pathContentFilter)


class SysPathDialog(KDialogBase):
    """ SysPathDialog(...) -> a dialog type to display the sys.path browser

    """
    def __init__(self, parent=None):
        buttonsmask = KDialogBase.Ok | KDialogBase.Cancel
        title = 'Select Callable in Python sys.path'
        KDialogBase.__init__(self, KDialogBase.Swallow, i18n(title),
                            buttonsmask, KDialogBase.Ok, parent, title, 
                            True, False)

        self.view = view = SysPathView(self)
        self.setMainWidget(view)
        self.connect(view, util.sigSelectChanged, self.selectPath)
        self.resize(400, 500)
        self.path = []

    def selectPath(self):
        """ selectPath() -> tracks item selection to path construction 

        """
        path = []
        item = self.view.selectedItem()
        while item:
            txt = '%s' % (item.text(0), )
            name, ext = os.path.splitext(txt)
            if ext in sourceExts:
                txt = name
            path.append(txt)
            item = item.parent()
        path.reverse()
        self.path = path[1:]

    def printPath(self):
        """ printPath() -> simple pprint

        """
        import pprint
        pprint.pprint(self.path, sys.__stdout__)


if __name__ == '__main__':
    import profit.device.about as about
    win, app = util.kMain(SysPathDialog, 'sys.path Browser Test',
                          about=about.aboutData)
    win.show()
    win.connect(win.view, util.sigSelectChanged, win.printPath)
    app.exec_loop()
