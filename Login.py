from __future__ import annotations

import sys

from PySide6 import QtGui, QtWidgets

from MainWindow import FTPMainWindow, LoginWindow


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("FTP客户端")
    app.setWindowIcon(QtGui.QIcon("4.ico"))

    windows: list[QtWidgets.QWidget] = []
    login = LoginWindow()
    windows.append(login)

    def open_main(worker, host: str) -> None:
        main_window = FTPMainWindow(worker, host)
        windows.append(main_window)
        main_window.resize(900, 650)
        main_window.show()

    login.connected.connect(open_main)
    login.resize(360, 220)
    login.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
