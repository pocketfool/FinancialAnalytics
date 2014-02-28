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

#ifndef QUOTEPLUGIN_HPP
#define QUOTEPLUGIN_HPP

#include <qstring.h>
#include <qnetworkprotocol.h>
#include <qurloperator.h>
#include <qtimer.h>
#include <qtabdialog.h>
#include <qtextedit.h>
#include <qlayout.h>
#include <qspinbox.h>
#include <qprogressbar.h>
#include "Toolbar.h"
#include "DBIndex.h"

/**
* \todo
* Needs to be re-written to not use the QUrlOperator.
* See http://doc.trolltech.com/4.3/porting4-overview.html#url-operations-qurloperator
*/
class QuotePlugin : public QTabDialog
{
  Q_OBJECT

  signals:
    void signalGetFileDone (bool);
    void signalCopyFileDone (QString);
    void signalTimeout ();
    void signalProgMessage (int, int);
    void chartUpdated ();
    void signalWakeup ();

  public:
    QuotePlugin ();
    virtual ~QuotePlugin ();
    bool setTFloat (QString &, bool);
    void stripJunk (QString &, QString &);
    void createDirectory (QString &, QString &);
    void getPluginName (QString &);
    void getHelpFile (QString &);
    void buildGui ();
    void enableGUI ();
    void disableGUI ();
    virtual void update ();
    void setChartIndex (DBIndex *);
    QProgressBar *progressBar;
    
  public slots:
    void getFile (QString &);
    void copyFile (QString &, QString &);
    void getFileDone (QNetworkOperation *);
    void copyFileDone (QNetworkOperation *);
    void dataReady (const QByteArray &, QNetworkOperation *);
    void slotTimeout ();
    void getQuotes ();
    void downloadComplete ();
    void cancelDownload ();
    void printStatusLogMessage (QString &);
    void help ();
    void slotWakeup ();
    
  protected:
    QString file;
    float tfloat;
    bool saveFlag;
    QString pluginName;
    QString helpFile;
    QUrlOperator *op;
    QString data;
    QTimer *timer;
    int errorLoop;
    QString stringDone;
    QString stringCanceled;
    QTextEdit *statusLog;
    Toolbar *toolbar;
    QVBoxLayout *vbox;
    QWidget *baseWidget;
    QGridLayout *grid;
    QSpinBox *retrySpin;
    QSpinBox *timeoutSpin;
    DBIndex *chartIndex;
};

#endif
