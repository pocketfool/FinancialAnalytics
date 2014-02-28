#!/usr/bin/env python
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
"""CollectorApp.py -> PyQt dialog to coordinate data collection sub-apps.

This is the script that runs via cron to collect ticker data from IB TWS.

Usage:

    python collector_app.py my_tws_script my_gui_helper my_sub_collector

This script creates a PyQt dialog that manages multiple child processes.  It 
creates and starts them, and interleaves their output.  When the last
child process is finished, the interleaved output is written to stdout (for 
cron to pick up) and the dialog exits.

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:26',
    'file' : 'collector_app.py,v 0.4 2004/09/11 09:20:26 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.4',
}

import sys
import time

import qt

import profit.lib.base as base


class StdOutTextEdit(qt.QTextEdit):
    """ StdOutTextEdit(...) -> simple stdout wrapper

    """
    def write(self, text):
        """ write(text) -> makes a text edit widget writable

        """
        self.append(text)
        self.moveCursor(qt.QTextEdit.MoveEnd, 0)
        self.y_last, self.x_last = self.getCursorPosition()


class DataCollectorMainForm(qt.QDialog):
    """ DataCollectorMainForm(...) -> main data collector parent process dialog

    """
    log_format = '%s: %s: %s\n'
    title = 'Profit Data Collector'
    
    def __init__(self, parent, apps):
        qt.QDialog.__init__(self, parent, self.title, 0, 0)
        self.setName('DataCollectorMain')
        self.allLogs = []

        mainLayout = qt.QVBoxLayout(self, 6, 6, 'mainLayout')
        self.processTabs = qt.QTabWidget(self, 'processTabs')
        self.setupChildApps(apps)
        mainLayout.addWidget(self.processTabs)

        buttonsLayout = qt.QHBoxLayout(None, 0, 6, 'buttonsLayout')
        spacer = qt.QSpacerItem(20, 20, qt.QSizePolicy.Expanding, 
                                qt.QSizePolicy.Minimum)
        buttonsLayout.addItem(spacer)

        self.buttonStop = qt.QPushButton(self, 'buttonStop')
        buttonsLayout.addWidget(self.buttonStop)
        self.buttonClose = qt.QPushButton(self,'buttonClose')
        buttonsLayout.addWidget(self.buttonClose)
        mainLayout.addLayout(buttonsLayout)

        self.setupSignals()
        self.setupMisc()
        self.emit(qt.PYSIGNAL('RunChildApps'), ())

    def setupSignals(self):
        """ setupSignals() -> connect some things

        """
        self.connect(self, qt.PYSIGNAL('RunChildApps'), self.runChildApps)
        self.connect(self.buttonStop, qt.SIGNAL('clicked()'), 
                     self, qt.SLOT('exec()'))
        self.connect(self.buttonClose, qt.SIGNAL('clicked()'), 
                     self, qt.SLOT('close()'))

    def setupMisc(self):
        """ setupMisc() -> an bad doc string is worse than no doc string

        """
        self.setCaption(self.title)
        self.buttonStop.setText('&Stop')
        self.buttonStop.setAccel(qt.QString('Alt+S'))
        self.buttonClose.setText('&Close')
        self.buttonClose.setAccel(qt.QString('Alt+C'))
        self.resize(qt.QSize(640, 400).expandedTo(self.minimumSizeHint()))
        self.clearWState(qt.Qt.WState_Polished)

    def runChildApps(self):
        """ runChildApps() -> run the child processes

        """
        for name, textedit, proc in self.child_apps:
            start_return = proc.start()
            print >> sys.__stdout__, name, textedit, start_return

            if start_return:
                args = qt.PYSIGNAL('ChildStartOkay'), (name, textedit, proc, )
            else:
                args = qt.PYSIGNAL('ChildStartFail'), (start_return, )
            self.emit(*args)

    def setupChildApps(self, seq):
        """ setupChildApps() -> make child processes from their definitions

        """
        self.child_apps = child_apps = []
        self.child_partials = child_partials = {}

        for child_def in seq:
            title, command = child_def[0:2]
            name = title.strip()

            page = qt.QWidget(self.processTabs, name+'Page')
            layout = qt.QHBoxLayout(page, 4, 4, name+'Layout')
            textedit = StdOutTextEdit(page, name+'TextEdit')
            layout.addWidget(textedit)
            self.processTabs.insertTab(page, title)

            process = qt.QProcess()
            process.title = title
            for arg in str(command).split():
                process.addArgument(arg)

            stdout_call = \
                base.PartialCall(self.handleReadyStdout, 
                                 process=process, textwidget=textedit)
            exit_call = \
                base.PartialCall(self.handleChildExit, 
                                 process=process, textwidget=textedit)
            child_partials[name] = (stdout_call, exit_call)

            self.connect(process, qt.SIGNAL('readyReadStdout()'), stdout_call)
            self.connect(process, qt.SIGNAL('processExited()'), exit_call)
            child_apps.append((name, textedit, process))

    def timeStamp(self):
        """ timeStamp() -> waste of a function

        """
        return str.join(' ', time.ctime().split()[1:4])

    def handleReadyStdout(self, process, textwidget):
        """ handleReadyStdout(...) -> write process stdout to text widget

        """
        while process.canReadLineStdout():
            args = (self.timeStamp(), process.title, process.readLineStdout())
            log = self.log_format % args
            textwidget.write(log)
            self.allLogs.append(log)

    def handleChildExit(self, process, textwidget):
        """ handleChildExit(...) -> log the process stdout, shuts down if last

        """
        self.handleReadyStdout(process, textwidget)
        args = (self.timeStamp(), process.title, 
                'exited with status %s' % process.exitStatus())
        log = self.log_format % args
        textwidget.write(log)
        self.allLogs.append(log)

        exits = [child[2].isRunning() for child in self.child_apps]
        if not sum(exits):
            self.close()

    def closeEvent(self, event):
        """ closeEvent(event) -> write log entries to stdout and accept

        """
        for line in self.allLogs:
            print line[:-1]
        event.accept()


if __name__ == '__main__':
    try:
        scripts = tws, helper, collector = sys.argv[1:4]
        scripts = zip(('Ib Tws', 'Gui Helper', 'Collector'), scripts)
    except (ValueError, ):
        print 'Usage: %s tws_cmd helper_cmd collector_cmd' % (__file__, )
        sys.exit(1)

    app = qt.QApplication([])
    win = DataCollectorMainForm(parent=None, apps=scripts)
    app.connect(app, qt.SIGNAL('lastWindowClosed()'), app, qt.SLOT('quit()'))
    app.setMainWidget(win)

    win.show()
    app.exec_loop()
