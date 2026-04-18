#!/usr/bin/env python3
"""
Let's Cook - Fire up your entire workspace with one command.
"""

import json
import os
import platform
import subprocess
import sys
import webbrowser
from pathlib import Path

CONFIG_DIR = Path.home() / ".letscook"
CONFIG_FILE = CONFIG_DIR / "config.json"
IS_WINDOWS = platform.system() == "Windows"

BANNER = """
╔═══════════════════════════════════════════╗
║          LET'S COOK  - v1.0               ║
║     Fire up your workspace instantly      ║
╚═══════════════════════════════════════════╝
"""

# Sensible defaults to pre-fill the setup wizard
DEFAULT_APPS = [
    {
        "name": "VS Code",
        "enabled": True,
        "windows": {"command": "code", "args": []},
        "linux":   {"command": "code", "args": []},
    },
    {
        "name": "Spotify",
        "enabled": True,
        "windows": {"command": str(Path.home() / "AppData/Roaming/Spotify/Spotify.exe"), "args": []},
        "linux":   {"command": "spotify", "args": []},
    },
    {
        "name": "Laragon",
        "enabled": True,
        "windows": {"command": "C:/laragon/laragon.exe", "args": []},
        "linux":   {"command": "", "args": []},
    },
    {
        "name": "Docker Desktop",
        "enabled": True,
        "windows": {"command": "C:/Program Files/Docker/Docker/Docker Desktop.exe", "args": []},
        "linux":   {"command": "docker", "args": ["info"]},
    },
    {
        "name": "Firefox",
        "enabled": False,
        "windows": {"command": "C:/Program Files/Mozilla Firefox/firefox.exe", "args": []},
        "linux":   {"command": "firefox", "args": []},
    },
]

DEFAULT_URLS = [
    "https://gitlab.dcs-sarl.com/",
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def clr(text: str, code: str) -> str:
    """ANSI colour; skipped on Windows unless ANSI is supported."""
    if IS_WINDOWS:
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7
            )
        except Exception:
            return text
    return f"\033[{code}m{text}\033[0m"

def green(t):  return clr(t, "32")
def yellow(t): return clr(t, "33")
def cyan(t):   return clr(t, "36")
def bold(t):   return clr(t, "1")
def red(t):    return clr(t, "31")

def ask(prompt: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    try:
        val = input(f"  {cyan('>')} {prompt}{hint}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)
    return val if val else default

def ask_yes_no(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    raw = ask(f"{prompt} ({hint})", "")
    if not raw:
        return default
    return raw.lower() in ("y", "yes")

def section(title: str):
    width = 46
    print(f"\n{bold('─' * width)}")
    print(f"  {bold(title)}")
    print(bold("─" * width))


# ─── Config I/O ───────────────────────────────────────────────────────────────

def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(green(f"\n  Config saved to {CONFIG_FILE}"))


# ─── Setup Wizard ─────────────────────────────────────────────────────────────

def run_setup(existing: dict = None) -> dict:
    print(BANNER)
    print(bold("  Welcome to the Let's Cook setup wizard!"))
    print("  Answer each prompt — press Enter to keep the default.\n")

    # ── Apps ──
    section("APPS")
    print("  Configure which apps to launch. Leave the command blank to skip an app.\n")

    apps = []
    seed = existing.get("apps", DEFAULT_APPS) if existing else DEFAULT_APPS

    for app in seed:
        os_key = "windows" if IS_WINDOWS else "linux"
        current_cmd = app[os_key]["command"]
        current_args = " ".join(app[os_key].get("args", []))

        print(f"  {bold(app['name'])}")
        enabled = ask_yes_no(f"    Enable {app['name']}?", app.get("enabled", True))
        if enabled:
            cmd  = ask(f"    Command/path", current_cmd)
            args_raw = ask(f"    Extra args (space-separated)", current_args)
            app[os_key]["command"] = cmd
            app[os_key]["args"] = args_raw.split() if args_raw else []
        app["enabled"] = enabled
        apps.append(app)
        print()

    # ── Custom apps ──
    print(f"  {bold('Add custom apps?')}  (leave name blank to stop)\n")
    while True:
        name = ask("  App name (blank = done)", "")
        if not name:
            break
        win_cmd   = ask(f"    Windows command/path for {name}", "")
        linux_cmd = ask(f"    Linux  command/path for {name}", "")
        win_args  = ask(f"    Windows extra args", "")
        linux_args = ask(f"    Linux   extra args", "")
        apps.append({
            "name": name,
            "enabled": True,
            "windows": {"command": win_cmd,   "args": win_args.split()   if win_args   else []},
            "linux":   {"command": linux_cmd, "args": linux_args.split() if linux_args else []},
        })
        print()

    # ── URLs ──
    section("URLS")
    print("  Enter URLs to open in your browser (one per line, blank line to finish).")
    print(f"  Current URLs: {', '.join(existing.get('urls', DEFAULT_URLS) if existing else DEFAULT_URLS)}\n")

    raw_urls = ask("  URLs (comma-separated)", ", ".join(
        existing.get("urls", DEFAULT_URLS) if existing else DEFAULT_URLS
    ))
    urls = [u.strip() for u in raw_urls.split(",") if u.strip()]

    # ── Delay ──
    section("TIMING")
    delay = ask("  Seconds to wait between launching apps", str(
        existing.get("delay", 1.5) if existing else 1.5
    ))
    try:
        delay = float(delay)
    except ValueError:
        delay = 1.5

    config = {"apps": apps, "urls": urls, "delay": delay}
    save_config(config)

    print(green("\n  All done! Run  lets_cook  anytime to fire everything up.\n"))
    return config


# ─── Launcher ─────────────────────────────────────────────────────────────────

def launch_app(app: dict):
    os_key = "windows" if IS_WINDOWS else "linux"
    details = app.get(os_key, {})
    cmd = details.get("command", "").strip()
    args = details.get("args", [])

    if not cmd:
        print(yellow(f"  [skip]  {app['name']} — no command configured for this OS"))
        return

    full_cmd = [cmd] + args
    try:
        if IS_WINDOWS:
            # Use shell=True so Windows can resolve .exe paths / env vars
            subprocess.Popen(full_cmd, shell=True,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(full_cmd,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)
        print(green(f"  [  OK  ]  {app['name']}"))
    except FileNotFoundError:
        print(red(f"  [ FAIL ]  {app['name']} — not found: {cmd}"))
    except Exception as exc:
        print(red(f"  [ FAIL ]  {app['name']} — {exc}"))


def cook(config: dict):
    import time

    print(BANNER)
    os_label = "Windows" if IS_WINDOWS else "Linux"
    print(bold(f"  OS: {os_label}  |  Launching your workspace...\n"))

    delay = config.get("delay", 1.5)
    apps  = [a for a in config.get("apps", []) if a.get("enabled")]
    urls  = config.get("urls", [])

    section("APPS")
    for i, app in enumerate(apps):
        launch_app(app)
        if i < len(apps) - 1:
            time.sleep(delay)

    section("URLS")
    for url in urls:
        try:
            webbrowser.open(url)
            print(green(f"  [  OK  ]  {url}"))
        except Exception as exc:
            print(red(f"  [ FAIL ]  {url} — {exc}"))

    print(f"\n{bold('  Everything is cooking! Happy coding.')}\n")


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if "--setup" in args or "--config" in args or "-s" in args:
        existing = load_config()
        run_setup(existing if existing else None)
        return

    if "--help" in args or "-h" in args:
        print(BANNER)
        print("  Usage:")
        print(f"    {cyan('lets_cook')}           — launch your workspace")
        print(f"    {cyan('lets_cook --setup')}   — re-run the setup wizard")
        print(f"    {cyan('lets_cook --help')}    — show this message")
        return

    config = load_config()

    if not config:
        print(BANNER)
        print(yellow("  No config found. Let's set things up first!\n"))
        config = run_setup()

    cook(config)


if __name__ == "__main__":
    main()
