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
""" profit.widgets.node -> widgets to display session objects


"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'tickernode.py,v 0.5 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.5',
}

import qt

import kdecore
import kdeui

import profit.device.util as util
import profit.device.widgets.plot as plot
import profit.device.widgets.nodebase as nodebase
import profit.device.dialogs.order as ordersdialog
import profit.lib.base as base


##-----------------------------------------------------------------------------
##
## Useful Constants
##
##-----------------------------------------------------------------------------
alignCenter = qt.Qt.AlignCenter
alignLeft = qt.Qt.AlignLeft
alignRight = qt.Qt.AlignRight

i18n = kdecore.i18n


shortStr = nodebase.shortStr
BaseNodeWidget = nodebase.BaseNodeWidget
BaseNodeTabWidget = nodebase.BaseNodeTabWidget
BaseNodeListView = nodebase.BaseNodeListView


##-------------------------------------------------------------------------
##
## Ticker Supervisor Node and related widgets
##
##-------------------------------------------------------------------------
class TickerSupervisorNode(BaseNodeListView):
    """ TickerSupervisorNode(...) -> a ticker supervisor as a list view

    """
    iconName = 'exec'
    focusAllColumns = True
    columnDefs = (
        ('Symbol', -1, alignLeft),
        ('Position', 60, alignRight),
        ('Value', 80, alignRight),
    )

    def __init__(self, parent, node):
        BaseNodeListView.__init__(self, parent, node)
        self.priceSizeColumn = {}
        self.columnPriceSize = {1 : 'position', 2 : 'market_value' }

        ## build the columns based on the price types available
        pricesizes = base.PriceSizeLookup.items()
        pricesizes.sort()
        for pskey, pslabel in pricesizes:
            self.priceSizeColumn[pskey] = colidx = self.addColumn(pslabel)
            self.columnPriceSize[colidx] = pskey
            self.setColumnAlignment(colidx, alignRight)

        ## build a list view item for every ticker
        for (tid, tsym), tobj in node.items():
            item = TickerSupervisorListItem(self, tobj)
            for key, value in tobj.current_data.items():
                if key in base.PriceTypes.values():
                    valuefs = '%.2f'
                else:
                    valuefs = '%s'
                try:
                    item.setText(self.priceSizeColumn[key], valuefs % value)
                except (KeyError, ):
                    pass

        sigtick = util.sigViewTickerItem
        self.connect(self, sigtick, qt.qApp.mainWidget(), sigtick)
        self.connect(self, util.sigListContext, self.handleContextMenu)
        self.connect(self, util.sigDoubleClicked, self.showChart)

    def slotTicker(self, event, floats=base.PriceTypes.values()):
        """ slotTicker(event) -> set list view item with new data

        """
        item = self.findItem(self.node[event.ticker_id].symbol, 0)
        if item:
            valuefs = '%s'
            field = event.field
            if field in floats:
                valuefs = '%.2f'
            item.setText(self.priceSizeColumn[field], valuefs % event.value)

    def slotPortfolio(self, event):
        """ slotPortfolio(event) -> update the position column

        """
        item = self.findItem(event.contract.symbol, 0)
        if item:
            item.setText(1, str(event.position))
            item.setText(2, '%.2f' % event.market_value)

    def handleContextMenu(self, item, pos, col):
        """ handleContextMenu(item, pos, col) -> display a context menu

        """
        self.context = item
        title = '%s' % (item.ticker.symbol, )
        pop = kdeui.KPopupMenu(self)
        pop.insertTitle(item.pixmap(0), title)

        position = item.ticker.current_data.get('position', 0)
        if position:
            label = i18n('&Close %s shares...' % (abs(position), ))
            pop.insertItem(label, self.closePosition)

        pop.insertSeparator()
        pop.insertItem(util.loadIconSet('chart'), i18n('&Chart...'), 
                       self.showChart)
        pop.insertItem(util.loadIconSet('kcalc'), i18n('&Order...'), 
                       self.handleOrderDialog)
        pop.insertSeparator()

        setups = enumerate(util.TickerUrl.request_defs)
        handler = self.requestBrowser
        for key, (label, icon, url) in setups:
            item = pop.insertItem(util.loadIconSet(icon), i18n(label), handler)
            pop.setItemParameter(item, key)

        pop.popup(pos)

    def requestBrowser(self, param):
        """ requestBrowser(param) -> invoke a browser with a page for a ticker

        """
        sym = str(self.context.text(0))
        req = util.TickerUrl(param, sym)
        util.invokeBrowser(req.url)

    def showChart(self, item):
        """ showChart() -> popup slot to display ticker chart

        """
        item = self.selectedItem()
        self.emit(util.sigViewTickerItem, (item.ticker, ))

    def closePosition(self):
        """ closePosition() -> popup slot to close position via order dialog

        """
        try:
            position_column = 1
            shares = self.context.text(position_column)
            shares = int(str(shares))
        except (IndexError, TypeError, ):
            return

        if not shares:
            return

        absshares = abs(shares)
        self.handleOrderDialog(shares=absshares, direction=shares/absshares)

    def handleOrderDialog(self, **kwds):
        """ handleOrderDialog() -> popup slot to display an order dialog

        """
        dlg = ordersdialog.OrderDialog(self)
        dlg.configFromSymView(self)

        shares = kwds.get('shares', 100)
        dlg.quantitySpin.setValue(shares)

        direction = kwds.get('direction', 0)
        if direction == -1:
            dlg.actionCombo.setCurrentItem(0)
        elif direction == 1:
            dlg.actionCombo.setCurrentItem(1)

        self.connect(dlg, util.sigSubmitOrder, qt.qApp.mainWidget().placeOrder)
        dlg.show()


class TickerSupervisorListItem(qt.QListViewItem):
    """ TickerSupervisorListItem(...) -> list item for a ticker supervisor node

    """
    def __init__(self, parent, ticker):
        fmtflt, zeroflt = '%.2f', 0.0
        args = (
            '%s' % ticker.current_data.get('position', 0),
            fmtflt % ticker.current_data.get('market_value', zeroflt),
            fmtflt % ticker.current_data.get(base.PriceTypes.Ask, zeroflt),
            fmtflt % ticker.current_data.get(base.PriceTypes.Bid, zeroflt),
            fmtflt % ticker.current_data.get(base.PriceTypes.Last, zeroflt),
        )
        args = (self, parent, ticker.symbol, ) + args
        qt.QListViewItem.__init__(*args)

        pxm = util.loadIcon(ticker.symbol.lower())
        self.setPixmap(0, pxm)

        self.ticker = ticker
        self.current = ticker.current_data
        self.previous = ticker.previous_data

        ## need to handle an updated config as this is static
        config = util.appConfig(util.groups.misc)
        self.useColor = config.readNumEntry(util.keys.colorTickers, 
                                             util.defaults.colorTickers)

    def paintCell(self, p, cg, column, width, align,
                  black=qt.Qt.black,
                  red=qt.Qt.red,
                  green=qt.Qt.darkGreen,
                  blue=qt.Qt.blue):
        """ paintCell(...) -> add some red/green logic to a cell before painting

        """
        if self.useColor:
            try:
                listview = self.listView()
                pricesize = listview.columnPriceSize[column]
                current = self.current[pricesize]
                previous = self.previous[pricesize]
            except (Exception, ):
                qt.QListViewItem.paintCell(self, p, cg, column, width, align)
                return
    
            cg = qt.QColorGroup(cg)
            if previous == 0:
                color = black
            elif current > previous:
                color = green
            elif current < previous:
                color = red
            else:
                color = blue

            cg.setColor(qt.QColorGroup.Text, color)

        qt.QListViewItem.paintCell(self, p, cg, column, width, align)


class TechnicalTickerNode(BaseNodeTabWidget):
    """ TechnicalTickerNode(...) -> node for displaying a technical ticker

    """
    iconName = 'newtodo'
    defaultMargin = 4
    includePriceTypes = (
        base.PriceTypes.Ask,
        base.PriceTypes.Bid,
        base.PriceTypes.Last, 
    )

    def __init__(self, parent, node):
        BaseNodeTabWidget.__init__(self, parent)
        self.symbol, self.id = node.symbol, node.id
        self.iconName = self.symbol
        self.plotPages = plotpages = {}
        self.tablePages = tablepages = {}
        self.partials = partials = []

        ## build a page for every price or size type in the ticker.series
        nodeitems = node.series.items()
        nodeitems.sort()
        partial = base.PartialCall

        for seriesps, series in nodeitems:
            if seriesps in self.includePriceTypes:
                page = plot.SeriesPlot(self, series)
                page.price_size_key = seriesps
                self.addTab(page, "%s" % base.PriceSizeLookup[seriesps])
                plotpages[seriesps] = page

                if seriesps == base.PriceTypes.Bid:
                    self.showPage(page)

                if seriesps in node.strategy_keys:
                    ticker_data = TickerSeriesDataNode(self, node, seriesps)
                    lbl = "%s Data" % base.PriceSizeLookup[seriesps]
                    self.addTab(ticker_data, lbl)
                    tablepages[seriesps] = ticker_data

                    ## connect the ticker_data page to the corresponding plot 
                    ## page double-click

                    func = partial(self.showTickerData, view=ticker_data)
                    partials.append(func)
                    for pp in plotpages.values():
                        for aplot in pp.plots.values():
                            self.connect(aplot, plot.plotCtrlClick, func)

    def showTickerData(self, xpos, view):
        """ showTickerData(xpos, view) -> jump to some ticker data

        """
        xpos = int(round(xpos))
        try:
            item = view.findItem('%s' % xpos, 0)
        except (KeyError, ):
            pass
        else:
            view.clearSelection()
            view.setSelected(item, True)
            view.ensureItemVisible(item)
            self.showPage(view)

    def slotTicker(self, event):
        """ slotTicker(event) -> set the cell text

        """
        tid, field, value = event.ticker_id, event.field, event.value
        if tid != self.id:
            return

        try:
            page = self.pageItems()[base.PriceSizeLookup[field]]
            page.redrawPlots()
        except (KeyError, ):
            pass

    def pageItems(self):
        """pageItems() -> a goofy way to get the page for a plot

        """
        try:
            indexes = range(self.count()-1)
        except (RuntimeError, ):
            ## wtf??
            return {}

        pages = [self.page(i) for i in indexes]
        labels = [str(s) for s in [self.label(i) for i in indexes]]
        return dict(zip(labels, pages))


class TickerSeriesDataNode(BaseNodeListView):
    """ TickerSeriesDataNode() -> list view of a series and its indexes

    """
    focusAllColumns = True
    sorting = (-1, )

    def __init__(self, parent, node, key):
        series = node.series[key]
        seqs = [(base.PriceSizeLookup[key], series), ]
        seqs += series.index_map.items()
        start = [('Series', -1, alignRight), ]
        middle = [(s, -1, alignRight) for s, seq in seqs]

        self.columnDefs = start + middle
        BaseNodeListView.__init__(self, parent, node)

        for i in range(len(series)):
            item = qt.QListViewItem(self, '%s' % i)
            for colidx, seq in enumerate(seqs):
                try:
                    v = seq[1][i] or ''
                except (IndexError, ):
                    v = seq
                try:
                    v = '%2.6f' % v
                except (TypeError, ):
                    pass
                item.setText(colidx+1, '%s' % (v, ))


class TickerPriceSizeMapNode(BaseNodeListView):
    """ TickerPriceSizeMapNode(parent, node) -> displays a price size mapping

    """
    focusAllColumns = True
    columnDefs = (
        ('Type', 100, alignLeft,),
        ('Value', 80, alignRight,),
    )

    def __init__(self, parent, node):
        BaseNodeListView.__init__(self, parent, node)
        for k, v in node.items():
            qt.QListViewItem(self, base.PriceSizeLookup[k], shortStr(v))
