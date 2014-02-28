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
""" library bits

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'util.py,v 0.4 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.4',
}

import inspect
import os
import re
import sys

import qt

import kdecore
import kdeui

import profit.lib.base as base


PYSIGNAL = qt.PYSIGNAL
SIGNAL = qt.SIGNAL
SLOT = qt.SLOT

sigNewSession = PYSIGNAL('new session')
sigBrowserWriteDone = PYSIGNAL('browser write done')
sigConfigChanged = PYSIGNAL('config changed')
sigConnectedTws = PYSIGNAL('connect tws')
sigConnectedTwsError = PYSIGNAL('connect tws error')
sigFinishTws = PYSIGNAL('tws finished')
sigOrdersUpdated = PYSIGNAL('OrderListViewUpdated')
sigStartTws = PYSIGNAL('StartTws')
sigStartTwsFail = PYSIGNAL('StartTwsFail')
sigSubmitOrder = PYSIGNAL('SubmitOrder')
sigUrlSelected = PYSIGNAL('urlSelected')
sigViewWebBrowser = PYSIGNAL('ViewWebBrowser')
sigViewSource = PYSIGNAL('ViewSource')
sigViewTicker = PYSIGNAL('ViewTicker')
sigViewTickerItem = PYSIGNAL('ViewTickerItem')

plotControlColorSelected = PYSIGNAL('PlotControlColorSelected')
plotControlToggle = PYSIGNAL('PlotControlToggle')
plotRescaled = PYSIGNAL('PlotRescaled')
plotCtrlClick = PYSIGNAL('PlotControlClicked')

sigActivated = SIGNAL('activated()')
sigClicked = SIGNAL('clicked()')
sigDockClosed = SIGNAL('headerCloseButtonClicked()')
sigDoubleClicked = SIGNAL('doubleClicked(QListViewItem *)')
sigLastClosed = SIGNAL('lastWindowClosed()')
sigPlotMouseMoved = SIGNAL('plotMouseMoved(const QMouseEvent &)')
sigPlotMouseReleased = SIGNAL('plotMouseReleased(const QMouseEvent&)')
sigProcessExit = SIGNAL('processExited()')
sigReleased = SIGNAL('released()')
sigSelectChanged = SIGNAL('selectionChanged(QListViewItem*)')
sigStateChanged = SIGNAL('stateChanged(int)')
sigStdoutReady = SIGNAL('readyReadStdout()')
sigTextChanged = SIGNAL('textChanged(const QString&)')
sigToggled = SIGNAL('toggled(bool)')
sigValueChanged = SIGNAL('valueChanged(int)')
sigListContext = \
    SIGNAL('contextMenuRequested(QListViewItem*,const QPoint&,int)')

slotAccept = SLOT('accept()')
slotQuit = SLOT('quit()')
slotReject = SLOT('reject()')

iconNoGroup = kdecore.KIcon.NoGroup
iconSizeSmall = kdecore.KIcon.SizeSmall
iconSizeMedium = kdecore.KIcon.SizeMedium

defaults = base.AttributeMapping(
    brokerDsn = 'localhost:7496',
    brokerScript = '',
    keyScript = '',
    keyScriptEnable = False,
    colorTickers = True,
    connectDelay = 0,
    embedDelay = 0,

    accountBuilder = '',
    strategyBuilder = '',
    tickersBuilder = '',
    tickersMappingBuilder = '',
)

keys = base.AttributeMapping(
    **dict(zip(defaults.keys(), defaults.keys()))
)

groups = base.AttributeMapping(
    broker = 'Broker',
    docks = 'Docks',
    output = 'Output',
    shell = 'Python Shell',
    toolbar = 'Toolbar',
    fonts = 'Fonts',
    misc = 'Misc',
    shortcuts = 'Shortcuts',
    session = 'Session',
    summary = 'Summary View',
    main = 'Main',
)


def addTickerImageDir(path, instance):
    """ addTickerImageDir(path, instance) -> help the instance load ticker icons

    """
    path = os.path.join(path, 'img/tickers/')
    loader = instance.iconLoader()
    dirs = instance.dirs()
    dirs.addResourceDir('icon', path)
    loader.reconfigure(str(instance.instanceName()), dirs)
    return path


def appConfig(group=None):
    """ appConfig(group=None) -> returns the application KConfig

    """
    config = kdecore.KGlobal.instance().config()
    if group is not None:
        config.setGroup(group)
    return config


def connectLastClosed(parent, method):
    """ connectLastClosed(parent, method) -> connects the last closed signal

    """
    parent.connect(qt.qApp, sigLastClosed, method)


def loadIcon(name, group=iconNoGroup, size=iconSizeSmall):
    """ loadIcon(name, group, size) -> load an icon

    """
    loader = kdecore.KGlobal.instance().iconLoader()
    return loader.loadIcon(name, group, size)


def loadIconSet(name, group=iconNoGroup, size=iconSizeSmall):
    """ loadIconSet(name, group, size) -> load an icon set

    """
    loader = kdecore.KGlobal.instance().iconLoader()
    return loader.loadIconSet(name, group, size)


def invokeBrowser(url='about:blank'):
    """ invokeBrowser(url) -> invoke the kde browser

    """
    kdecore.KApplication.kApplication().invokeBrowser(url)


def kMain(wintype, title, args=None, about=None, options=None):
    """ kMain(wintype, title, args) -> returns a KDE application and its window

    """
    if args is None:
        args = sys.argv

    if about:
        kdecore.KCmdLineArgs.init(args, about)
        if options is not None:
            kdecore.KCmdLineArgs.addCmdLineOptions(options)
        app = kdecore.KApplication()
        win = wintype()
    else:
        app = kdecore.KApplication(args, title)
        win = wintype(None)

    app.connect(app, sigLastClosed, app, slotQuit)
    app.setMainWidget(win)
    return (win, app)


def qMain(wintype, args=None):
    """ qMain(wintype, title, args) -> returns a KDE application and its window

    """
    if args is None:
        args = sys.argv[0:1]

    app = qt.QApplication(args)
    win = wintype()

    app.connect(app, sigLastClosed, app, slotQuit)
    app.setMainWidget(win)
    return (win, app)


def setShellFont(widget, config=None, key='Fonts', entry='shell'):
    """ setShellFont(self, config) -> read and set the shell font

    """
    if config is None:
        config = appConfig(key)

    if config is not None:
        default = kdecore.KGlobalSettings.fixedFont()
        widget.setFont(config.readFontEntry(entry, default))


def getTwsWindow(title='^.* - Interactive Brokers Trader Workstation'):
    """ getTwsWindow() -> window id and process id of a running TWS application

    """
    regx = re.compile(title)
    for win_id in kdecore.KWinModule().windows():
        info = kdecore.KWin.info(win_id)
        if regx.match(str(info.visibleNameWithState())):
            return win_id, info.pid
    return 0, 0


def getDockWidget(widget):
    """ getDockWidget(widget) -> returns the dock that contains the widget

    """
    try:
        manager = widget.topLevelWidget().manager()
        dock = manager.findWidgetParentDock(widget)
    except (AttributeError, ):
        dock = None
    return dock


def buildAction(name, label, icon, accel, tip, collection):
    """ buildAction(...) -> create and configure a KAction child

    """
    action = kdeui.KAction(collection, name)
    action.setShortcut(kdecore.KShortcut(accel))
    action.setIconSet(loadIconSet(icon))
    action.setIcon(icon)
    action.setText(kdecore.i18n(label))
    action.setToolTip(kdecore.i18n(tip))
    collection.insert(action)
    return action

class OutputFrame(kdeui.KTextEdit):
    """OutputFrame(...) -> outputs lines to a widget

    """
    def __init__(self, parent):
        kdeui.KTextEdit.__init__(self, parent)
        setShellFont(self)
        self.setReadOnly(True)

    def write(self, text):
        """write(txt) -> insert text into this widget

        """
        self.insert(text)

    def createPopupMenu(self, pos):
        """createPopupMenu(pos) -> redefines the popup menu with our extras

        """
        ret = kdeui.KTextEdit.createPopupMenu(self, pos)
        ret.insertItem('Clear', self.clear, qt.QKeySequence(), -1, 0)
        return ret

    def clear(self):
        """clear() -> removes all text from this widget

        """
        self.setText('')

    def connectProcess(self, process):
        """ connectProcess(process) -> connect process signals to this widget

        """
        self.process = process
        self.connect(process, sigStdoutReady, self.readStdout)
        self.connect(process, sigProcessExit, self.processExit)

    def readStdout(self):
        """ readStdout() -> read as much as possible from the process stdout

        """
        while self.process.canReadLineStdout():
            line = self.process.readLineStdout()
            line.append('\n')
            self.write(line)

    def processExit(self):
        """ processExit() -> writes process exit message

        """
        rpt = (self.process.exitStatus(), )
        self.write('Process Exited, status: %s' % rpt)

    def configChanged(self, config):
        config.setGroup(groups.fonts)
        font = config.readFontEntry('shell', qt.QFont('fixed'))
        self.setFont(font)


class SourceCodeRequest(qt.QObject):
    """ SourceCodeRequest(item) -> request to view the source code of an item

    """
    iconName = 'network'

    def __init__(self, item):
        qt.QObject.__init__(self)
        self.item = item

    def __str__(self):
        try:
            sourcefile = inspect.getsourcefile(self.item.__class__)
        except (TypeError, ):
            return self.item.__class__.__name__
        else:
            return '%s' % (os.path.split(sourcefile)[-1], )


class TickerUrl(qt.QObject):
    """ TickerUrl() -> emitted to display a ticker web page

        This could be integrated with the config with a bit of work.
    """
    request_defs = (
        ('Financials', 'money', 
         'http://biz.yahoo.com/fin/l/%(prefix)s/%(symbol)s.html'),

        ('Fundamentals', 'document', 
         'http://cbs.marketwatch.com/tools/quotes/news.asp?siteid=alliance' + \
         '&sid=609&property=sid&value=609&symb=%(symbol)s&doctype=2006'),

        ('Historical', 'history', 
         'about:blank'),

        ('News', 'flag', 
         'http://biz.yahoo.com/n/%(prefix)s/%(symbol)s.html'),

        ('Reports', 'document', 
         'http://screen.yahoo.com/d?vw=0&db=reports&z=dat&tk=%(symbol)s'),

        ('Research', 'todo', 
         'http://biz.yahoo.com/z/a/%(prefix)s/%(symbol)s.html'),
    )

    def __init__(self, key, symbol):
        qt.QObject.__init__(self)
        symbol = str(symbol).upper()
        prefix = symbol[0]
        label, icon, url = self.request_defs[key]
        params = {'icon':icon, 'label':label, 'prefix':prefix, 'symbol':symbol}
        self.url = url % params


def displayException(parent, title, exception):
    """ displayException(parent, title, exception) -> show an error message box

    """
    text = kdecore.i18n(title)
    details = '%s\n%r' % (exception, exception,)
    kdeui.KMessageBox.detailedError(parent, text, details)

