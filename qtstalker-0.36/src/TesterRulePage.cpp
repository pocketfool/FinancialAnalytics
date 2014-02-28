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

#include <qlayout.h>
#include <qvgroupbox.h>
#include <qfile.h>
#include <qtextstream.h>
#include "TesterRulePage.h"


TesterRulePage::TesterRulePage (QWidget *p) : QWidget (p)
{
  QVBoxLayout *vbox = new QVBoxLayout(this);
  vbox->setMargin(5);
  vbox->setSpacing(5);
  
  QGridLayout *grid = new QGridLayout(vbox, 2, 2);
  
  QVGroupBox *gbox = new QVGroupBox(tr("Enter Long"), this);
  grid->addWidget(gbox, 0, 0);

  enterLongEdit = new FormulaEdit(gbox, FormulaEdit::Logic);  
  
  gbox = new QVGroupBox(tr("Exit Long"), this);
  grid->addWidget(gbox, 0, 1);

  exitLongEdit = new FormulaEdit(gbox, FormulaEdit::Logic);  

  gbox = new QVGroupBox(tr("Enter Short"), this);
  grid->addWidget(gbox, 1, 0);

  enterShortEdit = new FormulaEdit(gbox, FormulaEdit::Logic);  
  
  gbox = new QVGroupBox(tr("Exit Short"), this);
  grid->addWidget(gbox, 1, 1);

  exitShortEdit = new FormulaEdit(gbox, FormulaEdit::Logic);  
}

TesterRulePage::~TesterRulePage ()
{
}

void TesterRulePage::saveEditRule (EditRule type, QString &ruleName)
{
  Config config;
  FormulaEdit *edit = 0;
  QString s;
  config.getData(Config::TestPath, s);
  s.append("/" + ruleName);
  
  switch(type)
  {
    case 0:
      edit = enterLongEdit;
      s.append("/el/rule");
      break;
    case 1:
      edit = exitLongEdit;
      s.append("/xl/rule");
      break;
    case 2:
      edit = enterShortEdit;
      s.append("/es/rule");
      break;
    case 3:
      edit = exitShortEdit;
      s.append("/xs/rule");
      break;
    default:
      break;
  }

  QFile f(s);
  if (! f.open(IO_WriteOnly))
    return;
  QTextStream stream(&f);

  edit->getText(s);
  stream << s << "\n";
  
  f.close();
}

void TesterRulePage::loadEditRule (EditRule type, QString &ruleName)
{
  Config config;
  FormulaEdit *edit = 0;
  QString s;
  config.getData(Config::TestPath, s);
  s.append("/" + ruleName);
  
  switch(type)
  {
    case 0:
      edit = enterLongEdit;
      s.append("/el/rule");
      break;
    case 1:
      edit = exitLongEdit;
      s.append("/xl/rule");
      break;
    case 2:
      edit = enterShortEdit;
      s.append("/es/rule");
      break;
    case 3:
      edit = exitShortEdit;
      s.append("/xs/rule");
      break;
    default:
      break;
  }

  QFile f(s);
  if (! f.open(IO_ReadOnly))
    return;
  QTextStream stream(&f);

  while(stream.atEnd() == 0)
  {
    s = stream.readLine();
    s = s.stripWhiteSpace();
    if (! s.length())
      continue;
  
    edit->setLine(s);
  }  
  
  f.close();
}

QString TesterRulePage::getEditRule (EditRule type)
{
  QString s;
  switch (type)
  {
    case EnterLong:
      enterLongEdit->getText(s);
      break;
    case ExitLong:
      exitLongEdit->getText(s);
      break;
    case EnterShort:
      enterShortEdit->getText(s);
      break;
    case ExitShort:
      exitShortEdit->getText(s);
      break;
    default:
      break;
  }

  return s;
}

