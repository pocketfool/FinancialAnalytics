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

#ifndef STOCKSDIALOG_HPP
#define STOCKSDIALOG_HPP

#include <qtabdialog.h>
#include <qlineedit.h>
#include <qlistview.h>
#include <qdatetimeedit.h>
#include "DbPlugin.h"
#include "BarEdit.h"
#include "DBIndex.h"

class StocksDialog : public QTabDialog
{
  Q_OBJECT

  public:
    StocksDialog (QString, DbPlugin *, DBIndex *);
    ~StocksDialog ();
    void createDetailsPage ();
    void createDataPage ();
    void createFundamentalsPage ();
    void createSplitPage ();
    void updateFields (Bar &);
    bool getReloadFlag ();

  public slots:
    void deleteRecord ();
    void saveRecord ();
    void slotDateSearch (QDateTime);
    void saveChart ();
    void help ();
    void split ();
    void slotFirstRecord ();
    void slotLastRecord ();
    void slotPrevRecord ();
    void slotNextRecord ();

  private:
    DbPlugin *db;
    QLineEdit *title;
    QLineEdit *splitRatio;
    QString helpFile;
    QListView *fundView;
    BarEdit *barEdit;
    QDateEdit *splitDate;
    QDateTime currentDate;
    DBIndex *index;
    QString symbol;
    bool reloadFlag;
};

#endif
