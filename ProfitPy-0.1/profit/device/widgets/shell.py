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
""" an interactive shell control

Based on PyCute, Copyright (c) 2003 Gerard Vermeulen
Based on Eric3, Copyright (c) 2003 - 2004 Detlev Offenbach <detlev@die-offenbachs.de>


"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'shell.py,v 0.7 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.7',
}

import cgitb
import os
import sys
import code
import traceback


import qt
import kdecore
import kdeui
import profit.lib.base as base
import profit.device.util as util


class InteractiveShell(kdeui.KTextEdit):
    """InteractiveShell(parent=None) -> python shell widget

    """
    eofPrompt = 'Use Alt-F4 (i.e. Close Window) to exit.'
    historyName = '~/.profitdevice/shellhistory'
    startScriptName = '~/.profitdevice/autostart.py'
    maxHistory = 200
    introText = (
        'Python %s on %s\n' % (sys.version, sys.platform),
        'Type "copyright", "credits" or "license" for more information on Python.\n',
    )

    def __init__(self, parent=None):
        kdeui.KTextEdit.__init__(self, parent)
        self.setupWidget()
        self.setupInterp()
        self.setupSys()
        self.setupHistory()
        self.setupMenu()

    def setupInterp(self):
        self.line = qt.QString()
        self.lines = []
        self.history = []
        self.reading = self.more = self.pointer = 0
        self.point = self.xlast = self.ylast = 0

        self.interpreter = interp = code.InteractiveInterpreter()
        interplocals = interp.locals
        interplocals['shell'] = self
        interplocals['quit'] = interplocals['exit'] = self.eofPrompt

    def setupWidget(self):
        util.setShellFont(self)
        self.setWrapPolicy(qt.QTextEdit.Anywhere)
        self.setCaption('Python Shell')
        self.setUndoRedoEnabled(False) ## big performance hit otherwise

    def setupSys(self):
        base.stdtee(self, 'stdout')
        try:
            throwaway = sys.ps1
            throwaway = sys.ps2
        except (AttributeError, ):
            sys.ps1 = '>>> '
            sys.ps2 = '... '
        self.writeBanner()

    def writeBanner(self):
        self.setText('')
        self.write(str.join('', self.introText + (sys.ps1, )))

    def setupHistory(self):
        ## add in the lines from the history file or make the file if absent
        self.historyName = historyName = os.path.expanduser(self.historyName)
        if os.path.exists(historyName):
            histfile = open(historyName, 'r')
            lines = [line for line in histfile.readlines() if line.strip()]
            self.history += [qt.QString(line) for line in lines]
            histfile.close()
        else:
            try:
                histfile = open(historyName, 'w')
                histfile.close()
            except (IOError, ):
                pass
        util.connectLastClosed(self, self.writeShellHistory)

    def setupMenu(self):
        self.menu = qt.QPopupMenu(self)
        self.menu.insertItem('Copy', self.copy)
        self.menu.insertItem('Paste', self.paste)
        self.menu.insertSeparator()
        self.menu.insertItem('Clear', self.clear)

    def writeShellHistory(self):
        try:
            history = ['%s' % (hl, ) for hl in self.history[-self.maxHistory:]]
            history = [hl.strip() for hl in history if hl.strip()]
            history = ['%s\n' % (hl, ) for hl in history if hl]

            histfile = open(self.historyName, 'w')
            histfile.writelines(history)
            histfile.close()

        except (Exception, ), ex:
            pass
            #sys.__stdout__.write('%s\n' % (ex, ))

    def write(self, text):
        if not str(text).strip():
            return
        self.append(text)
        self.moveCursor(qt.QTextEdit.MoveEnd, 0)
        self.ylast, self.xlast = self.getCursorPosition()
        self.update()

    def run(self):
        self.pointer = 0
        linestr = str(self.line)
        if linestr:
            self.history.append(qt.QString(linestr))
        self.lines.append(linestr)
        source = str.join('\n', self.lines)
        try:
            self.more = self.interpreter.runsource(source)
        except (SystemExit, ):
            print Exception('SystemExit attempted but not allowed')
            self.more = None
        if self.more:
            self.write(sys.ps2)
        else:
            self.write(sys.ps1)
            self.lines = []
        self.clearLine()

    def clearLine(self):
        self.line.truncate(0)
        self.point = 0

    def insertText(self, text):
        cursy, cursx = self.getCursorPosition()
        self.insertAt(text, cursy, cursx)
        self.line.insert(self.point, text)
        self.point += text.length()
        self.setCursorPosition(cursy, (cursx + text.length()))

    def keyPressEvent(self, e):
        text, key, ascii, state = e.text(), e.key(), e.ascii(), e.state()
        if (text.length() and ((ascii >= 32) and (ascii < 127))) or (key == qt.Qt.Key_Tab):
            self.insertText(text)
            return 

        if (state & qt.Qt.ControlButton):
            if key == qt.Qt.Key_L:
                self.clear()
            elif key == qt.Qt.Key_C:
                self.copy()
            elif key == qt.Qt.Key_V:
                self.paste()
            elif key == qt.Qt.Key_D:
                self.write("%s" % self.eofPrompt)
                self.run()
            elif key == qt.Qt.Key_A:
                self.setCursorPosition(self.ylast, self.xlast)
                self.point = 0
            elif key == qt.Qt.Key_E:
                self.moveCursor(qt.QTextEdit.MoveLineEnd, 0)
                self.point = self.line.length()

        if (state & qt.Qt.ControlButton) or (state & qt.Qt.ShiftButton):
            e.ignore()
            return 

        if (key == qt.Qt.Key_Backspace):
            if self.point:
                self.doKeyboardAction(qt.QTextEdit.ActionBackspace)
                self.point -= 1
                self.line.remove(self.point, 1)

        elif (key == qt.Qt.Key_Delete):
            self.doKeyboardAction(qt.QTextEdit.ActionDelete)
            self.line.remove(self.point, 1)

        elif (key == qt.Qt.Key_Return) or (key == qt.Qt.Key_Enter):
            if self.reading:
                self.reading = 0
            else:
                self.run()

        elif (key == qt.Qt.Key_Left):
            if self.point:
                self.moveCursor(qt.QTextEdit.MoveBackward, 0)
                self.point -= 1

        elif (key == qt.Qt.Key_Right):
            if (self.point < self.line.length()):
                self.moveCursor(qt.QTextEdit.MoveForward, 0)
                self.point += 1

        elif (key == qt.Qt.Key_Home):
            self.setCursorPosition(self.ylast, self.xlast)
            self.point = 0

        elif (key == qt.Qt.Key_End):
            self.moveCursor(qt.QTextEdit.MoveLineEnd, 0)
            self.point = self.line.length()

        elif (key == qt.Qt.Key_Up):
            if len(self.history):
                if (self.pointer == 0):
                    self.pointer = len(self.history)
                self.pointer -= 1
                self.recall()
        elif (key == qt.Qt.Key_Down):
            if len(self.history):
                self.pointer += 1
                if (self.pointer == len(self.history)):
                    self.pointer = 0
                self.recall()
        else:
            e.ignore()

    def recall(self):
        self.setCursorPosition(self.ylast, self.xlast)
        self.setSelection(self.ylast, self.xlast, 
                          self.ylast, self.paragraphLength(self.ylast))
        self.removeSelectedText()
        self.clearLine()
        self.insertText(self.history[self.pointer])

    def focusNextPrevChild(self, next):
        if next and self.more:
            return 0
        return qt.QTextEdit.focusNextPrevChild(self, next)

    def mousePressEvent(self, event):
        if event.button() == qt.Qt.LeftButton:
            self.moveCursor(qt.QTextEdit.MoveEnd, 0)

    def clear(self):
        self.setText('')
        self.run()

    def paste(self):
        pasted = qt.qApp.clipboard().text()
        if not pasted.isNull():
            self.insertText(pasted)

    def contentsContextMenuEvent(self, event):
        """
        """
        self.menu.popup(event.globalPos())
        event.accept()



##
## these methods are for the main gui client
##
    def sessionToNamespace(self, session):
        shelld = self.interpreter.locals

        shelld['device'] = self.topLevelWidget()
        shelld['session'] = session
        shelld.update(session)
        for ((tid, tsym,), tobj,) in session.tickers.items():
            shelld[tsym] = tobj

    def onGuiComplete(self):
        """ onGuiComplete() -> a callback (not a slot) for startup-complete-ness

        """
        try:
            self.startScriptName = os.path.expanduser(self.startScriptName)
            startScriptName = file(self.startScriptName, 'r')
        except (IOError, ), ex:
            pass
        else:
            try:
                for line in startScriptName.readlines():
                    self.interpreter.runsource(line)
            except (SyntaxError, ValueError , OverflowError), ex: 
                print 'Compiling code in startup script failed: %s' % (ex, )
            except (Exception ,), ex:
                print 'Startup script failure (non-compile): %s' % (ex, )

    def configChanged(self, config):
        config.setGroup(util.groups.fonts)
        font = config.readFontEntry('shell', qt.QFont('fixed'))
        self.setFont(font)


    def close(self):
        base.stdnotee(self, 'stderr', 'stdout')

if __name__ == '__main__':
    import profit.device.about as about
    window, application = util.kMain(InteractiveShell, 
                                    'Interactive Python Shell', 
                                    about=about.aboutData)
    window.show()
    application.exec_loop()
