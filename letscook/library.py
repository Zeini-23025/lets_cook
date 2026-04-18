"""Application library and library mapping helpers."""

import os
from pathlib import Path

from .constants import OS_KEY

# Windows environment path shortcuts
_AP   = os.environ.get("APPDATA",      "")   # %APPDATA%     Roaming
_LA   = os.environ.get("LOCALAPPDATA", "")   # %LOCALAPPDATA%
_PF   = "C:/Program Files"
_PF86 = "C:/Program Files (x86)"
_H    = str(Path.home())

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

def os_apps() -> list:
    return [a for a in APP_LIBRARY
            if a["platform"] in ("both", OS_KEY) and a.get(OS_KEY)]


# ─── Raw key reader (no external deps) ───────────────────────────────────────


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

