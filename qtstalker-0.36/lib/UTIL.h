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

#include "IndicatorPlugin.h"

class UTIL : public IndicatorPlugin
{
  public:
    UTIL ();
    virtual ~UTIL ();
    PlotLine * calculateCustom (QString &, QPtrList<PlotLine> &);
    PlotLine * calculateAccum (QString &, QPtrList<PlotLine> &);
    PlotLine * calculateNormal(QString &, QPtrList<PlotLine> &);
    PlotLine * calculateCOMP (QString &p, QPtrList<PlotLine> &d);
    PlotLine * calculateCOUNTER (QString &p, QPtrList<PlotLine> &d);
    PlotLine * calculateREF (QString &p, QPtrList<PlotLine> &d);
    PlotLine * calculateADMS (QString &p, QPtrList<PlotLine> &d, int);
    PlotLine * calculatePER (QString &p, QPtrList<PlotLine> &d);
    PlotLine * calculateCOLOR (QString &p, QPtrList<PlotLine> &d);
    PlotLine * calculateHL (QString &p, QPtrList<PlotLine> &d, int);
    PlotLine * calculateINRANGE (QString &p, QPtrList<PlotLine> &d);
    void formatDialog (QStringList &vl, QString &rv, QString &rs);
  
  private:
    QStringList methodList;
};

