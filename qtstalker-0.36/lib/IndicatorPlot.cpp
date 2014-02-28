/*
 *  Qtstalker stock charter
 *
 *  Copyright (C) 2001-2007 Stefan S. Stratigakos
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
 *  USA.
 */

#include "IndicatorPlot.h"
#include "DbPlugin.h"
#include "PrefDialog.h"
#include "HelpWindow.h"
#include "RcFile.h"
#include <qpainter.h>
#include <qpen.h>
#include <qpoint.h>
#include <qpointarray.h>
#include <qcursor.h>
#include <math.h>
#include <qprinter.h>
#include <qpaintdevicemetrics.h>
#include <qimage.h>
#include <qmessagebox.h>
#include <qinputdialog.h>
#include <qdir.h>
		
// only for fabs()
#include <math.h>
		
#include "../pics/indicator.xpm"
#include "../pics/edit.xpm"
#include "../pics/delete.xpm"
#include "../pics/co.xpm"
#include "../pics/print.xpm"
#include "../pics/loggrid.xpm"
#include "../pics/date.xpm"
#include "../pics/buyarrow.xpm"
#include "../pics/arc.xpm"
#include "../pics/fib.xpm"
#include "../pics/horizontal.xpm"
#include "../pics/sellarrow.xpm"
#include "../pics/text.xpm"
#include "../pics/trend.xpm"
#include "../pics/vertical.xpm"
#include "../pics/help.xpm"

IndicatorPlot::IndicatorPlot (QWidget *w, DBIndex *i) : QWidget(w)
{
  chartIndex = i;
  setBackgroundMode(NoBackground);
  startX = 2;
  backgroundColor.setNamedColor("black");
  borderColor.setNamedColor("white");
  gridColor.setNamedColor("#626262");
  pixelspace = 0;
  gridFlag = TRUE;
  interval = BarData::DailyBar;
  scaleToScreen = FALSE;
  logScale = FALSE;
  startIndex = 0;
  mouseFlag = None;
  crossHairFlag = FALSE;
  chartMenu = 0;
  drawMode = FALSE;
  crosshairs = TRUE;
  infoFlag = TRUE;
  coSelected = 0;
  dateFlag = TRUE;
  menuFlag = TRUE;

  plotFont.setFamily("Helvetica");
  plotFont.setPointSize(12);
  plotFont.setWeight(50);  
  plotFontMetrics = new QFontMetrics(plotFont);
  
  indy = 0;
  data = 0;

  chartMenu = new QPopupMenu();
  
  setMouseTracking(TRUE);

  setFocusPolicy(QWidget::ClickFocus);
  
  coList.setAutoDelete(TRUE);
}

IndicatorPlot::~IndicatorPlot ()
{
  delete chartMenu;
  config.closePlugins();
}

void IndicatorPlot::clear ()
{
  saveChartObjects();

  if (indy)
  {
    delete indy;
    indy = 0;
  }

  data = 0;
  mouseFlag = None;
  crossHairFlag = FALSE;

  coList.clear();
}

void IndicatorPlot::setData (BarData *l)
{
  if (! l->count())
    return;

  data = l;
}

void IndicatorPlot::setScaleToScreen (bool d)
{
  scaleToScreen = d;
}

void IndicatorPlot::setLogScale (bool d)
{
  logScale = d;
}

void IndicatorPlot::setDateFlag (bool d)
{
  dateFlag = d;
}

void IndicatorPlot::setChartPath (QString &d)
{
  chartPath = d;
}

void IndicatorPlot::setDrawMode (bool d)
{
  drawMode = d;
  
  if (drawMode)
    setCursor(QCursor(ArrowCursor));
  else
    setCursor(QCursor(CrossCursor));

  if (! drawMode && mouseFlag == COSelected && coSelected)
  {
    QPoint p(-1, -1);
    coSelected->pointerClick(p, x1, y1);
    mouseFlag = None;
  }
}

void IndicatorPlot::setInfoFlag (bool d)
{
  infoFlag = d;
}

void IndicatorPlot::setInterval (BarData::BarLength d)
{
  interval = d;
}

void IndicatorPlot::draw ()
{
  buffer.fill(backgroundColor);

  if (data)
  {
    if (! indy)
    {
      paintEvent(0);
      return;
    }

    setScale();
    drawXGrid();
    drawYGrid();
    drawInfo();
    drawLines();
    drawObjects();
    drawCrossHair();
//    drawInfo();
  }

  paintEvent(0);
  
  emit signalDraw();
}

void IndicatorPlot::drawRefresh ()
{
  paintEvent(0);
}

void IndicatorPlot::drawLines ()
{
  if (! indy->getEnable())
    return;

  int loop;
  for (loop = 0; loop < indy->getLines(); loop++)
  {
    currentLine = indy->getLine(loop);

    if (! currentLine->getSize())
      continue;
            
    switch (currentLine->getType())
    {
      case PlotLine::Histogram:
        drawHistogram();
        break;
      case PlotLine::HistogramBar:
        drawHistogramBar();
        break;
      case PlotLine::Dot:
        drawDot();
        break;
      case PlotLine::Line:
      case PlotLine::Dash:
        drawLine();
        break;
      case PlotLine::Horizontal:
        drawHorizontalLine();
        break;
      case PlotLine::Bar:
        drawBar();
        break;
      case PlotLine::Candle:
        drawCandle();
        break;
      case PlotLine::PF:
        drawPF();
        break;
      default:
        break;
    }
  }
}

void IndicatorPlot::paintEvent (QPaintEvent *)
{
  bitBlt(this, 0, 0, &buffer);
}

void IndicatorPlot::resizeEvent (QResizeEvent *event)
{
  buffer.resize(event->size());
  draw();
}

void IndicatorPlot::mousePressEvent (QMouseEvent *event)
{
  if (! indy || ! data)
    return;

  if (! drawMode)
  {
    if (event->button() == LeftButton)
    {
      if (crosshairs)
      {
        crossHair(event->x(), event->y(), TRUE);
        updateStatusBar(event->x(), event->y());
        emit leftMouseButton(event->x(), event->y(), 0);
      }
      else
        updateStatusBar(event->x(), event->y());
      return;
    }
  }
    
  if (event->button() == LeftButton)
  {
    getXY(event->x(), event->y());
    
    if (mouseFlag == None)
    {
      QDictIterator<COBase> it(coList);
      for (; it.current(); ++it)
      {
        coSelected = it.current();
	QPoint p(event->x(), event->y());
        COBase::Status rc = coSelected->pointerClick(p, x1, y1);
        if (rc != COBase::None)
        {
          mouseFlag = COSelected;
	  return;
        }
      }
    }
    
    if (mouseFlag == COSelected)
    {
      QPoint p(event->x(), event->y());
      COBase::Status rc = coSelected->pointerClick(p, x1, y1);
      if (rc == COBase::Moving)
      {
        mouseFlag = Moving;
	return;
      }
      
      if (rc == COBase::None)
      {
        mouseFlag = None;
	return;
      }
    }
    
    if (mouseFlag == Moving)
    {
      QPoint p(event->x(), event->y());
      coSelected->pointerClick(p, x1, y1);
      mouseFlag = COSelected;
      return;
    }
    
    if (mouseFlag == ClickWait)
    {
      QPoint p(event->x(), event->y());
      COBase::Status rc = coSelected->pointerClick(p, x1, y1);
      if (rc == COBase::None)
      {
        mouseFlag = None;
        emit statusMessage("");
        setCursor(QCursor(Qt::ArrowCursor));
	return;
      }
    }
  }
}

void IndicatorPlot::contextMenuEvent (QContextMenuEvent *)
{
  if (drawMode && mouseFlag == COSelected && coSelected)
    coSelected->showMenu();
  else
  {
    if (menuFlag)
      showPopupMenu();
  }
}

void IndicatorPlot::mouseMoveEvent (QMouseEvent *event)
{
  if (! indy || ! data)
    return;

  // ignore moves above the top of the chart - we get draw errors if we don't
  if (event->y() <= 0)
    return;
    
  // are we trying to drag a chart object?
  if (drawMode)
  {
    if (mouseFlag == Moving || mouseFlag == ClickWait)
    {
      getXY(event->x(), event->y());
      QPoint p(event->x(), event->y());
      coSelected->pointerMoving(buffer, p, x1, y1);
      return;
    }
  }
  
  if (! infoFlag)
    return;
  else
    getInfo(event->x());
}

void IndicatorPlot::getInfo (int x)
{
  int i = convertXToDataIndex(x);

  Setting tr;
  QString s, k;
  Bar bar;
  data->getBar(i, bar);
  bar.getDateString(TRUE, s);
  k = "D";
  tr.setData(k, s);
  bar.getTimeString(TRUE, s);
  k = "T";
  tr.setData(k, s);

  // If there are Buy/Sell objects, then show them in the data panel
  if (coList.count() > 0)
  {
    QDateTime d;
    bar.getDate(d);
    QDateTime coDate;
    int c = 0;
    Setting set;
    QDictIterator<COBase> it(coList);
    for (; it.current(); ++it)
    {
      it.current()->getDate(coDate);
      if (coDate == d)
      {
        it.current()->getSettings(set);
        k = "Type";
        set.getData(k, s);
        if (s == "BuyArrow" || s == "SellArrow")
        {
          c++;
          QString label = "Trade";
          label += "-" + QString::number(c);
          QString text = s.replace("Arrow", "");
          k = "Identifier";
          set.getData(k, s);
          if (s != "") text += " " + s;
          k = "Price";
          set.getData(k, s);
          if (s != "") text += " " + s;
          tr.setData(label, text);
        }
      }
    }
  }
  
  if (indy && indy->getEnable())
  {
    int loop;
    for (loop = 0; loop < (int) indy->getLines(); loop++)
    {
      PlotLine *line = indy->getLine(loop);
      int li = line->getSize() - data->count() + i;
      if (li > -1 && li < line->getSize())
        line->getInfo(li, tr);
    }
  }

  if (tr.count())
  {
    Setting *r = new Setting;
    tr.copy(r);
    emit infoMessage(r);
  }
}

void IndicatorPlot::mouseDoubleClickEvent (QMouseEvent *)
{
  if (! indy || ! data)
    return;

  if (mouseFlag != COSelected)
    return;
    
  coSelected->prefDialog();
}

void IndicatorPlot::keyPressEvent (QKeyEvent *key)
{
  // if chart object selected then pass keyevent to it
  if (mouseFlag == COSelected)
  {
    coSelected->keyEvent(key);
    return;
  }
  
  // process for plot keyevents
  switch (key->key())
  {
    case Qt::Key_Left:
    case Qt::Key_Right:
    case Qt::Key_Home:
    case Qt::Key_End:
    case Qt::Key_Plus:
    case Qt::Key_Minus:
    case Qt::Key_Prior:
    case Qt::Key_Next:
    case Qt::Key_Up:
    case Qt::Key_Down:
      emit keyPressed(key);
      break;
    default:
      key->ignore();
      break;
  }
}

void IndicatorPlot::setBackgroundColor (QColor &d)
{
  backgroundColor = d;
}

void IndicatorPlot::setBorderColor (QColor &d)
{
  borderColor = d;
}

void IndicatorPlot::setGridColor (QColor &d)
{
  gridColor = d;
}

void IndicatorPlot::setPlotFont (QFont &d)
{
  plotFont = d;
  delete plotFontMetrics;
  plotFontMetrics = new QFontMetrics(plotFont);
}

void IndicatorPlot::setGridFlag (bool d)
{
  gridFlag = d;
}

void IndicatorPlot::setMenuFlag (bool d)
{
  menuFlag = d;
}

void IndicatorPlot::setPixelspace (int d)
{
  pixelspace = d;
}

void IndicatorPlot::setIndex (int d)
{
  startIndex = d;
}

void IndicatorPlot::setXGrid (QMemArray<int> &d)
{
  xGrid = d;
}

void IndicatorPlot::drawXGrid ()
{
  if (gridFlag == FALSE)
    return;

  QPainter painter;
  painter.begin(&buffer);
  painter.setPen(QPen(gridColor, 1, QPen::DotLine));

  int loop;
  for (loop = 0; loop < (int) xGrid.size(); loop++)
  {
    if (xGrid[loop] >= startIndex)
    {
      int x = startX + (xGrid[loop] * pixelspace) - (startIndex * pixelspace);
      painter.drawLine (x, 0, x, buffer.height());
    }
  }

  painter.end();
}

void IndicatorPlot::addIndicator (Indicator *i)
{
  indy = i;
}

Indicator * IndicatorPlot::getIndicator ()
{
  return indy;
}

bool IndicatorPlot::deleteIndicator ()
{
  if (indy)
  {
    delete indy;
    indy = 0;
  }

  return FALSE;
}

void IndicatorPlot::drawYGrid ()
{
  if (! gridFlag)
    return;

  QPainter painter;
  painter.begin(&buffer);
  painter.setPen(QPen(gridColor, 1, QPen::DotLine));
  
  QMemArray<double> scaleArray;
  scaler.getScaleArray(scaleArray);

  int loop;
  for (loop = 0; loop < (int) scaleArray.size(); loop++)
  {
    int y = scaler.convertToY(scaleArray[loop]);
    painter.drawLine (startX, y, buffer.width(), y);
  }

  painter.end();
}

void IndicatorPlot::drawInfo ()
// plot the indicator values at the top of the screen
{
  QPainter painter;
  painter.begin(&buffer);
  painter.setPen(borderColor);
  painter.setFont(plotFont);
  painter.setBackgroundMode(OpaqueMode);
  painter.setBackgroundColor(backgroundColor);
  
  //QFontMetrics fm = painter.fontMetrics();
  int pos = startX;

  QString s;
  Bar bar;
  data->getBar(data->count() - 1, bar);
  bar.getDateString(TRUE, s);
  s.append(" ");
  painter.drawText(pos, 10, s, -1);
  pos = pos + plotFontMetrics->width(s);

  if (indy && indy->getEnable())
  {
    int loop;
    for (loop = 0; loop < (int) indy->getLines(); loop++)
    {
      PlotLine *line = indy->getLine(loop);
      if (line->getSize() > 1)
      {
        if (line->getType() == PlotLine::Bar || line->getType() == PlotLine::Candle)
        {
          if (data->count())
          {
            double ch = 0;
            double per = 0;
            if (data->count() > 1)
            {
              ch = data->getClose(data->count() - 1) - data->getClose(data->count() - 2);
              per = (ch / data->getClose(data->count() - 2)) * 100;
            }
            s = "CH=";
            QString str;
            strip(ch, 4, str);
            s.append(str);
            s.append(" (");
            strip(per, 2, str);
            s.append(str);
            s.append("%) ");
            if (ch < 0)
              painter.setPen(QColor("red"));
            else
            {
              if (ch > 0)
                painter.setPen(QColor("green"));
              else
                painter.setPen(QColor("blue"));
            }
            painter.drawText(pos, 10, s, -1);
            pos = pos + plotFontMetrics->width(s);
  
            painter.setPen(borderColor);
    
            s = "O=";
            strip(data->getOpen(data->count() - 1), 4, str);
            s.append(str);
            s.append(" H=");
            strip(data->getHigh(data->count() - 1), 4, str);
            s.append(str);
            s.append(" L=");
            strip(data->getLow(data->count() - 1), 4, str);
            s.append(str);
            s.append(" C=");
            strip(data->getClose(data->count() - 1), 4, str);
            s.append(str);
            s.append(" ");
            painter.drawText(pos, 10, s, -1);
            pos = pos + plotFontMetrics->width(s);
          }
        }
	
	else if (line->getType() == PlotLine::Horizontal)
	{
	  //dont print value of horizontal at the top 
	  //because its already displayed in the chart
	  continue;
	}
	else
        {
          line->getLabel(s);
          s.append("=");
	  QString str;
	  strip(line->getData(line->getSize() - 1), 4, str);
          s.append(str);
          s.append(" ");

          QColor c;
          line->getColor(c);
          painter.setPen(c);
          painter.drawText(pos, 10, s, -1);
          pos = pos + plotFontMetrics->width(s);
        }
      }
    }
  }
  
  painter.end();
}

void IndicatorPlot::crossHair (int x, int y, bool f)
{
  crossHairFlag = TRUE;
  getXY(x, y);
  crossHairY = y1;
  crossHairX = x1;
  if (f)
    draw();
}

void IndicatorPlot::drawCrossHair ()
{
  if (! crosshairs)
    return;
    
  if (! crossHairFlag)
    return;
    
  int y = scaler.convertToY(crossHairY);
  int x = startX + (data->getX(crossHairX) * pixelspace) - (startIndex * pixelspace);
  
  QPainter painter;
  painter.begin(&buffer);
  painter.setPen(QPen(borderColor, 1, QPen::DotLine));
  painter.drawLine (0, y, buffer.width(), y);
  painter.drawLine (x, 0, x, buffer.height());
  painter.end();
}

void IndicatorPlot::getXY (int x, int y)
{
  int i = convertXToDataIndex(x);
  data->getDate(i, x1);
  y1 = scaler.convertToVal(y);
}

int IndicatorPlot::convertXToDataIndex (int x)
{
  int i = (x / pixelspace) + startIndex;
  if (i >= (int) data->count())
    i = data->count() - 1;
  if (i < startIndex)
    i = startIndex;
  
  return i;
}

void IndicatorPlot::updateStatusBar (int x, int y)
{
  int i = convertXToDataIndex(x);
  QString s;
  Bar bar;
  data->getBar(i, bar);
  bar.getDateTimeString(TRUE, s);
  s.append(" ");
  QString str;
  strip(scaler.convertToVal(y), 4, str);
  s.append(str);
  emit statusMessage(s);
}

void IndicatorPlot::setScale ()
{
  double scaleHigh = -99999999;
  double scaleLow = 99999999;
  bool pfFlag = FALSE;

  if (indy && indy->getEnable())
  {
    int loop;
    for (loop = 0; loop < indy->getLines(); loop++)
    {
      PlotLine *line = indy->getLine(loop);
      if (line->getType() == PlotLine::Invisible)
	continue;

      if (line->getScaleFlag())
        continue;

      if (line->getType() == PlotLine::PF)
        pfFlag = TRUE;

      if (! scaleToScreen)
      {
	if (line->getHigh() > scaleHigh)
          scaleHigh = line->getHigh();

        if (line->getLow() < scaleLow)
          scaleLow = line->getLow();
      }
      else
      {        
        int loop2 = line->getSize() - data->count() + startIndex;
        int end = (buffer.width() / pixelspace) + loop2;
        if (loop2 < 0)
          loop2 = 0;
        if (end > line->getSize())
          end = line->getSize();

        double h, l;
        line->getHighLowRange(loop2, end - 1, h, l);
        if (h > scaleHigh)
          scaleHigh = h;
        if (l < scaleLow)
          scaleLow = l;
      }
    }
  }

  if (! scaleToScreen)
  {
    QDictIterator<COBase> it(coList);
    for (; it.current(); ++it)
    {
      COBase *plug = it.current();
      
      if (plug->getHigh() > scaleHigh)
        scaleHigh = plug->getHigh();
	
      if (plug->getLow() < scaleLow)
        scaleLow = plug->getLow();
    }
  }

  // we need to make a little extra room at the top of the chart for P&F plots
  // if we don't, then the top X or O is lost
  if (pfFlag)
    scaleHigh = scaleHigh * 1.02;

//  scaleLow = scaleLow * 0.999;

  double logScaleHigh = 1;
  double logRange = 0;
  if (logScale)
  {
    logScaleHigh = scaleHigh > 0.0 ? log(scaleHigh) : 1;
    double logScaleLow = scaleLow > 0.0 ? log(scaleLow) : 0;
    logRange = logScaleHigh - logScaleLow;
  }

  scaler.set(buffer.height(), scaleHigh, scaleLow, logScaleHigh, logRange, logScale);
}

int IndicatorPlot::getXFromDate (QDateTime &d)
{
  int x2 = data->getX(d);
  if (x2 == -1)
    return -1;

  int x = startX + (x2 * pixelspace) - (startIndex * pixelspace);

  return x;
}

void IndicatorPlot::strip (double d, int p, QString &s)
{
  if (fabs(d) < 1)
    s = QString::number(d, 'f', p);
  else
  {
    if (fabs(d) > 1000)
      s = QString::number(d, 'f', 0);
    else
      s = QString::number(d, 'f', 2);
  }

/*
s = QString::number(d, 'f', p);

  while (1)
  {
    if (s.find('.', -1, TRUE) != -1)
    {
      s.truncate(s.length() - 1);
      break;
    }
    else
    {
      if (s.find('0', -1, TRUE) != -1)
        s.truncate(s.length() - 1);
      else
        break;
    }
  }
*/
}

void IndicatorPlot::printChart ()
{
  QPrinter printer;
  printer.setPageSize(QPrinter::Letter);

  if (printer.setup())
  {
    emit statusMessage(tr("Creating chart snapshot..."));

    printer.setFullPage(true);
    QSize margins = printer.margins();
    int leftMargin = margins.width();
    int topMargin  = margins.height();

    QPaintDeviceMetrics prm(&printer);
    
    int prmw = prm.width() - leftMargin;
    int prmh = prm.height() - topMargin;

    if ((buffer.width() > prmw) || (buffer.height() > prmh))
    {
      QImage image = buffer.convertToImage();
      image = image.smoothScale(prmw, prmh, QImage::ScaleMin);
      buffer.convertFromImage(image);
    }

    emit statusMessage(tr("Printing..."));

    QPainter painter;
    painter.begin(&printer);
    painter.drawPixmap(leftMargin/2, topMargin/2, buffer);
    painter.end();
    emit statusMessage(tr("Printing complete."));
  }
}

void IndicatorPlot::showPopupMenu ()
{
  chartMenu->clear();
    
  chartMenu->insertItem(QPixmap(indicator), tr("New &Indicator"), this,
                        SLOT(slotNewIndicator()), CTRL+Key_I);
  chartMenu->insertItem(QPixmap(edit), tr("&Edit Indicator"), this, SLOT(slotEditIndicator()), CTRL+Key_E);
  chartMenu->insertItem(QPixmap(help), tr("Indicator &Help"), this, SLOT(slotIndicatorHelp()), CTRL+Key_H);
  chartMenu->insertSeparator ();
  chartMenu->insertItem(QPixmap(edit), tr("Edit &Chart"), this, SLOT(slotEditChart()), CTRL+Key_C);
  chartMenu->insertSeparator ();

  chartObjectMenu = new QPopupMenu();
  int id = chartObjectMenu->insertItem(QPixmap(buyarrow), "BuyArrow", this, SLOT(slotNewChartObject(int)));
  chartObjectMenu->setItemParameter(id, id);
  id = chartObjectMenu->insertItem(QPixmap(arc), "Cycle", this, SLOT(slotNewChartObject(int)));
  chartObjectMenu->setItemParameter(id, id);
  id = chartObjectMenu->insertItem(QPixmap(fib), "FiboLine", this, SLOT(slotNewChartObject(int)));
  chartObjectMenu->setItemParameter(id, id);
  id = chartObjectMenu->insertItem(QPixmap(horizontal), "HorizontalLine", this,
                                   SLOT(slotNewChartObject(int)));
  chartObjectMenu->setItemParameter(id, id);
  id = chartObjectMenu->insertItem(QPixmap(sellarrow), "SellArrow", this, SLOT(slotNewChartObject(int)));
  chartObjectMenu->setItemParameter(id, id);
  id = chartObjectMenu->insertItem(QPixmap(text), "Text", this, SLOT(slotNewChartObject(int)));
  chartObjectMenu->setItemParameter(id, id);
  id = chartObjectMenu->insertItem(QPixmap(trend), "TrendLine", this, SLOT(slotNewChartObject(int)));
  chartObjectMenu->setItemParameter(id, id);
  id = chartObjectMenu->insertItem(QPixmap(vertical), "VerticalLine", this, SLOT(slotNewChartObject(int)));
  chartObjectMenu->setItemParameter(id, id);

  id = chartMenu->insertItem (QPixmap(co), tr("New Chart Object"), chartObjectMenu);
  
  if (! drawMode || ! data)
    chartObjectMenu->setEnabled(FALSE);
  else
    chartObjectMenu->setEnabled(TRUE);
  
  chartMenu->insertItem(QPixmap(deleteitem), tr("Delete &All Chart Objects"), this,
                        SLOT(slotDeleteAllChartObjects()), CTRL+Key_A);

  chartMenu->insertSeparator ();
  chartMenu->insertItem(QPixmap(print), tr("&Print Chart"), this, SLOT(printChart()), CTRL+Key_P);
    
  id = chartMenu->insertItem(QPixmap(date), tr("Date"), this, SLOT(toggleDate()), CTRL+Key_D);
  chartMenu->setItemChecked(id, dateFlag);

  id = chartMenu->insertItem(QPixmap(loggridicon), tr("Log Scaling"), this, SLOT(toggleLog()), CTRL+Key_L);
  chartMenu->setItemChecked(id, logScale);
  
  chartMenu->exec(QCursor::pos());
}

void IndicatorPlot::toggleDate ()
{
  if (dateFlag == FALSE)
    dateFlag = TRUE;
  else
    dateFlag = FALSE;

  if (indy)
  {
    Setting set;
    QString s;
    indy->getFile(s);
    config.getIndicator(s, set);
    QString k = "dateFlag";
    QString d = QString::number(dateFlag);
    set.setData(k, d);
    config.setIndicator(s, set);
  }

  emit signalDateFlag(dateFlag);
}

void IndicatorPlot::toggleLog ()
{
  if (logScale == FALSE)
    logScale = TRUE;
  else
    logScale = FALSE;

  if (indy)
  {
    Setting set;
    QString s;
    indy->getFile(s);
    config.getIndicator(s, set);
    QString k = "logScale";
    QString d = QString::number(logScale);
    set.setData(k, d);
    config.setIndicator(s, set);
  }

  emit signalLogFlag(logScale);
}

void IndicatorPlot::setCrosshairsStatus (bool status)
{
  crosshairs = status;
  crossHairFlag = FALSE;
  draw();
}

void IndicatorPlot::slotEditIndicator ()
{
  if (indy)
  {
    QString s;
    indy->getName(s);
    emit signalEditIndicator(s);
  }
}

void IndicatorPlot::slotNewIndicator ()
{
  emit signalNewIndicator();
}

void IndicatorPlot::slotMessage (QString d)
{
  emit statusMessage(d);
}

void IndicatorPlot::slotSliderChanged (int v)
{
  setIndex(v);
  draw();
}

void IndicatorPlot::slotGridChanged (bool d)
{
  setGridFlag(d);
  draw();
}

void IndicatorPlot::slotScaleToScreenChanged (bool d)
{
  setScaleToScreen(d);
  draw();
}

void IndicatorPlot::slotDrawModeChanged (bool d)
{
  setDrawMode(d);
}

void IndicatorPlot::slotLogScaleChanged (bool d)
{
  setLogScale(d);
  draw();
}

int IndicatorPlot::getWidth ()
{
  return buffer.width();
}

void IndicatorPlot::slotEditChart ()
{
  emit signalEditChart(chartPath);
}

void IndicatorPlot::slotIndicatorHelp ()
{
  QString s, f;
  QString h = "indicator/intro.html";
  indy->getName(s);
  s.append(".html");
  // Convert to lowercase. The indicator names are case insensitive.
  // FIXME: Better to do case insensitive match for the file.
  s.lower();
  RcFile rcfile;
  rcfile.loadData(RcFile::UserDocsPath, userDocsPath);
  userDocsPath.append("/");
  rcfile.loadData(RcFile::HelpFilePath, helpFilePath);
  helpFilePath.append("/");
  QDir dir;
  // look for indicator doc first in the user docs,
  // then in main docs,
  // otherwise use the default "intro" page.
  f = userDocsPath + "indicator/" + s;
  if (dir.exists(f))
    h = f;
  else
  { 
    f = helpFilePath + "indicator/" + s;
    if (dir.exists(f))
      h = "indicator/" + s;
    else
    {
      // try old indicator docs location at top-level
      f = helpFilePath + s;
      if (dir.exists(f))
        h = s;
    }
  }
  HelpWindow *hw = new HelpWindow(this, h);
  hw->show();
}

//*************************************************************************
//******************** draw line functions ********************************
//*************************************************************************

void IndicatorPlot::drawLine ()
{
  QPainter painter;
  painter.begin(&buffer);

  QPen pen;
  QColor c;
  currentLine->getColor(c);
  pen.setColor(c);

  if (currentLine->getType() == PlotLine::Dash)
    pen.setStyle(Qt::DotLine);
  else
    pen.setStyle(Qt::SolidLine);
  painter.setPen(pen);

  int x = -1;
  int x2 = startX;
  int y = -1;
  int y2 = -1;
  int loop = currentLine->getSize() - data->count() + startIndex;
  
  Scaler scale;
  if (currentLine->getScaleFlag())
  {
    scale.set(scaler.getHeight(),
  	      currentLine->getHigh(),
	      currentLine->getLow(),
	      scaler.getLogScaleHigh(),
	      scaler.getLogRange(),
	      scaler.getLogFlag());
  }

  while ((x2 < buffer.width()) && (loop < (int) currentLine->getSize()))
  {
    if (loop > -1)
    {
      if (currentLine->getScaleFlag())
        y2 = scale.convertToY(currentLine->getData(loop));
      else
        y2 = scaler.convertToY(currentLine->getData(loop));

      if (y != -1)
        painter.drawLine (x, y, x2, y2);
      x = x2;
      y = y2;
    }

    x2 = x2 + pixelspace;
    loop++;
  }

  painter.end();
}

void IndicatorPlot::drawHorizontalLine ()
{
  QPainter painter;
  painter.begin(&buffer);

  QPen pen;
  QColor c;
  currentLine->getColor(c);
  pen.setColor(c);
  painter.setPen(pen);

  int y = scaler.convertToY(currentLine->getData(currentLine->getSize() - 1));

  painter.drawLine (0, y, buffer.width(), y);

  QString s, s2;
  strip(currentLine->getData(currentLine->getSize() - 1), 4, s);
  currentLine->getLabel(s2);
  s = s2 + "=" + s;
  
  painter.setBackgroundMode(OpaqueMode);
  painter.setBackgroundColor(backgroundColor);
  painter.setFont(plotFont);
  
  QRect rc = painter.boundingRect(startX, y - (plotFontMetrics->height()/2) , 1, 1, AlignAuto, s, -1, 0);
  painter.drawText(rc, AlignAuto, s);
  painter.drawRect(rc);
  painter.end();
}

void IndicatorPlot::drawDot ()
{
  QPainter painter;
  painter.begin(&buffer);

  QPen pen;
  QColor c;
  currentLine->getColor(c);
  pen.setColor(c);
  painter.setPen(pen);

  int x = startX;
  int loop = currentLine->getSize() - data->count() + startIndex;
  
  Scaler scale;
  if (currentLine->getScaleFlag())
  {
    scale.set(scaler.getHeight(),
  	      currentLine->getHigh(),
	      currentLine->getLow(),
	      scaler.getLogScaleHigh(),
	      scaler.getLogRange(),
	      scaler.getLogFlag());
  }

  while ((x < buffer.width()) && (loop < (int) currentLine->getSize()))
  {
    if (loop > -1)
    {
      int y;
      if (currentLine->getScaleFlag())
        y = scale.convertToY(currentLine->getData(loop));
      else
        y = scaler.convertToY(currentLine->getData(loop));

      painter.drawPoint(x, y);
    }

    x = x + pixelspace;
    loop++;
  }

  painter.end();
}

void IndicatorPlot::drawHistogram ()
{
  QPainter painter;
  painter.begin(&buffer);
  QColor c;
  currentLine->getColor(c);
  painter.setPen(c);
  painter.setBrush(c);

  int loop = currentLine->getSize() - data->count() + startIndex;

  QPointArray pa(4);

  int zero = 0;
  Scaler scale;
  if (currentLine->getScaleFlag())
  {
    scale.set(scaler.getHeight(),
  	      currentLine->getHigh(),
	      currentLine->getLow(),
	      scaler.getLogScaleHigh(),
	      scaler.getLogRange(),
	      scaler.getLogFlag());
    zero = scale.convertToY(0);
  }
  else
    zero = scaler.convertToY(0);

  int x = -1;
  int x2 = startX;
  int y = -1;
  int y2 = -1;

  while ((x < buffer.width()) && (loop < (int) currentLine->getSize()))
  {
    if (loop > -1)
    {
      if (currentLine->getScaleFlag())
        y2 = scale.convertToY(currentLine->getData(loop));
      else
        y2 = scaler.convertToY(currentLine->getData(loop));
      pa.setPoint(0, x, zero);
      pa.setPoint(1, x, y);
      pa.setPoint(2, x2, y2);
      pa.setPoint(3, x2, zero);

      if (y != -1)
        painter.drawPolygon(pa, TRUE, 0, -1);

      x = x2;
      y = y2;
    }

    x2 = x2 + pixelspace;
    loop++;
  }

  painter.end();
}

void IndicatorPlot::drawHistogramBar ()
{
  QPainter painter;
  painter.begin(&buffer);

  QColor color;
  currentLine->getColor(color);

  int x = startX;
  int zero = 0;
  Scaler scale;
  if (currentLine->getScaleFlag())
  {
    scale.set(scaler.getHeight(),
  	      currentLine->getHigh(),
	      currentLine->getLow(),
	      scaler.getLogScaleHigh(),
	      scaler.getLogRange(),
	      scaler.getLogFlag());
    zero = scale.convertToY(0);
  }
  else
    zero = scaler.convertToY(0);

  int loop = currentLine->getSize() - data->count() + startIndex;

  while ((x < buffer.width()) && (loop < (int) currentLine->getSize()))
  {
    if (loop > -1)
    {
      int y;
      if (currentLine->getScaleFlag())
        y = scale.convertToY(currentLine->getData(loop));
      else
        y = scaler.convertToY(currentLine->getData(loop));

      if (currentLine->getColorFlag() == TRUE)
	currentLine->getColorBar(loop, color);

      painter.fillRect(x, y, pixelspace - 1, zero - y, color);
    }

    x = x + pixelspace;
    loop++;
  }

  painter.end();
}

void IndicatorPlot::drawBar ()
{
  QPainter painter;
  painter.begin(&buffer);

  int loop = currentLine->getSize() - data->count() + startIndex;
  int x = startX;
  double o = 0;
  double h = 0;
  double l = 0;
  double cl = 0;
  bool ff = FALSE;
  QColor c;

  while ((x < buffer.width()) && (loop < (int) currentLine->getSize()))
  {
    if (loop > -1)
    {
      currentLine->getData(loop, c, o, h, l, cl, ff);

      painter.setPen(c);

      int y = scaler.convertToY(o);
      painter.drawLine (x - 2, y, x, y);

      y = scaler.convertToY(cl);
      painter.drawLine (x + 2, y, x, y);

      y = scaler.convertToY(h);
      int y2 = scaler.convertToY(l);
      painter.drawLine (x, y, x, y2);
    }

    x = x + pixelspace;
    loop++;
  }

  painter.end();
}

void IndicatorPlot::drawCandle ()
{
  QPainter painter;
  painter.begin(&buffer);

  int loop = currentLine->getSize() - data->count() + startIndex;
  int x = startX;
  double o = 0;
  double h = 0;
  double l = 0;
  double cl = 0;
  QColor c;
  bool ff = FALSE;

  while ((x < buffer.width()) && (loop < (int) currentLine->getSize()))
  {
    if (loop > -1)
    {
      currentLine->getData(loop, c, o, h, l, cl, ff);

      painter.setPen(c);

      int xh = scaler.convertToY(h);
      int xl = scaler.convertToY(l);
      int xc = scaler.convertToY(cl);
      int xo = scaler.convertToY(o);

      if (! ff)
      {
        painter.drawLine (x, xh, x, xc);
        painter.drawLine (x, xo, x, xl);

        if (xc == xo)
          painter.drawLine (x - 2, xo, x + 2, xo);
        else
          painter.drawRect(x - 2, xc, 5, xo - xc);
      }
      else
      {
        painter.drawLine (x, xh, x, xl);
      
        if (xc == xo)
          painter.drawLine (x - 2, xo, x + 2, xo);
        else
          painter.fillRect(x - 2, xo, 5, xc - xo, c);
      }
    }

    x = x + pixelspace;
    loop++;
  }

  painter.end();
}

void IndicatorPlot::drawPF ()
{
  QPainter painter;
  painter.begin(&buffer);

  painter.setFont(plotFont);
  //QFontMetrics fm(plotFont);

  double box = 0;
  double h = 0;
  double l = 0;
  double cl = 0;
  QColor c;
  bool ff = FALSE;
  int x = startX;
  int loop = currentLine->getSize() - data->count() + startIndex;

  while ((x < buffer.width()) && (loop < (int) currentLine->getSize()))
  {
    if (loop > -1)
    {
      currentLine->getData(loop, c, box, h, l, cl, ff);

      painter.setPen(c);

      QString s = "O";
      if (ff)
        s = "X";

//      int xh = scaler.convertToY(h);
//      int xl = scaler.convertToY(l);

//      painter.fillRect(x, xh, pixelspace - 1, xl - xh, c);

      // draw some separartor lines to simulate boxes
      double d = l;
//      painter.setPen(backgroundColor);
      while (d <= h)
      {
        int y = scaler.convertToY(d);
        painter.drawText (x, y, s, -1);
        d = d + box;
//        painter.drawLine (x, y, x + pixelspace - 1, y);
      }
    }

    x = x + pixelspace;
    loop++;
  }

  painter.end();
}

//*************************************************************************
//******************** chart object functions *****************************
//*************************************************************************

void IndicatorPlot::slotNewChartObject (int id)
{
  if (! chartPath.length())
    return;
    
  QDir dir;
  if (! dir.exists(chartPath))
    return;

  QString selection = chartObjectMenu->text(id);

  COBase tco;
  coSelected = tco.getCO(selection);
  if (! coSelected)
    return;
  
  coSelected->setData(data);
  QObject::connect(coSelected, SIGNAL(signalDraw()), this, SLOT(draw()));
  QObject::connect(coSelected, SIGNAL(signalRefresh()), this, SLOT(drawRefresh()));
  QObject::connect(coSelected, SIGNAL(message(QString)), this, SLOT(slotMessage(QString)));
  QObject::connect(coSelected, SIGNAL(signalObjectDeleted(QString)), this, SLOT(slotChartObjectDeleted(QString)));
  QObject::connect(coSelected, SIGNAL(signalSave(QString)), this, SLOT(saveChartObject(QString)));

  QFileInfo fi(chartPath);
  QString symbol = fi.fileName();
  DBIndexItem item;
  chartIndex->getIndexItem(symbol, item);
  QString s, name;
  item.getSymbol(s);
  chartIndex->getNewChartObjectName(s, name);

  coList.replace(name, coSelected);

  indy->getName(s);
  
  setCursor(QCursor(Qt::PointingHandCursor));

  mouseFlag = ClickWait;

  coSelected->newObject(s, name);
}

void IndicatorPlot::addChartObject (Setting &set)
{
  COBase tco;
  COBase *co = tco.getCO(set);
  if (! co)
    return;

  co->setData(data);
  QObject::connect(co, SIGNAL(signalDraw()), this, SLOT(draw()));
  QObject::connect(co, SIGNAL(signalRefresh()), this, SLOT(drawRefresh()));
  QObject::connect(co, SIGNAL(message(QString)), this, SLOT(slotMessage(QString)));
  QObject::connect(co, SIGNAL(signalObjectDeleted(QString)), this, SLOT(slotChartObjectDeleted(QString)));

  QString s;
  QString k = "Name";
  set.getData(k, s);
  coList.replace(s, co);

  co->addObject(set);
}

void IndicatorPlot::drawObjects ()
{
  QDictIterator<COBase> it(coList);
  for (; it.current(); ++it)
  {
    COBase *co = it.current();
    co->draw(buffer, scaler, startIndex, pixelspace, startX);
  }
}

void IndicatorPlot::slotDeleteAllChartObjects ()
{
  if (! chartPath.length())
    return;
    
  QDir dir;
  if (! dir.exists(chartPath))
    return;

  if (! coList.count())
  {
    QMessageBox::information(this,
                             tr("Qtstalker: Delete All Chart Objects"),
			     tr("No chart objects to delete."));
    return;
  }

  emit signalDeleteAllCO();
    
  coList.clear();

  mouseFlag = None;
  draw();
}

void IndicatorPlot::setCrosshairsFlag (bool d)
{
  crosshairs = d;
}

void IndicatorPlot::setScaler (Scaler &d)
{
  scaler = d;
}

Scaler & IndicatorPlot::getScaler ()
{
  return scaler;
}

void IndicatorPlot::slotChartObjectDeleted (QString d)
{
  if (! chartPath.length())
    return;
    
  QDir dir;
  if (! dir.exists(chartPath))
    return;

  if (! coList.count())
    return;

  emit signalDeleteCO(d);    

  coList.remove(d);

  mouseFlag = None;

  draw();
}

void IndicatorPlot::saveChartObjects ()
{
  if (! chartPath.length())
    return;

  QDictIterator<COBase> it(coList);
  for (; it.current(); ++it)
  {
    COBase *co = it.current();
    if (co->getSaveFlag())
    {
      Setting set;
      co->getSettings(set);
      emit signalSaveCO(set);
    }
  }
}

void IndicatorPlot::saveChartObject (QString name)
{
  COBase *co = coList[name];
  if (! co)
    return;

  Setting set;
  co->getSettings(set);
  emit signalSaveCO(set);
}

