# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 261)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.cBox_Ports = QtWidgets.QComboBox(self.centralwidget)
        self.cBox_Ports.setGeometry(QtCore.QRect(100, 30, 161, 22))
        self.cBox_Ports.setObjectName("cBox_Ports")
        self.cBox_BaudRates = QtWidgets.QComboBox(self.centralwidget)
        self.cBox_BaudRates.setGeometry(QtCore.QRect(100, 70, 161, 22))
        self.cBox_BaudRates.setObjectName("cBox_BaudRates")
        self.cBox_BaudRates.addItem("")
        self.cBox_BaudRates.addItem("")
        self.btn_ReadData = QtWidgets.QPushButton(self.centralwidget)
        self.btn_ReadData.setGeometry(QtCore.QRect(110, 120, 141, 41))
        self.btn_ReadData.setObjectName("btn_ReadData")
        self.txt_Results = QtWidgets.QTextBrowser(self.centralwidget)
        self.txt_Results.setGeometry(QtCore.QRect(340, 10, 391, 151))
        self.txt_Results.setObjectName("txt_Results")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(40, 30, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(40, 70, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.tBtn_UpdatePorts = QtWidgets.QToolButton(self.centralwidget)
        self.tBtn_UpdatePorts.setGeometry(QtCore.QRect(270, 30, 25, 19))
        self.tBtn_UpdatePorts.setObjectName("tBtn_UpdatePorts")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.cBox_BaudRates.setItemText(0, _translate("MainWindow", "9600"))
        self.cBox_BaudRates.setItemText(1, _translate("MainWindow", "115200"))
        self.btn_ReadData.setText(_translate("MainWindow", "Read"))
        self.label.setText(_translate("MainWindow", "Ports"))
        self.label_2.setText(_translate("MainWindow", "BR"))
        self.tBtn_UpdatePorts.setText(_translate("MainWindow", "..."))
