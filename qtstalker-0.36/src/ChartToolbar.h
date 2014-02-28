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

#ifndef CHARTTOOLBAR_HPP
#define CHARTTOOLBAR_HPP

#include <qstring.h>
#include <qtoolbar.h>
#include <qmainwindow.h>
#include <qcombobox.h>
#include <qspinbox.h>
#include <qlineedit.h>
#include <qslider.h>
#include <qtoolbutton.h>
#include <qdatetime.h>

#include "RcFile.h"

class ChartToolbar : public QToolBar
{
  Q_OBJECT
  
  signals:
    void signalBarLengthChanged (int);
    void signalPixelspaceChanged (int);
    void signalSliderChanged (int);
    void signalBarsChanged (int);
    void signalPaperTradeNextBar ();
    
  public:
  
    enum MenuAction
    {
      ToolbarFocus,
      BarLengthFocus,
      BarSpacingFocus,
      BarsLoadedFocus,
      ChartPannerFocus
    };
  
    ChartToolbar(QMainWindow *);
    ~ChartToolbar();
    int getBars ();
    void enableSlider (bool);
    void setPixelspace (int, int);
    int getPixelspace ();
    int getBarLengthInt ();
    QString getBarLength ();
    int getSlider ();
    int setSliderStart (int width, int records);
    void saveSettings ();
    void getPaperTradeDate (QDateTime &);
    
    
  public slots:
    void setFocus ();
    void slotAccel (int);
    void doKeyPress (QKeyEvent *);
    void barsChanged ();
    void paperTradeDate ();
    void paperTradeNextBar ();
    void paperTradeClicked (bool);
    void ps1ButtonClicked ();
    void ps2ButtonClicked ();
    void ps3ButtonClicked ();
    void cmpsBtnMClicked();
    void cmpsBtnWClicked();
    void cmpsBtnDClicked();
    void cmpsBtn15Clicked();
    void slotSetButtonView ();
  
  private:
    QComboBox *compressionCombo;
    QSpinBox *pixelspace;
    QLineEdit *barCount;
    QSlider *slider;
    MenuAction focusFlag;
    QToolButton *ptdButton;
    QToolButton *ptnButton;
    QDateTime ptDate;
    QStringList compressionList;
    QToolButton *cmpsBtnM;
    QToolButton *cmpsBtnW;
    QToolButton *cmpsBtnD;
    QToolButton *cmpsBtn15;
    QToolButton *ps1Button;
    QToolButton *ps2Button;
    QToolButton *ps3Button;
    
    int minPixelspace;
    RcFile rcfile;
    
  private slots:
    void slotOrientationChanged(Orientation);
    void barsChangedValidate ();
};

#endif
