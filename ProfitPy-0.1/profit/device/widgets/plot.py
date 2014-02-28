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
""" Plot widgets suitable for displaying ticker series data

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'plot.py,v 0.5 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.5',
}

import qt
import qwt

import kdecore
import kdeui

import profit.device.util as util

import profit.lib.base as base


##-----------------------------------------------------------------------------
##
## Useful Constants
##
##-----------------------------------------------------------------------------
plotControlColorSelected = qt.PYSIGNAL('PlotControlColorSelected')
plotControlToggle = qt.PYSIGNAL('PlotControlToggle')
plotRescaled = qt.PYSIGNAL('PlotRescaled')
plotCtrlClick = qt.PYSIGNAL('PlotControlClicked')

xBottom, xTop = qwt.QwtPlot.xBottom, qwt.QwtPlot.xTop
yLeft, yRight = qwt.QwtPlot.yLeft, qwt.QwtPlot.yRight

yAxisMap = {
    'left' : yLeft,
    'right' : yRight,
}

xAxisMap = {
    'top' : xTop,
    'bottom' : xBottom,
}

curveStyleMap = {
    'stick' : qwt.QwtCurve.Sticks, 
    'nocurve' : qwt.QwtCurve.NoCurve,
    'lines' : qwt.QwtCurve.Lines, 
    'steps' : qwt.QwtCurve.Steps,
    'dots' : qwt.QwtCurve.Dots, 
    'spline' : qwt.QwtCurve.Spline,
}

lineStyleMap = {
    'noline' : qt.Qt.NoPen, 
    'solid' : qt.Qt.SolidLine, 
    'dash' : qt.Qt.DashLine, 
    'dot' : qt.Qt.DotLine, 
    'dashdot' : qt.Qt.DashDotLine, 
    'dashdotdot' : qt.Qt.DashDotDotLine, 
}


def getCurveType(key, default=None):
    """ getCurveType(key, default=None) -> get a curve type

        This is wrapped up in a function so that the dictionary can be defined 
        before the actual types are defined (below).
    """
    types = {
        'trend' : TrendCurve, 
        'strategy' : StrategyCurve,
    }
    return types.get(key, default)


def getSequenceData(sequence):
    """ getSequenceData(sequence) -> Y and derived X data of a sequence

        This function eliminates None values from the sequence and assumes any
        None values are on the left of the sequence.  The X sequence is adjusted
        to account for any trimmed values.
    """
    seqx = range(len(sequence))
    seqy = [n for n in sequence if n is not None]
    seqx = seqx[-len(seqy):]
    return seqx, seqy


def getPenStyle(style):
    """ getPenStyle(style) -> returns a pen based on the style

    """
    color = qt.QColor(style.color)
    width = style.width
    linestyle = lineStyleMap.get(style.line_style, qt.Qt.SolidLine)
    return qt.QPen(color, width, linestyle)


def getCurveStyle(style, default=qwt.QwtCurve.Lines):
    """ getCurveStyle(style, default=Lines) -> returns a curve style

    """
    return curveStyleMap.get(style.curve_style, default)


def getPlotStyle(sequence, default='#aa0000'):
    """ getPlotStyle(seq) -> returns sequence.plot_style; builds it if necessary

    """
    try:
        plotstyle = sequence.plot_style
    except (AttributeError, ):
        base.set_plot_style(sequence, default)
        plotstyle = sequence.plot_style
    return plotstyle


##-----------------------------------------------------------------------------
##
## Plot Widgets
##
##-----------------------------------------------------------------------------
class BaseZoomer(qwt.QwtPlotZoomer):
    """ BaseZoomer(...) -> basic qwt plot zoomer

    """

    ## QwtPlotZoomer ctor is a bit awkward - it requires the canvas last.
    ## This implementation simplifies usage for clients at the risk of 
    ## a bit of confusion.
    def __init__(self, canvas, xAxis=xBottom, yAxis=yLeft,
                 selectionFlags=qwt.QwtPicker.DragSelection,
                 cursorLabelMode=qwt.QwtPicker.ActiveOnly,
                 name='foo'):
        qwt.QwtPlotZoomer.__init__(self, xAxis, yAxis, selectionFlags, 
                                   cursorLabelMode, canvas, name)
        self.setCursorLabelPen(qt.QPen(qt.Qt.white))
        ## not quite, but this does adjust the color
        self.setRubberBandPen(qt.QPen(qt.Qt.white))


    def rescale(self):
        """ rescale() -> rescales the zoomer and emits a signal when its done

        """
        qwt.QwtPlotZoomer.rescale(self)
        self.emit(plotRescaled, ())


class BasePlot(qwt.QwtPlot):
    """ BasePlot(parent) -> basic qwt plot

        This class implements the Template Pattern; subclasses may redefine 
        methods to customize axes, and grids construction.
    """
    axisLabelFormat = {}
    backgroundColor = '#c0c0c0'
    canvasMargin = 0

    majorGrid = ('#aaaaaa', 0, qt.Qt.SolidLine)
    minorGrid = ('#aaaaaa', 0, qt.Qt.DotLine)
    minimumSize = (100, 50)

    def __init__(self, parent):
        qwt.QwtPlot.__init__(self, parent)
        self.initAttributes()
        self.initAxes()
        self.initCanvas()
        self.initGrids()
        self.initSignals()

    def initAttributes(self):
        """ initAttributes() -> initialize the plot data attributes

        """
        self.curves = {}
        self.sequences = {}
        self.extents = {
            yLeft : [], yRight : [], xTop : [], xBottom : [],
        }

    def initAxes(self):
        """ initAxes() -> initialize the plot axes

            Note that this implementation does not enable the x axes.
        """
        for axis in yAxisMap.values():
            self.enableAxis(axis)

    def initCanvas(self):
        """ initCanvas() -> initialize the plot canvas

        """
        self.canvas().setMouseTracking(True)
        self.setMinimumSize(qt.QSize(*self.minimumSize))

        layout = self.plotLayout()
        layout.setCanvasMargin(self.canvasMargin)
        layout.setAlignCanvasToScales(True)
        self.setCanvasBackground(qt.QColor(self.backgroundColor))

    def initCurve(self, key, seq, style):
        """ initCurve(key, seq, style) -> initialize a curve with key and style

        """
        self.sequences[key] = seq
        side = yAxisMap.get(style.yaxis, yLeft)
        customtype = getCurveType(style.curve_type)

        if customtype is None:
            curveidx = self.insertCurve(key, xBottom, side)
            curve = self.curve(curveidx)
        else:
            curve = customtype(self, seq)
            curve.setAxis(xBottom, side)
            curveidx = self.insertCurve(curve)
            self.setCurveStyle(curveidx, qwt.QwtCurve.UserCurve)

        if style.curve_style is not None:
            curve.setStyle(getCurveStyle(style))

        curve.setPen(getPenStyle(style))
        curve.setEnabled(style.init_display)

        self.curves[key] = curveidx
        self.setCurveData(key)
        return curve

    def initGrids(self):
        """ initGrids() -> initialize the plot grids

        """
        griddefs = (
            (self.majorGrid, self.setGridMajPen),
            (self.minorGrid, self.setGridMinPen),
        )

        for (color, width, line), func in griddefs:
            func(qt.QPen(qt.QColor(color), width, line))

        for func in (self.enableGridXMin, self.enableGridYMin):
            func()

    def initSignals(self):
        """ initSignals() -> setup some signals

        """
        self.connect(self, util.sigPlotMouseReleased, self.plotMouseReleased)

    def plotMouseReleased(self, event):
        """ plotMouseReleased(event) -> mouse released on the plot widget

        """
        isctrl = event.stateAfter() == qt.QEvent.ControlButton
        isleft = event.stateAfter() == qt.QEvent.ControlButton 
        if isctrl and isleft:
            args = (self.invTransform(xBottom, event.x()), )
            self.emit(plotCtrlClick, args)

    def resetAxes(self):
        """ resetAxes() -> reset all four axes

        """
        for axis in yAxisMap.values() + xAxisMap.values():
            self.resetAxisScale(axis)

    def resetAxisScale(self, axis):
        """ resetAxisScale(axis) -> reset axis scale; subclasses should override

        """
        self.setAxisAutoScale(axis)
        self.resetAxisScaleDraw(axis)

    def resetAxisScaleDraw(self, axis):
        """ resetAxisScaleDraw(axis) -> reset the axis scale draw

        """
        scaledraw = self.axisScaleDraw(axis)
        format = self.axisLabelFormat.get(axis, ('g', 4, 4))
        scaledraw.setLabelFormat(*format)

    def setCurveData(self, key):
        """ setCurveData(key) -> set curve data for curve named by key

        """
        curve = self.curve(self.curves[key])
        data = self.sequences[key]

        try:
            xdata, ydata = getSequenceData(data)
        except (ValueError, TypeError, ):
            pass
        else:
            curve.setData(xdata, ydata)

        try:
            minx, maxx = min(xdata), max(xdata)
            miny, maxy = min(ydata), max(ydata)
            extents = ((minx, maxx), (miny, maxy), )
            self.extents[curve.yAxis()].append(extents)
        except (NameError, ValueError, ):
            pass


class MainPlot(BasePlot):
    """ MainPlot(parent) -> plot for main series and associated indexes

    """
    def resetAxisScale(self, axis):
        """ resetAxisScale(axis) -> forces right axis scale to be funky

            This is a total hack -- a better approach would be to have the trend
            line as a user curve that displays itself along the lower bound of the
            right axis.  But a user curve would be slow and difficult.
        """
        if axis == yRight:
            self.setAxisScale(axis, -2.0, 100.0)
            self.resetAxisScaleDraw(axis)
        else:
            BasePlot.resetAxisScale(self, axis)


class OscillatorPlot(BasePlot):
    """ OscillatorPlot(parent) -> plot for oscillator-type indexes

    """
    yMarkerColor = '#909090'
    yMarkerPos = 0.0

    def initAxes(self):
        """ initAxes() -> initialize the axes and a y axis marker

        """
        BasePlot.initAxes(self)
        self.yMarker = ymarker = self.insertLineMarker('', yLeft)
        self.setMarkerPen(ymarker, qt.QPen(qt.QColor(self.yMarkerColor)))
        self.setMarkerYPos(ymarker, self.yMarkerPos)

    def initCanvas(self):
        """ initCanvas() -> initialize the canvas and disable the drag outline

        """
        BasePlot.initCanvas(self)
        self.enableOutline(False)

    def resetAxisScale(self, axis):
        """ resetAxisScale(axis) -> reset the axis scale to the y values extents

        """
        if axis in yAxisMap.values():
            extents = [ex[1] for ex in self.extents[axis]]
            try:
                miny = min([yval[0] for yval in extents])
                maxy = max([yval[1] for yval in extents])
                maxy = max((abs(miny), abs(maxy)))
            except (ValueError, ):
                pass
            else:
                self.setAxisScale(axis, -maxy, maxy)
            self.resetAxisScaleDraw(axis)
        else:
            BasePlot.resetAxisScale(self, axis)


##-----------------------------------------------------------------------------
##
## Series Plot
##
##-----------------------------------------------------------------------------
class SeriesPlot(qt.QSplitter):
    """ SeriesPlot(parent, node) -> displays a series plot and tools for it

    """
    seriesKey = 'Series'
    mainKey = 'main'
    oscKey = 'osc'
    plotKeys = (mainKey, oscKey, )

    gridSpacing = 2
    gridMargin = 2

    trackingSides = (xBottom, yLeft, yRight, )

    def __init__(self, parent, series):
        qt.QSplitter.__init__(self, qt.Qt.Horizontal, parent)
        self.initAttributes(series)
        self.initControls()
        self.initPlots()
        self.initCurves()
        self.initSplitters()
        self.initSignals()
        self.redrawPlots()

    def initAttributes(self, series):
        """ initAttributes() -> initialize the instance attributes

        """
        self.series = series

        self.plots = {}
        self.zooms = {}

        self.curves = {}
        self.curveTools = {}
        self.pointLabels = dict([(key, {}) for key in self.plotKeys])
        self.partials = {}

    def initControls(self):
        """ initControls() -> create the plot controls

        """
        series = self.series
        connect = self.connect
        labels = self.pointLabels

        self.controlsBox = controlsbox = qt.QVBox(self)
        self.controlsGrid = controlsgrid = qt.QGrid(2, controlsbox)
        self.plotSplitter = qt.QSplitter(qt.Qt.Vertical, self)

        controlsgrid.setSpacing(self.gridSpacing)
        controlsgrid.setMargin(self.gridMargin)

        smap = [(self.seriesKey, series), ] + series.index_map.items()
        smap = [(k, v) for k, v in smap if hasattr(v, 'plot_style')]
        for key, seq in smap:
            style = getPlotStyle(seq)
            curve_check = CurveToggleCheckBox(controlsgrid, key)
            curve_color = CurveColorPickButton(controlsgrid, style.color, key)
            connect(curve_check, plotControlToggle, self.toggleCurveVisibility)
            connect(curve_color, plotControlColorSelected, self.setCurveColor)
            self.curveTools[key] = (curve_check, curve_color)

        for key in self.plotKeys:
            for side in self.trackingSides:
                labels[key][side] = TrackingPointLabel(controlsbox, side)

        lastlabel = qt.QFrame(controlsbox)
        controlsbox.setStretchFactor(lastlabel, 100)
        self.series_map = dict(smap)

    def initPlots(self):
        """ initPlots() -> create the plot widgets and zoomers for them

        """
        for key, plottype in zip(self.plotKeys, (MainPlot, OscillatorPlot)):
            self.plots[key] = plot = plottype(self.plotSplitter)
            self.zooms[key] = BaseZoomer(plot.canvas())

    def initCurves(self):
        """ initCurves() -> add curves to the appropriate plot

        """
        curves = self.curves
        tools = self.curveTools

        for key, series in self.series_map.items():
            style = series.plot_style
            initializer = self.plots[style.pkey].initCurve
            curves[key] = initializer(key, series, style)
            tools[key][0].setChecked(style.init_display)

    def initSplitters(self):
        """ initSplitters() -> configure splitter layouts and behaviors

        """
        opaquedefs = (self, self.plotSplitter, )
        for splitter in opaquedefs:
            splitter.setOpaqueResize(True)

        resizedefs = (
            (self.controlsBox, qt.QSplitter.KeepSize),
            (self.plotSplitter, qt.QSplitter.Stretch),
        )
        for wid, mod in resizedefs:
            self.setResizeMode(wid, mod)

        height = self.size().height()
        self.plotSplitter.setSizes([height*0.65, height*0.35])

    def initSignals(self):
        """ initSignals() -> do the signal to slot dance

        """
        connect = self.connect
        partials = self.partials

        connect(self.zooms[self.mainKey], plotRescaled, self.syncPlotZoom)

        for key, plot in self.plots.items():
            partials[key] = partial = base.PartialCall(self.showMousePoint, key=key)
            connect(plot, util.sigPlotMouseMoved, partial)

    def setCurveColor(self, key, color):
        """ setCurveColor(key, color) -> handle a series color change

        """
        curve = self.curves[str(key)]
        curve.setPen(qt.QPen(color))
        curve.parentPlot().replot()

    def toggleCurveVisibility(self, key, show):
        """ toggleCurveVisibility(key, show) -> handle a series select toggle

        """
        curve = self.curves[str(key)]
        curve.setEnabled(show)
        curve.parentPlot().replot()

    def syncPlotZoom(self):
        """ syncPlotZoom() -> sync osc plot zoom to main plot zoom

        """
        osczoom = self.zooms[self.oscKey]
        srcrect = self.zooms[self.mainKey].zoomRect()
        targetrect = osczoom.zoomRect()

        targetrect.setX1(srcrect.x1())
        targetrect.setX2(srcrect.x2())

        osczoom.zoom(targetrect)

    def redrawPlots(self):
        """ redrawPlots() -> redraw plot curves based on current config 

        """
        for key, plot in self.plots.items():
            plot.resetAxes()
            self.zooms[key].setZoomBase()

            for curvekey in plot.curves.keys():
                plot.setCurveData(curvekey)

            plot.replot()

    def showMousePoint(self, event, key=None):
        """ showMousePoint(event, ...) -> track the point to the status label

        """
        pos = event.pos()
        xpos, ypos = pos.x(), pos.y()
        trans = self.plots[key].invTransform

        for side, val in zip(self.trackingSides, (xpos, ypos, ypos)):
            val = trans(side, val)
            label = self.pointLabels[key][side]
            label.setText(val)


##-----------------------------------------------------------------------------
##
## User Curves
##
##-----------------------------------------------------------------------------
class SeriesCurve(qwt.QwtPlotCurve):
    """ SeriesCurve(parent, series) -> a plot curve to display a series

    """
    instances_map = {}

    def __init__(self, parent, series):
        qwt.QwtPlotCurve.__init__(self, parent)
        self.series = series
        self.markers = []


class StrategyCurve(SeriesCurve):
    """ StrategyCurve(parent, series) -> series curve for drawing a strategy

    """
    Long = base.Directions.Long 
    Short = base.Directions.Short 
    Rev = 1
    NoRev = 0

    signalRes = {
        (Long, NoRev): \
            (qwt.QwtSymbol.UTriangle, 
             qt.QBrush(qt.Qt.green, qt.Qt.SolidPattern), 
             qt.QPen(qt.QColor('white')), qt.QSize(10, 10)),

        (Long, Rev): \
            (qwt.QwtSymbol.UTriangle, 
             qt.QBrush(qt.Qt.green, qt.Qt.SolidPattern), 
             qt.QPen(qt.QColor('black')), qt.QSize(10, 10)),

        (Short, NoRev) : \
            (qwt.QwtSymbol.DTriangle, 
             qt.QBrush(qt.Qt.red, qt.Qt.SolidPattern), 
             qt.QPen(qt.QColor('white')), qt.QSize(10, 10)),

        (Short, Rev) : \
            (qwt.QwtSymbol.DTriangle, 
             qt.QBrush(qt.Qt.red, qt.Qt.SolidPattern), 
             qt.QPen(qt.QColor('black')), qt.QSize(10, 10)),
    }

    def draw(self, painter, xMap, yMap, start, stop):
        """ draw(...) -> called to draw the curve

        """
        plot = self.parentPlot()
        records = [record[0:4] for record in self.series.history]

        for xpos, ypos, sig, rev in records:
            if (not sig) and (not rev):
                continue
            marker = qwt.QwtPlotMarker(plot)
            markerid = plot.insertMarker(marker)
            self.markers.append(marker)
            plot.setMarkerPos(markerid, xpos, ypos)
            sigsym = qwt.QwtSymbol(*self.signalRes[(sig, rev)])
            plot.setMarkerSymbol(markerid, sigsym)

            # brain dead and/or broken
            if 0:
                gridmarkerpen = qt.QPen(
                    qt.QColor(BasePlot.majorGrid[0]), 0, qt.Qt.SolidLine)
                ## horizontal line
                symyline = plot.insertLineMarker("", qwt.QwtPlot.yLeft)
                plot.setMarkerPen(symyline, gridmarkerpen)
                plot.setMarkerYPos(symyline, ypos)
                self.markers.append(plot.marker(symyline))
                ## vertical line
                symxline = plot.insertLineMarker("", qwt.QwtPlot.xTop)
                plot.setMarkerPen(symxline, gridmarkerpen)
                plot.setMarkerXPos(symxline, xpos)
                self.markers.append(plot.marker(symxline))

    def setEnabled(self, checked):
        """ setEnabled(checked) -> toggle this curve and its markers

        """
        for marker in self.markers:
            marker.setEnabled(checked)
        qwt.QwtPlotCurve.setEnabled(self, checked)


class TrendCurve(SeriesCurve):
    """ TrendCurve(parent) -> displays trend bars

    """
    penWith = 2
    pens = {
        -1 : qt.QPen(qt.Qt.darkBlue, penWith),
         0 : qt.QPen(qt.Qt.darkGray, penWith, qt.Qt.NoPen),
        +1 : qt.QPen(qt.Qt.darkGreen, penWith)
    }

    def draw(self, painter, xMap, yMap, start, stop):
        """ draw(...) -> called to draw the curve

        """
        pens = self.pens
        for i in range(self.dataSize()):
            v = self.y(i)
            if v:
                painter.setPen(pens[abs(v) / v])
            else:
                painter.setPen(pens[0])

            xpos = self.x(i)
            xpos1 = xMap.transform(xpos)
            xpos2 = xMap.transform(xpos+1)
            ypos = yMap.transform(v)
            painter.drawLine(xpos1, ypos, xpos2, ypos)


##-----------------------------------------------------------------------------
##
## Plot Controls
##
##-----------------------------------------------------------------------------
class CurveToggleCheckBox(qt.QCheckBox):
    """ CurveToggleCheckBox(parent) -> check box toggle to show or hide a curve

    """
    def __init__(self, parent, key):
        qt.QCheckBox.__init__(self, parent)
        self.key = key
        self.connect(self, util.sigToggled, self.setToggled)

    def setToggled(self, checked):
        """ setToggled(checked) -> re-emit the toggle bool

        """
        self.emit(plotControlToggle, (self.key, checked, ))


class CurveColorPickButton(qt.QToolButton):
    """ CurveColorPickButton(parent, color) -> color selection button widget

    """
    def __init__(self, parent, color, key, swatchsize=(12, 8)):
        qt.QToolButton.__init__(self, parent)
        self.color = qt.QColor(color)
        self.key = key
        self.swatchSize = swatchsize

        self.setTextLabel(key)
        self.setUsesTextLabel(True)
        self.setTextPosition(qt.QToolButton.Right)
        self.setAutoRaise(True)
        self.setPaletteBackgroundColor(parent.paletteBackgroundColor())

        self.setColorPixmap()
        self.connect(self, util.sigClicked, self.selectColor)

    def setColorPixmap(self):
        """ setColorPixmap() -> set a pixmap swatch for this button

        """
        pxm = qt.QPixmap(*self.swatchSize)
        pxm.fill(self.color)
        self.setPixmap(pxm)

    def selectColor(self):
        """ selectColor() -> show the color dialog and emit a color selection

        """
        args = ()
        acolor = qt.QColor(self.color)
        if kdecore.KApplication.kApplication():
            result = kdeui.KColorDialog.getColor(acolor, self)
            if result == kdeui.KColorDialog.Accepted:
                self.color = acolor
                args = (self.key, self.color, )
        else:
            result = qt.QColorDialog.getColor(acolor, self)
            if result and result.isValid():
                self.color = result
                args = (self.key, self.color, )
        if args:
            self.setColorPixmap()
            self.emit(plotControlColorSelected, args)


class TrackingPointLabel(qt.QLabel):
    """ TrackingPointLabel(parent, ...) -> label for mouse tracking point

    """
    formats = {
        xBottom : 'xB: %3.f',
        xTop : 'xT: %3.f',
        yLeft : 'yL: %3.3f',
        yRight : 'yR: %3.3f',
    }

    def __init__(self, parent, side, margin=3):
        qt.QLabel.__init__(self, parent)
        self.format = self.formats[side]
        self.setMargin(margin)

    def setText(self, value):
        """ setText(value) -> set the text with local formatting

        """
        qt.QLabel.setText(self, self.format % value)
