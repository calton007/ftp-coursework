# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import time

ISOTIMEFORMAT = '%Y-%m-%d %X'
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(400, 197)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30, 50, 101, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.textEdit = QtGui.QLineEdit(Dialog)
        self.textEdit.setGeometry(QtCore.QRect(90, 80, 211, 31))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.confirmButton = QtGui.QPushButton(Dialog)
        self.confirmButton.setGeometry(QtCore.QRect(70, 140, 93, 28))
        self.confirmButton.setObjectName(_fromUtf8("confirmButton"))
        self.cancelButton = QtGui.QPushButton(Dialog)
        self.cancelButton.setGeometry(QtCore.QRect(230, 140, 93, 28))
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "请输入名字：", None))
        self.confirmButton.setText(_translate("Dialog", "确定", None))
        self.cancelButton.setText(_translate("Dialog", "取消", None))


# 重命名类
class Rename(QtGui.QMainWindow):
    ftp = None
    live = None
    status = 0
    mainwin = None
    select = None
    def __init__(self, t, parent = None):
        self.mainwin = t
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle(u"重命名")
        self.ui.textEdit.setText(self.mainwin.ui.treeWidget.currentItem().text(0))
        self.ui.cancelButton.clicked.connect(self.cancel_button_action)
        self.ui.confirmButton.clicked.connect(self.confirm_button_action)

    def cancel_button_action(self):
        self.close()

    def confirm_button_action(self):
        cur = self.mainwin.ui.treeWidget.currentItem()  # 获取操作对象
        times = 0
        parent = ''  # 路径
        temp = cur.parent()
        while str(temp.text(0)) != self.mainwin.ftp.host:  # 生成路径
            parent = r'/' + str(temp.text(0)) + r'/' + parent
            temp = temp.parent()
            times += 1
        self.mainwin.ftp.cwd(parent)     # 进入路径
        self.mainwin.ftp.rename(str(cur.text(0)), str(self.ui.textEdit.text()))
        s = time.strftime(ISOTIMEFORMAT, time.localtime()) + u'\t\t%s重命名成功' % (str(cur.text(0)),)
        self.mainwin.ui.plainTextEdit.appendPlainText(QtCore.QString(s))
        while times > 0:
            self.mainwin.ftp.cwd('..')
            times -= 1
        self.mainwin.refresh()
        self.close()


# 新建文件夹类
class Newfile(QtGui.QMainWindow):
    ftp = None
    live = None
    status = 0
    mainwin = None

    def __init__(self, t, parent = None):
        self.mainwin = t    # 获取传入对象
        QtGui.QWidget.__init__(self,parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle(u"新建文件夹")
        self.ui.textEdit.setText(u'New File')
        self.ui.cancelButton.clicked.connect(self.cancel_button_action)
        self.ui.confirmButton.clicked.connect(self.confirm_button_action)

    def cancel_button_action(self):
        self.close()

    # 确认按钮事件
    def confirm_button_action(self):
        cur = self.mainwin.ui.treeWidget.currentItem()  # 获取操作对象
        times = 1
        parent = ''  # 路径
        if not cur:     # 如果未选择，默认在根目录下新建
            cur = self.mainwin.root
        if cur != self.mainwin.root:
            temp = cur.parent()
            while str(temp.text(0)) != self.mainwin.ftp.host:  # 遍历路径
                parent = '/' + str(temp.text(0)) + '/' + parent
                temp = temp.parent()
                times += 1
            parent += '/' + str(cur.text(0)) + '/'
        self.mainwin.ftp.cwd(parent)    # 进入文件夹
        self.mainwin.ftp.mkd(str(self.ui.textEdit.text()))  # 新建文件
        s = time.strftime(ISOTIMEFORMAT, time.localtime()) + u'\t\t新建文件夹%s成功' % (str(self.ui.textEdit.text()),)
        self.mainwin.ui.plainTextEdit.appendPlainText(QtCore.QString(s))
        while times > 0:
            self.mainwin.ftp.cwd('..')
            times -= 1
        self.mainwin.refresh()
        self.close()
