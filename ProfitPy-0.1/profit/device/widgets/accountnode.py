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
""" profit.widgets.accountnode -> widgets to display account session objects


"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'accountnode.py,v 0.4 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.4',
}

import qt
import qwt

import kdeui

import profit.device.link as link
import profit.device.util as util
import profit.device.widgets.plot as plot
import profit.device.widgets.nodebase as nodebase

import profit.lib.base as base


alignCenter = qt.Qt.AlignCenter
alignLeft = qt.Qt.AlignLeft
alignRight = qt.Qt.AlignRight

shortStr = nodebase.shortStr
BaseNodeWidget = nodebase.BaseNodeWidget
BaseNodeListView = nodebase.BaseNodeListView


##-----------------------------------------------------------------------------
##
## Account Supervisor Node and related widgets
##
##-----------------------------------------------------------------------------
class AccountSupervisorNode(BaseNodeWidget):
    """AccountSupervisorNode(parent, node) -> displays account values and plot

    """
    iconName = 'contents'

    def __init__(self, parent, node):
        BaseNodeWidget.__init__(self, parent, node)

        mainlayout = qt.QHBoxLayout(self, 0, 0)
        mainsplit = qt.QSplitter(self)
        mainsplit.setOrientation(qt.QSplitter.Vertical)
        mainlayout.addWidget(mainsplit)

        plotsplit = qt.QSplitter(mainsplit)
        plotsplit.setOrientation(qt.QSplitter.Horizontal)

        self.accountView = AccountValuesListView(plotsplit, node)
        self.connect(self.accountView, plot.plotControlToggle, self.togglePlot)
        self.connect(self.accountView, plot.plotControlColorSelected, self.colorPlot)

        self.plotFrame = plot.BasePlot(plotsplit)
        self.plotFrame.axisLabelFormat[plot.yRight] = ('f', 2, 2)
        self.plotFrame.enableAxis(plot.yLeft, False)
        self.plotZoomer = plot.BaseZoomer(self.plotFrame.canvas())

        self.executionsView = AccountExecutionsNode(mainsplit, node.executions)


        link.connect(self.accountView)
        link.connect(self.executionsView)
        self.refreshPlot()

    def slotAccount(self, event):
        """slotAccount(event) -> update the account plot

        """
        key = event.key
        value = event.value
        item = self.accountView.findItem(key, 0)
        if item:
            try:
                ison = item.isOn()
            except (AttributeError, ):
                pass
            else:
                if ison:
                    self.refreshPlot((item, ))

    def refreshPlot(self, items=None):
        """refreshPlot() -> draw plot lines

        """
        if not items:
            items = []
            for item in self.accountView.items():
                try:
                    ison = item.isOn()
                except (AttributeError, ):
                    continue
                else:
                    if ison:
                        items.append(item)

        for item in items:
            key = '%s' % item.text(0)
            history = [x[1] for x in self.node.history_data[key]]
            history = [x for x in history if isinstance(x, (float, int, ))]

            try:
                curvekey = self.plotFrame.curves[key]
                curve = self.plotFrame.curve(curvekey)
                curve.setEnabled(item.isOn())
                self.plotFrame.sequences[key] = history
                self.plotFrame.setCurveData(key)
            except (KeyError, ):
                pxm = item.pixmap(2)
                if pxm:
                    color = item.pixmapColor
                else:
                    color = 'black'
                style = base.PlotStyleMarker(color, axis='main right')
                try:
                    curve = self.plotFrame.initCurve(key, history, style)
                except (TypeError, ):
                    pass

        ## lame
        self.plotFrame.resetAxes()
        self.plotZoomer.setZoomBase()
        self.plotFrame.replot()

    def togglePlot(self, key, state):
        try:
            curveidx = self.plotFrame.curves[key]
        except (KeyError, ):
            self.refreshPlot((self.accountView.findItem(key, 0), ))
            return

        curve = self.plotFrame.curve(curveidx)
        curve.setEnabled(state)
        item = self.accountView.findItem(key, 0)
        self.refreshPlot((item, ))

    def colorPlot(self, key, color):
        try:
            curveidx = self.plotFrame.curves[key]
        except (IndexError, ):
            pass
        else:
            curve = self.plotFrame.curve(curveidx)
            curve.setPen(qt.QPen(color))
            item = self.accountView.findItem(key, 0)
            self.refreshPlot((item, ))


class AccountValueListViewItem(qt.QCheckListItem):
    """ AccountValueListViewItem() -> a list item that tweaks its parent

    Because QListViewItem does not inherit QObject, instances can't emit 
    signals.  This type has a quick-n-dirty solution whereby it calls a method
    on the parent list view widget directly.
    """
    def __init__(self, parent, text):
        typ = qt.QCheckListItem.CheckBox
        qt.QCheckListItem.__init__(self, parent, text, typ)

    def stateChange(self, state):
        """ stateChange(state) -> user has checked or unchecked the list item

        """
        try:
            self.listView().togglePlotItem(self, state)
        except (AttributeError, ):
            pass


class AccountValuesListView(BaseNodeListView):
    """AccountValuesListView(parent, node) -> broker account values list view

    """
    autoSelect = ('NetLiquidation', )
    focusAllColumns = True
    swatchSize = (12, 9)

    columnDefs = (
        ('Item', 200, alignLeft),
        ('Value', 100, alignLeft),
        ('Color', 50, alignCenter),
    )

    plotDefs = {
        'AvailableFunds' : qt.Qt.blue,
        'SettledCash' : qt.Qt.green,
        'EquityWithLoanValue' : qt.Qt.black,
        'NetLiquidation' : qt.Qt.red,
    }

    def __init__(self, parent, node):
        BaseNodeListView.__init__(self, parent, node)
        self.setupNode()
        self.setupSignals()

    def setupSignals(self):
        """setupSignals() -> connect up

        """
        self.connect(self, util.sigDoubleClicked, self.selectPlotColor)

    def setupNode(self):
        """ setupNode() -> build this object

        """
        self.clear()

        for k, v in self.node.current_data.items():
            try:
                throwaway = float(v)
                if int(throwaway) == -1:
                    raise TypeError('foo!')
            except (TypeError, ValueError, ):
                item = qt.QListViewItem(self, k, '%s' % (v, ))
            else:
                item = AccountValueListViewItem(self, k)
                item.setText(1, '%s' % v)
                pxm = qt.QPixmap(*self.swatchSize)
                color = self.plotDefs.get(k, qt.Qt.gray)
                pxm.fill(color)
                item.setPixmap(2, pxm)
                item.pixmapColor = color
                if k in self.plotDefs:
                    item.setOn(True)

    def togglePlotItem(self, item, state):
        """ togglePlotItem(item, state) -> list item callback to emit its state

        """
        key = '%s' % (item.text(0), )
        self.emit(plot.plotControlToggle, (key, state))

    def slotAccount(self, event):
        """slotAccount(event) -> update list view from broker data

        """
        key, value = event.key, event.value
        item = self.findItem(key, 0)
        if item:
            item.setText(1, str(value))
        else:
            item = qt.QCheckListItem(self, key, qt.QCheckListItem.CheckBox)
            item.setText(1, '%s' % value)

    def selectPlotColor(self, item):
        """selectPlotColor(item) -> select new plot line color

        """
        acolor = qt.QColor(item.pixmapColor)
        key = '%s' % item.text(0)
        ret = kdeui.KColorDialog.getColor(acolor, self)
        if ret == kdeui.KColorDialog.Accepted:
            item.pixmapColor = acolor
            item.pixmap(2).fill(acolor)
            self.emit(plot.plotControlColorSelected, (key, acolor, ))


class AccountExecutionsNode(BaseNodeListView):
    """AccountExecutionsNode(parent, node) ->

    """
    focusAllColumns = True
    sideMap = {'BOT': 'Bought', 'SLD' : 'Sold' }
    columnDefs = (
        ('Time', 90, alignLeft,),
        ('Symbol', 60, alignLeft,),

        ('Side', 60, alignLeft,),
        ('Size', 50, alignRight,),
        ('Price', 50, alignRight,),

        ('Exchange', 70, alignRight,),
        ('Perm Id', 100, alignRight,),
    )

    def __init__(self, parent, node):
        BaseNodeListView.__init__(self, parent, node)
        self.setupNode()

    def setupNode(self):
        """setupNode() -> build this object

        """
        for idx, seq in self.node.items():
            for timestamp, contract, execution in seq:
                self.setupItem(contract, execution)

    def setupItem(self, contract, execution):
        """setupItem(...) -> build a list item

        """
        item = qt.QListViewItem(self)
        item.setPixmap(1, util.loadIcon(contract.symbol.lower()))
        vals = self.valueList(contract, execution)
        for c, v in enumerate(vals):
            item.setText(c, v)

    def valueList(self, contract, execution):
        """valueList(...) -> list of values for a row item

        """
        items = [execution.time.split()[1],
                 contract.symbol,
                 self.sideMap.get(execution.side, execution.side),
                 execution.shares,
                 execution.price,
                 contract.exchange,
                 execution.perm_id, ]
        return ['%s' % item for item in items]

    def slotExecutionDetails(self, event):
        """slotExecutionDetails(event) ->
    
        """
        self.setupItem(event.contract, event.details)


class AccountPortfolioNode(BaseNodeListView):
    """AccountPortfolioNode(parent, node) -> displays positions

    """
    iconName = 'appointment'

    focusAllColumns = True
    columnDefs = (
        ('Symbol', 60, alignLeft,),
        ('Position', 80, alignRight,),
        ('Price', 80, alignRight,),
        ('Value', 80, alignRight,),
    )

    def __init__(self, parent, node):
        BaseNodeListView.__init__(self, parent, node)
        for sym, pos in node.items():
            positems = [pos.position, pos.marketprice, pos.marketvalue]
            args = [self, sym, ] + [str(s) for s in positems]
            item = qt.QListViewItem(*args)
            item.setPixmap(0, util.loadIcon(sym.lower()))
        self.connect(self, util.sigDoubleClicked, self.handleShowTicker)


    def handleShowTicker(self, item):
        """handleShowTicker(item) -> display a ticker node in separate window

        """
        self.emit(util.sigViewTicker, (item.text(0), item.pixmap(0),))

    def slotPortfolio(self, evt):
        """slotPortfolio(event) -> update the list view item

        """
        contract, position, market_price, market_value = \
            evt.contract, evt.position, evt.market_price, evt.market_value

        item = self.findItem(contract.symbol, 0) # ExactMatch | CaseSensitive
        if not item:
            args = [self, contract.symbol, ] 
            args += [str(s) for s in [position, market_price, market_value]]
            item = qt.QListViewItem(*args)
            item.setPixmap(0, util.loadIcon(contract.symbol.lower()))
        else:
            args = [position, market_price, market_value]
            for col, txt in enumerate([str(s) for s in args]):
                item.setText(col+1, txt)
