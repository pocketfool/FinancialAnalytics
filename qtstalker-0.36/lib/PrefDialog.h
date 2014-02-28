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

#ifndef PREFDIALOG_HPP
#define PREFDIALOG_HPP

#include "ColorButton.h"
#include "FontButton.h"
#include "FileButton.h"
#include "SymbolButton.h"
#include <qtabdialog.h>
#include <qlayout.h>
#include <qwidget.h>
#include <qpushbutton.h>
#include <qdict.h>
#include <qspinbox.h>
#include <qlineedit.h>
#include <qvalidator.h>
#include <qcheckbox.h>
#include <qcombobox.h>
#include <qfont.h>
#include <qdatetimeedit.h>
#include <qdatetime.h>
#include <qstringlist.h>
#include <qstring.h>
#include <qlabel.h>

class PrefDialog : public QTabDialog
{
  Q_OBJECT

  public:
    PrefDialog (QWidget *);
    PrefDialog ();
    ~PrefDialog ();
    void init ();
    void createPage (QString &);
    void deletePage (QString &);
    void setHelpFile (QString &);
    void addColorItem (QString &, QString &, QColor &);
    void addColorPrefItem (QString &, QString &, QColor &);
    void getColor (QString &, QColor &);
    void addDoubleItem (QString &, QString &, double, double, double);
    void addDoubleItem (QString &, QString &, double);
    double getDouble (QString &);
    void addIntItem (QString &, QString &, int);
    void addIntItem (QString &, QString &, int, int, int);
    int getInt (QString &);
    void addCheckItem (QString &, QString &, bool);
    void addCheckItem (QString &, QString &, QString &);
    bool getCheck (QString &);
    void getCheckString (QString &, QString &);
    void addFontItem (QString &, QString &, QFont &);
    void getFont (QString &, QFont &);
    void addTextItem (QString &, QString &, QString &);
    void getText (QString &, QString &);
    void addComboItem (QString &, QString &, QStringList &, QString &);
    void addComboItem (QString &, QString &, QStringList &, int);
    void getCombo (QString &, QString &);
    int getComboIndex (QString &);
    QComboBox * getComboWidget (QString &);
    void addDateItem (QString &, QString &, QDateTime &);
    void getDate (QString &, QDateTime &);
    void addFileItem (QString &, QString &, QStringList &, QString &);
    void getFile (QString &, QStringList &);
    void addSymbolItem (QString &, QString &, QString &, QString &);
    void getSymbol (QString &, QString &);
    void addLabelItem (QString &, QString &, QString &);
    void getItem (QString &, QString &);
    void addTimeItem (QString &, QString &, QDateTime &);
    void getTime (QString &, QDateTime &);
    
  public slots:
    void help ();

  private:
    QDict<QWidget> widgetList;
    QDict<QGridLayout> gridList;
    QDict<ColorButton> colorButtonList;
    QDict<QSpinBox> intList;
    QDict<QLineEdit> doubleList;
    QDict<QCheckBox> checkList;
    QDict<FontButton> fontButtonList;
    QDict<QLineEdit> textList;
    QDict<QComboBox> comboList;
    QDict<QDateEdit> dateList;
    QDict<FileButton> fileList;
    QDict<SymbolButton> symbolList;
    QDict<QDoubleValidator> dvList;
    QDict<QLabel> labelList;
    QDict<QTimeEdit> timeList;
    QString helpFile;
};

#endif
