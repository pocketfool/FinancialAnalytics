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

#include "MainMenubar.h"
#include <qaccel.h>
#include "../pics/done.xpm"
#include "../pics/grid.xpm"
#include "../pics/datawindow.xpm"
#include "../pics/indicator.xpm"
#include "../pics/quotes.xpm"
#include "../pics/configure.xpm"
#include "../pics/scaletoscreen.xpm"
#include "../pics/nav.xpm"
#include "../pics/co.xpm"
#include "../pics/help.xpm"
#include "../pics/qtstalker.xpm"
#include "../pics/crosshair.xpm"
#include "../pics/papertrade.xpm"
#include "RcFile.h"


MainMenubar::MainMenubar (QMainWindow *mw) : QMenuBar (mw, "mainMenubar")
{
  actions.setAutoDelete(FALSE);
  
  RcFile rcfile;
  
  QPixmap icon(finished);
  QAction *action  = new QAction(this, "actionExit");
  action->setMenuText(tr("E&xit"));
  action->setIconSet(icon);
  action->setAccel(CTRL+Key_Q);
  action->setStatusTip(tr("Quit Qtstalker (Ctrl+Q)"));
  action->setToolTip(tr("Quit Qtstalker (Ctrl+Q)"));
  connect(action, SIGNAL(activated()), this, SIGNAL(signalExit()));
  actions.replace(Exit, action);
  
  icon = indicator;
  action = new QAction(this, "actionNewIndicator");
  action->setMenuText(tr("New &Indicator"));
  action->setIconSet(icon);
  action->setStatusTip(tr("Add a new indicator to chart (Ctrl+2)"));
  action->setToolTip(tr("Add a new indicator to chart (Ctrl+2)"));
  connect(action, SIGNAL(activated()), this, SIGNAL(signalNewIndicator()));
  actions.replace(NewIndicator, action);

  icon = configure;
  action = new QAction(this, "actionOptions");
  action->setMenuText(tr("Edit &Preferences"));
  action->setIconSet(icon);
  action->setStatusTip(tr("Modify user preferences  (Ctrl+3)"));
  action->setToolTip(tr("Modify user preferences  (Ctrl+3)"));
  connect(action, SIGNAL(activated()), mw, SLOT(slotOptions()));
  actions.replace(Options, action);

  icon = gridicon;
  bool b;
  rcfile.loadData(RcFile::Grid, b);
  action = new QAction(this, "actionGrid");
  action->setMenuText(tr("Chart &Grid"));
  action->setIconSet(icon);
  action->setStatusTip(tr("Toggle the chart grid  (Ctrl+4)"));
  action->setToolTip(tr("Toggle the chart grid  (Ctrl+4)"));
  action->setToggleAction(TRUE);
  action->setOn(b);
  connect(action, SIGNAL(toggled(bool)), this, SIGNAL(signalGrid(bool)));
  actions.replace(Grid, action);

  icon = quotes;
  action = new QAction(this, "actionQuote");
  action->setMenuText(tr("Load Quotes"));
  action->setIconSet(icon);
  action->setStatusTip(tr("Load Quotes (Ctrl+Y)"));
  action->setToolTip(tr("Load Quotes (Ctrl+Y)"));
  connect(action, SIGNAL(activated()), mw, SLOT(slotQuotes()));
  actions.replace(Quotes, action);

  icon = datawindow;
  action = new QAction(this, "actionDataWindow");
  action->setMenuText(tr("&Data Window"));
  action->setIconSet(icon);
  action->setAccel(ALT+Key_1);
  action->setStatusTip(tr("Show the data window (Alt+1)"));
  action->setToolTip(tr("Show the data window (Alt+1)"));
  connect(action, SIGNAL(activated()), mw, SLOT(slotDataWindow()));
  actions.replace(DataWindow, action);

  icon = qtstalker;
  action = new QAction(this, "actionAbout");
  action->setMenuText(tr("&About"));
  action->setIconSet(icon);
  action->setStatusTip(tr("About Qtstalker."));
  action->setToolTip(tr("About Qtstalker."));
  connect(action, SIGNAL(activated()), mw, SLOT(slotAbout()));
  actions.replace(About, action);

  icon = scaletoscreen;
  rcfile.loadData(RcFile::ScaleToScreen, b);
  action = new QAction(this, "actionScale");
  action->setMenuText(tr("&Scale To Screen"));
  action->setIconSet(icon);
  action->setStatusTip(tr("Scale chart to current screen data (Ctrl+5)"));
  action->setToolTip(tr("Scale chart to current screen data (Ctrl+5)"));
  action->setToggleAction(TRUE);
  action->setOn(b);
  connect(action, SIGNAL(toggled(bool)), this, SIGNAL(signalScale(bool)));
  actions.replace(ScaleToScreen, action);

  icon = nav;
  rcfile.loadData(RcFile::ShowSidePanel, b);
  action = new QAction(this, "actionPanel");
  action->setMenuText(tr("Side Pa&nel"));
  action->setIconSet(icon);
  action->setStatusTip(tr("Toggle the side panel area from view (Ctrl+7)"));
  action->setToolTip(tr("Toggle the side panel area from view (Ctrl+7)"));
  action->setToggleAction(TRUE);
  action->setOn(b);
  connect(action, SIGNAL(toggled(bool)), mw, SLOT(slotHideNav(bool)));
  actions.replace(SidePanel, action);

  icon = co;
  rcfile.loadData(RcFile::DrawMode, b);
  action = new QAction(this, "actionDraw");
  action->setMenuText(tr("Toggle Dra&w Mode"));
  action->setIconSet(icon);
  action->setStatusTip(tr("Toggle drawing mode (Ctrl+0)"));
  action->setToolTip(tr("Toggle drawing mode (Ctrl+0)"));
  action->setToggleAction(TRUE);
  action->setOn(b);
  connect(action, SIGNAL(toggled(bool)), this, SIGNAL(signalDraw(bool)));
  actions.replace(DrawMode, action);
  
  icon = crosshair;
  rcfile.loadData(RcFile::Crosshairs, b);
  action = new QAction(this, "actionCrosshairs");
  action->setMenuText(tr("Toggle Cross&hairs"));
  action->setIconSet(icon);
  action->setStatusTip(tr("Toggle crosshairs (Ctrl+6)"));
  action->setToolTip(tr("Toggle crosshairs (Ctrl+6)"));
  action->setToggleAction(TRUE);
  action->setOn(b);
  connect(action, SIGNAL(toggled(bool)), this, SIGNAL(signalCrosshairs(bool)));
  actions.replace(Crosshairs, action);

  icon = papertrade;
  rcfile.loadData(RcFile::PaperTradeMode, b);
  action = new QAction(this, "actionPaperTrade");
  action->setMenuText(tr("Paper Trade Mode"));
  action->setIconSet(icon);
  action->setStatusTip(tr("Toggle the paper trade mode"));
  action->setToolTip(tr("Toggle the paper trade mode"));
  action->setToggleAction(TRUE);
  action->setOn(b);
  connect(action, SIGNAL(toggled(bool)), this, SIGNAL(signalPaperTrade(bool)));
  actions.replace(PaperTrade, action);

  icon = help;
  action = new QAction(this, "actionHelp");
  action->setMenuText(tr("&Help"));
  action->setIconSet(icon);
  action->setAccel(ALT+Key_3);
  action->setStatusTip(tr("Display Help Dialog (Alt+3)"));
  action->setToolTip(tr("Display Help Dialog (Alt+3)"));
  connect(action, SIGNAL(activated()), mw, SLOT(slotHelp()));
  actions.replace(Help, action);

  action = new QAction(this, "actionAdvancePaperTrade");
  action->setAccel(CTRL+Key_Right);
  connect(action, SIGNAL(activated()), this, SIGNAL(signalAdvancePaperTrade()));
  actions.replace(AdvancePaperTrade, action);

  action = new QAction(this, "actionIndicatorSummary");
  action->setMenuText(tr("Indicator Summary"));
  action->setStatusTip(tr("Indicator Summary"));
  action->setToolTip(tr("Indicator Summary"));
  connect(action, SIGNAL(activated()), mw, SLOT(slotIndicatorSummary()));
  actions.replace(IndicatorSummary, action);
  
  QAccel *a = new QAccel(mw);
  connect(a, SIGNAL(activated(int)), this, SLOT(slotAccel(int)));
  a->insertItem(CTRL+Key_2, NewIndicator);
  a->insertItem(CTRL+Key_3, Options);
  a->insertItem(CTRL+Key_4, Grid);
  a->insertItem(CTRL+Key_5, ScaleToScreen);
  a->insertItem(CTRL+Key_6, Crosshairs);
  a->insertItem(CTRL+Key_7, SidePanel);
  a->insertItem(CTRL+Key_0, DrawMode);
  a->insertItem(CTRL+Key_Y, Quotes);
  a->insertItem(CTRL+Key_Right, AdvancePaperTrade);
  
  a->insertItem(CTRL+Key_Escape, 8);
  
  createMenus();
  
  rcfile.loadData(RcFile::ShowMenuBar, b);
  if (!b)
    hide();
}

MainMenubar::~MainMenubar ()
{
}

void MainMenubar::createMenus ()
{
  fileMenu = new QPopupMenu();
  actions[Exit]->addTo(fileMenu);

  editMenu = new QPopupMenu();
  actions[NewIndicator]->addTo(editMenu);
  actions[Options]->addTo(editMenu);

  viewMenu = new QPopupMenu();
  viewMenu->setCheckable(true);
  actions[Grid]->addTo(viewMenu);
  actions[ScaleToScreen]->addTo(viewMenu);
  actions[SidePanel]->addTo(viewMenu);
  actions[DrawMode]->addTo(viewMenu);
  actions[Crosshairs]->addTo(viewMenu);
  actions[PaperTrade]->addTo(viewMenu);

  toolMenu = new QPopupMenu();
  actions[DataWindow]->addTo(toolMenu);
  actions[IndicatorSummary]->addTo(toolMenu);
  actions[Quotes]->addTo(toolMenu);

  helpMenu = new QPopupMenu();
  actions[About]->addTo(helpMenu);
  actions[Help]->addTo(helpMenu);
  
  insertItem(tr("&File"), fileMenu);
  insertItem(tr("&Edit"), editMenu);
  insertItem(tr("&View"), viewMenu);
  insertItem(tr("&Tools"), toolMenu);
  insertSeparator();
  insertItem(tr("&Help"), helpMenu);
}

QAction * MainMenubar::getAction (int d)
{
  return actions[d];
}

bool MainMenubar::getStatus (int d)
{
  return actions[d]->isOn();
}

void MainMenubar::setStatus (int d, bool f)
{
  actions[d]->setOn(f);
}

void MainMenubar::saveSettings ()
{
  RcFile rcfile;
  rcfile.saveData(RcFile::DrawMode, getStatus(DrawMode));
  rcfile.saveData(RcFile::ScaleToScreen, getStatus(ScaleToScreen));
  rcfile.saveData(RcFile::Grid, getStatus(Grid));
  rcfile.saveData(RcFile::Crosshairs, getStatus(Crosshairs));
  rcfile.saveData(RcFile::PaperTradeMode, getStatus(PaperTrade));
  rcfile.saveData(RcFile::ShowSidePanel, getStatus(SidePanel));
}

void MainMenubar::slotAccel (int id)
{
  switch (id)
  {
    case NewIndicator:
      emit signalNewIndicator();
      break;
    case Options:
      emit signalOptions();
      break;
    case Grid:
      getAction(Grid)->toggle();
      break;
    case Quotes:
      emit signalQuotes();
      break;
    case ScaleToScreen:
      getAction(ScaleToScreen)->toggle();
      break;
    case SidePanel:
      getAction(SidePanel)->toggle();
      break;
    case DrawMode:
      getAction(DrawMode)->toggle();
      break;
    case Crosshairs:
      getAction(Crosshairs)->toggle();
      break;
    case AdvancePaperTrade:
      emit signalAdvancePaperTrade();
      break;
    default:
      break;
  }
}

void MainMenubar::doKeyPress (QKeyEvent *key)
{
  key->accept();

  if (key->state() == Qt::ControlButton)
  {
    switch (key->key())
    {
      case Qt::Key_2:
	slotAccel(NewIndicator);
        break;
      case Qt::Key_3:
	slotAccel(Options);
        break;
      case Qt::Key_4:
	slotAccel(Grid);
        break;
      case Qt::Key_5:
	slotAccel(ScaleToScreen);
        break;
      case Qt::Key_7:
	slotAccel(SidePanel);
        break;
      case Qt::Key_0:
	slotAccel(DrawMode);
        break;
      case Qt::Key_6:
	slotAccel(Crosshairs);
        break;
      case Qt::Key_Y:
        slotAccel(Quotes);
        break;
      case Qt::Key_Right:
        slotAccel(AdvancePaperTrade);
        break;
      default:
        break;
    }
  }
}

