# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import time
from Dialog import Rename, Newfile


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


class UiMainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(666, 629)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.treeWidget = QtGui.QTreeWidget(self.centralwidget)
        self.treeWidget.setGeometry(QtCore.QRect(20, 40, 441, 391))
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.filegroupBox = QtGui.QGroupBox(self.centralwidget)
        self.filegroupBox.setGeometry(QtCore.QRect(490, 50, 141, 221))
        self.filegroupBox.setObjectName(_fromUtf8("filegroupBox"))
        self.retrButton = QtGui.QPushButton(self.filegroupBox)
        self.retrButton.setGeometry(QtCore.QRect(20, 30, 93, 28))
        self.retrButton.setObjectName(_fromUtf8("retrButton"))
        self.storButton = QtGui.QPushButton(self.filegroupBox)
        self.storButton.setGeometry(QtCore.QRect(20, 80, 93, 28))
        self.storButton.setObjectName(_fromUtf8("storButton"))
        self.renameButton = QtGui.QPushButton(self.filegroupBox)
        self.renameButton.setGeometry(QtCore.QRect(20, 130, 93, 28))
        self.renameButton.setObjectName(_fromUtf8("renameButton"))
        self.deleteButton = QtGui.QPushButton(self.filegroupBox)
        self.deleteButton.setGeometry(QtCore.QRect(20, 180, 93, 28))
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.dirgroupBox = QtGui.QGroupBox(self.centralwidget)
        self.dirgroupBox.setGeometry(QtCore.QRect(489, 300, 141, 131))
        self.dirgroupBox.setObjectName(_fromUtf8("dirgroupBox"))
        self.mkdButton = QtGui.QPushButton(self.dirgroupBox)
        self.mkdButton.setGeometry(QtCore.QRect(20, 30, 93, 28))
        self.mkdButton.setObjectName(_fromUtf8("mkdButton"))
        self.rmdButton = QtGui.QPushButton(self.dirgroupBox)
        self.rmdButton.setGeometry(QtCore.QRect(20, 80, 93, 28))
        self.rmdButton.setObjectName(_fromUtf8("rmdButton"))
        self.plainTextEdit = QtGui.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(20, 470, 611, 111))
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.logLable = QtGui.QLabel(self.centralwidget)
        self.logLable.setGeometry(QtCore.QRect(30, 450, 72, 15))
        self.logLable.setObjectName(_fromUtf8("logLable"))
        self.dirLabel = QtGui.QLabel(self.centralwidget)
        self.dirLabel.setGeometry(QtCore.QRect(30, 10, 72, 15))
        self.dirLabel.setObjectName(_fromUtf8("dirLabel"))
        self.refreshButton = QtGui.QPushButton(self.centralwidget)
        self.refreshButton.setGeometry(QtCore.QRect(412, 10, 41, 28))
        self.refreshButton.setObjectName(_fromUtf8("refreshButton"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 666, 26))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFTP = QtGui.QMenu(self.menubar)
        self.menuFTP.setObjectName(_fromUtf8("menuFTP"))
        self.menu = QtGui.QMenu(self.menubar)
        self.menu.setObjectName(_fromUtf8("menu"))
        MainWindow.setMenuBar(self.menubar)
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionDisconnect = QtGui.QAction(MainWindow)
        self.actionDisconnect.setObjectName(_fromUtf8("actionDisconnect"))
        self.actionHelp = QtGui.QAction(MainWindow)
        self.actionHelp.setObjectName(_fromUtf8("actionHelp"))
        self.actionAbout_me = QtGui.QAction(MainWindow)
        self.actionAbout_me.setObjectName(_fromUtf8("actionAbout_me"))
        self.menuFTP.addAction(self.actionExit)
        self.menu.addAction(self.actionAbout_me)
        self.menubar.addAction(self.menuFTP.menuAction())
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.filegroupBox.setTitle(_translate("MainWindow", "文件操作", None))
        self.retrButton.setText(_translate("MainWindow", "下载文件", None))
        self.storButton.setText(_translate("MainWindow", "上传文件", None))
        self.renameButton.setText(_translate("MainWindow", "重命名", None))
        self.deleteButton.setText(_translate("MainWindow", "删除文件", None))
        self.dirgroupBox.setTitle(_translate("MainWindow", "文件夹操作", None))
        self.mkdButton.setText(_translate("MainWindow", "新建文件夹", None))
        self.rmdButton.setText(_translate("MainWindow", "删除文件夹", None))
        self.logLable.setText(_translate("MainWindow", "操作日志", None))
        self.dirLabel.setText(_translate("MainWindow", "目录", None))
        self.refreshButton.setText(_translate("MainWindow", "刷新", None))
        self.menuFTP.setTitle(_translate("MainWindow", "菜单", None))
        self.menu.setTitle(_translate("MainWindow", "帮助", None))
        self.actionExit.setText(_translate("MainWindow", "退出", None))
        self.actionExit.setToolTip(_translate("MainWindow", "退出", None))
        self.actionAbout_me.setText(_translate("MainWindow", "关于FTP客户端(&A)", None))
        self.actionAbout_me.setToolTip(_translate("MainWindow", "关于FTP客户端", None))


class FTPMainWindow(QtGui.QMainWindow):
    ftp = None
    dialog = None
    di = None

    def __init__(self, ftp, parent=None):
        self.ftp = ftp
        QtGui.QWidget.__init__(self, parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(u"FTP客户端")
        self.ui.actionExit.triggered.connect(self.exit_menu)
        self.ui.retrButton.clicked.connect(self.retr_button_action)
        self.ui.storButton.clicked.connect(self.stor_button_action)
        self.ui.deleteButton.clicked.connect(self.delete_button_action)
        self.ui.actionAbout_me.triggered.connect(self.about_me)
        self.ui.renameButton.clicked.connect(self.rename_button_action)
        self.ui.rmdButton.clicked.connect(self.rmd_button_action)
        self.ui.mkdButton.clicked.connect(self.mkd_button_action)
        self.ui.refreshButton.clicked.connect(self.refresh)

        self.refresh()
        s = time.strftime( ISOTIMEFORMAT, time.localtime() ) + u'\t\t登录成功'
        self.ui.plainTextEdit.appendPlainText(QtCore.QString(s))

    def mkd_button_action(self):
        if self.ui.treeWidget.currentItem().text(1) == QtCore.QString(u"文件夹") or \
                        self.ui.treeWidget.currentItem().text(0) == self.ftp.host :
            self.di = Newfile(self)
            self.di.show()
        else:
            QtGui.QMessageBox.information(self, u'错误', u'请选择一个文件夹！', QtGui.QMessageBox.Yes)

    def delete_dir(self, path):
        self.ftp.cwd(path)
        directory = self.ftp.dir()   # 列出文件夹内容
        if len(directory) > 0:
            for i in range(len(directory) - 1, -1, -1):
                temp = directory[i].split()  # 按空格拆分 0：修改时间  2：文件夹/文件大小 3：文件名
                n = len(temp)
                if n > 9:
                    n -= 9
                    for i in range(1, n + 1):
                        temp[8] += ' ' + temp[8 + i]
                if not temp[8].__contains__('.'):      # 是文件夹
                    print temp[3]
                    self.delete_dir(temp[8])
                else:   # 是文件
                    self.ftp.delete(temp[8])
                    s = time.strftime(ISOTIMEFORMAT, time.localtime()) + u'\t\t删除文件%s成功' % (temp[8],)
                    self.ui.plainTextEdit.appendPlainText(QtCore.QString(s))
        self.ftp.cwd('..')
        self.ftp.rmd(path)
        s = time.strftime(ISOTIMEFORMAT, time.localtime()) + u'\t\t删除文件夹%s成功' % (path,)
        self.ui.plainTextEdit.appendPlainText(QtCore.QString(s))

    def rmd_button_action(self):
        cur = self.ui.treeWidget.currentItem()
        times = 0   # 文件夹深度
        if cur.text(1) == QtCore.QString(u"文件夹"):  # 删除文件夹
            parent = ''  # 路径
            temp = self.ui.treeWidget.currentItem().parent()
            while str(temp.text(0)) != self.ftp.host:  # 遍历路径
                parent = r'/' + str(temp.text(0)) + r'/' + parent
                temp = temp.parent()
                times += 1
            self.ftp.cwd(parent)
            self.delete_dir(str(cur.text(0)))    # 删除文件夹内容
            while times > 0:
                self.ftp.cwd('..')
                times -= 1
            self.refresh()
        else:
            QtGui.QMessageBox.information(self, u'错误', u'请选择一个文件！', QtGui.QMessageBox.Yes)

    def rename_button_action(self):
        if self.ui.treeWidget.currentItem().text(1) != QtCore.QString(u"文件夹"):
            self.di = Rename(self)
            self.di.show()
        else:
            QtGui.QMessageBox.information(self, u'错误', u'请选择一个文件！', QtGui.QMessageBox.Yes)

    def about_me(self):
        QtGui.QMessageBox.information(self, u'FTP客户端',
                                      u'作者：李观波\n班级：计算131\n学号：1206020120                              '
                                      , QtGui.QMessageBox.Yes)

    # 递归生成文件列表
    def tree_widget(self, father):
        directory = self.ftp.dir()   # 获取当前目录下的文件和文件夹信息
        for i in range(len(directory) - 1, -1, -1):
            temp = directory[i].split()  # 按空格拆分 0：修改时间  2：文件夹/文件大小 3：文件名
            n = len(temp)
            if n > 9:
                n -= 9
                for i in range(1, n+1):
                    temp[8] += ' ' + temp[8 + i]
            t = QtGui.QTreeWidgetItem(father)
            t.setText(0, QtCore.QString(temp[8]))   # 设置名字
            if not temp[8].__contains__('.'):
                t.setText(1, u'文件夹')    # 类型为文件夹
                self.ftp.cwd(temp[8])   # 进入该文件夹
                self.tree_widget(t)  # 遍历
                self.ftp.cwd('..')
                t.setFlags(t.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
            else:
                filetype = temp[8].split('.')
                t.setText(1, filetype[1])   # 文件类型
                t.setText(2, temp[4])   # 文件大小
                t.setFlags(t.flags() | QtCore.Qt.ItemIsUserCheckable)
                t.setCheckState(0, QtCore.Qt.Unchecked)

    # 刷新目录
    def refresh(self):
        self.ui.treeWidget.clear()
        self.ui.treeWidget.setHeaderLabels([u'名称', u'类型', u'大小'])
        self.ui.treeWidget.setColumnWidth(0, 200)
        self.ui.treeWidget.setColumnWidth(1, 100)
        self.root = QtGui.QTreeWidgetItem(self.ui.treeWidget)
        self.root.setText(0, str(self.ftp.host))
        self.tree_widget(self.root)
        self.ui.treeWidget.expandItem(self.root)

    def delete_button_action(self):
        for item in self.ui.treeWidget.findItems("", QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive):
            if item.checkState(0) == QtCore.Qt.Checked:
                if item.text(1) != QtCore.QString(u"文件夹"):
                    parent = ''  # 路径
                    temp = item.parent()
                    times = 0
                    while str(temp.text(0)) != self.ftp.host:  # 遍历路径
                        parent = r'/' + str(temp.text(0)) + r'/' + parent
                        temp = temp.parent()
                        times += 1
                    self.ftp.cwd(parent)
                    self.ftp.delete(str(item.text(0)))
                    s = time.strftime(ISOTIMEFORMAT, time.localtime()) + u'\t\t删除%s成功' % (str(item.text(0)),)
                    self.ui.plainTextEdit.appendPlainText(QtCore.QString(s))
                    while times > 0:
                        self.ftp.cwd('..')
                        times -= 1
        self.refresh()

    def stor_button_action(self):
        cur = self.ui.treeWidget.currentItem()  # 获取选择文件夹
        if cur.text(1) == QtCore.QString(u"文件夹") or cur.text(0) == str(self.ftp.host):  # 选择的为文件夹或者根目录才能上传
            filepath = str(QtGui.QFileDialog.getOpenFileName(None, u"上传文件"))  # 获取上传文件路径
            t = filepath.split('/')  # 获取文件名
            filename = t[len(t) - 1]  # 文件名
            path = ''  # 上传路径
            times = 0
            while str(cur.text(0)) != self.ftp.host:    # 生成上传路径
                path = r'/' + str(cur.text(0)) + r'/' + path
                cur = cur.parent()
                times += 1
            print path
            self.ftp.cwd(path)  # 进入目录
            self.ftp.put_file(filepath, filename)    # 上传文件
            s = time.strftime(ISOTIMEFORMAT, time.localtime()) + u'\t\t上传%s成功' % (filename,)
            self.ui.plainTextEdit.appendPlainText(QtCore.QString(s))
            while times > 0:
                self.ftp.cwd('..')
                times -= 1
            self.refresh()
        else:
            QtGui.QMessageBox.information(self, u'错误', u'请选择一个文件夹！', QtGui.QMessageBox.Yes)

    def retr_button_action(self):
        filepath = QtGui.QFileDialog.getExistingDirectory(None, u"下载文件")
        for item in self.ui.treeWidget.findItems("", QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive):
            if item.checkState(0) == QtCore.Qt.Checked:
                if item.text(1) != QtCore.QString(u"文件夹"):
                    path = ''  # 路径
                    temp = item.parent()
                    while str(temp.text(0)) != self.ftp.host:  # 遍历路径
                        path = r'/' + str(temp.text(0)) + r'/' + path
                        temp = temp.parent()
                    t = QtCore.QString('D:/' + str(item.text(0)))  # 保存文件默认地址
                    self.ftp.get_file(path + str(item.text(0)), str(filepath))  # 获取文件
                    s = time.strftime(ISOTIMEFORMAT, time.localtime()) + u'\t\t下载%s成功' % (str(item.text(0)),)
                    self.ui.plainTextEdit.appendPlainText(QtCore.QString(s))

    def exit_menu(self):
        if self.ftp:
            self.ftp.quit()
            self.close()
