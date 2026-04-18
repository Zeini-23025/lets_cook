#!/usr/bin/env python3
"""Let's Cook v2.1 - Workspace launcher for Windows & Linux."""

import glob
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

# ─── Constants ────────────────────────────────────────────────────────────────

VERSION     = "2.1"
CONFIG_DIR  = Path.home() / ".letscook"
CONFIG_FILE = CONFIG_DIR / "config.json"
IS_WINDOWS  = platform.system() == "Windows"
OS_KEY      = "windows" if IS_WINDOWS else "linux"
OS_LABEL    = "Windows" if IS_WINDOWS else "Linux"

# Windows environment path shortcuts
_AP   = os.environ.get("APPDATA",      "")   # %APPDATA%     Roaming
_LA   = os.environ.get("LOCALAPPDATA", "")   # %LOCALAPPDATA%
_PF   = "C:/Program Files"
_PF86 = "C:/Program Files (x86)"
_H    = str(Path.home())

BANNER = f"""
╔═══════════════════════════════════════════════╗
║        LET'S COOK  v{VERSION}  -  Workspace        ║
║      Fire up your entire stack at once        ║
╚═══════════════════════════════════════════════╝"""

HELP_TEXT = """
  Usage:
    lets_cook            — launch your configured workspace
    lets_cook --setup    — full setup wizard (reconfigure everything)
    lets_cook --add      — add new apps or URLs
    lets_cook --edit     — toggle apps on/off or edit commands
    lets_cook --remove   — remove apps or URLs
    lets_cook --list     — show current configuration
    lets_cook --help     — show this help
"""

# ─── App Library ──────────────────────────────────────────────────────────────
# windows/linux keys:
#   cmd      : command or full path used to LAUNCH the app
#   check    : short binary name for shutil.which() (None = skip which())
#   paths    : explicit filesystem paths to probe for existence (Windows)
#   reg_name : substring to look for in the Windows registry DisplayName
#   args     : default launch arguments

APP_LIBRARY = [
    # ── Editors & IDEs ────────────────────────────────────────────────────────
    {"cat": "Editors & IDEs", "name": "VS Code", "platform": "both",
     "windows": {"cmd": "code", "check": "code", "args": [],
                 "paths": [f"{_PF}/Microsoft VS Code/Code.exe",
                            f"{_LA}/Programs/Microsoft VS Code/Code.exe"],
                 "reg_name": "Microsoft Visual Studio Code"},
     "linux":   {"cmd": "code", "check": "code", "args": []}},

    {"cat": "Editors & IDEs", "name": "Cursor", "platform": "both",
     "windows": {"cmd": f"{_LA}/Programs/cursor/Cursor.exe", "check": "cursor", "args": [],
                 "paths": [f"{_LA}/Programs/cursor/Cursor.exe",
                            f"{_PF}/Cursor/Cursor.exe"],
                 "reg_name": "Cursor"},
     "linux":   {"cmd": "cursor", "check": "cursor", "args": []}},

    {"cat": "Editors & IDEs", "name": "Neovim", "platform": "both",
     "windows": {"cmd": "nvim", "check": "nvim", "args": [],
                 "paths": [f"{_PF}/Neovim/bin/nvim.exe"],
                 "reg_name": "Neovim"},
     "linux":   {"cmd": "nvim", "check": "nvim", "args": []}},

    {"cat": "Editors & IDEs", "name": "Vim", "platform": "both",
     "windows": {"cmd": "vim", "check": "vim", "args": [],
                 "paths": [f"{_PF}/Vim/vim*/vim.exe",
                            f"{_PF86}/Vim/vim*/vim.exe"]},
     "linux":   {"cmd": "vim", "check": "vim", "args": []}},

    {"cat": "Editors & IDEs", "name": "Emacs", "platform": "both",
     "windows": {"cmd": "emacs", "check": "emacs", "args": [],
                 "paths": [f"{_PF}/GNU Emacs*/bin/emacs.exe",
                            f"{_PF86}/GNU Emacs*/bin/emacs.exe"]},
     "linux":   {"cmd": "emacs", "check": "emacs", "args": []}},

    {"cat": "Editors & IDEs", "name": "Sublime Text", "platform": "both",
     "windows": {"cmd": "subl", "check": "subl", "args": [],
                 "paths": [f"{_PF}/Sublime Text/subl.exe",
                            f"{_PF}/Sublime Text 3/subl.exe",
                            f"{_AP}/Sublime Text/subl.exe"],
                 "reg_name": "Sublime Text"},
     "linux":   {"cmd": "subl", "check": "subl", "args": []}},

    {"cat": "Editors & IDEs", "name": "Notepad++", "platform": "windows",
     "windows": {"cmd": f"{_PF}/Notepad++/notepad++.exe", "check": "notepad++", "args": [],
                 "paths": [f"{_PF}/Notepad++/notepad++.exe",
                            f"{_PF86}/Notepad++/notepad++.exe"],
                 "reg_name": "Notepad++"},
     "linux":   None},

    {"cat": "Editors & IDEs", "name": "IntelliJ IDEA", "platform": "both",
     "windows": {"cmd": "idea64", "check": "idea64", "args": [],
                 "paths": [f"{_PF}/JetBrains/IntelliJ IDEA*/bin/idea64.exe"],
                 "reg_name": "IntelliJ IDEA"},
     "linux":   {"cmd": "idea", "check": "idea", "args": []}},

    {"cat": "Editors & IDEs", "name": "PyCharm", "platform": "both",
     "windows": {"cmd": "pycharm64", "check": "pycharm64", "args": [],
                 "paths": [f"{_PF}/JetBrains/PyCharm*/bin/pycharm64.exe"],
                 "reg_name": "PyCharm"},
     "linux":   {"cmd": "pycharm", "check": "pycharm", "args": []}},

    {"cat": "Editors & IDEs", "name": "WebStorm", "platform": "both",
     "windows": {"cmd": "webstorm64", "check": "webstorm64", "args": [],
                 "paths": [f"{_PF}/JetBrains/WebStorm*/bin/webstorm64.exe"],
                 "reg_name": "WebStorm"},
     "linux":   {"cmd": "webstorm", "check": "webstorm", "args": []}},

    {"cat": "Editors & IDEs", "name": "Android Studio", "platform": "both",
     "windows": {"cmd": "studio64", "check": "studio64", "args": [],
                 "paths": [f"{_PF}/Android/Android Studio/bin/studio64.exe"],
                 "reg_name": "Android Studio"},
     "linux":   {"cmd": "studio.sh", "check": "studio.sh", "args": []}},

    {"cat": "Editors & IDEs", "name": "Eclipse", "platform": "both",
     "windows": {"cmd": "eclipse", "check": "eclipse", "args": [],
                 "paths": [f"{_PF}/Eclipse/eclipse.exe",
                            f"{_H}/eclipse/eclipse.exe"]},
     "linux":   {"cmd": "eclipse", "check": "eclipse", "args": []}},

    # ── Terminals ─────────────────────────────────────────────────────────────
    {"cat": "Terminals", "name": "Windows Terminal", "platform": "windows",
     "windows": {"cmd": "wt", "check": "wt", "args": [],
                 "reg_name": "Windows Terminal"},
     "linux":   None},

    {"cat": "Terminals", "name": "Alacritty", "platform": "both",
     "windows": {"cmd": "alacritty", "check": "alacritty", "args": [],
                 "paths": [f"{_LA}/Programs/Alacritty/alacritty.exe",
                            f"{_PF}/Alacritty/alacritty.exe"],
                 "reg_name": "Alacritty"},
     "linux":   {"cmd": "alacritty", "check": "alacritty", "args": []}},

    {"cat": "Terminals", "name": "Hyper", "platform": "both",
     "windows": {"cmd": "hyper", "check": "hyper", "args": [],
                 "paths": [f"{_LA}/Programs/hyper/Hyper.exe"],
                 "reg_name": "Hyper"},
     "linux":   {"cmd": "hyper", "check": "hyper", "args": []}},

    {"cat": "Terminals", "name": "Kitty", "platform": "both",
     "windows": {"cmd": "kitty", "check": "kitty", "args": [],
                 "paths": [f"{_LA}/Programs/kitty/kitty.exe",
                            f"{_PF}/kitty/bin/kitty.exe",
                            f"{_PF86}/kitty/bin/kitty.exe"],
                 "reg_name": "kitty"},
     "linux":   {"cmd": "kitty", "check": "kitty", "args": []}},

    {"cat": "Terminals", "name": "Tilix", "platform": "linux",
     "windows": None,
     "linux":   {"cmd": "tilix", "check": "tilix", "args": []}},

    # ── Browsers ──────────────────────────────────────────────────────────────
    {"cat": "Browsers", "name": "Chrome", "platform": "both",
     "windows": {"cmd": f"{_PF}/Google/Chrome/Application/chrome.exe",
                 "check": "chrome", "args": [],
                 "paths": [f"{_PF}/Google/Chrome/Application/chrome.exe",
                            f"{_PF86}/Google/Chrome/Application/chrome.exe",
                            f"{_LA}/Google/Chrome/Application/chrome.exe"],
                 "reg_name": "Google Chrome"},
     "linux":   {"cmd": "google-chrome", "check": "google-chrome", "args": []}},

    {"cat": "Browsers", "name": "Firefox", "platform": "both",
     "windows": {"cmd": f"{_PF}/Mozilla Firefox/firefox.exe",
                 "check": "firefox", "args": [],
                 "paths": [f"{_PF}/Mozilla Firefox/firefox.exe",
                            f"{_PF86}/Mozilla Firefox/firefox.exe"],
                 "reg_name": "Mozilla Firefox"},
     "linux":   {"cmd": "firefox", "check": "firefox", "args": []}},

    {"cat": "Browsers", "name": "Brave", "platform": "both",
     "windows": {"cmd": f"{_PF}/BraveSoftware/Brave-Browser/Application/brave.exe",
                 "check": "brave", "args": [],
                 "paths": [f"{_PF}/BraveSoftware/Brave-Browser/Application/brave.exe",
                            f"{_LA}/BraveSoftware/Brave-Browser/Application/brave.exe"],
                 "reg_name": "Brave"},
     "linux":   {"cmd": "brave-browser", "check": "brave-browser", "args": []}},

    {"cat": "Browsers", "name": "Opera", "platform": "both",
     "windows": {"cmd": "opera", "check": "opera", "args": [],
                 "paths": [f"{_LA}/Programs/Opera/opera.exe",
                            f"{_AP}/Opera Software/Opera Stable/opera.exe"],
                 "reg_name": "Opera"},
     "linux":   {"cmd": "opera", "check": "opera", "args": []}},

    # ── Dev Tools ─────────────────────────────────────────────────────────────
    {"cat": "Dev Tools", "name": "Docker Desktop", "platform": "both",
     "windows": {"cmd": f"{_PF}/Docker/Docker/Docker Desktop.exe",
                 "check": "docker", "args": [],
                 "paths": [f"{_PF}/Docker/Docker/Docker Desktop.exe"],
                 "reg_name": "Docker Desktop"},
     "linux":   {"cmd": "docker", "check": "docker", "args": []}},

    {"cat": "Dev Tools", "name": "Postman", "platform": "both",
     "windows": {"cmd": f"{_LA}/Postman/Postman.exe",
                 "check": None, "args": [],
                 "paths": [f"{_LA}/Postman/Postman.exe",
                            f"{_LA}/Programs/Postman/Postman.exe"],
                 "reg_name": "Postman"},
     "linux":   {"cmd": "postman", "check": "postman", "args": []}},

    {"cat": "Dev Tools", "name": "Insomnia", "platform": "both",
     "windows": {"cmd": f"{_LA}/insomnia/Insomnia.exe",
                 "check": None, "args": [],
                 "paths": [f"{_LA}/insomnia/Insomnia.exe"],
                 "reg_name": "Insomnia"},
     "linux":   {"cmd": "insomnia", "check": "insomnia", "args": []}},

    {"cat": "Dev Tools", "name": "DBeaver", "platform": "both",
     "windows": {"cmd": "dbeaver", "check": "dbeaver", "args": [],
                 "paths": [f"{_PF}/DBeaver/dbeaver.exe",
                            f"{_LA}/Programs/DBeaverCommunity/dbeaver.exe"],
                 "reg_name": "DBeaver"},
     "linux":   {"cmd": "dbeaver", "check": "dbeaver", "args": []}},

    {"cat": "Dev Tools", "name": "TablePlus", "platform": "windows",
     "windows": {"cmd": "TablePlus", "check": "TablePlus", "args": [],
                 "paths": [f"{_LA}/Programs/TablePlus/TablePlus.exe"],
                 "reg_name": "TablePlus"},
     "linux":   None},

    {"cat": "Dev Tools", "name": "HeidiSQL", "platform": "windows",
     "windows": {"cmd": "heidisql", "check": "heidisql", "args": [],
                 "paths": [f"{_PF}/HeidiSQL/heidisql.exe",
                            f"{_PF86}/HeidiSQL/heidisql.exe"],
                 "reg_name": "HeidiSQL"},
     "linux":   None},

    {"cat": "Dev Tools", "name": "MySQL Workbench", "platform": "both",
     "windows": {"cmd": "MySQLWorkbench", "check": "MySQLWorkbench", "args": [],
                 "paths": [f"{_PF}/MySQL/MySQL Workbench*/MySQLWorkbench.exe"],
                 "reg_name": "MySQL Workbench"},
     "linux":   {"cmd": "mysql-workbench", "check": "mysql-workbench", "args": []}},

    {"cat": "Dev Tools", "name": "pgAdmin 4", "platform": "both",
     "windows": {"cmd": "pgAdmin4", "check": "pgAdmin4", "args": [],
                 "paths": [f"{_PF}/pgAdmin 4/*/pgAdmin4.exe",
                            f"{_LA}/Programs/pgAdmin 4/*/pgAdmin4.exe"],
                 "reg_name": "pgAdmin 4"},
     "linux":   {"cmd": "pgadmin4", "check": "pgadmin4", "args": []}},

    {"cat": "Dev Tools", "name": "GitHub Desktop", "platform": "both",
     "windows": {"cmd": f"{_LA}/GitHubDesktop/GitHubDesktop.exe",
                 "check": None, "args": [],
                 "paths": [f"{_LA}/GitHubDesktop/GitHubDesktop.exe"],
                 "reg_name": "GitHub Desktop"},
     "linux":   {"cmd": "github-desktop", "check": "github-desktop", "args": []}},

    {"cat": "Dev Tools", "name": "GitKraken", "platform": "both",
     "windows": {"cmd": "gitkraken", "check": "gitkraken", "args": [],
                 "paths": [f"{_LA}/gitkraken/gitkraken.exe",
                            f"{_LA}/Programs/gitkraken/gitkraken.exe"],
                 "reg_name": "GitKraken"},
     "linux":   {"cmd": "gitkraken", "check": "gitkraken", "args": []}},

    {"cat": "Dev Tools", "name": "Lens (Kubernetes)", "platform": "both",
     "windows": {"cmd": "lens-desktop", "check": "lens-desktop", "args": [],
                 "paths": [f"{_LA}/Programs/Lens/Lens.exe"]},
     "linux":   {"cmd": "lens-desktop", "check": "lens-desktop", "args": []}},

    # ── Local Servers ─────────────────────────────────────────────────────────
    {"cat": "Local Servers", "name": "Laragon", "platform": "windows",
     "windows": {"cmd": "C:/laragon/laragon.exe", "check": None, "args": [],
                 "paths": ["C:/laragon/laragon.exe",
                            "C:/tools/laragon/laragon.exe",
                            f"{_PF}/Laragon/laragon.exe"]},
     "linux":   None},

    {"cat": "Local Servers", "name": "XAMPP", "platform": "windows",
     "windows": {"cmd": "C:/xampp/xampp-control.exe", "check": None, "args": [],
                 "paths": ["C:/xampp/xampp-control.exe",
                            f"{_PF}/XAMPP/xampp-control.exe"]},
     "linux":   None},

    # ── Communication ─────────────────────────────────────────────────────────
    {"cat": "Communication", "name": "Slack", "platform": "both",
     "windows": {"cmd": f"{_LA}/slack/slack.exe", "check": None, "args": [],
                 "paths": [f"{_LA}/slack/slack.exe"],
                 "reg_name": "Slack"},
     "linux":   {"cmd": "slack", "check": "slack", "args": []}},

    {"cat": "Communication", "name": "Discord", "platform": "both",
     "windows": {"cmd": f"{_LA}/Discord/Update.exe",
                 "check": None, "args": ["--processStart", "Discord.exe"],
                 "paths": [f"{_LA}/Discord/Update.exe"],
                 "glob_paths": [f"{_LA}/Discord/app-*/Discord.exe"],
                 "reg_name": "Discord"},
     "linux":   {"cmd": "discord", "check": "discord", "args": []}},

    {"cat": "Communication", "name": "Zoom", "platform": "both",
     "windows": {"cmd": "zoom", "check": "zoom", "args": [],
                 "paths": [f"{_AP}/Zoom/bin/Zoom.exe",
                            f"{_LA}/Zoom/bin/Zoom.exe"],
                 "reg_name": "Zoom"},
     "linux":   {"cmd": "zoom", "check": "zoom", "args": []}},

    {"cat": "Communication", "name": "Telegram", "platform": "both",
     "windows": {"cmd": "telegram", "check": "telegram", "args": [],
                 "paths": [f"{_AP}/Telegram Desktop/Telegram.exe",
                            f"{_LA}/Programs/Telegram Desktop/Telegram.exe"],
                 "reg_name": "Telegram"},
     "linux":   {"cmd": "telegram-desktop", "check": "telegram-desktop", "args": []}},

    # ── Notes & Productivity ──────────────────────────────────────────────────
    {"cat": "Notes & Productivity", "name": "Obsidian", "platform": "both",
     "windows": {"cmd": f"{_LA}/Obsidian/Obsidian.exe", "check": None, "args": [],
                 "paths": [f"{_LA}/Obsidian/Obsidian.exe",
                            f"{_LA}/Programs/obsidian/Obsidian.exe"],
                 "reg_name": "Obsidian"},
     "linux":   {"cmd": "obsidian", "check": "obsidian", "args": []}},

    {"cat": "Notes & Productivity", "name": "Notion", "platform": "both",
     "windows": {"cmd": "notion", "check": "notion", "args": [],
                 "paths": [f"{_LA}/Programs/Notion/Notion.exe"],
                 "reg_name": "Notion"},
     "linux":   {"cmd": "notion", "check": "notion", "args": []}},

    {"cat": "Notes & Productivity", "name": "Figma", "platform": "both",
     "windows": {"cmd": f"{_LA}/Figma/Figma.exe", "check": None, "args": [],
                 "paths": [f"{_LA}/Figma/Figma.exe"],
                 "reg_name": "Figma"},
     "linux":   {"cmd": "figma", "check": "figma", "args": []}},

    # ── Music & Media ─────────────────────────────────────────────────────────
    {"cat": "Music & Media", "name": "Spotify", "platform": "both",
     "windows": {"cmd": f"{_AP}/Spotify/Spotify.exe", "check": None, "args": [],
                 "paths": [f"{_AP}/Spotify/Spotify.exe",
                            f"{_LA}/Microsoft/WindowsApps/Spotify.exe"],
                 "reg_name": "Spotify"},
     "linux":   {"cmd": "spotify", "check": "spotify", "args": []}},

    {"cat": "Music & Media", "name": "VLC", "platform": "both",
     "windows": {"cmd": "vlc", "check": "vlc", "args": [],
                 "paths": [f"{_PF}/VideoLAN/VLC/vlc.exe",
                            f"{_PF86}/VideoLAN/VLC/vlc.exe"],
                 "reg_name": "VLC media player"},
     "linux":   {"cmd": "vlc", "check": "vlc", "args": []}},
]


# ─── UI Helpers ───────────────────────────────────────────────────────────────

def _enable_ansi():
    if IS_WINDOWS:
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_uint()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                # Preserve existing console flags; only add virtual terminal processing.
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass

_enable_ansi()

def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"

def green(t):  return _c(str(t), "32")
def yellow(t): return _c(str(t), "33")
def cyan(t):   return _c(str(t), "36")
def red(t):    return _c(str(t), "31")
def bold(t):   return _c(str(t), "1")
def dim(t):    return _c(str(t), "2")

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")

def _render_rows(lines: list[str], cols: int) -> int:
    """Count terminal rows occupied by rendered lines (accounting for wraps)."""
    cols = max(cols, 1)
    rows = 0
    for line in lines:
        plain = _ANSI_RE.sub("", line)
        rows += max(1, (len(plain) + cols - 1) // cols)
    return rows

def section(title: str):
    print(f"\n{bold('─' * 50)}")
    print(f"  {bold(title)}")
    print(bold("─" * 50))

def ask(prompt: str, default: str = "") -> str:
    hint = f" {dim('[' + default + ']')}" if default else ""
    try:
        val = input(f"  {cyan('>')} {prompt}{hint}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{yellow('  Aborted.')}")
        sys.exit(0)
    return val if val else default

def ask_yn(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    raw = ask(f"{prompt} ({hint})", "").lower()
    if not raw:
        return default
    return raw in ("y", "yes")


# ─── Installation Detection ───────────────────────────────────────────────────

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

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            print(red("  Warning: config file is corrupted. Starting fresh."))
    return {}

def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(green(f"\n  Config saved -> {CONFIG_FILE}"))


# ─── Filtered Library ─────────────────────────────────────────────────────────

def os_apps() -> list:
    return [a for a in APP_LIBRARY
            if a["platform"] in ("both", OS_KEY) and a.get(OS_KEY)]


# ─── Raw key reader (no external deps) ───────────────────────────────────────

def _read_key() -> str | None:
    """Return a key name: 'up','down','space','enter','backspace', or a character."""
    if IS_WINDOWS:
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):          # special key prefix
            ch2 = msvcrt.getwch()
            return {'H': 'up', 'P': 'down'}.get(ch2)
        if ch == '\r':   return 'enter'
        if ch == ' ':    return 'space'
        if ch == '\x08': return 'backspace'
        if ch == '\x03': raise KeyboardInterrupt
        return ch if ch.isprintable() else None
    else:
        import tty, termios
        fd  = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                nxt = sys.stdin.read(2)
                return {'[A': 'up', '[B': 'down'}.get(nxt)
            if ch in ('\r', '\n'): return 'enter'
            if ch == ' ':          return 'space'
            if ch in ('\x7f', '\x08'): return 'backspace'
            if ch == '\x03': raise KeyboardInterrupt
            return ch if ch.isprintable() else None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ─── TUI App Picker ───────────────────────────────────────────────────────────

MAX_VISIBLE = 16   # max rows shown at once

def pick_apps(available: list, pre_selected: set = None) -> list:
    """
    Arrow keys navigate, Space toggles, type to filter, Enter confirms.
    No external libraries — pure stdlib raw terminal input.
    """
    selected = set(pre_selected or set())
    cursor   = 0
    search   = ""
    offset   = 0    # first visible index into filtered list
    prev_rows = 0   # rendered terminal rows in last frame (includes wrapped lines)

    # Pre-warm install cache before entering raw mode
    sys.stdout.write(f"\n  {bold('Checking installation status...')} ")
    sys.stdout.flush()
    for app in available:
        check_installed(app)
    sys.stdout.write(green("done\n\n"))
    sys.stdout.flush()

    while True:
        # ── Filter list ──
        q        = search.lower()
        filtered = [a for a in available
                    if q in a["name"].lower() or q in a["cat"].lower()] if q else list(available)
        total_f  = len(filtered)

        # ── Clamp cursor + adjust scroll window ──
        cursor = max(0, min(cursor, total_f - 1)) if total_f else 0
        if cursor < offset:
            offset = cursor
        elif cursor >= offset + MAX_VISIBLE:
            offset = cursor - MAX_VISIBLE + 1

        # ── Build frame ──
        SEP = "─" * 54
        term_cols = shutil.get_terminal_size((80, 24)).columns
        # Keep row width inside terminal to prevent wrapping, which can desync redraw on Windows.
        name_w = 22
        cat_w = 20
        if term_cols < 72:
            shrink = 72 - term_cols
            cat_cut = min(shrink, cat_w - 8)
            cat_w -= cat_cut
            shrink -= cat_cut
            if shrink > 0:
                name_cut = min(shrink, name_w - 8)
                name_w -= name_cut

        frame = []
        frame.append(f"  {bold(SEP)}")
        search_display = cyan(search) if search else dim("type to filter…")
        frame.append(f"  Search : {search_display}   {dim('|')}   "
                     f"{cyan(str(len(selected)))} selected / {total_f} shown")
        frame.append(f"  {dim('↑↓ navigate   Space select   Enter confirm   Bksp erase')}")
        frame.append(f"  {bold(SEP)}")

        if not filtered:
            frame.append(yellow("  No apps match."))
        else:
            vis_end = min(offset + MAX_VISIBLE, total_f)
            if offset > 0:
                frame.append(dim(f"  ↑  {offset} more above"))

            for i in range(offset, vis_end):
                app    = filtered[i]
                ticked = app["name"] in selected
                inst   = check_installed(app)

                # Build plain strings first (no ANSI) for correct width calculation
                tick  = "[x]" if ticked else "[ ]"
                name  = app["name"][:name_w].ljust(name_w)
                badge = "installed" if inst else "not found"
                cat   = app["cat"][:cat_w]
                arrow = "> " if i == cursor else "  "

                if i == cursor:
                    # Reverse-video highlight — keep the whole row plain text
                    row = f"\033[7m  {arrow}{tick}  {name}  {badge:<10}  {cat}\033[0m"
                else:
                    # Colour only individual tokens (no ljust on ANSI strings)
                    tick_c  = f"\033[36m{tick}\033[0m" if ticked else tick
                    badge_c = f"\033[32m{badge}\033[0m" if inst else f"\033[33m{badge}\033[0m"
                    cat_c   = f"\033[2m{cat}\033[0m"
                    row = f"    {tick_c}  {name}  {badge_c:<10}  {cat_c}"

                frame.append(row)

            if vis_end < total_f:
                frame.append(dim(f"  ↓  {total_f - vis_end} more below"))

        frame.append(f"  {bold(SEP)}")

        # ── Erase last frame, draw new one ──
        if prev_rows:
            # Move to previous frame start and clear downward.
            sys.stdout.write(f"\033[{prev_rows}F\033[J")
        sys.stdout.write("\n".join(frame) + "\n")
        sys.stdout.flush()
        prev_rows = _render_rows(frame, term_cols)

        # ── Handle keypress ──
        try:
            key = _read_key()
        except KeyboardInterrupt:
            sys.stdout.write("\n")
            print(yellow("\n  Cancelled."))
            sys.exit(0)

        if key == 'up':
            cursor = max(0, cursor - 1)
        elif key == 'down':
            cursor = min(total_f - 1, cursor + 1) if total_f else 0
        elif key == 'space':
            if filtered:
                name = filtered[cursor]["name"]
                if name in selected:
                    selected.discard(name)
                else:
                    selected.add(name)
                    if not check_installed(filtered[cursor]):
                        # Shown in badge column — no extra print needed
                        pass
        elif key == 'enter':
            sys.stdout.write("\n")
            for nm in list(selected):
                app = next((a for a in available if a["name"] == nm), None)
                if app and not check_installed(app):
                    print(yellow(f"  Warning: {nm} not detected — verify its command after setup."))
            break
        elif key == 'backspace':
            search = search[:-1]
            cursor = 0
            offset = 0
        elif key and len(key) == 1:
            search += key
            cursor = 0
            offset = 0

    return [a for a in available if a["name"] in selected]


def toggle_apps(apps: list, pre_enabled: set = None) -> set:
    """Same TUI for toggling already-configured apps ON/OFF."""
    pseudo = [
        {"name": a["name"], "cat": a.get("cat", "Custom"),
         "platform": "both",
         OS_KEY: {"cmd": a.get("command", ""), "check": None, "args": []}}
        for a in apps
    ]
    chosen = pick_apps(pseudo, pre_enabled)
    return {a["name"] for a in chosen}


# ─── URL Editor ───────────────────────────────────────────────────────────────

def edit_urls(existing: list = None) -> list:
    section("URLS")
    print("  Enter the URLs to open in your browser.")
    print(dim("  Type one URL per line. Leave blank and press Enter when done.\n"))

    urls = []
    if existing:
        for i, u in enumerate(existing, 1):
            print(f"    {i}. {u}")
        print()
        if ask_yn("  Keep these URLs?", True):
            urls = list(existing)

    while True:
        raw = ask("  Add URL (blank = done)", "")
        if not raw:
            break
        for u in raw.split(","):
            u = u.strip()
            if not u:
                continue
            if not u.startswith(("http://", "https://")):
                u = "https://" + u
            urls.append(u)
            print(green(f"    + {u}"))

    return urls


# ─── Custom App Builder ───────────────────────────────────────────────────────

def build_custom_app() -> dict | None:
    name = ask("  App display name (blank = cancel)", "")
    if not name:
        return None
    cmd      = ask(f"  Command or full path to launch {name}", "")
    args_raw = ask("  Extra args (space-separated, or blank)", "")
    return {
        "name":    name,
        "cat":     "Custom",
        "enabled": True,
        "command": cmd,
        "args":    args_raw.split() if args_raw else [],
    }


# ─── Library → Config Converter ───────────────────────────────────────────────

def lib_to_config(lib_app: dict) -> dict:
    details = lib_app[OS_KEY]
    return {
        "name":    lib_app["name"],
        "cat":     lib_app["cat"],
        "enabled": True,
        "command": details["cmd"],
        "args":    details.get("args", []),
    }


# ─── Setup Wizard ─────────────────────────────────────────────────────────────

def run_setup(existing: dict = None) -> dict:
    print(BANNER)
    print(bold(f"\n  Welcome to Let's Cook setup!  OS: {OS_LABEL}\n"))

    # Step 1 — Pick apps
    section("STEP 1 / 3  —  SELECT YOUR APPS")
    pre_selected = {a["name"] for a in existing.get("apps", [])} if existing else set()
    chosen = pick_apps(os_apps(), pre_selected)

    # Step 1b — Custom apps
    section("STEP 1b  —  CUSTOM APPS  (optional)")
    custom = []
    while ask_yn("  Add a custom app not in the list?", False):
        entry = build_custom_app()
        if entry:
            custom.append(entry)

    apps = [lib_to_config(a) for a in chosen] + custom

    # Step 2 — URLs
    urls = edit_urls(existing.get("urls") if existing else None)

    # Step 3 — Delay
    section("STEP 3 / 3  —  TIMING")
    delay_default = str(existing.get("delay", 1.5) if existing else 1.5)
    try:
        delay = float(ask("  Seconds between app launches", delay_default))
    except ValueError:
        delay = 1.5

    config = {"apps": apps, "urls": urls, "delay": delay}
    save_config(config)
    print(green("\n  All set! Run  lets_cook  anytime to fire everything up.\n"))
    return config


# ─── Management Commands ──────────────────────────────────────────────────────

def _simple_menu(title: str, options: list[tuple]) -> str:
    """Print a numbered menu, return the chosen value."""
    print(f"\n  {bold(title)}\n")
    for i, (label, _) in enumerate(options, 1):
        print(f"  {i}.  {label}")
    print()
    while True:
        raw = ask("  Choice", "")
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx][1]
        print(yellow(f"  Enter a number between 1 and {len(options)}."))


def cmd_add(config: dict) -> dict:
    section("ADD")
    action = _simple_menu("What would you like to add?", [
        ("Pick from the app library",  "lib"),
        ("Add a custom app or script", "custom"),
        ("Add URLs",                   "url"),
        ("Cancel",                     "cancel"),
    ])

    configured_names = {a["name"] for a in config.get("apps", [])}

    if action == "lib":
        available = [a for a in os_apps() if a["name"] not in configured_names]
        if not available:
            print(yellow("  All library apps are already in your config."))
        else:
            chosen = pick_apps(available)
            new_entries = [lib_to_config(a) for a in chosen]
            config.setdefault("apps", []).extend(new_entries)
            print(green(f"\n  Added {len(new_entries)} app(s)."))
            save_config(config)

    elif action == "custom":
        entry = build_custom_app()
        if entry:
            config.setdefault("apps", []).append(entry)
            print(green(f"\n  Added: {entry['name']}"))
            save_config(config)

    elif action == "url":
        new_urls = edit_urls(None)
        config.setdefault("urls", []).extend(new_urls)
        print(green(f"\n  Added {len(new_urls)} URL(s)."))
        save_config(config)

    return config


def cmd_edit(config: dict) -> dict:
    section("EDIT")
    action = _simple_menu("What would you like to edit?", [
        ("Toggle apps ON/OFF or change a command", "apps"),
        ("Edit URLs",                              "urls"),
        ("Change launch delay",                    "delay"),
        ("Cancel",                                 "cancel"),
    ])

    if action == "apps":
        apps = config.get("apps", [])
        if not apps:
            print(yellow("  No apps configured yet."))
            return config

        currently_on = {a["name"] for a in apps if a.get("enabled", True)}
        enabled_now  = toggle_apps(apps, currently_on)

        for app in apps:
            app["enabled"] = app["name"] in enabled_now

        # Allow command edits
        print(f"\n  {dim('To change a command, type its number. Blank = done.')}")
        for i, app in enumerate(apps, 1):
            print(f"  {i:3}.  {app['name']:<24}  {dim(app.get('command',''))}")
        print()
        while True:
            raw = ask("  Edit command # (blank = done)", "")
            if not raw or not raw.isdigit():
                break
            idx = int(raw) - 1
            if 0 <= idx < len(apps):
                new_cmd = ask(f"  New command for {apps[idx]['name']}", apps[idx].get("command", ""))
                apps[idx]["command"] = new_cmd
                print(green(f"  Updated."))

        config["apps"] = apps
        save_config(config)

    elif action == "urls":
        config["urls"] = edit_urls(config.get("urls", []))
        save_config(config)

    elif action == "delay":
        try:
            config["delay"] = float(ask("  New delay (seconds)", str(config.get("delay", 1.5))))
            save_config(config)
        except ValueError:
            print(yellow("  Invalid number — unchanged."))

    return config


def cmd_remove(config: dict) -> dict:
    section("REMOVE")
    apps = config.get("apps", [])
    urls = config.get("urls", [])

    if not apps and not urls:
        print(yellow("  Nothing configured to remove."))
        return config

    print("\n  ── Apps ──")
    for i, app in enumerate(apps, 1):
        print(f"  {i:3}.  {app['name']}")
    offset = len(apps)
    print("\n  ── URLs ──")
    for j, url in enumerate(urls, offset + 1):
        print(f"  {j:3}.  {url}")
    print()
    raw = ask("  Numbers to remove (comma-separated, blank = cancel)", "")
    if not raw:
        return config

    picks = {int(t.strip()) for t in raw.split(",") if t.strip().isdigit()}
    app_idx_remove = {i - 1 for i in picks if 1 <= i <= offset}
    url_idx_remove = {i - offset - 1 for i in picks if offset < i <= offset + len(urls)}

    config["apps"] = [a for i, a in enumerate(apps) if i not in app_idx_remove]
    config["urls"] = [u for i, u in enumerate(urls) if i not in url_idx_remove]

    print(green(f"\n  Removed {len(app_idx_remove)} app(s) and {len(url_idx_remove)} URL(s)."))
    save_config(config)
    return config


def cmd_list(config: dict):
    print(BANNER)
    apps  = config.get("apps", [])
    urls  = config.get("urls", [])
    delay = config.get("delay", 1.5)

    section(f"APPS  ({len(apps)} configured)")
    if not apps:
        print(yellow("  None."))
    else:
        current_cat = None
        for app in apps:
            cat = app.get("cat", "Custom")
            if cat != current_cat:
                current_cat = cat
                print(f"\n  {dim('── ' + cat)}")
            state = green("ON ") if app.get("enabled", True) else red("OFF")
            print(f"    [{state}]  {app['name']:<24}  {dim(app.get('command',''))}")

    section(f"URLS  ({len(urls)})")
    for u in urls:
        print(f"    {cyan(u)}")
    if not urls:
        print(yellow("  None."))

    section("SETTINGS")
    print(f"    Delay between apps : {delay}s")
    print(f"    Config file        : {CONFIG_FILE}\n")


# ─── Launcher ─────────────────────────────────────────────────────────────────

def launch_app(app: dict):
    cmd  = app.get("command", "").strip()
    args = app.get("args", [])
    name = app["name"]

    if not cmd:
        print(yellow(f"  [SKIP]  {name:<26} no command configured"))
        return

    try:
        if IS_WINDOWS:
            subprocess.Popen([cmd] + args, shell=True,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen([cmd] + args,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)
        print(green(f"  [ OK ]  {name}"))
    except FileNotFoundError:
        print(red(f"  [FAIL]  {name:<26} not found: {cmd}"))
    except Exception as exc:
        print(red(f"  [FAIL]  {name:<26} {exc}"))


def cook(config: dict):
    print(BANNER)
    print(bold(f"  OS: {OS_LABEL}  |  Let's get cooking...\n"))

    delay = config.get("delay", 1.5)
    apps  = [a for a in config.get("apps", []) if a.get("enabled", True)]
    urls  = config.get("urls", [])

    section(f"APPS  ({len(apps)} enabled)")
    for i, app in enumerate(apps):
        launch_app(app)
        if i < len(apps) - 1:
            time.sleep(delay)

    section(f"URLS  ({len(urls)})")
    for url in urls:
        try:
            webbrowser.open(url)
            print(green(f"  [ OK ]  {url}"))
        except Exception as exc:
            print(red(f"  [FAIL]  {url}  {exc}"))

    print(f"\n{bold('  Everything is cooking!  Happy coding.')}\n")


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    argv = sys.argv[1:]

    if "--help" in argv or "-h" in argv:
        print(BANNER)
        print(HELP_TEXT)
        return

    if "--setup" in argv or "-s" in argv:
        config = run_setup(load_config() or None)
        return

    config = load_config()

    if "--add" in argv:
        config = cmd_add(config) if config else run_setup()
        return

    if "--edit" in argv:
        config = cmd_edit(config) if config else run_setup()
        return

    if "--remove" in argv:
        if not config:
            print(yellow("  Nothing to remove — no config found."))
        else:
            cmd_remove(config)
        return

    if "--list" in argv:
        if not config:
            print(yellow("  No config found. Run  lets_cook --setup  to get started."))
        else:
            cmd_list(config)
        return

    if not config:
        print(yellow("  No config found — let's set things up!\n"))
        config = run_setup()

    cook(config)


if __name__ == "__main__":
    main()
