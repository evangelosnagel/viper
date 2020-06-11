# -*- coding: utf-8 -*-



from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        ##### Display of RV plots #####
        self.RV_fit = QtWidgets.QGroupBox(self.centralwidget)
        self.RV_fit.setGeometry(QtCore.QRect(10, 180, 491, 371))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Mono")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.RV_fit.setFont(font)
        self.RV_fit.setObjectName("RV_fit")
        self.tabWidget = QtWidgets.QTabWidget(self.RV_fit)
        self.tabWidget.setGeometry(QtCore.QRect(10, 30, 461, 331))
        self.tabWidget.setObjectName("tabWidget")

        ### RV fit tab ######
        self.fit_tab = QtWidgets.QWidget()
        self.fit_tab.setObjectName("fit_tab")
        self.tabWidget.addTab(self.fit_tab, "")

        ### IP fit tab ######
        self.IP_tab = QtWidgets.QWidget()
        self.IP_tab.setObjectName("IP_tab")
        self.tabWidget.addTab(self.IP_tab, "")

        #### Data loading  ####
        self.load_data = QtWidgets.QGroupBox(self.centralwidget)
        self.load_data.setGeometry(QtCore.QRect(510, 10, 261, 131))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Mono")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.load_data.setFont(font)
        self.load_data.setObjectName("load_data")

        #### Results of the FIT  ####     
        self.fit_details = QtWidgets.QGroupBox(self.centralwidget)
        self.fit_details.setGeometry(QtCore.QRect(510, 180, 261, 371))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Mono")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.fit_details.setFont(font)
        self.fit_details.setObjectName("fit_details")
        self.textBrowser = QtWidgets.QTextBrowser(self.fit_details)
        self.textBrowser.setGeometry(QtCore.QRect(10, 30, 241, 331))
        self.textBrowser.setObjectName("textBrowser")

        #### Input parameters of the FIT ####           
        self.fit_params = QtWidgets.QGroupBox(self.centralwidget)
        self.fit_params.setGeometry(QtCore.QRect(20, 10, 481, 131))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Mono")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.fit_params.setFont(font)
        self.fit_params.setObjectName("fit_params")

        #### Compute RV push button #####
        self.compute_rv = QtWidgets.QPushButton(self.centralwidget)
        self.compute_rv.setGeometry(QtCore.QRect(260, 150, 131, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(136, 138, 133))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(136, 138, 133))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(136, 138, 133))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(190, 190, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.compute_rv.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Ubuntu Mono")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.compute_rv.setFont(font)
        self.compute_rv.setObjectName("compute_rv")

        #### Menu bar File ####
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionNew_Session = QtWidgets.QAction(MainWindow)
        self.actionNew_Session.setObjectName("actionNew_Session")
        self.actionSave_Session = QtWidgets.QAction(MainWindow)
        self.actionSave_Session.setObjectName("actionSave_Session")
        self.actionOpen_Session = QtWidgets.QAction(MainWindow)
        self.actionOpen_Session.setObjectName("actionOpen_Session")
        self.actionQuit_Session = QtWidgets.QAction(MainWindow)
        self.actionQuit_Session.setObjectName("actionQuit_Session")
        self.menuFile.addAction(self.actionNew_Session)
        self.menuFile.addAction(self.actionOpen_Session)
        self.menuFile.addAction(self.actionSave_Session)
        self.menuFile.addAction(self.actionQuit_Session)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.RV_fit.setTitle(_translate("MainWindow", "Radial Velocity Fit"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.fit_tab), _translate("MainWindow", "RV Fit"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.IP_tab), _translate("MainWindow", "IP Fit"))
        self.load_data.setTitle(_translate("MainWindow", "Load Data"))
        self.fit_details.setTitle(_translate("MainWindow", "Fit Details"))
        self.fit_params.setTitle(_translate("MainWindow", "Fit Parameters"))
        self.compute_rv.setText(_translate("MainWindow", "Compute RV"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionNew_Session.setText(_translate("MainWindow", "New Session"))
        self.actionSave_Session.setText(_translate("MainWindow", "Save Session"))
        self.actionOpen_Session.setText(_translate("MainWindow", "Open Session"))
        self.actionQuit_Session.setText(_translate("MainWindow", "Quit Session"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
