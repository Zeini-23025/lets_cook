"""Installed-app detection logic for Windows/Linux."""

import glob
import shutil
from pathlib import Path

from .constants import IS_WINDOWS, OS_KEY
from .ui import green, yellow

def _registry_has(name_pattern: str) -> bool:
    """Return True if a matching DisplayName is found in Windows Uninstall registry."""
    if not IS_WINDOWS:
        return False
    try:
        import winreg
    except ImportError:
        return False

    hives = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    pattern = name_pattern.lower()
    for hive, reg_path in hives:
        try:
            with winreg.OpenKey(hive, reg_path) as root:
                n_keys = winreg.QueryInfoKey(root)[0]
                for i in range(n_keys):
                    try:
                        sub_name = winreg.EnumKey(root, i)
                        with winreg.OpenKey(root, sub_name) as sub:
                            display = winreg.QueryValueEx(sub, "DisplayName")[0]
                            if pattern in display.lower():
                                return True
                    except (OSError, FileNotFoundError):
                        continue
        except (OSError, FileNotFoundError):
            continue
    return False


_install_cache: dict[str, bool] = {}


def check_installed(app: dict) -> bool:
    name = app["name"]
    if name in _install_cache:
        return _install_cache[name]

    details = app.get(OS_KEY)
    if not details:
        _install_cache[name] = False
        return False

    # 1. shutil.which() — fast PATH check
    check_bin = details.get("check")
    if check_bin and shutil.which(str(check_bin)) is not None:
        _install_cache[name] = True
        return True

    # 2. Explicit paths (supports glob patterns like C:/JetBrains/*/bin/idea64.exe)
    for raw_path in details.get("paths", []):
        matches = glob.glob(raw_path)
        if matches:
            _install_cache[name] = True
            return True

    # 3. Glob paths (separate list for apps with versioned directories)
    for raw_path in details.get("glob_paths", []):
        if glob.glob(raw_path):
            _install_cache[name] = True
            return True

    # 4. cmd path itself (if it looks like a file path)
    cmd = details.get("cmd", "")
    if cmd and ("/" in cmd or "\\" in cmd) and Path(cmd).exists():
        _install_cache[name] = True
        return True

    # 5. Windows registry lookup (catches apps that modify PATH after install)
    if IS_WINDOWS:
        reg_name = details.get("reg_name", "")
        if reg_name and _registry_has(reg_name):
            _install_cache[name] = True
            return True

    _install_cache[name] = False
    return False



def install_label(app: dict) -> str:
    if check_installed(app):
        return green("✓ installed")
    return yellow("✗ not found")


# ─── Config I/O ───────────────────────────────────────────────────────────────
