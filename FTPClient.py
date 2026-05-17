from __future__ import annotations

import posixpath
import re
import socket
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Literal


CRLF = "\r\n"
ProgressCallback = Callable[[int, int | None, str], None]


class FtpError(Exception):
    def __init__(self, message: str, *, command: str | None = None, response: str | None = None, cwd: str | None = None):
        self.command = command
        self.response = response
        self.cwd = cwd
        details = [message]
        if command:
            details.append(f"command={command}")
        if cwd:
            details.append(f"cwd={cwd}")
        if response:
            details.append(f"response={response}")
        super().__init__("; ".join(details))


@dataclass(frozen=True)
class FtpEntry:
    name: str
    path: str
    type: Literal["file", "dir"]
    size: int | None
    modified: datetime | None


def join_ftp_path(parent: str, name: str) -> str:
    if not name or "/" in name:
        raise ValueError(f"invalid FTP path segment: {name!r}")
    if parent in ("", "/"):
        return f"/{name}"
    return f"{parent.rstrip('/')}/{name}"


class FtpClient:
    def __init__(self, timeout: float = 20.0, encoding: str = "utf-8"):
        self.timeout = timeout
        self.encoding = encoding
        self.host = ""
        self.port = 21
        self._sock: socket.socket | None = None
        self._file = None

    def connect(self, host: str, port: int = 21) -> str:
        self.host = host
        self.port = port
        self._sock = socket.create_connection((host, port), timeout=self.timeout)
        self._file = self._sock.makefile("r", encoding=self.encoding, newline=CRLF)
        return self._expect(None, {"2"})

    def login(self, user: str, password: str) -> str:
        resp = self._command(f"USER {user}", {"2", "3"})
        if resp.startswith("331"):
            self._send_line(f"PASS {password}")
            resp = self._expect("PASS <redacted>", {"2"})
        elif not resp.startswith("230"):
            raise FtpError("unexpected login response", command="USER", response=resp, cwd=self.safe_pwd())
        return resp

    def quit(self) -> None:
        if self._sock is None:
            return
        try:
            self._command("QUIT", {"2"})
        finally:
            self.close()

    def close(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    def pwd(self) -> str:
        resp = self._command("PWD", {"2"})
        match = re.search(r'"((?:[^"]|"")*)"', resp)
        if not match:
            raise FtpError("PWD response did not contain a quoted path", command="PWD", response=resp)
        return match.group(1).replace('""', '"')

    def safe_pwd(self) -> str | None:
        try:
            return self.pwd()
        except Exception:
            return None

    def cwd(self, path: str) -> None:
        self._command(f"CWD {self._normalize_remote_path(path)}", {"2"})

    def mlsd(self, path: str = "/") -> list[FtpEntry]:
        remote_path = self._normalize_remote_path(path)
        lines = self._retr_lines(f"MLSD {remote_path}")
        entries: list[FtpEntry] = []
        for line in lines:
            if not line:
                continue
            facts, sep, name = line.partition(" ")
            if sep != " " or not name:
                raise FtpError("invalid MLSD row", command=f"MLSD {remote_path}", response=line, cwd=self.safe_pwd())
            if name in (".", ".."):
                continue
            parsed_facts = self._parse_facts(facts)
            entry_type = parsed_facts.get("type")
            if entry_type not in {"file", "dir"}:
                raise FtpError("MLSD row has unsupported type", command=f"MLSD {remote_path}", response=line, cwd=self.safe_pwd())
            size = int(parsed_facts["size"]) if "size" in parsed_facts else None
            modified = self._parse_modified(parsed_facts.get("modify"))
            entries.append(FtpEntry(name=name, path=join_ftp_path(remote_path, name), type=entry_type, size=size, modified=modified))
        return entries

    def download_file(self, remote_path: str, local_path: Path, progress: ProgressCallback | None = None) -> None:
        remote_path = self._normalize_remote_path(remote_path)
        total = self._size_or_none(remote_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        transferred = 0
        with local_path.open("wb") as output:
            conn = self._transfer_command(f"RETR {remote_path}")
            try:
                while True:
                    block = conn.recv(1024 * 64)
                    if not block:
                        break
                    output.write(block)
                    transferred += len(block)
                    if progress:
                        progress(transferred, total, f"download {remote_path}")
            finally:
                conn.close()
        self._expect(f"RETR {remote_path}", {"2"})

    def upload_file(self, local_path: Path, remote_path: str, progress: ProgressCallback | None = None) -> None:
        if not local_path.is_file():
            raise FtpError(f"local file does not exist: {local_path}")
        remote_path = self._normalize_remote_path(remote_path)
        total = local_path.stat().st_size
        transferred = 0
        conn = self._transfer_command(f"STOR {remote_path}")
        try:
            with local_path.open("rb") as source:
                while True:
                    block = source.read(1024 * 64)
                    if not block:
                        break
                    conn.sendall(block)
                    transferred += len(block)
                    if progress:
                        progress(transferred, total, f"upload {remote_path}")
        finally:
            conn.close()
        self._expect(f"STOR {remote_path}", {"2"})

    def delete_file(self, remote_path: str) -> None:
        self._command(f"DELE {self._normalize_remote_path(remote_path)}", {"2"})

    def make_dir(self, remote_path: str) -> None:
        self._command(f"MKD {self._normalize_remote_path(remote_path)}", {"2"})

    def remove_dir(self, remote_path: str) -> None:
        self._command(f"RMD {self._normalize_remote_path(remote_path)}", {"2"})

    def rename(self, old_path: str, new_path: str) -> None:
        old_path = self._normalize_remote_path(old_path)
        new_path = self._normalize_remote_path(new_path)
        self._command(f"RNFR {old_path}", {"3"})
        self._command(f"RNTO {new_path}", {"2"})

    def plan_delete_tree(self, remote_path: str) -> list[FtpEntry]:
        root = self._normalize_remote_path(remote_path)
        entries: list[FtpEntry] = []
        self._collect_delete_entries(root, entries)
        return entries

    def delete_tree(self, remote_path: str, progress: ProgressCallback | None = None) -> int:
        root = self._normalize_remote_path(remote_path)
        entries = self.plan_delete_tree(root)
        total = len(entries)
        for index, entry in enumerate(entries, 1):
            if entry.type == "file":
                self.delete_file(entry.path)
            else:
                self.remove_dir(entry.path)
            if progress:
                progress(index, total, f"delete {entry.path}")
        return total

    def _collect_delete_entries(self, remote_path: str, entries: list[FtpEntry]) -> None:
        children = self.mlsd(remote_path)
        for child in children:
            if child.type == "dir":
                self._collect_delete_entries(child.path, entries)
            entries.append(child)
        entries.append(FtpEntry(name=posixpath.basename(remote_path.rstrip("/")), path=remote_path, type="dir", size=None, modified=None))

    def _retr_lines(self, command: str) -> list[str]:
        self._command("TYPE A", {"2"})
        conn = self._transfer_command(command)
        chunks: list[bytes] = []
        try:
            while True:
                block = conn.recv(1024 * 64)
                if not block:
                    break
                chunks.append(block)
        finally:
            conn.close()
        self._expect(command, {"2"})
        text = b"".join(chunks).decode(self.encoding)
        return [line.rstrip("\r\n") for line in text.splitlines()]

    def _transfer_command(self, command: str) -> socket.socket:
        host, port = self._pasv()
        conn = socket.create_connection((host, port), timeout=self.timeout)
        try:
            self._command(command, {"1"})
        except Exception:
            conn.close()
            raise
        return conn

    def _pasv(self) -> tuple[str, int]:
        resp = self._command("PASV", {"2"})
        match = re.search(r"\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)", resp)
        if not match:
            raise FtpError("invalid PASV response", command="PASV", response=resp, cwd=self.safe_pwd())
        parts = [int(value) for value in match.groups()]
        return ".".join(str(value) for value in parts[:4]), (parts[4] << 8) + parts[5]

    def _size_or_none(self, remote_path: str) -> int | None:
        resp = self._command(f"SIZE {remote_path}", {"2", "5"})
        if resp.startswith("5"):
            return None
        pieces = resp.split(maxsplit=1)
        if len(pieces) != 2 or not pieces[1].isdigit():
            raise FtpError("invalid SIZE response", command=f"SIZE {remote_path}", response=resp, cwd=self.safe_pwd())
        return int(pieces[1])

    def _command(self, command: str, expected_prefixes: set[str]) -> str:
        self._send_line(command)
        return self._expect(command, expected_prefixes)

    def _send_line(self, line: str) -> None:
        if self._sock is None:
            raise FtpError("FTP connection is not open")
        self._sock.sendall((line + CRLF).encode(self.encoding))

    def _expect(self, command: str | None, expected_prefixes: set[str]) -> str:
        response = self._read_response()
        if response[:1] not in expected_prefixes:
            raise FtpError("unexpected FTP response", command=command, response=response)
        return response

    def _read_response(self) -> str:
        if self._file is None:
            raise FtpError("FTP connection is not open")
        first = self._file.readline()
        if not first:
            raise FtpError("FTP server closed the control connection")
        first = first.rstrip("\r\n")
        if len(first) >= 4 and first[:3].isdigit() and first[3] == "-":
            code = first[:3]
            lines = [first]
            while True:
                line = self._file.readline()
                if not line:
                    raise FtpError("FTP server closed a multiline response early", response="\n".join(lines))
                line = line.rstrip("\r\n")
                lines.append(line)
                if line.startswith(code + " "):
                    return "\n".join(lines)
        return first

    @staticmethod
    def _parse_facts(facts: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for item in facts.rstrip(";").split(";"):
            if not item:
                continue
            key, sep, value = item.partition("=")
            if sep != "=":
                raise FtpError("invalid MLSD fact", response=facts)
            result[key.lower()] = value
        return result

    @staticmethod
    def _parse_modified(value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.strptime(value[:14], "%Y%m%d%H%M%S")

    @staticmethod
    def _normalize_remote_path(path: str) -> str:
        if not path:
            raise ValueError("remote path is empty")
        normalized = posixpath.normpath(path.replace("\\", "/"))
        if not normalized.startswith("/"):
            normalized = "/" + normalized
        return normalized
