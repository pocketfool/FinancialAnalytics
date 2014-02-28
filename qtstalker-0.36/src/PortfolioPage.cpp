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

#include "PortfolioPage.h"
#include "PortfolioDialog.h"
#include "SymbolDialog.h"
#include "HelpWindow.h"
#include "../pics/help.xpm"
#include "../pics/open.xpm"
#include "../pics/newchart.xpm"
#include "../pics/delete.xpm"
#include "../pics/rename.xpm"
#include <qinputdialog.h>
#include <qmessagebox.h>
#include <qcursor.h>
#include <qfile.h>
#include <qaccel.h>

PortfolioPage::PortfolioPage (QWidget *w, DBIndex *i) : QListBox (w)
{
  chartIndex = i;

  connect(this, SIGNAL(contextMenuRequested(QListBoxItem *, const QPoint &)), this, SLOT(rightClick(QListBoxItem *)));
  connect(this, SIGNAL(highlighted(const QString &)), this, SLOT(portfolioSelected(const QString &)));
  connect(this, SIGNAL(doubleClicked(QListBoxItem *)), this, SLOT(doubleClick(QListBoxItem *)));
  
  menu = new QPopupMenu(this);
  menu->insertItem(QPixmap(newchart), tr("&New Portfolio	Ctrl+N"), this, SLOT(newPortfolio()));
  menu->insertItem(QPixmap(open), tr("&Open Portfolio		Ctrl+O"), this, SLOT(openPortfolio()));
  menu->insertItem(QPixmap(deleteitem), tr("&Delete Portfolio	Ctrl+D"), this, SLOT(deletePortfolio()));
  menu->insertItem(QPixmap(renam), tr("&Rename Portfolio	Ctrl+R"), this, SLOT(renamePortfolio()));
  menu->insertSeparator(-1);
  menu->insertItem(QPixmap(help), tr("&Help		Ctrl+H"), this, SLOT(slotHelp()));

  QAccel *a = new QAccel(this);
  connect(a, SIGNAL(activated(int)), this, SLOT(slotAccel(int)));
  a->insertItem(CTRL+Key_N, NewPortfolio);
  a->insertItem(CTRL+Key_O, OpenPortfolio);
  a->insertItem(CTRL+Key_D, DeletePortfolio);
  a->insertItem(CTRL+Key_R, RenamePortfolio);
  a->insertItem(CTRL+Key_H, Help);
  
  updateList();
  portfolioSelected(QString());
}

PortfolioPage::~PortfolioPage ()
{
}

void PortfolioPage::openPortfolio ()
{
  PortfolioDialog *dialog = new PortfolioDialog(currentText(), chartIndex);
  dialog->show();
}

void PortfolioPage::openPortfolio (QString d)
{
  PortfolioDialog *dialog = new PortfolioDialog(d, chartIndex);
  dialog->show();
}

void PortfolioPage::newPortfolio()
{
  bool ok;
  QString s = QInputDialog::getText(tr("New Portfolio"),
  				    tr("Enter new portfolio name."),
				    QLineEdit::Normal,
				    tr("NewPortfolio"),
				    &ok,
				    this);
  if ((ok) && (! s.isNull()))
  {
    int loop;
    QString selection;
    for (loop = 0; loop < (int) s.length(); loop++)
    {
      QChar c = s.at(loop);
      if (c.isLetterOrNumber())
        selection.append(c);
    }
  
    config.getData(Config::PortfolioPath, s);
    s.append("/" + selection);
    QDir dir(s);
    if (dir.exists(s, TRUE))
    {
      QMessageBox::information(this, tr("Qtstalker: Error"), tr("This portfolio already exists."));
      return;
    }

    // create the empty file    
    QFile f(s);
    if (! f.open(IO_WriteOnly))
      return;
    f.close();
    
    updateList();

    openPortfolio(selection);
  }
}

void PortfolioPage::deletePortfolio()
{
  QString s("*");
  QString s2;
  config.getData(Config::PortfolioPath, s2);
  SymbolDialog *dialog = new SymbolDialog(this,
                                          s2,
  				          s2,
					  s,
					  QFileDialog::ExistingFiles);
  dialog->setCaption(tr("Select Portfolios To Delete"));

  int rc = dialog->exec();

  if (rc == QDialog::Accepted)
  {
    rc = QMessageBox::warning(this,
  			      tr("Qtstalker: Warning"),
			      tr("Are you sure you want to delete this portfolio?"),
			      QMessageBox::Yes,
			      QMessageBox::No,
			      QMessageBox::NoButton);

    if (rc == QMessageBox::No)
    {
      delete dialog;
      return;
    }

    QStringList l = dialog->selectedFiles();
    int loop;
    QDir dir;
    for (loop = 0; loop < (int) l.count(); loop++)
      dir.remove(l[loop], TRUE);

    updateList();
    portfolioSelected(QString());
  }

  delete dialog;
}

void PortfolioPage::renamePortfolio ()
{
  bool ok;
  QString s = QInputDialog::getText(tr("Rename Portfolio"),
  				    tr("Enter new portfolio name."),
				    QLineEdit::Normal,
				    currentText(),
				    &ok,
				    this);
  if ((ok) && (! s.isNull()))
  {
    int loop;
    QString selection;
    for (loop = 0; loop < (int) s.length(); loop++)
    {
      QChar c = s.at(loop);
      if (c.isLetterOrNumber())
        selection.append(c);
    }
  
    config.getData(Config::PortfolioPath, s);
    s.append("/" + selection);
    QDir dir(s);
    if (dir.exists(s, TRUE))
    {
      QMessageBox::information(this, tr("Qtstalker: Error"), tr("This portfolio already exists."));
      return;
    }

    QString s2;
    config.getData(Config::PortfolioPath, s2);
    s2.append("/" + currentText());

    dir.rename(s2, s, TRUE);

    updateList();
    portfolioSelected(QString());
  }
}

void PortfolioPage::portfolioSelected (const QString &d)
{
  if (d.length())
  {
    menu->setItemEnabled(menu->idAt(1), TRUE);
    menu->setItemEnabled(menu->idAt(2), TRUE);
    menu->setItemEnabled(menu->idAt(3), TRUE);
  }
  else
  {
    menu->setItemEnabled(menu->idAt(1), FALSE);
    menu->setItemEnabled(menu->idAt(2), FALSE);
    menu->setItemEnabled(menu->idAt(3), FALSE);
  }
}

void PortfolioPage::rightClick (QListBoxItem *)
{
  menu->exec(QCursor::pos());
}

void PortfolioPage::updateList ()
{
  clear();

  QString s;
  config.getData(Config::PortfolioPath, s);
  QDir dir(s);
  int loop;
  for (loop = 2; loop < (int) dir.count(); loop++)
    insertItem(dir[loop], -1);
}

void PortfolioPage::doubleClick (QListBoxItem *item)
{
  if (! item)
    return;
    
  openPortfolio(item->text());
}

void PortfolioPage::slotHelp ()
{
  QString s = "workwithportfolios.html";
  HelpWindow *hw = new HelpWindow(this, s);
  hw->show();
}

void PortfolioPage::keyPressEvent (QKeyEvent *key)
{
  doKeyPress(key);  
}

void PortfolioPage::doKeyPress (QKeyEvent *key)
{
  key->accept();
  
  if (key->state() == Qt::ControlButton)
  {
    switch(key->key())
    {
      case Qt::Key_N:
        slotAccel(NewPortfolio);
	break;
      case Qt::Key_D:
        slotAccel(DeletePortfolio);
	break;
      case Qt::Key_O:
        slotAccel(OpenPortfolio);
	break;
      case Qt::Key_R:
        slotAccel(RenamePortfolio);
	break;
      default:
        break;
    }
  }
  else
  {
    switch (key->key())
    {
      case Qt::Key_Delete:
        deletePortfolio();
        break;
      case Qt::Key_Left: // segfaults if we dont trap this
      case Qt::Key_Right: // segfaults if we dont trap this
        break;      
      case Qt::Key_Enter:
      case Qt::Key_Return:
        openPortfolio();
        break;
      default:
        QListBox::keyPressEvent(key);
        break;
    }
  }
}

void PortfolioPage::slotAccel (int id)
{
  switch (id)
  {
    case NewPortfolio:
      newPortfolio();
      break;  
    case DeletePortfolio:
      deletePortfolio();
      break;  
    case RenamePortfolio:
      renamePortfolio();
      break;  
    case OpenPortfolio:
      openPortfolio();
      break;  
    case Help:
      slotHelp();
      break;  
    default:
      break;
  }
}

