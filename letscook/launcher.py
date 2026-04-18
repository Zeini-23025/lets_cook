"""Application and URL launch flow."""

import subprocess
import time
import webbrowser

from .constants import BANNER, IS_WINDOWS, OS_LABEL
from .ui import bold, green, red, section, yellow

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

