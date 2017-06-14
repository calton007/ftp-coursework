# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/dialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from FTPClient import FTP
from MainWindow import FTPMainWindow
import sys
from PyQt4.QtGui import *

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

class Login_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(400, 260)
        self.hostlabel = QtGui.QLabel(Dialog)
        self.hostlabel.setGeometry(QtCore.QRect(40, 50, 72, 15))
        self.hostlabel.setObjectName(_fromUtf8("hostlabel"))
        self.userlabel = QtGui.QLabel(Dialog)
        self.userlabel.setGeometry(QtCore.QRect(40, 90, 72, 15))
        self.userlabel.setObjectName(_fromUtf8("userlabel"))
        self.passwordlabel = QtGui.QLabel(Dialog)
        self.passwordlabel.setGeometry(QtCore.QRect(40, 130, 72, 15))
        self.passwordlabel.setObjectName(_fromUtf8("passwordlabel"))
        self.anonymouscheckBox = QtGui.QCheckBox(Dialog)
        self.anonymouscheckBox.setGeometry(QtCore.QRect(270, 50, 91, 19))
        self.anonymouscheckBox.setChecked(False)
        self.anonymouscheckBox.setObjectName(_fromUtf8("anonymouscheckBox"))
        self.hostEdit = QtGui.QLineEdit(Dialog)
        self.hostEdit.setGeometry(QtCore.QRect(120, 50, 131, 21))
        self.hostEdit.setObjectName(_fromUtf8("hostEdit"))
        self.userEdit = QtGui.QLineEdit(Dialog)
        self.userEdit.setGeometry(QtCore.QRect(120, 90, 131, 21))
        self.userEdit.setObjectName(_fromUtf8("userEdit_2"))
        self.passwordEdit = QtGui.QLineEdit(Dialog)
        self.passwordEdit.setGeometry(QtCore.QRect(120, 130, 131, 21))
        self.passwordEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordEdit.setObjectName(_fromUtf8("passwordEdit_3"))
        self.loginButton = QtGui.QPushButton(Dialog)
        self.loginButton.setGeometry(QtCore.QRect(70, 200, 93, 28))
        self.loginButton.setObjectName(_fromUtf8("loginButton"))
        self.CancelButton = QtGui.QPushButton(Dialog)
        self.CancelButton.setGeometry(QtCore.QRect(220, 200, 93, 28))
        self.CancelButton.setObjectName(_fromUtf8("CancelButton"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.hostlabel.setText(_translate("Dialog", "主  机", None))
        self.userlabel.setText(_translate("Dialog", "用户名", None))
        self.passwordlabel.setText(_translate("Dialog", "密  码", None))
        self.anonymouscheckBox.setText(_translate("Dialog", "匿名", None))
        self.loginButton.setText(_translate("Dialog", "连接", None))
        self.CancelButton.setText(_translate("Dialog", "取消", None))

class FTP_LOGIN_UI(QtGui.QMainWindow):
    ftp = None
    live = None
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.ui = Login_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle(u"FTP客户端")
        # 调试用
        self.ui.hostEdit.setText('127.0.0.1')
        self.ui.userEdit.setText('test')
        self.ui.passwordEdit.setText('test')
        self.ui.anonymouscheckBox.clicked.connect(self.anonymouscheckBox_Checked)
        self.ui.CancelButton.clicked.connect(self.exit_click)
        self.ui.loginButton.clicked.connect(self.login)
        self.show()

    def anonymouscheckBox_Checked(self):
        if(not self.ui.anonymouscheckBox.isChecked()):
            self.ui.userEdit.setEnabled(True)
            self.ui.userEdit.setText('')
            self.ui.passwordEdit.setEnabled(True)
            self.ui.passwordEdit.setText('')
        else:
            self.ui.userEdit.setEnabled(False)
            self.ui.userEdit.setText('anonymous')
            self.ui.passwordEdit.setEnabled(False)
            self.ui.passwordEdit.setText('anonymous@')

    def login(self):
        host = str(self.ui.hostEdit.text())
        user = str(self.ui.userEdit.text())
        password = str(self.ui.passwordEdit.text())
        self.ftp = FTP(host, user, password)
        if self.ftp.status == '230':
            QtGui.QMessageBox.information(self, u'FTP客户端', u'登录成功', QtGui.QMessageBox.Yes)
            self.live = self.ftp.live
            self.close()
            self.m = FTPMainWindow(self.ftp)
            self.m.show()
        else:
            QtGui.QMessageBox.information(self, u'FTP客户端', u'登录失败', QtGui.QMessageBox.Yes)
            self.ui.userEdit.setText('')
            self.ui.passwordEdit.setText('')

    def exit_click(self):
        if self.live:
            self.ftp.quit()
        sys.exit()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    my = FTP_LOGIN_UI()
    app.setWindowIcon(QtGui.QIcon('4.ico'))
    app.exec_()
    app = QApplication(sys.argv)

