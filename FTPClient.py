# _*_coding:utf-8_*_ #
import os
import socket
import re
from PyQt4 import QtCore, QtGui

CRLF = '\r\n'   # 回车换行

# 异常处理
class Error(Exception):
    def __init__(self, resp):
        QWidget = None
        QtGui.QMessageBox.information(QWidget, u'FTP客户端', u'操作异常', QtGui.QMessageBox.Yes)


class FTP:
    host = ''   # 主机号
    port = 21     # 端口号，默认为21
    sock = None     # socket
    file = None     # 套接字相关联的文件
    af = socket.AF_INET
    socktype = socket.SOCK_STREAM
    live = False

    def __init__(self, host='', user='', password=''):
        if host:
            self.connect(host)
            if user:
                self.status = self.login(user, password)
                self.status = self.status[:3]
                self.live = True

    def connect(self, host=''):
        if host != '':      # 不是0.0.0.0
            self.host = host
        self.sock = socket.create_connection((self.host, self.port))      # 建立连接(控制端口默认21)
        self.file = self.sock.makefile('rb')    # 创建一个与该套接字相关连的文件
        return self.getresp()   # 从服务器获取响应

    # 从服务器信息
    def getmessage(self):
        line = self.file.readline()     # 读取一行
        if line[-2:] == CRLF:   # 去除回车换行
            line = line[:-2]
        return line


    def getresp(self):
        resp = self.getmessage()
        print repr(resp)
        c = resp[:1]
        if c in ('1', '2', '3'):    # 响应代码为1、2、3开头
            return resp
        raise Error, resp

    def voidresp(self):
        resp = self.getresp()
        if resp[:1] != '2':
            raise Error, resp
        return resp

    # 发送一条指令并返回响应
    def sendcmd(self, cmd):
        cmd += CRLF  # 加上回车换行
        self.sock.sendall(cmd)
        resp = self.getmessage()
        print repr(resp)
        c = resp[:1]  # 获取应答码第1位
        if c in ('1', '2', '3'):
            return resp
        raise Error, resp

    def voidcmd(self, cmd):
        cmd += CRLF  # 加上回车换行
        self.sock.sendall(cmd)
        resp = self.getresp()
        if resp[:1] != '2':
            raise Error, resp
        return resp

    # PORT指令
    def sendport(self, host, port):
        h = host.split('.')    # 用.分割地址
        p = [repr(port // 256), repr(port % 256)]      # 计算端口号
        args = h + p
        cmd = 'PORT ' + ','.join(args)     # 用,分割参数
        return self.voidcmd(cmd)

    # 被动模式
    def makepasv(self):
        resp = self.sendcmd('PASV')
        if resp[:3] != '227':
            raise Error, resp
        m = re.compile(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)').search(resp)     # 判断接收的参数格式
        if not m:
            raise Error, resp
        numbers = m.groups()
        host = '.'.join(numbers[:4])    # 生成主机号
        port = (int(numbers[4]) << 8) + int(numbers[5])     # 计算端口号
        return host, port

    def transfercmd(self, cmd, rest=None):
        host, port = self.makepasv()    # 被动模式
        conn = socket.create_connection((host, port))   # 建立数据连接
        try:
            if rest is not None:
                self.sendcmd("REST %s" % rest)  # 从该位置继续传送
            resp = self.sendcmd(cmd)
            if resp[0] == '2':  # 226 250
                resp = self.getresp()
            if resp[0] != '1':  # 110
                raise Error, resp
        except:
            conn.close()
            raise
        return conn

    # 登录
    def login(self, user='', password=''):
        resp = self.sendcmd('USER ' + user)
        if resp[:3] == '331':      # 收到331，用户名正常需要密码
            resp = self.sendcmd('PASS ' + password)
        if resp[0] != '2':      # 命令未实现
            raise Error, resp
        return resp

    # 二进制模式获取文件
    def retrbinary(self, cmd, callback, blocksize=8192, rest=None):
        self.voidcmd('TYPE I')
        conn = self.transfercmd(cmd, rest)
        while 1:
            data = conn.recv(blocksize)
            if not data:
                break
            callback(data)
        conn.close()
        return self.voidresp()

    #  文本模式获取文件
    def retrlines(self, cmd, callback=None):
        if callback is None:
            callback = print_line
        resp = self.sendcmd('TYPE A')   # 设置文本模式
        conn = self.transfercmd(cmd)    # 建立数据连接
        fp = conn.makefile('rb')    #
        while 1:
            line = fp.readline()
            if not line:    # 结束
                break
            if line[-2:] == CRLF:
                line = line[:-2]
            callback(line)
        fp.close()
        conn.close()
        return self.voidresp()

    # 二进制模式上传文件
    def storbinary(self, cmd, fp, blocksize=8192, callback=None, rest=None):
        self.voidcmd('TYPE I')
        conn = self.transfercmd(cmd, rest)
        while 1:
            buf = fp.read(blocksize)
            if not buf:
                break
            conn.sendall(buf)
            if callback:
                callback(buf)
        conn.close()
        return self.voidresp()

    # 当前目录下的文件和文件夹列表
    def nlst(self, *args):
        cmd = 'NLST'
        for arg in args:
            cmd += (' ' + arg)
        files = []
        self.retrlines(cmd, files.append)
        return files

    # 列出目录
    def dir(self, *args):
        cmd = 'LIST'
        func = None
        if args[-1:] and type(args[-1])!= type(''):
            args, func = args[:-1], args[-1]
        for arg in args:
            if arg:
                cmd += (' ' + arg)
        files = []
        self.retrlines(cmd, files.append)
        return files

    # 文件重命名
    def rename(self, old_name, new_name):
        resp = self.sendcmd('RNFR ' + old_name)
        if resp[0] != '3':
            raise Error, resp
        return self.voidcmd('RNTO ' + new_name)

    # 删除文件
    def delete(self, filename):
        resp = self.sendcmd('DELE ' + filename)
        if resp[:3] in ('250', '200'):
            return resp
        else:
            raise Error, resp

    # 改变目录
    def cwd(self, dirname):
        if dirname == '..':     # 返回上一层
            return self.voidcmd('CDUP')
        elif dirname == '':
            dirname = '.'
        cmd = 'CWD ' + dirname
        return self.voidcmd(cmd)

    # 创建文件夹
    def mkd(self, dirname):
        resp = self.sendcmd('MKD ' + dirname)
        if resp[:3] != '257':
            raise Error, resp
        if resp[3:5] != ' "':
            return ''
        dirname = ''
        i = 5
        n = len(resp)
        while i < n:
            c = resp[i]
            i += + 1
            if c == '"':
                if i >= n or resp[i] != '"':
                    break
                i = i + 1
            dirname = dirname + c
        return dirname

    # 删除文件夹
    def rmd(self, dirname):
        return self.voidcmd('RMD ' + dirname)

    # 退出
    def quit(self):
        resp = self.voidcmd('QUIT')
        self.close()
        return resp

    # 关闭连接
    def close(self):
        self.file.close()
        self.sock.close()

    def _is_ftp_file(self, ftp_path):
        # os.path.dirname 获取 ftp_path所在的目录
        # nlst 获取该目录下的文件
        # 判断ftp_path是否在该目录下
        if ftp_path in self.nlst(os.path.dirname(ftp_path)):
            return True
        else:
            return False

    def _ftp_list(self, line):
        list = line.split(' ')
        if self.ftp_dir_name == list[-1] and list[0].startswith('d'):
            self._is_dir = True

    def _is_ftp_dir(self, ftp_path):
        ftp_path = ftp_path.rstrip('/')
        ftp_parent_path = os.path.dirname(ftp_path)    # 获取文件夹名
        self.ftp_dir_name = os.path.basename(ftp_path)      # 获取文件名
        self._is_dir = False
        if ftp_path == '.' or ftp_path == './' or ftp_path == '':
            self._is_dir = True
        else:
            self.retrlines('LIST %s' % ftp_parent_path, self._ftp_list)
        return self._is_dir

    def get_file(self, ftp_path, local_path='.'):
        ftp_path = ftp_path.rstrip('/')     # 去除路径后面的/
        if self._is_ftp_file(ftp_path):     # 判断文件是否存在ftp目录下
            file_name = os.path.basename(ftp_path)  # 获取文件名
            # 本地路径是文件夹
            if os.path.isdir(local_path):
                file_handler = open(os.path.join(local_path, file_name), 'wb')     # join连接目录和文件名  设置为二进制写模式
                self.retrbinary("RETR %s" % (ftp_path,), file_handler.write)
                file_handler.close()
            # 本地路径不是文件夹，但是上一层目录是文件夹
            elif os.path.isdir(os.path.dirname(local_path)):
                file_handler = open(local_path, 'wb')
                self.retrbinary("RETR %s" % (ftp_path,), file_handler.write)
                file_handler.close()
            else:
                print '错误:文件夹:%s 不存在' % os.path.dirname(local_path)
        else:   # 文件不存在
            print '错误:文件:%s 不存在' % ftp_path

    def put_file(self, local_path, ftp_path='.'):
        ftp_path = ftp_path.rstrip('/')     # 删除结尾的/
        if os.path.isfile(local_path):
            file_handler = open(local_path, "rb")
            local_file_name = os.path.basename(local_path)
            # 目的路径是文件夹
            if self._is_ftp_dir(ftp_path):
                self.storbinary('STOR %s' % os.path.join(ftp_path, local_file_name), file_handler)
            # 目的路径上一层是文件夹
            elif self._is_ftp_dir(os.path.dirname(ftp_path)):
                self.storbinary('STOR %s' % ftp_path, file_handler)
            # 路径错误
            else:
                print '错误:路径:%s 错误' % ftp_path
            file_handler.close()
        else:
            print '错误:文件:%s 不存在' % local_path


def print_line(line):
    print line
