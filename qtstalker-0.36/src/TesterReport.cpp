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

#include "TesterReport.h"
#include <qlayout.h>
#include <qvgroupbox.h>
#include <qheader.h>
#include <qfont.h>


TesterReport::TesterReport (QWidget *p) : QWidget (p)
{
  QVBoxLayout *vbox = new QVBoxLayout(this);
  vbox->setMargin(5);
  vbox->setSpacing(5);

  tradeList = new QTable(0, 9, this);
  tradeList->setSelectionMode(QTable::Single);
  tradeList->setSorting(FALSE);
  QHeader *header = tradeList->horizontalHeader();
  header->setLabel(0, tr("Type"), 40);
  header->setLabel(1, tr("Entry"), 90);
  header->setLabel(2, tr("Entry Price"), 60);
  header->setLabel(3, tr("Exit"), 90);
  header->setLabel(4, tr("Exit Price"), 60);
  header->setLabel(5, tr("Signal"), -1);
  header->setLabel(6, tr("Profit"), 60);
  header->setLabel(7, tr("Account"), -1);
  header->setLabel(8, tr("Vol"), 60);
  vbox->addWidget(tradeList);

  int loop;
  for (loop = 0; loop < 9; loop++)
    tradeList->setColumnReadOnly(loop, TRUE);
    
  // test summary
  
  QHBoxLayout *hbox = new QHBoxLayout(vbox);
  hbox->setSpacing(5);

  QVGroupBox *gbox = new QVGroupBox(tr("Test Summary"), this);
  gbox->setInsideSpacing(2);
  gbox->setColumns(2);
  hbox->addWidget(gbox);

  QLabel *label = new QLabel(tr("Account Balance "), gbox);
  summaryBalance = new QLabel(" ", gbox);
  
  label = new QLabel(tr("Net Profit "), gbox);
  summaryNetProfit = new QLabel(" ", gbox);

  label = new QLabel(tr("Net Profit % "), gbox);
  summaryNetPercentage = new QLabel(" ", gbox);

  label = new QLabel(tr("Initial Investment "), gbox);
  summaryInvestment = new QLabel(" ", gbox);

  label = new QLabel(tr("Commissions "), gbox);
  summaryCommission = new QLabel(" ", gbox);

  label = new QLabel(tr("Largest Drawdown "), gbox);
  summaryDrawdown = new QLabel(" ", gbox);

  label = new QLabel(tr("Trades "), gbox);
  summaryTrades = new QLabel(" ", gbox);

  label = new QLabel(tr("Long Trades "), gbox);
  summaryLongTrades = new QLabel(" ", gbox);

  label = new QLabel(tr("Short Trades "), gbox);
  summaryShortTrades = new QLabel(" ", gbox);
  
  // win summary

  gbox = new QVGroupBox(tr("Win Summary"), this);
  gbox->setInsideSpacing(2);
  gbox->setColumns(2);
  hbox->addWidget(gbox);

  label = new QLabel(tr("Trades "), gbox);
  summaryWinTrades = new QLabel(" ", gbox);

  label = new QLabel(tr("Profit "), gbox);
  summaryTotalWinTrades = new QLabel(" ", gbox);

  label = new QLabel(tr("Average "), gbox);
  summaryAverageWin = new QLabel(" ", gbox);

  label = new QLabel(tr("Largest "), gbox);
  summaryLargestWin = new QLabel(" ", gbox);

  label = new QLabel(tr("Long Trades "), gbox);
  summaryWinLongTrades = new QLabel(" ", gbox);

  label = new QLabel(tr("Short Trades "), gbox);
  summaryWinShortTrades = new QLabel(" ", gbox);

  // lose summary

  gbox = new QVGroupBox(tr("Loss Summary"), this);
  gbox->setInsideSpacing(2);
  gbox->setColumns(2);
  hbox->addWidget(gbox);

  label = new QLabel(tr("Trades "), gbox);
  summaryLoseTrades = new QLabel(" ", gbox);

  label = new QLabel(tr("Profit "), gbox);
  summaryTotalLoseTrades = new QLabel(" ", gbox);

  label = new QLabel(tr("Average "), gbox);
  summaryAverageLose = new QLabel(" ", gbox);

  label = new QLabel(tr("Largest "), gbox);
  summaryLargestLose = new QLabel(" ", gbox);

  label = new QLabel(tr("Long Trades "), gbox);
  summaryLoseLongTrades = new QLabel(" ", gbox);

  label = new QLabel(tr("Short Trades "), gbox);
  summaryLoseShortTrades = new QLabel(" ", gbox);
}

TesterReport::~TesterReport ()
{
}

void TesterReport::getSummary (QStringList &rl)
{
  rl.clear();

  int loop;
  for (loop = 0; loop < (int) tradeList->numRows(); loop++)
  {
    QStringList l;
    int loop2;
    for (loop2 = 0; loop2 < 9; loop2++)
      l.append(tradeList->text(loop, loop2));

    rl.append(l.join(","));
  }
}

void TesterReport::addTrade (QString &s, TradeItem *trade)
{
  QStringList l = QStringList::split(",", s, FALSE);

  if (! l[0].compare("S"))
    trade->setTradePosition(TradeItem::Short);

  Bar bar;
  if (bar.setDate(l[1]))
  {
    qDebug("TesterReport::addTrade:bad entry date");
    return;
  }
  QDateTime dt;
  bar.getDate(dt);
  trade->setEnterDate(dt);

  trade->setEnterPrice(l[2].toDouble());

  if (bar.setDate(l[3]))
  {
    qDebug("TesterReport::addTrade:bad exit date");
    return;
  }
  bar.getDate(dt);
  trade->setExitDate(dt);

  trade->setExitPrice(l[4].toDouble());

  trade->setExitSignal(l[5]);

  trade->setVolume(l[8].toInt());
}

void TesterReport::createSummary (QPtrList<TradeItem> &trades, double account)
{
  int shortTrades = 0;
  int longTrades = 0;
  int winLongTrades = 0;
  int loseLongTrades = 0;
  int winShortTrades = 0;
  int loseShortTrades = 0;
  double totalWinLongTrades = 0;
  double totalLoseLongTrades = 0;
  double totalWinShortTrades = 0;
  double totalLoseShortTrades = 0;
  double largestWin = 0;
  double largestLose = 0;
  double accountDrawdown = account;
  double commission = 0;
  double balance = account;

  int loop;
  for (loop = 0; loop < (int) trades.count(); loop++)
  {
    TradeItem *trade = trades.at(loop);

    // get long/short trades
    if (trade->getTradePosition() == TradeItem::Long)
    {
      longTrades++;

      if (trade->getProfit() < 0)
      {
        loseLongTrades++;
	totalLoseLongTrades = totalLoseLongTrades + trade->getProfit();

	if (trade->getProfit() < largestLose)
	  largestLose = trade->getProfit();
      }
      else
      {
        winLongTrades++;
	totalWinLongTrades = totalWinLongTrades + trade->getProfit();

	if (trade->getProfit() > largestWin)
	  largestWin = trade->getProfit();
      }
    }
    else
    {
      shortTrades++;

      if (trade->getProfit() < 0)
      {
        loseShortTrades++;
      	totalLoseShortTrades = totalLoseShortTrades + trade->getProfit();

	if (trade->getProfit() < largestLose)
	  largestLose = trade->getProfit();
      }
      else
      {
        winShortTrades++;
      	totalWinShortTrades = totalWinShortTrades + trade->getProfit();

	if (trade->getProfit() > largestWin)
	  largestWin = trade->getProfit();
      }
    }

    commission = commission + trade->getEntryCom() + trade->getExitCom();
    balance = trade->getBalance();

    if (trade->getBalance() < accountDrawdown)
      accountDrawdown = trade->getBalance();

    tradeList->setNumRows(tradeList->numRows() + 1);
    QString ts;
    trade->getTradePositionString(ts);
    tradeList->setText(tradeList->numRows() - 1, 0, ts);
    trade->getEnterDateString(ts);
    tradeList->setText(tradeList->numRows() - 1, 1, ts);
    tradeList->setText(tradeList->numRows() - 1, 2, QString::number(trade->getEnterPrice()));
    trade->getExitDateString(ts);
    tradeList->setText(tradeList->numRows() - 1, 3, ts);
    tradeList->setText(tradeList->numRows() - 1, 4, QString::number(trade->getExitPrice()));
    trade->getExitSignalString(ts);
    tradeList->setText(tradeList->numRows() - 1, 5, ts);
    tradeList->setText(tradeList->numRows() - 1, 6, QString::number(trade->getProfit()));
    tradeList->setText(tradeList->numRows() - 1, 7, QString::number(trade->getBalance()));
    tradeList->setText(tradeList->numRows() - 1, 8, QString::number(trade->getVolume()));
  }

  // main summary
  summaryBalance->setNum(balance);
  summaryNetProfit->setNum(balance - account);
  summaryNetPercentage->setNum(((balance - account) / account) * 100);
  summaryInvestment->setNum(account);
  summaryCommission->setNum(commission);
  summaryDrawdown->setNum(accountDrawdown - account);
  summaryTrades->setNum(longTrades + shortTrades);
  summaryLongTrades->setNum(longTrades);
  summaryShortTrades->setNum(shortTrades);

  // win summary
  summaryWinTrades->setNum(winLongTrades + winShortTrades);
  summaryTotalWinTrades->setNum(totalWinLongTrades + totalWinShortTrades);
  summaryAverageWin->setNum((totalWinLongTrades + totalWinShortTrades) / (winLongTrades + winShortTrades));
  summaryLargestWin->setNum(largestWin);
  summaryWinLongTrades->setNum(winLongTrades);
  summaryWinShortTrades->setNum(winShortTrades);

  // lose summary
  summaryLoseTrades->setNum(loseLongTrades + loseShortTrades);
  summaryTotalLoseTrades->setNum(totalLoseLongTrades + totalLoseShortTrades);
  summaryAverageLose->setNum((totalLoseLongTrades + totalLoseShortTrades) / (loseLongTrades + loseShortTrades));
  summaryLargestLose->setNum(largestLose);
  summaryLoseLongTrades->setNum(loseLongTrades);
  summaryLoseShortTrades->setNum(loseShortTrades);
}

void TesterReport::clear ()
{
  while (tradeList->numRows())
    tradeList->removeRow(0);
}

