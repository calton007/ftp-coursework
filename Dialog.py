from __future__ import annotations

from PySide6 import QtWidgets


def ask_name(parent: QtWidgets.QWidget, title: str, label: str, default: str = "") -> str | None:
    value, ok = QtWidgets.QInputDialog.getText(parent, title, label, text=default)
    if ok and value:
        return value
    return None
