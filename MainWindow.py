from __future__ import annotations

import posixpath
import queue
from dataclasses import asdict
from pathlib import Path

from PySide6 import QtCore, QtWidgets

from FTPClient import FtpClient, FtpError, join_ftp_path


ENTRY_ROLE = QtCore.Qt.UserRole + 1
LOADED_ROLE = QtCore.Qt.UserRole + 2


class FtpWorker(QtCore.QThread):
    started_task = QtCore.Signal(str)
    progress = QtCore.Signal(str, int, object, str)
    succeeded = QtCore.Signal(str, object)
    failed = QtCore.Signal(str, str)

    def __init__(self, parent: QtCore.QObject | None = None):
        super().__init__(parent)
        self._client: FtpClient | None = None
        self._tasks: queue.Queue[tuple[str, dict] | None] = queue.Queue()
        self._running = True

    def submit(self, task: str, **payload) -> None:
        self._tasks.put((task, payload))

    def stop(self) -> None:
        self._running = False
        self._tasks.put(None)

    def run(self) -> None:
        while self._running:
            item = self._tasks.get()
            if item is None:
                break
            task, payload = item
            self.started_task.emit(task)
            try:
                result = self._execute(task, payload)
                self.succeeded.emit(task, result)
            except Exception as exc:
                self.failed.emit(task, str(exc))

    def _execute(self, task: str, payload: dict):
        if task == "connect":
            client = FtpClient()
            client.connect(payload["host"], payload["port"])
            client.login(payload["user"], payload["password"])
            self._client = client
            return {"host": payload["host"], "root": client.pwd()}
        client = self._require_client()
        if task == "list_dir":
            return {"path": payload["path"], "entries": [asdict(entry) for entry in client.mlsd(payload["path"])]}
        if task == "download_file":
            remote_path = payload["remote_path"]
            local_path = Path(payload["local_dir"]) / posixpath.basename(remote_path)
            client.download_file(remote_path, local_path, self._progress(task))
            return {"remote_path": remote_path, "local_path": str(local_path)}
        if task == "upload_file":
            local_path = Path(payload["local_path"])
            remote_path = join_ftp_path(payload["remote_dir"], local_path.name)
            client.upload_file(local_path, remote_path, self._progress(task))
            return {"remote_path": remote_path}
        if task == "delete_file":
            client.delete_file(payload["path"])
            return {"path": payload["path"]}
        if task == "plan_delete_tree":
            entries = client.plan_delete_tree(payload["path"])
            return {"path": payload["path"], "name": posixpath.basename(payload["path"].rstrip("/")), "count": len(entries)}
        if task == "delete_tree":
            count = client.delete_tree(payload["path"], self._progress(task))
            return {"path": payload["path"], "count": count}
        if task == "rename":
            old_path = payload["path"]
            new_path = join_ftp_path(posixpath.dirname(old_path), payload["new_name"])
            client.rename(old_path, new_path)
            return {"old_path": old_path, "new_path": new_path}
        if task == "make_dir":
            new_path = join_ftp_path(payload["parent_path"], payload["name"])
            client.make_dir(new_path)
            return {"path": new_path}
        if task == "quit":
            client.quit()
            self._client = None
            return {}
        raise FtpError(f"unknown worker task: {task}")

    def _progress(self, task: str):
        def emit(done: int, total: int | None, message: str) -> None:
            self.progress.emit(task, done, total, message)

        return emit

    def _require_client(self) -> FtpClient:
        if self._client is None:
            raise FtpError("FTP connection is not open")
        return self._client


class LoginWindow(QtWidgets.QWidget):
    connected = QtCore.Signal(FtpWorker, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTP客户端")
        self.worker = FtpWorker(self)
        self.worker.succeeded.connect(self._task_succeeded)
        self.worker.failed.connect(self._task_failed)
        self.worker.start()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QFormLayout(self)
        self.host_edit = QtWidgets.QLineEdit()
        self.port_edit = QtWidgets.QSpinBox()
        self.port_edit.setRange(1, 65535)
        self.port_edit.setValue(21)
        self.user_edit = QtWidgets.QLineEdit()
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.anonymous_check = QtWidgets.QCheckBox("匿名")
        self.login_button = QtWidgets.QPushButton("连接")
        self.status_label = QtWidgets.QLabel("")

        layout.addRow("主机", self.host_edit)
        layout.addRow("端口", self.port_edit)
        layout.addRow("用户名", self.user_edit)
        layout.addRow("密码", self.password_edit)
        layout.addRow("", self.anonymous_check)
        layout.addRow("", self.login_button)
        layout.addRow("", self.status_label)

        self.anonymous_check.toggled.connect(self._anonymous_toggled)
        self.login_button.clicked.connect(self._connect_clicked)

    def _anonymous_toggled(self, checked: bool) -> None:
        self.user_edit.setEnabled(not checked)
        self.password_edit.setEnabled(not checked)
        if checked:
            self.user_edit.setText("anonymous")
            self.password_edit.setText("anonymous@")
        else:
            self.user_edit.clear()
            self.password_edit.clear()

    def _connect_clicked(self) -> None:
        self.login_button.setEnabled(False)
        self.status_label.setText("连接中...")
        self.worker.submit(
            "connect",
            host=self.host_edit.text().strip(),
            port=self.port_edit.value(),
            user=self.user_edit.text(),
            password=self.password_edit.text(),
        )

    def _task_succeeded(self, task: str, result: object) -> None:
        if task != "connect":
            return
        data = result if isinstance(result, dict) else {}
        self.connected.emit(self.worker, str(data["host"]))
        self.worker.setParent(None)
        self.close()

    def _task_failed(self, task: str, message: str) -> None:
        if task != "connect":
            return
        self.login_button.setEnabled(True)
        self.status_label.setText(message)

    def closeEvent(self, event) -> None:
        if self.worker.parent() is self:
            self.worker.stop()
            self.worker.wait(2000)
        super().closeEvent(event)


class FTPMainWindow(QtWidgets.QMainWindow):
    def __init__(self, worker: FtpWorker, host: str):
        super().__init__()
        self.worker = worker
        self.host = host
        self.pending_delete_tree: str | None = None
        self.setWindowTitle("FTP客户端")
        self._build_ui()
        self._connect_worker()
        self._set_busy(False)
        self._load_root()

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        toolbar = QtWidgets.QHBoxLayout()
        self.refresh_button = QtWidgets.QPushButton("刷新")
        self.download_button = QtWidgets.QPushButton("下载")
        self.upload_button = QtWidgets.QPushButton("上传")
        self.rename_button = QtWidgets.QPushButton("重命名")
        self.delete_button = QtWidgets.QPushButton("删除文件")
        self.make_dir_button = QtWidgets.QPushButton("新建文件夹")
        self.delete_dir_button = QtWidgets.QPushButton("删除文件夹")
        for button in (
            self.refresh_button,
            self.download_button,
            self.upload_button,
            self.rename_button,
            self.delete_button,
            self.make_dir_button,
            self.delete_dir_button,
        ):
            toolbar.addWidget(button)
        toolbar.addStretch()

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["名称", "类型", "大小"])
        self.tree.setColumnWidth(0, 280)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setVisible(False)
        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)

        layout.addLayout(toolbar)
        layout.addWidget(self.tree, 1)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log)
        self.setCentralWidget(central)

        self.refresh_button.clicked.connect(self._load_root)
        self.tree.itemExpanded.connect(self._item_expanded)
        self.download_button.clicked.connect(self._download_clicked)
        self.upload_button.clicked.connect(self._upload_clicked)
        self.rename_button.clicked.connect(self._rename_clicked)
        self.delete_button.clicked.connect(self._delete_file_clicked)
        self.make_dir_button.clicked.connect(self._make_dir_clicked)
        self.delete_dir_button.clicked.connect(self._plan_delete_tree_clicked)

    def _connect_worker(self) -> None:
        self.worker.started_task.connect(self._task_started)
        self.worker.progress.connect(self._task_progress)
        self.worker.succeeded.connect(self._task_succeeded)
        self.worker.failed.connect(self._task_failed)

    def _load_root(self) -> None:
        self.tree.clear()
        root = QtWidgets.QTreeWidgetItem(["/", "文件夹", ""])
        root.setData(0, ENTRY_ROLE, {"name": "/", "path": "/", "type": "dir", "size": None})
        root.setData(0, LOADED_ROLE, False)
        root.addChild(QtWidgets.QTreeWidgetItem(["加载中...", "", ""]))
        self.tree.addTopLevelItem(root)
        self.tree.expandItem(root)

    def _item_expanded(self, item: QtWidgets.QTreeWidgetItem) -> None:
        entry = self._entry(item)
        if not entry or entry["type"] != "dir" or item.data(0, LOADED_ROLE):
            return
        self.worker.submit("list_dir", path=entry["path"])
        item.setData(0, LOADED_ROLE, True)

    def _task_started(self, task: str) -> None:
        self._set_busy(True)
        self._append_log(f"开始: {task}")

    def _task_progress(self, task: str, done: int, total: object, message: str) -> None:
        self.progress_bar.setVisible(True)
        if isinstance(total, int) and total > 0:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(done)
        else:
            self.progress_bar.setRange(0, 0)
        self.progress_bar.setFormat(message)

    def _task_succeeded(self, task: str, result: object) -> None:
        self._set_busy(False)
        self.progress_bar.setVisible(False)
        if task == "list_dir":
            data = result if isinstance(result, dict) else {}
            item = self._find_item_by_path(str(data["path"]))
            if item is not None:
                self._fill_dir(item, data["entries"] if isinstance(data["entries"], list) else [])
        elif task == "plan_delete_tree":
            data = result if isinstance(result, dict) else {}
            self._confirm_delete_tree(str(data["path"]), str(data["name"]), int(data["count"]))
        else:
            self._append_log(f"完成: {task}")
            self._refresh_after_mutation(task, result)

    def _task_failed(self, task: str, message: str) -> None:
        self._set_busy(False)
        self.progress_bar.setVisible(False)
        self._append_log(f"失败: {task}: {message}")
        QtWidgets.QMessageBox.critical(self, "FTP错误", message)

    def _fill_dir(self, item: QtWidgets.QTreeWidgetItem, entries: list[dict]) -> None:
        item.takeChildren()
        for entry in sorted(entries, key=lambda value: (value["type"] != "dir", value["name"].lower())):
            size = "" if entry["size"] is None else str(entry["size"])
            child = QtWidgets.QTreeWidgetItem([entry["name"], "文件夹" if entry["type"] == "dir" else "文件", size])
            child.setData(0, ENTRY_ROLE, entry)
            child.setData(0, LOADED_ROLE, False)
            if entry["type"] == "dir":
                child.addChild(QtWidgets.QTreeWidgetItem(["加载中...", "", ""]))
            item.addChild(child)

    def _download_clicked(self) -> None:
        item = self.tree.currentItem()
        entry = self._entry(item)
        if not entry or entry["type"] != "file":
            QtWidgets.QMessageBox.information(self, "提示", "请选择一个文件")
            return
        local_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "下载到")
        if local_dir:
            self.worker.submit("download_file", remote_path=entry["path"], local_dir=local_dir)

    def _upload_clicked(self) -> None:
        target = self._selected_dir()
        if not target:
            QtWidgets.QMessageBox.information(self, "提示", "请选择一个文件夹")
            return
        local_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "上传文件")
        if local_path:
            self.worker.submit("upload_file", local_path=local_path, remote_dir=target["path"])

    def _rename_clicked(self) -> None:
        item = self.tree.currentItem()
        entry = self._entry(item)
        if not entry or entry["path"] == "/":
            QtWidgets.QMessageBox.information(self, "提示", "请选择要重命名的文件或文件夹")
            return
        new_name, ok = QtWidgets.QInputDialog.getText(self, "重命名", "新名称", text=entry["name"])
        if ok and new_name:
            self.worker.submit("rename", path=entry["path"], new_name=new_name)

    def _delete_file_clicked(self) -> None:
        entry = self._entry(self.tree.currentItem())
        if not entry or entry["type"] != "file":
            QtWidgets.QMessageBox.information(self, "提示", "请选择一个文件")
            return
        if QtWidgets.QMessageBox.question(self, "确认删除", f"删除文件 {entry['path']}？") == QtWidgets.QMessageBox.Yes:
            self.worker.submit("delete_file", path=entry["path"])

    def _make_dir_clicked(self) -> None:
        target = self._selected_dir()
        if not target:
            QtWidgets.QMessageBox.information(self, "提示", "请选择一个文件夹")
            return
        name, ok = QtWidgets.QInputDialog.getText(self, "新建文件夹", "文件夹名")
        if ok and name:
            self.worker.submit("make_dir", parent_path=target["path"], name=name)

    def _plan_delete_tree_clicked(self) -> None:
        entry = self._entry(self.tree.currentItem())
        if not entry or entry["type"] != "dir" or entry["path"] == "/":
            QtWidgets.QMessageBox.information(self, "提示", "请选择一个非根文件夹")
            return
        self.worker.submit("plan_delete_tree", path=entry["path"])

    def _confirm_delete_tree(self, path: str, name: str, count: int) -> None:
        typed, ok = QtWidgets.QInputDialog.getText(self, "确认递归删除", f"将删除 {count} 项：{path}\n请输入目录名确认")
        if ok and typed == name:
            self.worker.submit("delete_tree", path=path)
        elif ok:
            QtWidgets.QMessageBox.warning(self, "确认失败", "输入的目录名不匹配")

    def _selected_dir(self) -> dict | None:
        entry = self._entry(self.tree.currentItem())
        if entry and entry["type"] == "dir":
            return entry
        return None

    def _refresh_after_mutation(self, task: str, result: object) -> None:
        data = result if isinstance(result, dict) else {}
        refresh_path = "/"
        if task in {"upload_file", "make_dir"}:
            changed_path = str(data.get("remote_path") or data.get("path") or "/")
            refresh_path = posixpath.dirname(changed_path) or "/"
        elif task == "rename":
            refresh_path = posixpath.dirname(str(data.get("old_path") or "/")) or "/"
        elif task in {"delete_file", "delete_tree"}:
            refresh_path = posixpath.dirname(str(data.get("path") or "/")) or "/"
        item = self._find_item_by_path(refresh_path)
        if item is not None:
            item.setData(0, LOADED_ROLE, False)
            self._item_expanded(item)

    def _entry(self, item: QtWidgets.QTreeWidgetItem | None) -> dict | None:
        if item is None:
            return None
        value = item.data(0, ENTRY_ROLE)
        return value if isinstance(value, dict) else None

    def _find_item_by_path(self, path: str) -> QtWidgets.QTreeWidgetItem | None:
        matches = self.tree.findItems("", QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive)
        for item in [self.tree.topLevelItem(0), *matches]:
            entry = self._entry(item)
            if entry and entry["path"] == path:
                return item
        return None

    def _set_busy(self, busy: bool) -> None:
        for button in (
            self.refresh_button,
            self.download_button,
            self.upload_button,
            self.rename_button,
            self.delete_button,
            self.make_dir_button,
            self.delete_dir_button,
        ):
            button.setEnabled(not busy)

    def _append_log(self, message: str) -> None:
        self.log.appendPlainText(message)

    def closeEvent(self, event) -> None:
        self.worker.submit("quit")
        self.worker.stop()
        self.worker.wait(3000)
        super().closeEvent(event)
