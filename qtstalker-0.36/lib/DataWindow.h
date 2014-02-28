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

#ifndef DATAWINDOW_HPP
#define DATAWINDOW_HPP

#include <qstring.h>
#include <qdialog.h>
#include <qtable.h>
#include <qheader.h>
#include "BarData.h"
#include "Plot.h"


class DataWindow : public QDialog
{
  Q_OBJECT

  public:
    DataWindow(QWidget *);
    ~DataWindow();
    void setData (int, int, QString &);
    void setHeader (int, QString &);
    void setBars (BarData *);
    void setPlot (Plot *);
    QString strip (double, int);

  private:
    QTable *table;
    QHeader *hHeader;
};

#endif
