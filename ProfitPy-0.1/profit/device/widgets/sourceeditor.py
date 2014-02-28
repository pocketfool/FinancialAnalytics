#!/usr/bin/env python
##~
##~ Copyright 2004 Troy Melhase <troy@gci.net>
##~ Copyright (c) 2003 - 2004 Detlev Offenbach <detlev@die-offenbachs.de>
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
##~ To get more information about eric3 please see the
##~ <a href="http://www.die-offenbachs.de/detlev/eric3.html">eric3 web site</a>.
##~
""" Read-write python source widget, courtesy of the eric3 IDE.

The Editor.Editor class in the eric3 package reads in the user's preferences,
and the subclasses here are no exception.  The debug client and server is 
currently broken.
"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'sourceeditor.py,v 0.4 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.4',
}

import inspect
import os
import sys

import qt

import kdeui

import profit.device.util as util

## import the eric3 module without catching an import error.  this means the
## client of this module must catch the ImportError exception when trying to
## import this module.
import eric3

## after the top-level eric3 package is imported, jimmy the sys.path so that
## the imports in the eric3 package will work.
##
## note that the other eric3 modules cannot be imported here because some 
## require a QApplication instance.
eric3Dir = os.path.split(eric3.__file__)[0]
sys.path.append(eric3Dir)

## some additional eric3 bits that are safe to bring in when this module is
## imported.  note that the PixmapCache should only be available in eric3
## versions 3.4 or newer.
from eric3.UI import PixmapCache, Info

class MockDebugger(object):
    """ MockDebugger() -> fake debugger

        Importing and using the eric3 debug server is currently not 
        working/kinda broken.  This is a quick+temp fix.
    """

    def remoteBreakpoint(self, *args):
        """

        """

    def remoteBreakpointEnable(self, *args):
        """

        """

    def remoteBreakpointIgnore(self, *args):
        """

        """


class SimpleEditor(qt.QFrame):
    """ SimpleEditor(parent) -> a quick hack to re-use the eric3 Editor class


    """
    def __init__(self, parent=None):
        qt.QFrame.__init__(self, parent)
        qt.QVBoxLayout(self, 0, 3)
        
    def setupEditor(self, filename):
        """ setupEditor(filename) -> create the editors widgets

        """
        from eric3.QScintilla import Editor
        from eric3.Project import Project

        ## older versions
        try:
            from eric3.eric3 import initializeMimeSourceFactory
        except (ImportError, ):
            pass
        else:
            initializeMimeSourceFactory(eric3Dir)

        ## recent versions (around snapshot 20040818) 
        try:
            from eric3.Utilities import Startup
        except (ImportError, ):
            pass
        else:
            Startup.initializeMimeSourceFactory(eric3Dir)

        self.layout().setAutoAdd(True)
        self.project = Project.Project()
        self.editorActGrp = qt.QWidget(self)
        self.editor = Editor.Editor(MockDebugger(), filename, parent=self)

        menu = self.editor.menu
        for i in [menu.idAt(i) for i in range(menu.count())]:
            if menu.text(i) == 'Close':
                menu.setItemEnabled(i, False)
        menu.insertSeparator()
        menu.insertItem(qt.QIconSet(PixmapCache.getPixmap('eric')), 
                        'About %s' % (Info.Program, ),
                        self.aboutEditor)

    def aboutEditor(self):
        """ aboutEditor() -> displays a dialog with information about the editor

            This code was copied from the eric3 UI.UserInterface module.  It
            could be imported like the other eric3 modules, but the cost of that
            is too high for my liking.
        """
        qt.QMessageBox.about(self, Info.Program, self.trUtf8(
            """<h3> About %1</h3>"""
            """<p>%1 is an Integrated Development Environment for the Python"""
            """ programming language. It is written using the PyQt Python bindings for"""
            """ the Qt GUI toolutil and the QScintilla editor widget.</p>"""
            """<p>This version is %2.</p>"""
            """<p>For more information see"""
            """ <tt>http://www.die-offenbachs.de/detlev/eric3.html</tt>.</p>"""
            """<p>Please send bug reports or feature wishes to"""
            """ <tt>eric-bugs@die-offenbachs.de</tt>.</p>"""
            """<p>%3</p>"""
            """<p>%4 uses third party software which is copyrighted"""
            """ by its respective copyright holder. For details see"""
            """ the copyright notice of the individual package.</p>"""
            )
            .arg(Info.Program)
            .arg(Info.Program)
            .arg(Info.Version)
            .arg(Info.Copyright)
            .arg(Info.Program)
        )


    def getProject(self, *args):
        """ getProject(*args)


        """
        return self.project

    def addToRecentList(self, *args):
        """ addToRecentList(*args)

        """

    def getAPIs(self, name):
        """ getAPIs(name)

        """

    def setEditorName(self, *args):
        """ setEditorName(*args)

        """

    def editorsCheckFocusInEnabled(self):
        """ editorsCheckFocusInEnabled()

        """

    def closeEditor(self, *args):
        """ closeEditor(*args) -> need to remove/disable the popup "Close" item

        """


class SourceCodeRequestNode(SimpleEditor):
    """SourceCodeRequestNode(...) -> source code edit request

    """
    iconName = 'source_py'
    captions = {0 : '%s', 1 : '%s *', }

    def __init__(self, parent, node):
        SimpleEditor.__init__(self, parent)

        try:
            source_file = inspect.getsourcefile(node.item.__class__)
            self.setupEditor(source_file)
            self.file_name = os.path.split(source_file)[-1]
        except (TypeError, ):
            pass
        else:
            mod_status_sig = qt.PYSIGNAL('modificationStatusChanged')
            self.connect(self.editor, mod_status_sig, self.updateTabLabel)

    def updateTabLabel(self, data):
        try:
            dock = util.getDockWidget(self.parent())
        except (AttributeError, ):
            return

        caption = self.captions[data] % (self.file_name, )
        ## only both will make the change visible ??
        dock.setTabPageLabel(caption)
        dock.setCaption(caption)


if __name__ == '__main__':
    """ When run from the command line, this pops up the SimpleEditor window
        with the source of this script.

    """
    import profit.device.about as about
    win, app = util.kMain(SimpleEditor, 
                        'Editor Test', 
                         about=about.aboutData)
    try:
        filename = sys.argv[0]
    except (IndexError, ):
        filename = __file__
    win.setupEditor(filename)

    win.show()
    app.exec_loop()
