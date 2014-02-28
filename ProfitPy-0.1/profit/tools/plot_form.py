# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plot_form.ui'
#
# Created: Mon Apr 19 12:04:55 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.8.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class PlotForm(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("PlotForm")

        self.setMinimumSize(QSize(800,600))

        PlotFormLayout = QGridLayout(self,1,1,11,6,"PlotFormLayout")

        layout2 = QHBoxLayout(None,0,6,"layout2")
        spacer = QSpacerItem(571,21,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout2.addItem(spacer)

        self.openButton = QPushButton(self,"openButton")
        layout2.addWidget(self.openButton)

        self.exitButton = QPushButton(self,"exitButton")
        layout2.addWidget(self.exitButton)

        PlotFormLayout.addLayout(layout2,1,0)

        self.splitter2 = QSplitter(self,"splitter2")
        self.splitter2.setSizePolicy(QSizePolicy(7,5,3,0,self.splitter2.sizePolicy().hasHeightForWidth()))
        self.splitter2.setOrientation(QSplitter.Horizontal)

        self.tickersListView = QListView(self.splitter2,"tickersListView")
        self.tickersListView.addColumn(self.__tr("Id"))
        self.tickersListView.addColumn(self.__tr("Symbol"))
        self.tickersListView.addColumn(self.__tr("Length"))
        self.tickersListView.setSizePolicy(QSizePolicy(7,7,1,0,self.tickersListView.sizePolicy().hasHeightForWidth()))
        self.tickersListView.setMinimumSize(QSize(0,0))
        self.tickersListView.setResizePolicy(QScrollView.Manual)
        self.tickersListView.setVScrollBarMode(QListView.Auto)
        self.tickersListView.setSelectionMode(QListView.Single)
        self.tickersListView.setAllColumnsShowFocus(1)
        self.tickersListView.setShowSortIndicator(1)
        self.tickersListView.setResizeMode(QListView.AllColumns)

        self.stdoutTextEdit = QTextEdit(self.splitter2,"stdoutTextEdit")
        self.stdoutTextEdit.setSizePolicy(QSizePolicy(7,7,2,0,self.stdoutTextEdit.sizePolicy().hasHeightForWidth()))
        self.stdoutTextEdit.setMinimumSize(QSize(0,0))
        stdoutTextEdit_font = QFont(self.stdoutTextEdit.font())
        stdoutTextEdit_font.setFamily("Bitstream Vera Sans Mono")
        self.stdoutTextEdit.setFont(stdoutTextEdit_font)
        self.stdoutTextEdit.setResizePolicy(QTextEdit.Manual)
        self.stdoutTextEdit.setVScrollBarMode(QTextEdit.Auto)
        self.stdoutTextEdit.setHScrollBarMode(QTextEdit.Auto)
        self.stdoutTextEdit.setTextFormat(QTextEdit.PlainText)
        self.stdoutTextEdit.setWordWrap(QTextEdit.NoWrap)
        self.stdoutTextEdit.setOverwriteMode(1)

        PlotFormLayout.addWidget(self.splitter2,0,0)

        self.languageChange()

        self.resize(QSize(800,600).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.exitButton,SIGNAL("released()"),self,SLOT("close()"))


    def languageChange(self):
        self.setCaption(self.__tr("Ticker Plot Tool"))
        self.openButton.setText(self.__tr("Open"))
        self.exitButton.setText(self.__tr("Exit"))
        self.tickersListView.header().setLabel(0,self.__tr("Id"))
        self.tickersListView.header().setLabel(1,self.__tr("Symbol"))
        self.tickersListView.header().setLabel(2,self.__tr("Length"))


    def __tr(self,s,c = None):
        return qApp.translate("PlotForm",s,c)
