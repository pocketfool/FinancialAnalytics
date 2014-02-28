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
""" The application main window

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'main.py,v 0.7 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.7',
}

import os
import sys

import qt
import kdeui
import kdecore

import profit.device.about as about
import profit.device.link as link
import profit.device.util as util

import profit.device.dialogs.config as configdialog
import profit.device.views.session as sessionview
import profit.device.views.node as nodeview
import profit.device.views.summary as summaryview
import profit.device.widgets.shell as shell
import profit.device.widgets.statusbar as statusbar

import profit.lib.session as session
import profit.lib.base as base


dockBottom = kdeui.KDockWidget.DockBottom
dockCenter = kdeui.KDockWidget.DockCenter
dockRight = kdeui.KDockWidget.DockRight
i18n = kdecore.i18n


try:
    __file__
except (NameError, ):
    __file__ = sys.argv[0]




class ProfitDeviceMainWindow(kdeui.KDockMainWindow):
    """ ProfitDeviceMainWindow() -> main window 

    """
    def __init__(self):
        kdeui.KDockMainWindow.__init__(self, None, 'profitdevice')
        self.setupInstance()
        self.setupActions()
        self.setupWidgets()
        self.setupFinal()

    ##~
    ##~ Initializers
    ##~

    def setupInstance(self):
        """ setupInstance() -> setup this window instance

        """
        rcname = 'profitdevice.rc'
        confname = '~/.profitdevice'

        self.session = {}
        self.dockWidgets = []

        confdir = os.path.expanduser(confname)
        if not os.path.exists(confdir):
            try:
                os.mkdir(confdir)
            except (IOError, ):
                pass

        self.appScript = os.path.abspath(__file__)
        self.appDir = os.path.dirname(self.appScript)
        self.xmlRcFileName = os.path.abspath(os.path.join(self.appDir, rcname))

        util.addTickerImageDir(self.appDir, self.instance())
        self.nodeViewer = nodeview.NodeViewer(self)
        self.setXMLFile(self.xmlRcFileName)

    def setupActions(self):
        """ setupActions() -> create the action attributes for the widget

        """
        config = util.appConfig()
        actions = self.actionCollection()
        stdaction = kdeui.KStdAction
        actions.readShortcutSettings(util.groups.shortcuts, config)

        self.newAction = stdaction.openNew(self.newSession, actions)
        self.newAction.setIconSet(util.loadIconSet('blockdevice'))
        self.newAction.setIcon('blockdevice')
        self.newAction.setText(i18n('New Session'))

        self.quitAction = stdaction.quit(self.close, actions)
        self.closeWindowAction = stdaction.close(self.closeDockWindow, actions)

        self.toggleMenubarAction = \
            stdaction.showMenubar(self.showMenubar, actions)
        self.toggleToolbarAction = \
            stdaction.showToolbar(self.showToolbar, actions)
        self.toggleStatusbarAction = \
            stdaction.showStatusbar(self.showStatusbar, actions)
        self.configureKeysAction = \
            stdaction.keyBindings(self.showConfigureKeys, actions)
        self.configureToolbarAction = \
            stdaction.configureToolbars(self.showConfigureToolbars, actions)
        self.configureAppAction = \
            stdaction.preferences(self.showConfiguration, actions)

        self.webBrowserAction = util.buildAction('web_browser', 
            'Web Browser', 'konqueror', 'Ctrl+B', 'Show a web browser window',
            actions)

        self.startTwsAction = util.buildAction('start_tws', 
            'Start TWS', 'exec', 'Ctrl+T', 'Start the TWS application', 
            actions)

        self.connectTwsAction = util.buildAction('connect_tws', 
            'Connect to TWS', 'network', 'Ctrl+G', 'Connect to the TWS application',
            actions)

        sigAct = util.sigActivated
        self.connect(self.startTwsAction, sigAct, self.startTws)
        self.connect(self.connectTwsAction, sigAct, self.connectTws)
        self.connect(self.webBrowserAction, sigAct, util.invokeBrowser)

    def setupWidgets(self):
        """ setupWidgets() -> create main widgets for the window

        """
        self.manager().setSplitterOpaqueResize(True)
        statusbar.MainStatusBar(self)

        connect = self.connect
        nodeviewer = self.nodeViewer
        docktype = kdeui.KDockWidget
        build = self.buildDock

        shelldock, self.pythonShell = \
            build(util.groups.shell, 'terminal', shell.InteractiveShell)

        sessiondock, self.sessionList = \
            build('Session Tree', 'blockdevice', sessionview.SessionListView)

        summarydock, self.summaryFrame = \
            build('Account Summary', 'whatsnext', summaryview.SummaryLCDFrame)

        stdoutdock, self.stdoutFrame = \
            build(util.groups.output, 'openterm', util.OutputFrame)

        stderrdock, self.stderrFrame = \
            build('Error', 'openterm', util.OutputFrame)

        self.outputDock = stdoutdock
        shelldock.setEnableDocking(docktype.DockNone)
        self.setView(shelldock)
        self.setMainDockWidget(shelldock)

        shelldock.manualDock(sessiondock, dockRight, 30)
        summarydock.manualDock(sessiondock, dockCenter, 20)
        stdoutdock.manualDock(shelldock, dockBottom, 80)
        stderrdock.manualDock(stdoutdock, dockCenter, 80)

        for item in (self.pythonShell, self.stdoutFrame):
            base.stdtee(item, 'stdout')
        for item in (self.pythonShell, self.stderrFrame):
            base.stdtee(item, 'stderr')

        connect(self.sessionList, util.sigViewSource, nodeviewer.viewNode)
        connect(self.sessionList, util.sigDoubleClicked, nodeviewer.viewNode)

        sigNewSess = util.sigNewSession
        connect(self, sigNewSess, self.sessionList.setSession)
        connect(self, sigNewSess, self.pythonShell.sessionToNamespace)
        connect(self, sigNewSess, self.summaryFrame.resetDisplays)
        connect(self, util.sigViewTickerItem, self.nodeViewer.viewNode)

    def setupFinal(self):
        """ setupFinal() -> various final setup operations

        """
        config = util.appConfig(util.groups.main)
        self.restoreWindowSize(config)

        xmlfile = os.path.join(self.appDir, 'profitdevice.rc')
        self.createGUI(xmlfile, 0)

        kargs = kdecore.KCmdLineArgs.parsedArgs()

        if kargs.isSet('session'):
            self.newAction.activate()
            if kargs.isSet('start-tws'):
                self.startTwsAction.activate()

        ## apply the previous dock config and then delete it to keep it small
        config = util.appConfig()
        self.readDockConfig(config, util.groups.docks)
        config.deleteGroup(util.groups.docks, True)
        config.sync()

        ## looks nice with the sparkling icons
        pxm = util.loadIcon('tab_breakoff', size=kdecore.KIcon.SizeLarge)
        mpx = util.loadIcon('tab_breakoff', size=kdecore.KIcon.SizeSmall)
        kdecore.KWin.setIcons(self.winId(), pxm, mpx)

        config = util.appConfig()
        self.applyMainWindowSettings(config)
        self.toolBar().applySettings(config, None)
        self.pythonShell.onGuiComplete()

        ## optional parameter used because the main widget  isn't built yet
        link.connect(self.statusBar(), self)
        link.connect(self.summaryFrame, self)

    ##~
    ##~ Custom Slots
    ##~

    def newSession(self):
        """ newSession() -> slot for new session construction 

            This is where the new session is actually created.  A separate 
            signal is then emitted from this slot.
        """
        params = {}
        params['connection_builder'] = link.QIbSocketReader.build

        config = util.appConfig(util.groups.session)
        for (bkey, ckey) in configdialog.sessionBuilderKeys:
            value = '%s' % config.readEntry(ckey, '')
            if value:
                params[bkey] = value

        try:
            sess = session.Session(**params)
        except (Exception, ), ex:
            import traceback
            traceback.print_exc()
            print >> sys.__stdout__, ex
            util.displayException(self, 'Problem building session object', ex)
            sess = {}

        self.session = sess

        if sess:
            self.link = link.MessageTransmitter(self, sess)
            self.emit(util.sigNewSession, (sess, )) 

    def closeDockWindow(self):
        """ closeDockWindow() -> close the current tab on the main dock widget

        """
        dock = self.getMainDockWidget()
        tabs = dock.parentDockTabGroup()
        if tabs:
            self.removeDock(tabs.currentPage())

    def startGuiHelper(self):
        """ startGuiHelper() -> start the gui keystroke helper script

        """
        config = util.appConfig(util.groups.broker)
        script = config.readPathEntry(util.keys.keyScript, '')

        if not str(script): 
            return

        helper = qt.QProcess()
        for arg in str(script).split():
            helper.addArgument(arg)
        code = helper.start()
        if code:
            label = 'Keystroke Helper'
            dock, outputframe = \
                self.buildDock(label, 'openterm', util.OutputFrame)
            dock.manualDock(self.outputDock, dockCenter, 20)
            outputframe.connectProcess(helper)
            dock.dockManager().makeWidgetDockVisible(outputframe)

    def startTws(self):
        """ startTws() -> handles TWS start request

        """
        config = util.appConfig(util.groups.broker)
        script = config.readPathEntry(util.keys.brokerScript, '')

        if not str(script): 
            msg = 'Broker application start command not set.'
            title = 'Application Not Started'
            kdeui.KMessageBox.sorry(self, msg, title)
            return

        tws = qt.QProcess()
        for arg in str(script).split():
            tws.addArgument(arg)

        code = tws.start()
        if code:
            self.startGuiHelper()
            dock, outputframe = \
                self.buildDock('TWS Output', 'openterm', util.OutputFrame)  #, parent=None, transient=True)

            dock.manualDock(self.outputDock, dockCenter, 20)
            dock.dockManager().makeWidgetDockVisible(outputframe)
            outputframe.connectProcess(tws)

            #print self.shellDock, 
            #self.anyOtherDock = dock
            #print self.getMainDockWidget(), dock
            #dock.manualDock(self.getMainDockWidget(), dockBottom, 50) # , 100, qt.QPoint(0, 0), False, -1)
            #dock.dockManager().makeWidgetDockVisible(outputframe)
            #self.connect(dock, util.sigDockClosed, self.closeClicked)

            #self.shellDock.manualDock(dock, dockCenter)
            #print dock.manualDock
            #outputframe.connectProcess(tws)
            #dock.dockManager().makeWidgetDockVisible(outputframe)

            if 0: # this is how node viewers pull it off, but !!! it doesn't work here
                parent = self.parent()
                framector = base.PartialCall(NodeFrame, node=node, label=label)
                dock, obj = parent.buildDock(label, iconname, framector, transient=True)
                dock.manualDock(parent.getMainDockWidget(), center, 20)
                dock.dockManager().makeWidgetDockVisible(obj)
                self.connect(dock, util.sigDockClosed, self.closeClicked)

            defaults = util.defaults
            keys = util.keys
            readnum = util.appConfig(util.groups.broker).readNumEntry
            connectdelay = readnum(keys.connectDelay, defaults.connectDelay)
            embeddelay = readnum(keys.embedDelay, defaults.embedDelay)

            if connectdelay:
                qt.QTimer.singleShot(connectdelay*1000, self.connectTws)
            if embeddelay:
                qt.QTimer.singleShot(embeddelay*1000, self.embedTws)

            self.connect(tws, qt.SIGNAL('processExited()'), self.finishedTws)
            sig, args = (util.sigStartTws, (tws, ))
        else:
            sig, args = (util.sigStartTwsFail, (code, ))
        self.emit(sig, args)

    def finishedTws(self):
        """ finishedTws() -> a tws process has finished

        """
        process = self.sender()
        self.emit(util.sigFinishTws, (process, ))

    def embedTws(self):
        """ embedTws() -> embed the TWS main window into this window

        """
        winid, pid = util.getTwsWindow()
        if winid:
            dock, twsembed = self.buildDock('TWS Embeded', 'terminal', 
                                            kdeui.QXEmbed, transient=True)
            twsembed.embed(winid)
            dock.manualDock(self.getMainDockWidget(), dockCenter, 20)
            dock.dockManager().makeWidgetDockVisible(twsembed)
            dock.pid = pid

    def connectTws(self):
        """ connectTws() -> handles request to connect to tws

            If the broker is connected, this method requests the external data 
            feed.
        """
        config = util.appConfig(util.groups.broker)
        dsn = config.readEntry(util.keys.brokerDsn, 
                               util.defaults.brokerDsn)

        if not str(dsn):
            msg = 'Connection string not set.'
            title = 'Did Not Connect'
            kdeui.KMessageBox.sorry(self, msg, title)
            return

        host, port = str(dsn).split(':')
        broker = self.session.broker

        try:
            connected = broker.connection.reader.active
        except (AttributeError, ):
            pass
        else:
            if connected:
                msg = 'Broker connection is active, connect anyway?'
                title = 'Confirm Connect' 
                dlg = kdeui.KMessageBox
                cancel = (dlg.warningYesNo(self, msg, title) == dlg.No)
                if cancel:
                    return
    
        try:
            ## connect the lib object and request data feeds
            broker.connect((host, int(port)))
            broker.request_external()
            self.emit(util.sigConnectedTws, ())
        except (Exception, ), ex:
            self.emit(util.sigConnectedTwsError, (ex, ))

    def showConfiguration(self):
        """ showConfiguration() -> display the config dialog

        """
        dlg = configdialog.ConfigurationDialog(self)
        for obj in (self.stderrFrame, self.stdoutFrame, self.pythonShell):
            call = getattr(obj, 'configChanged', None)
            if call:
                self.connect(dlg, util.sigConfigChanged, call)
        dlg.show()

    def senderCheckShow(self, widget):
        """ senderCheckShow(widget) -> show or hide widget if sender is checked

        """
        if self.sender().isChecked():
            widget.show()
        else:
            widget.hide()

    def showMenubar(self):
        """ showMenuBar() -> toggle the menu bar

        """
        self.senderCheckShow(self.menuBar())

    def showToolbar(self):
        """ showToolbar() -> toggle the tool bar

        """
        self.senderCheckShow(self.toolBar())

    def showStatusbar(self):
        """ showStatusbar() -> toggle the status bar

        """
        self.senderCheckShow(self.statusBar())

    def showConfigureKeys(self):
        """ showConfigureKeys() -> show the shortcut keys dialog

        """
        ret = kdeui.KKeyDialog.configure(self.actionCollection(), self)
        if ret == qt.QDialog.Accepted:
            actions = self.actionCollection()
            actions.writeShortcutSettings(util.groups.shortcuts, util.appConfig())

    def showConfigureToolbars(self):
        """ showConfigureToolbars() -> broken

        """
        dlg = kdeui.KEditToolbar(self.actionCollection(), self.xmlRcFileName)
        self.connect(dlg, qt.SIGNAL('newToolbarConfig()'), self.rebuildGui)
        dlg.exec_loop()

    def rebuildGui(self):
        """ rebuildGui() -> recreate the gui and refresh the palette

        """
        self.createGUI(self.xmlRcFileName, 0)
        for widget in (self.toolBar(), self.menuBar(), ):
            widget.setPalette(self.palette())

    ##~
    ##~ Reimplemented Slots
    ##~

    def queryExit(self):
        """ queryExit(event) -> last window is closing

            This method returns a bool to meet KDE requirements.
        """
        return True

    def queryClose(self):
        """ queryClose() -> prompts user for close confirmation when connected

        """
        okay = True
        try:
            connected = self.session.account.connection.reader.active
        except (AttributeError, KeyError):
            pass
        else:
            if connected:
                msg = i18n('Broker connection is active, quit anyway?')
                title = i18n('Confirm Quit')
                dlg = kdeui.KMessageBox
                okay = (dlg.warningYesNo(self, msg, title) == dlg.Yes)
        if okay:
            config = util.appConfig()
            self.saveMainWindowSettings(config)
            config = util.appConfig(util.groups.main)
            self.saveWindowSize(config)
        return okay

    ##~
    ##~ Misc.
    ##~

    def buildDock(self, key, icon, klass, parent=None, transient=False):
        """ buildDock(...) -> create and configure a dock widget
    
        """
        dock = self.createDockWidget(key, util.loadIcon(icon), parent, key, key)
        widget = klass(dock)
        dock.setWidget(widget)
        dock.setDockSite(kdeui.KDockWidget.DockFullSite)
        self.dockWidgets.append(dock)
        dock.transient = transient
        return dock, widget

    def removeDock(self, dock):
        """ removeDock(dock) -> remove a dock widget

        """
        if dock.transient:
            try:
                self.dockWidgets.remove(dock)
            except (ValueError, ):
                pass
            else:
                dock.deleteLater()

    def buildMenu(self, label):
        """ buildMenu(label) -> create and configure a popup menu on the menubar

        """
        menu = qt.QPopupMenu(self)
        menu.insertTearOffHandle()
        self.menuBar().insertItem(i18n(label), menu)
        return menu

    def placeOrder(self, contract, order):
        account = self.session.account
        if not account.order_acceptable(order):
            return ## add a msg box
        oid = account.order_id_generator.next()
        account.orders.new_order(order_id=oid, contract=contract, order=order)
        account.connection.place_order(oid, contract, order)


if __name__ == '__main__':
    options = [
        ('nosession', 'Disable initial session construction.'), 
        ('start-tws', 'Launch TWS application on startup.'), 
        ('noembed', 'Disable embedding the TWS application.'),
    ]
    window, application = util.kMain(ProfitDeviceMainWindow, 
                                    'Profit Device', 
                                    about=about.aboutData,
                                    options=options)

    window.connect(application, qt.SIGNAL('kdisplayPaletteChanged()'),
                   window.rebuildGui)
    window.show()
    application.exec_loop()
