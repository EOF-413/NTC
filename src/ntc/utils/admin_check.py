# src/ntc/utils/admin_check.py
"""Проверка прав администратора/root."""
import os
import sys


def is_admin() -> bool:
    """True, если процесс запущен с административными правами."""
    if sys.platform == "win32":
        try:
            import ctypes

            return bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            return False
    try:
        return os.geteuid() == 0  # type: ignore[attr-defined]
    except AttributeError:
        return False
