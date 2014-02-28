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
""" Widget to display a summary of an account by way of lcds

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'summary.py,v 0.3 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.3',
}

import qt

import kdecore
import kdeui

import profit.device.link as link
import profit.device.util as util


KDialogBase = kdeui.KDialogBase
i18n = kdecore.i18n

sampleKeys = [
    'AccountCode',
    'AccountType',
    'AvailableFunds',
    'AvailableFunds-C',
    'AvailableFunds-S',
    'BuyingPower',
    'TotalCashBalance',
    'DayTradesRemaining',
    'DayTradesRemainingT+1',
    'DayTradesRemainingT+2',
    'DayTradesRemainingT+3',
    'DayTradesRemainingT+4',
    'EquityWithLoanValue',
    'EquityWithLoanValue-C',
    'EquityWithLoanValue-S',
    'ExcessLiquidity',
    'ExcessLiquidity-C',
    'ExcessLiquidity-S',
    'FullAvailableFunds',
    'FullAvailableFunds-C',
    'FullAvailableFunds-S',
    'FullExcessLiquidity',
    'FullExcessLiquidity-C',
    'FullExcessLiquidity-S',
    'FullInitMarginReq',
    'FullInitMarginReq-C',
    'FullInitMarginReq-S',
    'FullMaintMarginReq',
    'FullMaintMarginReq-C',
    'FullMaintMarginReq-S',
    'FutureOptionValue',
    'FuturesPNL',
    'GrossPositionValue',
    'GrossPositionValue-S',
    'InitMarginReq',
    'InitMarginReq-C',
    'InitMarginReq-S',
    'Leverage-S',
    'LookAheadAvailableFunds',
    'LookAheadAvailableFunds-C',
    'LookAheadAvailableFunds-S',
    'LookAheadExcessLiquidity',
    'LookAheadExcessLiquidity-C',
    'LookAheadExcessLiquidity-S',
    'LookAheadInitMarginReq',
    'LookAheadInitMarginReq-C',
    'LookAheadInitMarginReq-S',
    'LookAheadMaintMarginReq',
    'LookAheadMaintMarginReq-C',
    'LookAheadMaintMarginReq-S',
    'LookAheadNextChange',
    'MaintMarginReq',
    'MaintMarginReq-C',
    'MaintMarginReq-S',
    'NetLiquidation',
    'NetLiquidation-C',
    'NetLiquidation-S',
    'OptionMarketValue',
    'PNL',
    'PreviousDayEquityWithLoanValue',
    'PreviousDayEquityWithLoanValue-S',
    'RealizedPnL',
    'SettledCash',
    'SettledCash-C',
    'SettledCash-S',
    'StockMarketValue',
    'TimeStamp',
    'TotalCashValue',
    'TotalCashValue-C',
    'TotalCashValue-S',
    'UnalteredInitMarginReq',
    'UnalteredMaintMarginReq',
    'UnrealizedPnL',
]

defaultKeys = [
    'TotalCashBalance', 'RealizedPnL', 'UnrealizedPnL', 'NetLiquidation',
]

lcdStyles = [
    ('Outline', qt.QLCDNumber.Outline, 'color_line'),
    ('Filled', qt.QLCDNumber.Filled, 'color_fill', ),
    ('Flat', qt.QLCDNumber.Flat, 'greenled'),
]


class LCDNumber(qt.QLCDNumber):
    """LCDNumber() -> lcd number widget with a default appearance

    """
    def __init__(self, parent, initial_value='0,000,000.00', margin=4, width=0, 
                 small_decimal=True):
        qt.QLCDNumber.__init__(self, len(initial_value), parent)
        self.initial_value = initial_value
        self.display(initial_value)
        self.setMargin(margin)
        self.setLineWidth(width)
        self.setSmallDecimalPoint(small_decimal)

    def resetDisplay(self):
        """ resetDisplay() -> display the initial value

        """
        self.display(self.initial_value)


class SummarySelector(KDialogBase):
    """ SummarySelector() -> dialog box for selecting the account summary keys

    """
    def __init__(self, parent, title='Select Summary LCDs'):
        buttons_mask = KDialogBase.Ok | KDialogBase.Cancel
        KDialogBase.__init__(self, KDialogBase.Plain, i18n(title),
                            buttons_mask, KDialogBase.Ok, parent, title, 
                            True, False)

        self.selections = []
        self.view = view = qt.QListView(self)
        self.setMainWidget(view)
        self.layout().insertWidget(0, view, 100)
        self.setupView()

    def setupView(self):
        """ setupView() -> recreate the QListView attribute

        """
        parent = self.parent()
        view = self.view
        view.clear()
        header = view.header()

        for index in range(header.count()):
            header.removeLabel(index)

        view.addColumn(i18n('Account Key'))
        view.addColumn(i18n('Last Value'))
        view.setSelectionMode(qt.QListView.Single)
        view.setColumnWidthMode(0, qt.QListView.Maximum)

        ##
        ## sampleKeys needs to become account data keys
        ##
        displayed_keys = parent.summaries.keys()
        all_keys = sampleKeys
        for key in all_keys:
            item = qt.QCheckListItem(view, key, qt.QCheckListItem.CheckBox)
            #item.setText(1, '%s' % some_last_value)
            if key in displayed_keys:
                item.setOn(True)

    def slotCancel(self):
        """ slotCancel() -> reject the dialog

        """
        self.reject()

    def slotOk(self):
        """ slotOk() -> write the configuration and accept the dialog

        """
        selections = self.selections
        item = self.view.firstChild()

        while item:
            if item.isOn():
                selections.append(str(item.text()))
            item = item.nextSibling()

        self.accept()


class SummaryLCDFrame(qt.QFrame):
    """SummaryLCDFrame() -> frame that displays account data in lcd widgets

    """
    def __init__(self, parent=None):
        qt.QFrame.__init__(self, parent)
        self.summaries = {}

        layout = qt.QVBoxLayout(self)
        layout.setMargin(kdeui.KDialogBase.marginHint())
        layout.setSpacing(kdeui.KDialogBase.spacingHint())

        self.setupWidgets()
        self.setupInitial()

    def setupWidgets(self):
        """ setupWidgets() -> create the buttons for the frame

        """
        self.selectButton = select_button = \
            kdeui.KPushButton(i18n('Select...'), self)
        self.defaultsButton = defaults_button = \
            kdeui.KPushButton(i18n('Defaults'), self)

        button_layout = qt.QHBoxLayout()
        button_layout.addWidget(select_button, 0)
        button_layout.addWidget(defaults_button, 0)
        button_layout.addStretch(100)

        self.layout().addLayout(button_layout)
        self.layoutOffset = len(self.children())
        self.connect(select_button, util.sigClicked, self.selectSummaries)
        self.connect(defaults_button, util.sigClicked, self.defaultSummaries)

    def setupInitial(self):
        """ setupInitial() -> setup the initial display

        """
        config = util.appConfig(util.groups.summary)
        initkeys = [str(k) for k in config.readListEntry('Selected', ',')]
        initkeys = initkeys or defaultKeys
        for key in initkeys:
            self.addSummary(key)

    def resetDisplays(self, session):
        """ resetDisplays() -> set each current lcd to its default text

            This method could look at the session acocunt and loop over its 
            values and match its keys to the existing setup.  In  practice, 
            this method is never given a running session (i.e., one with 
            current data in an account object) so it doesn't bother.
        """
        for pair in self.summaries.values():
            lcd = pair[1]
            lcd.resetDisplay()
        session = session

    def slotAccount(self, evt):
        """ slotAccountUpdate(event) -> slot called with broker account update

        """
        key, value = evt.key, evt.value
        try:
            pair = self.summaries[key]
            lcd = pair[1]
            lcd.display(value)
        except (KeyError, IndexError, ):
            pass

    def contextMenuEvent(self, event):
        """ contextMenuEvent(event) -> display context menu

        """
        widget = self.childAt(event.pos())
        children, labels, lcds = self.summaryChildren()

        if widget in lcds:
            key = lcds[widget]
            lcd = widget
            label = self.summaries[key][0]
        elif widget in labels:
            key = labels[widget]
            lcd = self.summaries[key][1]
            label = widget
        else:
            event.ignore()
            return

        pop = kdeui.KPopupMenu(self)
        self.context = (key, label, lcd)

        item = pop.insertItem(util.loadIconSet('up'), i18n('Move Up'), 
                              self.moveSummary)
        pop.setItemParameter(item, 0)
        if not children.index(label):
            pop.setItemEnabled(item, False)

        item = pop.insertItem(util.loadIconSet('down'), i18n('Move Down'), 
                              self.moveSummary)
        pop.setItemParameter(item, 1)
        if children.index(lcd) + 1 == len(children):
            pop.setItemEnabled(item, False)

        pop.insertSeparator()
        item = pop.insertItem(util.loadIconSet('remove'), 
                              i18n('Remove "%s"' % (key, )), 
                              self.removeSummary)
        pop.insertSeparator()
        for index, label, color in (
                (0, 'Background color...', lcd.paletteBackgroundColor()),
                (1, 'Foreground color...', lcd.paletteForegroundColor())):

            item = pop.insertItem('', self.selectColor)
            pixmap = qt.QPixmap(16, 16)
            pixmap.fill(color)
            icons = qt.QIconSet(pixmap)
            pop.changeItem(item, icons, i18n(label))
            pop.setItemParameter(item, index)

        pop.insertSeparator()
        for label, style, icon in lcdStyles:
            item = pop.insertItem(util.loadIconSet(icon), i18n(label), 
                                  self.selectSegmentStyle)
            pop.setItemParameter(item, style)
            pop.setItemChecked(item, style==lcd.segmentStyle())

        pop.popup(event.globalPos())

    def swapItems(self, (label, lcd), (other_label, other_lcd)):
        """ swapItems(...) -> swap a label+lcd pair

        """
        text = label.text()
        other_text = other_label.text()
        label.setText(other_text)

        key = str(text)
        other_key = str(other_text)
        other_label.setText(text)

        value = lcd.value()
        other_value = other_lcd.value()
        lcd.display(other_value)
        other_lcd.display(value)

        style = lcd.segmentStyle()
        other_style = other_lcd.segmentStyle()
        lcd.setSegmentStyle(other_style)
        other_lcd.setSegmentStyle(style)

        fore_color =  qt.QColor(lcd.paletteForegroundColor())
        other_fore_color =  qt.QColor(other_lcd.paletteForegroundColor())
        lcd.setPaletteForegroundColor(other_fore_color)
        other_lcd.setPaletteForegroundColor(fore_color)

        back_color = qt.QColor(lcd.paletteBackgroundColor())
        other_back_color = qt.QColor(other_lcd.paletteBackgroundColor())
        lcd.setPaletteBackgroundColor(other_back_color)
        other_lcd.setPaletteBackgroundColor(back_color)

        self.summaries[key] = (other_label, other_lcd)
        self.summaries[other_key] = (label, lcd)
        self.writeLcd(key, other_lcd)
        self.writeLcd(other_key, lcd)

    def summaryChildren(self):
        """ summaryChildren() -> returns the widgets used in summary display

        """
        summary_items = self.summaries.items()
        labels = dict([(label, k) for k, (label, lcd) in summary_items])
        lcds = dict([(lcd, k) for k, (label, lcd) in summary_items])
        ## this is sorted because QWidget maitains the child order
        children = [child for child in self.children() 
                            if child in labels or child in lcds]
        return (children, labels, lcds)

    def moveSummary(self, direction):
        """ moveSummary(direction) -> move the current label+lcd pair up or down

        """
        label, lcd = self.context[1:3]
        all_children = self.summaryChildren()
        children = all_children[0]

        if direction:
            offset = +2
        else:
            offset = -2
        other_label = children[children.index(label) + offset]
        other_lcd = children[children.index(lcd) + offset]
        self.swapItems((label, lcd), (other_label, other_lcd))

    def selectSummaries(self):
        """ selectSummaries() -> show a widget for selecting summaries

        """
        selector = SummarySelector(self)
        selector.resize(self.size())
        selector.setGeometry(self.geometry())

        result = selector.exec_loop()
        if result == KDialogBase.Accepted:
            self.clearSummaries()

            for key in selector.selections:
                self.addSummary(key)

            self.showSummaries()

    def selectColor(self, param):
        """ selectColor(param) -> select the lcd fore- or back-ground color

        """
        key = self.context[0]
        lcd = self.context[2]

        ## lame but simple
        if param:
            getter = lcd.paletteForegroundColor
            setter = lcd.setPaletteForegroundColor
        else:
            getter = lcd.paletteBackgroundColor
            setter = lcd.setPaletteBackgroundColor

        oldcolor = getter()
        result = kdeui.KColorDialog.getColor(oldcolor, self)
        if result == kdeui.KColorDialog.Accepted:
            setter(oldcolor)
            self.writeLcd(key, lcd)

    def selectSegmentStyle(self, style):
        """ selectSegmentStyle(style) -> set the context lcd segment style

        """
        key = self.context[0]
        lcd = self.context[2]

        lcd.setSegmentStyle(style)
        self.writeLcd(key, lcd)

    def readLcd(self, key, widget):
        """ readLcd(key, widget) -> configure an lcd

        """
        config = util.appConfig(util.groups.summary)

        style = qt.QLCDNumber.Flat
        forecolor = qt.QColor(0, 255, 128)
        backcolor = qt.QColor(0, 0, 0)

        style = config.readNumEntry('%s__style' % (key, ), style)
        forecolor = config.readColorEntry('%s__fore' % (key, ), forecolor)
        backcolor = config.readColorEntry('%s__back' % (key, ), backcolor)

        widget.setFrameStyle(qt.QFrame.StyledPanel | qt.QFrame.Sunken)
        widget.setSegmentStyle(style)
        widget.setPaletteForegroundColor(forecolor)
        widget.setPaletteBackgroundColor(backcolor)

    def writeLcd(self, key, widget):
        """ writeLcd(key, widget) -> write lcd settings to the config

        """
        style = widget.segmentStyle()
        forecolor = widget.paletteForegroundColor()
        backcolor = widget.paletteBackgroundColor()
        
        config = util.appConfig(util.groups.summary)
        config.writeEntry('%s__style' % (key, ), style)
        config.writeEntry('%s__fore' % (key, ), forecolor)
        config.writeEntry('%s__back' % (key, ), backcolor)
        config.sync()

    def writeSelected(self):
        """ writeSelected() -> write the current selections to the app config

        """
        config = util.appConfig(util.groups.summary)
        config.writeEntry('Selected', self.summaries.keys())
        config.sync()

    def clearSummaries(self):
        """ clearSummaries() -> removes every summary

        """
        for key in self.summaries.keys():
            self.removeSummary(key=key)

    def showSummaries(self):
        """ showSummaries() -> display each label and lcd

        """
        for lcd, label in self.summaries.values():
            lcd.show()
            label.show()

    def addSummary(self, key):
        """ addSummary(key) -> add a summary label and lcd to the layout

        """
        label = qt.QLabel(key, self)
        font = qt.QFont(label.font())
        font.setBold(True)
        label.setFont(font)

        lcd = LCDNumber(self)

        layout = self.layout()
        layout.addWidget(label)
        layout.addWidget(lcd)
        layout.setStretchFactor(lcd, 100)

        self.readLcd(key, lcd)
        self.summaries[key] = (label, lcd)
        self.writeLcd(key, lcd)

    def defaultSummaries(self):
        """ defaultSummaries() -> clear and then create the default summary lcds

        """
        self.clearSummaries()
        config = util.appConfig()
        config.deleteGroup(util.groups.summary, True)
        for key in defaultKeys:
            self.addSummary(key)
        self.showSummaries()
        self.writeSelected()

    def removeSummary(self, param=None, key=None):
        """ removeSummary() -> remove the label and lcd

        """
        if key is None:
            key = self.context[0]

        label, lcd = self.summaries[key]
        layout = self.layout()

        param = param # pylint
        del(self.summaries[key])

        for widget in (label, lcd):
            layout.remove(widget)
            self.removeChild(widget)
            widget.close()
        self.writeSelected()


if __name__ == '__main__':
    import profit.device.about as about
    win, app = util.kMain(SummaryLCDFrame, 
                        'Profit Device Summary View', 
                         about=about.aboutData)
    win.show()
    app.exec_loop()
