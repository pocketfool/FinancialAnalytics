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

This module defines the Profit Device application configuration dialog.

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'config.py,v 0.6 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.6',
}

import qt
import kdecore
import kdeui
import kfile

import profit.device.util as util
import profit.device.dialogs.syspath as syspath


i18n = kdecore.i18n
KDialogBase = kdeui.KDialogBase
gridMargin = gridSpace = 4

defaults = util.defaults
groups = util.groups
keys = util.keys


sessionBuilderKeys = (
    ('account_builder', 'accountBuilder'),
    ('strategy_builder', 'strategyBuilder'),
    ('tickers_builder', 'tickersBuilder'),
    ('tickers_mapping_builder', 'tickersMappingBuilder'),
)


sessionHelpText = (
'In each field below, enter the name of a python callable object.  The object '
'that is specified will be imported and called each time a session is '
'constructed.  You should enter the callable via the path browser, or in the '
'form <b>package.subpackage.module.callable</b> '
'<br><br><b>Note:</b> if a value is left empty, its default will be used.'
'<br>'
)


def buildIntSlider(parent, label, initial, 
                   numrange=(0,100,1,True), special='Disabled'):
    """ buildIntSlider(parent, label, initial) -> creates a nice KIntNumInput

    """
    try:
        label = i18n(label)
        special = i18n(special)
    except (TypeError, ):
        pass
    
    widget = kdeui.KIntNumInput(parent)
    widget.setLabel(label)
    widget.setRange(*numrange)
    widget.setSpecialValueText(special)
    widget.setValue(initial)
    return widget


class FontLabel(qt.QLineEdit):
    """ FontLabel(...) -> label that displays font family and size

    """
    def __init__(self, parent, font):
        qt.QLineEdit.__init__(self, '', parent)
        self.setPaletteBackgroundColor(parent.paletteBackgroundColor())
        self.setFont(font)
        self.setFrameStyle(qt.QFrame.LineEditPanel | qt.QFrame.Sunken)

    def setFont(self, font):
        """ setFont(font) -> change the label font and display it's properties

        """
        self.setReadOnly(False)
        self.setText('%s %s' % (font.family(), font.pointSize(), ))
        qt.QLineEdit.setFont(self, font)
        self.setReadOnly(True)
        self.emit(util.sigTextChanged, (self.text(), ))


class ConfigurationDialog(KDialogBase):
    """ ConfigurationDialog(...) -> Config dialog box with multiple pages

    """
    title = 'Settings'
    pageDefs = (
        (groups.broker, 
            'Configure the way the Profit Device interacts with the broker',
            'network'),
        (groups.session, 
            'Configure the way Profit Device builds trading sessions', 
            'blockdevice'),
        (groups.fonts, 
            'Configure the fonts for the Profit Device', 
            'fonts'),
        (groups.misc, 
            'Configure the miscellaneous items', 
            'files'), 
    )
    buttonsMask = (KDialogBase.Help | KDialogBase.Default | KDialogBase.Ok |
                   KDialogBase.Apply | KDialogBase.Cancel)


    def __init__(self, parent=None):
        KDialogBase.__init__(self, KDialogBase.IconList, i18n(self.title), 
                             self.buttonsMask, KDialogBase.Ok, parent, 
                             self.title, False, True)
        self.pages = pages = []
        self.configWidgets = {}
        medium = kdecore.KIcon.SizeMedium

        for label, title, icon in self.pageDefs:
            builder = getattr(self, 'build%sPage' % (label, ))
            config = util.appConfig(label)
            icon = util.loadIcon(icon, size=medium)
            frame = self.addPage(i18n(label), i18n(title), icon)
            frame.groupLabel = label
            builder(config, frame)
            pages.append(frame)

        self.enableButton(KDialogBase.Help, False)
        self.enableButton(KDialogBase.Apply, False)

    def buildSessionPage(self, config, frame):
        """ buildSessionPage(...) -> constructs widgets for session settings

        """
        layout = qt.QGridLayout(frame, 10, 2, gridMargin, gridSpace)
        layout.setRowStretch(layout.numRows()+10, 10)
        offset = 0
        for args in ((0, 0), (1, 2), (2, 0)):
            layout.setColStretch(*args)

        helplabel = qt.QLabel(sessionHelpText, frame)
        helplabel.setTextFormat(qt.Qt.RichText)
        layout.addMultiCellWidget(helplabel, 0, 0, 0, 2)
        offset += 1

        buildkeys = sessionBuilderKeys
        configrows = [offset + crow for crow in range(len(buildkeys))]
        configvals = [config.readEntry(ckey, '') for (bkey, ckey) in buildkeys]
        widgetdefs = zip(configrows, buildkeys, configvals)

        for index, (bkey, ckey), value in widgetdefs:
            label = qt.QLabel(bkey, frame)
            choose = kdeui.KPushButton('Select...', frame)
            choose.setPixmap(util.loadIcon('fileopen'))
            szwidth = choose.pixmap().width() + 8
            szheight = choose.pixmap().width() + 8
            choose.setFixedSize(szwidth, szheight)
            preview = choose.target = qt.QLineEdit(value, frame)

            for column, widget in enumerate((label, preview, choose)):
                layout.addWidget(widget, index, column)

            configrecord = (ckey, preview, '', preview.text, preview.setText)
            self.setConfigWidget(frame, configrecord)
            self.connect(choose, util.sigClicked, self.selectSysPath)
            self.connectChanged((preview, util.sigTextChanged))

    def buildBrokerPage(self, config, frame):
        """ buildBrokerPage(...) -> construct widgets for the broker settings

        """
        readpath = config.readPathEntry
        readnum = config.readNumEntry

        dsn = config.readEntry(keys.brokerDsn, defaults.brokerDsn)
        keyscript = readpath(keys.keyScript, defaults.keyScript)
        startscript = readpath(keys.brokerScript, defaults.brokerScript)
        connectdelay = readnum(keys.connectDelay, defaults.connectDelay)
        embeddelay = readnum(keys.embedDelay, defaults.embedDelay)

        connectgroup = qt.QVGroupBox(i18n('Network Connection'), frame)
        qt.QLabel(i18n('Broker connection string:'), connectgroup)
        dsnline = qt.QLineEdit(dsn, connectgroup)
        connectwid = buildIntSlider(
            connectgroup, 
            i18n('Seconds to delay before connecting to broker after launch:'),
            connectdelay)

        scriptsgroup = qt.QVGroupBox(i18n('Scripts'), frame)
        qt.QLabel(i18n('Broker application start command:'), scriptsgroup)
        startline = kfile.KURLRequester(startscript, scriptsgroup)
        qt.QLabel(i18n('Keystroke automation command:'), scriptsgroup)
        keyline = kfile.KURLRequester(keyscript, scriptsgroup)

        label = i18n('Seconds to delay before embedding broker window:')
        embedgroup = qt.QVGroupBox(i18n('Window Embedding'), frame)
        embedwid = buildIntSlider(embedgroup, label, embeddelay)

        layout = qt.QVBoxLayout(frame, gridMargin, gridSpace)
        layout.addWidget(connectgroup)
        layout.addWidget(scriptsgroup)
        layout.addWidget(embedgroup)
        layout.addStretch(10)

        self.setConfigWidget(frame, (keys.brokerDsn, 
                             dsnline, defaults.brokerDsn, dsnline.text, 
                             dsnline.setText))
 
        self.setConfigWidget(frame, (keys.brokerScript, 
                             startline, defaults.brokerScript, 
                             startline.url, startline.setURL))

        self.setConfigWidget(frame, (keys.keyScript, 
                             keyline, defaults.keyScript,
                             keyline.url, keyline.setURL))

        self.setConfigWidget(frame, (keys.connectDelay, 
                             connectwid, defaults.connectDelay,
                             connectwid.value, connectwid.setValue))

        self.setConfigWidget(frame, (keys.embedDelay, 
                             embedwid, defaults.embedDelay, 
                             embedwid.value, embedwid.setValue))

        self.connectChanged((dsnline, util.sigTextChanged),
                            (startline, util.sigTextChanged),
                            (keyline, util.sigTextChanged),
                            (connectwid, util.sigValueChanged),
                            (embedwid, util.sigValueChanged),)

    def buildFontsPage(self, config, frame):
        """ buildFontsPage(...) -> construct widgets for the font settings

        """
        layout = qt.QGridLayout(frame, 10, 2, gridMargin, gridSpace)
        layout.setRowStretch(layout.numRows()+10, 10)
        defaultfont = kdecore.KGlobalSettings.fixedFont()

        for args in ((0, 0), (1, 2), (2, 0)):
            layout.setColStretch(*args)

        for index, key in enumerate(('shell', 'code')):
            font = config.readFontEntry(key, defaultfont)

            fontlabel = qt.QLabel('%s' % (key.capitalize(), ), frame)
            fontchoose = kdeui.KPushButton('Choose...', frame)
            fontpreview = fontchoose.target = FontLabel(frame, font)

            layout.addWidget(fontlabel, index, 0)
            layout.addWidget(fontpreview, index, 1)
            layout.addWidget(fontchoose, index, 2)

            configrecord = (key, fontpreview, defaultfont, 
                             fontpreview.font, fontpreview.setFont)
            self.setConfigWidget(frame, configrecord)

            self.connect(fontchoose, util.sigClicked, self.selectFont)
            self.connectChanged((fontpreview, util.sigTextChanged))


    def buildMiscPage(self, config, frame):
        """ buildMiscPage(...) -> construct widgets for the misc settings

        """
        colortickers = config.readBoolEntry(keys.colorTickers, 
                                            defaults.colorTickers)

        label = i18n('Use colors when painting tickers list')
        color_check = qt.QCheckBox(label, frame)
        color_check.setChecked(colortickers)

        layout = qt.QVBoxLayout(frame, gridMargin, gridSpace)
        layout.addStretch(1)
        layout.addWidget(color_check)
        layout.addStretch(10)

        self.setConfigWidget(frame, (keys.colorTickers, 
                             color_check, defaults.colorTickers, 
                             color_check.isChecked, color_check.setChecked))

        self.connectChanged((color_check, util.sigStateChanged))


    def connectChanged(self, *pairs):
        """ connectChanged(*pairs) -> connect pairs to the hasChanged slot

        """
        for sender, signal in pairs:
            self.connect(sender, signal, self.hasChanged)


    def hasChanged(self):
        """ hasChanged() -> something has changed 

        """
        self.enableButtonApply(True)


    def slotApply(self):
        """ slotApply() -> write the configuration

        """
        for page in self.pages:
            config = util.appConfig(page.groupLabel)
            for items in self.getConfigWidgets(page):
                key = items[0]
                getter = items[3]
                config.writeEntry(key, getter())
        config.sync()
        self.emit(util.sigConfigChanged, (config, ))
        self.enableButtonApply(False)


    def slotCancel(self):
        """ slotCancel() -> reject the dialog

        """
        self.reject()


    def slotDefault(self):
        """ slotDefault() -> set default values on widgets in the active page

        """
        page = self.pages[self.activePageIndex()]
        for item in self.getConfigWidgets(page):
            default = item[2]
            setter = item[4]
            setter(default)
        self.hasChanged()


    def slotOk(self, *args):
        """ slotOk() -> write the configuration and accept the dialog

        """
        self.slotApply()
        self.accept()


    def selectFont(self):
        """ selectFont(target) -> set the targets font and text

        """
        target = self.sender().target
        dlg = kdeui.KFontDialog(self)
        dlg.setFont(target.font(), True)
        if dlg.exec_loop() == kdeui.KFontDialog.Accepted:
            target.setFont(dlg.font())


    def selectSysPath(self):
        """ selectSysPath() -> select an item from sys.path

        """
        target= self.sender().target
        dlg = syspath.SysPathDialog(self)
        if dlg.exec_loop() == kdeui.KFontDialog.Accepted:
            path = str.join('.', dlg.path)
            target.setText(path)


    def setConfigWidget(self, page, record):
        """ setConfigWidget(...) -> adds a config record to widget
    
        """
        widgets = self.configWidgets.setdefault(page, [])
        widgets.append(record)


    def getConfigWidgets(self, page):
        """ getConfigWidgets(parent) -> children of parent with a config record
    
        """
        return self.configWidgets.get(page, [])


if __name__ == '__main__':
    import profit.device.about as about
    win, app = util.kMain(ConfigurationDialog, 
                        'Profit Device Configuration', 
                         about=about.aboutData)
    win.show()
    app.exec_loop()
