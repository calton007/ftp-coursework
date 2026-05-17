from __future__ import annotations

import hashlib
import threading
from pathlib import Path

import pytest
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from FTPClient import FtpClient, FtpError, join_ftp_path


@pytest.fixture
def ftp_server(tmp_path: Path):
    root = tmp_path / "ftp-root"
    root.mkdir()
    (root / "read me.txt").write_text("hello ftp", encoding="utf-8")
    (root / "folder.with.dot").mkdir()
    (root / "folder.with.dot" / "nested.txt").write_text("nested", encoding="utf-8")

    authorizer = DummyAuthorizer()
    authorizer.add_user("user", "pass", str(root), perm="elradfmwMT")

    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer(("127.0.0.1", 0), handler)
    host, port = server.socket.getsockname()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield host, port, root
    finally:
        server.close_all()
        thread.join(timeout=2)


@pytest.fixture
def client(ftp_server):
    host, port, _root = ftp_server
    ftp = FtpClient()
    ftp.connect(host, port)
    ftp.login("user", "pass")
    try:
        yield ftp
    finally:
        ftp.close()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_login_failure_exposes_response(ftp_server):
    host, port, _root = ftp_server
    ftp = FtpClient()
    ftp.connect(host, port)
    with pytest.raises(FtpError) as error:
        ftp.login("user", "bad-password")
    assert "PASS" in str(error.value)
    assert "response=" in str(error.value)
    ftp.close()


def test_mlsd_returns_strict_file_and_dir_entries(client):
    entries = {entry.name: entry for entry in client.mlsd("/")}
    assert entries["read me.txt"].type == "file"
    assert entries["folder.with.dot"].type == "dir"
    assert entries["read me.txt"].path == "/read me.txt"
    assert entries["folder.with.dot"].path == "/folder.with.dot"


def test_upload_download_and_windows_path_normalization(client, tmp_path: Path):
    local_source = tmp_path / "local file.txt"
    local_source.write_text("payload", encoding="utf-8")
    client.upload_file(local_source, "\\uploaded file.txt")

    local_target = tmp_path / "downloaded.txt"
    client.download_file("/uploaded file.txt", local_target)

    assert sha256(local_source) == sha256(local_target)
    assert "\\" not in join_ftp_path("/", "uploaded file.txt")


def test_rename_and_make_dir(client):
    client.make_dir("/new dir")
    client.rename("/new dir", "/renamed dir")
    entries = {entry.name: entry for entry in client.mlsd("/")}
    assert "renamed dir" in entries
    assert entries["renamed dir"].type == "dir"


def test_delete_file(client):
    client.delete_file("/read me.txt")
    entries = {entry.name for entry in client.mlsd("/")}
    assert "read me.txt" not in entries


def test_recursive_delete_stops_on_tree_entries(client):
    count = client.delete_tree("/folder.with.dot")
    entries = {entry.name for entry in client.mlsd("/")}
    assert count == 2
    assert "folder.with.dot" not in entries
