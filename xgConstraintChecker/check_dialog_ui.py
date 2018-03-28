# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\clairel\.qgis2\python\plugins\xgConstraintChecker\check_dialog_base.ui'
#
# Created: Tue Mar 27 16:25:11 2018
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_check_dialog(object):
    def setupUi(self, check_dialog):
        check_dialog.setObjectName(_fromUtf8("check_dialog"))
        check_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        check_dialog.resize(443, 401)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(check_dialog.sizePolicy().hasHeightForWidth())
        check_dialog.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/xgConstraintChecker/checker_config.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        check_dialog.setWindowIcon(icon)
        check_dialog.setModal(False)
        self.buttonBox = QtGui.QDialogButtonBox(check_dialog)
        self.buttonBox.setGeometry(QtCore.QRect(260, 360, 171, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.grp_check = QtGui.QGroupBox(check_dialog)
        self.grp_check.setGeometry(QtCore.QRect(10, 10, 421, 341))
        self.grp_check.setObjectName(_fromUtf8("grp_check"))
        self.chk_word_report = QtGui.QCheckBox(self.grp_check)
        self.chk_word_report.setGeometry(QtCore.QRect(10, 220, 141, 17))
        self.chk_word_report.setObjectName(_fromUtf8("chk_word_report"))
        self.grp_report = QtGui.QGroupBox(self.grp_check)
        self.grp_report.setGeometry(QtCore.QRect(10, 240, 401, 91))
        self.grp_report.setObjectName(_fromUtf8("grp_report"))
        self.lbl_report_name = QtGui.QLabel(self.grp_report)
        self.lbl_report_name.setGeometry(QtCore.QRect(10, 20, 81, 16))
        self.lbl_report_name.setObjectName(_fromUtf8("lbl_report_name"))
        self.lbl_created_by = QtGui.QLabel(self.grp_report)
        self.lbl_created_by.setGeometry(QtCore.QRect(10, 60, 71, 16))
        self.lbl_created_by.setObjectName(_fromUtf8("lbl_created_by"))
        self.txt_word_report = QtGui.QPlainTextEdit(self.grp_report)
        self.txt_word_report.setGeometry(QtCore.QRect(100, 20, 261, 31))
        self.txt_word_report.setObjectName(_fromUtf8("txt_word_report"))
        self.btn_browse = QtGui.QPushButton(self.grp_report)
        self.btn_browse.setGeometry(QtCore.QRect(370, 20, 23, 23))
        self.btn_browse.setObjectName(_fromUtf8("btn_browse"))
        self.txt_created_by = QtGui.QPlainTextEdit(self.grp_report)
        self.txt_created_by.setGeometry(QtCore.QRect(100, 60, 261, 21))
        self.txt_created_by.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txt_created_by.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txt_created_by.setObjectName(_fromUtf8("txt_created_by"))
        self.lst_checks = QtGui.QListWidget(self.grp_check)
        self.lst_checks.setGeometry(QtCore.QRect(10, 20, 401, 192))
        self.lst_checks.setObjectName(_fromUtf8("lst_checks"))

        self.retranslateUi(check_dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), check_dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), check_dialog.reject)
        QtCore.QObject.connect(self.chk_word_report, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.grp_report.setEnabled)
        QtCore.QObject.connect(self.btn_browse, QtCore.SIGNAL(_fromUtf8("clicked()")), check_dialog.openFileDialog)
        QtCore.QObject.connect(self.lst_checks, QtCore.SIGNAL(_fromUtf8("itemDoubleClicked(QListWidgetItem*)")), check_dialog.runSelected)
        QtCore.QMetaObject.connectSlotsByName(check_dialog)
        check_dialog.setTabOrder(self.lst_checks, self.chk_word_report)
        check_dialog.setTabOrder(self.chk_word_report, self.txt_word_report)
        check_dialog.setTabOrder(self.txt_word_report, self.btn_browse)
        check_dialog.setTabOrder(self.btn_browse, self.txt_created_by)
        check_dialog.setTabOrder(self.txt_created_by, self.buttonBox)

    def retranslateUi(self, check_dialog):
        check_dialog.setWindowTitle(_translate("check_dialog", "xgConstraintChecker", None))
        self.grp_check.setTitle(_translate("check_dialog", "Select Constraint Check to run:", None))
        self.chk_word_report.setText(_translate("check_dialog", "Produce Word report", None))
        self.grp_report.setTitle(_translate("check_dialog", "Report Details:", None))
        self.lbl_report_name.setText(_translate("check_dialog", "Save report as:", None))
        self.lbl_created_by.setText(_translate("check_dialog", "Created by:", None))
        self.btn_browse.setText(_translate("check_dialog", "...", None))

import resources_rc
