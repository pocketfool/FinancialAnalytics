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

#include "Toolbar.h"
#include <qtooltip.h>

//Toolbar::Toolbar (QWidget *w, int h, int wi, bool f) : QFrame (w)
Toolbar::Toolbar (QWidget *w, Bias b) : QFrame (w)
{
//  height = h;
//  width = wi;
//  pflag = f;
  bias = b;
  list.setAutoDelete(TRUE);
/*  because it looks bad, cut out
  setFrameShape(Box);
  setFrameShadow(Sunken);
// don't work, why ever ->  setFrameStyle(ToolBarPanel);
  setLineWidth(1);
*/

  QHBoxLayout *hbox = 0;
  QVBoxLayout *vbox = 0;
  
  if (bias == Vertical)
  {
// seems to be obsolete
//    setMinimumWidth(ToolBarBtn::btnMinWidth + 3);
//    setMaximumWidth(ToolBarBtn::btnMaxWidth + 3);
    vbox = new QVBoxLayout(this);  
    vbox->setSpacing(0);
    vbox->setMargin(0);
    grid = new QGridLayout(vbox, 1, 1);  
  }
  else
  {
//    setMinimumHeight(ToolBarBtn::btnMinHeight + 3);
//    setMaximumHeight(ToolBarBtn::btnMaxHeight + 3);
    hbox = new QHBoxLayout(this);  
    hbox->setSpacing(0);
    hbox->setMargin(0);
    grid = new QGridLayout(hbox, 1, 1);  
  }
  
  grid->setSpacing(2); // space between each button
  grid->setMargin(4);  // ...the button row to its environment
  
  if (bias == Vertical)
    vbox->addStretch(1);
  else
    hbox->addStretch(1);
}

Toolbar::~Toolbar ()
{
}

void Toolbar::addButton (QString &name, QPixmap pix, QString &tt)
{
  ToolBarBtn *button = new ToolBarBtn (this);
  QToolTip::add(button, tt);
  button->setPixmap(pix);

  //button->setMaximumWidth(width);
  //button->setMaximumHeight(height);
  if (bias == Vertical)
    grid->addWidget(button, list.count(), 0);
  else
    grid->addWidget(button, 0, list.count());
  list.replace(name, button);
}

ToolBarBtn * Toolbar::getButton (QString &name)
{
  return list[name];
}

void Toolbar::setButtonStatus (QString &name, bool d)
{
  ToolBarBtn *button = list[name];
  if (button)
    button->setEnabled(d);
}

void Toolbar::addSeparator ()
{
  QFrame *vline = new QFrame(this);
  vline->setFrameStyle(QFrame::VLine | QFrame::Sunken);
  if (bias == Vertical)
    grid->addWidget(vline, -1, 0);
  else
    grid->addWidget(vline, 0, -1);
}

