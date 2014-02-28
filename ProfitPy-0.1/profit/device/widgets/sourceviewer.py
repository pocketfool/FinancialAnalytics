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
""" Read-only source code viewer widget

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'sourceviewer.py,v 0.4 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.4',
}

import inspect

import qt
import qtext

import profit.device.util as util


class SourceCodeRequestNode(qtext.QextScintilla):
    """SourceCodeRequestNode(...) -> source code viewer widget

    """
    def __init__(self, parent, node): #, flags=0):
        # flags = flags | Qt.WDestructiveClose
        qtext.QextScintilla.__init__(self, parent) 
        self.lexer = SourceBrowserLexer(self)
        self.setLexer(self.lexer)
        self.setIndentationGuides(True)
        self.setWhitespaceVisibility(1)
        self.setMarginsFont(qt.QFont('fixed'))
        self.setMarginLineNumbers(0, 1)
        self.setFolding(qtext.QextScintilla.BoxedTreeFoldStyle)
        self.setMarginWidth(0, "abcd")

        self.setReadOnly(False)
        node = node.item
        try:
            txt_lines,  lineno = inspect.findsource(node.__class__)
            txt = str.join('', txt_lines)
        except (IOError, TypeError):
            txt = 'Unable to get source.'
            lineno = 0
        self.setText(txt)
        self.setCursorPosition(lineno, 0)
        self.ensureLineVisible(lineno)
        self.setReadOnly(True)


class SourceBrowserLexer(qtext.QextScintillaLexerPython):
    """SourceBrowserLexer(...) -> lexer for the code browser

    """
    def __init__(self, parent=None, name=None):
        qtext.QextScintillaLexerPython.__init__(self, parent, name)

    def font(self, style):
        """font(style) -> the qt font to display for the indicated style

        """
        font = util.appConfig('Fonts').readFontEntry('code', qt.QFont('fixed'))
        if style in (5, 8, 9): # (Keyword, ClassName, FunctionMethodName,)
            font.setBold(True)
        return font
