# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(984, 751)
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox_plots = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_plots.setObjectName(_fromUtf8("groupBox_plots"))
        self.plotLayout = QtGui.QVBoxLayout(self.groupBox_plots)
        self.plotLayout.setObjectName(_fromUtf8("plotLayout"))
        self.gridLayout.addWidget(self.groupBox_plots, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 984, 18))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget = QtGui.QDockWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidget.sizePolicy().hasHeightForWidth())
        self.dockWidget.setSizePolicy(sizePolicy)
        self.dockWidget.setMinimumSize(QtCore.QSize(330, 697))
        self.dockWidget.setMaximumSize(QtCore.QSize(330, 524287))
        self.dockWidget.setFloating(False)
        self.dockWidget.setObjectName(_fromUtf8("dockWidget"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_input = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox_input.setObjectName(_fromUtf8("groupBox_input"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_input)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_5 = QtGui.QLabel(self.groupBox_input)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 5, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox_input)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 4, 0, 1, 1)
        self.lineEdit_2 = QtGui.QLineEdit(self.groupBox_input)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.gridLayout_2.addWidget(self.lineEdit_2, 1, 1, 1, 3)
        self.label = QtGui.QLabel(self.groupBox_input)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_input)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 1)
        self.lineEdit_3 = QtGui.QLineEdit(self.groupBox_input)
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.gridLayout_2.addWidget(self.lineEdit_3, 4, 1, 1, 3)
        self.label_4 = QtGui.QLabel(self.groupBox_input)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 8, 0, 1, 1)
        self.lineEdit_4 = QtGui.QLineEdit(self.groupBox_input)
        self.lineEdit_4.setObjectName(_fromUtf8("lineEdit_4"))
        self.gridLayout_2.addWidget(self.lineEdit_4, 8, 1, 1, 3)
        self.lineEdit_5 = QtGui.QLineEdit(self.groupBox_input)
        self.lineEdit_5.setObjectName(_fromUtf8("lineEdit_5"))
        self.gridLayout_2.addWidget(self.lineEdit_5, 5, 1, 1, 3)
        self.label_7 = QtGui.QLabel(self.groupBox_input)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_2.addWidget(self.label_7, 7, 0, 1, 1)
        self.lineEdit_6 = QtGui.QLineEdit(self.groupBox_input)
        self.lineEdit_6.setObjectName(_fromUtf8("lineEdit_6"))
        self.gridLayout_2.addWidget(self.lineEdit_6, 7, 1, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.groupBox_input)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout_2.addWidget(self.lineEdit, 2, 1, 1, 3)
        self.lineEdit_7 = QtGui.QLineEdit(self.groupBox_input)
        self.lineEdit_7.setObjectName(_fromUtf8("lineEdit_7"))
        self.gridLayout_2.addWidget(self.lineEdit_7, 7, 3, 1, 1)
        self.label_8 = QtGui.QLabel(self.groupBox_input)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_2.addWidget(self.label_8, 7, 2, 1, 1)
        self.label_MODE = QtGui.QLabel(self.groupBox_input)
        self.label_MODE.setObjectName(_fromUtf8("label_MODE"))
        self.gridLayout_2.addWidget(self.label_MODE, 0, 0, 1, 4)
        self.verticalLayout.addWidget(self.groupBox_input)
        self.groupBox_magnets = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox_magnets.setObjectName(_fromUtf8("groupBox_magnets"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_magnets)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.checkBox_deguassQ = QtGui.QCheckBox(self.groupBox_magnets)
        self.checkBox_deguassQ.setObjectName(_fromUtf8("checkBox_deguassQ"))
        self.verticalLayout_3.addWidget(self.checkBox_deguassQ)
        self.checkBox_deguassD = QtGui.QCheckBox(self.groupBox_magnets)
        self.checkBox_deguassD.setObjectName(_fromUtf8("checkBox_deguassD"))
        self.verticalLayout_3.addWidget(self.checkBox_deguassD)
        self.checkBox_deguassC = QtGui.QCheckBox(self.groupBox_magnets)
        self.checkBox_deguassC.setObjectName(_fromUtf8("checkBox_deguassC"))
        self.verticalLayout_3.addWidget(self.checkBox_deguassC)
        self.checkBox_deguassS = QtGui.QCheckBox(self.groupBox_magnets)
        self.checkBox_deguassS.setObjectName(_fromUtf8("checkBox_deguassS"))
        self.verticalLayout_3.addWidget(self.checkBox_deguassS)
        self.checkBox_quadOff = QtGui.QCheckBox(self.groupBox_magnets)
        self.checkBox_quadOff.setObjectName(_fromUtf8("checkBox_quadOff"))
        self.verticalLayout_3.addWidget(self.checkBox_quadOff)
        self.checkBox_corrOff = QtGui.QCheckBox(self.groupBox_magnets)
        self.checkBox_corrOff.setObjectName(_fromUtf8("checkBox_corrOff"))
        self.verticalLayout_3.addWidget(self.checkBox_corrOff)
        self.verticalLayout.addWidget(self.groupBox_magnets)
        self.groupBox_method = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox_method.setObjectName(_fromUtf8("groupBox_method"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.groupBox_method)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.checkBox_all = QtGui.QCheckBox(self.groupBox_method)
        self.checkBox_all.setChecked(True)
        self.checkBox_all.setObjectName(_fromUtf8("checkBox_all"))
        self.verticalLayout_4.addWidget(self.checkBox_all)
        self.checkBox_1 = QtGui.QCheckBox(self.groupBox_method)
        self.checkBox_1.setChecked(True)
        self.checkBox_1.setObjectName(_fromUtf8("checkBox_1"))
        self.verticalLayout_4.addWidget(self.checkBox_1)
        self.checkBox_2 = QtGui.QCheckBox(self.groupBox_method)
        self.checkBox_2.setChecked(True)
        self.checkBox_2.setObjectName(_fromUtf8("checkBox_2"))
        self.verticalLayout_4.addWidget(self.checkBox_2)
        self.checkBox_3 = QtGui.QCheckBox(self.groupBox_method)
        self.checkBox_3.setChecked(True)
        self.checkBox_3.setObjectName(_fromUtf8("checkBox_3"))
        self.verticalLayout_4.addWidget(self.checkBox_3)
        self.checkBox_4 = QtGui.QCheckBox(self.groupBox_method)
        self.checkBox_4.setChecked(True)
        self.checkBox_4.setObjectName(_fromUtf8("checkBox_4"))
        self.verticalLayout_4.addWidget(self.checkBox_4)
        self.pushButton_run = QtGui.QPushButton(self.groupBox_method)
        self.pushButton_run.setMinimumSize(QtCore.QSize(0, 100))
        self.pushButton_run.setObjectName(_fromUtf8("pushButton_run"))
        self.verticalLayout_4.addWidget(self.pushButton_run)
        self.verticalLayout.addWidget(self.groupBox_method)
        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget)
        self.actionSave_Calibation_Data = QtGui.QAction(MainWindow)
        self.actionSave_Calibation_Data.setObjectName(_fromUtf8("actionSave_Calibation_Data"))
        self.menuFile.addAction(self.actionSave_Calibation_Data)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.lineEdit_2, self.lineEdit_3)
        MainWindow.setTabOrder(self.lineEdit_3, self.lineEdit_4)
        MainWindow.setTabOrder(self.lineEdit_4, self.checkBox_deguassQ)
        MainWindow.setTabOrder(self.checkBox_deguassQ, self.checkBox_deguassD)
        MainWindow.setTabOrder(self.checkBox_deguassD, self.checkBox_deguassC)
        MainWindow.setTabOrder(self.checkBox_deguassC, self.checkBox_deguassS)
        MainWindow.setTabOrder(self.checkBox_deguassS, self.checkBox_1)
        MainWindow.setTabOrder(self.checkBox_1, self.checkBox_3)
        MainWindow.setTabOrder(self.checkBox_3, self.checkBox_4)
        MainWindow.setTabOrder(self.checkBox_4, self.pushButton_run)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Phase Calibration", None))
        self.groupBox_plots.setTitle(_translate("MainWindow", "Phase Calibration Plots", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.dockWidget.setWindowTitle(_translate("MainWindow", "Phase Calibration Settings", None))
        self.groupBox_input.setTitle(_translate("MainWindow", "Input", None))
        self.label_5.setText(_translate("MainWindow", "Number of Scanning Points", None))
        self.label_3.setText(_translate("MainWindow", "Number of Shots (per point)", None))
        self.lineEdit_2.setText(_translate("MainWindow", "4.5", None))
        self.label.setText(_translate("MainWindow", "Desitred Momentum", None))
        self.label_2.setText(_translate("MainWindow", "Desirsed off-crest Phase", None))
        self.lineEdit_3.setText(_translate("MainWindow", "10", None))
        self.label_4.setText(_translate("MainWindow", "Range (Degrees)", None))
        self.lineEdit_4.setText(_translate("MainWindow", "20", None))
        self.lineEdit_5.setText(_translate("MainWindow", "20", None))
        self.label_7.setText(_translate("MainWindow", "Approx. Range (Degrees)", None))
        self.lineEdit_6.setText(_translate("MainWindow", "-115", None))
        self.lineEdit.setText(_translate("MainWindow", "-15", None))
        self.lineEdit_7.setText(_translate("MainWindow", "-75", None))
        self.label_8.setText(_translate("MainWindow", "to", None))
        self.label_MODE.setText(_translate("MainWindow", "Mode", None))
        self.groupBox_magnets.setTitle(_translate("MainWindow", "Magnets", None))
        self.checkBox_deguassQ.setText(_translate("MainWindow", "Deguass Quadruoles", None))
        self.checkBox_deguassD.setText(_translate("MainWindow", "Deguass Dipoles", None))
        self.checkBox_deguassC.setText(_translate("MainWindow", "Deguass Correctors", None))
        self.checkBox_deguassS.setText(_translate("MainWindow", "Deguass Solenoids", None))
        self.checkBox_quadOff.setText(_translate("MainWindow", "Turn Off Quads", None))
        self.checkBox_corrOff.setText(_translate("MainWindow", "Turn Off Correctors", None))
        self.groupBox_method.setTitle(_translate("MainWindow", "Method", None))
        self.checkBox_all.setText(_translate("MainWindow", "All", None))
        self.checkBox_1.setText(_translate("MainWindow", "1. Setup Magnets", None))
        self.checkBox_2.setText(_translate("MainWindow", "2.Aprroximately Find Crest with WCM", None))
        self.checkBox_3.setText(_translate("MainWindow", "3. Find Crest with BPM", None))
        self.checkBox_4.setText(_translate("MainWindow", "4. Set Momentum of Beam", None))
        self.pushButton_run.setText(_translate("MainWindow", "Run", None))
        self.actionSave_Calibation_Data.setText(_translate("MainWindow", "Save Calibation Data", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

