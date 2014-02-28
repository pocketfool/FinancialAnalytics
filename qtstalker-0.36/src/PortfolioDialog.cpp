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

#include "PortfolioDialog.h"
#include "Setting.h"
#include "FuturesData.h"
#include "PrefDialog.h"
#include "DbPlugin.h"
#include "HelpWindow.h"
#include "DBIndexItem.h"
#include "../pics/newchart.xpm"
#include "../pics/edit.xpm"
#include "../pics/delete.xpm"
#include <qstringlist.h>
#include <qmessagebox.h>
#include <qdir.h>
#include <qfile.h>
#include <qtextstream.h>
#include <qlayout.h>

PortfolioDialog::PortfolioDialog (QString p, DBIndex *i) : QTabDialog (0, "PortfolioDialog", TRUE)
{
  portfolio = p;
  index = i;

  QString s = tr("Qtstalker: Portfolio") + " " + portfolio;
  setCaption(s);

  QWidget *w = new QWidget(this);
    
  QVBoxLayout *vbox = new QVBoxLayout(w);
  vbox->setMargin(5);
  vbox->setSpacing(0);

  toolbar = new Toolbar(w, Toolbar::Horizontal);
  vbox->addWidget(toolbar);
  vbox->addSpacing(10);
  
  connect(this, SIGNAL(applyButtonPressed()), this, SLOT(savePortfolio()));

  s = "add";
  QString s2(tr("Add"));
  toolbar->addButton(s, QPixmap(newchart), s2);
  connect(toolbar->getButton(s), SIGNAL(clicked()), this, SLOT(addItem()));
  toolbar->getButton(s)->setAccel(CTRL+Key_A);

  s = "edit";
  s2 = tr("Edit");
  toolbar->addButton(s, QPixmap(edit), s2);
  connect(toolbar->getButton(s), SIGNAL(clicked()), this, SLOT(modifyItem()));
  toolbar->setButtonStatus(s, FALSE);
  toolbar->getButton(s)->setAccel(CTRL+Key_E);

  s = "delete";
  s2 = tr("Delete");
  toolbar->addButton(s, QPixmap(deleteitem), s2);
  connect(toolbar->getButton(s), SIGNAL(clicked()), this, SLOT(deleteItem()));
  toolbar->setButtonStatus(s, FALSE);
  toolbar->getButton(s)->setAccel(CTRL+Key_D);

  plist = new QListView(w);
  plist->setSelectionMode(QListView::Single);
  plist->addColumn(tr("Symbol"), -1);
  plist->addColumn(tr("L/S"), -1);
  plist->addColumn(tr("Vol"), -1);
  plist->addColumn(tr("Buy"), -1);
  plist->addColumn(tr("Last Date"), -1);
  plist->addColumn(tr("Value"), -1);
  plist->addColumn(tr("Profit"), -1);
  plist->addColumn(tr("Profit%"), -1);
  connect(plist, SIGNAL(clicked(QListViewItem *)), this, SLOT(buttonStatus(QListViewItem *)));
  connect(plist, SIGNAL(doubleClicked(QListViewItem *, const QPoint &, int)), this,
          SLOT(itemDoubleClicked(QListViewItem *, const QPoint &, int)));
  vbox->insertWidget(2, plist);
  
  QHBoxLayout *hbox = new QHBoxLayout(vbox);
  
  balance = new QLabel(w);
  hbox->addWidget(balance);
  
  addTab(w, tr("Details"));
  
  setCancelButton();
  
  setHelpButton();
  QObject::connect(this, SIGNAL(helpButtonPressed()), this, SLOT(slotHelp()));

  buttonStatus(0);

  updatePortfolio();
}

PortfolioDialog::~PortfolioDialog ()
{
}

void PortfolioDialog::updatePortfolio ()
{
  plist->clear();

  QString s;
  config.getData(Config::PortfolioPath, s);
  s.append("/" + portfolio);

  QFile f(s);
  if (! f.open(IO_ReadOnly))
    return;
  QTextStream stream(&f);
  while(stream.atEnd() == 0)
  {
    s = stream.readLine();
    s = s.stripWhiteSpace();
    if (s.length())
    {
      QStringList l = QStringList::split(",", s, FALSE);

      s = l[0];
      if (s.contains("/"))
      {
        QFileInfo fi(s);
        s = fi.fileName();
      }
      item = new QListViewItem(plist, s, l[1], l[2], l[3]);
    }
  }

  f.close();

  updatePortfolioItems();
}

void PortfolioDialog::updatePortfolioItems ()
{
  double bal = 0;
  double orig = 0;
  
  QListViewItemIterator it(plist);
  for (; it.current(); ++it)
  {
    item = it.current();

    QString symbol = item->text(0);
    QString action = item->text(1);
    QString volume = item->text(2);
    QString price = item->text(3);

    DBIndexItem hitem;
    index->getIndexItem(symbol, hitem);
    QString s;
    hitem.getPath(s);
    QDir dir(s);
    if (! dir.exists(s, TRUE))
      continue;

    DbPlugin plug;
    if (plug.open(s, index))
      continue;

    QString type;
    hitem.getType(type);
    
    QString futuresType;
    hitem.getFuturesType(futuresType);
    
    Bar bar;
    plug.getLastBar(bar);
    
    if (bar.getEmptyFlag())
    {
      plug.close();
      continue;
    }
    
    bar.getDateTimeString(TRUE, s);
    item->setText(4, s);

    QString last = QString::number(bar.getClose());
    item->setText(5, last);

    double total;
    if (! action.compare(tr("Long")))
      total = volume.toDouble() * (last.toDouble() - price.toDouble());
    else
      total = volume.toDouble() * (price.toDouble() - last.toDouble());

    if (! type.compare("Futures"))
      total = futuresProfit(futuresType, total);

    item->setText(6, QString::number(total));
    
    double spent = price.toDouble() * volume.toDouble() * (action.compare(tr("Long"))?-1:1);

    if (total == 0)
      item->setText(7, "0%");
    else if (spent == 0)
      item->setText(7, "");
    else
      item->setText(7, QString::number((total / spent) * 100, 'f', 2) + "%");

    bal += total;
    orig += spent;
    
    plug.close();
  }

  if (bal == 0 || orig == 0)
    balance->setText(tr("Balance: ") + QString::number(bal) + " (0%)");
  else  
    balance->setText(tr("Balance: ") + QString::number(bal) + 
		     " (" + QString::number((bal / orig) * 100, 'f', 2) + "%)");
}

void PortfolioDialog::savePortfolio ()
{
  QString s;
  config.getData(Config::PortfolioPath, s);
  s.append("/" + portfolio);
  QFile f(s);
  if (! f.open(IO_WriteOnly))
    return;
  QTextStream stream(&f);

  QListViewItemIterator it(plist);
  for (; it.current(); ++it)
  {
    item = it.current();
    s = item->text(0) + "," + item->text(1) + "," + item->text(2) + "," + item->text(3);
    stream << s << "\n";
  }

  f.close();

  reject();
}

void PortfolioDialog::addItem ()
{
  PrefDialog *dialog = new PrefDialog;
  dialog->setCaption(tr("New Portfolio Item"));
  
  QString pl = tr("Details");
  QString sl = tr("Symbol");
  QString al = tr("Action");
  QString prl = tr("Price");
  QString vl = tr("Volume");
  
  dialog->createPage(pl);
  
  QString dpath;
  config.getData(Config::DataPath, dpath);
  QString s;
  dialog->addSymbolItem(sl, pl, dpath, s);

  QStringList l;
  l.append(tr("Long"));
  l.append(tr("Short"));
  dialog->addComboItem(al, pl, l, l[0]);
  
  dialog->addDoubleItem(prl, pl, 0, 0, 9999999999.0);
  
  dialog->addDoubleItem(vl, pl, 1, 1, 99999999);
  
  int rc = dialog->exec();
  
  if (rc == QDialog::Accepted)
  {
    QString symbol;
    dialog->getSymbol(sl, symbol);
    if (symbol.isNull())
      QMessageBox::information(this, tr("Qtstalker: Error"), tr("No symbol selected."));
    else
    {
      QString action;
      dialog->getCombo(al, action);
      double vol = dialog->getDouble(vl);
      double price = dialog->getDouble(prl);
      QFileInfo fi(symbol);
      new QListViewItem(plist, fi.fileName(), action, QString::number(vol), QString::number(price));

      updatePortfolioItems();
    }
  }

  delete dialog;
}

void PortfolioDialog::deleteItem ()
{
  item = plist->selectedItem();
  if (item)
  {
    QListViewItemIterator it(plist);
    int count = 0;
    for (; it.current(); ++it)
    {
      if (it.current()->text(0) == item->text(0))
        count++;
    }
    delete item;
  }

  updatePortfolioItems();

  buttonStatus(0);
}

void PortfolioDialog::modifyItem ()
{
  item = plist->currentItem();
  if (! item)
    return;

  PrefDialog *dialog = new PrefDialog;
  dialog->setCaption(tr("Edit Portfolio Item"));
  
  QString pl = tr("Details");
  QString sl = tr("Symbol");
  QString al = tr("Action");
  QString prl = tr("Price");
  QString vl = tr("Volume");
  
  dialog->createPage(pl);

  QString dpath;
  config.getData(Config::DataPath, dpath);

  QString ts = item->text(0);
  DBIndexItem iitem;
  index->getIndexItem(ts, iitem);
  QString ts2, s;
  iitem.getPath(ts2);

  dialog->addSymbolItem(sl, pl, dpath, ts2);

  QStringList l;
  l.append(tr("Long"));
  l.append(tr("Short"));
  s = item->text(1);
  dialog->addComboItem(al, pl, l, s);
  
  dialog->addDoubleItem(prl, pl, item->text(3).toDouble(), 0, 9999999999.0);
  
  dialog->addDoubleItem(vl, pl, item->text(2).toDouble(), 1, 99999999);
  
  int rc = dialog->exec();

  if (rc == QDialog::Accepted)
  {
    QString symbol;
    dialog->getSymbol(sl, symbol);
    if (symbol.isNull())
      QMessageBox::information(this, tr("Qtstalker: Error"), tr("No symbol selected."));
    else
    {
      QString action;
      dialog->getCombo(al, action);
      double vol = dialog->getDouble(vl);
      double price = dialog->getDouble(prl);

      QFileInfo fi(symbol);
      item->setText(0, fi.fileName());
      item->setText(1, action);
      item->setText(2, QString::number(vol));
      item->setText(3, QString::number(price));

      updatePortfolioItems();
    }
  }

  delete dialog;
}

void PortfolioDialog::buttonStatus (QListViewItem *i)
{
  QString s("edit");
  QString s2("delete");
  
  if (! i)
  {
    toolbar->setButtonStatus(s, FALSE);
    toolbar->setButtonStatus(s2, FALSE);
  }
  else
  {
    toolbar->setButtonStatus(s, TRUE);
    toolbar->setButtonStatus(s2, TRUE);
  }
}

double PortfolioDialog::futuresProfit (QString &sym, double diff)
{
  FuturesData *fd = new FuturesData();
  fd->setSymbol(sym);
  double rate = fd->getRate();
  double t = diff * rate;
  delete fd;

  return t;
}

void PortfolioDialog::itemDoubleClicked (QListViewItem *item, const QPoint &, int)
{
  if (! item)
    return;
    
  modifyItem();    
}

void PortfolioDialog::slotHelp ()
{
  QString s = "portfolios.html";
  HelpWindow *hw = new HelpWindow(this, s);
  hw->show();
}

